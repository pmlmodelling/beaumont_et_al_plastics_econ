""" Module for shared constants etc
"""
import cartopy.crs as ccrs
import shapely.geometry

font_size = 8

data_crs=ccrs.PlateCarree()


# List of North Atlantic States for the project
na_countries = ['Belgium',
                'Canada',
                'Denmark',
                'France',
                'Germany',
                'Dom. Rep.',
                'Haiti',
                'Ireland',
                'Mexico',
                'Morocco',
                'Netherlands',
                'Portugal',
                'Spain',
                'Sweden',
                'UK',
                'US']

# List of GNI names for the North Atlantic States
gni_names = {'Belgium': 'Belgium',
             'Canada': 'Canada',
             'Denmark': 'Denmark',
             'France': 'France',
             'Germany': 'Germany',
             'Dom. Rep.': 'Dominican Republic',
             'Haiti': 'Haiti',
             'Ireland': 'Ireland',
             'Mexico': 'Mexico',
             'Morocco': 'Morocco',
             'Netherlands': 'Netherlands',
             'Portugal': 'Portugal',
             'Spain': 'Spain',
             'Sweden': 'Sweden',
             'UK': 'United Kingdom',
             'US': 'United States'}

# Dictionary of country names, as given in the Geopandas World Data dataset; these
# names were used to associate Meijer rivers with countries.
world_data_names = {'Belgium': 'Belgium',
                    'Canada': 'Canada',
                    'Denmark': 'Denmark',
                    'France': 'France',
                    'Germany': 'Germany',
                    'Dom. Rep.': 'Dominican Rep.',
                    'Haiti': 'Haiti',
                    'Ireland': 'Ireland',
                    'Mexico': 'Mexico',
                    'Morocco': 'Morocco',
                    'Netherlands': 'Netherlands',
                    'Portugal': 'Portugal',
                    'Spain': 'Spain',
                    'Sweden': 'Sweden',
                    'UK': 'United Kingdom',
                    'US': 'United States of America'}

# Dictionary of EEZ names, as given in the Marine Boundaries data set for
# EEZs (v11).
#
# Notes
# -----
# Excludes several exclave regions, including: French Guiana (France).
#
# Includes exclave and semi-exclave regions for the US, including:
# Hawaii and Alaska.
eez_names = {'Belgium': 'Belgian Exclusive Economic Zone',
             'Canada': 'Canadian Exclusive Economic Zone',
             'Denmark': 'Danish Exclusive Economic Zone',
             'France': 'French Exclusive Economic Zone',
             'Germany': 'German Exclusive Economic Zone',
             'Dom. Rep.': 'Dominican Republic Exclusive Economic Zone',
             'Haiti': 'Haitian Exclusive Economic Zone',
             'Ireland': 'Irish Exclusive Economic Zone',
             'Mexico': 'Mexican Exclusive Economic Zone',
             'Morocco': 'Moroccan Exclusive Economic Zone',
             'Morocco (Western Saharan)': 'Overlapping claim Western Saharan Exclusive Economic Zone',
             'Netherlands': 'Dutch Exclusive Economic Zone',
             'Portugal': 'Portuguese Exclusive Economic Zone',
             'Portugal (Azores)': 'Portuguese Exclusive Economic Zone (Azores)',
             'Portugal (Madeira)': 'Portuguese Exclusive Economic Zone (Madeira)',
             'Spain': 'Spanish Exclusive Economic Zone',
             'Spain (Canary Islands)': 'Spanish Exclusive Economic Zone (Canary Islands)',
             'Sweden': 'Swedish Exclusive Economic Zone',
             'UK': 'United Kingdom Exclusive Economic Zone',
             'US': 'United States Exclusive Economic Zone',
             'US (Alaska)': 'United States Exclusive Economic Zone (Alaska)',
             'US (Hawaii)': 'United States Exclusive Economic Zone (Hawaii)'}

# Dictionary of netcdf friendly country names for the connectivity files
connectivity_netcdf_names = {'Belgium': 'belgium',
                             'Canada': 'canada',
                             'Denmark': 'denmark',
                             'France': 'france',
                             'Germany': 'germany',
                             'Dom. Rep.': 'dom_rep',
                             'Haiti': 'haiti',
                             'Ireland': 'ireland',
                             'Mexico': 'mexico',
                             'Morocco': 'morocco',
                             'Morocco (Western Saharan)': 'western_saharan',
                             'Netherlands': 'netherlands',
                             'Portugal': 'portugal',
                             'Portugal (Azores)': 'azores',
                             'Portugal (Madeira)': 'madeira',
                             'Spain': 'spain',
                             'Spain (Canary Islands)': 'canaries',
                             'Sweden': 'sweden',
                             'UK': 'uk',
                             'US': 'us',
                             'US (Alaska)': 'alaska',
                             'US (Hawaii)': 'hawaii'}


international_waters_netcdf_var_name = "is_present_in_international_waters"
international_waters_netcdf_var_attrs = {'units': 'n/a',
        'long_name': 'Binary flag indicating presence (=1) and absence (=0)'}


