from abc import ABC, abstractmethod


class Entry(ABC):
    def __init__(self, entry_id):
        self.entry_id = entry_id
        self._page = None
        self._headwords = None
        self._part_of_speech_tags = None

    @abstractmethod
    def set_page(self, page):
        pass

    @abstractmethod
    def get_page_soup(self):
        pass

    @abstractmethod
    def get_headwords(self):
        pass

    @abstractmethod
    def get_part_of_speech_tags(self):
        pass

    def get_first_expression(self):
        headwords = self.get_headwords()
        expressions = next(iter(headwords.values()))
        expression = expressions[0]
        return expression

    def get_first_reading(self):
        headwords = self.get_headwords()
        reading = next(iter(headwords.keys()))
        return reading
