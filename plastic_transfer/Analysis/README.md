# Plastic transfer configuration and analysis scripts

## Installation

In a Linux/Unix environment, begin by install PyLag by following [PyLag's online installation instructions](https://pylag.readthedocs.io/en/latest/install/installation.html).

Once PyLag is installed, a small number of extra dependencies should be installed
using the supplied requirements.txt file. Assuming Conda was used to install PyLag, this can be done by running the following
command in the terminal:

```bash
conda install --yes --file requirements.txt
```

If the installation takes a long time, consider using *mamba* instead of *conda*. With Mamba, the command would be:

```bash
conda install --yes mamba
mamba install --yes --file requirements.txt
```

and installation times should be less than one minute.

## Contents

The directory contians the following core scripts, which should be edited/run in the following order in a Linux or Unix environment.

* `project_paths.py` - Edit to set paths.
* `cython_helpers.pyx` and `build_cython_modules.py` - helper functions written in Cython for speed. The corresponding extension module should first be built by executing the build script and saving the shared library in place.

```bash
python build_cython_modules.py build_ext --inplace
```

* `add_countries_to_meijer_2021_river_data.py` - Add country info to the Meijer river data.
* `create_ocean_grid_metrics_file.py` - Create ocean grid metrics file needed by PyLag.
* `create_atmosphere_grid_metrics_file.py` - Create atmosphere grid metrics file needed by PyLag
* `make_pylag_input_files.py` - Script to make particle initial positions files needed by PyLag.
* `configure_pylag_simulations.py` - Script to configure PyLag simulations. This also creates run script(s) in your simulations directory, which must be executed.
* `associate_grid_elements_with_marine_boundaries.py` - Script which associates ocean elements with EEZs. This is used to simplify the calculation of stocks.
* `compute_connectivity_metrics.py` - Script which flags whether or not particles are in a given EEZ at a given point in time. The emitting country is passed in as a command line argument (e.g. Belgium).
* `compute_plastic_stock_in_eezs.py` - Script which computes the mass of plastic in each EEZ.