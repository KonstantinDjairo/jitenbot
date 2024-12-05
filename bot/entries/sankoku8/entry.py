from bot.entries.sankoku8.base_entry import BaseEntry
from bot.entries.sankoku8.preprocess import preprocess_page


class Entry(BaseEntry):
    def __init__(self, target, page_id):
        entry_id = (page_id, 0)
        super().__init__(target, entry_id)
        self._midashi_name = "見出部"
        self._midashi_kana_name = "見出仮名"

    def set_page(self, page):
        page = preprocess_page(page)
        super().set_page(page)
