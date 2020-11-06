import json
import os
from pprint import pprint
from receipt_parser import GcloudParser

PATH = 'D:\\Documents\\Kvitto Scanner\\Receipts\\coop-20-11-05.pdf'
receipt_paths = [
  'D:\\Documents\\Kvitto Scanner\\Receipts\\coop-20-10-20.pdf',
  'D:\\Documents\\Kvitto Scanner\\Receipts\\coop-20-10-27.pdf',
  'D:\\Documents\\Kvitto Scanner\\Receipts\\coop-20-10-29.pdf',
  'D:\\Documents\\Kvitto Scanner\\Receipts\\coop-20-11-05.pdf'
]

parser = GcloudParser()


def parse_one_pdf():
  articles, dates, markets, discounts, total = parser.parse_pdf(PATH)
  pprint(articles)
  #print(len(articles))
  print(dates)
  print(markets)
  print(discounts)
  print(total)


def parse_all_pdfs():
  if os.path.exists("articles.json"):
    os.remove("articles.json")

  f = open("articles.json", "a")
  j = []

  for i, path in enumerate(receipt_paths):
    articles, dates, markets, discounts, total = parser.parse_pdf(path)
    j.append({
      "markets": markets, 
      "dates": dates, 
      "articles": articles, 
      "discounts": discounts
    })

  f.write(json.dumps(j, indent=2))
  f.close()

  # j = json.dumps({
  #   "markets": markets, 
  #   "dates": dates, 
  #   "articles": articles, 
  #   "discounts": discounts
  # }, indent=2)

parse_one_pdf()
