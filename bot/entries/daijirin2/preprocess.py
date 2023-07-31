import re
from bs4 import BeautifulSoup

from bot.data import get_adobe_glyph


__GAIJI = {
    "gaiji/DJRK0002.svg": "𦬇",
    "gaiji/U芸E0102.svg": "芸",
}


def preprocess_page(page):
    soup = BeautifulSoup(page, features="xml")
    __replace_glyph_codes(soup)
    __add_gaiji_alt_text(soup)
    __replace_halfwidth_braces(soup)
    page = __strip_page(soup)
    return page


def __replace_glyph_codes(soup):
    for el in soup.find_all(style=True):
        m = re.search(r"^glyph:([0-9]+);?$", el.attrs["style"])
        if not m:
            continue
        del el.attrs["style"]
        if el.has_attr("alt"):
            el.string = el.attrs["alt"]
            continue
        code = int(m.group(1))
        for geta in el.find_all(string="〓"):
            glyph = get_adobe_glyph(code)
            geta.replace_with(glyph)


def __add_gaiji_alt_text(soup):
    for gaiji in soup.find_all(class_="gaiji"):
        src = gaiji.attrs["src"] if gaiji.has_attr("src") else ""
        if src in __GAIJI:
            gaiji.attrs["alt"] = __GAIJI[src]


def __replace_halfwidth_braces(soup):
    for x in soup.find_all("送り仮名省略"):
        for el in x.find_all(string="("):
            el.replace_with("（")
        for el in x.find_all(string=")"):
            el.replace_with("）")


def __strip_page(soup):
    koumoku = soup.find("項目")
    if koumoku is None:
        raise Exception(f"Primary 項目 not found in page:\n{soup.prettify()}")
    return koumoku.decode()
