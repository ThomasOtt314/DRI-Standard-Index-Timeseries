# DRI Standar Index time series pyhone code Alpha
This code was produced to calulate standard index timeseries based on three different distribution types: LogLogistic, Gamma, and NonParametric. <br>

## Notes
Leap days in this code are considered in sumation at each timestep however, the values on Feb 29th are repeated from Feb 28th.

## How to run the code
This is a pretty bare bones repository and will require a bit of coding knowlage from the individual running it.
To run the code open file standard_index_example.py in your faveorite python IDE and run the code.

## LogLogistic
Based on journal article cited below. <br>
S.M. Vicente-Serrano, S. Beguería, J.I. López-Moreno. 2010.
    A Multi-scalar drought index sensitive to global warming:
    The Standardized Precipitation Evapotranspiration Index – SPEI.
    Journal of Climate 23: 1696, DOI: 10.1175/2009JCLI2909.1.

### Function
```
utils.get_standard_index_loglogistic(df_in, length, start_year, end_year):
    df_in: pandas dataframe w/ datetime index and a single data column
    length: integer value for how long to make the aggregation
    start_year: integer value for start year of climatology
    end_year: integer value for start end of climatology
    return: Pandas dataframe with datetime index and single column named standard_index
```

## Gamma
Methods based on paper (uses maximum licklihood to estimate gamma parameters) <br>
http://www.atmo.arizona.edu/students/courselinks/fall11/atmo529/Lectures/SPIhandout.pdf

### Function
```
utils.get_standard_index_gamma(df_in, length, start_year, end_year):
    df_in: pandas dataframe w/ datetime index and a single data column
    length: integer value for how long to make the aggregation
    start_year: integer value for start year of climatology
    end_year: integer value for start end of climatology
    return: Pandas dataframe with datetime index and single column named standard_index
```

## NonParametric
Compute a standardized index timeseries using a non-parametric ranking approach for a custom date range, climatology, and aggregation length

### Function
```
utils.get_standard_index_nonparametric(df_in, length, start_year, end_year):
    df_in: pandas dataframe w/ datetime index and a single data column
    length: integer value for how long to make the aggregation
    start_year: integer value for start year of climatology
    end_year: integer value for start end of climatology
    return: Pandas dataframe with datetime index and single column named standard_index
```

