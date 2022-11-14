

import argparse
from utils_package import store_json, load_json

from utils import filter_articles
from validate_json import validate_receipt

if __name__ ==  "__main__":
  arg_parser = argparse.ArgumentParser(
    description="Filters out all the duplicate articles"
  )
  arg_parser.add_argument(
    "--input_file", 
    help="Path to the json file where the receipts are stored"
  )
  arg_parser.add_argument(
    "--output_file", 
    help="Path to the json file to store the output"
  )
  arg_parser.add_argument(
    "--validate_receipt",
    action="store_true",
    help="If set, the articles will be validated"
  )
  args = arg_parser.parse_args()
  
  receipts = load_json(args.input_file)
  for receipt in receipts:
    articles = receipt["articles"]
    articles = filter_articles(articles)
    receipt["articles"] = articles
      
    if args.validate_receipt:
      validate_receipt(receipt)      
  
  store_json(receipts, args.output_file)