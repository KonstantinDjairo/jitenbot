import re

import bot.entries.base.expressions as Expressions
from bot.data import load_phrase_readings
from bot.entries.smk8.base_entry import BaseEntry


class PhraseEntry(BaseEntry):
    def __init__(self, target, entry_id):
        super().__init__(target, entry_id)
        self.__phrase_readings = load_phrase_readings(self.target)

    def get_part_of_speech_tags(self):
        # phrase entries do not contain these tags
        return []

    def _get_headwords(self):
        soup = self.get_page_soup()
        headwords = {}
        expressions = self._find_expressions(soup)
        readings = self._find_readings()
        for idx, expression in enumerate(expressions):
            reading = readings[idx]
            if reading in headwords:
                headwords[reading].append(expression)
            else:
                headwords[reading] = [expression]
        return headwords

    def _find_expressions(self, soup):
        self._delete_unused_nodes(soup)
        self._fill_alts(soup)
        text = soup.find("標準表記").text
        text = self._clean_expression(text)
        alternatives = parse_phrase(text)
        expressions = []
        for alt in alternatives:
            for exp in Expressions.expand_abbreviation(alt):
                expressions.append(exp)
        return expressions

    def _find_readings(self):
        text = self.__phrase_readings[self.entry_id]
        alternatives = parse_phrase(text)
        readings = []
        for alt in alternatives:
            for reading in Expressions.expand_abbreviation(alt):
                readings.append(reading)
        return readings


def parse_phrase(text):
    """Return a list of strings described by △ notation."""
    match = re.search(r"△([^（]+)（([^（]+)）", text)
    if match is None:
        return [text]
    alt_parts = [match.group(1)]
    for alt_part in match.group(2).split("・"):
        alt_parts.append(alt_part)
    alts = []
    for alt_part in alt_parts:
        alt_exp = re.sub(r"△[^（]+（[^（]+）", alt_part, text)
        alts.append(alt_exp)
    return alts
