from src.receipt_parser import GcloudParser
from src.validate_receipt_data import ReceiptDataValidator
from src.prettyfier import Prettyfier


PATH = "data/receipts/coop/coop-22-02-22.pdf"

parser = GcloudParser()
validator = ReceiptDataValidator()
prettyfier = Prettyfier()

def parse_one_pdf():
  articles, dates, markets, discounts, totals, bounding_box = parser.parse_pdf(PATH)
  articles = prettyfier.clean_article_names(articles)
  # pprint(articles)
  # #print(len(articles))
  # print(dates)
  # print(markets)
  # pprint(discounts)
  # print(totals)
  # pprint(bounding_box)

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


parse_one_pdf()
