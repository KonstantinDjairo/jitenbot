from bot.data import load_phrase_readings
from bot.entries.sankoku8.base_entry import BaseEntry
from bot.entries.sankoku8.parse import parse_hyouki_soup
from bot.entries.sankoku8.parse import parse_hyouki_pattern


class PhraseEntry(BaseEntry):
    def get_part_of_speech_tags(self):
        # phrases do not contain these tags
        return []

    def _get_headwords(self):
        soup = self.get_page_soup()
        self._delete_unused_nodes(soup)
        expressions = self._find_expressions(soup)
        readings = self._find_readings(soup)
        headwords = {}
        if len(expressions) != len(readings):
            raise Exception(f"{self.entry_id[0]}-{self.entry_id[1]}")
        for idx, expression in enumerate(expressions):
            reading = readings[idx]
            if reading in headwords:
                headwords[reading].append(expression)
            else:
                headwords[reading] = [expression]
        return headwords

    def _find_expressions(self, soup):
        phrase_soup = soup.find("句表記")
        expressions = parse_hyouki_soup(phrase_soup, [""])
        return expressions

    def _find_readings(self, soup):
        reading_patterns = load_phrase_readings(self.target)
        reading_pattern = reading_patterns[self.entry_id]
        readings = parse_hyouki_pattern(reading_pattern)
        return readings
