from bot.crawlers.base.jitenon import JitenonCrawler


class Crawler(JitenonCrawler):
    def __init__(self, target):
        super().__init__(target)
        self._gojuon_url = "https://kotowaza.jitenon.jp/cat/gojuon.php"
        self._page_id_pattern = r"([0-9]+)\.php$"
