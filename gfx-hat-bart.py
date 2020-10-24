import os
import requests
import atexit

from gfxhat import backlight, lcd, fonts
from PIL import Image, ImageFont, ImageDraw

API_BASE = 'http://api.bart.gov/api'
API_KEY = os.getenv('BART_API_KEY', 'MW9S-E7SL-26DU-VV8V')

width, height = lcd.dimensions()
font = ImageFont.truetype(fonts.BitbuntuFull, 10)
image = Image.new('P', (width, height))
draw = ImageDraw.Draw(image)

stations = {}

class MenuOption:
    def __init__(self, name, action, options=()):
        self.name = name
        self.action = action
        self.options = options
        self.size = font.getsize(name)
        self.width, self.height = self.size
  
    def trigger(self):
        self.action(*self.options)

def cleanup():
    backlight.set_all(0, 0, 0)
    backlight.show()
    lcd.clear()
    lcd.show()

def set_backlight(r, g, b):
    backlight.set_all(r, g, b)
    backlight.show()

def make_api_url(res, cmd):
    return f'{API_BASE}/{res}.aspx?cmd={cmd}&key={API_KEY}&json=y'

def load_stations():
    response = requests.get(url=f'{make_api_url("stn", "stns")}')
    response_json = response.json()

    for station in response_json['root']['stations']['station']:
        stations[station['abbr']] = station['name']

def show_departures(stationAbbr):
    print(stationAbbr)

def show_station_picker():
    set_backlight(255, 255, 255)

    menu_options = []

    image.paste(0, (0, 0, width, height))

    for stationAbbr in stations:
        menu_options.append(MenuOption(stations[stationAbbr], show_departures, (stationAbbr))) 

    for index in range(len(menu_options)):
        x = 5 
        y = (index * 12)
        #y = (index * 12) + (height / 2) - 4 - offset_top
        print(y)
        option = menu_options[index]
        draw.text((x, y), option.name, 1, font) 

    for x in range(width):
        for y in range(height):
            pixel = image.getpixel((x, y))
            lcd.set_pixel(x, y, pixel)

    lcd.show()

    while True:
        pass

atexit.register(cleanup)
load_stations()
show_station_picker()
