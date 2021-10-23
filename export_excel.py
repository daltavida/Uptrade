from os import listdir
from os.path import isfile, join
import pickle
import pandas as pd

file_list = [f for f in listdir('tradeups') if isfile(join('tradeups', f))]
file_list = [f for f in file_list if 'tradeups' in f]

profitable_tradeups = []

for file in file_list:
  with open(f'tradeups/{file}', 'rb') as tradeups:
    profitable_tradeups += pickle.load(tradeups) 

df = pd.DataFrame(profitable_tradeups, columns=['inputs', 'profit %'])
df.to_excel("Profitable Tradeups.xlsx")  
