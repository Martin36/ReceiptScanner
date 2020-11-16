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
      sum = self.get_number_from_string(article['sum'])
      calc_sum = np.round(amount*price, 2)

      if calc_sum != sum:
        faulty_indx.append(i)
    
    return faulty_indx

  # def check_nr_of_articles(self, parsed_data):


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


