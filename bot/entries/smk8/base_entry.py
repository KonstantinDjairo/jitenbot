import bot.soup as Soup
import bot.entries.base.expressions as Expressions
from bot.entries.base.sanseido_entry import SanseidoEntry


class BaseEntry(SanseidoEntry):
    def __init__(self, target, entry_id):
        super().__init__(target, entry_id)
        self.children = []
        self.phrases = []
        self.kanjis = []

    def get_part_of_speech_tags(self):
        if self._part_of_speech_tags is not None:
            return self._part_of_speech_tags
        self._part_of_speech_tags = []
        soup = self.get_page_soup()
        headword_info = soup.find("見出要素")
        if headword_info is None:
            return self._part_of_speech_tags
        for tag in headword_info.find_all("品詞M"):
            if tag.text not in self._part_of_speech_tags:
                self._part_of_speech_tags.append(tag.text)
        return self._part_of_speech_tags

    def _find_reading(self, soup):
        midasi_kana = soup.find("見出仮名")
        reading = midasi_kana.text
        for x in [" ", "・"]:
            reading = reading.replace(x, "")
        return reading

    def _find_expressions(self, soup):
        clean_expressions = []
        for expression in soup.find_all("標準表記"):
            clean_expression = self._clean_expression(expression.text)
            clean_expressions.append(clean_expression)
        expressions = Expressions.expand_abbreviation_list(clean_expressions)
        return expressions

    def _get_subentry_parameters(self):
        from bot.entries.smk8.child_entry import ChildEntry
        from bot.entries.smk8.phrase_entry import PhraseEntry
        from bot.entries.smk8.kanji_entry import KanjiEntry
        subentry_parameters = [
            [ChildEntry, ["子項目F", "子項目"], self.children],
            [PhraseEntry, ["句項目F", "句項目"], self.phrases],
            [KanjiEntry, ["造語成分項目"], self.kanjis],
        ]
        return subentry_parameters

    @staticmethod
    def _delete_unused_nodes(soup):
        """Remove extra markup elements that appear in the entry
        headword line which are not part of the entry headword"""
        unused_nodes = [
            "表音表記", "表外音訓マーク", "表外字マーク", "ルビG"
        ]
        for name in unused_nodes:
            Soup.delete_soup_nodes(soup, name)

    @staticmethod
    def _clean_expression(expression):
        for x in ["〈", "〉", "｛", "｝", "…", " "]:
            expression = expression.replace(x, "")
        return expression

    @staticmethod
    def _fill_alts(soup):
        for elm in soup.find_all(["親見出仮名", "親見出表記"]):
            elm.string = elm.attrs["alt"]
        for gaiji in soup.find_all("外字"):
            gaiji.string = gaiji.img.attrs["alt"]
