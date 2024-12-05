from bot.entries.daijirin2.base_entry import BaseEntry


class ChildEntry(BaseEntry):
    def _get_headwords(self):
        soup = self.get_page_soup()
        self._delete_unused_nodes(soup)
        headwords = self._get_regular_headwords(soup)
        return headwords
