import re

import src.categories as categories

MAPPINGS = {
  'avo.ado': categories.GRONSAKER,
  'blandf.rs': categories.KOTT,
  '.gg': categories.MEJERI,
  'pant': categories.PANT,
  'dressing': categories.SASER,
  'bacon': categories.CHARK,
  'basilika': categories.KRYDDOR,  # TODO: What if this would be "basilika the plant", instead of the spice
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
  'crispy pear': categories.DRYCK,
  'hallon bcaa': categories.DRYCK,
  'k.rsb.rstomat': categories.GRONSAKER,
  # 'chevre': categories.MEJERI,
  'chilipulver': categories.KRYDDOR,
  'clementin': categories.FRUKT,
  'cr.me': categories.MEJERI,
  'dark temptation': categories.KAFFE,
  'dryck': categories.DRYCK,
  'drink': categories.DRYCK,
  'energidry': categories.DRYCK,
  'filter oblekt': categories.KAFFE,
  'fl.skytterfil': categories.KOTT,
  'flankstek': categories.KOTT,
  'frisco': categories.SPANNMAL,
  'flingor': categories.SPANNMAL,
  'flamingo': categories.DRYCK,
  'fiberhusk': categories.OVRIGT,
  'godis': categories.SNACKS,
  'gr.dde': categories.MEJERI,
  'guacamole dip mix': categories.KRYDDOR,
  'gurka': categories.GRONSAKER,
  'handdisk': categories.HYGIEN,
  'h.grev': categories.KOTT,
  'hallon acai': categories.DRYCK,
  'brioche': categories.SPANNMAL,
  'herrg.*rd': categories.MEJERI, # represents Herrgård the cheese
  'hårpynt': categories.OVRIGT,
  'intenzo': categories.KAFFE,
  'isbergssallad': categories.GRONSAKER,
  'j.ttefranska': categories.SPANNMAL,
  'choklad': categories.SNACKS,
  'kaffe': categories.KAFFE,
  'kokosmj.lk': categories.OVRIGT,
  'kyckling': categories.KOTT,
  'l.kpulver': categories.KRYDDOR,
  'lax': categories.FISK,
  'led par16': categories.OVRIGT,
  'l.k ': categories.GRONSAKER,   # taking a guess here that "Lök" is always followed by another word, to not confuse it with "lökpulver"
  'majonn.s': categories.OVRIGT,
  'max spearmint': categories.OVRIGT,
  'm.rkrost': categories.KAFFE,
  'mozzarella': categories.MEJERI, 
  'n.tf.rs': categories.KOTT,
  '.lgf.rs': categories.KOTT,
  '.liver': categories.GRONSAKER,
  'olivolja': categories.OLJOR,
  'oregano': categories.KRYDDOR,
  'orginalrost': categories.SPANNMAL,
  'ost': categories.MEJERI,
  'papperskasse': categories.OVRIGT,
  'paprikamix': categories.GRONSAKER,
  'paprika ': categories.GRONSAKER,  # this should represent "paprika ... and something more", which would be paprika the vegetable 
  'paprika': categories.KRYDDOR, # From sample data one can conclude that only the word "paprika" represents the spice
  'parmig': categories.MEJERI,
  'pasta': categories.SPANNMAL,
  'pesto': categories.OVRIGT, # TODO: Maybe this should be a sauce?
  'philadelp': categories.MEJERI,
  'plopp': categories.SNACKS,
  'procomfort': categories.OVRIGT,
  'pumpa hallowen': categories.OVRIGT,
  'roll-on': categories.HYGIEN,
  'russin': categories.SNACKS,
  'salladskrydda': categories.KRYDDOR,
  'sallad isberg': categories.GRONSAKER,
  'salla. roman': categories.GRONSAKER,
  'satsumas': categories.FRUKT,
  'skalkniv': categories.OVRIGT,
  'sk.ner.st': categories.SPANNMAL,
  'sk.ljmedel': categories.HYGIEN,
  'sm.r': categories.MEJERI,  # TODO: Det här kommer även matcha "Smörgås" t.ex.
  'spareribs': categories.KOTT,
  'sylt': categories.SNACKS,
  'tampong': categories.OVRIGT,
  'tomatpur': categories.OVRIGT,
  'tomater krossade': categories.OVRIGT, # TODO: Finns det någon kategori som man kan lägga det här i?
  'tomat': categories.GRONSAKER,
  'torsk': categories.FISK,
  'tortilla chips': categories.SNACKS,
  'tortilla original': categories.SPANNMAL,
  'tv.ttservetter': categories.HYGIEN,
  'ultra long': categories.OVRIGT,
  'ultra night': categories.OVRIGT,
  'vitk.l': categories.GRONSAKER,
  'vitl.kspulver': categories.KRYDDOR,
  'vin.ger': categories.OVRIGT,
  'werthers': categories.SNACKS,
  'white peach': categories.DRYCK,
  'winegums': categories.SNACKS,
  'yoggi': categories.MEJERI,
  'korv': categories.CHARK,
  'tv.l': categories.HYGIEN,
  'de.': categories.HYGIEN,
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

  def categorize_discounts(self, discounts):
    if len(discounts) == 0:
      return

    for discount in discounts:
      category = self.get_category(discount['name'])
      discount['category'] = category
    
    return discounts


  def get_category(self, name):
    for mapping_key in MAPPINGS:
      reg = re.compile(mapping_key)
      if reg.search(name.lower()):
        if self.debug:
          print("Matched article {} with category {}".format(name, MAPPINGS[mapping_key]))
        return MAPPINGS[mapping_key]
    return None
