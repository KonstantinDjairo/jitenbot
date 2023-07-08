import re
import os
from bs4 import BeautifulSoup
from functools import cache
from pathlib import Path

import bot.icons as Icons
from bot.soup import delete_soup_nodes
from bot.data import load_yomichan_name_conversion
from bot.yomichan.glossary.gloss import make_gloss
from bot.name_conversion import convert_names


def make_glossary(entry, image_dir):
    soup = entry.get_page_soup()
    __add_rubies(soup)
    __hyperlink_parent_expression(soup, entry)
    __delete_unused_nodes(soup, image_dir)
    __clear_styles(soup)
    __set_data_class(soup)
    __convert_links(soup, entry)
    __convert_gaiji(soup, image_dir)
    __convert_graphics(soup, image_dir)
    __convert_logos(soup, image_dir)
    __convert_kanjion_logos(soup, image_dir)
    __convert_daigoginum(soup, image_dir)
    __convert_jundaigoginum(soup, image_dir)

    name_conversion = load_yomichan_name_conversion(entry.target)
    convert_names(soup, name_conversion)

    gloss = make_gloss(soup.span)
    glossary = [gloss]
    return glossary


def __add_rubies(soup):
    for name in ["表外音訓", "表外字"]:
        for ruby in soup.find_all(name):
            ruby.name = "ruby"
            rt = ruby.find("表外字マーク")
            rt.name = "rt"
            ruby.append(rt)  # needs to positioned after the text


def __hyperlink_parent_expression(soup, entry):
    if soup.find("親表記") is None:
        return
    parent_entry_id = entry.SUBENTRY_ID_TO_ENTRY_ID[entry.entry_id]
    parent_entry = entry.ID_TO_ENTRY[parent_entry_id]
    parent_expression = parent_entry.get_first_expression()
    for el in soup.find_all("親表記"):
        el.name = "a"
        el.attrs["href"] = f"?query={parent_expression}&wildcards=off"


def __delete_unused_nodes(soup, image_dir):
    if not __graphics_directory_exists(image_dir):
        delete_soup_nodes(soup, "カットG")
    for el in soup.find_all("logo"):
        next_sibling = el.next_sibling
        if next_sibling is None:
            continue
        elif next_sibling.name in ["漢字見出G", "漢字音G"]:
            el.decompose()
    for el in soup.find_all("漢字音G"):
        for child in el.find_all(string="・"):
            child.replace_with("")


@cache
def __graphics_directory_exists(image_dir):
    path = os.path.join(image_dir, "graphics")
    return Path(path).is_dir()


def __clear_styles(soup):
    for el in soup.select("[style]"):
        del el.attrs["style"]


def __set_data_class(soup):
    for el in soup.select("[class]"):
        el.attrs["data-class"] = el.attrs["class"]


def __convert_links(soup, entry):
    for el in soup.find_all("a"):
        href = el.attrs["href"]
        if re.match(r"^[0-9]+(?:-[0-9A-F]{4})?$", href):
            ref_entry_id = entry.id_string_to_entry_id(href)
            ref_entry = entry.ID_TO_ENTRY[ref_entry_id]
            expression = ref_entry.get_first_expression()
            el.attrs["href"] = f"?query={expression}&wildcards=off"
        elif re.match(r"^(?:https?:|\?)[\w\W]*", href):
            pass
        else:
            raise Exception(f"Invalid href format: {href}")


def __convert_gaiji(soup, image_dir):
    for el in soup.find_all("img"):
        src = el.attrs["src"]
        if not src.startswith("gaiji"):
            continue
        path = image_dir
        for part in src.split("/"):
            if part.strip() == "":
                continue
            path = os.path.join(path, part)
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
            "title": el.attrs["alt"] if el.has_attr("alt") else "",
            "path": f"{os.path.basename(image_dir)}/{src}",
            "src": src,
        }
        el.name = "span"
        el.clear()
        el.append(img)
        el.attrs["style"] = "vertical-align: text-bottom;"


def __convert_graphics(soup, image_dir):
    for el in soup.find_all("img"):
        src = el.attrs["src"]
        if not src.startswith("graphics"):
            continue
        el.attrs = {
            "collapsible": True,
            "collapsed": True,
            "title": el.attrs["alt"] if el.has_attr("alt") else "",
            "path": f"{os.path.basename(image_dir)}/{src}",
            "src": src,
        }


def __convert_logos(soup, image_dir):
    for el in soup.find_all("logo"):
        filename = f"{el.text}-default.svg"
        path = os.path.join(image_dir, filename)
        Icons.make_rectangle(path, el.text, "black", "transparent", "black")
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
            "title": el.text,
            "path": f"{os.path.basename(image_dir)}/{filename}",
        }
        el.name = "span"
        el.clear()
        el.append(img)
        el.attrs["style"] = "vertical-align: text-bottom; margin-right: 0.25em;"


def __convert_kanjion_logos(soup, image_dir):
    for el in soup.find_all("漢字音logo"):
        filename = f"{el.text}-default.svg"
        path = os.path.join(image_dir, filename)
        Icons.make_rectangle(path, el.text, "black", "transparent", "black")
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
            "title": el.text,
            "path": f"{os.path.basename(image_dir)}/{filename}",
        }
        el.name = "span"
        el.clear()
        el.append(img)
        el.attrs["style"] = "vertical-align: text-bottom; margin-left: 0.25em;"


def __convert_daigoginum(soup, image_dir):
    for el in soup.find_all("大語義num"):
        filename = f"{el.text}-fill.svg"
        path = os.path.join(image_dir, filename)
        Icons.make_monochrome_fill_rectangle(path, el.text)
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
            "title": el.text,
            "path": f"{os.path.basename(image_dir)}/{filename}",
        }
        el.name = "span"
        el.clear()
        el.append(img)
        el.attrs["style"] = "vertical-align: text-bottom;"


def __convert_jundaigoginum(soup, image_dir):
    for el in soup.find_all("準大語義num"):
        filename = f"{el.text}-default.svg"
        path = os.path.join(image_dir, filename)
        Icons.make_rectangle(path, el.text, "black", "transparent", "black")
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
            "title": el.text,
            "path": f"{os.path.basename(image_dir)}/{filename}",
        }
        el.name = "span"
        el.clear()
        el.append(img)
        el.attrs["style"] = "vertical-align: text-bottom;"
