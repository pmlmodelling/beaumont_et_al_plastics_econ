# Atmosphere data

Atmosphere input data should be saved here. It consists of 10 m wind velocity components. The full dataset used in the study covers the period 1995 - 2015 and is 100s Gb in size. To replicate the results, the dataset must be downloaded from the Climate Data Store (Product ID: [reanalysis-era5-single-levels](https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-single-levels?tab=overview)).

For this study, the data were downloaded as monthly files usinng the cdsapi python package. The command takes the form:

```python
import cdsapi


c = cdsapi.Client()

c.retrieve(
    'reanalysis-era5-single-levels',
    {
        'product_type': 'reanalysis',
        'variable': [
            '10m_u_component_of_wind', '10m_v_component_of_wind',
        ],
        'year': '2000',
        'month': '01',
        'day': [
            '01', '02', '03',
            '04', '05', '06',
            '07', '08', '09',
            '10', '11', '12',
            '13', '14', '15',
            '16', '17', '18',
            '19', '20', '21',
            '22', '23', '24',
            '25', '26', '27',
            '28', '29', '30',
            '31',
        ],
        'time': [
            '00:00', '01:00', '02:00',
            '03:00', '04:00', '05:00',
            '06:00', '07:00', '08:00',
            '09:00', '10:00', '11:00',
            '12:00', '13:00', '14:00',
            '15:00', '16:00', '17:00',
            '18:00', '19:00', '20:00',
            '21:00', '22:00', '23:00',
        ],
        'format': 'grib',
    },
    f'./era5_winds_2000_01.grib')
```

The resulting grib files must be converted to the NetCDF file format. This can be done with several packages, including the tool `grid_to_netcdf`.

File names should follow the naming convention:

...
...
era5_winds_2000_01.nc
era5_winds_2000_02.nc
...
...

Example NetCDF header information is provided in the file:

./HEADER_era5_winds_2000_01.txt

which can be found in the current working directory.
