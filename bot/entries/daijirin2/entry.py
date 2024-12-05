import bot.entries.base.expressions as Expressions
from bot.entries.daijirin2.base_entry import BaseEntry
from bot.entries.daijirin2.preprocess import preprocess_page


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
        if soup.find("漢字見出") is not None:
            headwords = self._get_kanji_headwords(soup)
        elif soup.find("略語G") is not None:
            headwords = self._get_acronym_headwords(soup)
        else:
            headwords = self._get_regular_headwords(soup)
        return headwords

    def _get_kanji_headwords(self, soup):
        readings = []
        for el in soup.find_all("漢字音"):
            hira = Expressions.kata_to_hira(el.text)
            readings.append(hira)
        if soup.find("漢字音") is None:
            readings.append("")
        expressions = []
        for el in soup.find_all("漢字見出"):
            expressions.append(el.text)
        headwords = {}
        for reading in readings:
            headwords[reading] = expressions
        return headwords

    def _get_acronym_headwords(self, soup):
        expressions = []
        for el in soup.find_all("略語"):
            expression_parts = []
            for part in el.find_all(["欧字", "和字"]):
                expression_parts.append(part.text)
            expression = "".join(expression_parts)
            expressions.append(expression)
        headwords = {"": expressions}
        return headwords
