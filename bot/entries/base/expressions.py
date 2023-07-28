import re
from bot.data import load_variant_kanji


__KATA_TO_HIRA_MAP = {
    i: i - 96 for i in [
        *range(0x30A1, 0x30F7),
        *range(0x30FD, 0x30FF),
    ]
}


__HALFWIDTH_TO_FULLWIDTH_MAP = {
    i: i + 0xFEE0 for i in [
        *range(0x21, 0x7F),
    ]
}


def kata_to_hira(text):
    hira = text.translate(__KATA_TO_HIRA_MAP)
    return hira


def add_fullwidth(expressions):
    for expression in expressions:
        new_exp = expression.translate(__HALFWIDTH_TO_FULLWIDTH_MAP)
        if new_exp not in expressions:
            expressions.append(new_exp)


def add_variant_kanji(expressions):
    variant_kanji = load_variant_kanji()
    for kyuuji, shinji in variant_kanji.items():
        new_exps = []
        for expression in expressions:
            if kyuuji in expression:
                new_exp = expression.replace(kyuuji, shinji)
                new_exps.append(new_exp)
            if shinji in expression:
                new_exp = expression.replace(shinji, kyuuji)
                new_exps.append(new_exp)
        for new_exp in new_exps:
            if new_exp not in expressions:
                expressions.append(new_exp)


def remove_iteration_mark(expressions):
    iterated_kanji = r"(.)々"
    for expression in expressions:
        for char in re.findall(iterated_kanji, expression):
            new_exp = expression.replace(f"{char}々", f"{char}{char}")
            if new_exp not in expressions:
                expressions.append(new_exp)


def add_iteration_mark(expressions):
    repeat_kanji = r"([^0-z０-ｚぁ-ヿ])\1"
    for expression in expressions:
        for char in re.findall(repeat_kanji, expression):
            new_exp = expression.replace(f"{char}{char}", f"{char}々")
            if new_exp not in expressions:
                expressions.append(new_exp)


def expand_abbreviation(abbreviated_expression):
    """Return a list of words described by a 省略 notation."""
    groups = re.findall(r"([^（]*)(（([^（]+)）)?", abbreviated_expression)
    expressions = [""]
    for group in groups:
        new_exps = []
        for expression in expressions:
            new_exps.append(expression + group[0])
        expressions = new_exps.copy()
        if group[2] == '':
            continue
        new_exps = []
        for expression in expressions:
            new_exps.append(expression + group[2])
        expressions = new_exps.copy() + expressions.copy()
    return expressions


def expand_abbreviation_list(expressions):
    new_exps = []
    for expression in expressions:
        for new_exp in expand_abbreviation(expression):
            if new_exp not in new_exps:
                new_exps.append(new_exp)
    return new_exps
