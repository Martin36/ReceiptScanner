import json
import os
import sys
from glob import glob
from receipt_parser import GcloudParser
from categorizer import Categorizer
from prettyfier import Prettyfier
from write_to_csv import write_to_csv
from validate_json import validate_json

receipt_paths = glob("data/receipts/coop/*.pdf")
# receipt_paths += glob("data/receipts/hemkop/*")
# receipt_paths += glob("data/receipts/ica/*")

parser = GcloudParser()
categorizer = Categorizer()
prettyfier = Prettyfier()


def parse_all_pdfs():
  if os.path.exists(os.path.join(sys.path[0], "articles.json")):
    os.remove(os.path.join(sys.path[0], "articles.json"))

  f = open(os.path.join(sys.path[0], "articles.json"), "a", encoding='utf8')
  j = []

  for _, path in enumerate(receipt_paths):
    print("Parsing receipt: {}".format(path))
    articles, dates, market, discounts, totals, bounding_box = parser.parse_pdf(path)
    articles = prettyfier.clean_article_names(articles)  
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
  print("Finished parsing all receipts")

def categorize_articles():
  f = open(os.path.join(sys.path[0], "articles.json"), "r+", encoding="utf8")
  data = json.load(f)

  for _, receipt in enumerate(data):
    print("Categorizing articles for receipt {}".format(receipt['name']))
    articles = categorizer.categorize_articles(receipt['articles']) 
    discounts = categorizer.categorize_discounts(receipt['discounts'])
    receipt['articles'] = articles 
    receipt['discounts'] = discounts

  # Remove everything in the file 
  f.seek(0)
  f.truncate()
  f.write(json.dumps(data, indent=2, ensure_ascii=False))
  f.close()
  print("Finished categorizing all receipts")

parse_all_pdfs()
validate_json()
# categorize_articles()
# write_to_csv()
