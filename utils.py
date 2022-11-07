import re
import numpy as np
import unidecode

SWE_LETTERS = ['å', 'Å', 'ä', 'Ä', 'ö', 'Ö']

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

# Removed all the things above letters such as Ã becomes A
# But it also keeps the swedish letters ÅÄÖ
def remove_diactrics(string):
  string = replace_weird_chars(string)
  swe_char_arr = find_swe_chars(string)
  decoded_str = unidecode.unidecode(string)
  final_str = return_swe_chars(decoded_str, swe_char_arr)
  return final_str

def find_swe_chars(string):
  result = []
  for _, c in enumerate(SWE_LETTERS):
    idx = string.find(c)
    while idx != -1:
      result.append({
        'letter': c,
        'idx': idx
      })
      idx = string.find(c, idx + 1)
  return result

# Returns swedish characters to a word where the diactrics has been removed
def return_swe_chars(string, char_arr):
  string_list = list(string)
  for _, char_obj in enumerate(char_arr):
    letter = char_obj['letter']
    idx = char_obj['idx']
    string_list[idx] = letter
  return "".join(string_list)

def replace_weird_chars(string):
  char_mappings = [
    {
      'char':'®',
      'new_char': '@'
    }
  ]
  for _, char_mapping in enumerate(char_mappings):
    char = char_mapping['char']
    new_char = char_mapping['new_char']
    if char in string:
      string = string.replace(char, new_char)
  return string
