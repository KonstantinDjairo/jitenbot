import re
from bs4 import BeautifulSoup

from bot.data import get_adobe_glyph


__GAIJI = {
    "gaiji/5350.svg": "卐",
    "gaiji/62cb.svg": "抛",
    "gaiji/7be1.svg": "簒",
}


def preprocess_page(page):
    page = __strip_page(page)
    page = __replace_glyph_codes(page)
    page = __format_hyougai_marks(page)
    page = __remove_pronunciation_parentheses(page)
    return page


def __strip_page(page):
    soup = BeautifulSoup(page, features="xml")
    koumoku = soup.find(["項目", "字音語参照項目"])
    if koumoku is not None:
        return koumoku.decode()
    else:
        raise Exception(f"Primary 項目 not found in page:\n{soup.prettify()}")


def __replace_glyph_codes(page):
    soup = BeautifulSoup(page, features="xml")
    for span in soup.find_all("span"):
        if "style" in span.attrs:
            m = re.search(r"^glyph:([0-9]+);$", span.attrs["style"])
            del span.attrs["style"]
            if m is None:
                continue
            code = int(m.group(1))
            for geta in span.find_all(string="〓"):
                glyph = get_adobe_glyph(code)
                geta.replace_with(glyph)
    for hyouki in soup.find_all("親見出表記"):
        if "alt" not in hyouki.attrs:
            continue
        alt = hyouki.attrs["alt"]
        codes = re.findall(r"{CID([0-9]+)}", alt)
        for code in codes:
            glyph = get_adobe_glyph(int(code))
            alt = alt.replace(f"{{CID{code}}}", glyph)
            hyouki.attrs["alt"] = alt
    for gaiji in soup.find_all("外字"):
        img = gaiji.img
        src = img.attrs["src"] if img.has_attr("src") else ""
        if src in __GAIJI:
            img.attrs["alt"] = __GAIJI[src]
    return soup.decode()


def __format_hyougai_marks(page):
    soup = BeautifulSoup(page, features="xml")
    for el in soup.find_all("外字"):
        el.string = "〓"
    text = soup.text
    for x in ["\n", "\t", " "]:
        text = text.replace(x, "")
    text = re.sub(r"〈([^〈]+)〉", r"\1", text)

    page = re.sub(r"〈([^〈]+)〉", r"␂\1␃", page)
    for mark in re.findall(r"《.", text):
        if mark[1] == "〓":
            page = page.replace("《", "<表外音訓/>", 1)
        else:
            page = re.sub(f"《([^{mark[1]}]*)({mark[1]})",
                          r"\1<表外音訓>\2</表外音訓>",
                          page, count=1)
    for mark in re.findall(r"〈.", text):
        if mark[1] == "〓":
            page = page.replace("〈", "<表外字/>", 1)
        else:
            page = re.sub(f"〈([^{mark[1]}]*)({mark[1]})",
                          r"\1<表外字>\2</表外字>",
                          page, count=1)

    page = page.replace("␂", "〈")
    page = page.replace("␃", "〉")
    soup = BeautifulSoup(page, features="xml")

    for el in soup.find_all("表外音訓"):
        if el.text == "":
            el.append(el.next_sibling)
        mark_xml = "<表外音訓マーク>︽</表外音訓マーク>"
        mark_soup = BeautifulSoup(mark_xml, "xml")
        el.append(mark_soup.表外音訓マーク)

    for el in soup.find_all("表外字"):
        if el.text == "":
            el.append(el.next_sibling)
        mark_xml = "<表外字マーク>︿</表外字マーク>"
        mark_soup = BeautifulSoup(mark_xml, "xml")
        el.append(mark_soup.表外字マーク)

    return soup.decode()


def __remove_pronunciation_parentheses(page):
    page = page.replace("<表音表記>（", "<表音表記>")
    page = page.replace("）</表音表記>", "</表音表記>")
    return page
