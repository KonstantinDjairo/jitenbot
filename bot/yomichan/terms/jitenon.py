import bot.yomichan.grammar as Grammar
from bot.yomichan.terms.terminator import Terminator
from bot.yomichan.glossary.jitenon import make_glossary


class JitenonTerminator(Terminator):
    def __init__(self):
        super().__init__()

    def _definition_tags(self, entry):
        return None

    def _glossary(self, entry):
        if entry.entry_id in self.glossary_cache:
            return self.glossary_cache[entry.entry_id]
        glossary = make_glossary(entry)
        self.glossary_cache[entry.entry_id] = glossary
        return glossary

    def _sequence(self, entry):
        return entry.entry_id

    def _link_glossary_parameters(self, entry):
        return []

    def _subentry_lists(self, entry):
        return []


class JitenonYojiTerminator(JitenonTerminator):
    def __init__(self):
        super().__init__()

    def _inflection_rules(self, entry, expression):
        return ""

    def _term_tags(self, entry):
        tags = entry.kankenkyuu.split("/")
        return " ".join(tags)


class JitenonKotowazaTerminator(JitenonTerminator):
    def __init__(self):
        super().__init__()

    def _inflection_rules(self, entry, expression):
        return Grammar.sudachi_rules(expression)

    def _term_tags(self, entry):
        return ""
