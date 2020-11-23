import re
import utils
import numpy as np


class ReceiptDataValidator:
  def __init__(self, debug=False):
    self.debug = debug

  # Function for checking that all the articles on the receipt has been
  # scanned correctly
  def check_articles(self, articles):
    faulty_indx = []
    for i, article in enumerate(articles):
      amount = self.get_number_from_string(article['amount'])
      price = self.get_number_from_string(article['price'])
      article_sum = self.get_number_from_string(article['sum'])
      calc_sum = np.round(amount*price, 2)

      if calc_sum != article_sum:
        faulty_indx.append(i)
    
    return faulty_indx

  def check_nr_of_articles(self, parsed_data):
    nr_parsed_articles = self.count_articles(parsed_data['articles'])
    nr_receipt_articles = self.get_nr_receipt_articles(parsed_data['totals'])
    
    if not nr_receipt_articles:
      # This means that the amount of articles is not specified on the receipt
      # and therefore this validation is not relevant
      # TODO: This could also mean that the nr of articles were not scanned correctly
      # TODO: How should that case be handled?
      return True
    if nr_parsed_articles != nr_receipt_articles:
      return False
    return True

  # Checks if the total amount on the receip has been scanned correctly
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
    if any_incorrect:
      return False, err_msg
    return True, None

  def count_articles(self, articles):
    total = 0
    for article in articles:
      amount = article['amount']
      # If the article is measured in weight, it is counted as one
      if "kg" in amount:
        amount = 1
      else:
        amount = int(self.get_number_from_string(amount))
      
      total += amount
    
    return total
      


  # Checking if the sum on the receipt is equal to the sum of the 
  # parsed articles. If it is not, then something may have been 
  # scanned incorrectly
  # def check_sum_equal_articles(self, parsed_data):
  #   faulty_indx = []
  #   for i, receipt in enumerate(parsed_data):
  #     # receipt_sum = receipt['']



  def convert_to_nr(self, string):
    parsed_number = float(string.replace(",", ".")) 
    if not parsed_number:
      return None
    return parsed_number
  
  def get_number_from_string(self, string):
    rex = r'[\d]+[.,\d]+|[\d]*[.][\d]+|[\d]+'
    match = re.search(rex, string)
    if match:
      return self.convert_to_nr(match.group(0))
    return None

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
