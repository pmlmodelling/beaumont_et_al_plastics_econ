""" This script calculates the stock of plastic in an EEZ

To do this, it:

1) For a given receiving region, cycles over all emitting countries.
2) For a given emitting country, cycles over all releases for that year and
before.
3) Sums the mass of plastic in each element that lies within the EEZ
of the receiving country.
4) This operation is repeated for each day in the year.
5) The output of the previous step is saved to file. From this, the
annual mean is calculated.

Usage
-----
python compute_plastic_stock_in_eezs.py -r <region> -y <year> -m <month>
"""
import sys
import numpy as np
import argparse
import pandas
import pathlib
from calendar import monthrange
import datetime
from collections import OrderedDict


from pylag.processing.ncview import Viewer

from shared import na_countries
from utils import get_pylag_file_list
from utils import get_weights
from project_paths import simulations_dir

import cython_helpers


def process_receiving_region(region, year, month, num_threads=8):
    """ Process data for the the receiving region `region`

    Stocks are estimated for each year, and are broken down
    by contributing country. Outputs are saved as pickle
    files.

    Parameters
    ----------
    region : str
        The region (EEZ) for which stocks are to be computed.

    year : int
        The year in which stocks will be computed.

    month : int
        The month in which stocks will be estimated.

    num_threads : int
        The number of threads to use in support of the calculation.
    """
    assert month in [m for m in range(1, 13)], \
        f"Must provide a valid month. Received `{month}`."

    print(f'Computing plastic stock for {region} in month {month:02} of year '
          f'{year}')

    # Read weights
    weights, weights_decay_coefs = get_weights(n_particles_prz, na_countries)

    # Read in valid boundary elements for the receiving region
    bdy_dir = '../Derived_data/grid_elements/EEZ'
    bdy_file_name = f'{bdy_dir}/grid_elements_for_{region}_EEZ_boundary.csv'
    bdy_elements = np.fromfile(bdy_file_name, sep=',')
    bdy_elements = np.sort(np.array(bdy_elements, dtype=np.int32))

    # Create data structure in which to store masses
    data = OrderedDict()
    data['Date'] = []
    for country in na_countries:
        data[country] = []

    # Compute the number of days we will need to cycle over
    days_in_month = monthrange(target_year, month)[1]

    # Loop over all days in the month
    days = [day for day in range(1, days_in_month+1)]
    for day_idx, day in enumerate(days):
        print(f'Processing data for day {day}')

        # The hour on which particles were released
        current_date = datetime.datetime(target_year, month, day,
                                         release_hour)

        # Save the current date
        data['Date'].append(current_date)

        # Cycle over all emitting countries
        for emitting_country in na_countries:
            print(f'Processing data for emitter {emitting_country}')
            # Set masses for this time point to 0.0, then sum over all runs
            data[emitting_country].append(0.0)

            # Get a list of all paths
            file_paths = get_pylag_file_list(pylag_root_dir,
                                             emissions_start_date,
                                             current_date,
                                             emitting_country)

            for file_path in file_paths:
                # Open the output file for reading
                pylag_viewer = Viewer(file_path, time_rounding=3600)

                n_groups = int(pylag_viewer._ds.dimensions['particles'].size / n_particles_prz)

                # Extract dates
                pylag_dates = pylag_viewer.date

                # Get the index of the current date
                tidx = pylag_dates.tolist().index(current_date)

                # Compute the weights, noting:
                #   - we account for decay as a function of time
                #   - time is given by tidx, the day number, as the outputs
                #     were saved every day
                #   - decay coeffs are per river, so we tile this array by
                #     the number of rivers
                decay_coefs = np.tile(weights_decay_coefs.loc[tidx].values,
                                      n_groups)
                decayed_weights = weights[emitting_country] * decay_coefs

                # Get host elems
                hosts = pylag_viewer('host_arakawa_a')[tidx].astype(np.int32)
                within = cython_helpers.match_elements(hosts,
                                                       bdy_elements,
                                                       num_threads=num_threads)
                # Compute particle masses
                particle_masses = within * decayed_weights

                # Add this mass to the total inventory
                data[emitting_country][-1] += particle_masses.sum()

    # Save the data to file
    pdf = pandas.DataFrame(data)

    # Sum across all countries
    pdf['All countries'] = pdf.sum(axis=1, numeric_only=True)

    # Create a directory in which to save the outputs
    out_dir = f"../Derived_data/plastic_stock/{region}/{year}/{month:02}"
    pathlib.Path(out_dir).mkdir(parents=True, exist_ok=True)
    out_file = f"{out_dir}/plastic_stock_in_{region}_{year}_{month:02}.pkl"
    pdf.to_pickle(out_file)

    return pdf


# Parse command line agruments
parser = argparse.ArgumentParser()
parser.add_argument('-r',
                    '--region',
                    help='EEZ region key (see shared.py)',
                    metavar='')
parser.add_argument('-y',
                    '--year',
                    help='Target year',
                    metavar='')
parser.add_argument('-m',
                    '--month',
                    help='Target month',
                    metavar='')

parsed_args = parser.parse_args(sys.argv[1:])

# Save args
target_region = parsed_args.region
target_year = int(parsed_args.year)
target_month = int(parsed_args.month)

num_threads = 8

# Scenario (only ocean_leeway available, given current runs)
scenario = 'ocean_leeway'

# Location where simulation outputs are stored
pylag_root_dir = simulations_dir

# The number of partcles released per release zone
n_particles_prz = 100

# The date when monthly emissions started
release_day = 1
release_hour = 12
emissions_start_date = datetime.datetime(2000, 1, release_day, release_hour)

# Limiting here the list of emitting countries to Belgium
na_countries = ['Belgium']

# Get masses
pdf = process_receiving_region(target_region, target_year, target_month,
                               num_threads)
