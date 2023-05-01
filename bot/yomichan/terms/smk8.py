from bot.data import load_yomichan_inflection_categories

from bot.entries.smk8 import Smk8KanjiEntry as KanjiEntry
from bot.entries.smk8 import Smk8PhraseEntry as PhraseEntry

from bot.yomichan.terms.terminator import Terminator
from bot.yomichan.glossary.smk8 import make_glossary
from bot.yomichan.grammar import sudachi_rules, tags_to_rules


class Smk8Terminator(Terminator):
    def __init__(self, name):
        super().__init__(name)
        categories = load_yomichan_inflection_categories()
        self._inflection_categories = categories[name]

    def _definition_tags(self, entry):
        if isinstance(entry, KanjiEntry):
            return "造"
        else:
            return ""

    def _inflection_rules(self, entry, expression):
        if isinstance(entry, PhraseEntry):
            return sudachi_rules(expression)
        elif isinstance(entry, KanjiEntry):
            return ""
        pos_tags = entry.get_part_of_speech_tags()
        if len(pos_tags) == 0:
            return sudachi_rules(expression)
        else:
            return tags_to_rules(expression, pos_tags, self._inflection_categories)

    def _glossary(self, entry):
        if entry.entry_id in self._glossary_cache:
            return self._glossary_cache[entry.entry_id]
        glossary = make_glossary(entry, self._image_dir)
        self._glossary_cache[entry.entry_id] = glossary
        return glossary

    def _sequence(self, entry):
        return entry.entry_id[0] * 100000 + entry.entry_id[1]

    def _term_tags(self, entry):
        return ""

    def _link_glossary_parameters(self, entry):
        return [
            [entry.children, "子"],
            [entry.phrases, "句"]
        ]

    def _subentry_lists(self, entry):
        return [
            entry.children,
            entry.phrases,
            entry.kanjis
        ]
