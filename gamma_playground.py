import pandas as pd
import math
import scipy.special as sc
import numpy as np


path = '/Users/Thomas.Ott@dri.edu/Documents/GitHub/dri-wwdt/standard_index_time_series/example_data_input/ppt_pet_monthly.csv'
df_in = pd.read_csv(path)
df_in.index = pd.to_datetime(df_in['date'])
df_in = df_in.drop(columns=['date'])
length = 1
start_year = 1991
end_year = 2020


# set df as copy of input
df = df_in.copy()

# As a result of leap year interfearing with calculation they will
#   be removed before the calculation is made (only in daily data)
df = df[(df.index.month != 2) | (df.index.day != 29)]

# get data column name
column_name = df.columns[0]

# Calculate rolling df
df = df.rolling(window=length, min_periods=length).sum().dropna()

# Add month to dataset
df['month_day'] = df.index.strftime('%m-%d')
df['year'] = df.index.strftime('%Y').astype(int)

# Build month-day climatology look-up table
# Get unique list of dates
month_day_list = df['month_day'].unique()
month_day_climo = {}
for month_day in month_day_list:
    # Get data array from input df
    df_sub = df.loc[(df['month_day'] == month_day) &
                    (df['year'] >= start_year) &
                    (df['year'] <= end_year), [column_name]]

    # get data array
    month_day_climo[month_day] = pd.Series(df_sub.squeeze().values)

def apply_func(row):
    # Define variables of interest from row
    target_value = row.iloc[0]
    target_month_day = row.iloc[1]
    target_year = row.iloc[2]

    # get data array
    climo_array = month_day_climo[target_month_day]

    # Remove 0s from climatology list
    climo_sub_array = climo_array[climo_array > 0]

    # Get probability of value = 0
    q = (len(climo_array) - len(climo_sub_array)) / len(climo_array)

    # Compute Gamma a and b using Maximum Likelihood Estimator
    A = math.log(climo_sub_array.mean()) - climo_sub_array.apply(math.log).mean()
    a = (1 + (1 + (A * 4 / 3)) ** 0.5) / (A * 4)
    b = climo_sub_array.mean() / a

    # Compare target image to climos
    target_value = target_value + 0.000001
    
    gx = sc.gammainc(a, target_value / b)
    hx = q + gx * (1 - q)

    # Compute normalized probability from inverse CDF of plotting positions
    # Following Abramowitz and Stegun (1965) outlined:
    # http://journals.ametsoc.org/doi/pdf/10.1175/2009JCLI2909.1

    w0 = (math.log(hx ** -2)) ** 0.5  # default log in ln
    w1 = (math.log((1 - hx) ** -2)) ** 0.5  # default log in ln

    output0 = (w0 - (2.515517 + 0.802853 * w0 + 0.010328 * w0 ** 2) / (
                1 + 1.432788 * w0 + 0.189269 * w0 ** 2 + 0.001308 * w0 ** 3)) * -1
    output1 = (w1 - (2.515517 + 0.802853 * w1 + 0.010328 * w1 ** 2) / (
                1 + 1.432788 * w1 + 0.189269 * w1 ** 2 + 0.001308 * w1 ** 3))

    if hx > 0.5:
        print(output1)
        # return output1
    else:
        print(output0)
        # return output0

# map fucntion across df
df['standard_index_gamma'] = df.apply(apply_func, axis=1)
