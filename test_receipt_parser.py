import unittest

from receipt_parser import GcloudParser

parser = GcloudParser()

class TestParser(unittest.TestCase):
  
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

if __name__ == '__main__':
  unittest.main()

