import re
import os
from bs4 import BeautifulSoup

import bot.yomichan.glossary.icons as Icons
from bot.data import load_yomichan_name_conversion
from bot.yomichan.glossary.gloss import make_gloss
from bot.name_conversion import convert_names


def make_glossary(entry, media_dir):
    soup = entry.get_page_soup()
    __remove_glyph_styles(soup)
    __reposition_marks(soup)
    __remove_links_without_href(soup)
    __remove_appendix_links(soup)
    __convert_links(soup, entry)
    __add_parent_link(soup, entry)
    __add_homophone_links(soup, entry)
    __convert_images_to_text(soup)
    __text_parens_to_images(soup, media_dir)
    __replace_icons(soup, media_dir)
    __replace_accent_symbols(soup, media_dir)
    __convert_gaiji(soup, media_dir)
    __convert_graphics(soup, media_dir)
    __convert_number_icons(soup, media_dir)

    name_conversion = load_yomichan_name_conversion(entry.target)
    convert_names(soup, name_conversion)

    gloss = make_gloss(soup.span)
    glossary = [gloss]
    return glossary


def __remove_glyph_styles(soup):
    """The css_parser library will emit annoying warning messages
    later if it sees these glyph character styles"""
    for elm in soup.find_all("glyph"):
        if elm.has_attr("style"):
            elm["data-style"] = elm.attrs["style"]
            del elm.attrs["style"]


def __reposition_marks(soup):
    """These マーク symbols will be converted to rubies later, so they need to
    be positioned after the corresponding text in order to appear correctly"""
    for elm in soup.find_all("表外字"):
        mark = elm.find("表外字マーク")
        elm.append(mark)
    for elm in soup.find_all("表外音訓"):
        mark = elm.find("表外音訓マーク")
        elm.append(mark)


def __remove_links_without_href(soup):
    for elm in soup.find_all("a"):
        if elm.has_attr("href"):
            continue
        elm.attrs["data-name"] = elm.name
        elm.name = "span"


def __remove_appendix_links(soup):
    for elm in soup.find_all("a"):
        if elm.attrs["href"].startswith("appendix"):
            elm.unwrap()


def __convert_links(soup, entry):
    for elm in soup.find_all("a"):
        href = elm.attrs["href"].split(" ")[0]
        href = href.removeprefix("#")
        if not re.match(r"^[0-9]+(?:-[0-9A-F]{4})?$", href):
            raise Exception(f"Invalid href format: {href}")
        ref_entry_id = entry.id_string_to_entry_id(href)
        if ref_entry_id in entry.ID_TO_ENTRY:
            ref_entry = entry.ID_TO_ENTRY[ref_entry_id]
        else:
            ref_entry = entry.ID_TO_ENTRY[(ref_entry_id[0], 0)]
        expression = ref_entry.get_first_expression()
        elm.attrs["href"] = f"?query={expression}&wildcards=off"


def __add_parent_link(soup, entry):
    elm = soup.find("親見出相当部")
    if elm is not None:
        parent_entry = entry.get_parent()
        expression = parent_entry.get_first_expression()
        elm.attrs["href"] = f"?query={expression}&wildcards=off"
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
                expression = link_entry.get_first_expression()
                link = BeautifulSoup("<a/>", "xml").a
                link.string = text
                link.attrs["href"] = f"?query={expression}&wildcards=off"
                elm.append(link)
            elm.unwrap()


def __convert_images_to_text(soup):
    conversions = [
        ["svg-logo/重要語.svg", "＊", "vertical-align: super; font-size: 0.6em"],
        ["svg-logo/最重要語.svg", "＊＊", "vertical-align: super; font-size: 0.6em"],
        ["svg-logo/一般常識語.svg", "☆☆", "vertical-align: super; font-size: 0.6em"],
        ["svg-logo/追い込み.svg", "", ""],
        ["svg-special/区切り線.svg", "|", ""],
    ]
    for conversion in conversions:
        filename, text, style = conversion
        for elm in soup.find_all("img", attrs={"src": filename}):
            if text == "":
                elm.unwrap()
                continue
            if style != "":
                elm.attrs["style"] = style
            elm.attrs["data-name"] = elm.name
            elm.attrs["data-src"] = elm.attrs["src"]
            elm.name = "span"
            elm.string = text
            del elm.attrs["src"]


