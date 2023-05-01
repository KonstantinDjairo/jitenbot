import re
from css_parser import parseStyle


def make_gloss(soup):
    node = __get_page_structure(soup)
    return {
        "type": "structured-content",
        "content": node["content"],
    }


def __get_page_structure(soup):
    node = {"tag": soup.name}
    content = []
    for child in soup.children:
        if child.name is None:
            text = child.text.strip()
            if text != "":
                content.append(text)
        else:
            content.append(__get_page_structure(child))

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
    if "height" in attrs:
        attributes["height"] = float(attrs["height"])
    if "width" in attrs:
        attributes["width"] = float(attrs["width"])
    if "sizeUnits" in attrs:
        attributes["sizeUnits"] = attrs["sizeUnits"]
    if "appearance" in attrs:
        attributes["appearance"] = attrs["appearance"]
    if "title" in attrs:
        attributes["title"] = attrs["title"]
    if "collapsible" in attrs:
        attributes["collapsible"] = bool(attrs["collapsible"])
    if "collapsed" in attrs:
        attributes["collapsed"] = bool(attrs["collapsed"])
    if "background" in attrs:
        attributes["background"] = bool(attrs["background"])
    if "path" in attrs:
        attributes["path"] = attrs["path"]
    if "style" in attrs:
        style = __get_style(attrs["style"])
        if len(style) > 0:
            attributes["style"] = style
    data_attrs = {}
    for attr_key in attrs.keys():
        if attr_key.startswith("data-"):
            key = attr_key.removeprefix("data-")
            data_attrs[key] = attrs[attr_key]
    if len(data_attrs) > 0:
        attributes["data"] = data_attrs
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

    margins = {
        "marginTop":    parsedStyle.marginTop,
        "marginRight":  parsedStyle.marginRight,
        "marginBottom": parsedStyle.marginBottom,
        "marginLeft":   parsedStyle.marginLeft,
    }
    for key, val in margins.items():
        m = re.search(r"(\d+(\.\d*)?|\.\d+)em", val)
        if m:
            style[key] = float(m.group(1))

    return style
