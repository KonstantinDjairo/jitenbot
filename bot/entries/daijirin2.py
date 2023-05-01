import re
from bs4 import BeautifulSoup

import bot.expressions as Expressions
import bot.soup as Soup
from bot.data import load_daijirin2_phrase_readings
from bot.data import load_daijirin2_kana_abbreviations
from bot.entries.entry import Entry
from bot.entries.daijirin2_preprocess import preprocess_page


class _BaseDaijirin2Entry(Entry):
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
        self._kana_abbreviations = load_daijirin2_kana_abbreviations()

    def set_page(self, page):
        page = self.__decompose_subentries(page)
        self._page = page

    def get_page_soup(self):
        soup = BeautifulSoup(self._page, "xml")
        return soup

    def get_part_of_speech_tags(self):
        if self._part_of_speech_tags is not None:
            return self._part_of_speech_tags
        self._part_of_speech_tags = []
        soup = self.get_page_soup()
        for pos_group in soup.find_all("品詞G"):
            if pos_group.parent.name == "大語義":
                self._set_part_of_speech_tags(pos_group)
        return self._part_of_speech_tags

    def _set_part_of_speech_tags(self, el):
        pos_names = ["品詞", "品詞活用", "品詞行", "用法"]
        for child in el.children:
            if child.name is not None:
                self._set_part_of_speech_tags(child)
                continue
            pos = str(child)
            if el.name not in pos_names:
                continue
            elif pos in ["［", "］"]:
                continue
            elif pos in self._part_of_speech_tags:
                continue
            else:
                self._part_of_speech_tags.append(pos)

    def get_headwords(self):
        if self._headwords is not None:
            return self._headwords
        self._set_headwords()
        self._set_variant_headwords()
        return self._headwords

    def _set_regular_headwords(self, soup):
        self._fill_alts(soup)
        reading = soup.find("見出仮名").text
        expressions = []
        for el in soup.find_all("標準表記"):
            expression = self._clean_expression(el.text)
            if "—" in expression:
                kana_abbrs = self._kana_abbreviations[self.entry_id]
                for abbr in kana_abbrs:
                    expression = expression.replace("—", abbr, 1)
            expressions.append(expression)
        expressions = Expressions.expand_abbreviation_list(expressions)
        if len(expressions) == 0:
            expressions.append(reading)
        self._headwords = {reading: expressions}

    def _set_variant_headwords(self):
        for expressions in self._headwords.values():
            Expressions.add_variant_kanji(expressions, self._variant_kanji)
            Expressions.add_fullwidth(expressions)
            Expressions.remove_iteration_mark(expressions)
            Expressions.add_iteration_mark(expressions)

    def __decompose_subentries(self, page):
        soup = BeautifulSoup(page, features="xml")
        subentry_parameters = [
            [Daijirin2ChildEntry, ["子項目"], self.children],
            [Daijirin2PhraseEntry, ["句項目"], self.phrases],
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
    def _delete_unused_nodes(soup):
        unused_nodes = [
            "漢字音logo", "活用分節", "連語句活用分節", "語構成",
            "表外字マーク", "表外字マーク", "ルビG"
        ]
        for name in unused_nodes:
            Soup.delete_soup_nodes(soup, name)

    @staticmethod
    def _clean_expression(expression):
        for x in ["〈", "〉", "《", "》", " "]:
            expression = expression.replace(x, "")
        return expression

    @staticmethod
    def _fill_alts(soup):
        for gaiji in soup.find_all(class_="gaiji"):
            if gaiji.name == "img" and gaiji.has_attr("alt"):
                gaiji.name = "span"
                gaiji.string = gaiji.attrs["alt"]


class Daijirin2Entry(_BaseDaijirin2Entry):
    def __init__(self, page_id):
        entry_id = (page_id, 0)
        super().__init__(entry_id)

    def set_page(self, page):
        page = preprocess_page(page)
        super().set_page(page)

    def _set_headwords(self):
        soup = self.get_page_soup()
        self._delete_unused_nodes(soup)
        if soup.find("漢字見出") is not None:
            self._set_kanji_headwords(soup)
        elif soup.find("略語G") is not None:
            self._set_acronym_headwords(soup)
        else:
            self._set_regular_headwords(soup)

    def _set_kanji_headwords(self, soup):
        readings = []
        for el in soup.find_all("漢字音"):
            hira = Expressions.kata_to_hira(el.text)
            readings.append(hira)
        if soup.find("漢字音") is None:
            readings.append("")
        expressions = []
        for el in soup.find_all("漢字見出"):
            expressions.append(el.text)
        self._headwords = {}
        for reading in readings:
            self._headwords[reading] = expressions

    def _set_acronym_headwords(self, soup):
        expressions = []
        for el in soup.find_all("略語"):
            expression_parts = []
            for part in el.find_all(["欧字", "和字"]):
                expression_parts.append(part.text)
            expression = "".join(expression_parts)
            expressions.append(expression)
        self._headwords = {"": expressions}


class Daijirin2ChildEntry(_BaseDaijirin2Entry):
    def __init__(self, entry_id):
        super().__init__(entry_id)

    def _set_headwords(self):
        soup = self.get_page_soup()
        self._delete_unused_nodes(soup)
        self._set_regular_headwords(soup)


class Daijirin2PhraseEntry(_BaseDaijirin2Entry):
    def __init__(self, entry_id):
        super().__init__(entry_id)
        self.__phrase_readings = load_daijirin2_phrase_readings()

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
        self._delete_unused_nodes(soup)
        text = soup.find("句表記").text
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
        """Return a list of strings described by ＝ notation.
        eg. "同じ穴の＝狢（＝狐・狸）" -> [
            "同じ穴の狢", "同じ穴の狐", "同じ穴の狸"
        ]
        eg. "聞くは＝一時（＝一旦）の恥、聞かぬは＝末代（＝一生）の恥" -> [
            "聞くは一時の恥、聞かぬは末代の恥",
            "聞くは一時の恥、聞かぬは一生の恥",
            "聞くは一旦の恥、聞かぬは末代の恥",
            "聞くは一旦の恥、聞かぬは一生の恥"
        ]
        """
        group_pattern = r"([^＝]+)(＝([^（]+)（＝([^（]+)）)?"
        groups = re.findall(group_pattern, expression)
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
