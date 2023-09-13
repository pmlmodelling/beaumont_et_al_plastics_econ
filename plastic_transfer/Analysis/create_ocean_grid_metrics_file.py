""" Create PyLag ocean grid metrics file

CMEMS global ocean reanalysis data is downloaded from the CMEMS website
(https://data.marine.copernicus.eu/) using the motu client
(https://pypi.org/project/motuclient/). This project uses surface data
from the GLORYS12V1 global reanalysis product. A single
input file is used to create a grid metrics file for use with PyLag.
The grid metrics file is created in the Inputs/grid_metrics directory.

CMEMS data DOI: 10.48670/moi-00021
"""
import pathlib

from pylag.grid_metrics import create_arakawa_a_grid_metrics_file as create

from project_paths import cmems_data_dir


in_file = f'{cmems_data_dir}/DAILY_GLOBAL_REANALYSIS_PHY_001_030-TDS_uv_2015_01.nc'

# Create output directory
pathlib.Path('../Inputs/grid_metrics').mkdir(parents=True, exist_ok=True)

# Create grid metrics file
out_file = f'../Inputs/grid_metrics/grid_metrics_surface_ocean.nc'
create(in_file, is_global=True, surface_only=True, reference_var_name='uo',
       prng_seed=162, grid_metrics_file_name=out_file)
