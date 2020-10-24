import os
import requests
import atexit

from gfxhat import backlight, lcd, fonts, touch
from PIL import Image, ImageFont, ImageDraw

API_BASE = 'http://api.bart.gov/api'
API_KEY = os.getenv('BART_API_KEY', 'MW9S-E7SL-26DU-VV8V')

width, height = lcd.dimensions()
font = ImageFont.truetype(fonts.BitbuntuFull, 10)
image = Image.new('P', (width, height))
draw = ImageDraw.Draw(image)

stations = {}
menu_options = []
current_menu_option = 2

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

def paint_image(image):
    for x in range(width):
        for y in range(height):
            pixel = image.getpixel((x, y))
            lcd.set_pixel(x, y, pixel)

    lcd.show()

def make_api_url(res, cmd):
    return f'{API_BASE}/{res}.aspx?cmd={cmd}&key={API_KEY}&json=y'

def load_stations():
    response = requests.get(url=f'{make_api_url("stn", "stns")}')
    response_json = response.json()

    for station in response_json['root']['stations']['station']:
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

    print(f'current_menu_option = {current_menu_option}')

def setup_touch_buttons():
    for x in range(6):
        touch.set_led(x, 0)
        touch.on(x, button_press_handler)

def show_departures(stationAbbr):
    print(stationAbbr)

def show_station_picker():
    set_backlight(255, 255, 255)

    image.paste(0, (0, 0, width, height))

    for stationAbbr in stations:
        menu_options.append(MenuOption(stations[stationAbbr], show_departures, (stationAbbr))) 

    for index in range(len(menu_options)):
        x = 7 
        y = (index * 12)
        option = menu_options[index]

        if index == current_menu_option:
            draw.rectangle(((x - 2, y - 1), (width, y + 10)), 1)

        draw.text((x, y), option.name, 0 if index == current_menu_option else 1, font) 

    w, h = font.getsize('>')
    draw.text((0, ((height - h) / 2) - 3), '>', 1, font)

    paint_image(image)

    while True:
        pass

atexit.register(cleanup)
load_stations()
setup_touch_buttons()
show_station_picker()
