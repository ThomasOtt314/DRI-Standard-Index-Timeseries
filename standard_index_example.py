import os
import pandas as pd

import utils

# ----------------------------------------------------------------------------
#                              30 day SPI example Gamma
# ----------------------------------------------------------------------------

# Import example data
pr_df = pd.read_csv(os.path.join('example_data_input', 'ppt_daily.csv'))

# Build datetime index and drop date column
pr_df.index = pd.to_datetime(pr_df['date']).drop(columns=['date'])
pr_df = pr_df.drop(columns=['date'])

# Calculate gamma distribution
spi_df = utils.get_standard_index_gamma(df_in=pr_df,
                                        length=30,
                                        start_year=1991,
                                        end_year=2020)

spi_df.to_csv(os.path.join('example_data_output', '30_day_spi_gamma.csv'))
spi_df=None


# ----------------------------------------------------------------------------
#                              2 month SPI example Gamma
# ----------------------------------------------------------------------------

# Import example data
ppt_df = pd.read_csv(os.path.join('example_data_input', 'ppt_monthly.csv'))

# Build datetime index and drop date column
ppt_df.index = pd.to_datetime(ppt_df['date']).drop(columns=['date'])
ppt_df = ppt_df.drop(columns=['date'])

# Calculate gamma distribution
spi_df = utils.get_standard_index_gamma(df_in=ppt_df,
                                        length=2,
                                        start_year=1991,
                                        end_year=2020)

spi_df.to_csv(os.path.join('example_data_output', '2_month_spi_gamma.csv'))
spi_df=None


# ----------------------------------------------------------------------------
#                              30 day SPEI example LogLogistic
# ----------------------------------------------------------------------------

# Import example data
ppt_pet_df = pd.read_csv(os.path.join('example_data_input', 'ppt_pet_daily.csv'))

# Build datetime index and drop date column
ppt_pet_df.index = pd.to_datetime(ppt_pet_df['date']).drop(columns=['date'])
ppt_pet_df = ppt_pet_df.drop(columns=['date'])

# Calculate gamma distribution
spei_df = utils.get_standard_index_loglogistic(df_in=ppt_pet_df,
                                               length=30,
                                               start_year=1981,
                                               end_year=2020)

spei_df.to_csv(os.path.join('example_data_output', '30_day_spei_loglogistic.csv'))
spei_df=None


# ----------------------------------------------------------------------------
#                              3 month SPEI example NonParametric
# ----------------------------------------------------------------------------

# Import example data
ppt_pet_df = pd.read_csv(os.path.join('example_data_input', 'ppt_pet_monthly.csv'))

# Build datetime index and drop date column
ppt_pet_df.index = pd.to_datetime(ppt_pet_df['date']).drop(columns=['date'])
ppt_pet_df = ppt_pet_df.drop(columns=['date'])

# Calculate gamma distribution
spei_df = utils.get_standard_index_nonparametric(df_in=ppt_pet_df,
                                                 length=3,
                                                 start_year=1981,
                                                 end_year=2020)

spei_df.to_csv(os.path.join('example_data_output', '3_month_spei_nonparametric.csv'))
spei_df=None



