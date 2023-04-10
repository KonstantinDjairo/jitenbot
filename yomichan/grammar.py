from sudachipy import tokenizer
from sudachipy import dictionary


def sudachi_rules(expression, reading):
    tokenizer_obj = dictionary.Dictionary().create()
    splitmode = tokenizer.Tokenizer.SplitMode.A
    tokens = tokenizer_obj.tokenize(expression, splitmode)
    pos = tokens[len(tokens)-1].part_of_speech()[4]
    tags = pos.split("-")
    rules = __sudachi_tags_to_rules(tags, expression, reading)
    return rules


def __sudachi_tags_to_rules(tags, expression, reading):
    u_endings = ["う", "く", "す", "つ", "ぬ", "ふ", "む",
                 "ゆ", "る", "ぐ", "ず", "づ", "ぶ", "ぷ"]
    rules = set()
    for tag in tags:
        if expression.endswith("い"):
            if tag == "形容詞" or "ナイ" in tag or "タイ" in tag:
                rules.add("adj-i")
        if expression.endswith("る"):
            if "一" in tag or tag == "レル":
                rules.add("v1")
        if "二" in tag or "四" in tag or "五" in tag:
            for u_ending in u_endings:
                if expression.endswith(u_ending):
                    rules.add("v5")
                    break
        if "サ" in tag and (expression.endswith("する") or expression == "為る"):
            rules.add("vs")
        if "サ" in tag and expression.endswith("ずる"):
            rules.add("vz")
    if expression.endswith("来る") and reading.endswith("くる"):
        rules = set()
        rules.add("vk")
    return " ".join(list(rules))
