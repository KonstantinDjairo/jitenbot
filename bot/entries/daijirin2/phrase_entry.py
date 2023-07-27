import re

import bot.entries.base.expressions as Expressions
from bot.data import load_phrase_readings
from bot.entries.daijirin2.base_entry import BaseEntry


class PhraseEntry(BaseEntry):
    def get_part_of_speech_tags(self):
        # phrases do not contain these tags
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
        text = soup.find("句表記").text
        text = self._clean_expression(text)
        alternatives = parse_phrase(text)
        expressions = []
        for alt in alternatives:
            for exp in Expressions.expand_abbreviation(alt):
                expressions.append(exp)
        return expressions

    def _find_readings(self):
        phrase_readings = load_phrase_readings(self.target)
        text = phrase_readings[self.entry_id]
        alternatives = parse_phrase(text)
        readings = []
        for alt in alternatives:
            for reading in Expressions.expand_abbreviation(alt):
                readings.append(reading)
        return readings


def parse_phrase(text):
    """Return a list of strings described by ＝ notation."""
    group_pattern = r"([^＝]+)(＝([^（]+)（＝([^（]+)）)?"
    groups = re.findall(group_pattern, text)
    expressions = [""]
    for group in groups:
        new_exps = []
        for expression in expressions:
            new_exps.append(expression + group[0])
        expressions = new_exps.copy()
        if group[1] == "":
            continue
        new_exps = []
        for expression in expressions:
            new_exps.append(expression + group[2])
        for expression in expressions:
            for alt in group[3].split("・"):
                new_exps.append(expression + alt)
        expressions = new_exps.copy()
    return expressions
