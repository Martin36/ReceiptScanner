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

# Returns the string with only one minus sign instead of multiple
# Used for when the OCR scan happens to think there is multiple 
# minus signs instead of only one
def remove_double_minus_sign(string):
  rex = r'-*(-\d+,\d\d)'
  match = re.search(rex, string)
  if match:
    return match.group(1)
  else:
    return string

def get_first(array):
  return next(iter(array), None)

# Function for detecting a price string
# A price string has the format (X)XX,XX
# Returns false if the string does not represent a price
def check_price(string):
  rex = r'-*\d+[,|.]\d\d'
  if re.fullmatch(rex, string):
    return string
  return False

def is_integer(text_body):
  try:
    _ = int(text_body)
  except:
    return False
  if round(float(text_body)) == float(text_body):
    return True
  return False

