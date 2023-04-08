import json
import os
import shutil
import uuid
from pathlib import Path
from css_parser import parseStyle


def create_zip(terms, index, tags=[]):
    build_directory = str(uuid.uuid4())
    os.mkdir(build_directory)

    terms_per_file = 500
    max_i = int(len(terms) / terms_per_file) + 1
    for i in range(max_i):
        term_file = os.path.join(build_directory, f"term_bank_{i+1}.json")
        with open(term_file, "w", encoding='utf8') as f:
            start = terms_per_file * i
            end = terms_per_file * (i + 1)
            json.dump(terms[start:end], f, indent=4, ensure_ascii=False)

    index_file = os.path.join(build_directory, "index.json")
    with open(index_file, 'w', encoding='utf8') as f:
        json.dump(index, f, indent=4, ensure_ascii=False)

    if len(tags) > 0:
        tag_file = os.path.join(build_directory, "tag_bank_1.json")
        with open(tag_file, 'w', encoding='utf8') as f:
            json.dump(tags, f, indent=4, ensure_ascii=False)

    zip_filename = index["title"]
    zip_file = f"{zip_filename}.zip"
    if Path(zip_file).is_file():
        os.remove(zip_file)
    shutil.make_archive(zip_filename, "zip", build_directory)
    if not Path("output").is_dir():
        os.mkdir("output")
    shutil.move(zip_file, "output")
    shutil.rmtree(build_directory)


def soup_to_gloss(soup):
    structured_content = __get_markup_structure(soup)
    return {
        "type": "structured-content",
        "content": structured_content
    }


def __get_markup_structure(soup):
    node = {}
    content = []
    for child in soup.children:
        if child.name is None:
            text = child.text.strip()
            if text != "":
                content.append(text)
        else:
            content.append(__get_markup_structure(child))

    node["tag"] = soup.name
    attributes = __get_attributes(soup.attrs)
    for key, val in attributes.items():
        node[key] = val

    if node["tag"] == "th":
        node["style"] = {"verticalAlign": "middle", "textAlign": "center"}
    elif node["tag"] == "p":
        node["tag"] = "span"

    if len(content) == 0:
        pass
    elif len(content) == 1:
        node["content"] = content[0]
    else:
        node["content"] = content

    return node


def __get_attributes(attrs):
    attributes = {}
    if "href" in attrs:
        attributes["href"] = attrs["href"]
    if "rowspan" in attrs:
        attributes["rowSpan"] = int(attrs["rowspan"])
    if "colspan" in attrs:
        attributes["colSpan"] = int(attrs["colspan"])
    if "style" in attrs:
        attributes["style"] = __get_style(attrs["style"])
    return attributes


def __get_style(inline_style_string):
    style = {}
    parsedStyle = parseStyle(inline_style_string)
    if parsedStyle.fontSize != "":
        style["fontSize"] = parsedStyle.fontSize
    if parsedStyle.verticalAlign != "":
        style["verticalAlign"] = parsedStyle.verticalAlign
    if parsedStyle.textDecoration != "":
        style["textDecorationLine"] = parsedStyle.textDecoration
    if parsedStyle.listStyleType != "":
        style["listStyleType"] = parsedStyle.listStyleType
    if parsedStyle.fontStyle != "":
        style["fontStyle"] = parsedStyle.fontStyle
    if parsedStyle.fontWeight != "":
        style["fontWeight"] = parsedStyle.fontWeight
    return style
