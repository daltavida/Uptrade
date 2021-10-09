import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from util.misc_data import *


# Function that calculates the float to use for each gun. Average float in most cases.
def float_to_use(row):
  print(f"Calculated float for {row.name}")
  wear = row['Wear']
  wear_float = float_values.get(wear)
  wear_min = wear_float[0]
  wear_max = wear_float[1]

  gun_min = float(row['Min Float'])
  gun_max = float(row['Max Float'])

  # Some guns have unique max and min float. For those, use the unique float to find average.
  if gun_min > wear_min:
    wear_min = gun_min
  if gun_max < wear_max:
    wear_max = gun_max

  return (wear_max + wear_min )/ 2


def get_data():
  print("Opening browser")
  # Start the driver and get collection data from CSGO Exchange
  driver = webdriver.Chrome()
  driver.get('http://csgo.exchange/collection/')
  driver.maximize_window()

  try:

    # List to contain dictionaries to later add to a dataframe
    row_list = []

    # Wait until main content loads and get a list of all collections
    main = WebDriverWait(driver, 10).until(
      EC.presence_of_element_located((By.CLASS_NAME, 'contentMain'))
    )
    collections = main.text.split('\n')
    
    for collection in collections:
      
      # Click on a collection and wait until weapons from that collection load
      driver.find_element_by_xpath(f"//*[@data-custom='{collection}']").click()
      window = WebDriverWait(driver, 100).until(
        EC.presence_of_element_located((By.XPATH, "//*[@id='widw'][contains(@style, 'display: block')]"))
      )

      weaponCollection = window.find_element_by_css_selector('div.weaponCollection')
      weapons = weaponCollection.find_elements_by_css_selector('div.vItem.Normal')

      for weapon in weapons:
        
        # Hover over each weapon in collection to get extra information
        reset = driver.find_element_by_tag_name('a')
        hover = ActionChains(driver).move_to_element(reset)
        hover.perform()

        hover = ActionChains(driver).move_to_element(weapon)
        hover.perform()

        itemData = WebDriverWait(driver, 100).until(
          EC.presence_of_element_located((By.XPATH, "//*[@class='ItemData'][contains(@style, 'display: block')]"))
        )
    
        # Store the collection, gun, skin, rarity, minimum float and maximum float for each weapon 
        description = itemData.find_element_by_tag_name('h3').text
        description = description.split('|')
        gun = description[0].strip()
        skin = description[1].strip()
        rarity = itemData.find_element_by_tag_name('div').text
        max_float = itemData.find_element_by_class_name('value-max').text.split(' ')[-1]
        min_float = itemData.find_element_by_class_name('value-min').text.split(' ')[-1]
        
        row_dict = {
          'Collection' : collection,
          'Gun' : gun,
          'Skin' : skin,
          'Rarity' : rarity,
          'Max Float' : max_float,
          'Min Float' : min_float
        }
        row_list.append(row_dict)

      # Refresh page to remove overlay
      driver.refresh()

    print("Saving Collection Data")
    # Pickle data and save to excel
    skin_df = pd.DataFrame(row_list, columns=['Collection','Gun','Skin','Rarity','Max Float','Min Float'])
    skin_df.to_pickle('pickle/collection_data.pkl')
    skin_df.to_excel('data/collection_data.xlsx', sheet_name='Collections')
  finally:
    driver.quit()

  print("Fixing skin and gun names")
  # The names on CSGO Exchange and CSGO Backpack don't match
  skin_df['Gun'] = skin_df['Gun'].map(weapon_map)
  skin_df['Skin'] = skin_df['Skin'].map(skin_map).fillna(skin_df['Skin'])
  col_names = skin_df.columns
  
  print("Creating Stattrak and wear variants")
  # Create 10 rows for each weapon, one version for every wear, stattrak and normal
  wear = pd.Series(np.tile(wear_types, len(skin_df)))
  stattrak = pd.Series(np.tile([True, False], len(wear)))
  wear = pd.Series(np.repeat(wear, 2)).reset_index(drop=True)

  skin_df = pd.DataFrame(np.repeat(skin_df.values, 10, axis=0))
  skin_df.columns = col_names

  skin_df['Wear'] = wear
  skin_df['Stattrak'] = stattrak

  print("Getting float values")
  # Decide what float to use for each weapon
  skin_df['Float'] = skin_df.apply(float_to_use, axis=1)

  print("Saving data")
  # Pickle data and save to excel
  skin_df.to_pickle("pickle/skin_data.pkl")
  skin_df.to_excel("data/skin_data.xlsx", sheet_name='Skins')


if __name__ == 'main':
  get_data()