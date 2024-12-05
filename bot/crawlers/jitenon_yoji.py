from bot.crawlers.base.jitenon import JitenonCrawler


class Crawler(JitenonCrawler):
    def __init__(self, target):
        super().__init__(target)
        self._gojuon_url = "https://yoji.jitenon.jp/cat/gojuon.html"
        self._page_id_pattern = r"([0-9]+)\.html$"
