### Cameron Chandra Final Project 
import json
import sqlite3
import requests 
import urllib3
import facebook
import Authentication
import contextlib2
import forecastio
import datetime
import webbrowser


# uprint definition
import sys
def uprint(*objects, sep=' ', end='\n', file=sys.stdout):
    enc = file.encoding
    if enc == 'UTF-8':
        print(*objects, sep=sep, end=end, file=file)
    else:
        f = lambda obj: str(obj).encode(enc, errors='backslashreplace').decode(enc)
        print(*map(f, objects), sep=sep, end=end, file=file)

# Caching setup (2 caches, one fore Facebook one for Dark Sky)
CACHE_FNAME = "Facebook_cache.json"
try:
    cache_file = open(CACHE_FNAME, 'r') 
    cache_contents = cache_file.read() 
    CACHE_DICTION = json.loads(cache_contents) 
    cache_file.close() 
except:
	CACHE_DICTION ={}

C_FNAME = "DS_cache.json"
try:
    c_file = open(C_FNAME, 'r') 
    c_contents = c_file.read() 
    C_DICTION = json.loads(c_contents) 
    c_file.close() 
except:
	C_DICTION ={}

########################## DATABASE #################################
connection = sqlite3.connect("206_Project4.sqlite")
cur = connection.cursor()
# FB Table 
cur.execute("DROP TABLE IF EXISTS Facebook")
cur.execute(''' 
CREATE TABLE Facebook (name TEXT, latitude INTEGER, longitude INTEGER, start_time TIMESTAMP, id INTEGER)''')

# Dark Sky Table
cur.execute("DROP TABLE IF EXISTS DS")
cur.execute('''
CREATE TABLE DS (conditions TEXT, time_of_conditions TEXT, lat_long INTEGER, temperature INTEGER, precipProbability INTEGER)''')



########################### FACEBOOK ########################################

# Facebook API access 
token = Authentication.fb_access_token
graph = facebook.GraphAPI(access_token=token,version=2.7)

# Get data from Facebook or cache
def get_fb_data(token):
	if token in CACHE_DICTION:
		uprint("using cache")
		uprint("$$$$$$$")
		return CACHE_DICTION[token]
	else:
		uprint("Retreiving from Facebook")
		uprint("$$$$$$$")
		event_list = graph.request('/me/events?limit=100')
		CACHE_DICTION[token] = event_list['data']
		dumped_json_cache = json.dumps(CACHE_DICTION) + '\n'
		fw = open(CACHE_FNAME,'w')
		fw.write(dumped_json_cache)
		fw.close()
		return CACHE_DICTION[token] 


fb_data = get_fb_data(token)

# Write cached data to database 
for event in fb_data:
	if "place" in event.keys():
		if 'location' in event['place'].keys():
			info_tup = event['name'], event['place']['location']['latitude'], event['place']['location']['longitude'], event['start_time'], event['id']
			cur.execute(''' INSERT INTO Facebook (name, latitude, longitude, start_time, id)
 			VALUES (?,?,?,?,?)''', info_tup)


connection.commit() 

# Dark Sky Historic Weather API
key = Authentication.ds_secret_key


# Retrieve event times from Facebook table
time_lst = []

cur.execute('SELECT start_time FROM Facebook')
time_data = cur.fetchall()
for time in time_data:
	a_time = time[0].replace('T',"")
	b_time = a_time.replace(':','')
	c_time = b_time.replace('-','')
	d_time = c_time.strip()
	time_lst.append(((int(d_time[:4])),(int(d_time[4:6])),(int(d_time[6:8])),(int(d_time[8:10])),(int(d_time[10:12]))))

# Retrieve event latitude and longitude from Facebook table
cur.execute('SELECT latitude,longitude FROM Facebook')
lat_long = cur.fetchall()
# Make a dictionary of required info 
info_dict = dict(zip(time_lst,lat_long))

# Function that returns forecast data from cache or Dark Sky API
def get_ds_data(date):
	if str(date) in C_DICTION.keys():
		uprint("Using Cache")
		uprint("$$$$$")
		return C_DICTION[str(date)]
	else:
		uprint('Retrieving data from Dark Sky')
		lat = info_dict[date][0]
		longitude = info_dict[date][-1]
		year = date[0]
		month = date[1]
		day = date[2]
		hour = date[3]
		second = date[4]
		current_time = datetime.datetime(year, month, day, hour, second)
		forecast = forecastio.load_forecast(key,lat,longitude,time= current_time)
		c_forecast = forecast.currently()
		C_DICTION[str(date)] = str(info_dict[date]),str(c_forecast.summary),str(c_forecast.time),str(c_forecast.temperature),str(c_forecast.precipProbability)
		dumped_json_cache = json.dumps(C_DICTION) + '\n'
		fw = open(C_FNAME,'w')
		fw.write(dumped_json_cache)
		fw.close()
		return C_DICTION[str(date)]

# Retrieve info and write to cache
ds_data = []
for date in info_dict:
	ds_data.append(get_ds_data(date))


# Write forecast data to database (DS) 

for forecast in ds_data:
	forecast_tup = forecast[1], forecast[2], forecast[0], forecast[3], forecast[4]
	cur.execute('INSERT INTO DS (conditions, time_of_conditions, lat_long, temperature, precipProbability) VALUES (?,?,?,?,?)', forecast_tup)


cur.execute("SELECT name FROM Facebook")
event_names = cur.fetchall()

# for name in event_names:
# 	cur.execute('UPDATE DS (name) VALUES (?,?,?,?,?,?,?)', name)

connection.commit()


# Google Map API + visualization


# Get lat/long from Facebook table 
cur.execute('SELECT latitude,longitude FROM Facebook')
coordinates = cur.fetchall() 
cur.close()

# Define marker locations and specifications 
markers_str = ''
for coordinate in coordinates:
	str_coordinate = ''
	for x in coordinate:
		str_coordinate = str_coordinate + ',' + str(x)
	markers_str = markers_str + "&markers=color:blue%7C{}&markers=size:tiny&".format(str_coordinate[1:])

# URL Setup
g_key = Authentication.gm_key
url = 'https://maps.googleapis.com/maps/api/staticmap?size=480x480&format=PNG&maptype=roadmap&markers=%s&key=%s' % (markers_str, g_key)

# Open static map in browser
webbrowser.open(url)