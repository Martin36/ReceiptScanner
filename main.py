from receipt_parser import GcloudParser

PATH = 'D:\\Documents\\Kvitto Scanner\\Receipts\\coop-20-10-27.pdf'

parser = GcloudParser()

articles, dates, markets, discounts = parser.parse_pdf(PATH)
print(articles)
print(dates)
print(markets)
print(discounts)