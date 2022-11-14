from collections import defaultdict
import json, utils, argparse
from validate_receipt_data import ReceiptDataValidator

validator = ReceiptDataValidator()

stats = defaultdict(int)

def validate_receipt(receipt: dict):
  faulty_indx = validator.check_articles(receipt["articles"])
  if len(faulty_indx) != 0:
    faulty_articles = [article for idx, article in 
                        enumerate(receipt["articles"]) 
                        if idx in faulty_indx]
    print("Error for receipt '{} {}, for articles {}".format(receipt["market"], 
      utils.get_first(receipt["dates"]), faulty_indx))
    stats["receipts with faulty articles"] += 1
    
  
  # Check that the nr of articles are correct
  if not validator.check_nr_of_articles(receipt):
    nr_parsed_articles = validator.count_articles(receipt['articles'])
    nr_receipt_articles = validator.get_nr_receipt_articles(receipt['totals'], nr_parsed_articles)
    market = receipt["market"]
    date = utils.get_first(receipt["dates"])
    print(f"Error for receipt '{market} {date}, the parsed number of articles is {nr_parsed_articles} and the number on the receipt is {nr_receipt_articles}")
    stats["receipts with incorrect nr of articles"] += 1

  # Check that the totals has been correctly parsed
  totals_correct, err_msg = validator.check_totals(receipt['totals'])
  if not totals_correct:
    print("Error for receipt: {}".format(receipt['name']))
    print(err_msg)
    stats["receipts with incorrect totals"] += 1
  
  # Check that the receipt has at least one date
  date_correct, err_msg = validator.check_dates(receipt['dates'])
  if not date_correct:
    print("Error for receipt: {}".format(receipt['name']))
    print(err_msg)
    stats["receipts with incorrect dates"] += 1
    
  stats["total receipts"] += 1


def validate_json(file: str):
  f = open(file)
  data = json.load(f)
  
  if type(data) is dict:
    validate_receipt(data)
  else:  
    for receipt in data:
      validate_receipt(receipt)    
    print("All receipts validated")

if __name__ == "__main__":
  arg_parser = argparse.ArgumentParser(
    description="Validates an json output from the receipt parser"
  )
  arg_parser.add_argument("--file", help="Path to the file to be validated")
  args = arg_parser.parse_args()

  validate_json(args.file)
  
  print(stats)