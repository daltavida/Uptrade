import pandas as pd
from configparser import ConfigParser
from util.build_database import get_data
from util.get_price_data import get_price_data
from util.get_usability import get_usage_data
from util.trade_up import find_tradeups
import multiprocessing


if __name__ == "__main__":
    
  config = ConfigParser()
  config.read('config.ini')

  build_db = config.getboolean('STEPS', 'build_db')
  get_price = config.getboolean('STEPS', 'get_price')
  get_use = config.getboolean('STEPS', 'get_use')

  min_price = config.getfloat('PARAMS', 'min_price')
  max_price = config.getfloat('PARAMS', 'max_price')
  usable_cutoff = config.getfloat('PARAMS', 'usable_cutoff')

  if build_db:
    get_data()
  if get_price:
    get_price_data()
  if get_use:
    get_usage_data()

  print("Reading usage data")
  usage_data = pd.read_pickle("pickle/usage_data.pkl")

  stattrak_values = [True, False]
  rarity_values = ["Consumer Grade", "Industrial Grade", "Mil-Spec Grade", "Restricted", "Classified"]

  processes = []

  for stattrak in stattrak_values:
    for rarity in rarity_values:
      skin_pool = usage_data[(usage_data['Stattrak'] == stattrak) & (usage_data['Rarity'] == rarity) & (usage_data['Usable'])]
      skin_pool = skin_pool[(min_price < skin_pool['Price']) & (skin_pool['Price'] < max_price)]
      skin_pool = skin_pool[skin_pool['Profit'] > usable_cutoff]
      skin_pool = skin_pool.sort_values('Profit', ascending=False)
      
      p = multiprocessing.Process(target=find_tradeups, args=(skin_pool, usage_data, rarity, stattrak))
      processes.append(p)
      p.start()

  for process in processes:
    process.join()
