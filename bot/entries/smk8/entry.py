from bot.entries.smk8.base_entry import BaseEntry
from bot.entries.smk8.preprocess import preprocess_page


class Entry(BaseEntry):
    def __init__(self, target, page_id):
        entry_id = (page_id, 0)
        super().__init__(target, entry_id)

    def set_page(self, page):
        page = preprocess_page(page)
        super().set_page(page)

    def _get_headwords(self):
        soup = self.get_page_soup()
        self._delete_unused_nodes(soup)
        self._fill_alts(soup)
        reading = self._find_reading(soup)
        expressions = []
        if soup.find("見出部").find("標準表記") is None:
            expressions.append(reading)
        for expression in self._find_expressions(soup):
            if expression not in expressions:
                expressions.append(expression)
        headwords = {reading: expressions}
        return headwords
