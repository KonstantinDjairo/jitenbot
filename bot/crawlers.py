import os
import re
from bs4 import BeautifulSoup

import bot.scraper as Scraper

from bot.entries.jitenon import JitenonKotowazaEntry
from bot.entries.jitenon import JitenonYojiEntry
from bot.entries.smk8 import Smk8Entry
from bot.entries.daijirin2 import Daijirin2Entry

from bot.yomichan.export import JitenonKotowazaExporter
from bot.yomichan.export import JitenonYojiExporter
from bot.yomichan.export import Smk8Exporter
from bot.yomichan.export import Daijirin2Exporter


class _Crawler():
    def __init__(self, args):
        self._page_dir = args.page_dir
        self._image_dir = args.image_dir
        self._page_map = {}
        self._entries = []

    def read_pages(self):
        pages_len = len(self._page_map)
        items = self._page_map.items()
        for idx, (page_id, page_path) in enumerate(items):
            update = f"Reading page {idx+1}/{pages_len}"
            print(update, end='\r', flush=True)
            entry = self._entry_class(page_id)
            with open(page_path, "r", encoding="utf-8") as f:
                page = f.read()
            entry.set_page(page)
            self._entries.append(entry)
        print()

    def make_yomichan_dictionary(self):
        self._yomi_exporter.export(self._entries, self._image_dir)

    def _parse_page_id(self, page_link):
        m = re.search(self._page_id_pattern, page_link)
        if not m:
            return None
        page_id = int(m.group(1))
        if page_id in self._page_map:
            return None
        return page_id


class _JitenonCrawler(_Crawler):
    def __init__(self, args):
        super().__init__(args)

    def collect_pages(self):
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
    def __init__(self, args):
        super().__init__(args)
        self._entry_class = JitenonYojiEntry
        self._yomi_exporter = JitenonYojiExporter(args.target)
        self._gojuon_url = "https://yoji.jitenon.jp/cat/gojuon.html"
        self._page_id_pattern = r"([0-9]+)\.html$"


class JitenonKotowazaCrawler(_JitenonCrawler):
    def __init__(self, args):
        super().__init__(args)
        self._entry_class = JitenonKotowazaEntry
        self._yomi_exporter = JitenonKotowazaExporter(args.target)
        self._gojuon_url = "https://kotowaza.jitenon.jp/cat/gojuon.php"
        self._page_id_pattern = r"([0-9]+)\.php$"


class _MonokakidoCrawler(_Crawler):
    def __init__(self, args):
        super().__init__(args)
        self._page_id_pattern = r"^([0-9]+)\.xml$"

    def collect_pages(self):
        print(f"Searching for page files in `{self._page_dir}`")
        for pagefile in os.listdir(self._page_dir):
            page_id = self._parse_page_id(pagefile)
            if page_id is None or page_id == 0:
                continue
            path = os.path.join(self._page_dir, pagefile)
            self._page_map[page_id] = path
        pages_len = len(self._page_map)
        print(f"Found {pages_len} page files for processing")


class Smk8Crawler(_MonokakidoCrawler):
    def __init__(self, args):
        super().__init__(args)
        self._entry_class = Smk8Entry
        self._yomi_exporter = Smk8Exporter(args.target)


class Daijirin2Crawler(_MonokakidoCrawler):
    def __init__(self, args):
        super().__init__(args)
        self._entry_class = Daijirin2Entry
        self._yomi_exporter = Daijirin2Exporter(args.target)
