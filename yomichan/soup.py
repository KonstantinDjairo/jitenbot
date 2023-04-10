import re
from css_parser import parseStyle


def make_gloss(soup):
    __preprocess_soup(soup)
    structured_content = __get_markup_structure(soup)
    return {
        "type": "structured-content",
        "content": structured_content
    }


def __preprocess_soup(soup):
    patterns = [
        r"^(.+)（[ぁ-ヿ、\s]+）$",
        r"^(.+)（[ぁ-ヿ、\s]+（[ぁ-ヿ、\s]）[ぁ-ヿ、\s]+）$"
    ]
    for a in soup.find_all("a"):
        for pattern in patterns:
            m = re.search(pattern, a.text)
            if m:
                a['href'] = f"?query={m.group(1)}&wildcards=off"
                break
    for p in soup.find_all("p"):
        p.name = "span"
    for th in soup.find_all("th"):
        th['style'] = "vertical-align: middle; text-align: center;"


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
    if parsedStyle.fontStyle != "":
        style["fontStyle"] = parsedStyle.fontStyle
    if parsedStyle.fontWeight != "":
        style["fontWeight"] = parsedStyle.fontWeight
    if parsedStyle.fontSize != "":
        style["fontSize"] = parsedStyle.fontSize
    if parsedStyle.textDecoration != "":
        style["textDecorationLine"] = parsedStyle.textDecoration
    if parsedStyle.verticalAlign != "":
        style["verticalAlign"] = parsedStyle.verticalAlign
    if parsedStyle.textAlign != "":
        style["textAlign"] = parsedStyle.textAlign
    if parsedStyle.listStyleType != "":
        style["listStyleType"] = parsedStyle.listStyleType
    return style
