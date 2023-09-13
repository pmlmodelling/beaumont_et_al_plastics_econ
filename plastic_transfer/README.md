# Plastic transfer modelling

The plastic transfer coefficients were generated using a Lagrangian particle tracking model. The model was used to simulate the movement of plastic particles released from rivers. The particles were advected by surface ocean currents and winds.

## Compute environment

The plastic transfer code will only run in a Linux/Unix environment. Due to the size of the datasets, it is recommended that the code is run on a computer with at least 16 GB of RAM. The full set of model runs require a significant amount of compute power and storage space, and are best conducted on a high performance computing cluster. To generate the results for the study, the authors used the UK ARCHER2 supercomputer.

## Particle tracking software

All particle tracking simulations were run using the particle tracking model [PyLag](https://github.com/pmlmodelling/pylag). PyLag's code is open source and free to use. Detailed installation instructions for PyLag can be found in [PyLag's online documenation](https://pylag.readthedocs.io/en/latest/). The core simulations performed in the study follow similar configuration steps to those described in [PyLag's online tutorials](https://pylag.readthedocs.io/en/latest/examples/index.html). The tutorials provide a detailed description of how the model is configured, and include direct links to pre-prepared driving data. As such, the tutorials represent a good starting point for learning how to use the model, and a demonstration of how it is used.

## Required input data

The work relies on five freely available datasets. Once downloaded, the paths to these datasets should be set in the module `./Analysis/project_paths.py`. The five datasets are:

* Plastic emissions data from [Meijer et al (2021)](https://figshare.com/articles/dataset/Supplementary_data_for_More_than_1000_rivers_account_for_80_of_global_riverine_plsatic_emissions_into_the_ocean_/14515590);
* Data on national boundaries from the [Natural Earth](https://www.naturalearthdata.com) dataset. This data is accessible via the [GeoPandas](https://geopandas.org/) library, and does not need to be downloaded;
* Data on Exclusive Economic Zones (EEZs) from the [Marine Regions](https://www.marineregions.org/) dataset;
* Surface ocean velocities for 1994 - 2015 from the global ocean physcis reanalysis at 1/12 deg (DOI:  10.48670/moi-00021), which can be downloaded from the [CMEMS Catalogue](https://data.marine.copernicus.eu/);
* 10 m winds from 1994 - 2015 from the ERA5 reanalysis (DOI: 10.24381/cds.adbb2d47) which can be downloaded from the [Climate Data Store](https://cds.climate.copernicus.eu/).

The directory `./Data` is suggested as a location to store the data. A set of detailed
instructions on how to download each of the datasets is provided in a collection of READMEs, which can be found in the respective sub-directories.

## Running the model

Simplified configration and analysis scripts can be found in the `./Analysis` directory. More details on the functionality of each script can be found in the README `./Analysis/README.md`.

## Results

Tables giving the stock matrix for the years 2012, 2013 and 2014 can be found in the `Results` directory.
