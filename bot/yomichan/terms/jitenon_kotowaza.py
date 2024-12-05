from bot.yomichan.grammar import sudachi_rules
from bot.yomichan.glossary.jitenon import JitenonKotowazaGlossary
from bot.yomichan.terms.base.jitenon import JitenonTerminator


class Terminator(JitenonTerminator):
    def __init__(self, target):
        super().__init__(target)
        self._glossary_maker = JitenonKotowazaGlossary()

    def _inflection_rules(self, entry, expression):
        return sudachi_rules(expression)

    def _term_tags(self, entry):
        return ""
