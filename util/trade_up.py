import pandas as pd
import itertools
import pickle
import os.path
import math

# A function that calculates the profit percentage given 10 inputs to a trade up contract
def get_profit(inputs, usage_data):
  avg_float = 0
  cost = 0

  # Get every possible outcome from the trade up
  possible_outcomes = []

  for gun in inputs:
    gun_data = usage_data.loc[gun]
    avg_float += gun_data['Float']/10
    cost += gun_data['Price']

    for outcome in gun_data['Outcomes']:
      possible_outcomes.append(outcome)

  num_outcomes = 0
  expected_value = 0

  # For each outcome, check what float of that outcome you can get
  for possible_outcome in possible_outcomes:
    outcome_data = usage_data.loc[possible_outcome]
    min_float = outcome_data['Min Float']
    max_float = outcome_data['Max Float']
    
    outcome_float = ((max_float-min_float)* avg_float) + min_float
    
    outcome = 0

    # Because of the way that data is stored, simply adding 2 to an outcome changes it to next wear
    if outcome_float < 0.07:
      outcome = possible_outcome
    elif outcome_float < 0.15:
      outcome = possible_outcome + 2
    elif outcome_float < 0.38:
      outcome = possible_outcome + 4
    elif outcome_float < 0.45:
      outcome = possible_outcome + 6
    else:
      outcome = possible_outcome + 8

    num_outcomes += 1
    if math.isnan(usage_data.loc[outcome]['Price']):
      return None
    expected_value += usage_data.loc[outcome]['Price']

  # Find the profit percentage
  expected_value = expected_value / num_outcomes
  profit = expected_value - cost 
  profit_percent = (profit * 100) / cost

  return profit_percent


def find_tradeups(skin_pool, usage_data, rarity, stattrak):
  print(f'Finding tradeups for {rarity} {stattrak}')
  if skin_pool.empty:
    return

  if os.path.isfile(f'tradeups/{rarity}_{stattrak}_iterable.pkl'):
    print("Resusing data")

    with open(f'tradeups/{rarity}_{stattrak}_iterable.pkl', 'rb') as iterator:
      skin_pool_iterable = pickle.load(iterator)
    with open(f'tradeups/{rarity}_{stattrak}_tradeups.pkl', 'rb') as tradeups:
      profitable_tradeups = pickle.load(tradeups)    
  else:
    print("Creating new data")
    
    skin_pool_iterable = itertools.combinations_with_replacement(skin_pool.index.values, 10)
    profitable_tradeups = []

  count = 0
  hasNext = True
  while hasNext:
    inputs = next(skin_pool_iterable)
    if inputs == None:
      hasNext = False
      return

    profit = get_profit(inputs, usage_data)
    if profit is not None:
      profitable_tradeups.append((inputs, profit))

    count += 1
    if count % 10000 == 0:
      print(f'Processed {count} for {rarity} {stattrak}')
      best_tradeups = sorted(profitable_tradeups, key = lambda x: x[1], reverse = True)[:1000]
      
      with open(f'tradeups/{rarity}_{stattrak}_tradeups.pkl', 'wb') as tradeups:
        pickle.dump(best_tradeups, tradeups, protocol=pickle.HIGHEST_PROTOCOL)
      
      with open(f'tradeups/{rarity}_{stattrak}_iterable.pkl', 'wb') as iterator:
        pickle.dump(skin_pool_iterable, iterator, protocol=pickle.HIGHEST_PROTOCOL)