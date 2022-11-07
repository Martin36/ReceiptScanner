MARKETS = ['ica', 'coop', 'hemköp', 'city gross']
SKIPWORDS = ['SEK', 'www.coop.se', 'Tel.nr:', 'Kvitto:', 
             'Kvitto', 'Datum:', 'Datum', 'Kassör:', 'Org Nr:', 
             'Org', 'Nr:', 'SUMMERING', 'KÖP', 'Kassör',
             'Kassör:']
# TODO: What happens if an article name starts with 'att' (or any of the other words)?
TOTAL_WORDS = ['att', 'betala', 'totalt', 'total']
DISCOUNT_WORDS = ['summering', 'rabatter']
# This represents the offset on the x-axis that the additional information
# has from the start of the article name. It needs to be tweaked so that it
# works correctly
X_OFFSET = 50
# This represents the distance from the edge of the receipt that the 
# price should end AFTER. It is not an optimal solution since the 
# required distance may differ between receipts
PRICE_OFFSET = 200
# This is used to check if an article has been scanned correctly
# One common feature of the articles for different receipts is that
# the name starts close to the left edge of the receipt
ARTICLE_OFFSET = 150
