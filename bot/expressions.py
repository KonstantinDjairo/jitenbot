import re

__WIDE_MAP = {i: i + 0xFEE0 for i in range(0x21, 0x7F)}


def add_fullwidth(expressions):
    for expression in expressions:
        if re.match(r"[A-Za-z0-9]", expression):
            new_exp = expression.translate(__WIDE_MAP)
            if new_exp not in expressions:
                expressions.append(new_exp)


def add_variant_kanji(expressions, variant_kanji):
    for old_kanji, new_kanji in variant_kanji.items():
        new_exps = []
        for expression in expressions:
            if old_kanji in expression:
                new_exp = expression.replace(old_kanji, new_kanji)
                new_exps.append(new_exp)
        for new_exp in new_exps:
            if new_exp not in expressions:
                expressions.append(new_exp)


def expand_shouryaku(shouryaku):
    """Return a list of words described by a 省略 notation.
    eg. "有（り）合（わ）せ" -> [
        "有り合わせ", "有合わせ", "有り合せ", "有合せ"
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
