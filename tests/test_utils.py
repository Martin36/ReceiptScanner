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
    
    string = "0,00"
    result = utils.get_number_from_string(string)
    correct = 0.00
    self.assertEqual(result, correct, "Should return parsed float if string contains only a number with comma")


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

  def test_remove_diactrics(self):
    string = 'NOTF@RS 12%'
    result = utils.remove_diactrics(string)
    self.assertEqual(result, string, "Should not change a string containing @ signs")

    string = 'FL®SKYTTERFIL®'
    result = utils.remove_diactrics(string)
    correct = 'FL@SKYTTERFIL@'
    self.assertEqual(result, correct, "Should not change a string containing no diactrics")

    string = 'MOŽŽARELLA Ġ'
    result = utils.remove_diactrics(string)
    correct = 'MOZZARELLA G'
    self.assertEqual(result, correct, "Should change a string containing diactrics")

    string = 'MOZZAŘELLA för 22kr'
    result = utils.remove_diactrics(string)
    correct = 'MOZZARELLA för 22kr'
    self.assertEqual(result, correct, "Should only change a non-swedish diactrics")

  def test_find_swe_chars(self):
    string = 'MOZZAŘELLA för 22kr'
    result = utils.find_swe_chars(string)
    self.assertEqual(len(result), 1, "Should find correct amount of swe chars")
    result_obj = result[0]
    self.assertEqual(result_obj['letter'], 'ö', 'Should find the correct swe char')
    self.assertEqual(result_obj['idx'], 12, 'Should find the correct idx of char')

  def test_return_swe_chars(self):
    string = 'MOZZAŘELLA for 22kr'
    char_arr = [{'letter': 'ö', 'idx': 12}]
    correct = 'MOZZAŘELLA för 22kr'
    result = utils.return_swe_chars(string, char_arr)
    self.assertEqual(result, correct, "Should return the correct char at the correct pos")
    
  def test_replace_weird_chars(self):
    string = 'FL®SKYTTERFIL®'
    result = utils.replace_weird_chars(string)
    correct = 'FL@SKYTTERFIL@'
    self.assertEqual(result, correct, 'Should replace ® with @')

    string = 'blabla'
    result = utils.replace_weird_chars(string)
    correct = 'blabla'
    self.assertEqual(result, correct, 'Should not replace any chars in a string without weird chars')


if __name__ == '__main__':
  unittest.main()
