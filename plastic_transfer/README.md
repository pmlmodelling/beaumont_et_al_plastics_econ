# Plastic transfer modelling

This collection of scripts supports a workflow which was
used to generate the plastic transfer coefficients in
Breaumont_et_al_submitted. The scripts rely on a number
of other packages, as listed in the file `requirements.txt`.

## Particle tracking software

All particle tracking simulations were run using the particle
tracking model [PyLag](https://github.com/pmlmodelling/pylag).
PyLag's code is open source and free for others to use. General
details on using PyLag can be found in its online
[documentation](https://pylag.readthedocs.io/en/latest/).

## Required input data

The work relies on three freely available datasets which must be
downloaded separately. Once downloaded, the paths to these datasets
should be set in the module `project_paths.py`. The three datasets are:

* Plastic emissions data from [Meijer et al (2021)](https://figshare.com/articles/dataset/Supplementary_data_for_More_than_1000_rivers_account_for_80_of_global_riverine_plsatic_emissions_into_the_ocean_/14515590);
* Surface ocean velocities for 1994 - 2015 from the global ocean physcis reanalysis at 1/12 deg (DOI:  10.48670/moi-00021), which can be downloaded from the [CMEMS Catalogue](https://data.marine.copernicus.eu/);
* 10 m winds from 1994 - 2015 from the ERA5 reanalysis (DOI: 10.24381/cds.adbb2d47) which can be downloaded from the [Climate Data Store](https://cds.climate.copernicus.eu/).

## Contents

The repository contians the following core scripts, which should be edited/run in the following order in a Linux or Unix environment.

* `project_paths.py` - Edit to set paths.
* `cython_helpers.pyx` and `build_cython_modules.py` - helper functions written in Cython for speed. The corresponding extension module should first be built by executing the build script and saving the shared library in place.
* `add_countries_to_meijer_2021_river_data.py` - Add country info to the Meijer river data.
* `create_ocean_grid_metrics_file.py`` - Create ocean grid metrics file needed by PyLag.
* `create_atmosphere_grid_metrics_file.py`` - Create atmosphere grid metrics file needed by PyLag
* `make_pylag_input_files.py` - Script to make particle initial positions files needed by PyLag.
* `configure_pylag_simulations.py` - Script to configure PyLag simulations. This also creates run script(s) in your simulations directory, which must be executed.
* `associate_grid_elements_with_marine_boundaries.py` - Script which associated ocean elements with EEZs. This is used to simplify the calculation of stocks.
* `compute_connectivity_metrics.py` - Script which flags whether or not particles are in a given EEZ at a given point in time. The emitting country is passed in as a command line argument (e.g. Belgium).
* `compute_plastic_stock_in_eezs.py` - Script which computes the mass of plastic in each EEZ.