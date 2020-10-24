import os
import requests

API_BASE = 'http://api.bart.gov/api'
API_KEY = os.getenv('BART_API_KEY', 'MW9S-E7SL-26DU-VV8V')

stations = {}

def make_api_url(res, cmd):
    return f'{API_BASE}/{res}.aspx?cmd={cmd}&key={API_KEY}&json=y'

def load_stations():
    response = requests.get(url=f'{make_api_url("stn", "stns")}')
    response_json = response.json()

    for station in response_json['root']['stations']['station']:
        stations[station['abbr']] = station['name']

def show_station_picker():
    for stationAbbr in stations:
        print(stations[stationAbbr])

load_stations()
show_station_picker()