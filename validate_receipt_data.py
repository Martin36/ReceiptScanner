import re
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
    nr_of_parsed_articles = parsed_data['articles']

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
    rex = '[\d]+[.,\d]+|[\d]*[.][\d]+|[\d]+'
    match = re.search(rex, string)
    if match:
      return self.convert_to_nr(match.group(0))
    return None


