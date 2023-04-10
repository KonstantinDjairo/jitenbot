from entries.jitenon import Jitenon
import yomichan.grammar as Grammar


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
