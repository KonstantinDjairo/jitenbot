from bs4 import BeautifulSoup


def convert_names(soup, name_conversion):
    for child in soup.children:
        if child.name is None:
            continue
        else:
            convert_names(child, name_conversion)

        if child.name in name_conversion.keys():
            conversion = name_conversion[child.name]
            if "name" in conversion:
                child.attrs["data-name"] = child.name
                child.name = conversion["name"]
            if "style" in conversion:
                child.attrs["style"] = conversion["style"]
            if "procedures" in conversion:
                procedures = conversion["procedures"]
                __apply_name_conversion_procedures(child, procedures)
        else:
            child.attrs["data-name"] = child.name
            child.name = "span"


def __apply_name_conversion_procedures(soup, procedures):
    functions = {
        "has_class": __has_class,
        "has_parent": __has_parent,
        "has_previous_sibling": __has_previous_sibling,
        "replace": __replace,
        "wrap": __wrap,
        "insert_span": __insert_span,
    }
    for procedure in procedures:
        function = functions[procedure["procedure_name"]]
        parameters = procedure["parameters"]
        function(soup, **parameters)


def __has_class(soup, class_name, key, value):
    if not soup.has_attr("class"):
        return
    soup_classes = soup.attrs["class"].split(" ")
    if class_name not in soup_classes:
        return
    if key == "style":
        soup.attrs["style"] = value
    elif key == "name":
        soup.name = value
    else:
        raise Exception()


def __has_parent(soup, parent_name, key, value):
    if soup.find_parent(parent_name) is None:
        return
    if key == "style":
        soup.attrs["style"] = value
    elif key == "name":
        soup.name = value
    else:
        raise Exception()


def __has_previous_sibling(soup, name, key, value):
    sibling = soup.previous_sibling
    if sibling is None:
        return
    elif sibling.name is None:
        return
    elif sibling.has_attr("data-name"):
        previous_sibling_name = sibling.attrs["data-name"]
    else:
        previous_sibling_name = sibling.name
    if previous_sibling_name != name:
        return
    if key == "style":
        soup.attrs["style"] = value
    elif key == "name":
        soup.name = value
    else:
        raise Exception()


def __replace(soup, old, new):
    soup.string = soup.text.replace(old, new)


def __wrap(soup, l_wrap, r_wrap):
    if soup.text.strip() != "":
        soup.string = f"{l_wrap}{soup.text}{r_wrap}"


def __insert_span(soup, attr_name, attr_val):
    span_markup = f"<span {attr_name}='{attr_val}'></span>"
    span_soup = BeautifulSoup(span_markup, "xml")
    for content in reversed(soup.contents):
        span_soup.span.insert(0, content.extract())
    soup.append(span_soup.span)
