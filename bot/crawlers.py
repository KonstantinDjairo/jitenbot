import re
from bs4 import BeautifulSoup

import bot.scraper as Scraper

from bot.entries.jitenon import JitenonKotowazaEntry
from bot.yomichan.export import JitenonKotowazaExporter

from bot.entries.jitenon import JitenonYojiEntry
from bot.yomichan.export import JitenonYojiExporter


class Crawler():
    def __init__(self):
        self._crawl_map = {}
        self.__entries = []

    def read_entries(self):
        entries_len = len(self._crawl_map)
        items = self._crawl_map.items()
        for idx, (entry_id, entry_path) in enumerate(items):
            update = f"Reading entry {idx+1}/{entries_len}"
            print(update, end='\r', flush=True)
            entry = self._entry_class(entry_id)
            entry.set_markup(entry_path)
            self.__entries.append(entry)
        print()

    def make_yomichan_dictionary(self):
        self._yomi_exporter.export(self.__entries)


class JitenonCrawler(Crawler):
    def __init__(self):
        super().__init__()

    def crawl(self):
        print(f"Scraping {self._name}...")
        jitenon = Scraper.Jitenon()
        gojuon_doc, _ = jitenon.scrape(self._gojuon_url)
        gojuon_soup = BeautifulSoup(gojuon_doc, features="html.parser")
        for gojuon_a in gojuon_soup.select(".kana_area a", href=True):
            gojuon_href = gojuon_a['href']
            kana_doc, _ = jitenon.scrape(gojuon_href)
            kana_soup = BeautifulSoup(kana_doc, features="html.parser")
            for kana_a in kana_soup.select(".word_box a", href=True):
                entry_link = kana_a['href']
                entry_id = self.__parse_entry_id(entry_link)
                if entry_id is None:
                    continue
                _, entry_path = jitenon.scrape(entry_link)
                self._crawl_map[entry_id] = entry_path
        entries_len = len(self._crawl_map)
        print(f"Finished scraping {entries_len} entries")

    def __parse_entry_id(self, entry_link):
        m = re.search(self._entry_id_pattern, entry_link)
        if not m:
            return None
        entry_id = int(m.group(1))
        if entry_id in self._crawl_map:
            return None
        return entry_id


class JitenonYojiCrawler(JitenonCrawler):
    def __init__(self):
        super().__init__()
        self._entry_class = JitenonYojiEntry
        self._yomi_exporter = JitenonYojiExporter()
        self._name = "jitenon-yoji"
        self._gojuon_url = "https://yoji.jitenon.jp/cat/gojuon.html"
        self._entry_id_pattern = r"([0-9]+).html"


class JitenonKotowazaCrawler(JitenonCrawler):
    def __init__(self):
        super().__init__()
        self._entry_class = JitenonKotowazaEntry
        self._yomi_exporter = JitenonKotowazaExporter()
        self._name = "jitenon-kotowaza"
        self._gojuon_url = "https://kotowaza.jitenon.jp/cat/gojuon.php"
        self._entry_id_pattern = r"([0-9]+).php"
