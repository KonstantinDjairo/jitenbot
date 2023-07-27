from bot.entries.smk8.base_entry import BaseEntry


class ChildEntry(BaseEntry):
    def _get_headwords(self):
        soup = self.get_page_soup()
        self._delete_unused_nodes(soup)
        self._fill_alts(soup)
        reading = self._find_reading(soup)
        expressions = []
        if soup.find("子見出部").find("標準表記") is None:
            expressions.append(reading)
        for expression in self._find_expressions(soup):
            if expression not in expressions:
                expressions.append(expression)
        headwords = {reading: expressions}
        return headwords
