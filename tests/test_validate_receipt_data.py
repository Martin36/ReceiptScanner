import unittest
import sys, os
from os.path import dirname, join, abspath
sys.path.insert(0, abspath(join(dirname(__file__), '..')))
from validate_receipt_data import ReceiptDataValidator

validator = ReceiptDataValidator()

parsed_data = {
  "name": "D:\\Documents\\Kvitto Scanner\\Receipts\\coop-20-10-20.pdf",
  "market": "coop",
  "dates": [
    "2020-10-20"
  ],
  "articles": [
    {
      "name": "BLANDFARS 20% 50/50",
      "sum": "75,25",
      "amount": "1,004 kg",
      "price": "74,95 SEK/kg",
      "bounding_box": {
        "xmin": 1185,
        "xmax": 2314,
        "ymin": 1292,
        "ymax": 1495
      }
    },
    {
      "name": "BLANDFARS 20% 50/50",
      "sum": "75,85",
      "amount": "1,012 kg",
      "price": "74,95 SEK/kg",
      "bounding_box": {
        "xmin": 1187,
        "xmax": 2311,
        "ymin": 1468,
        "ymax": 1670
      }
    },
    {
      "name": "BLOMKAL GRÖN",
      "sum": "21,18",
      "amount": "0,606 kg",
      "price": "34,95 SEK/kg",
      "bounding_box": {
        "xmin": 1183,
        "xmax": 2311,
        "ymin": 1648,
        "ymax": 1855
      }
    },
    {
      "name": "BLOMKAL ST",
      "sum": "21,95",
      "amount": "1 st",
      "price": "21,95",
      "bounding_box": {
        "xmin": 1180,
        "xmax": 1487,
        "ymin": 1816,
        "ymax": 1915
      }
    },
    {
      "name": "BRYSSEL NAT 50OG",
      "sum": "17,95",
      "amount": "1 st",
      "price": "17,95",
      "bounding_box": {
        "xmin": 1178,
        "xmax": 1487,
        "ymin": 1902,
        "ymax": 2019
      }
    },
    {
      "name": "CITRON LIME",
      "sum": "17,95",
      "amount": "1 st",
      "price": "17,95",
      "bounding_box": {
        "xmin": 1181,
        "xmax": 1445,
        "ymin": 1996,
        "ymax": 2112
      }
    },
    {
      "name": "PANT 1KR BURK 1X1KR",
      "sum": "1,00",
      "amount": "1 st",
      "price": "1,00",
      "bounding_box": {
        "xmin": 1240,
        "xmax": 1443,
        "ymin": 2084,
        "ymax": 2201
      }
    },
    {
      "name": "CREME FRAICHE 34%",
      "sum": "49,00",
      "amount": "2 st",
      "price": "24,50",
      "bounding_box": {
        "xmin": 1172,
        "xmax": 1603,
        "ymin": 2172,
        "ymax": 2384
      }
    },
    {
      "name": "DARK TEMPTATION",
      "sum": "41,95",
      "amount": "1 st",
      "price": "41,95",
      "bounding_box": {
        "xmin": 1186,
        "xmax": 1359,
        "ymin": 2375,
        "ymax": 2460
      }
    },
    {
      "name": "DRYCK VATTENM/PARON",
      "sum": "13,95",
      "amount": "1 st",
      "price": "13,95",
      "bounding_box": {
        "xmin": 1164,
        "xmax": 1411,
        "ymin": 2453,
        "ymax": 2558
      }
    },
    {
      "name": "GURKA STYCK",
      "sum": "25,90",
      "amount": "2 st",
      "price": "12,95",
      "bounding_box": {
        "xmin": 1187,
        "xmax": 1575,
        "ymin": 2540,
        "ymax": 2725
      }
    },
    {
      "name": "HALLON ACAI",
      "sum": "17,95",
      "amount": "1 st",
      "price": "17,95",
      "bounding_box": {
        "xmin": 1186,
        "xmax": 1447,
        "ymin": 2720,
        "ymax": 2805
      }
    },
    {
      "name": "PANT 1KR BURK 1X1KR",
      "sum": "1,00",
      "amount": "1 st",
      "price": "1,00",
      "bounding_box": {
        "xmin": 1275,
        "xmax": 1443,
        "ymin": 2808,
        "ymax": 2888
      }
    },
    {
      "name": "INTENZO XLT",
      "sum": "41,95",
      "amount": "1 st",
      "price": "41,95",
      "bounding_box": {
        "xmin": 1188,
        "xmax": 1487,
        "ymin": 2900,
        "ymax": 2975
      }
    },
    {
      "name": "KYCKLING FARS Medlem M",
      "sum": "99,80",
      "amount": "2 st",
      "price": "49,90",
      "bounding_box": {
        "xmin": 1182,
        "xmax": 1575,
        "ymin": 2974,
        "ymax": 3159
      }
    },
    {
      "name": "KYCKLINGFILE",
      "sum": "169,90",
      "amount": "2 st",
      "price": "84,95",
      "bounding_box": {
        "xmin": 1182,
        "xmax": 1706,
        "ymin": 3142,
        "ymax": 3338
      }
    },
    {
      "name": "MULTIVITAMINDRINK",
      "sum": "13,50",
      "amount": "1 st",
      "price": "13,50",
      "bounding_box": {
        "xmin": 1183,
        "xmax": 1918,
        "ymin": 3318,
        "ymax": 3430
      }
    },
    {
      "name": "ORIGINAL KRAMIG HAL",
      "sum": "19,50",
      "amount": "1 st",
      "price": "19,50",
      "bounding_box": {
        "xmin": 1184,
        "xmax": 1562,
        "ymin": 3414,
        "ymax": 3521
      }
    },
    {
      "name": "PHILADELP ORIGINAL",
      "sum": "39,90",
      "amount": "2 st",
      "price": "19,95",
      "bounding_box": {
        "xmin": 1184,
        "xmax": 1572,
        "ymin": 3504,
        "ymax": 3698
      }
    },
    {
      "name": "SATSUMAS",
      "sum": "11,81",
      "amount": "0,538 kg",
      "price": "21,95 SEK/kg",
      "bounding_box": {
        "xmin": 1182,
        "xmax": 2298,
        "ymin": 3683,
        "ymax": 3879
      }
    },
    {
      "name": "SKÁNERÖST",
      "sum": "41,95",
      "amount": "1 st",
      "price": "41,95",
      "bounding_box": {
        "xmin": 1180,
        "xmax": 1570,
        "ymin": 3855,
        "ymax": 3967
      }
    },
    {
      "name": "SMÖR OSALTAT",
      "sum": "39,95",
      "amount": "1 st",
      "price": "39,95",
      "bounding_box": {
        "xmin": 1176,
        "xmax": 1351,
        "ymin": 3952,
        "ymax": 4066
      }
    },
    {
      "name": "SQUEEZY JORDGSYLT",
      "sum": "27,95",
      "amount": "1 st",
      "price": "27,95",
      "bounding_box": {
        "xmin": 1172,
        "xmax": 1482,
        "ymin": 4042,
        "ymax": 4155
      }
    },
    {
      "name": "4TOMATER KROSSADE",
      "sum": "11,95",
      "amount": "1 st",
      "price": "11,95",
      "bounding_box": {
        "xmin": 1180,
        "xmax": 1571,
        "ymin": 4122,
        "ymax": 4247
      }
    },
    {
      "name": "VISPGRADDE 36%",
      "sum": "39,95",
      "amount": "1 st",
      "price": "39,95",
      "bounding_box": {
        "xmin": 1174,
        "xmax": 1603,
        "ymin": 4207,
        "ymax": 4334
      }
    },
    {
      "name": "WHITE PEACH",
      "sum": "17,95",
      "amount": "1 st",
      "price": "17,95",
      "bounding_box": {
        "xmin": 1172,
        "xmax": 1412,
        "ymin": 4307,
        "ymax": 4422
      }
    },
    {
      "name": "PANT 1KR BURK 1X1KR",
      "sum": "1,00",
      "amount": "1 st",
      "price": "1,00",
      "bounding_box": {
        "xmin": 1262,
        "xmax": 1439,
        "ymin": 4405,
        "ymax": 4504
      }
    }
  ],
  "discounts": [
    {
      "name": "RABATTER",
      "price": "-3,90"
    },
    {
      "name": "Kaffe 59kr",
      "price": "-66,85"
    },
    {
      "name": "Blandfärs 49,90/kg",
      "price": "-9,95"
    },
    {
      "name": "Philadelphia 10kr",
      "price": "-9,95"
    },
    {
      "name": "Philadelphia 10kr",
      "price": "-25,05"
    },
    {
      "name": "Kyckling 59,90",
      "price": "-25,05"
    }
  ],
  "totals": [
    {
      "name": "totals",
      "sum": "766,69",
      "amount": "32"
    }
  ],
  "bounding_box": {
    "xmin": 1164,
    "xmax": 3084,
    "ymin": -16,
    "ymax": 5777
  }
}

