from bot.entries.smk8.kanji_entry import KanjiEntry
from bot.entries.smk8.phrase_entry import PhraseEntry
from bot.yomichan.terms.base.terminator import BaseTerminator
from bot.yomichan.glossary.smk8 import make_glossary
from bot.yomichan.grammar import sudachi_rules, tags_to_rules


class Terminator(BaseTerminator):
    def __init__(self, target):
        super().__init__(target)

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
