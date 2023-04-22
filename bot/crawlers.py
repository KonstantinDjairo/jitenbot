import re
from bs4 import BeautifulSoup

import bot.scraper as Scraper

from bot.entries.jitenon_kotowaza import JitenonKotowazaEntry
from bot.yomichan.export import JitenonKotowazaExporter

from bot.entries.jitenon_yoji import JitenonYojiEntry
from bot.yomichan.export import JitenonYojiExporter


class Crawler():
    def __init__(self):
        self.crawl_map = {}
        self.entries = []

    def make_entries(self):
        entries_len = len(self.crawl_map)
        items = self.crawl_map.items()
        for idx, (entry_id, entry_path) in enumerate(items):
            update = f"Reading entry {idx+1}/{entries_len}"
            print(update, end='\r', flush=True)
            entry = self.entry_class(entry_id)
            entry.add_document(entry_path)
            self.entries.append(entry)
        print()

    def make_yomichan_dictionary(self):
        self.yomi_exporter.export(self.entries)


class JitenonYojiCrawler(Crawler):
    def __init__(self):
        super().__init__()
        self.entry_class = JitenonYojiEntry
        self.yomi_exporter = JitenonYojiExporter()

    def crawl(self):
        print("Scraping jitenon-yoji...")
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
                if entry_id in self.crawl_map:
                    continue
                _, entry_path = jitenon.scrape(kana_href)
                self.crawl_map[entry_id] = entry_path
        entries_len = len(self.crawl_map)
        print(f"Finished scraping {entries_len} entries")


class JitenonKotowazaCrawler(Crawler):
    def __init__(self):
        super().__init__()
        self.entry_class = JitenonKotowazaEntry
        self.yomi_exporter = JitenonKotowazaExporter()

    def crawl(self):
        print("Scraping jitenon-kotowaza...")
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
                if entry_id in self.crawl_map:
                    continue
                _, entry_path = jitenon.scrape(kana_href)
                self.crawl_map[entry_id] = entry_path
        entries_len = len(self.crawl_map)
        print(f"Finished scraping {entries_len} entries")
