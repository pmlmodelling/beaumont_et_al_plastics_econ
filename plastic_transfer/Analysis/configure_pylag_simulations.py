""" Configure PyLag simulations

From template files, create all PyLag input files required for
running the particle tracking simulations. This includes:

1) Set up a directory for each country from which particles
will be released.

2) Wthin each country directory, set up a year directory
corresponding to the year in which particles are to be
released.

3) Within the year directory of each country directory, create
a set of month directories.

4) Within each month directory for all countries, create:

4.1) An input directory containing the initial positions file
and the grid metrics file.

4.2) The pylag configuration file.

4.3) A run script which will launch the model.

Notes
-----

- In this step, we allow for paths being different depending
on whether the model is run on a PML desktop or on ARCHER2.
"""
import os
import pathlib
import stat
import configparser

from project_paths import cmems_data_dir, era5_data_dir, simulations_dir

def get_root_run_directory():
    root_dir = simulations_dir

    return root_dir


def get_input_paths():
    inputs_dir = '../Inputs'
    ocean_forcing_dir = cmems_data_dir
    atmos_forcing_dir = era5_data_dir

    return inputs_dir, ocean_forcing_dir, atmos_forcing_dir


def create_ocean_leeway_config(cf, ocean_data_dir, ocean_grid_metrics,
                               atmos_data_dir, atmos_grid_metrics,
                               wind_factor,
                               hbc='reflecting'):
    # Set paths for ocean data
    cf.set('OCEAN_DATA', 'data_dir', ocean_data_dir)
    cf.set('OCEAN_DATA', 'grid_metrics_file', ocean_grid_metrics)

    # Set paths for atmospheric data
    cf.set('ATMOSPHERE_DATA', 'name', 'standard')
    cf.set('ATMOSPHERE_DATA', 'data_dir', atmos_data_dir)
    cf.set('ATMOSPHERE_DATA', 'grid_metrics_file', atmos_grid_metrics)

    # Specify the type of windage calculator we will use
    cf.set('WINDAGE', 'windage_calculator', 'zero_deflection')
    cf.set('ZERO_DEFLECTION_WINDAGE_CALCULATOR', 'wind_factor', wind_factor)

    # Assert we are not running with wave data
    cf.set('WAVE_DATA', 'name', 'none')
    cf.set('STOKES_DRIFT', 'stokes_drift_calculator', 'none')

    # Set horizontal boundary condition
    cf.set('BOUNDARY_CONDITIONS', 'horiz_bound_cond', hbc)

    return cf


def create_ocean_only_config(cf, ocean_data_dir, ocean_grid_metrics,
                             hbc='reflecting'):
    # Set paths for ocean data
    cf.set('OCEAN_DATA', 'data_dir', ocean_data_dir)
    cf.set('OCEAN_DATA', 'grid_metrics_file', ocean_grid_metrics)

    # Assert we are not running with wave data
    cf.set('WAVE_DATA', 'name', 'none')
    cf.set('STOKES_DRIFT', 'stokes_drift_calculator', 'none')

    # Assert we are not running with atmospheric data
    cf.set('ATMOSPHERE_DATA', 'name', 'none')
    cf.set('WINDAGE', 'windage_calculator', 'none')

    # Set horizontal boundary condition
    cf.set('BOUNDARY_CONDITIONS', 'horiz_bound_cond', hbc)

    return cf


# The scenario
# ------------
#
# standard_run - Standard run with surface ocean currents and Leeway at 2 %.
# ocean_only - Run that uses surface ocean currents only.
# wind_factor - Standard run in which the wind factor is varied.
scenario = 'standard_run'

# The list of countries from which to perform releases
countries = ['Belgium']

# The number of particles to release per release zone
n_particles = 100

# The release year
release_year = 2000
release_year_str = str(release_year)

# The year in which the simulation terminates
end_datetime = '2015-01-01 12:00:00'

# Release months
months = range(1, 13)
month_strs = ['{0:02}'.format(month) for month in months]

# The wind factor
wind_factor = '0.02'

# Default horizontal boundary condition
hbc = 'reflecting'

# Get the root run directory
root_run_dir = get_root_run_directory()

# Set run directory based on the scenario
if scenario == 'standard_run':
    scenario_run_dir = f'{root_run_dir}/ocean_leeway'
elif scenario == 'ocean_only':
    scenario_run_dir = f'{root_run_dir}/ocean_only'
