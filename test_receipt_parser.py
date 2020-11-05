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


if __name__ == '__main__':
  unittest.main()

