from netCDF4 import Dataset
import numpy as np
from collections import OrderedDict
import os


class NetCDFFileCreator(object):
    """ NetCDF file creator

    Class to assist with the creation of netCDF files

    Parameters
    ----------
    file_name : str, optional
        The name of the grid metrics file that will be created.

    format : str, optional
        The format of the NetCDF file (e.g. NetCDF4). Default: NetCDF4.

    """

    def __init__(self, file_name, title='', format="NETCDF4"):
        self.file_name = file_name
        self.title = title

        self.format = format

        # Compression options for the netCDF variables.
        self.ncopts = {'zlib': True, 'complevel': 7}

        # Create attribute for the NetCDF4 dataset
        self.ncfile = None

        # Create the file
        self._create_file()

    def _create_file(self):
        """ Create the file

        Create a new, skeleton file. Dimensions and variables must be added separately.

        Parameters
        ----------
        N/A

        Returns
        -------
        N/A
        """
        if not os.path.isfile(self.file_name):
            # Create the file
            self.ncfile = Dataset(self.file_name, mode='w', format=self.format)
            
            # Add global attributes
            self._set_global_attributes()
        else:
            # Open the file
            self.ncfile = Dataset(self.file_name, mode='a')


    def create_dimension(self, name, size):
        """ Add dimension variable

        Parameters
        ----------
        name : str
            Name of the dimension

        size : int
            Name of the string
        """
        if name in self.ncfile.dimensions.keys():
            raise RuntimeError('Dimension {} already exists'.format(name))
            
        self.ncfile.createDimension(name, size)

    def create_variable(self, var_name, var_data, dimensions, dtype, fill_value=None, attrs=None):
        """" Add variable

        Parameters
        ----------
        var_name : str
            Name of the variable to add

        var_data : ndarray
            Data array

        dimensions : tuple
            Dimensions of the ndarray

        dtype : str
            Data type (e.g. float)

        fill_value : int, float, optional.
            Fill value to use. Default: None.

        attrs : dict, optional
            Dictionary of attributes. Default: None.
        """
        if var_name in self.ncfile.variables.keys():
            raise RuntimeError('Variable {} already exists'.format(var_name))

        for dimension in dimensions:
            if dimension not in self.ncfile.dimensions.keys():
                raise RuntimeError("Can't create variable `{}': the `{}' coordinate " \
                                   "variable has not yet been created.".format(var_name, dimension))

        if fill_value is not None:
            var = self.ncfile.createVariable(var_name, dtype, dimensions, fill_value=fill_value,
                                                             **self.ncopts)
        else:
            var = self.ncfile.createVariable(var_name, dtype, dimensions, **self.ncopts)

        if attrs is not None:
            var.setncatts(attrs)

        var[:] = var_data.astype(dtype, casting='same_kind')

    def _set_global_attributes(self):
        """ Set global attributes

        Add a set of global attributes.
        """

        global_attrs = OrderedDict()

        global_attrs['title'] = self.title
        global_attrs['institution'] = 'Plymouth Marine Laboratory (PML)'
        global_attrs['contact'] = 'James R. Clark (jcl@pml.ac.uk)'
        global_attrs['netcdf-version-id'] = 'netCDF-4'

        self.ncfile.setncatts(global_attrs)

        global_attrs['comment'] = ""

        return global_attrs

    def close_file(self):
        """ Close the file
        """
        try:
            self.ncfile.close()
        except:
            raise RuntimeError('Problem closing file')