def __text_parens_to_images(soup, media_dir):
    for elm in soup.find_all("red"):
        char = elm.text
        if char not in ["（", "）"]:
            continue
        filename = f"red_{char}.svg"
        path = os.path.join(media_dir, filename)
        Icons.make_red_char(path, char)
        ratio = Icons.calculate_ratio(path)
        img = BeautifulSoup("<img/>", "xml").img
        img.attrs = {
            "height": 1.0,
            "width": ratio,
            "sizeUnits": "em",
            "collapsible": False,
            "collapsed": False,
            "background": False,
            "appearance": "auto",
            "path": f"{os.path.basename(media_dir)}/{filename}",
        }
        elm.attrs["data-name"] = elm.name
        elm.name = "span"
        elm.string = ""
        elm.append(img)
        elm.attrs["style"] = "vertical-align: text-bottom;"


def __replace_icons(soup, media_dir):
    cls_to_appearance = {
        "default": "monochrome",
        "fill": "monochrome",
        "red": "auto",
        "redfill": "auto",
        "none": "monochrome",
    }
    icon_info_list = [
        ["svg-logo/アク.svg", "アク", "default"],
        ["svg-logo/丁寧.svg", "丁寧", "default"],
        ["svg-logo/可能.svg", "可能", "default"],
        ["svg-logo/尊敬.svg", "尊敬", "default"],
        ["svg-logo/接尾.svg", "接尾", "default"],
        ["svg-logo/接頭.svg", "接頭", "default"],
        ["svg-logo/表記.svg", "表記", "default"],
        ["svg-logo/謙譲.svg", "謙譲", "default"],
        ["svg-logo/区別.svg", "区別", "redfill"],
        ["svg-logo/由来.svg", "由来", "redfill"],
        ["svg-logo/人.svg", "", "none"],
        ["svg-logo/他.svg", "", "none"],
        ["svg-logo/動.svg", "", "none"],
        ["svg-logo/名.svg", "", "none"],
        ["svg-logo/句.svg", "", "none"],
        ["svg-logo/派.svg", "", "none"],
        ["svg-logo/自.svg", "", "none"],
        ["svg-logo/連.svg", "", "none"],
        ["svg-logo/造.svg", "", "none"],
        ["svg-logo/造2.svg", "", "none"],
        ["svg-logo/造3.svg", "", "none"],
        ["svg-logo/百科.svg", "", "none"],
    ]
    for icon_info in icon_info_list:
        src, text, cls = icon_info
        for elm in soup.find_all("img", attrs={"src": src}):
            path = media_dir
            for part in src.split("/"):
                path = os.path.join(path, part)
            __make_rectangle(path, text, cls)
            ratio = Icons.calculate_ratio(path)
            img = BeautifulSoup("<img/>", "xml").img
            img.attrs = {
                "height": 1.0,
                "width": ratio,
                "sizeUnits": "em",
                "collapsible": False,
                "collapsed": False,
                "background": False,
                "appearance": cls_to_appearance[cls],
                "title": elm.attrs["alt"] if elm.has_attr("alt") else "",
                "path": f"{os.path.basename(media_dir)}/{src}",
            }
            elm.name = "span"
            elm.clear()
            elm.append(img)
            elm.attrs["style"] = "vertical-align: text-bottom; margin-right: 0.25em;"