elif scenario == 'wind_factor':
    # Override wind factor
    wind_factor_percent = '1'
    wind_factor = f'0.0{wind_factor_percent}'
    scenario_run_dir = f'{root_run_dir}/wind_factor/{wind_factor_percent}_percent'
else:
    raise RuntimeError(f'Unsupported scenario {scenario}')

# Create the scenario directory
pathlib.Path(scenario_run_dir).mkdir(parents=True, exist_ok=True)

# Get paths to the input files
inputs_dir, ocean_forcing_dir, atmos_forcing_dir = get_input_paths()

# Loop over all countries
for country in countries:
    country_dir = f'{scenario_run_dir}/{country}'
    year_dir = f'{country_dir}/{release_year}'

    # Make year directory
    pathlib.Path(year_dir).mkdir(parents=True, exist_ok=True)

    for month_str in month_strs:
        month_dir = f'{year_dir}/{month_str}'
        pathlib.Path(month_dir).mkdir(parents=True, exist_ok=True)

        # Set up the run folder
        run_inputs_dir = f'{month_dir}/input'
        pathlib.Path(run_inputs_dir).mkdir(parents=True, exist_ok=True)

        # Link to the ocean grid metrics file
        ocean_grid_metrics_file_name = f'{inputs_dir}/grid_metrics/grid_metrics_surface_ocean.nc'
        ocean_grid_metrics_link_name = f'{run_inputs_dir}/grid_metrics_surface_ocean.nc'
        try:
            os.symlink(ocean_grid_metrics_file_name,
                       ocean_grid_metrics_link_name)
        except FileExistsError:
            pass

        # Link to the atmosphere grid metrics file
        atmos_grid_metrics_file_name = f'{inputs_dir}/grid_metrics/grid_metrics_atmosphere.nc'
        atmos_grid_metrics_link_name = f'{run_inputs_dir}/grid_metrics_atmosphere.nc'
        try:
            os.symlink(atmos_grid_metrics_file_name,
                       atmos_grid_metrics_link_name)
        except FileExistsError:
            pass

        # Create link to initial positions data in the run inputs directory
        src_positions_file = f'{inputs_dir}/{n_particles}_particles/positions/initial_positions_{country}.dat'
        if not os.path.isfile(src_positions_file):
            raise RuntimeError(f'File {src_positions_file} does not exist')

        dst_positions_file_link = f'{run_inputs_dir}/initial_positions.dat'
        try:
            os.symlink(src_positions_file, dst_positions_file_link)
        except FileExistsError:
            pass

        # Set the start datetime
        start_datetime = f'{release_year_str}-{month_str}-01 12:00:00'

        # Create the run configuration file
        template_config = './templates/pylag.cfg.TEMPLATE'
        config = configparser.ConfigParser()
        config.read(template_config)

        # Set start and end times
        config.set('SIMULATION', 'start_datetime', start_datetime)
        config.set('SIMULATION', 'end_datetime', end_datetime)

        # Set parameters depending on the run scenario
        if scenario in ['standard_run', 'grounding', 'wind_factor']:
            config = create_ocean_leeway_config(config,
                                                ocean_data_dir=ocean_forcing_dir,
                                                ocean_grid_metrics=ocean_grid_metrics_link_name,
                                                atmos_data_dir=atmos_forcing_dir,
                                                atmos_grid_metrics=atmos_grid_metrics_link_name,
                                                wind_factor=wind_factor,
                                                hbc=hbc)
        elif scenario == 'ocean_only':
            config = create_ocean_only_config(config,
                                              ocean_data_dir=ocean_forcing_dir,
                                              ocean_grid_metrics=ocean_grid_metrics_link_name,
                                              hbc=hbc)
        else:
            raise RuntimeError(f'Unsupported scenario {scenario}')

        # Write the file out again
        run_config = f'{month_dir}/pylag.cfg'
        with open(run_config, 'w') as file:
            config.write(file)
            
        # Add run script
        template_run_script = './templates/run_pylag.sh.TEMPLATE'
        with open(template_run_script, 'r') as file :
            filedata = file.read()
        
        # Replace the target strings
        filedata = filedata.replace('__SIMULATION_DIR__', month_dir)

        # Write the file out again
        month_run_script = f'{month_dir}/run_pylag.sh'
        with open(month_run_script, 'w') as file:
            file.write(filedata)

        # Add execute permissions
        st = os.stat(month_run_script)
        os.chmod(month_run_script, st.st_mode | stat.S_IEXEC) 