class TestReceiptDataValidator(unittest.TestCase):

  def test_check_articles(self):
    result = validator.check_articles(parsed_data['articles'])
    self.assertEqual(result, [], "Should return empty array if all articles are scanned correctly")

  def test_check_nr_of_articles(self):
    result = validator.check_nr_of_articles(parsed_data)
    self.assertTrue(result, "Should return True if the nr of parsed articles and the amount read on the receipt are the same")

  def test_count_articles(self):
    articles = [
      {
        "name": "AVOCADO 3-PACK",
        "sum": "59,16",
        "amount": "1 st",
        "price": "59,16",
      },
      {
        "name": "KEXCHOKLAD MINI",
        "sum": "17,95",
        "amount": "1 st",
        "price": "17,95",
      },
      {
        "name": "MAX SPEARMINT",
        "sum": "29,00",
        "amount": "2 st",
        "price": "14,50",
      },
    ]
    result = validator.count_articles(articles)
    correct = 4
    self.assertEqual(result, correct, "Should return correct amount of articles")

    articles = [
      {
        "name": "LAXFIL@",
        "sum": "164,14",
        "amount": "1,658kg",
        "price": "99,00kr/kg",
        "bounding_box": {
          "xmin": 1082,
          "xmax": 2365,
          "ymin": 546,
          "ymax": 789
        }
      },
      {
        "name": "TORSKRYGG 3FIL@ 450G",
        "sum": "178,00",
        "amount": "2st",
        "price": "89,00",
        "bounding_box": {
          "xmin": 1078,
          "xmax": 2636,
          "ymin": 796,
          "ymax": 947
        }
      }
    ]
    result = validator.count_articles(articles)
    correct = 3
    self.assertEqual(result, correct, "Should count weight-based articles as 1")

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
