import bot.soup as Soup
from bot.data import load_daijirin2_kana_abbreviations
from bot.entries.base.sanseido_entry import SanseidoEntry
import bot.entries.base.expressions as Expressions


class BaseEntry(SanseidoEntry):
    def __init__(self, target, entry_id):
        super().__init__(target, entry_id)
        self.children = []
        self.phrases = []
        self._kana_abbreviations = load_daijirin2_kana_abbreviations()

    def get_part_of_speech_tags(self):
        if self._part_of_speech_tags is not None:
            return self._part_of_speech_tags
        self._part_of_speech_tags = []
        soup = self.get_page_soup()
        for pos_group in soup.find_all("品詞G"):
            if pos_group.parent.name == "大語義":
                self._set_part_of_speech_tags(pos_group)
        return self._part_of_speech_tags

    def _set_part_of_speech_tags(self, el):
        pos_names = ["品詞", "品詞活用", "品詞行", "用法"]
        for child in el.children:
            if child.name is not None:
                self._set_part_of_speech_tags(child)
                continue
            pos = str(child)
            if el.name not in pos_names:
                continue
            elif pos in ["［", "］"]:
                continue
            elif pos in self._part_of_speech_tags:
                continue
            else:
                self._part_of_speech_tags.append(pos)

    def _get_regular_headwords(self, soup):
        self._fill_alts(soup)
        reading = soup.find("見出仮名").text
        expressions = []
        for el in soup.find_all("標準表記"):
            expression = self._clean_expression(el.text)
            if "—" in expression:
                kana_abbrs = self._kana_abbreviations[self.entry_id]
                for abbr in kana_abbrs:
                    expression = expression.replace("—", abbr, 1)
            expressions.append(expression)
        expressions = Expressions.expand_abbreviation_list(expressions)
        if len(expressions) == 0:
            expressions.append(reading)
        headwords = {reading: expressions}
        return headwords

    def _get_subentry_parameters(self):
        from bot.entries.daijirin2.child_entry import ChildEntry
        from bot.entries.daijirin2.phrase_entry import PhraseEntry
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
            "漢字音logo", "活用分節", "連語句活用分節", "語構成",
            "表外字マーク", "表外字マーク", "ルビG"
        ]
        for name in unused_nodes:
            Soup.delete_soup_nodes(soup, name)

    @staticmethod
    def _clean_expression(expression):
        for x in ["〈", "〉", "《", "》", " "]:
            expression = expression.replace(x, "")
        return expression

    @staticmethod
    def _fill_alts(soup):
        for gaiji in soup.find_all(class_="gaiji"):
            if gaiji.name == "img" and gaiji.has_attr("alt"):
                gaiji.name = "span"
                gaiji.string = gaiji.attrs["alt"]
