from sudachipy import tokenizer
from sudachipy import dictionary

from bot.data import load_yomichan_inflection_categories

__U_KANA_LIST = ["う", "く", "す", "つ", "ぬ", "ふ", "む",
                 "ゆ", "る", "ぐ", "ず", "づ", "ぶ", "ぷ"]

__SUDACHI_DICTIONARY = None
__SUDACHI_INFLECTION_TYPES = None


def sudachi_rules(expression):
    global __SUDACHI_DICTIONARY
    global __SUDACHI_INFLECTION_TYPES
    if __SUDACHI_DICTIONARY is None:
        __SUDACHI_DICTIONARY = dictionary.Dictionary(dict="full").create()
    if __SUDACHI_INFLECTION_TYPES is None:
        categories = load_yomichan_inflection_categories()
        __SUDACHI_INFLECTION_TYPES = categories["sudachi"]
    splitmode = tokenizer.Tokenizer.SplitMode.A
    tokens = __SUDACHI_DICTIONARY.tokenize(expression, splitmode)
    if len(tokens) == 0:
        return ""
    pos = tokens[len(tokens)-1].part_of_speech()[4]
    tags = pos.split("-")
    rules = tags_to_rules(expression, tags, __SUDACHI_INFLECTION_TYPES)
    return rules


def tags_to_rules(expression, tags, inflection_types):
    rules = set()
    exp_final_character = expression[len(expression)-1:]
    for tag in tags:
        if tag in inflection_types["sahen"]:
            if expression.endswith("する"):
                rules.add("vs")
            elif expression.endswith("為る"):
                rules.add("vs")
            elif expression.endswith("ずる"):
                rules.add("vz")
            elif expression.endswith("す"):
                rules.add("v5")
        if tag in inflection_types["godan"]:
            if exp_final_character in __U_KANA_LIST:
                rules.add("v5")
        if tag in inflection_types["ichidan"]:
            if expression.endswith("る"):
                rules.add("v1")
        if tag in inflection_types["keiyoushi"]:
            if expression.endswith("い"):
                rules.add("adj-i")
        if tag in inflection_types["kahen"]:
            if expression.endswith("くる"):
                rules.add("vk")
            elif expression.endswith("来る"):
                rules.add("vk")
        if tag in inflection_types["sudachi"]:
            return sudachi_rules(expression)
    return " ".join(list(rules))
