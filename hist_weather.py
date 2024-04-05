#!/usr/bin/env python3
import sys
import requests
import datetime as dt

today = dt.date.today()
yesterday = today - dt.timedelta(days=1)
few_days_ago = today - dt.timedelta(days=4)

def para_future(long, lat):
	"""Function to take in coorodinates and create list of para_future. """
	result = { "longitude": long, 
		"latitude": lat, 
		"hourly": ["temperature_2m", "dew_point_2m", "precipitation", "weather_code", "cloud_cover"],
		"temperature_unit": "fahrenheit",
		"precipitation_unit": "mm"
		} 
	return result

def para_past(long, lat):
	"""Function to take in coordinates and create list of para past. """
	result = { "longitude": long, 
		"latitude": lat, 
		"start_date":  few_days_ago,
		"end_date": yesterday,
		"hourly": ["temperature_2m", "dew_point_2m", "precipitation", "weather_code", "cloud_cover"]
		} 
	return result

# Call open-mateo using requests library and json format
def call_forecast(lat, long):
	url = "https://api.open-meteo.com/v1/forecast"
	loc_forecast = requests.get(url, params=para_future(lat, long))
	return loc_forecast.json().get('hourly', 'failed to obtain hours')

def call_history(lat, long):
	url_two = "https://archive-api.open-meteo.com/v1/archive"
	loc_history = requests.get(url_two, params=para_past(lat, long))
	return loc_history.json().get('hourly', 'failed to obtain hours')
 
#parameters from the past
def data_points(terms, tense='future'):
	"""Takes call_forecast or call_ history and future or past tense to 
	return the data points at 2 days in the past or 1 day in the future
	Use json hourly readings 7 days worth provided each parameter 
	limited to 24 hours with 24 hour slice. """
	if tense == 'past':
		sliced = 72
	else:
		sliced = 48
	time = terms.get('time', 'failed to obtain time')[0:sliced]
	temp = terms.get('temperature_2m', 'failed to obtain temperature_2m')[0:sliced]
	dew_point = terms.get('dew_point_2m', 'failed to obtain dew_point_2m')[0:sliced]
	precip = terms.get('precipitation', 'failed to obtain precipitation')[0:sliced]
	w_code =  terms.get('weather_code', 'failed to obtain weather_code')[0:sliced]
	clouds = terms.get('cloud_cover', 'failed to obtain cloud_cover')[0:sliced]
	assert len(time) == len(temp) == len(dew_point) == len(precip) == len(w_code) == len(clouds), "all elements must be of the same length"
	return [time, temp, dew_point, precip, w_code, clouds]

def time(r):
	return r[0]

def temperature(r):
	return r[1]

def dew_point(r):
	return r[2]

def precip(r):
	return r[3]

def w_code(r):
	return r[4]

def clouds(r):
	return r[5]

def parser(data_out):
	ti, te, de = time(data_out), temperature(data_out), dew_point(data_out)
	pr, w_, cl = precip(data_out), w_code(data_out), clouds(data_out) 
	length, holder = len(ti), {}
	for i in range(length):
		holder[i] = {'time':ti[i], 'temp':te[i], 'dew':de[i], 
        'precip':pr[i], 'w_code':w_[i], 'cloud_cover':cl[i]
        }
	return holder

def composer_future(lat, long):
    """This function return the forcast and parses it ."""
    future = call_forecast(lat, long)
    tomorrow = data_points(future, "future")
    return parser(tomorrow)

def composer_past(lat, long):
    past = call_history(lat, long)
    yesterday = data_points(past, "past")
    return parser(yesterday)

def snow_finder(dictionary):
    """This function uses the weather codes to track snow accumulation ."""
    accumulated_snow = 0
    for item in dictionary.items():
        precip = item[1]['precip']
        code = item[1]['w_code']
        if code in [70, 71, 72, 36]:
            accumulated_snow += precip
        elif code in [73, 74, 38]:
            accumulated_snow += precip
        elif code in [75, 76, 85, 86, 83, 37, 39]:
            accumulated_snow += precip
    return accumulated_snow



#IKON PASS Ski locations on east coast 
ski_locations = {
    'Stratton' : [43.1134, 72.9065],
    'Sugarbush' : [44.1371, 72.8922],
    'Killington' : [43.6779, 72.7795],
    'Pico' : [43.6674, 72.8503],
    'Windham' : [42.2996, 74.2633],
    'Snowshoe' : [38.4122, 79.9962],
    'Sunday' : [44.4764, 70.8584],
    'Sugarloaf' : [45.0315, 70.3134],
    'Loon' : [44.0363, 71.6217],
    'Camelback' : [41.0503, 75.3566],
    'Blue' : [40.6878, 75.2942]
}

#Epic Pass "    "   
Epic_Pass = {
    'Stowe_VT': [44.5297, 72.7873],
    'Okemo_VT': [43.4013, 72.7170],
    'Mount_Snow_VT': [42.9604, 72.9205],
    'Mount_Sunapee_NH': [43.3203, 72.0876],
    'Attitash_NH': [44.0821, 71.2293],
    'Wildcat_NH': [44.2639, 71.2358],
    'Crotched_NH': [42.9983, 71.8744],
    'Hunter_NY': [42.2027, 74.2305]
    }

if __name__ == "__main__":
    totals = []
    for place, coords in ski_locations.items():
        future = snow_finder(composer_future(*coords)) 
        past = snow_finder(composer_past(*coords))
        total = past + future
        pair = [place, total]
        totals.append(pair)
    for item in sorted(totals, key=lambda x: x[1], reverse=True):
        print("{} - {:.3f} inches".format(item[0], item[1]))
