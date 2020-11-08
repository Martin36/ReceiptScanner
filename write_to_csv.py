import json
import os
import csv

with open('articles.csv', 'w', newline='', encoding='utf8') as csvfile:
  csv_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
  
  f = open('articles.json', encoding='utf8')
  json_data = json.load(f)

  # Add the header
  csv_writer.writerow(['Market', 'Date', 'Receipt total', 'Article name', 'Sum'])

  for receipt in json_data:
    
    market = receipt['markets'][0]
    date = receipt['dates'][0]
    total = receipt['total']

    for article in receipt['articles'] + receipt['discounts']:
      name = article['name']
      price_sum = article['price']
      csv_writer.writerow([market, date, total, name, price_sum])   

  f.close()
  print("Finished writing to csv file")
