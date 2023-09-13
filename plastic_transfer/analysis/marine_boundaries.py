""" Module to assist working with marine boundary data
"""
import geopandas
import shapely
import numpy as np


def read_shapefile(data_dir, bdy_type):
    """ Read in the shape file for country level marine boundaries

    There are three options, which are selected using the argument
    `boundary_type`:

    '12NM' : The 12 nautical mile limit.

    '24NM' : The 24 nautical mile limit.

    'EEZ' : The exclusive economic zone.

    Parameters
    ----------
    data_dir : str
        Path to boundary data.

    bdy_type : str
        The boundary type.    

    Returns
    -------
     : geopandas.GeoDataFrame
        Boundary data frame
    """
    if bdy_type == "12NM":
        shape_file_name = f'{data_dir}/12NM/World_12NM_v3_20191118/eez_12nm_v3.shp'
    elif bdy_type == "24NM":
        shape_file_name = f'{data_dir}/24NM/World_24NM_v3_20191118/eez_24nm_v3.shp'
    elif bdy_type == "EEZ":
        shape_file_name = f'{data_dir}/EEZ/World_EEZ_v11_20191118/eez_v11.shp'
    else:
        raise ValueError('Invalid boundary type: {bdy_type!r}')

    return geopandas.read_file(shape_file_name)


def get_eez_region(gdf, geoname):
    """ Search the data frame for the correct entry

    Parameters
    ----------
    gdf : geopandas.GeoDataFrame
        Data frame.

    geoname : str
        Country EEZ long name (e.g. 'Yemeni Exclusive Economic Zone').

    Returns
    -------
     : geopandas.GeoDataFrame
        A new data frame with a single entry for the EEZ of interest.
    """
    # Check that some data was found
    if (all_regions := gdf[gdf['GEONAME'] == geoname]).empty:
        raise RuntimeError(f'Failed to find any marine boundary data for '
                           f'country {geoname!r}.')

    # Check there is only one entry
    if len(all_regions) == 1:
        return all_regions
    else:
        raise RuntimeError(f'Failed to find marine boundary data specific to '
                           f'country {geoname!r} only.')


def remove_us_west_coast_rivers(gdf):
    ll = [-101.8, 22.9]
    lr = [-50.0, 20.9]
    ur = [-45.0, 56.4]
    ul = [-111, 61.0]
    point_list = [ll, lr, ur, ul]
    poly = shapely.geometry.Polygon([[p[0], p[1]] for p in point_list])

    in_out = []
    for point in gdf['geometry']:
        if point.within(poly):
            in_out.append(True)
        else:
            in_out.append(False)

    return gdf[in_out]


def remove_french_guiana_rivers(gdf, verbose=True):
    # Polygon covering French Guiana
    ll = [-60, 0.0]
    lr = [-40.0, 0.0]
    ur = [-40.0, 10.0]
    ul = [-60.0, 10.0]
    french_guiana_point_list = [ll, lr, ur, ul]
    poly = shapely.geometry.Polygon([[p[0], p[1]] for p in french_guiana_point_list])


    in_out = []
    for point in gdf['geometry']:
        if point.within(poly):
            in_out.append(True)
        else:
            in_out.append(False)

    # Convert to array
    in_out = np.array(in_out)

    if verbose:
        n_french_guiana_rivers = np.asarray(in_out==True).sum()
        n_euro_france_rivers = np.asarray(in_out==False).sum()

        # Compute plastic massese associated with these
        plastic_emissions_from_french_rivers = gdf['Plastic emissions'].sum()
        plastic_emissions_from_euro_france_rivers = \
            gdf[~in_out]['Plastic emissions'].sum()
        plastic_emissions_from_french_guiana_rivers = \
            gdf[in_out]['Plastic emissions'].sum()

        print(f"\nRemoving French Guiana rivers")
        print(f'\nIn total, there are {len(gdf)} french rivers with '\
              f'emissions of {plastic_emissions_from_french_rivers} tonnes per annum')
        print(f'\n{n_euro_france_rivers} of these belonged to European '\
              f'France with emissions of {plastic_emissions_from_euro_france_rivers} '\
              f'tonnes per annum')
        print(f'\n{n_french_guiana_rivers} of these belonged to French Guiana with '\
              f'emissions of {plastic_emissions_from_french_guiana_rivers} tonnes '\
              f'per annum')

    # Return the points that aren't within the French Guiana polygon
    return gdf[~in_out]


def reassign_madeira_rivers(gdf, verbose=True):
    # Polygon covering Madeira
    ll = [-18.0, 32.0]
    lr = [-15.0, 32.0]
    ur = [-15.0, 34.0]
    ul = [-18.0, 34.0]
    madeira_point_list = [ll, lr, ur, ul]
    poly = shapely.geometry.Polygon([[p[0], p[1]] for p in madeira_point_list])


    in_out = []
    for point in gdf['geometry']:
        if point.within(poly):
            in_out.append(True)
        else:
            in_out.append(False)

    # Convert to array
    in_out = np.array(in_out)

    gdf.loc[in_out, "countries"] = "Portugal"

    return gdf
