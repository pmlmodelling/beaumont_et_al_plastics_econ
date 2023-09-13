import datetime
import numpy as np
import pandas


def generate_grid(spacing, use_global_land_mask=True):
    """ Generate the grid on which to save concentrations

    Parameters
    ----------
    spacing : float
        The spacing between grid points in decimal degress.
    """

    # Set parameters for the grid edges
    n_lons = int(360./spacing)
    n_lats = int(180./spacing)

    print(f'There are {n_lons} longitude points')
    print(f'There are {n_lats} latitude points')

    # Compute longitude and latitude bin edge locations
    lon_bin_edges = np.linspace(-180., 180., n_lons+1)
    lat_bin_edges = np.linspace(-90., 90., n_lats+1)

    # Compute cell areas for a single longitude strip, then tile
    # for all longitudes. Assume a spherical earth.
    lat_bin_edges_r = np.radians(lat_bin_edges)
    areas = earth_radius**2 * np.radians(spacing) * (np.sin(lat_bin_edges_r[1:]) -
                                                     np.sin(lat_bin_edges_r[:-1]))

    # Create grid of cell centres
    lons_grid = lon_bin_edges[:-1] + 0.5*grid_spacing
    lats_grid = lat_bin_edges[:-1] + 0.5*grid_spacing

    # Compute mask
    lats2D, lons2D = np.meshgrid(lats_grid, lons_grid, indexing='ij')
    is_on_land = globe.is_land(lats2D.flatten(), lons2D.flatten())

    if use_global_land_mask:
        mask = is_on_land.reshape(lats2D.shape)
    else:
        mask = None

    # Compute areas
    areas = np.tile(areas[:, np.newaxis], (1, n_lons))

    return lons_grid, lats_grid, lon_bin_edges, lat_bin_edges, mask, areas


def get_pylag_file_list(pylag_root_dir, emissions_start_date, current_date,
                        emitting_country, release_day=1, release_hour=12):
    """ Return a list of PyLag output files

    Return a list of PyLag output files for releases that precede
    the current date. Releases were performed on at 1200 on the 1st
    of each month.

    Parameters
    ----------
    pylag_root_dir : str
        Root path to where PyLag output files are stored

    emissions_start_date : datetime.datetime
        The date on which plastic emissions started.

    current_date : datetime.datetime
        The current date.

    emitting_country : str
        The name of the emitting country.
    """
    assert current_date >= emissions_start_date, \
        'The current date precedes the emissions start date'

    # Form a list of months in a year
    release_months = [f'{month:02}' for month in range(1, 13)]

    # Container for the full list of file paths
    file_paths = []

    # Process the years leading up to the current year
    year = emissions_start_date.year
    while year < current_date.year:
        for month_str in release_months:
            if int(month_str) >= emissions_start_date.month:
                # Path to the run output file
                pylag_data_dir = (f'{pylag_root_dir}/{emitting_country}/{year}/'
                                  f'{month_str}/output')
                pylag_data_file = f'{pylag_data_dir}/pylag_1.nc'

                file_paths.append(pylag_data_file)

        year += 1

    # Process the current year by including only those runs where the
    # particle release date precedes the current date
    year = current_date.year
    for month_str in release_months:
        month = int(month_str)
        month_release_date = datetime.datetime(year,
                                               month,
                                               release_day,
                                               release_hour)

        if current_date >= month_release_date:
            pylag_data_dir = (f'{pylag_root_dir}/{emitting_country}/{year}/'
                              f'{month_str}/output')
            pylag_data_file = f'{pylag_data_dir}/pylag_1.nc'

            file_paths.append(pylag_data_file)
        else:
            break

    return file_paths


def get_connectivity_file_list(connectivity_root_dir, emissions_start_date,
                               current_date, emitting_country, release_day=1,
                               release_hour=12):
    """ Return a list of connectivity data files

    Return a list of connectivity data files for releases that precede
    `current_date`. Defaults parameters assume releases were performed
    at 1200 on the 1st of each month.

    Parameters
    ----------
    connectivity_root_dir : str
        Root path to where connectivity data files are stored

    emissions_start_date : datetime.datetime
        The date on which plastic emissions started.

    current_date : datetime.datetime
        The current date.

    emitting_country : str
        The name of the emitting country.
    """
    assert current_date >= emissions_start_date, \
        'The current date precedes the emissions start date'

    # Form a list of months in a year
    release_months = [f'{month:02}' for month in range(1, 13)]

    # Container for the full list of file paths
    file_paths = []

    # Process the years leading up to the current year
    year = emissions_start_date.year
    while year < current_date.year:
        for month_str in release_months:
            if int(month_str) >= emissions_start_date.month:
                # Path to the run output file
                connectivity_data_dir = (f'{connectivity_root_dir}/{year}/'
                                         f'{month_str}')
                connectivity_data_file = \
                    (f'{connectivity_data_dir}/'
                     f'{emitting_country}_connectivity_{year}_{month_str}.nc')

                file_paths.append(connectivity_data_file)

        year += 1

    # Process the current year by including only those runs where the
    # particle release date precedes the current date
    year = current_date.year
    for month_str in release_months:
        month = int(month_str)
        month_release_date = datetime.datetime(year,
                                               month,
                                               release_day,
                                               release_hour)

        if current_date >= month_release_date:
            # Path to the run output file
            connectivity_data_dir = (f'{connectivity_root_dir}/{year}/'
                                     f'{month_str}')
            connectivity_data_file = \
                (f'{connectivity_data_dir}/'
                 f'{emitting_country}_connectivity_{year}_{month_str}.nc')

            file_paths.append(connectivity_data_file)
        else:
            break

    return file_paths


def get_weights(n_particles_prz, na_countries):
    # Directory for particle weights
    weights_dir = (f'../Derived_data/particle_weights/'
                   f'{n_particles_prz}_particles/monthly')

    weights = {}
    for emitting_country in na_countries:
        # Read in weights for the emitting country
        weights_file = (f'{weights_dir}/'
                        f'monthly_particle_weights_{emitting_country}.csv')
        weights[emitting_country] = np.fromfile(weights_file, sep=',')

    # Read in weights decay coefficients
    weights_decay_coef_file_dir = (f'../Derived_data/particle_weights'
                                   f'/{n_particles_prz}_particles')
    weights_decay_coef_file = (f'{weights_decay_coef_file_dir}'
                               f'/weights_decay_coefficients_per_day.pkl')

    weights_decay_coefs = \
        pandas.read_pickle(weights_decay_coef_file).set_index('Day number')

    return weights, weights_decay_coefs
