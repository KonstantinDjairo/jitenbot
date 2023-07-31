from bot.yomichan.glossary.jitenon import JitenonYojiGlossary
from bot.yomichan.terms.base.jitenon import JitenonTerminator


class Terminator(JitenonTerminator):
    def __init__(self, target):
        super().__init__(target)
        self._glossary_maker = JitenonYojiGlossary()

    def _inflection_rules(self, entry, expression):
        return ""

    def _term_tags(self, entry):
        tags = entry.kanken_level.split("/")
        return " ".join(tags)
