import re
from bs4 import BeautifulSoup

from bot.data import get_adobe_glyph


__GAIJI = {
    "svg-gaiji/byan.svg": "𰻞",
    "svg-gaiji/G16EF.svg": "篡",
}


def preprocess_page(page):
    soup = BeautifulSoup(page, features="xml")
    __replace_glyph_codes(soup)
    __add_image_alt_text(soup)
    __replace_tatehyphen(soup)
    page = __strip_page(soup)
    return page


def __replace_glyph_codes(soup):
    for el in soup.find_all("glyph"):
        m = re.search(r"^glyph:([0-9]+);?$", el.attrs["style"])
        code = int(m.group(1))
        for geta in el.find_all(string="〓"):
            glyph = get_adobe_glyph(code)
            geta.replace_with(glyph)


def __add_image_alt_text(soup):
    for img in soup.find_all("img"):
        if not img.has_attr("src"):
            continue
        src = img.attrs["src"]
        if src in __GAIJI:
            img.attrs["alt"] = __GAIJI[src]


def __replace_tatehyphen(soup):
    for img in soup.find_all("img", {"src": "svg-gaiji/tatehyphen.svg"}):
        img.string = "−"
        img.unwrap()


def __strip_page(soup):
    koumoku = soup.find(["項目"])
    if koumoku is not None:
        return koumoku.decode()
    else:
        raise Exception(f"Primary 項目 not found in page:\n{soup.prettify()}")
