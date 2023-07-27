from abc import abstractmethod
from bs4 import BeautifulSoup

from bot.entries.base.entry import Entry
import bot.entries.base.expressions as Expressions


class SanseidoEntry(Entry):
    def set_page(self, page):
        page = self._decompose_subentries(page)
        self._page = page

    def get_page_soup(self):
        soup = BeautifulSoup(self._page, "xml")
        return soup

    def get_global_identifier(self):
        parent_part = format(self.entry_id[0], '06')
        child_part = hex(self.entry_id[1]).lstrip('0x').zfill(4).upper()
        return f"@{self.target.value}-{parent_part}-{child_part}"

    def _decompose_subentries(self, page):
        soup = BeautifulSoup(page, features="xml")
        for x in self._get_subentry_parameters():
            subentry_class, tags, subentry_list = x
            for tag in tags:
                tag_soup = soup.find(tag)
                while tag_soup is not None:
                    tag_soup.name = "項目"
                    subentry_id = self.id_string_to_entry_id(tag_soup.attrs["id"])
                    self.SUBENTRY_ID_TO_ENTRY_ID[subentry_id] = self.entry_id
                    subentry = subentry_class(self.target, subentry_id)
                    page = tag_soup.decode()
                    subentry.set_page(page)
                    subentry_list.append(subentry)
                    tag_soup.decompose()
                    tag_soup = soup.find(tag)
        return soup.decode()

    @abstractmethod
    def _get_subentry_parameters(self):
        pass

    def _add_variant_expressions(self, headwords):
        for expressions in headwords.values():
            Expressions.add_variant_kanji(expressions)
            Expressions.add_fullwidth(expressions)
            Expressions.remove_iteration_mark(expressions)
            Expressions.add_iteration_mark(expressions)

    @staticmethod
    def id_string_to_entry_id(id_string):
        parts = id_string.split("-")
        if len(parts) == 1:
            return (int(parts[0]), 0)
        elif len(parts) == 2:
            # subentries have a hexadecimal part
            return (int(parts[0]), int(parts[1], 16))
        else:
            raise Exception(f"Invalid entry ID: {id_string}")
