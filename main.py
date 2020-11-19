import json
import os
import sys
import csv
from pprint import pprint
from receipt_parser import GcloudParser
from validate_receipt_data import ReceiptDataValidator


PATH = 'D:\\Documents\\Kvitto Scanner\\Receipts\\hemköp-20-10-12.pdf'
receipt_paths = [
  'D:\\Documents\\Kvitto Scanner\\Receipts\\coop-20-10-20.pdf',
  'D:\\Documents\\Kvitto Scanner\\Receipts\\coop-20-10-27.pdf',
  'D:\\Documents\\Kvitto Scanner\\Receipts\\coop-20-10-29.pdf',
  'D:\\Documents\\Kvitto Scanner\\Receipts\\coop-20-11-05.pdf',
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
  articles, dates, markets, discounts, total, bounding_box = parser.parse_pdf(PATH)
  pprint(articles)
  #print(len(articles))
  print(dates)
  print(markets)
  pprint(discounts)
  print(total)
  pprint(bounding_box)

  # Validate the parsed data
  faulty_indx = validator.check_articles(articles)
  print("Faulty articles: \n")
  print(faulty_indx)


def parse_all_pdfs():
  if os.path.exists("articles.json"):
    os.remove("articles.json")

  f = open("articles.json", "a", encoding='utf8')
  j = []

  for i, path in enumerate(receipt_paths):
    articles, dates, market, discounts, total, bounding_box = parser.parse_pdf(path)
    j.append({
      "name": path,
      "market": market, 
      "dates": dates, 
      "articles": articles, 
      "discounts": discounts,
      "total": total,
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
      print("Error for receipt '{} {}, for articles {}".format(receipt["markets"], 
        get_first(receipt["dates"]), faulty_indx))

def get_first(array):
  return next(iter(array), None)

# validate_json()
# parse_all_pdfs()
parse_one_pdf()
