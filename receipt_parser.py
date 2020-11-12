import io
import os
import datetime
import numpy as np
import regex

from google.cloud import vision_v1
from pdf2image import convert_from_path

MARKETS = ['ica', 'coop', 'hemköp']
SKIPWORDS = ['SEK', 'www.coop.se', 'Tel.nr:', 'Kvitto:', 'Datum:', 'Kassör:', 'Org Nr:']
STOPWORDS = []
BLACKLIST_WORDS = []
TOTAL_WORDS = ['ATT BETALA']
# This represents the offset on the x-axis that the additional information
# has from the start of the article name. It needs to be tweaked so that it
# works correctly
X_OFFSET = 50
# This represents the distance from the edge of the receipt that the 
# price should end AFTER. It is not an optimal solution since the 
# required distance may differ between receipts
PRICE_OFFSET = 200

class GcloudParser:
  def __init__(self, debug=False, min_length=5, max_height=1):
    self.debug = debug
    self.min_length = min_length
    self.max_height = max_height
    self.client = vision_v1.ImageAnnotatorClient()
    self.allowed_labels = ['article', 'price', 'market', 'address', 'date', 'misc']
    self.total_amount = 0
    self.market = None

  def parse_pdf(self, path):
    pages = convert_from_path(path, 500)
    articles = []
    dates = []
    discounts = []
    for page in pages:
      page.save('tmp.jpg')
      gcloud_response = self.detect_text('tmp.jpg')
      os.system('del tmp.jpg')
      _art, _dat, _mar, _dis = self.parse_response(gcloud_response)
      articles += _art
      dates += _dat
      discounts += _dis
    return articles, dates, self.market, discounts, self.total_amount

  # Detects text in the file.
  def detect_text(self, path):
    with io.open(path, 'rb') as image_file:
      content = image_file.read()
    image = vision_v1.types.Image(content=content)
    response = self.client.text_detection(image=image)
    if response.error.message:
      raise Exception(
        '{}\nFor more info on error messages, check: '
        'https://cloud.google.com/apis/design/errors'.format(
          response.error.message))
    return response

  def parse_response(self, gcloud_response):
    articles = []
    dates = []
    discounts = []
    seen_indexes = []
    seen_prices = []
    parsed_y = 0
    base_ann = gcloud_response.text_annotations[0]
    g_xmin = np.min([v.x for v in base_ann.bounding_poly.vertices])
    g_xmax = np.max([v.x for v in base_ann.bounding_poly.vertices])
    g_ymin = np.min([v.y for v in base_ann.bounding_poly.vertices])
    g_ymax = np.max([v.y for v in base_ann.bounding_poly.vertices])
    break_this = False
    sorted_annotations = gcloud_response.text_annotations[1:]
    # sorted_annotations = sorted(gcloud_response.text_annotations[1:],
    #                             key=lambda x: x.bounding_poly.vertices[0].y)
    current_name = ''    
    for i, annotation in enumerate(sorted_annotations):
      skip_this = False

      for skipword in SKIPWORDS+STOPWORDS+BLACKLIST_WORDS:
        if skipword.lower() in annotation.description.lower().split(' '):
          if(self.debug):
            print("Skipping: " + str(annotation.description))
          skip_this = True

      if skip_this:
        continue

      if i in seen_indexes:
        continue

      t_type = self.check_annotation_type(annotation.description)

      if self.debug:
        print(annotation.description + ' ' + t_type)

      if t_type == 'text':
        if break_this:
          continue
        used_idx = []
        used_pr = []
        xmin = np.min([v.x for v in annotation.bounding_poly.vertices])
        xmax = np.max([v.x for v in annotation.bounding_poly.vertices])
        ymin = np.min([v.y for v in annotation.bounding_poly.vertices])
        ymax = np.max([v.y for v in annotation.bounding_poly.vertices])
        ymid = ymax - (ymax - ymin)/2
        # This represents the bounding box of the current item
        # It includes the additional information that is underneath the name
        # of the article
        # Initially this is just the bounding box for the first word
        # but it grows as new words are added
        bounding_box = {
          'xmin': xmin,
          'xmax': xmax,
          'ymin': ymin,
          'ymax': ymax
        }

        if (ymax + ymin)/2 < parsed_y:
          if self.debug:
            print('Skipping ' + annotation.description + ' ' + str(ymax) + ' ' + str(parsed_y))
          continue
        line_height = ymax - ymin
        current_price = None
        current_name = ''
        current_name += annotation.description
        # If the item has additional information e.g. how many of the item was bought
        # then this will have a value
        current_amount = None 
        # This represents how much each item costs, which is only present for some items
        current_st_price = None
        # This string holds the information about the quantity and the price for each item
        current_quantity_string = ''
        # TODO: What is this?
        y_current = 0
        price_x_current = 0
        is_hanging = False
        p_description = ''
        # This is for keeping track of the start of the next item
        # when we are looking for the quantity row
        # If the quantity row is underneath this, then we know it doesn't 
        # belong to the current article
        y_min_next_article = g_ymax

        for j, p_ann in enumerate(sorted_annotations):
          if i == j:
            continue
          skip_this = False
          for skipword in SKIPWORDS+BLACKLIST_WORDS+STOPWORDS:
            if skipword in p_ann.description.lower().split(' '):
              skip_this = True
          if skip_this:
            continue
          p_xmin = np.min([v.x for v in p_ann.bounding_poly.vertices])
          p_xmax = np.max([v.x for v in p_ann.bounding_poly.vertices])
          p_ymin = np.min([v.y for v in p_ann.bounding_poly.vertices])
          p_ymax = np.max([v.y for v in p_ann.bounding_poly.vertices])

          # This means that the first word is underneath the next word
          # Therefore we can skip this, since we never want to add a word
          # above the first       
          if p_ymax < ymin:
            continue

          p_type = self.check_annotation_type(p_ann.description)

          # Check if the next word is underneath the first
          # and if the quantity string is finished, then we can skip this part
          if p_ymin > ymid and \
             p_ymin < y_min_next_article and \
             not self.is_amount_line(current_quantity_string):
            # If this is the case, it could be a row that contains information
            # about the quantity bought
            # Check if the next word is offset on the x-axis
            if p_xmin-X_OFFSET > xmin:
              # Treat a row with pant as a new article
              if self.check_if_pant(p_ann.description):
                y_min_next_article = p_ymin
                continue
              # If the next word is not a number, we know that it is 
              # part of the additional information
              if p_type != 'number':
                current_quantity_string += ' ' + p_ann.description
                used_idx.append(j)
                # Extend the bounding box to contain the new word
                if p_xmax > bounding_box['xmax']:
                  bounding_box['xmax'] = p_xmax
                if p_ymax > bounding_box['ymax']:
                  bounding_box['ymax'] = p_ymax 
                continue               

              # If it is a number it becomes trickier, since it could
              # both be part of the additional information or it could
              # be the price of the article
              else:
                # Assume that it is the price of the article
                # if it is ends close to the edge of the receipt
                if g_xmax-PRICE_OFFSET < p_xmax:
                  used_pr.append(j)
                  current_price = self.check_price(p_ann.description) 
                # If the price is not on the far right, we assume that 
                # it is part of the quantity string
                else:
                  current_quantity_string += ' ' + p_ann.description
                  used_idx.append(j)
                continue
            else:
              # If we get here it means that the next word is aligned with
              # the current article, therefore it must be a new article
              # and we should stop expanding the bounding box on the y-axis
              y_min_next_article = p_ymin
              continue

          line_overlap = np.min([p_ymax-ymin, ymax-p_ymin]) / np.max([p_ymax-p_ymin, ymax-ymin])
          if line_overlap < 0.45:
            continue
          if is_hanging:
            p_description += p_ann.description
            is_hanging = False
          else:
            p_description = p_ann.description
  
          if p_type == 'hanging':
            is_hanging = True
            continue
  
          if p_type == 'number':
            # Keep track of the largest read number, which is the total amount
            parsed_number = float(p_description.replace(",", ".")) 
            if parsed_number > self.total_amount:
              self.total_amount = parsed_number
            # Checking if the number ends on the left side of the middle of the document
            if p_xmax < g_xmax / 2:
              continue
            if j in seen_prices:
              continue
            # Checking if the price text start before the middle of the page
            # the price should always be to the right of the middle of the page
            # If the number does not start on the right side, then it might be
            # the price per kg e.g. SEK/kg
            if p_xmin < g_xmax * 0.7:
              current_name += ' ' + p_description
              continue
            
            if p_ymax < ymin or p_ymin > ymax or p_xmax < xmax or p_xmin < price_x_current:
              if current_price or p_ymin > ymin + 2*line_height:
                continue
            if self.debug:
              print('Checking ' + p_description)
            y_current = p_ymin
            used_pr.append(j)
            current_price = self.check_price(p_description)
            price_x_current = p_xmin
            if self.debug:
              print('New price ' + str(current_price))
            parsed_y = max(parsed_y, (p_ymax + p_ymin) / 2)
  
          elif p_type == 'text':
            # Checking if left side of bounding box for next word is before the right side of the first word
            # in that case it means that the next word comes BEFORE the word that is already added, 
            # and should not be added
            if p_xmin < xmax:
              continue
            # Checking if the words are on different rows
            # if they are the second word should not be added
            if p_ymax < ymin or p_ymin > ymax:
              continue

            # if ( y_current > 0 and p_ymin > y_current):
            #   continue

            used_idx.append(j)
            parsed_y = max(parsed_y, (p_ymax + p_ymin) / 2)
            if self.debug:
              print('Appending ' + current_name + ' ' + p_description)
            current_name += ' ' + p_ann.description
            
        y_min_next_article = g_ymax
        if self.debug:
          print(current_name + ' ' + str(current_price))
        if current_price:
          seen_prices += used_pr
          seen_indexes += used_idx
          skip_this = False
          if self.debug:
            print(current_name.lower())

          # Check if the current item is a discount
          if self.check_discount(current_price):
            if self.debug:
              print('Adding discount: ' + current_name + ' ' + str(current_price))
            discounts.append({
              'name': current_name,
              'price': current_price
            })
            current_name = ''
            current_price = None
          
          if not self.check_article_name(current_name):
            skip_this = True
          if not skip_this:
            if self.debug:
              print('Adding ' + current_name + ' ' + str(current_price))
            
            # Check if the article has a correct quantity string
            if self.is_amount_line(current_quantity_string):
              current_amount = self.get_amount(current_quantity_string)
              current_st_price = self.get_st_price(current_quantity_string)

            articles.append({
              'name': current_name,
              'sum': current_price,
              'amount': current_amount if current_amount else '1 st',
              'price': current_st_price if current_st_price else current_price
            })

      elif t_type == 'date':
        dates.append(self.parse_date(annotation.description))

      elif t_type == 'market':
        if self.check_market(annotation.description):
          market = self.check_market(annotation.description)
    return articles, dates, market, discounts

  def check_annotation_type(self, text_body):
    # TODO: What is 'hanging'?
    if text_body[-1] == ',':
      return 'hanging'
    if self.check_price(text_body):
      return 'number'
    if self.parse_date(text_body):
      return 'date'
    if self.is_integer(text_body):
      return 'int'
    if self.check_market(text_body):
      return 'market'
    return 'text'

  def check_market(self, text_body):
    for market in MARKETS:
      if market.lower() in text_body.lower().split(' '):
        return market
    
    # Hemköp will probably not be handled correctly since 
    # they can't handle ÅÄÖ, therefore it needs to be handled separately
    re_hemkop = regex.compile(r'HEMK.P')
    for text in text_body.upper().split(' '):
      if regex.fullmatch(re_hemkop, text):
        return 'hemköp'

    return None

  # Function for checking if a string is an article on the receipt
  # The article name begins with an all-caps word (Coop and Hemköp)
  # The article name can also contain a number due to special characters, 
  # The article name on an ICA receipt starts with a capital letter and 
  # the rest are small letters
  # such as the clove on coop receipts
  def check_article_name(self, article_name):
    rex = regex.compile(r'[0-9\*]*[[:upper:]]+')
    words = article_name.split(' ')
    if(words[0] == "*"):
      return True
    if regex.fullmatch(rex, words[0]):
      return True

    # Coop and Hemköp receipts have all articles in only capital letters
    # so if the market is any of them we skip this regex match
    if self.market not in ['coop', 'hemköp']:
      re_ica = regex.compile(r'[[:upper:]][[:lower:]]*')
      if regex.fullmatch(re_ica, words[0]):
        return True

    return False
  
  # Function for detecting a price string
  # A price string has the format (X)XX,XX
  # Returns false if the string does not represent a price
  def check_price(self, string):
    rex = r'-?\d+,\d\d'
    if regex.fullmatch(rex, string):
      return string
    return False

  # Function for checking if the current item is a discount
  # Discounts have a negative price
  def check_discount(self, string):
    rex = r'-\d+,\d\d'
    if regex.fullmatch(rex, string):
      return True
    return False

  # Checking if the string is pant, which should be 
  # handled differently
  def check_if_pant(self, string):
    rex = r'pant'
    string = string.lower()
    if regex.search(rex, string):
      return True
    else:
      return False

  # Gets the amount of a product from a string
  # For the string "0,538 kg x 21,95 SEK/kg" it would return "0,538 kg"
  def get_amount(self, string):
    string = string.strip()
    re_kg = r'(\d+,\d+\s*kg)\s*[x|\*]\s*\d\d,\d\d\s*.*/kg'
    re_st = r'(\d+\s*st)\s*[x|\*]\s*\d\d,\d\d'
    
    kg_search = regex.search(re_kg, string)
    if kg_search:
      return kg_search.group(1)
    
    st_search = regex.search(re_st, string)
    if st_search:
      return st_search.group(1)

    else:
      return False

  # Gets the price for each of a product from a string
  # For the string "0,538 kg x 21,95 SEK/kg" it would return "21,95 SEK/kg"
  def get_st_price(self, string):
    string = string.strip()
    re_kg = r'\d+,\d+\s*kg\s*[x|\*]\s*(\d\d,\d\d\s*.*/kg)'
    re_st = r'\d+\s*st\s*[x|\*]\s*(\d\d,\d\d)'
    
    kg_search = regex.search(re_kg, string)
    if kg_search:
      return kg_search.group(1)
    
    st_search = regex.search(re_st, string)
    if st_search:
      return st_search.group(1)

    else:
      return False

  # Checks if the string is an amount of a product e.g. number of items bought
  # It could be on the form: X,XXX kr x XX,XX SEK/kg (where X is an int)
  # Or it could be on the form: X st x XX,XX
  def is_amount_line(self, string):
    string = string.strip()
    re_kg = r'\d+,\d+\s*kg\s*[x|\*]\s*\d\d,\d\d\s*.*/kg'
    re_st = r'\d+\s*st\s*[x|\*]\s*\d\d,\d\d'
    if regex.match(re_kg, string):
      return True
    elif regex.match(re_st, string):
      return True
    return False

  def is_integer(self, text_body):
    try:
      _ = int(text_body)
    except:
      return False
    if round(float(text_body)) == float(text_body):
      return True
    return False

  def parse_date(self, date_str):
    for fmt in ['%d.%m.%y', '%Y-%m-%d', '%d.%m.%y %H:%M', '%d.%m.%Y', '%y-%m-%d']:
      for substr in date_str.split(' '):
        try:
          new_purch_date = datetime.datetime.strptime(substr, fmt).strftime('%Y-%m-%d')
          return new_purch_date
        except Exception as e:
          pass
    return None
