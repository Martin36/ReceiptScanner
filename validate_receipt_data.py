import re
import utils
import numpy as np

# Articles that should not be counted (for now, only for city gross receipts)
SKIP_ARTICLES = ['pant']

class ReceiptDataValidator:
  def __init__(self, debug=False):
    self.debug = debug

  # Function for checking that all the articles on the receipt has been
  # scanned correctly
  def check_articles(self, articles):
    faulty_indx = []
    for i, article in enumerate(articles):
      amount = utils.get_number_from_string(article['amount'])
      price = utils.get_number_from_string(article['price'])
      article_sum = utils.get_number_from_string(article['sum'])
      calc_sum = np.round(amount*price, 2)
      if calc_sum != article_sum:
        faulty_indx.append(i)
    return faulty_indx

  def check_nr_of_articles(self, parsed_data):
    market = parsed_data['market']
    nr_parsed_articles = self.count_articles(parsed_data['articles'], market)
    nr_receipt_articles = self.get_nr_receipt_articles(parsed_data['totals'])
    err_msg = None
    if not nr_receipt_articles:
      # This means that the amount of articles is not specified on the receipt
      # and therefore this validation is not relevant
      # TODO: This could also mean that the nr of articles were not scanned correctly
      # TODO: How should that case be handled?
      return True, err_msg
    if nr_parsed_articles != nr_receipt_articles:
      err_msg = 'Error: nr of parsed articles were {}, but the amount on the receipt were {}'.format(nr_parsed_articles, nr_receipt_articles)
      return False, err_msg
    return True, err_msg

  # Checks if the total amount on the receipt has been scanned correctly
  def check_totals(self, totals):
    if len(totals) == 0:
      err_msg = "Error: No totals have been found on this receipt"
      return False, err_msg
    # Assume that no receipt can have more than 2 totals
    if len(totals) > 2:
      err_msg = "Error: More than two totals have been found on this receipt"
      return False, err_msg
    any_incorrect = False
    err_msg = None
    for total in totals:
      # Each total should have either a sum or an amount (or both)
      if "sum" in total:
        if not utils.check_price(total['sum']):
          any_incorrect = True
          err_msg = "Error: total with incorrect sum"
      if "amount" in total:
        if not utils.is_integer(total['amount']):
          any_incorrect = True
          err_msg = "Error: total with incorrect amount"    
      if "sum" not in total and \
         "amount" not in total:
        any_incorrect = True
        err_msg = "Error: total must have either 'sum' or 'amount'"
    if any_incorrect:
      return False, err_msg
    return True, None

  def check_dates(self, dates):
    if len(dates) == 0:
      err_msg = "Error: No dates found for receipt"
      return False, err_msg
    if len(dates) > 1:
      prev_date = None
      for date in dates:
        if prev_date and \
           prev_date != date:
          # TODO: Ask the user which date is correct
          err_msg = "Error: Multiple different dates found"
          return False, err_msg
    return True, None

  def count_articles(self, articles, market):
    total = 0
    for article in articles:
      # For city gross receipts, pant and bags should not be counted
      if market == 'city gross' and \
         self.check_if_skip_article(article['name']):
        continue
      amount = article['amount']
      # If the article is measured in weight, it is counted as one
      if "kg" in amount:
        amount = 1
      else:
        amount = int(utils.get_number_from_string(amount))
      total += amount
    return total
        
  # TODO: What if there are multiple totals with nr of articles
  def get_nr_receipt_articles(self, totals):
    result = None
    amount = None
    for total in totals:
      if 'amount' in total:
        amount = total['amount']
      if amount != None:
        result = int(amount)
    return result

  def check_if_skip_article(self, name):
    for string in SKIP_ARTICLES:
      reg = re.compile(string)
      if re.search(reg, name.lower()):
        return True
    return False