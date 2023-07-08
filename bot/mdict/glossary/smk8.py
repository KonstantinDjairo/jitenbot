import re

from bot.soup import delete_soup_nodes
from bot.data import load_mdict_name_conversion
from bot.name_conversion import convert_names


def make_glossary(entry, media_dir):
    soup = entry.get_page_soup()
    __fill_alts(soup, entry)
    __delete_unused_nodes(soup)
    __convert_links(soup, entry)
    __convert_priority_markers(soup)

    name_conversion = load_mdict_name_conversion(entry.target)
    convert_names(soup, name_conversion)

    glossary = soup.span.decode()
    return glossary


def __fill_alts(soup, entry):
    names = ["親見出仮名", "親見出表記"]
    if soup.find(names) is None:
        return
    parent_entry = entry.get_parent()
    gid = parent_entry.get_global_identifier()
    for el in soup.find_all(names):
        el.name = "a"
        alt = el.attrs["alt"]
        el.string = alt
        el.attrs["href"] = f"entry://{gid}"
        del el.attrs["alt"]


def __delete_unused_nodes(soup):
    for name in ["連濁"]:
        delete_soup_nodes(soup, name)


def __convert_links(soup, entry):
    for el in soup.find_all("a"):
        href = el.attrs["href"]
        if href.startswith("$"):
            el.unwrap()
        elif re.match(r"^[0-9]+(?:-[0-9A-F]{4})?$", href):
            ref_entry_id = entry.id_string_to_entry_id(href)
            ref_entry = entry.ID_TO_ENTRY[ref_entry_id]
            gid = ref_entry.get_global_identifier()
            el.attrs["href"] = f"entry://{gid}"
        elif re.match(r"^[0-9]+[ab]?\.aac$", href):
            el.attrs["href"] = f"sound://audio/{href}"
        elif re.match(r"^entry:", href):
            pass
        elif re.match(r"^https?:[\w\W]*", href):
            pass
        else:
            raise Exception(f"Invalid href format: {href}")


def __convert_priority_markers(soup):
    for el in soup.find_all("img", attrs={"alt": "*"}):
        el.name = "span"
        el.string = "＊"
    for el in soup.find_all("img", attrs={"alt": "⁑"}):
        el.name = "span"
        el.string = "＊＊"
