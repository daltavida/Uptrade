import pandas as pd
from util.misc_data import *


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
  outcomes = outcomes[~pd.isnull(outcomes['Price'])]
  
  return list(outcomes.index.values)


def get_usage_data():
  print("Reading price data")
  price_data = pd.read_pickle("pickle/price_data.pkl")

  print("Checking outcomes")
  price_data['Outcomes'] = price_data.apply(get_outcomes, axis=1, args=(price_data,))

  print("Checking usability")
  # A skin can only be used in trade up contracts if it has at least one outcome
  price_data['Usable'] = price_data['Outcomes'].apply(lambda x : False if len(x) == 0 else True)

  print("Saving data")
  # Pickle data and save to excel
  price_data.to_pickle("pickle/usage_data.pkl")
  price_data.to_excel("data/usage_data.xlsx", sheet_name='Usage')


if __name__ == 'main':
  get_usage_data()