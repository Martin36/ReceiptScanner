import argparse
from receipt_parser import GcloudParser
from utils import filter_articles
from validate_receipt_data import ReceiptDataValidator
from prettyfier import Prettyfier
from utils_package import store_json

parser = GcloudParser()
validator = ReceiptDataValidator()
prettyfier = Prettyfier()


def parse_one_pdf(pdf_file: str):
  parse_res = parser.parse_pdf(pdf_file)

  articles = prettyfier.clean_article_names(parse_res["articles"])
  for article in articles:
    del article["bounding_box"]
  articles = filter_articles(articles)
  
  # Validate the parsed data
  faulty_indx = validator.check_articles(articles)
  print("Faulty articles:")
  print(faulty_indx)
  
  # TODO: How to remove duplicate discounts?

  result_obj = {
    "articles": articles, 
    "dates": parse_res["dates"], 
    "market": parse_res["market"], 
    "discounts": parse_res["discounts"], 
    "totals": parse_res["totals"], 
    "bounding_box": parse_res["bounding_box"]
  }

  if not validator.check_nr_of_articles(result_obj):
    print("The parsed nr of articles are not the same as the amount on the receipt")
    
  return result_obj

if __name__ ==  "__main__":
  arg_parser = argparse.ArgumentParser(
    description="Parses a single PDF file into a structured format"
  )
  arg_parser.add_argument(
    "--input_file", 
    help="Path to the PDF file to be parsed"
  )
  arg_parser.add_argument(
    "--output_file", 
    help="Path to the json file to store the output"
  )
  args = arg_parser.parse_args()
  
  result = parse_one_pdf(args.input_file)
  
  if args.output_file:
    store_json(result, args.output_file)