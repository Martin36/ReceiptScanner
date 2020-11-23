import json
import os
import csv
import utils
import numpy as np

with open('articles.csv', 'w', newline='', encoding='utf8') as csvfile:
  csv_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
  
  f = open('articles.json', encoding='utf8')
  json_data = json.load(f)

  # Add the header
  csv_writer.writerow(['Market', 'Date', 'Receipt total', 'Article name', 'Sum'])

  for receipt in json_data:
    
    market = receipt['market'][0]
    date = utils.get_first(receipt['dates'])
    # If the receipt contains multiple totals, the lowest is probably the amount paid
    # with the higher being the sum without discounts
    total = get_smallest_total(receipt['totals'])

    for article in receipt['articles'] + receipt['discounts']:
      name = article['name']
      price_sum = article['price']
      csv_writer.writerow([market, date, total, name, price_sum])   

  f.close()
  print("Finished writing to csv file")

def get_smallest_total(totals):
  
  np.min([utils.convert_to_nr(total['sum']) for total in receipt['totals']]) 