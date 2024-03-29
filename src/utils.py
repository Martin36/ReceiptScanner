import re
from typing import List, Union
import numpy as np
import unidecode
from copy import deepcopy

SWE_LETTERS = ['å', 'Å', 'ä', 'Ä', 'ö', 'Ö']

def closest_value(list: List[int], value: int):
  """Returns the closest value in a list to a given value

  Args:
      list (List[int]): The list to search in
      value (int): The value to look for

  Returns:
      int: The closest value in the list
  """
  arr = np.asarray(list)
  idx = (np.abs(arr - value)).argmin()
  return arr[idx]


def convert_to_price_string(number: Union[int, float]):
  """Function that converts a float or int to a string
  on the format XX.XX where X is an int

  Args:
      number (Union[int, float]): The number to convert

  Returns:
      str: The number as a string 
  """
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


def filter_articles(articles: list):
  """Filters out the articles that are duplicates, ignoring 'pant' 
  as these can be multiple per receipt

  Args:
      articles (list): A list of articles

  Returns:
      list: A filtered list of articles
  """
  # Need to remove the bounding box first
  mod_articles = deepcopy(articles)
  for article in mod_articles:
    if 'bounding_box' in article:
      del article['bounding_box']
  filtered_articles = []
  for article in mod_articles:
    if "pant" in article["name"].lower():
      filtered_articles.append(article)
    elif article not in filtered_articles:
      filtered_articles.append(article)
  return filtered_articles


def get_bb_corners(vertices):
  """Returns the corners of the bounding box

  Args:
      vertices (any): The vertices of the bounding polygon

  Returns:
      tuple: A tuple of (xmin, xmax, ymin, ymax)
  """
  xmin = np.min([v.x for v in vertices])
  xmax = np.max([v.x for v in vertices])
  ymin = np.min([v.y for v in vertices])
  ymax = np.max([v.y for v in vertices])
  return xmin, xmax, ymin, ymax


def get_first(array):
  return next(iter(array), None)


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
