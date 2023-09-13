""" Create PyLag atmosphere grid metrics file

ERA5 global atmospheric reanalysis data is downloaded from the Climate Data
Store (https://cds.climate.copernicus.eu). A single input file is used to
create a grid metrics file for use with PyLag. The grid metrics file is
created in the Inputs/grid_metrics directory.

ERA5 Product DOI: 10.24381/cds.adbb2d47
"""
import pathlib

from pylag.grid_metrics import create_arakawa_a_grid_metrics_file

from project_paths import era5_data_dir


in_file = f'{era5_data_dir}/era5_winds_2015_01.nc'

# Make the output directory if it doesn't exist
pathlib.Path('../Inputs/grid_metrics').mkdir(parents=True, exist_ok=True)

# Create the grid metrics file
out_file = f'../Inputs/grid_metrics/grid_metrics_atmosphere.nc'
create_arakawa_a_grid_metrics_file(in_file,
                                   lon_var_name='longitude',
                                   lat_var_name='latitude',
                                   is_global=True,
                                   surface_only=True,
                                   save_mask=False,
                                   prng_seed=200,
                                   grid_metrics_file_name=out_file)
