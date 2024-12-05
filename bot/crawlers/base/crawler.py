import re
from abc import ABC, abstractmethod

from bot.factory import new_entry
from bot.factory import new_yomichan_exporter
from bot.factory import new_mdict_exporter


class BaseCrawler(ABC):
    def __init__(self, target):
        self._target = target
        self._page_map = {}
        self._entries = []
        self._page_id_pattern = None

    @abstractmethod
    def collect_pages(self, page_dir):
        raise NotImplementedError

    def read_pages(self):
        pages_len = len(self._page_map)
        items = self._page_map.items()
        for idx, (page_id, page_path) in enumerate(items):
            update = f"\tReading page {idx+1}/{pages_len}"
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

    def make_yomichan_dictionary(self, media_dir, validate):
        exporter = new_yomichan_exporter(self._target)
        exporter.export(self._entries, media_dir, validate)

    def make_mdict_dictionary(self, media_dir, icon_file):
        exporter = new_mdict_exporter(self._target)
        exporter.export(self._entries, media_dir, icon_file)

    def _parse_page_id(self, page_link):
        m = re.search(self._page_id_pattern, page_link)
        if m is None:
            return None
        page_id = int(m.group(1))
        if page_id in self._page_map:
            return None
        return page_id
