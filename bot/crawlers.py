import re
from bs4 import BeautifulSoup

import bot.scraper as Scraper
import bot.yomichan.export as YomichanExport
from bot.entries.jitenon_kotowaza import JitenonKotowaza
from bot.entries.jitenon_yoji import JitenonYoji


def run_all():
    jitenon_yoji()
    jitenon_kotowaza()


def jitenon_yoji():
    seq_to_entries = {}
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
            if sequence in seq_to_entries:
                continue
            yoji_doc = jitenon.scrape(kana_href)
            entry = JitenonYoji(sequence)
            entry.add_document(yoji_doc)
            seq_to_entries[sequence] = entry
    entries = seq_to_entries.values()
    YomichanExport.jitenon_yoji(entries)


def jitenon_kotowaza():
    seq_to_entries = {}
    jitenon = Scraper.Jitenon()
    gojuon_doc = jitenon.scrape("https://kotowaza.jitenon.jp/cat/gojuon.php")
    gojuon_soup = BeautifulSoup(gojuon_doc, features="html.parser")
    for gojuon_a in gojuon_soup.select(".kana_area a", href=True):
        gojuon_href = gojuon_a['href']
        kana_doc = jitenon.scrape(gojuon_href)
        kana_soup = BeautifulSoup(kana_doc, features="html.parser")
        for kana_a in kana_soup.select(".word_box a", href=True):
            kana_href = kana_a['href']
            m = re.search(r"([0-9]+).php", kana_href)
            if m:
                sequence = int(m.group(1))
            else:
                continue
            if sequence in seq_to_entries:
                continue
            kotowaza_doc = jitenon.scrape(kana_href)
            entry = JitenonKotowaza(sequence)
            entry.add_document(kotowaza_doc)
            seq_to_entries[sequence] = entry
    entries = seq_to_entries.values()
    YomichanExport.jitenon_kotowaza(entries)
