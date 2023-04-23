import re
from bs4 import BeautifulSoup

from bot.yomichan.glossary.gloss import make_gloss


def make_glossary(entry):
    soup = BeautifulSoup(entry.markup, "html5lib")
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
    gloss = make_gloss(soup.table)
    glossary = [gloss]
    return glossary
