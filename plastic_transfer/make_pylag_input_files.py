import os
import numpy as np
from netCDF4 import Dataset
from scipy.spatial import cKDTree
import geopandas
from matplotlib import pyplot as plt
import cartopy.feature as cfeature
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
    
from pylag.math import geographic_to_cartesian_coords_python
from pylag.processing.coordinate import utm_from_lonlat, lonlat_from_utm
from pylag.processing.release_zone import create_release_zone

from marine_boundaries import remove_us_west_coast_rivers
from marine_boundaries import remove_french_guiana_rivers

from shared import na_countries

from plot_utils import make_plot


# What fraction of all river inputs should be accounted for?
input_fraction = 1.0

# Release zone radius (m)
radius = 1000.0

# Number of particles to be released from each location
n_particles_target = 100

# Release depths
depth_below_surface = 0.0

# Remove us west coast rivers
use_us_west_coast_rivers = True

# Remove French Guiana rivers
use_french_guiana_rivers = False

# Temporary limit on na_countries
#na_countries = ['France']

# Read in plastics data
meijer_dir = './Derived_data/meijer_midpoint_emissions'
gdf = geopandas.read_file(f'{meijer_dir}/Meijer2021_midpoint_emissions_with_countries.shp')

# Rename column
gdf = gdf.rename(columns={'dots_exten': 'Plastic emissions'})

# Path for grid metrics file(s)
grid_metrics_1_12_deg = './Inputs/grid_metrics/grid_metrics_surface_ocean.nc'

# Create positions and volume data dirs if they have not been created already
output_root_dir = f'./Inputs/{n_particles_target}_particles'
if not os.path.isdir(output_root_dir):
    os.mkdir(output_root_dir)

positions_dir = f'{output_root_dir}/positions'
if not os.path.isdir(positions_dir):
    os.mkdir(positions_dir)

emissions_dir = f'{output_root_dir}/emissions'
if not os.path.isdir(emissions_dir):
    os.mkdir(emissions_dir)

# Create a new data frame for the selected north atlantic countries
gdf_list = []
for country in na_countries:
    if country in gdf["countries"].unique():
        gdf_tmp = gdf[gdf["countries"] == country].copy()

        if country == "US":
            if not use_us_west_coast_rivers:
                gdf_tmp = remove_us_west_coast_rivers(gdf_tmp)

        if country == "France":
            if not use_french_guiana_rivers:
                gdf_tmp = remove_french_guiana_rivers(gdf_tmp)

        gdf_tmp.sort_values(by=['Plastic emissions'], ascending=False, inplace=True)
        gdf_tmp['cumsum_normed'] = (gdf_tmp['Plastic emissions'].cumsum(axis=0) / 
                                    gdf_tmp['Plastic emissions'].sum())
        if True in (gdf_tmp['cumsum_normed'] < input_fraction).values:
            gdf_tmp = gdf_tmp[gdf_tmp['cumsum_normed'] <= input_fraction]
        else:
            gdf_tmp = gdf_tmp.head(1)
        gdf_list.append(gdf_tmp)
    else:
        print(f'Could not find {country}')

# How many rivers for each country?
for _gdf, country in zip(gdf_list, na_countries):
    print(f"\nCountry {country} has {_gdf.shape[0]} rivers that account "\
          f"for {input_fraction} of it's total plastic inputs")

# Read in grid metrics info
gm = Dataset(grid_metrics_1_12_deg)
lonc = gm['longitude_c'][:]
latc = gm['latitude_c'][:]
maskc = gm.variables['mask_c'][:]

# Indices for ocean elements
ocean_elements = np.asarray(maskc == 0).nonzero()[0]

# Limit grid to ocean elements only
lonc = lonc[ocean_elements]
latc = latc[ocean_elements]

# Convert to Cartesian coords and build a KDE tree
lonc_radians = np.radians(lonc)
latc_radians = np.radians(latc)

# Convert to Cartesian coordinates
x, y, z = geographic_to_cartesian_coords_python(lonc_radians, latc_radians)
grid_points = np.column_stack([x, y, z])

# Form KDTree
tree = cKDTree(grid_points)

# Write river data to file. One file per country, one group per river.
plot = True
for _gdf, country in zip(gdf_list, na_countries):

    # Get river coordinates in radians
    lon_rivers = np.radians([location.x for location in _gdf['geometry']])
    lat_rivers = np.radians([location.y for location in _gdf['geometry']])

    # Compute river Cartesian coordinates
    x_rivers, y_rivers, z_rivers = geographic_to_cartesian_coords_python(lon_rivers,
                                                                         lat_rivers)
    river_points = np.column_stack([x_rivers, y_rivers, z_rivers])

    # Query nearest neighbours
    distances, indices = tree.query(river_points, k=1)

    # River input coordinates snapped to centroids on the model grid
    lon_rivers_on_grid = lonc[indices]
    lat_rivers_on_grid = latc[indices]

    # Plot locations to check
    # -----------------------
    if plot:
        print('\nPlotting data for {}'.format(country))

        # Create figure
        fig, ax = make_plot()

        # Extents are global
        extents = np.array([-180, 180, -90, 90])
        ax.set_extent(extents, ccrs.PlateCarree())

        # Add coastline
        ax.add_feature(cfeature.NaturalEarthFeature(category='physical', name='coastline',
            scale = '10m', facecolor = 'none', edgecolor = 'black', linewidth=.5))

        # Add borders
        ax.add_feature(cfeature.BORDERS)

        # Add on river data
        ax.scatter(lon_rivers_on_grid, lat_rivers_on_grid, c='b', s=10)

        ax.set_title('{} river locations'.format(country))


    # Convert to UTM coordinates
    eastings = []
    northings = []
    epsg_codes = []
    for x1, x2 in zip(lon_rivers_on_grid, lat_rivers_on_grid):
        easting, northing, epsg_code = utm_from_lonlat(x1, x2)
        eastings.append(easting[0])
        northings.append(northing[0])
        epsg_codes.append(epsg_code)

    release_zones = []
    for i, (easting, northing) in enumerate(zip(eastings, northings)):
        group_id = i

        # Create the release zone
        release_zone = create_release_zone(group_id = group_id,
                                           radius = radius,
                                           centre = [easting, northing],
                                           n_particles = n_particles_target,
                                           depth = depth_below_surface,
                                           random = True)

        release_zones.append(release_zone)

    # Write position data to file
    # ---------------------------
    all_lons = []
    all_lats = []

    # Total number of particles
    n = 0
    for release_zone in release_zones:
        n = n + release_zone.get_number_of_particles()

    f = open(f'{positions_dir}/initial_positions_{country}.dat', 'w')
    f.write(str(n) + '\n')
    for i, release_zone in enumerate(release_zones):
        # Convert utm coords to degrees
        lons, lats = lonlat_from_utm(release_zone.get_eastings(),
                                     release_zone.get_northings(),
                                     epsg_code=epsg_codes[i])
        depths = release_zone.get_depths()

        all_lons = all_lons + lons.tolist()
        all_lats = all_lats + lats.tolist()

        for x, y, z in zip(lons, lats, depths):
            line = str(release_zone.get_group_id()) + ' ' + str(x) + ' ' + str(y) + ' ' + str(z) + '\n'
            f.write(line)
    f.close()

    # Write emissions data to file
    # ----------------------------
    _gdf.to_csv(f'{emissions_dir}/emissions_{country}.csv')

# If plot, display these
if plot:
    plt.show()

