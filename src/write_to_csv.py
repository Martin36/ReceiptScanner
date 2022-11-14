import argparse
import csv
import os
from typing import Union
import utils
import sys
from utils_package import load_json

def write_to_csv(data: Union[dict,list], csv_file: str):
  with open(csv_file, 'w', newline='', encoding='utf8') as csvfile:
    csv_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    
    # Add the header
    csv_writer.writerow(['Market', 'Date', 'Receipt total', 'Article name', 
      'Sum', 'Quantity', 'Price', 'Category'])
    
    if type(data) is not list:
      data = [data]

    for receipt in data:
      
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
        category = article.get('category', None)
        csv_writer.writerow(
          [market, date, total, name, price_sum, quantity, price, category]
        )   

      for discount in receipt['discounts']:
        name = discount['name']
        price_sum = discount['price']
        quantity = ""
        price = discount['price']
        category = discount.get('category', None)
        csv_writer.writerow(
          [market, date, total, name, price_sum, quantity, price, category]
        )   

    print(f"Stored results in {csv_file}")


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


def write_to_folder(json_file: str, folder: str):
  receipts = load_json(json_file)
  
  for receipt in receipts:
    market = receipt['market']
    date = utils.get_first(receipt['dates'])
    file_name = os.path.join(folder, f"{market}-{date}.csv")
    write_to_csv(receipt, file_name)


if __name__ == "__main__":
  arg_parser = argparse.ArgumentParser(
    description="Converts a json file of receipts to a csv file, or a folder of csv files, one for each receipt"
  )
  arg_parser.add_argument(
    "--json_file", 
    help="Path to the json file to be converted"
  )
  arg_parser.add_argument(
    "--csv_file", 
    help="Path to the output csv file"
  )
  arg_parser.add_argument(
    "--csv_folder", 
    help="Path to the output csv file"
  )  
  args = arg_parser.parse_args()

  if args.csv_folder:
    write_to_folder(args.json_file, args.csv_folder)
  elif args.csv_file:
    write_to_csv(args.json_file, args.csv_file)
  else:
    print("You need to specify either --csv_file or --csv_folder")