def __replace_accent_symbols(soup, media_dir):
    accent_info_list = [
        ["svg-accent/平板.svg", Icons.make_heiban],
        ["svg-accent/アクセント.svg", Icons.make_accent],
    ]
    for info in accent_info_list:
        src, write_svg_function = info
        for elm in soup.find_all("img", attrs={"src": src}):
            path = media_dir
            for part in src.split("/"):
                path = os.path.join(path, part)
            write_svg_function(path)
            ratio = Icons.calculate_ratio(path)
            img = BeautifulSoup("<img/>", "xml").img
            img.attrs = {
                "height": 1.0,
                "width": ratio,
                "sizeUnits": "em",
                "collapsible": False,
                "collapsed": False,
                "background": False,
                "appearance": "auto",
                "path": f"{os.path.basename(media_dir)}/{src}",
            }
            elm.name = "span"
            elm.clear()
            elm.append(img)
            elm.attrs["style"] = "vertical-align: super; margin-left: -0.25em;"


def __convert_gaiji(soup, media_dir):
    for elm in soup.find_all("img"):
        if not elm.has_attr("src"):
            continue
        src = elm.attrs["src"]
        if src.startswith("graphics"):
            continue
        path = media_dir
        for part in src.split("/"):
            if part.strip() == "":
                continue
            path = os.path.join(path, part)
        ratio = Icons.calculate_ratio(path)
        img = BeautifulSoup("<img/>", "xml").img
        img.attrs = {
            "height": 1.0,
            "width": ratio,
            "sizeUnits": "em",
            "collapsible": False,
            "collapsed": False,
            "background": False,
            "appearance": "monochrome",
            "title": elm.attrs["alt"] if elm.has_attr("alt") else "",
            "path": f"{os.path.basename(media_dir)}/{src}",
        }
        elm.name = "span"
        elm.clear()
        elm.append(img)
        elm.attrs["style"] = "vertical-align: text-bottom;"


def __convert_graphics(soup, media_dir):
    for elm in soup.find_all("img"):
        if not elm.has_attr("src"):
            continue
        src = elm.attrs["src"]
        if not src.startswith("graphics"):
            continue
        elm.attrs = {
            "collapsible": True,
            "collapsed": True,
            "title": elm.attrs["alt"] if elm.has_attr("alt") else "",
            "path": f"{os.path.basename(media_dir)}/{src}",
            "src": src,
        }


def __convert_number_icons(soup, media_dir):
    for elm in soup.find_all("大語義番号"):
        if elm.find_parent("a") is None:
            filename = f"{elm.text}-fill.svg"
            appearance = "monochrome"
            path = os.path.join(media_dir, filename)
            __make_rectangle(path, elm.text, "fill")
        else:
            filename = f"{elm.text}-bluefill.svg"
            appearance = "auto"
            path = os.path.join(media_dir, filename)
            __make_rectangle(path, elm.text, "bluefill")
        ratio = Icons.calculate_ratio(path)
        img = BeautifulSoup("<img/>", "xml").img
        img.attrs = {
            "height": 1.0,
            "width": ratio,
            "sizeUnits": "em",
            "collapsible": False,
            "collapsed": False,
            "background": False,
            "appearance": appearance,
            "title": elm.text,
            "path": f"{os.path.basename(media_dir)}/{filename}",
        }
        elm.name = "span"
        elm.clear()
        elm.append(img)
        elm.attrs["style"] = "vertical-align: text-bottom; margin-right: 0.25em;"


def __make_rectangle(path, text, cls):
    if cls == "none":
        pass
    elif cls == "fill":
        Icons.make_monochrome_fill_rectangle(path, text)
    elif cls == "red":
        Icons.make_rectangle(path, text, "red", "white", "red")
    elif cls == "redfill":
        Icons.make_rectangle(path, text, "red", "red", "white")
    elif cls == "bluefill":
        Icons.make_rectangle(path, text, "blue", "blue", "white")
    else:
        Icons.make_rectangle(path, text, "black", "transparent", "black")
