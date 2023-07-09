import re
import os
from bs4 import BeautifulSoup

import bot.yomichan.glossary.icons as Icons
from bot.yomichan.glossary.gloss import make_gloss


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
                expression = ref_entry.get_first_expression()
                el.attrs["href"] = f"?query={expression}&wildcards=off"
            elif re.match(r"^(?:https?:|\?)[\w\W]*", href):
                pass
            else:
                raise Exception(f"Invalid href format: {href}")

    def _convert_paragraphs(self, soup):
        for p in soup.find_all("p"):
            p.name = "div"

    def _style_table_headers(self, soup):
        for th in soup.find_all("th"):
            th['style'] = "vertical-align: middle; text-align: center;"

    def _unwrap_table_body(self, soup):
        if soup.find("tbody") is not None:
            soup.tbody.unwrap()

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
                soup.body.insert(0, definition)
                tr.decompose()
        if soup.find("tr") is None:
            soup.table.decompose()

    def _insert_headword_line(self, soup, entry):
        headword_line = soup.new_tag("span")
        if self._do_display_yomikata_in_headword(entry):
            headword_line.string = f"{entry.yomikata}【{entry.expression}】"
        else:
            headword_line.string = f"【{entry.expression}】"
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

    def make_glossary(self, entry, image_dir):
        soup = entry.get_page_soup()
        self._remove_antonym_list_item(soup)
        self._replace_number_icons(soup, image_dir)
        self._replace_punctuation(soup)
        self._add_internal_links(soup, entry)
        self._convert_paragraphs(soup)
        self._style_table_headers(soup)
        self._unwrap_table_body(soup)
        self._decompose_table_rows(soup, entry)
        self._insert_headword_line(soup, entry)
        gloss = make_gloss(soup.body)
        glossary = [gloss]
        return glossary

    def _remove_antonym_list_item(self, soup):
        for el in soup.find_all("li"):
            if el.text == "対義語辞典":
                el.decompose()

    def _replace_number_icons(self, soup, image_dir):
        for el in soup.find_all("img"):
            alt = el.attrs["alt"]
            text = re.search(r"[０-９]+", alt).group(0)
            filename = f"{text}-fill.svg"
            path = os.path.join(image_dir, filename)
            Icons.make_monochrome_fill_rectangle(path, text)
            ratio = Icons.calculate_ratio(path)
            img = BeautifulSoup("<img/>", "xml").img
            img.attrs = {
                "height": 1.0 if ratio > 1.0 else ratio,
                "width": ratio if ratio > 1.0 else 1.0,
                "sizeUnits": "em",
                "collapsible": False,
                "collapsed": False,
                "background": False,
                "appearance": "monochrome",
                "title": alt,
                "path": f"{os.path.basename(image_dir)}/{filename}",
            }
            el.name = "span"
            el.append(img)
            el.attrs["style"] = "margin-right: 0.25em;"

    def _do_display_yomikata_in_headword(self, entry):
        return len(entry.yomikata) <= 10


class JitenonYojiGlossary(JitenonGlossary):
    def __init__(self):
        super().__init__()
        self._expression_header = "四字熟語"
        self._id_pattern = r"yoji.jitenon.jp/yoji.?/([0-9]+)\.html$"

    def make_glossary(self, entry, image_dir):
        soup = entry.get_page_soup()
        self._replace_punctuation(soup)
        self._add_internal_links(soup, entry)
        self._convert_paragraphs(soup)
        self._style_table_headers(soup)
        self._unwrap_table_body(soup)
        self._decompose_table_rows(soup, entry)
        self._insert_headword_line(soup, entry)
        gloss = make_gloss(soup.body)
        glossary = [gloss]
        return glossary


class JitenonKotowazaGlossary(JitenonGlossary):
    def __init__(self):
        super().__init__()
        self._expression_header = "言葉"
        self._id_pattern = r"kotowaza.jitenon.jp/kotowaza/([0-9]+)\.php$"

    def make_glossary(self, entry, image_dir):
        soup = entry.get_page_soup()
        self._replace_punctuation(soup)
        self._add_internal_links(soup, entry)
        self._convert_paragraphs(soup)
        self._style_table_headers(soup)
        self._unwrap_table_body(soup)
        self._decompose_table_rows(soup, entry)
        self._insert_headword_line(soup, entry)
        gloss = make_gloss(soup.body)
        glossary = [gloss]
        return glossary
