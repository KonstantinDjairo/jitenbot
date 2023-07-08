import re
import os
from functools import cache
from pathlib import Path

from bot.soup import delete_soup_nodes
from bot.data import load_mdict_name_conversion
from bot.name_conversion import convert_names


def make_glossary(entry, media_dir):
    soup = entry.get_page_soup()
    __add_rubies(soup)
    __hyperlink_parent_expression(soup, entry)
    __delete_unused_nodes(soup, media_dir)
    __convert_links(soup, entry)

    name_conversion = load_mdict_name_conversion(entry.target)
    convert_names(soup, name_conversion)

    glossary = soup.span.decode()
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
    parent_entry = entry.get_parent()
    gid = parent_entry.get_global_identifier()
    for el in soup.find_all("親表記"):
        el.name = "a"
        el.attrs["href"] = f"entry://{gid}"


def __delete_unused_nodes(soup, media_dir):
    if not __graphics_directory_exists(media_dir):
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
def __graphics_directory_exists(media_dir):
    path = os.path.join(media_dir, "graphics")
    return Path(path).is_dir()


def __convert_links(soup, entry):
    for el in soup.find_all("a"):
        href = el.attrs["href"]
        if re.match(r"^[0-9]+(?:-[0-9A-F]{4})?$", href):
            ref_entry_id = entry.id_string_to_entry_id(href)
            ref_entry = entry.ID_TO_ENTRY[ref_entry_id]
            gid = ref_entry.get_global_identifier()
            el.attrs["href"] = f"entry://{gid}"
        elif re.match(r"^entry:", href):
            pass
        elif re.match(r"^https?:[\w\W]*", href):
            pass
        else:
            raise Exception(f"Invalid href format: {href}")
