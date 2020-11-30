import utils


class Prettyfier:
  def __init__(self, debug=False):
    self.debug = debug

  def clean_article_names(self, articles):
    for i, article in enumerate(articles):
      name = article['name']
      clean_name = utils.remove_diactrics(name)
      article['name'] = clean_name
    return articles