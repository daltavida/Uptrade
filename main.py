from configparser import ConfigParser
from util.build_database import get_data
from util.get_price_data import get_price_data
from util.get_usability import get_usage_data

config = ConfigParser()
config.read('config.ini')

build_db = config.getboolean('STEPS', 'build_db')
get_price = config.getboolean('STEPS', 'get_price')
get_use = config.getboolean('STEPS', 'get_use')

if build_db:
  get_data()
if get_price:
  get_price_data()
if get_use:
  get_usage_data()
