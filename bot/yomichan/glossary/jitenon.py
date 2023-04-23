import re
from bs4 import BeautifulSoup

from bot.yomichan.glossary.gloss import make_gloss


def make_glossary(entry):
    soup = BeautifulSoup(entry.markup, "html5lib")
    __replace_punctuation(soup)
    __add_internal_links(soup)
    __convert_paragraphs(soup)
    __style_table_headers(soup)
    __unwrap_table_body(soup)
    __decompose_table_rows(soup, entry)
    __insert_headword_line(soup, entry)
    gloss = make_gloss(soup.body)
    glossary = [gloss]
    return glossary


def __replace_punctuation(soup):
    punctuation = {
        "/": "／",
        ",": "、",
    }
    for el in soup.find_all(string=True):
        text = el.text
        for old, new in punctuation.items():
            text = text.replace(old, new)
        el.replace_with(text)


def __add_internal_links(soup):
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


def __convert_paragraphs(soup):
    for p in soup.find_all("p"):
        p.name = "span"


def __style_table_headers(soup):
    for th in soup.find_all("th"):
        th['style'] = "vertical-align: middle; text-align: center;"


def __unwrap_table_body(soup):
    if soup.find("tbody") is not None:
        soup.tbody.unwrap()


def __decompose_table_rows(soup, entry):
    for tr in soup.find_all("tr"):
        if tr.find("th") is None:
            continue
        elif tr.th.text in ["四字熟語", "言葉"]:
            tr.decompose()
        elif tr.th.text == "読み方":
            if __do_display_yomikata_in_headword(entry):
                tr.decompose()
        elif tr.th.text == "意味":
            imi = tr.td
            imi.name = "div"
            soup.body.insert(0, imi)
            tr.decompose()
    if soup.find("tr") is None:
        soup.table.decompose()


def __insert_headword_line(soup, entry):
    headword_line = soup.new_tag("span")
    if __do_display_yomikata_in_headword(entry):
        headword_line.string = f"{entry.yomikata}【{entry.expression}】"
    else:
        headword_line.string = f"【{entry.expression}】"
    soup.body.insert(0, headword_line)


def __do_display_yomikata_in_headword(entry):
    if not re.match(r"^[ぁ-ヿ、]+$", entry.yomikata):
        return False
    elif len(entry.yomikata) > 10:
        return False
    else:
        return True
