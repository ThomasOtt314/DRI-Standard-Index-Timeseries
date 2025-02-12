import pandas as pd
import math
import scipy.special as sc
import numpy as np



path = '/Users/Thomas.Ott@dri.edu/Documents/GitHub/dri-wwdt/standard_index_time_series/example_data_input/ppt_pet_daily.csv'
df_in = pd.read_csv(path)
df_in.index = pd.to_datetime(df_in['date'])
df_in = df_in.drop(columns=['date'])
length = 90
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

# Calculate rolling df and drop na
df = df.rolling(window=length, min_periods=length).sum().dropna()

# Add month-day and year columns to dataset
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

# Build apply function
def apply_func(row):
    # Define variables of interest from row
    target_value = row.iloc[0]
    target_month_day = row.iloc[1]
    target_year = row.iloc[2]

    # get data array
    data_array = month_day_climo[target_month_day]

    # Climatology values must be sorted for log-logistic calculation
    sorted_data_array = data_array.sort_values(ascending=True)
    sorted_data_array.reset_index(inplace=True, drop=True)
    n = len(sorted_data_array)

    # Compute the unbiased Probability Weighted Moments (PWM)
    # w0 reduces to the simple mean (since comb(n, 0) reduces to 1)
    w0 = sorted_data_array.mean()

    # w1_factors is simply the index value starting at 0
    w1_factors = pd.Series(range(0, n))
    w1 = (((sorted_data_array * w1_factors).sum()) / n) / (n - 1)

    # w2_factors reduces to  j * (j - 1) / 2
    w2_factors = pd.Series([(j * (j - 1) / 2) for j in range(0, n)])
    w2 = (((((sorted_data_array * w2_factors).sum()) / n) / (n - 1)) / (n - 2)) * 2

    # Log-logistic parameters
    b = (2 * w1 - w0) / (6 * w1 - w0 - 6 * w2)
    gamma_b = math.gamma(1 - (1 / b)) * math.gamma(1 + (1 / b))
    a = (w0 - 2 * w1) * b / gamma_b
    g = w0 - a * gamma_b

    # clamp target value based on +4 -4 limits
    target_value_limit_1 = g + a * (31570.13766594579)**(-1/b) 
    target_value_limit_2 = g + a * (3.167550330569687e-05)**(-1/b)
    target_value_min = min(target_value_limit_1, target_value_limit_2)
    target_value_max = max(target_value_limit_1, target_value_limit_2)
    target_value = np.clip(target_value, target_value_min, target_value_max)
    
    fx = (1 + (a / (target_value - g)) ** b) ** -1
    p = 1 - fx
    
    # Compute normalized probability from inverse CDF of plotting positions
    # Following Abramowitz and Stegun (1965) outlined:
    # http://journals.ametsoc.org/doi/pdf/10.1175/2009JCLI2909.1

    wa = (math.log(p ** -2)) ** 0.5  # default log in ln
    wb = (math.log(fx ** -2)) ** 0.5  # default log in ln

    output_a = (wa - (2.515517 + 0.802853 * wa + 0.010328 * wa ** 2) / (
                1 + 1.432788 * wa + 0.189269 * wa ** 2 + 0.001308 * wa ** 3)) * -1
    output_b = wb - (2.515517 + 0.802853 * wb + 0.010328 * wb ** 2) / (
                1 + 1.432788 * wb + 0.189269 * wb ** 2 + 0.001308 * wb ** 3)

    if p > 0.5:
        pass
        si = output_b
    else:
        pass
        si = output_a
    
    return round(si, 4)

# Apply function to dataframe (this take about 10sec to run for 15,000 dates)
df['standard_index_loglogistic'] = df.apply(apply_func, axis=1)

# df = df.loc[:, ['standard_index_loglogistic']]
