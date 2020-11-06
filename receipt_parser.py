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

class GcloudParser:
  def __init__(self, debug=False, min_length=5, max_height=1):
    self.debug = debug
    self.min_length = min_length
    self.max_height = max_height
    self.client = vision_v1.ImageAnnotatorClient()
    self.allowed_labels = ['article', 'price', 'market', 'address', 'date', 'misc']
    self.total_amount = 0

  def parse_pdf(self, path):
    pages = convert_from_path(path, 500)
    articles = []
    dates = []
    markets = []
    discounts = []
    for page in pages:
      page.save('tmp.jpg')
      gcloud_response = self.detect_text('tmp.jpg')
      os.system('del tmp.jpg')
      _art, _dat, _mar, _dis = self.parse_response(gcloud_response)
      articles += _art
      dates += _dat
      markets += _mar
      discounts += _dis
    return articles, dates, markets, discounts, self.total_amount

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
    markets = []
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

        if (ymax + ymin)/2 < parsed_y:
          if self.debug:
            print('Skipping ' + annotation.description + ' ' + str(ymax) + ' ' + str(parsed_y))
          continue
        line_height = ymax - ymin
        # look for a price that is in the same line on the far right
        current_price = None
        current_name += annotation.description
        y_current = 0
        price_x_current = 0
        is_hanging = False
        p_description = ''

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

          if p_ymax < ymin or p_ymin > ymax:
            continue
          line_overlap = np.min([p_ymax-ymin, ymax-p_ymin]) / np.max([p_ymax-p_ymin, ymax-ymin])
          if line_overlap < 0.45:
            continue
          if is_hanging:
            p_description += p_ann.description
            is_hanging = False
          else:
            p_description = p_ann.description
          p_type = self.check_annotation_type(p_description)
  
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
            if p_xmin < g_xmax * 0.7:
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
            if p_ymax < ymin or p_ymin > ymax or ( y_current > 0 and p_ymin > y_current):
              continue
            used_idx.append(j)
            parsed_y = max(parsed_y, (p_ymax + p_ymin) / 2)
            if self.debug:
              print('Appending ' + current_name + ' ' + p_description)
            current_name += ' ' + p_ann.description
            
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
            articles.append({
              'name': current_name,
              'price': current_price
            })
            current_name = ''
            current_price = None
          else:
            current_name = ''
            current_price = None
        else:
          # If there is no current price at this stage, we assume that the read line was not an article
          current_name = ''
          current_price = None

      elif t_type == 'date':
        dates.append(self.parse_date(annotation.description))

      elif t_type == 'market':
        if self.check_market(annotation.description):
          markets.append(self.check_market(annotation.description))
    return articles, dates, markets, discounts

  def check_annotation_type(self, text_body):
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
    return None

  # Function for checking if a string is an article on the receipt
  # The article name begins with an all-caps word
  # The article name can also contain a number due to special characters, 
  # such as the clove on coop receipts
  def check_article_name(self, article_name):
    rex = regex.compile(r'[0-9]?[[:upper:]]+')
    words = article_name.split(' ')
    if regex.fullmatch(rex, words[0]):
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

  def is_integer(self, text_body):
    try:
      _ = int(text_body)
    except:
      return False
    if round(float(text_body)) == float(text_body):
      return True
    return False

  def parse_date(self, date_str):
    for fmt in ['%d.%m.%y', '%Y-%m-%d', '%d.%m.%y %H:%M', '%d.%m.%Y']:
      for substr in date_str.split(' '):
        try:
          new_purch_date = datetime.datetime.strptime(substr, fmt).strftime('%Y-%m-%d')
          return new_purch_date
        except Exception as e:
          pass
    return None
