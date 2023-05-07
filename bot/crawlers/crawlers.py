import os
import re
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup

import bot.scraper as Scraper
from bot.entries.factory import new_entry
from bot.yomichan.exporters.factory import new_exporter


class Crawler(ABC):
    def __init__(self, target):
        self._target = target
        self._page_map = {}
        self._entries = []
        self._page_id_pattern = None

    @abstractmethod
    def collect_pages(self, page_dir):
        pass

    def read_pages(self):
        pages_len = len(self._page_map)
        items = self._page_map.items()
        for idx, (page_id, page_path) in enumerate(items):
            update = f"Reading page {idx+1}/{pages_len}"
            print(update, end='\r', flush=True)
            entry = new_entry(self._target, page_id)
            with open(page_path, "r", encoding="utf-8") as f:
                page = f.read()
            try:
                entry.set_page(page)
            except ValueError as err:
                print(err)
                print("Try deleting and redownloading file:")
                print(f"\t{page_path}\n")
                continue
            self._entries.append(entry)
        print()

    def make_yomichan_dictionary(self, image_dir):
        exporter = new_exporter(self._target)
        exporter.export(self._entries, image_dir)

    def _parse_page_id(self, page_link):
        m = re.search(self._page_id_pattern, page_link)
        if m is None:
            return None
        page_id = int(m.group(1))
        if page_id in self._page_map:
            return None
        return page_id


class JitenonKokugoCrawler(Crawler):
    def __init__(self, target):
        super().__init__(target)
        self._gojuon_url = "https://kokugo.jitenon.jp/cat/gojuonindex.php"
        self._page_id_pattern = r"word/p([0-9]+)$"

    def collect_pages(self, page_dir):
        jitenon = Scraper.Jitenon()
        gojuon_doc, _ = jitenon.scrape(self._gojuon_url)
        gojuon_soup = BeautifulSoup(gojuon_doc, features="html.parser")
        for gojuon_a in gojuon_soup.select(".kana_area a", href=True):
            gojuon_href = gojuon_a['href']
            max_kana_page = 1
            current_kana_page = 1
            while current_kana_page <= max_kana_page:
                kana_doc, _ = jitenon.scrape(f"{gojuon_href}&page={current_kana_page}")
                current_kana_page += 1
                kana_soup = BeautifulSoup(kana_doc, features="html.parser")
                page_total = kana_soup.find(class_="page_total").text
                m = re.search(r"全([0-9]+)件", page_total)
                if m:
                    max_kana_page = int(m.group(1))
                for kana_a in kana_soup.select(".word_box a", href=True):
                    page_link = kana_a['href']
                    page_id = self._parse_page_id(page_link)
                    if page_id is None:
                        continue
                    _, page_path = jitenon.scrape(page_link)
                    self._page_map[page_id] = page_path
        pages_len = len(self._page_map)
        print(f"Finished scraping {pages_len} pages")


class _JitenonCrawler(Crawler):
    def __init__(self, target):
        super().__init__(target)
        self._gojuon_url = None

    def collect_pages(self, page_dir):
        print("Scraping jitenon.jp")
        jitenon = Scraper.Jitenon()
        gojuon_doc, _ = jitenon.scrape(self._gojuon_url)
        gojuon_soup = BeautifulSoup(gojuon_doc, features="html.parser")
        for gojuon_a in gojuon_soup.select(".kana_area a", href=True):
            gojuon_href = gojuon_a['href']
            kana_doc, _ = jitenon.scrape(gojuon_href)
            kana_soup = BeautifulSoup(kana_doc, features="html.parser")
            for kana_a in kana_soup.select(".word_box a", href=True):
                page_link = kana_a['href']
                page_id = self._parse_page_id(page_link)
                if page_id is None:
                    continue
                _, page_path = jitenon.scrape(page_link)
                self._page_map[page_id] = page_path
        pages_len = len(self._page_map)
        print(f"Finished scraping {pages_len} pages")


class JitenonYojiCrawler(_JitenonCrawler):
    def __init__(self, target):
        super().__init__(target)
        self._gojuon_url = "https://yoji.jitenon.jp/cat/gojuon.html"
        self._page_id_pattern = r"([0-9]+)\.html$"


class JitenonKotowazaCrawler(_JitenonCrawler):
    def __init__(self, target):
        super().__init__(target)
        self._gojuon_url = "https://kotowaza.jitenon.jp/cat/gojuon.php"
        self._page_id_pattern = r"([0-9]+)\.php$"


class _MonokakidoCrawler(Crawler):
    def __init__(self, target):
        super().__init__(target)
        self._page_id_pattern = r"^([0-9]+)\.xml$"

    def collect_pages(self, page_dir):
        print(f"Searching for page files in `{page_dir}`")
        for pagefile in os.listdir(page_dir):
            page_id = self._parse_page_id(pagefile)
            if page_id is None or page_id == 0:
                continue
            path = os.path.join(page_dir, pagefile)
            self._page_map[page_id] = path
        pages_len = len(self._page_map)
        print(f"Found {pages_len} page files for processing")


class Smk8Crawler(_MonokakidoCrawler):
    def __init__(self, target):
        super().__init__(target)


class Daijirin2Crawler(_MonokakidoCrawler):
    def __init__(self, target):
        super().__init__(target)
