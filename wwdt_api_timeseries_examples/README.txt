API /timeseries/standard_index/points documentation link:
https://docs.climateengine.org/docs/build/html/timeseries.html#rst-timeseries-standard-index-points

API /timeseries/native/points documentation link:
https://docs.climateengine.org/docs/build/html/timeseries.html#timeseries-native-points


drought_index_ts_points_example.py

This code shows examples that return a standard timeseries based on a list of points.
The timeseries returned is the full monthly timeseries, I filtered for the month in the example tif.

Some things to note, the "coordinates" parameter needs to be a string list. Meaning it needs to be a python
  list that is converted to a string.
Also, all temperature units are in Celsius, and precipitation units are in mm.


drought_index_ts_states_example.py

This code is almost exactly the same as the points version however it summarizes over states.
The sub_choices parameter needs to be in a string list.
