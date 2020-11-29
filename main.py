import json
import os
import sys
import csv
import utils
from pprint import pprint
from receipt_parser import GcloudParser
from validate_receipt_data import ReceiptDataValidator
from write_to_csv import write_to_csv


PATH = 'D:\\Documents\\Kvitto Scanner\\Receipts\\hemköp-20-10-12.pdf'
receipt_paths = [
  'D:\\Documents\\Kvitto Scanner\\Receipts\\coop-20-10-20.pdf',
  'D:\\Documents\\Kvitto Scanner\\Receipts\\coop-20-10-27.pdf',
  'D:\\Documents\\Kvitto Scanner\\Receipts\\coop-20-10-29.pdf',
  'D:\\Documents\\Kvitto Scanner\\Receipts\\coop-20-11-05.pdf',
  'D:\\Documents\\Kvitto Scanner\\Receipts\\coop-20-11-22.pdf',
  'D:\\Documents\\Kvitto Scanner\\Receipts\\coop-20-11-25.pdf',
  'D:\\Documents\\Kvitto Scanner\\Receipts\\hemköp-20-10-02.pdf',
  'D:\\Documents\\Kvitto Scanner\\Receipts\\hemköp-20-10-12.pdf',
  'D:\\Documents\\Kvitto Scanner\\Receipts\\hemköp-20-10-18.pdf',
  'D:\\Documents\\Kvitto Scanner\\Receipts\\hemköp-20-10-24.pdf',
  'D:\\Documents\\Kvitto Scanner\\Receipts\\ica-20-10-11.pdf',
  'D:\\Documents\\Kvitto Scanner\\Receipts\\ica-20-11-09.pdf',
]

parser = GcloudParser()
validator = ReceiptDataValidator()

def parse_one_pdf():
  articles, dates, markets, discounts, totals, bounding_box = parser.parse_pdf(PATH)
  pprint(articles)
  #print(len(articles))
  print(dates)
  print(markets)
  pprint(discounts)
  print(totals)
  pprint(bounding_box)

  # Validate the parsed data
  faulty_indx = validator.check_articles(articles)
  print("Faulty articles:")
  print(faulty_indx)

  result_obj = {
    "articles": articles, 
    "dates": dates, 
    "markets": markets, 
    "discounts": discounts, 
    "totals": totals, 
    "bounding_box": bounding_box
  }
  is_corr_nr_articles = validator.check_nr_of_articles(result_obj)
  if not is_corr_nr_articles:
    print("The parsed nr of articles are not the same as the amount on the receipt")


def parse_all_pdfs():
  if os.path.exists(os.path.join(sys.path[0], "articles.json")):
    os.remove(os.path.join(sys.path[0], "articles.json"))

  f = open(os.path.join(sys.path[0], "articles.json"), "a", encoding='utf8')
  j = []

  for _, path in enumerate(receipt_paths):
    articles, dates, market, discounts, totals, bounding_box = parser.parse_pdf(path)
    j.append({
      "name": path,
      "market": market, 
      "dates": dates, 
      "articles": articles, 
      "discounts": discounts,
      "totals": totals,
      "bounding_box": bounding_box
    })

  f.write(json.dumps(j, indent=2, ensure_ascii=False))
  f.close()

def validate_json():
  f = open(os.path.join(sys.path[0], "articles.json"), "r", encoding="utf8")
  data = json.load(f)
  
  for receipt in data:
    faulty_indx = validator.check_articles(receipt["articles"])
    if len(faulty_indx) != 0:
      print("Error for receipt '{} {}, for articles {}".format(receipt["market"], 
        utils.get_first(receipt["dates"]), faulty_indx))
    
    # Check that the nr of articles are correct
    if not validator.check_nr_of_articles(receipt):
      print("Error for receipt '{} {}, the parsed number of articles does not coincide with the number of the receipt"
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

validate_json()
# parse_all_pdfs()
# parse_one_pdf()
# write_to_csv()
