# Atmosphere data

Ocean input data should be saved here. It consists of surface u and v velocity components. The full dataset used in the study covers the period 1995 - 2015 and is 100s Gb in size. To replicate the results, the dataset must be downloaded from the CMEMS catalogue (Product ID: [GLOBAL_MULTIYEAR_PHY_001_030](https://data.marine.copernicus.eu/product/GLOBAL_MULTIYEAR_PHY_001_030/description)).

For this study, the data were downloaded as monthly files using motuclient. The motuclient command takes the form:

```bash
python3 -m motuclient --user <CMEMS_USER_NAME> --pwd <CMEMS_PASSWORD> 
                      --motu http://my.cmems-du.eu/motu-web/Motu --service-id GLOBAL_REANALYSIS_PHY_001_030-TDS
                      --product-id global-reanalysis-phy-001-030-daily --longitude-min -180.
                      --longitude-max 179.9166717529297 --latitude-min -75.
                      --latitude-max 90. --date-min "2000-01-01 12:00:00"
                      --date-max "2000-31-01 12:00:00" --depth-min 0.493 --depth-max 0.4942
                      --variable uo --variable vo --out-dir ./ --out-name DAILY_GLOBAL_REANALYSIS_PHY_001_030-TDS_uv_2000_01.nc
```

File names should follow the naming convention:

...
...
DAILY_GLOBAL_REANALYSIS_PHY_001_030-TDS_uv_2000_01.nc
DAILY_GLOBAL_REANALYSIS_PHY_001_030-TDS_uv_2000_02.nc
...
...

Example NetCDF header information is provided in the file:

./HEADER_DAILY_GLOBAL_REANALYSIS_PHY_001_030-TDS_uv_2000_01.txt

which can be found in the current working directory.