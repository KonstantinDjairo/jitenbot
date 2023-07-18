from bs4 import BeautifulSoup
import bot.entries.expressions as Expressions
import bot.soup as Soup
from bot.entries.entry import Entry
from bot.data import load_phrase_readings
from bot.entries.sankoku8_preprocess import preprocess_page


class _BaseSankoku8Entry(Entry):
    def __init__(self, target, entry_id):
        super().__init__(target, entry_id)
        self.children = []
        self.phrases = []
        self._hyouki_name = "表記"
        self._midashi_name = None
        self._midashi_kana_name = None

    def get_global_identifier(self):
        parent_part = format(self.entry_id[0], '06')
        child_part = hex(self.entry_id[1]).lstrip('0x').zfill(4).upper()
        return f"@{self.target.value}-{parent_part}-{child_part}"

    def set_page(self, page):
        page = self.__decompose_subentries(page)
        self._page = page

    def get_page_soup(self):
        soup = BeautifulSoup(self._page, "xml")
        return soup

    def _get_headwords(self):
        soup = self.get_page_soup()
        self._delete_unused_nodes(soup)
        readings = self._find_readings(soup)
        expressions = self._find_expressions(soup)
        headwords = {}
        for reading in readings:
            headwords[reading] = []
        if len(readings) == 1:
            reading = readings[0]
            if soup.find(self._midashi_name).find(self._hyouki_name) is None:
                headwords[reading].append(reading)
            for exp in expressions:
                if exp not in headwords[reading]:
                    headwords[reading].append(exp)
        elif len(readings) > 1 and len(expressions) == 0:
            for reading in readings:
                headwords[reading].append(reading)
        elif len(readings) > 1 and len(expressions) == 1:
            if soup.find(self._midashi_name).find(self._hyouki_name) is None:
                for reading in readings:
                    headwords[reading].append(reading)
            expression = expressions[0]
            for reading in readings:
                if expression not in headwords[reading]:
                    headwords[reading].append(expression)
        elif len(readings) > 1 and len(expressions) == len(readings):
            if soup.find(self._midashi_name).find(self._hyouki_name) is None:
                for reading in readings:
                    headwords[reading].append(reading)
            for idx, reading in enumerate(readings):
                exp = expressions[idx]
                if exp not in headwords[reading]:
                    headwords[reading].append(exp)
        else:
            raise Exception()  # shouldn't happen
        return headwords

    def _add_variant_expressions(self, headwords):
        for expressions in headwords.values():
            Expressions.add_variant_kanji(expressions)
            Expressions.add_fullwidth(expressions)
            Expressions.remove_iteration_mark(expressions)
            Expressions.add_iteration_mark(expressions)

    def get_part_of_speech_tags(self):
        if self._part_of_speech_tags is not None:
            return self._part_of_speech_tags
        self._part_of_speech_tags = []
        soup = self.get_page_soup()
        for midashi in soup.find_all([self._midashi_name, "見出部要素"]):
            pos_group = midashi.find("品詞G")
            if pos_group is None:
                continue
            for tag in pos_group.find_all("a"):
                if tag.text not in self._part_of_speech_tags:
                    self._part_of_speech_tags.append(tag.text)
        return self._part_of_speech_tags

    def _find_expressions(self, soup):
        expressions = []
        for hyouki in soup.find_all(self._hyouki_name):
            for expression in parse_hyouki_soup(hyouki, [""]):
                expressions.append(expression)
        return expressions

    def _find_readings(self, soup):
        midasi_kana = soup.find(self._midashi_kana_name)
        readings = parse_hyouki_soup(midasi_kana, [""])
        return readings

    def __decompose_subentries(self, page):
        soup = BeautifulSoup(page, features="xml")
        subentry_parameters = [
            [Sankoku8ChildEntry, ["子項目"], self.children],
            [Sankoku8PhraseEntry, ["句項目"], self.phrases],
        ]
        for x in subentry_parameters:
            subentry_class, tags, subentry_list = x
            for tag in tags:
                tag_soup = soup.find(tag)
                while tag_soup is not None:
                    tag_soup.name = "項目"
                    subentry_id = self.id_string_to_entry_id(tag_soup.attrs["id"])
                    self.SUBENTRY_ID_TO_ENTRY_ID[subentry_id] = self.entry_id
                    subentry = subentry_class(self.target, subentry_id)
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
        """Remove extra markup elements that appear in the entry
        headword line which are not part of the entry headword"""
        unused_nodes = [
            "語構成", "平板", "アクセント", "表外字マーク", "表外音訓マーク",
            "アクセント分節", "活用分節", "ルビG", "分書"
        ]
        for name in unused_nodes:
            Soup.delete_soup_nodes(soup, name)


class Sankoku8Entry(_BaseSankoku8Entry):
    def __init__(self, target, page_id):
        entry_id = (page_id, 0)
        super().__init__(target, entry_id)
        self._midashi_name = "見出部"
        self._midashi_kana_name = "見出仮名"

    def set_page(self, page):
        page = preprocess_page(page)
        super().set_page(page)


class Sankoku8ChildEntry(_BaseSankoku8Entry):
    def __init__(self, target, page_id):
        super().__init__(target, page_id)
        self._midashi_name = "子見出部"
        self._midashi_kana_name = "子見出仮名"


class Sankoku8PhraseEntry(_BaseSankoku8Entry):
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


def parse_hyouki_soup(soup, base_exps):
    omitted_characters = [
        "／", "〈", "〉", "（", "）", "⦅", "⦆", "：", "…"
    ]
    exps = base_exps.copy()
    for child in soup.children:
        new_exps = []
        if child.name == "言換G":
            for alt in child.find_all("言換"):
                parts = parse_hyouki_soup(alt, [""])
                for exp in exps:
                    for part in parts:
                        new_exps.append(exp + part)
        elif child.name == "補足表記":
            alt1 = child.find("表記対象")
            alt2 = child.find("表記内容G")
            parts1 = parse_hyouki_soup(alt1, [""])
            parts2 = parse_hyouki_soup(alt2, [""])
            for exp in exps:
                for part in parts1:
                    new_exps.append(exp + part)
                for part in parts2:
                    new_exps.append(exp + part)
        elif child.name == "省略":
            parts = parse_hyouki_soup(child, [""])
            for exp in exps:
                new_exps.append(exp)
                for part in parts:
                    new_exps.append(exp + part)
        elif child.name is not None:
            new_exps = parse_hyouki_soup(child, exps)
        else:
            text = child.text
            for char in omitted_characters:
                text = text.replace(char, "")
            for exp in exps:
                new_exps.append(exp + text)
        exps = new_exps.copy()
    return exps


def parse_hyouki_pattern(pattern):
    replacements = {
        "（": "<省略>（",
        "）": "）</省略>",
        "｛": "<補足表記><表記対象>",
        "・": "</表記対象><表記内容G>（<表記内容>",
        "｝": "</表記内容>）</表記内容G></補足表記>",
        "〈": "<言換G>〈<言換>",
        "／": "</言換>／<言換>",
        "〉": "</言換>〉</言換G>",
        "⦅": "<補足表記><表記対象>",
        "＼": "</表記対象><表記内容G>⦅<表記内容>",
        "⦆": "</表記内容>⦆</表記内容G></補足表記>",
    }
    markup = f"<span>{pattern}</span>"
    for key, val in replacements.items():
        markup = markup.replace(key, val)
    soup = BeautifulSoup(markup, "xml")
    hyouki_soup = soup.find("span")
    exps = parse_hyouki_soup(hyouki_soup, [""])
    return exps
