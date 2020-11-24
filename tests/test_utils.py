import unittest
import sys, os
from os.path import dirname, join, abspath
sys.path.insert(0, abspath(join(dirname(__file__), '..')))
import utils

class TestUtils(unittest.TestCase):

  def test_convert_to_price_string(self):
    number = 39.90
    result = utils.convert_to_price_string(number)
    correct = "39,90"
    self.assertEqual(result, correct, "Should return correct price string for floats")

    number = 39
    result = utils.convert_to_price_string(number)
    correct = "39,00"
    self.assertEqual(result, correct, "Should return correct price string for ints")

    # TODO: This does not act as the normal rounding when a 5 is rounded up
    # TODO: which might cause a problem
    number = 39.555
    result = utils.convert_to_price_string(number)
    correct = "39,55"
    self.assertEqual(result, correct, "Should round the input correctly")


    number = "blabla"
    result = utils.convert_to_price_string(number)
    correct = None
    self.assertEqual(result, correct, "Should return None if incorrect input")

  def test_convert_to_nr(self):
    string = "39,90"
    result = utils.convert_to_nr(string)
    correct = 39.90
    self.assertEqual(result, correct, "Should return parsed float if number contains comma")

    string = "39.90"
    result = utils.convert_to_nr(string)
    correct = 39.90
    self.assertEqual(result, correct, "Should return parsed float if number contains dot")

    string = "blabla"
    result = utils.convert_to_nr(string)
    correct = None
    self.assertEqual(result, correct, "Should return None if input is not a number")

    string = "blabla39.90"
    result = utils.convert_to_nr(string)
    correct = None
    self.assertEqual(result, correct, "Should return None if input is not ONLY a number")

  def test_get_number_from_string(self):
    string = "39,90Kr/kg"
    result = utils.get_number_from_string(string)
    correct = 39.90
    self.assertEqual(result, correct, "Should return parsed float if number contains comma")

    string = "*Cel Flamingo35.5c1"
    result = utils.get_number_from_string(string)
    correct = 35.5
    self.assertEqual(result, correct, "Should return parsed float if number contains dot")

    string = "*Cel Flamingo 35c1"
    result = utils.get_number_from_string(string)
    correct = 35
    self.assertEqual(result, correct, "Should return parsed float if number is an int")

    string = "blablabla"
    result = utils.get_number_from_string(string)
    correct = None
    self.assertEqual(result, correct, "Should return None if string doesnt contain any number")

  def test_remove_double_minus_sign(self):
    string = "--4,00"
    result = utils.remove_double_minus_sign(string)
    correct = "-4,00"
    self.assertEqual(result, correct, "Should return price with single minus sign if input has multiple minus signs")

    string = "------4,00"
    result = utils.remove_double_minus_sign(string)
    correct = "-4,00"
    self.assertEqual(result, correct, "Should return price with single minus sign if input has multiple minus signs")

    string = "blabla"
    result = utils.remove_double_minus_sign(string)
    correct = string
    self.assertEqual(result, correct, "Should return input if not a price string")

  def test_check_price(self):
    price = "34,99"
    result = utils.check_price(price)
    self.assertEqual(price, result, "Should return the price if the format is correct")

    price = "34.99"
    result = utils.check_price(price)
    self.assertEqual(price, result, "Should work with dots")

    price = "-34,99"
    result = utils.check_price(price)
    self.assertEqual(price, result, "Should be able to handle negative prices")

    price = "blabla"
    result = utils.check_price(price)
    self.assertFalse(result, "Should be false if input is not a price")


if __name__ == '__main__':
  unittest.main()
