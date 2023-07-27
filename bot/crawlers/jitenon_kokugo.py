import re
from bs4 import BeautifulSoup

from bot.crawlers.base.crawler import BaseCrawler
from bot.crawlers.scrapers.jitenon import Jitenon as JitenonScraper


class Crawler(BaseCrawler):
    def __init__(self, target):
        super().__init__(target)
        self._gojuon_url = "https://kokugo.jitenon.jp/cat/gojuonindex.php"
        self._page_id_pattern = r"word/p([0-9]+)$"

    def collect_pages(self, page_dir):
        jitenon = JitenonScraper()
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
