import pandas as pd
from util.misc_data import *
import math

# A function to get all the skins a skin can trade up to. Only includes the ST FN version
def get_outcomes(row, price_data):
  print(f"Found outcomes for {row.name}")
  
  # If rarity is higher than classified or no price available, the skin has no outcomes
  if row["Rarity"] == 'Covert' or row["Rarity"] == 'Contraband':
    return []
  if pd.isnull(row['Price']) or row['Price'] == 0:
    return []
  
  # Get all skins of the next rarity from the same collection
  collection_weapons = price_data[price_data['Collection'] == row['Collection']]
  next_rarity = rarities.get(row['Rarity'])
  
  # Only use outcomes that have a price
  outcomes = collection_weapons[collection_weapons['Rarity'] == next_rarity]
  outcomes = outcomes[(outcomes['Stattrak'] == row['Stattrak']) & (outcomes['Wear'] == "Factory New")]
  
  return list(outcomes.index.values)


# A function to see how much profit a single skin can make
def get_profitability(row, price_data):
  print(f"Found profitability for {row.name}")
  
  cost = row['Price'] * 10
  total_profit = 0
  num_outcomes = 0
  wear = row['Wear']
  
  for outcome in row['Outcomes']:
    price = 0
    
    if wear == 'Factory New':
      price = price_data.loc[outcome]['Price']
    elif wear == 'Minimal Wear':
      price = price_data.loc[outcome + 2]['Price']
    elif wear == 'Field-Tested':
      price = price_data.loc[outcome + 4]['Price']
    elif wear == 'Well-Worn':
      price = price_data.loc[outcome + 6]['Price']
    else:
      price = price_data.loc[outcome + 8]['Price']

    if math.isnan(price):
      return 0
    else:
      total_profit += (price - cost)
      num_outcomes += 1

  if num_outcomes == 0:
    return 0
  else:
    return total_profit/num_outcomes


def get_usage_data():
  print("Reading price data")
  price_data = pd.read_pickle("pickle/price_data.pkl")

  print("Checking outcomes")
  price_data['Outcomes'] = price_data.apply(get_outcomes, axis=1, args=(price_data,))

  print("Checking usability")
  # A skin can only be used in trade up contracts if it has at least one outcome
  price_data['Usable'] = price_data['Outcomes'].apply(lambda x : False if len(x) == 0 else True)
  price_data['Profit'] = price_data.apply(get_profitability, axis=1, args=(price_data,))

  # Fix numbers stored as string error
  price_data['Min Float'] = price_data['Min Float'].astype(float)
  price_data['Max Float'] = price_data['Max Float'].astype(float)
  
  print("Saving data")
  # Pickle data and save to excel
  price_data.to_pickle("pickle/usage_data.pkl")
  price_data.to_excel("data/usage_data.xlsx", sheet_name='Usage')