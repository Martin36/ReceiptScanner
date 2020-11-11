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

    text_body = "blablabla"
    result = parser.check_annotation_type(text_body)
    self.assertEqual(result, 'text', "Should return text for all other inputs")

  def test_check_article_name(self):
    article_name = "QWEÄÖPLÄÖÜÊÉ"
    is_article = parser.check_article_name(article_name)
    self.assertEqual(is_article, True, "Should be able to handle special characters")

    article_name = "TEST TeST"
    is_article = parser.check_article_name(article_name)
    self.assertEqual(is_article, True, "Should be article if multiple words (only first word needs to have all caps)")

    article_name = "test TEST"
    is_article = parser.check_article_name(article_name)
    self.assertEqual(is_article, False, "Should not be article if first word is not all caps")

  def test_check_market(self):
    market = "ICA"
    is_market = parser.check_market(market)
    self.assertTrue(is_market, "Should work with capital letters")

    market = "Coop"
    is_market = parser.check_market(market)
    self.assertTrue(is_market, "Should work with mixed letters")
  
  def test_check_price(self):
    price = "34,99"
    result = parser.check_price(price)
    self.assertEqual(price, result, "Should return the price if the format is correct")

    price = "-34,99"
    result = parser.check_price(price)
    self.assertEqual(price, result, "Should be able to handle negative prices")

    price = "blabla"
    result = parser.check_price(price)
    self.assertFalse(result, "Should be false if input is not a price")
  
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

