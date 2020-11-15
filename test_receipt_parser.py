import unittest

from receipt_parser import GcloudParser

parser = GcloudParser()

class TestParser(unittest.TestCase):
  
  def test_check_annotation_type(self):
    text_body = "34,55"
    result = parser.check_annotation_type(text_body)
    self.assertEqual(result, 'number', "Should return number if input is correct price")

    text_body = "20-05-12"
    result = parser.check_annotation_type(text_body)
    self.assertEqual(result, 'date', "Should return date if input is correct date")

    text_body = "23"
    result = parser.check_annotation_type(text_body)
    self.assertEqual(result, 'int', "Should return int if input is correct int")

    text_body = "coop"
    result = parser.check_annotation_type(text_body)
    self.assertEqual(result, 'market', "Should return market if input is correct market")

    text_body = "Totalt"
    result = parser.check_annotation_type(text_body)
    self.assertEqual(result, 'total', "Should return total if input is a total word")

    text_body = "blablabla"
    result = parser.check_annotation_type(text_body)
    self.assertEqual(result, 'text', "Should return text for all other inputs")

  def test_check_article_name(self):
    article_name = "QWEÄÖPLÄÖÜÊÉ"
    is_article = parser.check_article_name(article_name)
    self.assertTrue(is_article, "Should be able to handle special characters")

    article_name = "TEST TeST"
    is_article = parser.check_article_name(article_name)
    self.assertTrue(is_article, "Should be article if multiple words (only first word needs to have all caps)")

    article_name = "test TEST"
    is_article = parser.check_article_name(article_name)
    self.assertFalse(is_article, "Should not be article if first word is not all caps")

    article_name = "Blomkål blabla"
    is_article = parser.check_article_name(article_name)
    self.assertTrue(is_article, "Should return true for names where first letter is capital")

    article_name = "* PAPPKASSE BRUN 30L"
    is_article = parser.check_article_name(article_name)
    self.assertTrue(is_article, "Should return true for names that begins with *")

    article_name = 'NOTF@RS 12%'
    is_article = parser.check_article_name(article_name)
    self.assertTrue(is_article, "Should return true for names that contain non-alphabetic characters")

    article_name = '*Celsius Citr/Lime'
    is_article = parser.check_article_name(article_name)
    self.assertTrue(is_article, "Should return true for names that start with * then 1 capital letter and the rest lower case")

    article_name = 'Brejk'
    parser.market = "hemköp"
    is_article = parser.check_article_name(article_name)
    self.assertFalse(is_article, "Should return false for names where only first letter is capital when market is coop or hemköp")

    article_name = "Blomkål blabla"
    parser.market = "coop"
    is_article = parser.check_article_name(article_name)
    self.assertFalse(is_article, "Should return false for names where only first letter is capital when market is coop or hemköp")

  def test_check_if_total(self):
    text = "Totalt"
    result = parser.check_if_total(text)
    self.assertTrue(result, "Should return true if correct total input")

    text = "blabla"
    result = parser.check_if_total(text)
    self.assertFalse(result, "Should return false if incorrect input")

  def test_check_market(self):
    market = "ICA"
    result = parser.check_market(market)
    self.assertEqual(result, "ica", "Should work with capital letters")

    market = "Coop"
    result = parser.check_market(market)
    self.assertEqual(result, "coop", "Should work with first letter capital")

    market = "Hemköp"
    result = parser.check_market(market)
    self.assertEqual(result, "hemköp", "Should work for hemköp")

    market = "Hemk@p"
    result = parser.check_market(market)
    self.assertEqual(result, "hemköp", "Should work for hemköp, even if Ö is incorrect")

    market = "blablabla"
    result = parser.check_market(market)
    self.assertEqual(result, None, "Should return none if input is not a market recognized by the algorithm")

  def test_check_price(self):
    price = "34,99"
    result = parser.check_price(price)
    self.assertEqual(price, result, "Should return the price if the format is correct")

    price = "34.99"
    result = parser.check_price(price)
    self.assertEqual(price, result, "Should work with dots")

    price = "-34,99"
    result = parser.check_price(price)
    self.assertEqual(price, result, "Should be able to handle negative prices")

    price = "blabla"
    result = parser.check_price(price)
    self.assertFalse(result, "Should be false if input is not a price")
  
  def test_convert_price(self):
    price = "34.99"
    correct = "34,99"
    result = parser.convert_price(price)
    self.assertEqual(correct, result, "Should change dot to comma")

    price = "34,99"
    result = parser.convert_price(price)
    self.assertEqual(price, result, "Should keep price with comma the same")


  def test_check_discount(self):
    discount = "-5,89"
    is_discount = parser.check_discount(discount)
    self.assertTrue(is_discount, "Should be discount if negative number")

    discount = "5,89"
    is_discount = parser.check_discount(discount)
    self.assertFalse(is_discount, "Should not be discount if positive number")

    discount = "-54,89"
    is_discount = parser.check_discount(discount)
    self.assertTrue(is_discount, "Should be discount if double digit negative number")

    discount = "blabla"
    is_discount = parser.check_discount(discount)
    self.assertFalse(is_discount, "Should not be discount if arbitrary string")

  def test_check_if_pant(self):
    string = "gfdspokPANT eqåpwoeads"
    is_pant = parser.check_if_pant(string)
    self.assertTrue(is_pant, "Should return true when input includes 'pant'")
    
    string = "gfdspokPNT eqåpwoeads"
    is_pant = parser.check_if_pant(string)
    self.assertFalse(is_pant, "Should return false when input doesnt include 'pant'")

  def test_is_amount_line(self):
    string = "2 st x 12,95"
    is_amount_line = parser.is_amount_line(string)
    self.assertTrue(is_amount_line, "Should return true when correct input (Coop st pris)")

    string = "2stx12,95"
    is_amount_line = parser.is_amount_line(string)
    self.assertTrue(is_amount_line, "Should return true when correct input (Hemköp st pris)")

    string = "2st*12,95"
    is_amount_line = parser.is_amount_line(string)
    self.assertTrue(is_amount_line, "Should return true when correct input (Hemköp st pris)")

    string = "1,004 kg x 74,95 SEK/kg"
    is_amount_line = parser.is_amount_line(string)
    self.assertTrue(is_amount_line, "Should return true when correct input (Coop kg pris)")

    string = "1,131kg*79,00kr/kg"
    is_amount_line = parser.is_amount_line(string)
    self.assertTrue(is_amount_line, "Should return true when correct input (Hemköp kg pris)")

    string = " 1,131kg*79,00kr/kg "
    is_amount_line = parser.is_amount_line(string)
    self.assertTrue(is_amount_line, "Should be able to handle leading and trailing spaces")

    string = "blablalba"
    is_amount_line = parser.is_amount_line(string)
    self.assertFalse(is_amount_line, "Should return false when incorrect input")

    string = "BLANDFARS 1,131kg*79,00kr/kg"
    is_amount_line = parser.is_amount_line(string)
    self.assertTrue(is_amount_line, "Should return true when the quantity string happens to be on the same line as the article")

  def test_extract_amount_line(self):
    string = "BLANDFARS 1,131kg*79,00kr/kg"
    amount_line = "1,131kg*79,00kr/kg"
    result = parser.extract_amount_line(string)
    self.assertEqual(result, amount_line, "Should return the correct amount line")

    string = "BLANDFARS 1,004 kg x 74,95 SEK/kg"
    amount_line = "1,004 kg x 74,95 SEK/kg"
    result = parser.extract_amount_line(string)
    self.assertEqual(result, amount_line, "Should return the correct amount line")

    string = "blablalba"
    result = parser.extract_amount_line(string)
    self.assertEqual(result, None, "Should return None if string does not contain a correct amount line")

  def test_get_amount(self):
    string = "2 st x 12,95"
    amount = parser.get_amount(string)
    self.assertEqual(amount, "2 st")

    string = "2stx12,95"
    amount = parser.get_amount(string)
    self.assertEqual(amount, "2st")

    string = "2st*12,95"
    amount = parser.get_amount(string)
    self.assertEqual(amount, "2st")

    string = "1,004 kg x 74,95 SEK/kg"
    amount = parser.get_amount(string)
    self.assertEqual(amount, "1,004 kg")

    string = "1,131kg*79,00kr/kg"
    amount = parser.get_amount(string)
    self.assertEqual(amount, "1,131kg")

    string = " 1,131kg*79,00kr/kg "
    amount = parser.get_amount(string)
    self.assertEqual(amount, "1,131kg", "Should be able to handle leading and trailing spaces")

    string = "blablalba"
    amount = parser.get_amount(string)
    self.assertFalse(amount, "Should return false if an invalid quantity string")

  def test_get_st_price(self):
    string = "2 st x 12,95"
    amount = parser.get_st_price(string)
    self.assertEqual(amount, "12,95")

    string = "2stx12,95"
    amount = parser.get_st_price(string)
    self.assertEqual(amount, "12,95")

    string = "2st*12,95"
    amount = parser.get_st_price(string)
    self.assertEqual(amount, "12,95")

    string = "1,004 kg x 74,95 SEK/kg"
    amount = parser.get_st_price(string)
    self.assertEqual(amount, "74,95 SEK/kg")

    string = "1,131kg*79,00kr/kg"
    amount = parser.get_st_price(string)
    self.assertEqual(amount, "79,00kr/kg")

    string = " 1,131kg*79,00kr/kg "
    amount = parser.get_st_price(string)
    self.assertEqual(amount, "79,00kr/kg", "Should be able to handle leading and trailing spaces")

    string = "blablalba"
    amount = parser.get_st_price(string)
    self.assertFalse(amount, "Should return false if an invalid quantity string")


if __name__ == '__main__':
  unittest.main()

