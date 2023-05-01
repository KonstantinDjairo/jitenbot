import re
from bs4 import BeautifulSoup

import bot.expressions as Expressions
import bot.soup as Soup
from bot.data import load_smk8_phrase_readings
from bot.entries.entry import Entry
from bot.entries.smk8_preprocess import preprocess_page


class _BaseSmk8Entry(Entry):
    ID_TO_ENTRY = {}
    SUBENTRY_ID_TO_ENTRY_ID = {}

    def __init__(self, entry_id):
        super().__init__(entry_id)
        if entry_id not in self.ID_TO_ENTRY:
            self.ID_TO_ENTRY[entry_id] = self
        else:
            raise Exception(f"Duplicate entry ID: {entry_id}")
        self.children = []
        self.phrases = []
        self.kanjis = []

    def set_page(self, page):
        page = self.__decompose_subentries(page)
        self._page = page

    def get_page_soup(self):
        soup = BeautifulSoup(self._page, "xml")
        return soup

    def get_headwords(self):
        if self._headwords is not None:
            return self._headwords
        self._set_headwords()
        self._set_variant_headwords()
        return self._headwords

    def get_part_of_speech_tags(self):
        if self._part_of_speech_tags is not None:
            return self._part_of_speech_tags
        self._part_of_speech_tags = []
        soup = self.get_page_soup()
        headword_info = soup.find("見出要素")
        if headword_info is None:
            return self._part_of_speech_tags
        for tag in headword_info.find_all("品詞M"):
            if tag.text not in self._part_of_speech_tags:
                self._part_of_speech_tags.append(tag.text)
        return self._part_of_speech_tags

    def _set_variant_headwords(self):
        for expressions in self._headwords.values():
            Expressions.add_variant_kanji(expressions, self._variant_kanji)
            Expressions.add_fullwidth(expressions)
            Expressions.remove_iteration_mark(expressions)
            Expressions.add_iteration_mark(expressions)

    def _find_reading(self, soup):
        midasi_kana = soup.find("見出仮名")
        reading = midasi_kana.text
        for x in [" ", "・"]:
            reading = reading.replace(x, "")
        return reading

    def _find_expressions(self, soup):
        clean_expressions = []
        for expression in soup.find_all("標準表記"):
            clean_expression = self._clean_expression(expression.text)
            clean_expressions.append(clean_expression)
        expressions = Expressions.expand_abbreviation_list(clean_expressions)
        return expressions

    def __decompose_subentries(self, page):
        soup = BeautifulSoup(page, features="xml")
        subentry_parameters = [
            [Smk8ChildEntry, ["子項目F", "子項目"], self.children],
            [Smk8PhraseEntry, ["句項目F", "句項目"], self.phrases],
            [Smk8KanjiEntry, ["造語成分項目"], self.kanjis],
        ]
        for x in subentry_parameters:
            subentry_class, tags, subentry_list = x
            for tag in tags:
                tag_soup = soup.find(tag)
                while tag_soup is not None:
                    tag_soup.name = "項目"
                    subentry_id = self.id_string_to_entry_id(tag_soup.attrs["id"])
                    self.SUBENTRY_ID_TO_ENTRY_ID[subentry_id] = self.entry_id
                    subentry = subentry_class(subentry_id)
                    page = tag_soup.decode()
                    subentry.set_page(page)
                    subentry_list.append(subentry)
                    tag_soup.decompose()
                    tag_soup = soup.find(tag)
        return soup.decode()

    @staticmethod
    def id_string_to_entry_id(id_string):
        parts = id_string.split("-")
        if len(parts) == 1:
            return (int(parts[0]), 0)
        elif len(parts) == 2:
            # subentries have a hexadecimal part
            return (int(parts[0]), int(parts[1], 16))
        else:
            raise Exception(f"Invalid entry ID: {id_string}")

    @staticmethod
    def _clean_expression(expression):
        for x in ["〈", "〉", "｛", "｝", "…", " "]:
            expression = expression.replace(x, "")
        return expression

    @staticmethod
    def _fill_alts(soup):
        for e in soup.find_all(["親見出仮名", "親見出表記"]):
            e.string = e.attrs["alt"]
        for gaiji in soup.find_all("外字"):
            gaiji.string = gaiji.img.attrs["alt"]


