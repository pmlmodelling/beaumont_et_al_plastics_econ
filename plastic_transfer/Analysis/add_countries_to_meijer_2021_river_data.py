""" Script for adding countries to plastic emissions data

The Meijer et al. (2021) dataset contains plastic emissions data for rivers
around the world. A shapefile giving river locations and fluxes is
available from the following website:

https://figshare.com/articles/dataset/Supplementary_data_for_More_than_1000_\
rivers_account_for_80_of_global_riverine_plsatic_emissions_into_the_\
ocean_/14515590

The dataset with countries added is saved to a directory called Derived_data
for use with other scripts.

References
----------

Lourens J. J. Meijer et al. ,More than 1000 rivers account for 80% of global
riverine plastic emissions into the ocean.
Sci.Adv.7,eaaz5803(2021).DOI:10.1126/sciadv.aaz5803
"""

import os
import pathlib
import geopandas
    
from shared import world_data_names
from marine_boundaries import reassign_madeira_rivers
from project_paths import meijer_data_dir as data_dir

# River plastics data
path_to_plastics_data = f'{data_dir}/Meijer2021_midpoint_emissions.shp'

# Make directory in which to store derived plastics data
output_dir = '../Derived_data/meijer_midpoint_emissions'
pathlib.Path(output_dir).mkdir(parents=True, exist_ok=True)

# Path to file which we will create. 
path_to_derived_data = f'{output_dir}/Meijer2021_midpoint_emissions_with_countries.shp'

# Read plastics input data with geopandas
gdf_plastics = geopandas.read_file(path_to_plastics_data)

# Read in country boundary data with geopandas
path_to_country_data = geopandas.datasets.get_path("naturalearth_lowres")
gdf_countries = geopandas.read_file(path_to_country_data)

# Set the country index to name
gdf_countries.set_index('name')

countries = []
for location in gdf_plastics['geometry']:
    country_index = gdf_countries.geometry.distance(location).idxmin()
    countries.append(gdf_countries.name[country_index])

gdf_plastics['countries'] = countries

# Fix up names
for standard_name, world_data_name in world_data_names.items():
    gdf_plastics.replace(world_data_name, standard_name, inplace=True)
    gdf_plastics.replace(world_data_name, standard_name, inplace=True)

# Special fix for Madeira, which is incorrectly associated with Morocco
gdf_plastics = reassign_madeira_rivers(gdf_plastics)

gdf_plastics.to_file(path_to_derived_data)
