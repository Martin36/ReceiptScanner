import re
import numpy as np

# This function converts a float or int number to a string 
# on the format XX,XX where X is an int
def convert_to_price_string(number):
  if type(number) is int:
    return str(number) + ",00"
  if type(number) is float: 
    return f"{number:.2f}".replace('.',',')
  else:
    return None

def convert_to_nr(string):
  try:
    parsed_number = float(string.replace(",", ".")) 
  except ValueError:
    return None
  if not parsed_number:
    return None
  return parsed_number

def get_number_from_string(string):
  rex = r'[\d]+[.,\d]+|[\d]*[.][\d]+|[\d]+'
  match = re.search(rex, string)
  if match:
    return convert_to_nr(match.group(0))
  return None
