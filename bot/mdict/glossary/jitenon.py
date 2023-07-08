# pylint: disable=too-few-public-methods

import re


class JitenonGlossary():
    def __init__(self):
        self._id_pattern = None
        self._expression_header = None

    def _replace_punctuation(self, soup):
        punctuation = {
            "/": "／",
            ",": "、",
        }
        for el in soup.find_all(string=True):
            text = el.text
            for old, new in punctuation.items():
                text = text.replace(old, new)
            el.replace_with(text)

    def _add_internal_links(self, soup, entry):
        for el in soup.find_all("a"):
            href = el.attrs["href"]
            m = re.search(self._id_pattern, href)
            if m is not None:
                ref_entry_id = int(m.group(1))
                ref_entry = entry.ID_TO_ENTRY[ref_entry_id]
                gid = ref_entry.get_global_identifier()
                el.attrs["href"] = f"entry://{gid}"
            elif re.match(r"^(?:https?:|\?)[\w\W]*", href):
                pass
            else:
                raise Exception(f"Invalid href format: {href}")

    def _decompose_table_rows(self, soup, entry):
        for tr in soup.find_all("tr"):
            if tr.find("th") is None:
                continue
            elif tr.th.text == self._expression_header:
                tr.decompose()
            elif tr.th.text == "読み方":
                if self._do_display_yomikata_in_headword(entry):
                    tr.decompose()
            elif tr.th.text == "意味":
                definition = tr.td
                definition.name = "div"
                definition.attrs["class"] = "意味"
                soup.body.insert(0, definition)
                tr.decompose()
        if soup.find("tr") is None:
            soup.table.decompose()

    def _insert_headword_line(self, soup, entry):
        headword_line = soup.new_tag("div")
        headword_line.attrs["class"] = "見出し"
        if self._do_display_yomikata_in_headword(entry):
            reading = soup.new_tag("span")
            reading.attrs["class"] = "読み方"
            reading.string = entry.yomikata
            headword_line.append(reading)
        expression = soup.new_tag("span")
        expression.attrs["class"] = self._expression_header
        expression.string = f"【{entry.expression}】"
        headword_line.append(expression)
        soup.body.insert(0, headword_line)

    def _do_display_yomikata_in_headword(self, entry):
        if not re.match(r"^[ぁ-ヿ、]+$", entry.yomikata):
            return False
        elif len(entry.yomikata) > 10:
            return False
        else:
            return True


class JitenonKokugoGlossary(JitenonGlossary):
    def __init__(self):
        super().__init__()
        self._expression_header = "言葉"
        self._id_pattern = r"kokugo.jitenon.jp/word/p([0-9]+)$"

    def make_glossary(self, entry, media_dir):
        soup = entry.get_page_soup()
        self._remove_antonym_list_item(soup)
        self._replace_number_icons(soup, media_dir)
        self._replace_punctuation(soup)
        self._add_internal_links(soup, entry)
        self._decompose_table_rows(soup, entry)
        self._insert_headword_line(soup, entry)
        glossary = soup.body.prettify()
        return glossary

    def _remove_antonym_list_item(self, soup):
        for el in soup.find_all("li"):
            if el.text == "対義語辞典":
                el.decompose()

    def _replace_number_icons(self, soup, media_dir):
        for el in soup.find_all("img"):
            alt = el.attrs["alt"]
            text = re.search(r"[０-９]+", alt).group(0)
            el.name = "span"
            el.string = text
            del el.attrs["src"]
            del el.attrs["alt"]

    def _do_display_yomikata_in_headword(self, entry):
        return len(entry.yomikata) <= 10


class JitenonYojiGlossary(JitenonGlossary):
    def __init__(self):
        super().__init__()
        self._expression_header = "四字熟語"
        self._id_pattern = r"yoji.jitenon.jp/yoji.?/([0-9]+)\.html$"

    def make_glossary(self, entry, media_dir):
        soup = entry.get_page_soup()
        self._replace_punctuation(soup)
        self._add_internal_links(soup, entry)
        self._decompose_table_rows(soup, entry)
        self._insert_headword_line(soup, entry)
        glossary = soup.body.prettify()
        return glossary


class JitenonKotowazaGlossary(JitenonGlossary):
    def __init__(self):
        super().__init__()
        self._expression_header = "言葉"
        self._id_pattern = r"kotowaza.jitenon.jp/kotowaza/([0-9]+)\.php$"

    def make_glossary(self, entry, media_dir):
        soup = entry.get_page_soup()
        self._replace_punctuation(soup)
        self._add_internal_links(soup, entry)
        self._decompose_table_rows(soup, entry)
        self._insert_headword_line(soup, entry)
        glossary = soup.body.prettify()
        return glossary