class Smk8Entry(_BaseSmk8Entry):
    def __init__(self, page_id):
        entry_id = (page_id, 0)
        super().__init__(entry_id)

    def set_page(self, page):
        page = preprocess_page(page)
        super().set_page(page)

    def _set_headwords(self):
        soup = self.get_page_soup()
        Soup.delete_soup_nodes(soup, "表音表記")
        self._fill_alts(soup)
        reading = self._find_reading(soup)
        expressions = []
        if soup.find("見出部").find("標準表記") is None:
            expressions.append(reading)
        for expression in self._find_expressions(soup):
            if expression not in expressions:
                expressions.append(expression)
        self._headwords = {reading: expressions}


class Smk8ChildEntry(_BaseSmk8Entry):
    def __init__(self, entry_id):
        super().__init__(entry_id)

    def _set_headwords(self):
        soup = self.get_page_soup()
        Soup.delete_soup_nodes(soup, "表音表記")
        self._fill_alts(soup)
        reading = self._find_reading(soup)
        expressions = []
        if soup.find("子見出部").find("標準表記") is None:
            expressions.append(reading)
        for expression in self._find_expressions(soup):
            if expression not in expressions:
                expressions.append(expression)
        self._headwords = {reading: expressions}


class Smk8PhraseEntry(_BaseSmk8Entry):
    def __init__(self, entry_id):
        super().__init__(entry_id)
        self.__phrase_readings = load_smk8_phrase_readings()

    def get_part_of_speech_tags(self):
        # phrases do not contain these tags
        return []

    def _set_headwords(self):
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
        self._headwords = headwords

    def _find_expressions(self, soup):
        Soup.delete_soup_nodes(soup, "ルビG")
        self._fill_alts(soup)
        text = soup.find("標準表記").text
        text = self._clean_expression(text)
        alternatives = self.__expand_alternatives(text)
        expressions = []
        for alt in alternatives:
            for exp in Expressions.expand_abbreviation(alt):
                expressions.append(exp)
        return expressions

    def _find_readings(self):
        text = self.__phrase_readings[self.entry_id]
        alternatives = self.__expand_alternatives(text)
        readings = []
        for alt in alternatives:
            for reading in Expressions.expand_abbreviation(alt):
                readings.append(reading)
        return readings

    @staticmethod
    def __expand_alternatives(expression):
        """Return a list of strings described by △ notation
        eg. "△金（時間・暇）に飽かして" -> [
            "金に飽かして", "時間に飽かして", "暇に飽かして"
        ]
        """
        m = re.search(r"△([^（]+)（([^（]+)）", expression)
        if not m:
            return [expression]
        alt_parts = [m.group(1)]
        for alt_part in m.group(2).split("・"):
            alt_parts.append(alt_part)
        alts = []
        for alt_part in alt_parts:
            alt_exp = re.sub(r"△[^（]+（[^（]+）", alt_part, expression)
            alts.append(alt_exp)
        return alts


class Smk8KanjiEntry(_BaseSmk8Entry):
    def __init__(self, entry_id):
        super().__init__(entry_id)

    def _set_headwords(self):
        soup = self.get_page_soup()
        self._fill_alts(soup)
        reading = self.__get_parent_reading()
        expressions = self._find_expressions(soup)
        self._headwords = {reading: expressions}

    def __get_parent_reading(self):
        parent_id = self.SUBENTRY_ID_TO_ENTRY_ID[self.entry_id]
        parent = self.ID_TO_ENTRY[parent_id]
        reading = parent.get_first_reading()
        return reading
