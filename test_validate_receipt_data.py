import unittest

from validate_receipt_data import ReceiptDataValidator

validator = ReceiptDataValidator()

class TestReceiptDataValidator(unittest.TestCase):

  def test_check_articles(self):

  def test_check_nr_of_articles(self):

  def test_convert_to_nr(self):

  def test_get_number_from_string(self):
    string = "39,90Kr/kg"
    result = validator.get_number_from_string(string)
    correct = 39.90
    self.assertEqual(result, correct, "Should return parsed float if number contains comma")

    string = "*Cel Flamingo35.5c1"
    result = validator.get_number_from_string(string)
    correct = 35.5
    self.assertEqual(result, correct, "Should return parsed float if number contains dot")

    string = "*Cel Flamingo 35c1"
    result = validator.get_number_from_string(string)
    correct = 35
    self.assertEqual(result, correct, "Should return parsed float if number is an int")

    string = "blablabla"
    result = validator.get_number_from_string(string)
    correct = None
    self.assertEqual(result, correct, "Should return None if string doesnt contain any number")
