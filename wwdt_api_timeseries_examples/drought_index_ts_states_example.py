import requests
import pandas as pd


Access_Token = 'API Key Here'


# Example for SPI Nevada
# spi_values_10_2023_05.tiff: May spi with 10 month accumulation
# Values from 1990 to 2023

params = {
    'dataset': 'PRISM_MONTHLY',
    'variable': 'spi',
    'area_reducer': 'mean',
    'start_date': '1990-01-01',
    'end_date': '2023-12-31',
    'start_year': '1895', # start year climatology
    'end_year': '2022',   # end year climatology
    'accumulation': '10', # accumulation period
    'distribution': 'gamma', # gamma is used for spi
    'region': 'states',
    'sub_choices': "['Nevada']", # this has to be a string
    'filter_by': 'Name', # Property to filter by
}

url = 'http://dev.climateengine.org/timeseries/standard_index/climate_engine_asset'    
r = requests.get(url, params=params, headers={'Authorization': Access_Token}, verify=False)
response = r.json()
# Convert Json file to csv
d = []
for feat in response:
    meta = feat['Metadata']
    for sub in feat['Data']:
        sub.update(meta)
        d.append(sub)
df = pd.DataFrame(d)
df['Date'] = pd.to_datetime(df['Date'])
df['month'] = df['Date'].dt.month
df_spi = df.loc[df['month'] == 5,['Date', 'spi']]



# Example for SPEI
# spei_values_72_2023_06.tiff: June spei with 72 month accumulation
# Values from 1990 to 2023

params = {
    'dataset': 'PRISM_MONTHLY',
    'variable': 'speih',
    'area_reducer': 'mean',
    'start_date': '1990-01-01',
    'end_date': '2023-12-31',
    'start_year': '1895', # start year climatology
    'end_year': '2022',   # end year climatology
    'accumulation': '72', # accumulation period
    'distribution': 'loglogistic', # loglogistic is used for spei
    'region': 'states',
    'sub_choices': "['Nevada']", # this has to be a string
    'filter_by': 'Name', # Property to filter by
}

url = 'http://dev.climateengine.org/timeseries/standard_index/climate_engine_asset'    
r = requests.get(url, params=params, headers={'Authorization': Access_Token}, verify=False)
response = r.json()
# Convert Json file to csv
d = []
for feat in response:
    meta = feat['Metadata']
    for sub in feat['Data']:
        sub.update(meta)
        d.append(sub)
df = pd.DataFrame(d)
df['Date'] = pd.to_datetime(df['Date'])
df['month'] = df['Date'].dt.month
df_spei = df.loc[df['month'] == 6,['Date', 'speih']]


# Example for Temperature
# This will return a native monthly time series between dates
# It will be in Deg C

params = {
    'dataset': 'PRISM_MONTHLY',
    'variable': 'tmean',
    'area_reducer': 'mean',
    'start_date': '1990-01-01',
    'end_date': '2023-12-31',
    'region': 'states',
    'sub_choices': "['Nevada']", # this has to be a string
    'filter_by': 'Name', # Property to filter by
}

url = 'http://dev.climateengine.org/timeseries/native/climate_engine_asset'    
r = requests.get(url, params=params, headers={'Authorization': Access_Token}, verify=False)
response = r.json()
# Convert Json file to csv
d = []
for feat in response:
    meta = feat['Metadata']
    for sub in feat['Data']:
        sub.update(meta)
        d.append(sub)
df = pd.DataFrame(d)
df_tmean = df.loc[:,['Date', 'tmean (C°)']]


# Example for Precipitation
# This will return a native monthly time series between dates
# It will be in mm

params = {
    'dataset': 'PRISM_MONTHLY',
    'variable': 'ppt',
    'area_reducer': 'mean',
    'start_date': '1990-01-01',
    'end_date': '2023-12-31',
    'region': 'states',
    'sub_choices': "['Nevada']", # this has to be a string
    'filter_by': 'Name', # Property to filter by
}

url = 'http://dev.climateengine.org/timeseries/native/climate_engine_asset'    
r = requests.get(url, params=params, headers={'Authorization': Access_Token}, verify=False)
response = r.json()
# Convert Json file to csv
d = []
for feat in response:
    meta = feat['Metadata']
    for sub in feat['Data']:
        sub.update(meta)
        d.append(sub)
df = pd.DataFrame(d)
df_ppt = df.loc[:,['Date', 'ppt (mm)']]

