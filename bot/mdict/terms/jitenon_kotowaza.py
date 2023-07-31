from bot.mdict.terms.base.jitenon import JitenonTerminator
from bot.mdict.glossary.jitenon import JitenonKotowazaGlossary


class Terminator(JitenonTerminator):
    def __init__(self, target):
        super().__init__(target)
        self._glossary_maker = JitenonKotowazaGlossary()
