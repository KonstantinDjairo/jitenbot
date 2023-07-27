import re
from bs4 import BeautifulSoup

from bot.data import get_adobe_glyph


def preprocess_page(page):
    soup = BeautifulSoup(page, features="xml")
    __replace_glyph_codes(soup)
    page = __strip_page(soup)
    return page


def __replace_glyph_codes(soup):
    for el in soup.find_all("glyph"):
        m = re.search(r"^glyph:([0-9]+);?$", el.attrs["style"])
        code = int(m.group(1))
        for geta in el.find_all(string="〓"):
            glyph = get_adobe_glyph(code)
            geta.replace_with(glyph)


def __strip_page(soup):
    koumoku = soup.find(["項目"])
    if koumoku is not None:
        return koumoku.decode()
    else:
        raise Exception(f"Primary 項目 not found in page:\n{soup.prettify()}")
