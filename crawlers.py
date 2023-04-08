import re
from bs4 import BeautifulSoup

import scraper as Scraper
import yomichan as Yomichan
from jitenon_yoji import JitenonYoji


def jitenon_yoji_crawler():
    entries = {}
    jitenon = Scraper.Jitenon()
    gojuon = jitenon.scrape("https://yoji.jitenon.jp/cat/gojuon.html")
    gojuon_soup = BeautifulSoup(gojuon, features="html.parser")
    for gojuon_a in gojuon_soup.select(".kana_area a", href=True):
        gojuon_href = gojuon_a['href']
        kana = jitenon.scrape(gojuon_href)
        kana_soup = BeautifulSoup(kana, features="html.parser")
        for kana_a in kana_soup.select(".word_box a", href=True):
            kana_href = kana_a['href']
            sequence = int(re.search(r"([0-9]+).html", kana_href).group(1))
            if sequence in entries:
                continue
            yoji = jitenon.scrape(kana_href)
            yoji_soup = BeautifulSoup(yoji, features="html5lib")
            entry = JitenonYoji(sequence)
            entry.add_soup(yoji_soup)
            entries[sequence] = entry
    terms = []
    for entry in entries.values():
        for term in entry.yomichan_terms():
            terms.append(term)
    index = {
        "title": "四字熟語辞典オンライン",
        "revision": "test",
        "sequenced": True,
        "format": 3,
        "url": "https://yoji.jitenon.jp/",
        "attribution": "© 2012-2023 四字熟語辞典オンライン",
        "description": "",
    }
    Yomichan.create_zip(terms, index)
