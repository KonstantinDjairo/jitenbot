import re

import yomichan as Yomichan
import util as Util


class JitenonYoji:
    columns = {
        "四字熟語": ["yojijukugo", ""],
        "読み方":   ["yomikata", ""],
        "意味":     ["imi", ""],
        "出典":     ["shutten", ""],
        "漢検級":   ["kankenkyuu", ""],
        "場面用途": ["bamenyouto", ""],
        "異形":     ["ikei", []],
        "類義語":   ["ruigigo", []],
    }

    def __init__(self, sequence):
        self.sequence = sequence
        self.yomichan_glossary = [""]
        for column in self.columns.values():
            setattr(self, column[0], column[1])

    def add_soup(self, yoji_soup):
        table = yoji_soup.find(class_="kanjirighttb")
        rows = table.find("tbody").find_all("tr")
        colname = ""
        for row in rows:
            colname = row.th.text if row.th is not None else colname
            colval = row.td.decode_contents()
            self.__set_column(colname, colval)
        self.yomichan_glossary = [Yomichan.soup_to_gloss(table)]

    def yomichan_terms(self):
        terms = []
        for idx, headword in enumerate(self.__headwords()):
            (yoji, reading) = headword
            definition_tags = None
            inflection_rules = ""
            score = -idx
            glossary = self.yomichan_glossary
            sequence = self.sequence
            term_tags = ""
            term = [
                yoji, reading, definition_tags, inflection_rules,
                score, glossary, sequence, term_tags
            ]
            terms.append(term)
        return terms

    def __set_column(self, colname, colval):
        attr_name = self.columns[colname][0]
        attr_value = getattr(self, attr_name)
        colval = colval.replace("\n", "").replace(",", "、").strip()
        if isinstance(attr_value, str):
            setattr(self, attr_name, colval)
        elif isinstance(attr_value, list):
            if len(attr_value) == 0:
                setattr(self, attr_name, [colval])
            else:
                attr_value.append(colval)
                setattr(self, attr_name, attr_value)

    def __headwords(self):
        words = []
        for yomikata in self.__yomikatas():
            headword = [self.yojijukugo, yomikata]
            if headword in words:
                words.remove(headword)
            words.append(headword)
        for headword in self.__ikei_headwords():
            if headword in words:
                words.remove(headword)
            words.append(headword)
        return words

    def __yomikatas(self):
        m = re.search(r"^[ぁ-ヿ]+$", self.yomikata)
        if m:
            return [self.yomikata]
        m = re.search(r"^([ぁ-ヿ]+)<br/>", self.yomikata)
        if m:
            return [m.group(1)]
        m = re.search(r"^[ぁ-ヿ]+（[ぁ-ヿ]）[ぁ-ヿ]+$", self.yomikata)
        if m:
            return Util.expand_shouryaku(self.yomikata)
        m = re.search(r"^([ぁ-ヿ]+)（([ぁ-ヿ/\s]+)）$", self.yomikata)
        if m:
            yomikatas = [m.group(1)]
            alts = m.group(2).split("/")
            for alt in alts:
                yomikatas.append(alt.strip())
            return yomikatas
        raise Exception(f"Invalid 読み方 format: {self.yomikata}\n{self}")

    def __ikei_headwords(self):
        ikei_headwords = []
        for val in self.ikei:
            m = re.search(r"^([^（]+)（([ぁ-ヿ]+)）$", val)
            if m:
                headword = [m.group(1), m.group(2)]
                ikei_headwords.append(headword)
            else:
                raise Exception(f"Invalid 異形 format: {val}\n{self}")
        return ikei_headwords

    def __str__(self):
        colvals = [str(self.sequence)]
        for attr in self.columns.values():
            attr_val = getattr(self, attr[0])
            if isinstance(attr_val, str):
                colvals.append(attr_val)
            elif isinstance(attr_val, list):
                colvals.append("；".join(attr_val))
        return ",".join(colvals)
