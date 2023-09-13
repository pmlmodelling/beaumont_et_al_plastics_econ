""" Create a file with weight decay coefficients

The weights file is used to model the loss/removal of plastic particles
from the surface ocean.

We use a simple model of exponential decay:

w(t) = w(t=0) * exp(-k_i*t), where w is the "weight" of the modelled plastic
particle (in tonnes), t is time (in days) and k_i is the decay coefficient
(day^-1). We root this against what is approximately the steady state
mass of plastic in the ocean, based on a model of linear decay. This
gives us the steady state mass y = M/k, where M is the total flux of plastic
into the ocean per year. Creating a spread of 100 k values from 0.1 to 10, and
associating each with a fraction M/100 of the total in flux, we achieve a
steady state concentration which is approx. M/2.
"""
import numpy as np
import pandas
import datetime
from collections import OrderedDict

# Constants
# ---------
years_per_day = 1/365.25

# Create array of datetime strings
# --------------------------------
start_datetime = datetime.datetime.strptime("2000-01-01 12:00:00",
                                            "%Y-%m-%d %H:%M:%S")
#start_datetime = datetime.datetime.strptime("1995-01-01 12:00:00",
#                                            "%Y-%m-%d %H:%M:%S")
end_datetime = datetime.datetime.strptime("2015-01-01 12:00:00",
                                          "%Y-%m-%d %H:%M:%S")

# Compute the total number of days (plus one to capture start and end points)
n_days = (end_datetime - start_datetime).days + 1

# Add array of day numbers to a data dict
data = OrderedDict()
data["Day number"] = np.arange(0, n_days)

# Particles released per river
n_particles = 100

# Create array of gamma values (units: yr^-1)
gammas = np.linspace(.1, 10, n_particles)

# Initialise a dictionary for the precomputed decay coefficients
for idx, gamma in enumerate(gammas):
    data[f"k{idx+1}"] = []

# Fill out the dictionary with pre-computed decay coefficients
for day_number in data['Day number']:
    for idx, gamma in enumerate(gammas):
        data[f"k{idx+1}"].append(np.exp(-day_number * gamma * years_per_day))

# Save the dictionary to file
df = pandas.DataFrame(data)
df.to_pickle(f'../Derived_data/particle_weights/{n_particles}_particles/weights_decay_coefficients_per_day.pkl')
#df.to_pickle(f'../Derived_data/particle_weights/{n_particles}_particles/weights_decay_coefficients_per_day_1995.pkl')
