from bot.yomichan.grammar import sudachi_rules
from bot.yomichan.terms.terminator import Terminator

from bot.yomichan.glossary.jitenon import JitenonKokugoGlossary
from bot.yomichan.glossary.jitenon import JitenonYojiGlossary
from bot.yomichan.glossary.jitenon import JitenonKotowazaGlossary


class JitenonTerminator(Terminator):
    def __init__(self, name):
        super().__init__(name)

    def _definition_tags(self, entry):
        return None

    def _glossary(self, entry):
        if entry.entry_id in self._glossary_cache:
            return self._glossary_cache[entry.entry_id]
        glossary = self._glossary_maker.make_glossary(entry, self._image_dir)
        self._glossary_cache[entry.entry_id] = glossary
        return glossary

    def _sequence(self, entry):
        return entry.entry_id

    def _link_glossary_parameters(self, entry):
        return []

    def _subentry_lists(self, entry):
        return []


class JitenonKokugoTerminator(JitenonTerminator):
    def __init__(self, name):
        super().__init__(name)
        self._glossary_maker = JitenonKokugoGlossary()

    def _inflection_rules(self, entry, expression):
        return sudachi_rules(expression)

    def _term_tags(self, entry):
        return ""


class JitenonYojiTerminator(JitenonTerminator):
    def __init__(self, name):
        super().__init__(name)
        self._glossary_maker = JitenonYojiGlossary()

    def _inflection_rules(self, entry, expression):
        return ""

    def _term_tags(self, entry):
        tags = entry.kankenkyuu.split("/")
        return " ".join(tags)


class JitenonKotowazaTerminator(JitenonTerminator):
    def __init__(self, name):
        super().__init__(name)
        self._glossary_maker = JitenonKotowazaGlossary()

    def _inflection_rules(self, entry, expression):
        return sudachi_rules(expression)

    def _term_tags(self, entry):
        return ""
