import re
import os
from bs4 import BeautifulSoup

import bot.icons as Icons
from bot.soup import delete_soup_nodes
from bot.data import load_smk8_yomichan_name_conversion
from bot.yomichan.glossary.gloss import make_gloss
from bot.yomichan.glossary.name_conversion import convert_names


def make_glossary(entry, image_dir):
    soup = entry.get_page_soup()
    __fill_alts(soup)
    __delete_unused_nodes(soup)
    __clear_styles(soup)
    __set_data_class(soup)
    __convert_links(soup, entry)
    __convert_priority_markers(soup)
    __convert_gaiji(soup, image_dir)
    __convert_rectangles(soup, image_dir)

    name_conversion = load_smk8_yomichan_name_conversion()
    convert_names(soup, name_conversion)

    gloss = make_gloss(soup.span)
    glossary = [gloss]
    return glossary


def __fill_alts(soup):
    for name in ["親見出仮名", "親見出表記"]:
        for el in soup.find_all(name):
            el.name = "a"
            alt = el.attrs["alt"]
            el.string = alt
            el.attrs["href"] = f"?query={alt}&wildcards=off"
            del el.attrs["alt"]


def __delete_unused_nodes(soup):
    for name in ["audio", "連濁"]:
        delete_soup_nodes(soup, name)


def __clear_styles(soup):
    for el in soup.select("[style]"):
        del el.attrs["style"]


def __set_data_class(soup):
    for el in soup.select("[class]"):
        el.attrs["data-class"] = el.attrs["class"]


def __convert_links(soup, entry):
    for el in soup.find_all("a"):
        href = el.attrs["href"]
        if href.startswith("$"):
            el.unwrap()
        elif re.match(r"^[0-9]+(?:-[0-9A-F]{4})?$", href):
            ref_entry_id = entry.id_string_to_entry_id(href)
            ref_entry = entry.ID_TO_ENTRY[ref_entry_id]
            expression = ref_entry.get_first_expression()
            el.attrs["href"] = f"?query={expression}&wildcards=off"
        elif re.match(r"^(?:https?:|\?)[\w\W]*", href):
            pass
        else:
            raise Exception(f"Invalid href format: {href}")


def __convert_priority_markers(soup):
    style = "vertical-align: super; font-size: 0.6em"
    for el in soup.find_all("img", attrs={"alt": "*"}):
        el.name = "span"
        el.string = "＊"
        el.attrs["style"] = style
    for el in soup.find_all("img", attrs={"alt": "⁑"}):
        el.name = "span"
        el.string = "＊＊"
        el.attrs["style"] = style


def __convert_gaiji(soup, image_dir):
    for el in soup.find_all("img"):
        src = el.attrs["src"]
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


def __convert_rectangles(soup, image_dir):
    cls_to_appearance = {
        "default": "monochrome",
        "fill": "monochrome",
        "red": "auto",
        "redfill": "auto",
    }
    for el in soup.find_all("rect"):
        cls = el.attrs["class"] if el.has_attr("class") else "default"
        filename = f"{el.text}-{cls}.svg"
        path = os.path.join(image_dir, filename)
        __make_rectangle(path, el.text, cls)
        ratio = Icons.calculate_ratio(path)
        img = BeautifulSoup("<img/>", "xml").img
        img.attrs = {
            "height": 1.0 if ratio > 1.0 else ratio,
            "width": ratio if ratio > 1.0 else 1.0,
            "sizeUnits": "em",
            "collapsible": False,
            "collapsed": False,
            "background": False,
            "appearance": cls_to_appearance[cls],
            "title": el.text,
            "path": f"{os.path.basename(image_dir)}/{filename}",
        }
        el.name = "span"
        el.clear()
        el.append(img)
        el.attrs["style"] = "vertical-align: text-bottom; margin-right: 0.25em"


def __make_rectangle(path, text, cls):
    if cls == "fill":
        Icons.make_monochrome_fill_rectangle(path, text)
    elif cls == "red":
        Icons.make_rectangle(path, text, "red", "white", "red")
    elif cls == "redfill":
        Icons.make_rectangle(path, text, "red", "red", "white")
    else:
        Icons.make_rectangle(path, text, "black", "transparent", "black")
