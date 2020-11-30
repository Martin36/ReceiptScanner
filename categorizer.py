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
  'city pulse': categories.DRYCK,
  'citron lime': categories.DRYCK,
  'cel flamingo': categories.DRYCK,
  'hallon bcaa': categories.DRYCK,
  'k.rsb.rstomat': categories.GRONSAKER,
  'white peach': categories.DRYCK,
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
  'frisco': categories.SPANNMAL,
  'flingor': categories.SPANNMAL,
  'godis': categories.SNACKS,
  'gr.dde': categories.MEJERI,
  'guacamole dip mix': categories.KRYDDOR,
  'gurka': categories.GRONSAKER,
  'h.grev': categories.KOTT,
  'hallon acai': categories.DRYCK,
  'brioche': categories.SPANNMAL,
  'herrg.*rd': categories.MEJERI, # represents Herrgård the cheese
  'hårpynt': categories.OVRIGT,
  'intenzo': categories.KAFFE,
  'isbergssallad': categories.GRONSAKER,
  'j.ttefranska': categories.SPANNMAL,
  'choklad': categories.SNACKS,
  'kokosmjölk': categories.OVRIGT,
  'kyckling': categories.KOTT,
  'l.kpulver': categories.KRYDDOR,
  'lax': categories.FISK,
  'led par16': categories.OVRIGT,
  'l.k ': categories.GRONSAKER,   # taking a guess here that "Lök" is always followed by another word, to not confuse it with "lökpulver"
  'majonn.s': categories.OVRIGT,
  'max spearmint': categories.OVRIGT,
  'm.rkrost': categories.KAFFE,
  'mozzarella': categories.MEJERI, 
  
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