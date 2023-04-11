from bot.entries.jitenon import Jitenon
import bot.yomichan.grammar as Grammar


class JitenonKotowaza(Jitenon):
    columns = {
        "言葉":   ["expression", ""],
        "読み方": ["yomikata", ""],
        "意味":   ["imi", ""],
        "出典":   ["shutten", ""],
        "例文":   ["reibun", ""],
        "異形":   ["ikei", []],
        "類句":   ["ruiku", []],
    }

    def __init__(self, sequence):
        Jitenon.__init__(self, sequence)

    def yomichan_terms(self):
        terms = []
        for idx, headword in enumerate(self._headwords()):
            (expression, reading) = headword
            definition_tags = None
            inflection_rules = Grammar.sudachi_rules(expression, reading)
            score = -idx
            glossary = self.yomichan_glossary
            sequence = self.sequence
            term_tags = ""
            term = [
                expression, reading, definition_tags, inflection_rules,
                score, glossary, sequence, term_tags
            ]
            terms.append(term)
        return terms

    def _headwords(self):
        if self.expression == "金棒引き・鉄棒引き":
            return [["金棒引き", "かなぼうひき"],
                    ["鉄棒引き", "かなぼうひき"]]
        else:
            return Jitenon._headwords(self)