def get_country_regions(country):
    if country == "Morocco":
        regions = ["Morocco", "Morocco (Western Saharan)"]
    elif country == "Portugal":
        regions = ["Portugal", "Portugal (Azores)", "Portugal (Madeira)"]
    elif country == "Spain":
        regions = ["Spain", "Spain (Canary Islands)"]
    elif country == "US":
        regions = ["US", "US (Alaska)", "US (Hawaii)"]
    else:
        regions = [f"{country}"]
    return regions


# Regions that are directly connected geographically
region_connections = {'Belgium': ['Belgium', 'France', 'Netherlands', 'UK', 'Other Waters'],
                      'Canada': ['Canada', 'US', 'US (Alaska)', 'Other Waters'],
                      'Denmark': ['Denmark', 'Germany', 'Sweden', 'Other Waters'],
                      'France': ['Belgium', 'France', 'Netherlands', 'Spain', 'UK', 'Other Waters'],
                      'Germany': ['Denmark', 'Germany', 'Netherlands', 'Sweden', 'Other Waters'],
                      'Dom. Rep.': ['Dom. Rep.', 'Haiti', 'Other Waters'],
                      'Haiti': ['Dom. Rep.', 'Haiti', 'Other Waters'],
                      'Ireland': ['Ireland', 'UK', 'Other Waters'],
                      'Mexico': ['Mexico', 'US', 'Other Waters'],
                      'Morocco': ['Morocco', 'Morocco (Western Saharan)', 'Spain', 'Spain (Canary Islands)', 'Other Waters'],
                      'Morocco (Western Saharan)': ['Morocco', 'Morocco (Western Saharan)', 'Spain (Canary Islands)', 'Other Waters'],
                      'Netherlands': ['Belgium', 'Denmark', 'Germany', 'Netherlands', 'UK', 'Other Waters'],
                      'Portugal': ['Morocco', 'Portugal', 'Spain', 'Other Waters'],
                      'Portugal (Azores)': ['Portugal (Azores)', 'Other Waters'],
                      'Portugal (Madeira)': ['Morocco', 'Portugal (Madeira)', 'Spain (Canary Islands)', 'Other Waters'],
                      'Spain': ['France', 'Morocco', 'Portugal', 'Spain', 'Other Waters'],
                      'Spain (Canary Islands)': ['Morocco', 'Morocco (Western Saharan)', 'Portugal (Madeira)', 'Spain (Canary Islands)', 'Other Waters'],
                      'Sweden': ['Denmark', 'Germany', 'Sweden', 'Other Waters'],
                      'UK': ['Belgium', 'Denmark', 'France', 'Germany', 'Ireland', 'Netherlands', 'UK', 'Other Waters'],
                      'US': ['Canada', 'Mexico', 'US', 'Other Waters'],
                      'US (Alaska)': ['Canada', 'US (Alaska)', 'Other Waters'],
                      'US (Hawaii)': ['US (Hawaii)', 'Other Waters']}

# Add Other Waters
region_connections['Other Waters'] = list(eez_names.keys())
region_connections['Other Waters'].append('Other Waters')


# Country specific run parameters
archer_nodes = {'Belgium': '3',
                'Canada': '3',
                'Denmark': '3',
                'France': '3',
                'Germany': '3',
                'Dom. Rep.': '3',
                'Haiti': '3',
                'Ireland': '3',
                'Mexico': '6',
                'Morocco': '3',
                'Netherlands': '3',
                'Portugal': '3',
                'Spain': '3',
                'Sweden': '3',
                'UK': '6',
                'US': '6'}

# Country specific run parameters
archer_queue = {'Belgium': 'standard',
                'Canada': 'standard',
                'Denmark': 'standard',
                'France': 'standard',
                'Germany': 'standard',
                'Dom. Rep.': 'standard',
                'Haiti': 'standard',
                'Ireland': 'standard',
                'Mexico': 'long',
                'Morocco': 'standard',
                'Netherlands': 'standard',
                'Portugal': 'standard',
                'Spain': 'standard',
                'Sweden': 'standard',
                'UK': 'long',
                'US': 'long'}

# Country specific run parameters
archer_wall_time = {'Belgium': '24:00:00',
                    'Canada': '24:00:00',
                    'Denmark': '24:00:00',
                    'France': '24:00:00',
                    'Germany': '24:00:00',
                    'Dom. Rep.': '24:00:00',
                    'Haiti': '24:00:00',
                    'Ireland': '24:00:00',
                    'Mexico': '36:00:00',
                    'Morocco': '24:00:00',
                    'Netherlands': '24:00:00',
                    'Portugal': '24:00:00',
                    'Spain': '24:00:00',
                    'Sweden': '24:00:00',
                    'UK': '36:00:00',
                    'US': '36:00:00'}

# Polygons that roughly outline countries
canada_outline = [[-47.2, 40.], [-47.2, 55.], [-63.7, 78.5], [-50., 86.8],
                  [-105., 86.8], [-142, 80.], [-142., 45.], [-80., 40.]]
canada_outline_poly = shapely.geometry.Polygon([[p[0], p[1]] for p in canada_outline])

# Earth's radius
earth_radius = 6378137.
