import re
from datetime import datetime, date
from bs4 import BeautifulSoup

import bot.expressions as Expressions


class JitenonEntry:
    def __init__(self, entry_id):
        self.entry_id = entry_id
        self.markup = ""
        self.modified_date = date(1970, 1, 1)
        self.attribution = ""
        for column in self.COLUMNS.values():
            setattr(self, column[0], column[1])
        self._headwords = None

    def set_markup(self, path):
        with open(path, "r") as f:
            html = f.read()
        soup = BeautifulSoup(html, features="html5lib")
        self.__set_modified_date(html)
        self.attribution = soup.find(class_="copyright").text
        table = soup.find(class_="kanjirighttb")
        rows = table.find("tbody").find_all("tr")
        colname = ""
        for row in rows:
            colname = row.th.text if row.th is not None else colname
            colval = self.__clean_text(row.td.text)
            self.__set_column(colname, colval)
        self.markup = table.decode()

    def get_headwords(self):
        if self._headwords is not None:
            return self._headwords
        self._set_headwords()
        return self._headwords

    def _set_headwords(self):
        headwords = {}
        for yomikata in self.__yomikatas():
            headwords[yomikata] = [self.expression]
        ikei_headwords = self.__ikei_headwords()
        for reading, expressions in ikei_headwords.items():
            if reading not in headwords:
                headwords[reading] = []
            for expression in expressions:
                if expression not in headwords[reading]:
                    headwords[reading].append(expression)
        self._headwords = headwords

    def __set_modified_date(self, html):
        m = re.search(r"\"dateModified\": \"(\d{4}-\d{2}-\d{2})", html)
        if not m:
            return
        date = datetime.strptime(m.group(1), '%Y-%m-%d').date()
        self.modified_date = date

    def __set_column(self, colname, colval):
        attr_name = self.COLUMNS[colname][0]
        attr_value = getattr(self, attr_name)
        if isinstance(attr_value, str):
            setattr(self, attr_name, colval)
        elif isinstance(attr_value, list):
            if len(attr_value) == 0:
                setattr(self, attr_name, [colval])
            else:
                attr_value.append(colval)

    def __yomikatas(self):
        yomikata = self.yomikata
        m = re.search(r"^[ぁ-ヿ、]+$", yomikata)
        if m:
            return [yomikata]
        m = re.search(r"^([ぁ-ヿ、]+)※", yomikata)
        if m:
            return [m.group(1)]
        m = re.search(r"^[ぁ-ヿ、]+（[ぁ-ヿ、]）[ぁ-ヿ、]+$", yomikata)
        if m:
            return Expressions.expand_shouryaku(yomikata)
        m = re.search(r"^([ぁ-ヿ、]+)（([ぁ-ヿ/\s、]+)）$", yomikata)
        if m:
            yomikatas = [m.group(1)]
            alts = m.group(2).split("/")
            for alt in alts:
                yomikatas.append(alt.strip())
            return yomikatas
        print(f"Invalid 読み方 format: {self.yomikata}\n{self}\n")
        return [""]

    def __ikei_headwords(self):
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
        for attr in self.COLUMNS.values():
            attr_val = getattr(self, attr[0])
            if isinstance(attr_val, str):
                colvals.append(attr_val)
            elif isinstance(attr_val, list):
                colvals.append("；".join(attr_val))
        return ",".join(colvals)


class JitenonYojiEntry(JitenonEntry):
    COLUMNS = {
        "四字熟語": ["expression", ""],
        "読み方":   ["yomikata", ""],
        "意味":     ["imi", ""],
        "出典":     ["shutten", ""],
        "漢検級":   ["kankenkyuu", ""],
        "場面用途": ["bamenyouto", ""],
        "異形":     ["ikei", []],
        "類義語":   ["ruigigo", []],
    }

    def __init__(self, sequence):
        super().__init__(sequence)


class JitenonKotowazaEntry(JitenonEntry):
    COLUMNS = {
        "言葉":   ["expression", ""],
        "読み方": ["yomikata", ""],
        "意味":   ["imi", ""],
        "出典":   ["shutten", ""],
        "例文":   ["reibun", ""],
        "異形":   ["ikei", []],
        "類句":   ["ruiku", []],
    }

    def __init__(self, sequence):
        super().__init__(sequence)

    def _set_headwords(self):
        if self.expression == "金棒引き・鉄棒引き":
            self._headwords = {
                "かなぼうひき": ["金棒引き", "鉄棒引き"]
            }
        else:
            super()._set_headwords()
