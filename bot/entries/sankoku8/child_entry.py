from bot.entries.sankoku8.base_entry import BaseEntry


class ChildEntry(BaseEntry):
    def __init__(self, target, page_id):
        super().__init__(target, page_id)
        self._midashi_name = "子見出部"
        self._midashi_kana_name = "子見出仮名"
