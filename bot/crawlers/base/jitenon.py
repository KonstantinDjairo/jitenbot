from bs4 import BeautifulSoup

from bot.crawlers.scrapers.jitenon import Jitenon as JitenonScraper
from bot.crawlers.base.crawler import BaseCrawler


class JitenonCrawler(BaseCrawler):
    def __init__(self, target):
        super().__init__(target)
        self._gojuon_url = None

    def collect_pages(self, page_dir):
        print("Scraping jitenon.jp")
        jitenon = JitenonScraper()
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
