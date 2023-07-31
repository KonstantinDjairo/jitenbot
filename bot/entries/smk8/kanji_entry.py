from bot.entries.smk8.base_entry import BaseEntry


class KanjiEntry(BaseEntry):
    def get_part_of_speech_tags(self):
        # kanji entries do not contain these tags
        return []

    def _get_headwords(self):
        soup = self.get_page_soup()
        self._delete_unused_nodes(soup)
        self._fill_alts(soup)
        reading = self.__get_parent_reading()
        expressions = self._find_expressions(soup)
        headwords = {reading: expressions}
        return headwords

    def __get_parent_reading(self):
        parent_id = self.SUBENTRY_ID_TO_ENTRY_ID[self.entry_id]
        parent = self.ID_TO_ENTRY[parent_id]
        reading = parent.get_first_reading()
        return reading
