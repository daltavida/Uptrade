import pandas as pd
import requests
import time

#Function to check the price of a gun from a JSON file requested from CSGO Backpack
def check_price(row, items_dict):
  print(f"Checked price for {row.name}")
  
  # Use gun, skin, wear and stattrak to uniquely identify guns in JSON
  gun = row['Gun']
  skin = row['Skin'].replace("'", "&#39")
  wear = row['Wear']

  if row['Stattrak']:
    request_id = f"StatTrak\u2122 {gun} | {skin} ({wear})"
  else:
    request_id = f"{gun} | {skin} ({wear})"

  if request_id in items_dict:
    return items_dict.get(request_id)
  else:
    return None


def get_price_data():

  # Steam Web API can be accessed with this URL. Each page has only 100 results. To get more results,
  # start value can be incremented by 100
  template = "https://steamcommunity.com/market/search/render/?appid=730&norender=1&count=100&start="
  start = 0
  size = 0

  request_url = template + str(start)
  response = requests.get(request_url)
  size = response.json().get('total_count')
  size = round((size + 50) / 100)

  items_dict = dict()

  # Keep incrementing start by 100 and adding prices to dict until all pages are visited
  for i in range(size):
    time.sleep(15)
    start = 100 * i
    request_url = template + str(start)
    print(request_url)
    response = requests.get(request_url)
    results = response.json().get('results')
    for each in results:
      items_dict[each.get('name')] = each.get('sell_price') / 100 * 1.05 
      
  print("Reading skin data")
  skin_data = pd.read_pickle("pickle/skin_data.pkl")

  print("Checking prices")
  # # Apply check price function to each row
  skin_data['Price'] = skin_data.apply(check_price, args=(items_dict,), axis=1)

  print("Saving data")
  # Pickle data and save to excel
  skin_data.to_pickle("pickle/price_data.pkl")
  skin_data.to_excel("data/price_data.xlsx", sheet_name='Prices')

if __name__ == '__main__':
  get_price_data()