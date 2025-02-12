import pandas as pd
import math
import scipy.special as sc
import numpy as np


def get_standard_index_loglogistic(df_in, length, start_year, end_year):
    """
    Compute a standardized index image using a log-logistic distribution approach
        for a custom date range and climatology
    S.M. Vicente-Serrano, S. Beguería, J.I. López-Moreno. 2010.
        A Multi-scalar drought index sensitive to global warming:
        The Standardized Precipitation Evapotranspiration Index – SPEI.
        Journal of Climate 23: 1696, DOI: 10.1175/2009JCLI2909.1.
    :param df_in: pandas dataframe w/ datetime index and a single data column
    :param length: integer value for how long to make the aggregation
    :param start_year: integer value for start year of climatology
    :param end_year: integer value for start end of climatology
    :return: Pandas dataframe with datetime index and single column named standard_index
    """

    # set df as copy of input
    df = df_in.copy()

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
        target_value = row[0]
        target_month_day = row[1]
        target_year = row[2]

        # get data array
        data_array = month_day_climo[target_month_day]

        # Add target value to data array if it falls outside of climatology
        if (target_year < start_year) or (target_year > end_year):
            data_array = pd.concat([data_array, pd.Series(target_value)])

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
        
        # Log-logistic PDF
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
            si = output_b
        else:
            si = output_a
        
        return round(si, 4)

    # Apply function to dataframe (this take about 10sec to run for 15,000 dates)
    df['standard_index_loglogistic'] = df.apply(apply_func, axis=1)

    # Refill missing leap year values
    df.loc[(df.index.month == 2) & (df.index.day == 29), ['standard_index']] = np.nan
    # Forward fill to replace leap day with value from day before
    df = df.ffill()

    return df.loc[:, ['standard_index_loglogistic']]


# New Function
def get_standard_index_gamma(df_in, length, start_year, end_year):
    """
    Methods based on paper (uses maximum licklihood to estimate gamma parameters)
    http://www.atmo.arizona.edu/students/courselinks/fall11/atmo529/Lectures/SPIhandout.pdf

    Compute a standardized index timeseries using a gamma distribution approach
        for a custom date range and climatology
    :param df_in: pandas dataframe w/ datetime index and a single data column
    :param length: integer value for how long to make the aggregation
    :param start_year: integer value for start year of climatology
    :param end_year: integer value for start end of climatology
    :return: Pandas dataframe with datetime index and single column named standard_index
    """

    # set df as copy of input
    df = df_in.copy()

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
        target_value = row[0]
        target_month_day = row[1]
        target_year = row[2]

        # get data array
        climo_array = month_day_climo[target_month_day]

        # Add target value to data array if it falls outside of climatology
        if (target_year < start_year) or (target_year > end_year):
            climo_array = pd.concat([climo_array, pd.Series(target_value)])

        # Remove 0s from climatology list
        climo_sub_array = climo_array[climo_array > 0]

        # Get probability of value = 0
        q = (len(climo_array) - len(climo_sub_array)) / len(climo_array)

        # Compute Gamma a and b using Maximum Likelihood Estimator
        A = math.log(climo_sub_array.mean()) - climo_sub_array.apply(math.log).mean()
        a = (1 + (1 + (A * 4 / 3)) ** 0.5) / (A * 4)
        b = climo_sub_array.mean() / a

        # Compare target image to climos
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
            si = output1
        else:
            si = output0
                
        
        return si

    # map fucntion across df
    df['standard_index_gamma'] = df.apply(apply_func, axis=1)

    # Refill missing leap year values
    df.loc[(df.index.month == 2) & (df.index.day == 29), ['standard_index']] = np.nan
    # Forward fill to replace leap day with value from day before
    df = df.ffill()

    return df.loc[:, ['standard_index_gamma']]


# New function
def get_standard_index_nonparametric(df_in, length, start_year, end_year):
    """
    Compute a standardized index timeseries using a non-parametric ranking approach
        for a custom date range, climatology, and aggregation length
    :param df_in: pandas dataframe w/ datetime index and a single data column
    :param length: Length of aggregation period
    :param start_year: integer value for start year of climatology
    :param end_year: integer value for start end of climatology
    :return: Pandas dataframe with datetime index and single column named standard_index
    """

    # Set start year and end year to integers
    start_year = int(start_year)
    end_year = int(end_year)

    # set df as copy of input
    df = df_in.copy()

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
        target_value = row[0]
        target_month_day = row[1]

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
            return output1
        else:
            return output0

    df['standard_index_nonparametric'] = df.apply(apply_func, axis=1)

    # Refill missing leap year values
    df.loc[(df.index.month == 2) & (df.index.day == 29), ['standard_index']] = np.nan
    # Forward fill to replace leap day with value from day before
    df = df.ffill()

    return df.loc[:, ['standard_index_nonparametric']]
