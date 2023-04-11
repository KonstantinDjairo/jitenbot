import re
from datetime import datetime, date
from bs4 import BeautifulSoup

import bot.yomichan.html_gloss as YomichanGloss
import bot.util as Util


class Jitenon:
    def __init__(self, sequence):
        self.sequence = sequence
        self.yomichan_glossary = [""]
        self.modified_date = date(1970, 1, 1)
        self.attribution = ""
        for column in self.columns.values():
            setattr(self, column[0], column[1])

    def add_document(self, html):
        yoji_soup = BeautifulSoup(html, features="html5lib")
        self.__set_modified_date(html)
        self.attribution = yoji_soup.find(class_="copyright").text
        table = yoji_soup.find(class_="kanjirighttb")
        rows = table.find("tbody").find_all("tr")
        colname = ""
        for row in rows:
            colname = row.th.text if row.th is not None else colname
            colval = self.__clean(row.td.text)
            self.__set_column(colname, colval)
        self.__prepare_yomichan_soup(table)
        gloss = YomichanGloss.make_gloss(table)
        self.yomichan_glossary = [gloss]

    def __set_modified_date(self, html):
        m = re.search(r"\"dateModified\": \"(\d{4}-\d{2}-\d{2})", html)
        if not m:
            return
        date = datetime.strptime(m.group(1), '%Y-%m-%d').date()
        self.modified_date = date

    def __clean(self, text):
        text = text.replace("\n", "")
        text = text.replace(",", "、")
        text = text.replace(" ", "")
        text = text.strip()
        return text

    def __set_column(self, colname, colval):
        attr_name = self.columns[colname][0]
        attr_value = getattr(self, attr_name)
        if isinstance(attr_value, str):
            setattr(self, attr_name, colval)
        elif isinstance(attr_value, list):
            if len(attr_value) == 0:
                setattr(self, attr_name, [colval])
            else:
                attr_value.append(colval)

    def __prepare_yomichan_soup(self, soup):
        patterns = [
            r"^(.+)（[ぁ-ヿ、\s]+）$",
            r"^(.+)（[ぁ-ヿ、\s]+（[ぁ-ヿ、\s]）[ぁ-ヿ、\s]+）$"
        ]
        for a in soup.find_all("a"):
            for pattern in patterns:
                m = re.search(pattern, a.text)
                if m:
                    a['href'] = f"?query={m.group(1)}&wildcards=off"
                    break
        for p in soup.find_all("p"):
            p.name = "span"
        for th in soup.find_all("th"):
            th['style'] = "vertical-align: middle; text-align: center;"

    def _headwords(self):
        words = []
        for yomikata in self.__yomikatas():
            headword = [self.expression, yomikata]
            if headword in words:
                words.remove(headword)
            words.append(headword)
        for headword in self.__ikei_headwords():
            if headword in words:
                words.remove(headword)
            words.append(headword)
        return words

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
            return Util.expand_shouryaku(yomikata)
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
        ikei_headwords = []
        for val in self.ikei:
            m = re.search(r"^([^（]+)（([ぁ-ヿ、]+)）$", val)
            if m:
                headword = [m.group(1), m.group(2)]
                ikei_headwords.append(headword)
            else:
                print(f"Invalid 異形 format: {val}\n{self}\n")
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
