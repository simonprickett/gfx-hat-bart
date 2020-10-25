import atexit
import os
import requests
import time

from enum import Enum
from gfxhat import backlight, lcd, fonts, touch
from PIL import Image, ImageFont, ImageDraw

API_BASE = 'http://api.bart.gov/api'
API_KEY = os.getenv('BART_API_KEY', 'MW9S-E7SL-26DU-VV8V')

NO_REAL_TIME_DEPARTURE_STATIONS = [ 'OAKL' ]

BAR_LOCATION = 2

class ApplicationState(Enum):
    STATION_LIST = 0
    STATION_DEPARTURES = 1

application_state = ApplicationState.STATION_LIST
width, height = lcd.dimensions()
font = ImageFont.truetype(fonts.BitbuntuFull, 10)
image = Image.new('P', (width, height))
draw = ImageDraw.Draw(image)

stations = {}
menu_options = []
current_menu_option = BAR_LOCATION

class MenuOption:
    def __init__(self, name, action, abbr):
        self.name = name
        self.action = action
        self.abbr = abbr 
        self.size = font.getsize(name)
        self.width, self.height = self.size
  
    def trigger(self):
        self.action(self.abbr)

def cleanup():
    backlight.set_all(0, 0, 0)
    backlight.show()
    lcd.clear()
    lcd.show()

def set_backlight(r, g, b):
    backlight.set_all(r, g, b)
    backlight.show()

def paint_image(image):
    for x in range(width):
        for y in range(height):
            pixel = image.getpixel((x, y))
            lcd.set_pixel(x, y, pixel)

    lcd.show()

def make_api_url(res, cmd, params = None):
    api_url = f'{API_BASE}/{res}.aspx?cmd={cmd}&key={API_KEY}&json=y' 

    if params is not None:
        api_url = f'{api_url}&{params}'

    return api_url

def load_stations():
    response = requests.get(url=f'{make_api_url("stn", "stns")}')
    response_json = response.json()

    for station in response_json['root']['stations']['station']:
        if station['abbr'] not in NO_REAL_TIME_DEPARTURE_STATIONS:
            stations[station['abbr']] = station['name']

def button_press_handler(ch, event):
    global current_menu_option

    if event != 'press':
        return

    if ch == 0:
        current_menu_option -= 1

        if current_menu_option == -1:
            current_menu_option = 0
    elif ch == 1:
        current_menu_option += 1

        if current_menu_option == len(menu_options):
            current_menu_option = len(menu_options) - 1
    elif ch == 4:
        menu_options[current_menu_option].trigger()

def setup_touch_buttons():
    for x in range(6):
        touch.set_led(x, 0)
        touch.on(x, button_press_handler)

def show_departures(stationAbbr):
    print(stationAbbr)
    orig = f'orig={stationAbbr}'
    response = requests.get(url=f'{make_api_url("etd", "etd", orig)}')
    response_json = response.json()

    departures_by_platform = {}

    for etds in response_json['root']['station'][0]['etd']:
        for estimate in etds['estimate']:
            platform = estimate['platform']
            departure = {}
            departure['destination'] = etds['destination']
            minutes = estimate['minutes']

            if minutes == 'Leaving':
                minutes = 0
            else:
                minutes = int(minutes)

            departure['minutes'] = minutes
            print(departure)

            if platform not in departures_by_platform:
                departures_by_platform[platform] = []

            departures_by_platform[platform].append(departure)

    # https://stackoverflow.com/questions/72899/how-do-i-sort-a-list-of-dictionaries-by-a-value-of-the-dictionary
    print(departures_by_platform)

def show_station_picker():
    set_backlight(255, 255, 255)

    for stationAbbr in stations:
        menu_options.append(MenuOption(stations[stationAbbr], show_departures, stationAbbr)) 

    while True:
        line = 0
        image.paste(0, (0, 0, width, height))

        start_pos = current_menu_option - BAR_LOCATION 

        if start_pos < 0:
            line = abs(start_pos)
            start_pos = 0

        end_pos = current_menu_option + 4
 
        if end_pos >= len(menu_options):
            end_pos = len(menu_options)

        for index in range(start_pos, end_pos):
            x = 7 
            y = (line * 12)
            option = menu_options[index]

            if line  == BAR_LOCATION:
                draw.rectangle(((x - 2, y - 1), (width, y + 10)), 1)

            draw.text((x, y), option.name, 0 if line == BAR_LOCATION else 1, font) 
            line += 1

        w, h = font.getsize('>')
        draw.text((0, ((height - h) / 2) - 3), '>', 1, font)

        paint_image(image)
        time.sleep(1.0 / 30)

atexit.register(cleanup)
load_stations()
setup_touch_buttons()
show_station_picker()