class MassConcNetCDFFileCreator(object):
    """ Class to assist in the modification of NetCDF files
    """
    _time_name = 'time'
    _lat_name = 'latitude'
    _lon_name = 'longitude'
    _depth_name = 'depth'

    def __init__(self, file_name):
        logger = logging.getLogger(__name__)
        logger.info('Creating output file: {}.'.format(file_name))
        self.ncfile = Dataset(file_name, mode='w')

        # Coordinate dimensions
        self.dims = dict()

        # Coordinate variables
        self.coordinates = dict()

        # Dictionary holding netcdf variable data
        self.vars = dict()

        # Compression options for the netCDF variables.
        self.ncopts = {'zlib': True, 'complevel': 7}

    def create_dimension(self, name, size):
        if name in self.ncfile.dimensions.keys():
            raise RuntimeError(
                '{} dimension has already been created.'.format(name))

        self.dims[name] = self.ncfile.createDimension(name, size)

        return

    def create_time(self, datetimes):
        if self._time_name in self.dims.keys():
            raise RuntimeError('Time variable has already been created')

        # Add time dimension
        self.create_dimension(self._time_name, len(datetimes))

        # Add time variable
        self.coordinates[self._time_name] = self.ncfile.createVariable(
            self._time_name, 'f4', (self._time_name,), **self.ncopts)
        self.coordinates[
            self._time_name].units = 'seconds since 2018-01-01 00:00:00'
        self.coordinates[self._time_name].calendar = 'Gregorian'
        self.coordinates[self._time_name].standard_name = 'time'
        self.coordinates[self._time_name].long_name = 'time'
        self.coordinates[self._time_name].axis = 'T'

        times = date2num(datetimes,
                         units=self.coordinates[self._time_name].units,
                         calendar=self.coordinates[self._time_name].calendar)

        self.coordinates[self._time_name].valid_min = np.min(times)
        self.coordinates[self._time_name].valid_max = np.max(times)

        self.coordinates[self._time_name][:] = times

    def create_depth(self, depths):
        if self._depth_name in self.ncfile.variables.keys():
            raise RuntimeError('Depth variable has already been created')

        if isinstance(depths, np.ndarray):
            depths_arr = depths
        elif isinstance(depths, list):
            depths_arr = np.array(depths)
        elif isinstance(depths, float):
            depths_arr = np.array([depths])
        else:
            raise ValueError(
                'Unsupported variable type for depths array. Should be np.ndarray, list or float')

        if depths_arr.ndim != 1:
            raise ValueError('Depths array should be 1D')

        if depths_arr.shape[0] != 1:
            raise ValueError('Depths array should be single valued')

        # Add depth dimension
        if self._depth_name not in self.dims.keys():
            self.create_dimension(self._depth_name, depths_arr.shape[0])

        # Add depth variable
        self.coordinates[self._depth_name] = self.ncfile.createVariable(
            self._depth_name, 'f4',
            (self._depth_name,), **self.ncopts)
        self.coordinates[self._depth_name].standard_name = 'depth'
        self.coordinates[self._depth_name].long_name = 'depth'
        self.coordinates[self._depth_name].units = 'm'
        self.coordinates[self._depth_name].axis = 'Z'
        self.coordinates[self._depth_name].positive = 'down'

        self.coordinates[self._depth_name].valid_min = np.min(depths)
        self.coordinates[self._depth_name].valid_max = np.max(depths)

        self.coordinates[self._depth_name][:] = depths

    def create_latitude(self, lats):
        if self._lat_name in self.dims.keys():
            raise RuntimeError('Lat variable has already been created')

        # Add latitude dimension
        self.create_dimension(self._lat_name, len(lats))

        # Add latitude variable
        self.coordinates[self._lat_name] = self.ncfile.createVariable(
            self._lat_name, lats.dtype, (self._lat_name,), **self.ncopts)
        self.coordinates[self._lat_name].standard_name = 'latitude'
        self.coordinates[self._lat_name].long_name = 'latitude'
        self.coordinates[self._lat_name].units = 'degrees_north'
        self.coordinates[self._lat_name].axis = 'Y'

        self.coordinates[self._lat_name].valid_min = np.min(lats)
        self.coordinates[self._lat_name].valid_max = np.max(lats)

        self.coordinates[self._lat_name][:] = lats

    def create_longitude(self, lons):
        if self._lon_name in self.dims.keys():
            raise RuntimeError('Lat variable has already been created')

        # Add longitude dimension
        self.create_dimension(self._lon_name, len(lons))

        # Add longitude variable
        self.coordinates[self._lon_name] = self.ncfile.createVariable(
            self._lon_name, lons.dtype, (self._lon_name,), **self.ncopts)
        self.coordinates[self._lon_name].standard_name = 'longitude'
        self.coordinates[self._lon_name].long_name = 'longitude'
        self.coordinates[self._lon_name].units = 'degrees_east'
        self.coordinates[self._lon_name].axis = 'X'

        self.coordinates[self._lon_name].valid_min = np.min(lons)
        self.coordinates[self._lon_name].valid_max = np.max(lons)

        self.coordinates[self._lon_name][:] = lons

    def create_variable(self, var_name, var_data, dtype, fill_value,
                        missing_value, attrs):

        n_dims = len(var_data.shape)
        if n_dims == 3:
            dimensions = (self._time_name, self._lat_name, self._lon_name)
        elif n_dims == 4:
            dimensions = (self._time_name, self._depth_name,
                          self._lat_name, self._lon_name)
        else:
            raise RuntimeError('Unsupported number of dims')

        self.vars[var_name] = self.ncfile.createVariable(var_name, dtype,
                                                         dimensions,
                                                         fill_value=fill_value,
                                                         **self.ncopts)
        self.vars[var_name].standard_name = attrs['standard_name']
        self.vars[var_name].long_name = attrs['long_name']
        self.vars[var_name].units = attrs['units']
        # self.vars[var_name].missing_value = missing_value

        if 'positive' in attrs:
            self.vars[var_name].positive = attrs['positive']

        self.vars[var_name][:] = var_data

    def set_global_attributes(self, global_attributes):
        self.ncfile.setncatts(global_attributes)

    def close_file(self):
        try:
            self.ncfile.close()
        except:
            raise RuntimeError('Problem closing file')


# Disclaimer text
disclaimer = ""\
"Use by you of the data (which includes model outputs and simulatins) \n"\
"provided by PML in this file is entirely at your own risk. This data is \n"\
"provided \"as is\" without any warranty of any kind, either expressed or \n"\
"implied, including without limitation, any implied warranties as to its \n"\
"merchantability or its suitability for any use. All implied conditions \n"\
"relating to the quality or suitability of the data and the medium on which \n"\
"it is provided, and all liabilities arising from the supply of the data \n"\
"(including any liability arising in negligence) are excluded to the fullest \n"\
"extent permitted by law. In using the data you agree to acknowledge use of \n"\
"the data in the acknowledgement section of any resulting publication."