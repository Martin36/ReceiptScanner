import unittest
import sys, os
from os.path import dirname, join, abspath
sys.path.insert(0, abspath(join(dirname(__file__), '..')))

from write_to_csv import *

class TestWriteToCsv(unittest.TestCase):

  def test_get_smallest_total(self):
    totals = [
      {
        "name": "totals",
        "sum": "766,69",
        "amount": "32"
      }
    ]
    smallest_total = get_smallest_total(totals)
    correct = "766,69"
    self.assertEqual(smallest_total, correct, "Should return the lowest sum of the totals, if only one")

    totals = [
      {
        "name": "totals",
        "sum": "628,07",
        "amount": "17"
      },
      {
        "name": "totals",
        "sum": "597,07"
      }
    ]
    smallest_total = get_smallest_total(totals)
    correct = "597,07"
    self.assertEqual(smallest_total, correct, "Should return the lowest sum of the totals, if multiple")

    totals = []
    smallest_total = get_smallest_total(totals)
    correct = ""
    self.assertEqual(smallest_total, correct, "Should return empty string if there are no totals")

    totals = [
      {
        "name": "totals",
        "amount": "17"
      },
    ]
    smallest_total = get_smallest_total(totals)
    correct = ""
    self.assertEqual(smallest_total, correct, "Should return empty string if there are no totals with sums")


if __name__ == '__main__':
  unittest.main()
