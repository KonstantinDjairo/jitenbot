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
    print("Scraping jitenon-yoji...")
    entry_id_to_entry_path = {}
    jitenon = Scraper.Jitenon()
    gojuon_doc, _ = jitenon.scrape("https://yoji.jitenon.jp/cat/gojuon.html")
    gojuon_soup = BeautifulSoup(gojuon_doc, features="html.parser")
    for gojuon_a in gojuon_soup.select(".kana_area a", href=True):
        gojuon_href = gojuon_a['href']
        kana_doc, _ = jitenon.scrape(gojuon_href)
        kana_soup = BeautifulSoup(kana_doc, features="html.parser")
        for kana_a in kana_soup.select(".word_box a", href=True):
            kana_href = kana_a['href']
            entry_id = int(re.search(r"([0-9]+).html", kana_href).group(1))
            if entry_id in entry_id_to_entry_path:
                continue
            _, entry_path = jitenon.scrape(kana_href)
            entry_id_to_entry_path[entry_id] = entry_path
    entries_len = len(entry_id_to_entry_path)
    print(f"Finished scraping {entries_len} entries")
    entries = []
    items = entry_id_to_entry_path.items()
    for idx, (entry_id, entry_path) in enumerate(items):
        update = f"Reading entry {idx+1}/{entries_len}"
        print(update, end='\r', flush=True)
        entry = JitenonYoji(entry_id)
        entry.add_document(entry_path)
        entries.append(entry)
    print()
    exporter = YomichanExport.JitenonYojiExporter()
    exporter.export(entries)


def jitenon_kotowaza():
    print("Scraping jitenon-kotowaza...")
    entry_id_to_entry_path = {}
    jitenon = Scraper.Jitenon()
    gojuon_doc, _ = jitenon.scrape("https://kotowaza.jitenon.jp/cat/gojuon.php")
    gojuon_soup = BeautifulSoup(gojuon_doc, features="html.parser")
    for gojuon_a in gojuon_soup.select(".kana_area a", href=True):
        gojuon_href = gojuon_a['href']
        kana_doc, _ = jitenon.scrape(gojuon_href)
        kana_soup = BeautifulSoup(kana_doc, features="html.parser")
        for kana_a in kana_soup.select(".word_box a", href=True):
            kana_href = kana_a['href']
            m = re.search(r"([0-9]+).php", kana_href)
            if not m:
                continue
            entry_id = int(m.group(1))
            if entry_id in entry_id_to_entry_path:
                continue
            _, entry_path = jitenon.scrape(kana_href)
            entry_id_to_entry_path[entry_id] = entry_path
    entries_len = len(entry_id_to_entry_path)
    print(f"Finished scraping {entries_len} entries")
    entries = []
    items = entry_id_to_entry_path.items()
    for idx, (entry_id, entry_path) in enumerate(items):
        update = f"Reading entry {idx+1}/{entries_len}"
        print(update, end='\r', flush=True)
        entry = JitenonKotowaza(entry_id)
        entry.add_document(entry_path)
        entries.append(entry)
    print()
    exporter = YomichanExport.JitenonKotowazaExporter()
    exporter.export(entries)
