import re

import categories

MAPPINGS = {
  'avokado': categories.GRONSAKER,
  'blandf.rs': categories.KOTT,
  '.gg': categories.MEJERI,
  'pant': categories.PANT,
  'dressing': categories.SASER,
  'bacon': categories.CHARK,
  'biff': categories.KOTT,
  'banan': categories.FRUKT,
  'bearnaise': categories.SASER,
  'blomk.l': categories.GRONSAKER,
  'bregott': categories.MEJERI,
  'broccoli': categories.GRONSAKER,
  'bryssel': categories.GRONSAKER,
  'celsius': categories.DRYCK,
  # 'chevre': categories.MEJERI,
  'chilipulver': categories.KRYDDOR,
  'clementin': categories.FRUKT,
  'cr.me': categories.MEJERI,
  'dark temptation': categories.KAFFE,
  'deo': categories.HYGIEN,
  'dryck': categories.DRYCK,
  'drink': categories.DRYCK,
  'energidry': categories.DRYCK,
  'filter oblekt': categories.KAFFE,
  'fl.skytterfil': categories.KOTT,
  'flankstek': categories.KOTT,
  'gr.dde': categories.MEJERI,
  'intenzo': categories.KAFFE,
  'kyckling': categories.KOTT,
  'ost': categories.MEJERI,
  'philadelp': categories.MEJERI,
  'satsumas': categories.FRUKT,
  'sm.r': categories.MEJERI,  # TODO: Det här kommer även matcha "Smörgås" t.ex.
  'tomater krossade': categories.OVRIGT, # TODO: Finns det någon kategori som man kan lägga det här i?
  'tv.l': categories.HYGIEN,
}

class Categorizer:
  def __init__(self, debug=False):
    self.debug = debug

  def categorize_articles(self, articles):
    if len(articles) == 0:
      return

    for article in articles:
      category = self.get_category(article['name'])
      article['category'] = category
    
    return articles


  def get_category(self, name):
    for mapping_key in MAPPINGS:
      reg = re.compile(mapping_key)
      if reg.search(name.lower()):
        if self.debug:
          print("Matched article {} with category {}".format(name, MAPPINGS[mapping_key]))
        return MAPPINGS[mapping_key]
    return None
