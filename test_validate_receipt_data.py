import unittest

from validate_receipt_data import ReceiptDataValidator

validator = ReceiptDataValidator()

class TestReceiptDataValidator(unittest.TestCase):

  # def test_check_articles(self):

  # def test_check_nr_of_articles(self):

  # def test_count_articles(self):

  def test_get_nr_receipt_articles(self):
    totals = [
      {
        "name": "totals",
        "sum": "766,69",
        "amount": "32"
      }
    ]
    result = validator.get_nr_receipt_articles(totals)
    correct = 32
    self.assertEqual(result, correct, "Should return the correct nr of articles")

    totals = [
      {
        "name": "totals",
        "sum": "766,69",
      }
    ]
    result = validator.get_nr_receipt_articles(totals)
    correct = None
    self.assertEqual(result, correct, "Should return None if the total does not have an amount")

    totals = [
      {
        "name": "totals",
        "sum": "766,69",
      },
      {
        "name": "totals",
        "sum": "766,69",
        "amount": "32"
      }
    ]
    result = validator.get_nr_receipt_articles(totals)
    correct = 32
    self.assertEqual(result, correct, "Should return correct amount, even if one of the entries does not have any amount")

if __name__ == '__main__':
  unittest.main()
