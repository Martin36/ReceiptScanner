import os, json, utils, sys, argparse
from validate_receipt_data import ReceiptDataValidator

validator = ReceiptDataValidator()


def validate_json(file: str):
  f = open(file)
  data = json.load(f)
  
  for receipt in data:
    
    faulty_indx = validator.check_articles(receipt["articles"])
    if len(faulty_indx) != 0:
      faulty_articles = [article for idx, article in 
                         enumerate(receipt["articles"]) 
                         if idx in faulty_indx]
      print("Error for receipt '{} {}, for articles {}".format(receipt["market"], 
        utils.get_first(receipt["dates"]), faulty_indx))
      
    
    # Check that the nr of articles are correct
    if not validator.check_nr_of_articles(receipt):
      print("Error for receipt '{} {}, the parsed number of articles does not coincide with the number on the receipt"
        .format(receipt["market"], utils.get_first(receipt["dates"])))
  
    # Check that the totals has been correctly parsed
    totals_correct, err_msg = validator.check_totals(receipt['totals'])
    if not totals_correct:
      print("Error for receipt: {}".format(receipt['name']))
      print(err_msg)
    
    # Check that the receipt has at least one date
    date_correct, err_msg = validator.check_dates(receipt['dates'])
    if not date_correct:
      print("Error for receipt: {}".format(receipt['name']))
      print(err_msg)
  print("All receipts validated")

if __name__ == "__main__":
  arg_parser = argparse.ArgumentParser(
    description="Validates an json output from the receipt parser"
  )
  arg_parser.add_argument("--file", help="Path to the file to be validated")
  args = arg_parser.parse_args()

  validate_json(args.file)