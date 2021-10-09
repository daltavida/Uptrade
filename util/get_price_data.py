import pandas as pd
import requests


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

  # Get 24 Hour average price. If not available, use 7 Days, 30 Days or all time in that order.
  if request_id in items_dict:
    try:
      price_dict = items_dict.get(request_id).get('price')
      if '24_hours' in price_dict:
        return price_dict.get('24_hours').get('average')
      elif '7_days' in price_dict:
        return price_dict.get('7_days').get('average')
      elif '30_days' in price_dict:
        return price_dict.get('30_days').get('average')
      else:
        return price_dict.get('all_time').get('average')
    except:
      return None
  else:
    # Return None if price not found. In most cases, that gun is too expensive or doesn't exist. 
    return None


def get_price_data():

  print("Getting price data")
  # Get a JSON with data of every item in CSGO from CSGO Backpack
  request_url = "http://csgobackpack.net/api/GetItemsList/v2/"
  response = requests.get(request_url)
  response_dict = response.json()
  items_dict = response_dict.get('items_list')

  print("Reading skin data")
  skin_data = pd.read_pickle("pickle/skin_data.pkl")

  print("Checking prices")
  # Apply check price function to each row
  skin_data['Price'] = skin_data.apply(check_price, args=(items_dict,), axis=1)

  print("Saving data")
  # Pickle data and save to excel
  skin_data.to_pickle("pickle/price_data.pkl")
  skin_data.to_excel("data/price_data.xlsx", sheet_name='Prices')


if __name__ == 'main':
  get_price_data()