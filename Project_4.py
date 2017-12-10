### Cameron Chandra Final Project 
import json
import sqlite3
import requests 
import urllib3
import facebook
import Authentication
from darksky import forecast
from datetime import datetime as dt
import contextlib2

# uprint definition
import sys
def uprint(*objects, sep=' ', end='\n', file=sys.stdout):
    enc = file.encoding
    if enc == 'UTF-8':
        print(*objects, sep=sep, end=end, file=file)
    else:
        f = lambda obj: str(obj).encode(enc, errors='backslashreplace').decode(enc)
        print(*map(f, objects), sep=sep, end=end, file=file)

# Caching setup 
CACHE_FNAME = "206_Project4_cache.json"
try:
    cache_file = open(CACHE_FNAME, 'r') 
    cache_contents = cache_file.read() 
    CACHE_DICTION = json.loads(cache_contents) 
    cache_file.close() 
except:
	CACHE_DICTION ={}

########################## DATABASE #################################
connection = sqlite3.connect("206_Project4.sqlite")
cur = connection.cursor()
# FB Table 
cur.execute("DROP TABLE IF EXISTS Facebook")
cur.execute(''' 
CREATE TABLE Facebook (name TEXT , place TEXT, start_time TIMESTAMP, id INTEGER)''')





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

		# 	uprint(event['place'])
		# 	uprint(event['start_time'])
fb_data = get_fb_data(token)
uprint(fb_data)

# Write cached data to database 
# for event in fb_data:
# 	try:
# 		for event_location in event['place']:
# 			event_tup = event['']






# Dark Sky Historic Weather API
# key = Authentication.ds_secret_key
# boston = forecast(key, 42.3601,-71.0589)
# boston.