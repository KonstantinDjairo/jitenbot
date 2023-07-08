from abc import ABC, abstractmethod


class Entry(ABC):
    ID_TO_ENTRY = {}
    SUBENTRY_ID_TO_ENTRY_ID = {}

    def __init__(self, target, entry_id):
        if entry_id not in self.ID_TO_ENTRY:
            self.ID_TO_ENTRY[entry_id] = self
        else:
            raise Exception(f"Duplicate entry ID: {entry_id}")
        self.target = target
        self.entry_id = entry_id
        self._page = None
        self._headwords = None
        self._part_of_speech_tags = None

    @abstractmethod
    def get_global_identifier(self):
        pass

    @abstractmethod
    def set_page(self, page):
        pass

    @abstractmethod
    def get_page_soup(self):
        pass

    def get_headwords(self):
        if self._headwords is not None:
            return self._headwords
        headwords = self._get_headwords()
        self._add_variant_expressions(headwords)
        self._headwords = headwords
        return headwords

    @abstractmethod
    def _get_headwords(self):
        pass

    @abstractmethod
    def _add_variant_expressions(self, headwords):
        pass

    @abstractmethod
    def get_part_of_speech_tags(self):
        pass

    def get_parent(self):
        if self.entry_id in self.SUBENTRY_ID_TO_ENTRY_ID:
            parent_id = self.SUBENTRY_ID_TO_ENTRY_ID[self.entry_id]
            parent = self.ID_TO_ENTRY[parent_id]
        else:
            parent = None
        return parent

    def get_first_expression(self):
        headwords = self.get_headwords()
        expressions = next(iter(headwords.values()))
        expression = expressions[0]
        return expression

    def get_first_reading(self):
        headwords = self.get_headwords()
        reading = next(iter(headwords.keys()))
        return reading
