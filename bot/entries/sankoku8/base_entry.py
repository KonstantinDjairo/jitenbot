import bot.soup as Soup
from bot.entries.base.sanseido_entry import SanseidoEntry
from bot.entries.sankoku8.parse import parse_hyouki_soup


class BaseEntry(SanseidoEntry):
    def __init__(self, target, entry_id):
        super().__init__(target, entry_id)
        self.children = []
        self.phrases = []
        self._hyouki_name = "表記"
        self._midashi_name = None
        self._midashi_kana_name = None

    def _get_headwords(self):
        soup = self.get_page_soup()
        self._delete_unused_nodes(soup)
        readings = self._find_readings(soup)
        expressions = self._find_expressions(soup)
        headwords = {}
        for reading in readings:
            headwords[reading] = []
        if len(readings) == 1:
            reading = readings[0]
            if soup.find(self._midashi_name).find(self._hyouki_name) is None:
                headwords[reading].append(reading)
            for exp in expressions:
                if exp not in headwords[reading]:
                    headwords[reading].append(exp)
        elif len(readings) > 1 and len(expressions) == 0:
            for reading in readings:
                headwords[reading].append(reading)
        elif len(readings) > 1 and len(expressions) == 1:
            if soup.find(self._midashi_name).find(self._hyouki_name) is None:
                for reading in readings:
                    headwords[reading].append(reading)
            expression = expressions[0]
            for reading in readings:
                if expression not in headwords[reading]:
                    headwords[reading].append(expression)
        elif len(readings) > 1 and len(expressions) == len(readings):
            if soup.find(self._midashi_name).find(self._hyouki_name) is None:
                for reading in readings:
                    headwords[reading].append(reading)
            for idx, reading in enumerate(readings):
                exp = expressions[idx]
                if exp not in headwords[reading]:
                    headwords[reading].append(exp)
        else:
            raise Exception()  # shouldn't happen
        return headwords

    def get_part_of_speech_tags(self):
        if self._part_of_speech_tags is not None:
            return self._part_of_speech_tags
        self._part_of_speech_tags = []
        soup = self.get_page_soup()
        for midashi in soup.find_all([self._midashi_name, "見出部要素"]):
            pos_group = midashi.find("品詞G")
            if pos_group is None:
                continue
            for tag in pos_group.find_all("a"):
                if tag.text not in self._part_of_speech_tags:
                    self._part_of_speech_tags.append(tag.text)
        return self._part_of_speech_tags

    def _find_expressions(self, soup):
        expressions = []
        for hyouki in soup.find_all(self._hyouki_name):
            for expression in parse_hyouki_soup(hyouki, [""]):
                expressions.append(expression)
        return expressions

    def _find_readings(self, soup):
        midasi_kana = soup.find(self._midashi_kana_name)
        readings = parse_hyouki_soup(midasi_kana, [""])
        return readings

    def _get_subentry_parameters(self):
        from bot.entries.sankoku8.child_entry import ChildEntry
        from bot.entries.sankoku8.phrase_entry import PhraseEntry
        subentry_parameters = [
            [ChildEntry, ["子項目"], self.children],
            [PhraseEntry, ["句項目"], self.phrases],
        ]
        return subentry_parameters

    @staticmethod
    def _delete_unused_nodes(soup):
        """Remove extra markup elements that appear in the entry
        headword line which are not part of the entry headword"""
        unused_nodes = [
            "語構成", "平板", "アクセント", "表外字マーク", "表外音訓マーク",
            "アクセント分節", "活用分節", "ルビG", "分書"
        ]
        for name in unused_nodes:
            Soup.delete_soup_nodes(soup, name)
