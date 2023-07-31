import os
from bot.time import timestamp
from bot.crawlers.base.crawler import BaseCrawler


class MonokakidoCrawler(BaseCrawler):
    def __init__(self, target):
        super().__init__(target)
        self._page_id_pattern = r"^([0-9]+)\.xml$"

    def collect_pages(self, page_dir):
        print(f"{timestamp()} Searching for page files in `{page_dir}`")
        for pagefile in os.listdir(page_dir):
            page_id = self._parse_page_id(pagefile)
            if page_id is None or page_id == 0:
                continue
            path = os.path.join(page_dir, pagefile)
            self._page_map[page_id] = path
        pages_len = len(self._page_map)
        print(f"{timestamp()} Found {pages_len} page files for processing")
