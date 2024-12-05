import re
from bs4 import BeautifulSoup
from bot.data import load_mdict_name_conversion
from bot.name_conversion import convert_names


def make_glossary(entry, media_dir):
    soup = entry.get_page_soup()
    __reposition_marks(soup)
    __remove_appendix_links(soup)
    __convert_images(soup)
    __remove_links_without_href(soup)
    __convert_links(soup, entry)
    __add_parent_link(soup, entry)
    __add_homophone_links(soup, entry)

    name_conversion = load_mdict_name_conversion(entry.target)
    convert_names(soup, name_conversion)

    glossary = soup.span.decode()
    return glossary


def __reposition_marks(soup):
    """These 表外字マーク symbols will be converted to rubies later, so they need to
    be positioned after the corresponding text in order to appear correctly"""
    for elm in soup.find_all("表外字"):
        mark = elm.find("表外字マーク")
        elm.append(mark)
    for elm in soup.find_all("表外音訓"):
        mark = elm.find("表外音訓マーク")
        elm.append(mark)


def __remove_appendix_links(soup):
    """This info would be useful and nice to have, but jitenbot currently
    isn't designed to fetch and process these appendix files. It probably
    wouldn't be possible to include them in Yomichan, but it would definitely
    be possible for Mdict."""
    for elm in soup.find_all("a"):
        if not elm.has_attr("href"):
            continue
        if elm.attrs["href"].startswith("appendix"):
            elm.attrs["data-name"] = "a"
            elm.attrs["data-href"] = elm.attrs["href"]
            elm.name = "span"
            del elm.attrs["href"]


def __convert_images(soup):
    conversions = [
        ["svg-logo/重要語.svg", "＊"],
        ["svg-logo/最重要語.svg", "＊＊"],
        ["svg-logo/一般常識語.svg", "☆☆"],
        ["svg-logo/追い込み.svg", ""],
        ["svg-special/区切り線.svg", "|"],
        ["svg-accent/平板.svg", "⎺"],
        ["svg-accent/アクセント.svg", "⌝"],
        ["svg-logo/アク.svg", "アク"],
        ["svg-logo/丁寧.svg", "丁寧"],
        ["svg-logo/可能.svg", "可能"],
        ["svg-logo/尊敬.svg", "尊敬"],
        ["svg-logo/接尾.svg", "接尾"],
        ["svg-logo/接頭.svg", "接頭"],
        ["svg-logo/表記.svg", "表記"],
        ["svg-logo/謙譲.svg", "謙譲"],
        ["svg-logo/区別.svg", "区別"],
        ["svg-logo/由来.svg", "由来"],
    ]
    for conversion in conversions:
        filename, text = conversion
        for elm in soup.find_all("img", attrs={"src": filename}):
            elm.attrs["data-name"] = elm.name
            elm.attrs["data-src"] = elm.attrs["src"]
            elm.name = "span"
            elm.string = text
            del elm.attrs["src"]


def __remove_links_without_href(soup):
    for elm in soup.find_all("a"):
        if elm.has_attr("href"):
            continue
        elm.attrs["data-name"] = elm.name
        elm.name = "span"


def __convert_links(soup, entry):
    for elm in soup.find_all("a"):
        href = elm.attrs["href"].split(" ")[0]
        if re.match(r"^#?[0-9]+(?:-[0-9A-F]{4})?$", href):
            href = href.removeprefix("#")
            ref_entry_id = entry.id_string_to_entry_id(href)
            if ref_entry_id in entry.ID_TO_ENTRY:
                ref_entry = entry.ID_TO_ENTRY[ref_entry_id]
            else:
                ref_entry = entry.ID_TO_ENTRY[(ref_entry_id[0], 0)]
            gid = ref_entry.get_global_identifier()
            elm.attrs["href"] = f"entry://{gid}"
        elif re.match(r"^entry:", href):
            pass
        elif re.match(r"^https?:[\w\W]*", href):
            pass
        else:
            raise Exception(f"Invalid href format: {href}")


def __add_parent_link(soup, entry):
    elm = soup.find("親見出相当部")
    if elm is not None:
        parent_entry = entry.get_parent()
        gid = parent_entry.get_global_identifier()
        elm.attrs["href"] = f"entry://{gid}"
        elm.attrs["data-name"] = elm.name
        elm.name = "a"


def __add_homophone_links(soup, entry):
    forward_link = ["←", entry.entry_id[0] + 1]
    backward_link = ["→", entry.entry_id[0] - 1]
    homophone_info_list = [
        ["svg-logo/homophone1.svg", [forward_link]],
        ["svg-logo/homophone2.svg", [forward_link, backward_link]],
        ["svg-logo/homophone3.svg", [backward_link]],
    ]
    for homophone_info in homophone_info_list:
        filename, link_info = homophone_info
        for elm in soup.find_all("img", attrs={"src": filename}):
            for info in link_info:
                text, link_id = info
                link_entry = entry.ID_TO_ENTRY[(link_id, 0)]
                gid = link_entry.get_global_identifier()
                link = BeautifulSoup("<a/>", "xml").a
                link.string = text
                link.attrs["href"] = f"entry://{gid}"
                elm.append(link)
            elm.unwrap()
