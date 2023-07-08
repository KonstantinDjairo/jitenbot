import re
from abc import abstractmethod
from datetime import datetime, date
from bs4 import BeautifulSoup

from bot.entries.entry import Entry
import bot.entries.expressions as Expressions


class _JitenonEntry(Entry):
    def __init__(self, target, entry_id):
        super().__init__(target, entry_id)
        self.expression = ""
        self.yomikata = ""
        self.definition = ""
        self.other_forms = []
        self.modified_date = date(1970, 1, 1)
        self.attribution = ""

    def get_global_identifier(self):
        return f"@{self.target.value}-{format(self.entry_id, '06')}"

    def set_page(self, page):
        soup = BeautifulSoup(page, features="html5lib")
        self.__set_modified_date(page)
        self.__set_attribution(soup)
        table = soup.find(class_="kanjirighttb")
        if table is None:
            raise ValueError("Error: table data not found in page.")
        rows = table.find("tbody").find_all("tr")
        colname = ""
        for row in rows:
            colname = row.th.text if row.th is not None else colname
            colval = self.__clean_text(row.td.text)
            self.__set_column(colname, colval)
        self._page = table.decode()

    def get_page_soup(self):
        soup = BeautifulSoup(self._page, "html5lib")
        return soup

    def get_part_of_speech_tags(self):
        # Jitenon doesn't have any
        return []

    def _get_headwords(self):
        headwords = {}
        for reading in self._get_readings():
            headwords[reading] = [self.expression]
        other_form_headwords = self._other_form_headwords()
        for reading, expressions in other_form_headwords.items():
            if reading not in headwords:
                headwords[reading] = []
            for expression in expressions:
                if expression not in headwords[reading]:
                    headwords[reading].append(expression)
        return headwords

    @abstractmethod
    def _get_column_map(self):
        pass

    def __set_modified_date(self, page):
        m = re.search(r"\"dateModified\": \"(\d{4}-\d{2}-\d{2})", page)
        if m is None:
            return
        modified_date = datetime.strptime(m.group(1), '%Y-%m-%d').date()
        self.modified_date = modified_date

    def __set_attribution(self, soup):
        attribution = soup.find(class_="copyright")
        if attribution is not None:
            self.attribution = soup.find(class_="copyright").text
        else:
            self.attribution = ""

    def __set_column(self, colname, colval):
        column_map = self._get_column_map()
        attr_name = column_map[colname]
        attr_value = getattr(self, attr_name)
        if isinstance(attr_value, str):
            setattr(self, attr_name, colval)
        elif isinstance(attr_value, list):
            if len(attr_value) == 0:
                setattr(self, attr_name, [colval])
            else:
                attr_value.append(colval)

    def _get_readings(self):
        yomikata = self.yomikata
        m = re.search(r"^[ぁ-ヿ、]+$", yomikata)
        if m:
            return [yomikata]
        m = re.search(r"^([ぁ-ヿ、]+)※", yomikata)
        if m:
            return [m.group(1)]
        m = re.search(r"^[ぁ-ヿ、]+（[ぁ-ヿ、]）[ぁ-ヿ、]+$", yomikata)
        if m:
            return Expressions.expand_abbreviation(yomikata)
        m = re.search(r"^([ぁ-ヿ、]+)（([ぁ-ヿ/\s、]+)）$", yomikata)
        if m:
            yomikatas = [m.group(1)]
            alts = m.group(2).split("/")
            for alt in alts:
                yomikatas.append(alt.strip())
            return yomikatas
        print(f"Invalid 読み方 format: {self.yomikata}\n{self}\n")
        return [""]

    def _other_form_headwords(self):
        other_form_headwords = {}
        for val in self.other_forms:
            m = re.search(r"^([^（]+)（([ぁ-ヿ、]+)）$", val)
            if not m:
                print(f"Invalid 異形 format: {val}\n{self}\n")
                continue
            expression = m.group(1)
            reading = m.group(2)
            if reading not in other_form_headwords:
                other_form_headwords[reading] = []
            if expression not in other_form_headwords[reading]:
                other_form_headwords[reading].append(expression)
        return other_form_headwords

    @staticmethod
    def __clean_text(text):
        text = text.replace("\n", "")
        text = text.replace(",", "、")
        text = text.replace(" ", "")
        text = text.strip()
        return text

    def __str__(self):
        column_map = self._get_column_map()
        colvals = [str(self.entry_id)]
        for attr_name in column_map.values():
            attr_val = getattr(self, attr_name)
            if isinstance(attr_val, str):
                colvals.append(attr_val)
            elif isinstance(attr_val, list):
                colvals.append("；".join(attr_val))
        return ",".join(colvals)


class JitenonYojiEntry(_JitenonEntry):
    def __init__(self, target, entry_id):
        super().__init__(target, entry_id)
        self.origin = ""
        self.kanken_level = ""
        self.category = ""
        self.related_expressions = []

    def _get_column_map(self):
        return {
            "四字熟語": "expression",
            "読み方":   "yomikata",
            "意味":     "definition",
            "異形":     "other_forms",
            "出典":     "origin",
            "漢検級":   "kanken_level",
            "場面用途": "category",
            "類義語":   "related_expressions",
        }

    def _add_variant_expressions(self, headwords):
        for expressions in headwords.values():
            Expressions.add_variant_kanji(expressions)


class JitenonKotowazaEntry(_JitenonEntry):
    def __init__(self, target, entry_id):
        super().__init__(target, entry_id)
        self.origin = ""
        self.example = ""
        self.related_expressions = []

    def _get_column_map(self):
        return {
            "言葉":   "expression",
            "読み方": "yomikata",
            "意味":   "definition",
            "異形":   "other_forms",
            "出典":   "origin",
            "例文":   "example",
            "類句":   "related_expressions",
        }

    def _get_headwords(self):
        if self.expression == "金棒引き・鉄棒引き":
            headwords = {
                "かなぼうひき": ["金棒引き", "鉄棒引き"]
            }
        else:
            headwords = super()._get_headwords()
        return headwords

    def _add_variant_expressions(self, headwords):
        for expressions in headwords.values():
            Expressions.add_variant_kanji(expressions)
            Expressions.add_fullwidth(expressions)


class JitenonKokugoEntry(_JitenonEntry):
    def __init__(self, target, entry_id):
        super().__init__(target, entry_id)
        self.example = ""
        self.alt_expression = ""
        self.antonym = ""
        self.attachments = ""
        self.compounds = ""
        self.related_words = ""

    def _get_column_map(self):
        return {
            "言葉":   "expression",
            "読み方": "yomikata",
            "意味":   "definition",
            "例文":   "example",
            "別表記": "alt_expression",
            "対義語": "antonym",
            "活用":   "attachments",
            "用例":   "compounds",
            "類語":   "related_words",
        }

    def _get_headwords(self):
        headwords = {}
        for reading in self.yomikata.split("・"):
            if reading not in headwords:
                headwords[reading] = []
            for expression in self.expression.split("・"):
                headwords[reading].append(expression)
            if self.alt_expression.strip() != "":
                for expression in self.alt_expression.split("・"):
                    headwords[reading].append(expression)
        return headwords

    def _add_variant_expressions(self, headwords):
        for expressions in headwords.values():
            Expressions.add_variant_kanji(expressions)
            Expressions.add_fullwidth(expressions)
            Expressions.remove_iteration_mark(expressions)
            Expressions.add_iteration_mark(expressions)
