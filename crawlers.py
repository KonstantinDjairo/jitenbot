import re
from bs4 import BeautifulSoup

import scraper as Scraper
import yomichan as Yomichan
from jitenon_yoji import JitenonYoji


def jitenon_yoji_crawler():
    entries = {}
    jitenon = Scraper.Jitenon()
    gojuon_doc = jitenon.scrape("https://yoji.jitenon.jp/cat/gojuon.html")
    gojuon_soup = BeautifulSoup(gojuon_doc, features="html.parser")
    for gojuon_a in gojuon_soup.select(".kana_area a", href=True):
        gojuon_href = gojuon_a['href']
        kana_doc = jitenon.scrape(gojuon_href)
        kana_soup = BeautifulSoup(kana_doc, features="html.parser")
        for kana_a in kana_soup.select(".word_box a", href=True):
            kana_href = kana_a['href']
            sequence = int(re.search(r"([0-9]+).html", kana_href).group(1))
            if sequence in entries:
                continue
            yoji_doc = jitenon.scrape(kana_href)
            entry = JitenonYoji(sequence)
            entry.add_document(yoji_doc)
            entries[sequence] = entry

    terms = []
    attribution = ""
    modified_date = None
    for entry in entries.values():
        if modified_date is None or entry.modified_date > modified_date:
            modified_date = entry.modified_date
            attribution = entry.attribution
        for term in entry.yomichan_terms():
            terms.append(term)
    index = {
        "title": "四字熟語辞典オンライン",
        "revision": f"jitenon-yoji.{modified_date}",
        "sequenced": True,
        "format": 3,
        "url": "https://yoji.jitenon.jp/",
        "attribution": attribution,
    }
    Yomichan.create_zip(terms, index)
