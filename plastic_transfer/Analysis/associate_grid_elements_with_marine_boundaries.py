""" Flag elements associated with the different EEZ

We use v11 of the marine boundaries data set, which is available from:
https://www.marineregions.org.
"""
import os
import numpy as np
from multiprocessing import Pool
import pathlib
import geopandas
import shapely
from netCDF4 import Dataset
from matplotlib import pyplot as plt
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

from marine_boundaries import read_shapefile, get_eez_region
from shared import eez_names
from project_paths import marine_boundaries_data_dir


def flag_elements(lons, lats, country_geometry, valid_elements):
    """ Identify which grid elements lie within the country's boundary

    Note the call to `contains()` can be exceptionally expensive to run for
    countries with complicate, extensive geometries such as Canada, where
    testing indicated a single call (for a single point) can take 2 s to
    execute. The execution time is much smaller for distant points,
    presumably because tha algorithm screens out such points before
    running a more involved test of whether the point lies within the
    shape or not. Some time can be saved by screening out land points
    and non-sensical ocean points (e.g. those in a different hemisphere);
    but, even then, the time to execute in serial may be prohibitive.
    For these reasons, this function can be called in parallel using
    functionality implemented below. When using 24 threads, this reduced
    the execution time to something like 18 hours in scripts run on
    gridnode135 at PML.   
 
    Parameters
    ----------
    lons : 1D NumPy array 
        1D array of grid longitudes at element centres.

    lats : 1D NumPy array 
        1D array of grid latitudes at element centres.

    country_geometry : shapely.geometry.Polygon
        Polygon or Multipolygon object that defines the country boundary.
    
    valid_elements : 1D NumPy array 
        1D array of valid element ids

    Returns
    -------
    element_ids : 1D NumPy array
        List of element IDs that lie within the country polygon.
    """
    element_ids = []
    for element in valid_elements:
        location = shapely.geometry.Point(lons[element], lats[element])
        if country_geometry.contains(location):
            element_ids.append(element)

    element_ids = np.array(element_ids)

    return element_ids


def flag_elements_wrapper(args):
    # Wrapper for multiprocessing
    return flag_elements(*args)


def flag_elements_multiprocessing(lons, lats, country_geometry, valid_elements,
                                  file_name=None, num_threads=8):
    """ Identify which grid elements lie within the country's boundary

    Here we split the valid elements array up before passing it on so
    the calculation can be run in parallel.

    Parameters
    ----------
    lons : 1D NumPy array 
        1D array of grid longitudes at element centres.

    lats : 1D NumPy array 
        1D array of grid latitudes at element centres.

    country_geometry : shapely.geometry.Polygon
        Polygon or Multipolygon object that defines the country boundary.
    
    valid_elements : 1D NumPy array 
        1D array of valid element ids

    file_name : str or None
        If not None, the name of the file to save element identies in.

    num_threads : int
        The number of threads to use.
    """
    # Create a copy
    valid_elements_mp = np.copy(valid_elements)
    valid_elements_mp_split = np.array_split(valid_elements_mp, num_threads)

    # Run the task in parallel
    p = Pool(num_threads)
    element_ids = p.map(flag_elements_wrapper,
                        ((lons, lats, country_geometry, valid_elements_mp_split[i]) for i in range(num_threads)))

    # Join the arrays
    element_ids = np.concatenate(element_ids)

    if file_name is not None:
        element_ids.tofile(file_name, sep=',')

    return element_ids


# Read in grid data
# -----------------
grid_metrics_file_name = './Inputs/grid_metrics/grid_metrics_surface_ocean.nc'
grid_metrics = Dataset(grid_metrics_file_name)
lons = grid_metrics['longitude_c'][:]
lats = grid_metrics['latitude_c'][:]
mask = grid_metrics['mask_c'][:]
ocean_elements = np.asarray(mask==0).nonzero()[0]

# Limit the countries/regions we will look at
na_countries = eez_names.keys()


# Limit the list of elements to check to save time
# ------------------------------------------------
valid_elements = {}
for country in na_countries:
    northern_hemisphere_elements = np.asarray(lats>0.0).nonzero()[0]
    valid_elements[country] = np.intersect1d(ocean_elements,
                                             northern_hemisphere_elements)

# Select boundary types
# ---------------------
boundary_data_dir = marine_boundaries_data_dir
boundary_types = ['EEZ']

# Flag all elemenets lying within the boundary of each country and save to file
# -----------------------------------------------------------------------------
for boundary_type in boundary_types:
    gdf = read_shapefile(boundary_data_dir, boundary_type)

    # Create a dictionary of data frames, one for each country, that describe
    # the marine region/boundary for that country.
    regions = {}
    for country in na_countries:
        geoname = eez_names[country]
        if boundary_type == 'EEZ':
            regions[country] = get_eez_region(gdf, geoname)
        elif boundary_type == '12NM':
            regions[country] = get_12nm_region(gdf, geoname)
        else:
            raise ValueError(f'Support for boundary type {boundary_type} is '\
                             f'yet to be implemented')

    # Visualise regions
    plot_regions = False
    if plot_regions:
        world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))
        for country in na_countries:
            # Plot world map
            ax = world.plot(color='white', edgecolor='black')

            # Overlay EEZ
            regions[country].plot(ax=ax)

            ax.set_title(f'{country}')

    plt.show()

    # Associate grid elements with countries
    flag_elements_switch = True
    if flag_elements_switch:
        # Make output directory
        out_dir = f'./Derived_data/grid_elements/{boundary_type}'
        pathlib.Path(out_dir).mkdir(parents=True, exist_ok=True)
        
        for country in na_countries:
            print(f'Identifying grid elements that lie with the {boundary_type} '\
                  f'marine boundary for {country}')

            country_geometry = regions[country]['geometry'].values
            if country_geometry.shape[0] == 1:
                country_geometry = country_geometry[0]
            else:
                raise RuntimeError('Length of single country geometry array is not singular.')

            output_file_name = f'{out_dir}/grid_elements_for_{country}_{boundary_type}_boundary.csv'

            # Only process those countries that haven't been processed already
            if not os.path.isfile(output_file_name):
                flag_elements_multiprocessing(lons, lats, country_geometry,
                                              valid_elements[country], output_file_name) 

