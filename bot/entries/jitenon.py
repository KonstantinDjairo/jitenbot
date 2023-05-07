import re
from datetime import datetime, date
from bs4 import BeautifulSoup

from bot.entries.entry import Entry
import bot.entries.expressions as Expressions


class _JitenonEntry(Entry):
    ID_TO_ENTRY = {}

    def __init__(self, entry_id):
        super().__init__(entry_id)
        if entry_id not in self.ID_TO_ENTRY:
            self.ID_TO_ENTRY[entry_id] = self
        else:
            raise Exception(f"Duplicate entry ID: {entry_id}")
        self.modified_date = date(1970, 1, 1)
        self.attribution = ""
        for column in self._COLUMNS.values():
            setattr(self, column[0], column[1])

    def set_page(self, page):
        soup = BeautifulSoup(page, features="html5lib")
        self.__set_modified_date(page)
        self.attribution = soup.find(class_="copyright").text
        table = soup.find(class_="kanjirighttb")
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

    def get_headwords(self):
        if self._headwords is not None:
            return self._headwords
        self._set_headwords()
        self._set_variant_headwords()
        return self._headwords

    def get_part_of_speech_tags(self):
        # Jitenon doesn't have any
        return []

    def _set_headwords(self):
        headwords = {}
        for yomikata in self._yomikatas():
            headwords[yomikata] = [self.expression]
        ikei_headwords = self._ikei_headwords()
        for reading, expressions in ikei_headwords.items():
            if reading not in headwords:
                headwords[reading] = []
            for expression in expressions:
                if expression not in headwords[reading]:
                    headwords[reading].append(expression)
        self._headwords = headwords

    def __set_modified_date(self, page):
        m = re.search(r"\"dateModified\": \"(\d{4}-\d{2}-\d{2})", page)
        if not m:
            return
        date = datetime.strptime(m.group(1), '%Y-%m-%d').date()
        self.modified_date = date

    def __set_column(self, colname, colval):
        attr_name = self._COLUMNS[colname][0]
        attr_value = getattr(self, attr_name)
        if isinstance(attr_value, str):
            setattr(self, attr_name, colval)
        elif isinstance(attr_value, list):
            if len(attr_value) == 0:
                setattr(self, attr_name, [colval])
            else:
                attr_value.append(colval)

    def _yomikatas(self):
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

    def _ikei_headwords(self):
        ikei_headwords = {}
        for val in self.ikei:
            m = re.search(r"^([^（]+)（([ぁ-ヿ、]+)）$", val)
            if not m:
                print(f"Invalid 異形 format: {val}\n{self}\n")
                continue
            expression = m.group(1)
            reading = m.group(2)
            if reading not in ikei_headwords:
                ikei_headwords[reading] = []
            if expression not in ikei_headwords[reading]:
                ikei_headwords[reading].append(expression)
        return ikei_headwords

    @staticmethod
    def __clean_text(text):
        text = text.replace("\n", "")
        text = text.replace(",", "、")
        text = text.replace(" ", "")
        text = text.strip()
        return text

    def __str__(self):
        colvals = [str(self.entry_id)]
        for attr in self._COLUMNS.values():
            attr_val = getattr(self, attr[0])
            if isinstance(attr_val, str):
                colvals.append(attr_val)
            elif isinstance(attr_val, list):
                colvals.append("；".join(attr_val))
        return ",".join(colvals)


class JitenonYojiEntry(_JitenonEntry):
    _COLUMNS = {
        "四字熟語": ["expression", ""],
        "読み方":   ["yomikata", ""],
        "意味":     ["imi", ""],
        "出典":     ["shutten", ""],
        "漢検級":   ["kankenkyuu", ""],
        "場面用途": ["bamenyouto", ""],
        "異形":     ["ikei", []],
        "類義語":   ["ruigigo", []],
    }

    def __init__(self, entry_id):
        super().__init__(entry_id)

    def _set_variant_headwords(self):
        for expressions in self._headwords.values():
            Expressions.add_variant_kanji(expressions)


class JitenonKotowazaEntry(_JitenonEntry):
    _COLUMNS = {
        "言葉":   ["expression", ""],
        "読み方": ["yomikata", ""],
        "意味":   ["imi", ""],
        "出典":   ["shutten", ""],
        "例文":   ["reibun", ""],
        "異形":   ["ikei", []],
        "類句":   ["ruiku", []],
    }

    def __init__(self, entry_id):
        super().__init__(entry_id)

    def _set_headwords(self):
        if self.expression == "金棒引き・鉄棒引き":
            self._headwords = {
                "かなぼうひき": ["金棒引き", "鉄棒引き"]
            }
        else:
            super()._set_headwords()

    def _set_variant_headwords(self):
        for expressions in self._headwords.values():
            Expressions.add_variant_kanji(expressions)
            Expressions.add_fullwidth(expressions)


class JitenonKokugoEntry(_JitenonEntry):
    _COLUMNS = {
        "言葉":   ["expression", ""],
        "読み方": ["yomikata", ""],
        "意味":   ["imi", ""],
        "例文":   ["reibun", ""],
        "別表記": ["betsuhyouki", ""],
        "対義語": ["taigigo", ""],
        "活用":   ["katsuyou", ""],
        "用例":   ["yourei", ""],
        "類語":   ["ruigo", ""],
    }

    def __init__(self, entry_id):
        super().__init__(entry_id)

    def _set_headwords(self):
        headwords = {}
        for reading in self.yomikata.split("・"):
            if reading not in headwords:
                headwords[reading] = []
            for expression in self.expression.split("・"):
                headwords[reading].append(expression)
            if self.betsuhyouki.strip() != "":
                for expression in self.betsuhyouki.split("・"):
                    headwords[reading].append(expression)
        self._headwords = headwords

    def _set_variant_headwords(self):
        for expressions in self._headwords.values():
            Expressions.add_variant_kanji(expressions)
            Expressions.add_fullwidth(expressions)
            Expressions.remove_iteration_mark(expressions)
            Expressions.add_iteration_mark(expressions)
