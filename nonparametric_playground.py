import pandas as pd
import math
import scipy.special as sc
import numpy as np


path = '/Users/Thomas.Ott@dri.edu/Documents/GitHub/dri-wwdt/standard_index_time_series/example_data_input/ppt_pet_daily.csv'
df_in = pd.read_csv(path)
df_in.index = pd.to_datetime(df_in['date'])
df_in = df_in.drop(columns=['date'])
length = 7
start_year = 1991
end_year = 2020


# set df as copy of input
df = df_in.copy()
# df['WB'] = df['WB']*-1

# As a result of leap year interfearing with calculation they will
#   be removed before the calculation is made (only in daily data)
df = df[(df.index.month != 2) | (df.index.day != 29)]

# get data column name
column_name = df.columns[0]

# Calculate rolling df
df = df.rolling(window=length, min_periods=length).sum()
# Add month to dataset
df['month_day'] = df.index.strftime('%m-%d')
df['year'] = df.index.strftime('%Y').astype(int)

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

    # get climo array
    climo_array = month_day_climo[target_month_day]

    years = int(end_year) - int(start_year) + 1
    if years > 1:
        pct_step = 100.0 / (years - 1)
        pct_list = list(np.arange(0, 100, pct_step) / 100)
        # pct_list.append(1)  # Not sure why this was here, removing
    else:
        # pct_step = 100
        pct_list = list(np.arange(0, 100 + 1, 100) / 100)  # +1 since numpy is exclusive

    # Calculate the values at the percentiles
    climo_percentiles = climo_array.quantile(pct_list)

    # Get 1's below, 0's above, a mean will give the percent below value.
    target_value = 1600
    positions = len(climo_percentiles[climo_percentiles > target_value])

    # Compute Tukey plotting positions
    # Add 1 since positions were computed as 0 based indices
    # https://github.com/statsmodels/statsmodels/blob/master/statsmodels/sandbox/stats/stats_mstats_short.py
    alpha = 1.0 / 3
    beta = 1.0 / 3
    pp = (positions + (1 - alpha)) / (years + 1 - alpha - beta)
    p = 1 - pp

    # Compute normalized probability from inverse CDF of plotting positions
    # Following Abramowitz and Stegun (1965) outlined:
    # http://journals.ametsoc.org/doi/pdf/10.1175/2009JCLI2909.1

    w0 = (math.log(p ** -2)) ** 0.5  # default log in ln
    w1 = (math.log(pp ** -2)) ** 0.5  # default log in ln

    output0 = (w0 - (2.515517 + 0.802853 * w0 + 0.010328 * w0 ** 2) / (
                1 + 1.432788 * w0 + 0.189269 * w0 ** 2 + 0.001308 * w0 ** 3)) * -1
    output1 = w1 - (2.515517 + 0.802853 * w1 + 0.010328 * w1 ** 2) / (
                1 + 1.432788 * w1 + 0.189269 * w1 ** 2 + 0.001308 * w1 ** 3)

    if p > 0.5:
        print(output1)
    else:
        print(output0)

df['standard_index_nonparametric'] = df.apply(apply_func, axis=1)
