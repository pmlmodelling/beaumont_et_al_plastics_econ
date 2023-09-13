""" Compute connectivity metrics

This script computes connectivity metrics for each run. It does this
by flagging whether whether or not particles lie within the EEZ of
each receiving country. The output is written to a netCDF file.
"""

import sys
import os
import numpy as np
import pathlib
from cftime import date2num
import argparse

from pylag.processing.ncview import Viewer

from netcdf_utils import NetCDFFileCreator
from shared import na_countries, connectivity_netcdf_names
from project_paths import simulations_dir

import cython_helpers


def process_emitting_country(emitting_country, year_str, month_str):
    print(f'Processing data for emitting country {emitting_country} and '
          f'month {month_str}')

    # Path to the run output file
    pylag_data_dir = f'{root_dir}/{scenario}/{emitting_country}/{year_str}/{month_str}/output'
    pylag_data = f'{pylag_data_dir}/pylag_1.nc'

    # Open the output file for reading
    pylag_viewer = Viewer(pylag_data, time_rounding=3600)

    # Get dimension sizes (workaround as can't access dimensions directly)
    n_dates = pylag_viewer._ds.dimensions['time'].size
    n_particles = pylag_viewer._ds.dimensions['particles'].size

    # Extract dates
    pylag_dates = pylag_viewer.date

    # The set of time indices to process
    time_indices = np.arange(0, n_dates, time_step)

    # The total number of time indices to process
    n_time_indices = time_indices.shape[0]
    print(f'Processing data for {n_time_indices} time points between '
          f'{pylag_dates[0]} and {pylag_dates[-1]}')

    dates = pylag_dates[time_indices]

    # Output file
    # -----------
    root_out_dir = f'../Derived_data/connectivity/{scenario}'
    year_out_dir = f'{root_out_dir}/{year_str}'
    month_out_dir = f'{year_out_dir}/{month_str}'
    pathlib.Path(month_out_dir).mkdir(parents=True, exist_ok=True)
    file_name = f'{month_out_dir}/{emitting_country}_connectivity_{year_str}_{month_str}.nc'
    # Create the file if it has not been created already
    if not os.path.isfile(file_name):
        title = f'Connectivity data for {emitting_country} river plastic emissions'
        nc_file = NetCDFFileCreator(file_name, title)

        # Add dimension data
        nc_file.create_dimension('time', n_time_indices)
        nc_file.create_dimension('particles', n_particles)

        # Add time variable
        time_attrs = {'units': 'seconds since 1990-01-01 00:00:00',
                      'calendar': 'standard',
                      'long_name': 'Time'}
        time = date2num(dates, units=time_attrs['units'], calendar=time_attrs['calendar'])
        nc_file.create_variable('time', time, ('time',), dtype=time.dtype, attrs=time_attrs)

    else:
        nc_file = NetCDFFileCreator(file_name)
   
    # Process all receiving countries
    # -------------------------------

    # Compute connectivity metrics
    for receiving_region in receiving_regions:
        
        print(f'\nComputing connectivity metrics for receiving region {receiving_region}')

        # Generate variable name and attributes
        netcdf_region_name = connectivity_netcdf_names[receiving_region]
        var_name = f'is_present_in_waters_of_{netcdf_region_name}'
        var_attrs = {'units': 'n/a',
                     'long_name': 'Binary flag indicating presence (=1) and absence (=0)'}
        
        # Check to see if the country has been processed already
        if var_name in nc_file.ncfile.variables.keys():
            print(f'\n ... data for receiving region {receiving_region} '
                  f'has been processed already')
            continue 

        # Read in valid boundary elements for the receiving country
        bdy_dir = '../Derived_data/grid_elements/EEZ'
        bdy_file_name = f'{bdy_dir}/grid_elements_for_{receiving_region}_EEZ_boundary.csv'
        bdy_elements = np.fromfile(bdy_file_name, sep=',')
        bdy_elements = np.sort(np.array(bdy_elements, dtype=np.int32))
       
        # Array in which to store in/out flags
        within = np.zeros((n_time_indices, n_particles), dtype=int)
        
        # Loop over all time points and compute how many host elements match those
        # that lie within the specified area
        for tidx_new, tidx_old in enumerate(time_indices):
            hosts = pylag_viewer('host_arakawa_a')[tidx_old, :].astype(np.int32)
            within[tidx_new, :] = cython_helpers.match_elements(hosts, bdy_elements, num_threads=8)

        nc_file.create_variable(var_name,
                                within,
                                ('time', 'particles',),
                                within.dtype,
                                attrs=var_attrs)

    print(f'\nClosing file {file_name}')
    nc_file.close_file()


# Directory where simulation results can be found
root_dir = simulations_dir

# The run scenario
scenario = 'ocean_leeway'

# The months that were run
months = range(1, 13)
valid_month_strs = ['{0:02}'.format(month) for month in months]

# The time step used when indexing in time (unit days for daily outputs)
time_step = 1

# The list of receiving countries
receiving_regions = connectivity_netcdf_names.keys()


if __name__ == "__main__":
    # Parse command line agruments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--country', help='Name of emitting country',  metavar='')
    parser.add_argument('-y', '--year', help='Year',  metavar='')
    parser.add_argument('-m', '--month', help='Month number',  metavar='')
    parsed_args = parser.parse_args(sys.argv[1:])

    # Check country    
    country = parsed_args.country
    if country not in na_countries:
        raise RuntimeError(f'Invalid country name {country}')

    # Year string
    year_str_in = parsed_args.year

    # Check month
    month = int(parsed_args.month)
    month_str_in = '{0:02}'.format(month)
    if month_str_in not in valid_month_strs:
        raise RuntimeError(f'Invalid month {month}')

    # Run the job
    process_emitting_country(country, year_str_in, month_str_in)
