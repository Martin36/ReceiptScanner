import json
import os
import csv
import src.utils as utils
import sys
import numpy as np

def write_to_csv():
  with open(os.path.join(sys.path[0], 'articles.csv'), 'w', newline='', encoding='utf8') as csvfile:
    csv_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    
    f = open(os.path.join(sys.path[0], 'articles.json'), 'r', encoding='utf8')
    json_data = json.load(f)

    # Add the header
    csv_writer.writerow(['Market', 'Date', 'Receipt total', 'Article name', 
      'Sum', 'Quantity', 'Price', 'Category'])

    for receipt in json_data:
      
      market = receipt['market']
      date = utils.get_first(receipt['dates'])
      # If the receipt contains multiple totals, the lowest is probably the amount paid
      # with the higher being the sum without discounts
      total = get_smallest_total(receipt['totals'])

      for article in receipt['articles']:
        name = article['name']
        price_sum = article['sum']
        quantity = article['amount']
        price = article['price']
        category = article['category']
        csv_writer.writerow(
          [market, date, total, name, price_sum, quantity, price, category]
        )   

      for discount in receipt['discounts']:
        name = discount['name']
        price_sum = discount['price']
        quantity = ""
        price = discount['price']
        category = discount['category']
        csv_writer.writerow(
          [market, date, total, name, price_sum, quantity, price, category]
        )   

    f.close()
    print("Finished writing to csv file")

def get_smallest_total(totals):
  if len(totals) == 0:
    return ""
  total_sum = sys.float_info.max
  for total in totals:
    if 'sum' in total:
      sum_nr = utils.convert_to_nr(total['sum'])
      if sum_nr < total_sum:
        total_sum = sum_nr
  if total_sum == sys.float_info.max:
    # This means that no total sum were found
    return ""
  return utils.convert_to_price_string(total_sum)
