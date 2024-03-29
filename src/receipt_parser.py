# pylint: disable=no-member
import io
import datetime
import numpy as np
import regex
import utils

from google.cloud import vision_v1
from pdf2image import convert_from_path
from constants import ( MARKETS, SKIPWORDS, TOTAL_WORDS, 
                       DISCOUNT_WORDS, X_OFFSET, PRICE_OFFSET, 
                       ARTICLE_OFFSET )

class GcloudParser:
  def __init__(self, debug=False, min_length=5, max_height=1):
    self.debug = debug
    self.min_length = min_length
    self.max_height = max_height
    self.client = vision_v1.ImageAnnotatorClient()
    self.totals = []
    self.market = None
    self.largets_number = 0
    self.bounding_box = None

  def parse_pdf(self, path):
    self.totals = []
    self.market = None
    self.bounding_box = None
    pages = convert_from_path(path, 500)
    articles = []
    dates = []
    discounts = []
    for page in pages:
      page.save('tmp.jpg')
      gcloud_response = self.detect_text('tmp.jpg')
      _art, _dat, _mar, _dis = self.parse_response(gcloud_response)
      if not _art:
        continue
      articles += _art
      dates += _dat
      discounts += _dis
      
    return {
      "articles": articles,
      "dates": dates,
      "market": self.market,
      "discounts": discounts,
      "totals": self.totals,
      "bounding_box": self.bounding_box
    }
    # return articles, dates, self.market, discounts, self.totals, self.bounding_box

  # Detects text in the file.
  def detect_text(self, path):
    with io.open(path, 'rb') as image_file:
      content = image_file.read()
    image = vision_v1.types.Image(content=content)
    response = self.client.text_detection(
      image=image,
      image_context={"language_hints": ["sv", "en"]}
    )
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
    if len(gcloud_response.text_annotations) == 0:
      return None, None, None, None
    base_ann = gcloud_response.text_annotations[0]
    g_xmin, g_xmax, g_ymin, g_ymax = utils.get_bb_corners(base_ann.bounding_poly.vertices)    
    if self.bounding_box == None:
      self.bounding_box = {
        'xmin': g_xmin.item(),  # Converts from numpy type to regular
        'xmax': g_xmax.item(),
        'ymin': g_ymin.item(),
        'ymax': g_ymax.item()
      }
    sorted_annotations = gcloud_response.text_annotations[1:]
    current_name = ''    
    # This is used for tracking where the discount items start (e.g. on Coop receipts)
    discounts_start = None
    
    for i, annotation in enumerate(sorted_annotations):

      skip_this = self.check_if_skip_word(annotation.description)
      if skip_this:
        continue

      if i in seen_indexes:
        continue

      t_type = self.check_annotation_type(annotation.description)

      if self.debug:
        print(annotation.description + ' ' + t_type)       

      if t_type == 'total':
        used_idx = []
        used_pr = []
        xmin, xmax, ymin, ymax = utils.get_bb_corners(annotation.bounding_poly.vertices)
        ymid = ymax - (ymax - ymin)/2
        line_height = ymax - ymin
        total_price = None
        nr_of_articles = None

        for j, p_ann in enumerate(sorted_annotations):
          if i == j:
            continue

          skip_this = self.check_if_skip_word(p_ann.description)
          if skip_this:
            continue

          if j in seen_prices or j in seen_indexes:
            continue

          p_xmin, p_xmax, p_ymin, p_ymax = utils.get_bb_corners(p_ann.bounding_poly.vertices)
          # This means that the first word is underneath the next word
          # Therefore we can skip this, since we never want to add a word
          # above the first       
          if p_ymax < ymin:
            continue

          # If the current word is too far underneath the first, we skip it
          if p_ymin-2*line_height > ymax:
            continue

          p_type = self.check_annotation_type(p_ann.description)

          # If next word is an int, it means that it is the number of articles
          # on the receipt
          if p_type == 'int' and nr_of_articles == None:
            nr_of_articles = p_ann.description
            used_idx.append(j)
          
          # If the next word is a number, it is the total amount paid
          if p_type == 'number' and total_price == None:
            total_price = p_ann.description  
            used_pr.append(j)

          if p_type == 'text':
            used_idx.append(j)

          # If both nr of articles and total price are found, we save this obj
          if nr_of_articles != None and total_price != None:
            self.totals.append({
              'name': 'totals',
              'sum': total_price,
              'amount': nr_of_articles
            })
            total_price = None
            nr_of_articles = None
            break
              
        # Sometimes the totals line does not have the number of articles
        # In this case it should be added anyways
        if total_price != None:
          self.totals.append({
            'name': 'totals',
            'sum': total_price
          })

        seen_indexes += used_idx
        seen_prices += used_pr

      if t_type == 'text':
        used_idx = []
        used_pr = []
        xmin, xmax, ymin, ymax = utils.get_bb_corners(annotation.bounding_poly.vertices)
        ymid = ymax - (ymax - ymin)/2

        if not discounts_start and \
           annotation.description.lower() in DISCOUNT_WORDS:
          discounts_start = ymin

        # This represents the bounding box of the current item
        # It includes the additional information that is underneath the name
        # of the article
        # Initially this is just the bounding box for the first word
        # but it grows as new words are added
        bounding_box = {
          'xmin': xmin.item(),
          'xmax': xmax.item(),
          'ymin': ymin.item(),
          'ymax': ymax.item()
        }

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
        # This is for storing the price of a discount if there is a discount line 
        # beneath the article line
        current_discount_price = None
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
          skip_this = self.check_if_skip_word(p_ann.description)
          if skip_this:
            continue

          p_xmin, p_xmax, p_ymin, p_ymax = utils.get_bb_corners(p_ann.bounding_poly.vertices)
          # This means that the first word is underneath the next word
          # Therefore we can skip this, since we never want to add a word
          # above the first       
          if p_ymax < ymin:
            continue

          p_type = self.check_annotation_type(p_ann.description)

          # Check if the next word is underneath the first
          # and if the quantity string is finished, then we can skip this part
          # line_height/2 is added to the condition because sometimes p_ymin 
          # can be smaller for the next word on the line
          # We also don't want to add any more text if the first word is below
          # the discount header (only existing for Coop receipts), because discounts
          # doesn't span multiple lines
          if p_ymin > ymid and \
             p_ymin+line_height/2 < y_min_next_article and \
             not self.check_if_below_discount(p_ymin, discounts_start) and \
             (not self.is_amount_line(current_quantity_string) or \
              current_price == None):
            # If this is the case, it could be a row that contains information
            # about the quantity bought
            # Check if the next word is offset on the x-axis
            if p_xmin-X_OFFSET > xmin:
              # Treat a row with pant as a new article
              # Also treat a row containing the total as the next article
              if self.check_if_pant(p_ann.description) or \
                 p_type == 'total':
                y_min_next_article = p_ymin
                continue
              
              # If the next word is not a number, we know that it is 
              # part of the additional information
              # TODO: This may cause a bug in the case where the quantity string 
              # TODO: is the quantity string of the next item IF the quantity string
              # TODO: would be read before the actual name of the item and before
              # TODO: the price of the next item
              if p_type != 'number':
                current_quantity_string += ' ' + p_ann.description
                used_idx.append(j)
                # Extend the bounding box to contain the new word
                if p_xmax > bounding_box['xmax']:
                  bounding_box['xmax'] = p_xmax.item()
                if p_ymax > bounding_box['ymax']:
                  bounding_box['ymax'] = p_ymax.item()
                continue               

              # If it is a number it becomes trickier, since it could
              # both be part of the additional information or it could
              # be the price of the article
              else:
                # This could either be a price or a discount
                # if it is ends close to the edge of the receipt
                # Do not update price if the article already has a price
                # Here the assumption is made that the prices will always come
                # in correct order
                if g_xmax-PRICE_OFFSET < p_xmax:
                  # First check if this is a discount price
                  # If the current price of the article is a discount price
                  # this should not be added to the discount price, since a
                  # discount can not have another discount
                  if current_discount_price == None and \
                     self.check_discount(p_ann.description) and \
                     not self.check_discount(current_price):
                     used_pr.append(j)
                     current_discount_price = p_ann.description
                  if current_price == None:
                    used_pr.append(j)
                    current_price = utils.check_price(p_ann.description) 
                  else:
                    # This means that we have already found a price for this article
                    # and the read item is a price, therefore this must be the price
                    # for the next article (assuming that the prices comes in order)
                    if not self.check_discount(p_ann.description):
                      y_min_next_article = p_ymin
                    continue
                # If the price is not on the far right, we assume that 
                # it is part of the quantity string
                else:
                  current_quantity_string += ' ' + p_ann.description
                  used_idx.append(j)
                continue
            else:
              # If we get here it means that the next word is aligned with
              # the current article, therefore it could be a new article
              # and we should stop expanding the bounding box on the y-axis
              if self.check_article_name(p_ann.description) or \
                 p_type == 'total':
                y_min_next_article = p_ymin
              # It could also be a discount 
              if p_ann.description.lower() in DISCOUNT_WORDS and \
                 not discounts_start:
                discounts_start = p_ymin
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
            # Remove minus sign if it is multiple
            p_description = utils.remove_double_minus_sign(p_description)
            # Keep track of the largest read number, which is the total amount
            parsed_number = float(p_description.replace(",", ".")) 
            if parsed_number > self.largets_number:
              self.largets_number = parsed_number
            if j in seen_prices:
              continue
            # Checking if the price text start before the middle of the page
            # the price should always be to the right of the middle of the page
            # If the number does not start on the right side, then it might be
            # the price per kg e.g. SEK/kg
            if p_xmin < g_xmax * 0.7:
              current_name += ' ' + p_description
              continue
            
            if self.debug:
              print('Checking ' + p_description)
            used_pr.append(j)
            current_price = self.convert_price(p_description)
            if self.debug:
              print('New price ' + str(current_price))
  
          elif p_type == 'text' or \
               p_type == 'int':
            # Checking if left side of bounding box for next word is before the right side of the first word
            # in that case it means that the next word comes BEFORE the word that is already added, 
            # and should not be added
            if p_xmax < xmax:
              continue
            # Checking if the words are on different rows
            # if they are the second word should not be added
            if p_ymax < ymin or p_ymin > ymax:
              continue

            used_idx.append(j)
            if self.debug:
              print('Appending ' + current_name + ' ' + p_description)
            current_name += ' ' + p_ann.description
            
        y_min_next_article = g_ymax
        if self.debug:
          print(current_name + ' ' + str(current_price))
        if current_price:
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
            seen_prices += used_pr
            seen_indexes += used_idx
            continue

          if not self.check_article_name(current_name):
            skip_this = True
                      
          # Verify that the bounding box of the article is close to 
          # the left edge of the receipt
          # The exeption here is pant, which are a bit shifted to the right
          # TODO: This causes a problem with the products at Coop which has a 
          # cloves in front of them. How to handle this?
          if bounding_box['xmin']-ARTICLE_OFFSET > g_xmin and \
             not self.check_if_pant(current_name):
            skip_this = True
         
          if self.check_discount_name(current_name):
            skip_this = True

          if not skip_this:
            if self.debug:
              print('Adding ' + current_name + ' ' + str(current_price))

            # Check if the current discount price has a value
            # then this item has an discount associated with it
            if current_discount_price != None:
              discounts.append({
                'name': current_quantity_string,
                'price': current_discount_price
              })

            # Sometimes the quantity string is on the same line as the article
            # In this case we need to move it from the article string to the 
            # quantity string
            if self.is_amount_line(current_name):
              current_quantity_string = self.extract_amount_line(current_name)
              current_name = current_name.replace(current_quantity_string, '')  

            # Check if the article has a correct quantity string
            if self.is_amount_line(current_quantity_string):
              current_amount = self.get_amount(current_quantity_string)
              current_st_price = self.get_st_price(current_quantity_string)

            # This is done because some items may appear to be one item
            # but are actually multiple items
            if self.is_group_price(current_name):
              amount, st_price = self.extract_group_price(current_name)
              if not current_amount:
                new_amount = amount
              else:
                new_amount = utils.get_number_from_string(current_amount)*amount
              current_amount = str(int(new_amount)) + ' st'
              current_st_price = utils.convert_to_price_string(st_price)

            articles.append({
              'name': current_name.strip(),
              'sum': current_price,
              'amount': current_amount if current_amount else '1 st',
              'price': current_st_price if current_st_price else current_price,
              'bounding_box': bounding_box
            })
            seen_prices += used_pr
            seen_indexes += used_idx

      if t_type == 'date':
        dates.append(self.parse_date(annotation.description))

      if t_type == 'market':
        if self.check_market(annotation.description):
          self.market = self.check_market(annotation.description)

      if self.check_if_part_of_date(annotation.description):
        # This could be a date if the parts of the date were parsed seperately
        used_idx = []
        used_pr = []
        xmin, xmax, ymin, ymax = utils.get_bb_corners(annotation.bounding_poly.vertices)
        ymid = ymax - (ymax - ymin)/2
        line_height = ymax - ymin
        total_price = None
        nr_of_articles = None
        current_name = ''
        current_name += annotation.description
        used_idx.append(i)

        for j, p_ann in enumerate(sorted_annotations):
          if i == j:
            continue

          skip_this = self.check_if_skip_word(p_ann.description)
          if skip_this:
            continue

          if j in seen_prices or j in seen_indexes:
            continue

          p_xmin, p_xmax, p_ymin, p_ymax = utils.get_bb_corners(p_ann.bounding_poly.vertices)
          # This means that the first word is underneath the next word
          # Therefore we can skip this, since we never want to add a word
          # above the first       
          if p_ymax < ymin:
            continue

          # This means the the first word is above the next word
          if p_ymin > ymax:
            continue
          
          used_idx.append(j)
          current_name += p_ann.description
          
          # Check if the current name is a date, and add it to dates array
          if self.check_annotation_type(current_name) == 'date':
            seen_indexes += used_idx
            dates.append(self.parse_date(current_name))
            break

    return articles, dates, self.market, discounts

  def check_annotation_type(self, text_body):
    # TODO: What is 'hanging'?
    if text_body[-1] == ',':
      return 'hanging'
    if utils.check_price(text_body):
      return 'number'
    if self.parse_date(text_body):
      return 'date'
    if utils.is_integer(text_body):
      return 'int'
    if self.check_market(text_body):
      return 'market'
    if self.check_if_total(text_body):
      return 'total'
    return 'text'

  # Checking if a word is the start of the totals row
  def check_if_total(self, text_body):
    for total in TOTAL_WORDS:
      if total.lower() == text_body.lower():
        return True
    return False

  def check_if_part_of_date(self, text_body):
    rex = r'^(\d{4}|\d{2})(-|-\d{2})?(-|-\d{2})?$'
    if regex.search(rex, text_body):
      return True
    return False

  def check_market(self, text_body):
    for market in MARKETS:
      if market.lower() in text_body.lower().split(' '):
        return market
    
    # Hemköp will probably not be handled correctly since 
    # they can't handle ÅÄÖ, therefore it needs to be handled separately
    re_hemkop = regex.compile(r'HEMK.P')
    for text in text_body.upper().split(' '):
      if regex.search(re_hemkop, text):
        return 'hemköp'

    return None

  # Function for checking if a string is an article on the receipt
  # The article name begins with an all-caps word (Coop and Hemköp)
  # The article name can also contain a number due to special characters, 
  # such as the clove on coop receipts
  # The article name on an ICA receipt starts with a capital letter and 
  # the rest are small letters
  # Due to Hemköps inability to handle ÅÄÖ, random characters will appear
  # in the article names. Because of this the regex will need to match non-alpha chars
  def check_article_name(self, article_name):
    if self.check_total_name(article_name):
      return False

    # A word that only consists of numbers and a dash,
    # should not be considered an article name
    rex = r'\d+-\d*'
    if regex.fullmatch(rex, article_name):
      return False  

    words = article_name.split(' ')
    if words[0] == "*":
      return True
    if words[0] == words[0].upper():
      return True

    # Coop and Hemköp receipts have all articles in only capital letters
    # so if the market is any of them we skip this regex match
    if self.market not in ['coop', 'hemköp']:
      re_ica = regex.compile(r'\*?[[:upper:]][[:lower:]]*')
      if regex.fullmatch(re_ica, words[0]):
        return True

    return False

  # Checks if the string is a line with the total sum 
  def check_total_name(self, string):
    total_names = ['ATT BETALA', 'BETALA', 'Totalt', 'Total']
    for total_name in total_names:
      if total_name in string:
        return True
    return False

  # This is used to prevent the "summar of discounts" line to be
  # considered an article
  def check_discount_name(self, string):
    for discount_name in DISCOUNT_WORDS:
      if discount_name.lower() in string.lower():
        return True
    return False
  
  def check_if_below_discount(self, ymin, discounts_start):
    if not discounts_start:
      return False
    if ymin > discounts_start:
      return True
    return False

  def convert_price(self, string):
    return string.replace('.', ',')

  # Function for checking if the current item is a discount
  # Discounts have a negative price
  def check_discount(self, string):
    if type(string) != str:
      return False
    rex = r'-+\d+,\d\d'
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

  def check_if_skip_word(self, string):
    for skipword in SKIPWORDS:
      if skipword.lower() in string.lower().split(' '):
        if(self.debug):
          print("Skipping: " + str(string))
        return True
    return False

  # Gets the amount of a product from a string
  # For the string "0,538 kg x 21,95 SEK/kg" it would return "0,538 kg"
  def get_amount(self, string):
    string = string.strip()
    re_kg = r'(\d+[,|\.]\d+\s*kg)\s*[x|\*|\s]\s*\d+[,|\.]\d\d\s*.*/kg'
    re_st = r'(\d+\s*(st)?)\s*[x|\*|\s]\s*\d+[,|\.]\d\d'
    
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
    re_kg = r'\d+[,|\.]\d+\s*kg\s*[x|\*|\s]\s*(\d+[,|\.]\d\d\s*.*/kg)'
    re_st = r'\d+\s*(st)?\s*[x|\*|\s]\s*(\d+[,|\.]\d\d)'
    
    kg_search = regex.search(re_kg, string)
    if kg_search:
      return kg_search.group(1)
    
    st_search = regex.search(re_st, string)
    if st_search:
      return st_search.group(2)

    else:
      return False

  # Checks if the string is an amount of a product e.g. number of items bought
  # It could be on the form: X,XXX kr x XX,XX SEK/kg (where X is an int)
  # Or it could be on the form: X st x XX,XX
  # Or the form X * XX,XX
  # City gross has the form X.XXX kg XX.XX kr/kg
  def is_amount_line(self, string):
    string = string.strip()
    re_kg = r'\d+[,|\.]\d+\s*kg\s*[x|\*|\s]\s*\d\d*[,|\.]\d\d\s*.*/kg'
    re_st = r'\d+\s*(st)?\s*[x|\*|\s]\s*\d\d*[,|\.]\d\d'
    if regex.search(re_kg, string):
      return True
    elif regex.search(re_st, string):
      return True
    return False

  # Gets the amount line from a string if it has any
  def extract_amount_line(self, string):
    string = string.strip()
    re_kg = r'(\d+[,|\.]\d+\s*kg\s*[x|\*|\s]\s*\d+[,|\.]\d\d\s*.*/kg)'
    result = regex.search(re_kg, string)
    if result:
      return result.group(1)

    re_st = r'(\d+\s*(st)?\s*[x|\*|\.]\s*\d+[,|\.]\d\d)'
    result = regex.search(re_st, string)
    if result:
      return result.group(1)
    
    return None

  # Checking if the name of the article contains a group discount string
  # For example on Hemköp receipts it would be 
  def is_group_price(self, string):
    string = string.strip()
    rex = r'\dF\d\d?\d?'
    if regex.search(rex, string):
      return True
    return False

  # Extracts the price for each individual item for an article that has a
  # group price
  # For example the line "MOZZARELLA 2F20 V3 2*20,00 40,00" inplies that
  # each item on this row is 2 pakets of mozzarella
  def extract_group_price(self, string):
    string = string.strip()
    rex = r'(\d)F(\d\d?\d?)'
    match = regex.search(rex, string)
    if not match:
      return None, None
    amount = int(match.group(1))
    price = int(match.group(2))
    st_price = price/amount
    return amount, st_price

  def parse_date(self, date_str):
    for fmt in ['%d.%m.%y', '%Y-%m-%d', '%d.%m.%y %H:%M', '%d.%m.%Y', '%y-%m-%d']:
      for substr in date_str.split(' '):
        try:
          new_purch_date = datetime.datetime.strptime(substr, fmt).strftime('%Y-%m-%d')
          return new_purch_date
        except Exception:
          pass
    return None
