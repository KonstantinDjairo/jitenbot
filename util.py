import re


def expand_shouryaku(shouryaku):
    """Return a list of words described by a 省略 notation.
    eg. "有（り）合（わ）せ" -> [
        "有り合わせ",
        "有合わせ",
        "有り合せ",
        "有合せ"
    ]
    """
    groups = re.findall(r"([^（]*)(（([^（]+)）)?", shouryaku)
    forms = [""]
    for group in groups:
        new_forms = []
        for form in forms:
            new_forms.append(form + group[0])
        forms = new_forms.copy()
        if group[2] == '':
            continue
        new_forms = []
        for form in forms:
            new_forms.append(form + group[2])
        forms = new_forms.copy() + forms.copy()
    return forms
