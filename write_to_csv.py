import json
import os
import csv
import utils
import sys
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
  return str(total_sum)
