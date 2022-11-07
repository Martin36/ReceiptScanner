import unittest
import sys, os
from os.path import dirname, join, abspath
sys.path.insert(0, abspath(join(dirname(__file__), '..')))
from categorizer import Categorizer

categorizer = Categorizer()

class TestCategorizer(unittest.TestCase):

  def test_get_category(self):
    name = "BLANDFARS"
    result = categorizer.get_category(name)
    self.assertEqual(result, 'Kött', 'Should return correct category')

    name = "BLANDFÄRS"
    result = categorizer.get_category(name)
    self.assertEqual(result, 'Kött', 'Should return correct category')

    name = "blabla"
    result = categorizer.get_category(name)
    self.assertEqual(result, None, 'Should return None if unknown category')


if __name__ == '__main__':
  unittest.main()