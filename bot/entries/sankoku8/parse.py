from bs4 import BeautifulSoup


def parse_hyouki_soup(soup, base_exps):
    omitted_characters = [
        "／", "〈", "〉", "（", "）", "⦅", "⦆", "：", "…"
    ]
    exps = base_exps.copy()
    for child in soup.children:
        new_exps = []
        if child.name == "言換G":
            for alt in child.find_all("言換"):
                parts = parse_hyouki_soup(alt, [""])
                for exp in exps:
                    for part in parts:
                        new_exps.append(exp + part)
        elif child.name == "補足表記":
            alt1 = child.find("表記対象")
            alt2 = child.find("表記内容G")
            parts1 = parse_hyouki_soup(alt1, [""])
            parts2 = parse_hyouki_soup(alt2, [""])
            for exp in exps:
                for part in parts1:
                    new_exps.append(exp + part)
                for part in parts2:
                    new_exps.append(exp + part)
        elif child.name == "省略":
            parts = parse_hyouki_soup(child, [""])
            for exp in exps:
                new_exps.append(exp)
                for part in parts:
                    new_exps.append(exp + part)
        elif child.name is not None:
            new_exps = parse_hyouki_soup(child, exps)
        else:
            text = child.text
            for char in omitted_characters:
                text = text.replace(char, "")
            for exp in exps:
                new_exps.append(exp + text)
        exps = new_exps.copy()
    return exps


def parse_hyouki_pattern(pattern):
    replacements = {
        "（": "<省略>（",
        "）": "）</省略>",
        "｛": "<補足表記><表記対象>",
        "・": "</表記対象><表記内容G>（<表記内容>",
        "｝": "</表記内容>）</表記内容G></補足表記>",
        "〈": "<言換G>〈<言換>",
        "／": "</言換>／<言換>",
        "〉": "</言換>〉</言換G>",
        "⦅": "<補足表記><表記対象>",
        "＼": "</表記対象><表記内容G>⦅<表記内容>",
        "⦆": "</表記内容>⦆</表記内容G></補足表記>",
    }
    markup = f"<span>{pattern}</span>"
    for key, val in replacements.items():
        markup = markup.replace(key, val)
    soup = BeautifulSoup(markup, "xml")
    hyouki_soup = soup.find("span")
    exps = parse_hyouki_soup(hyouki_soup, [""])
    return exps
