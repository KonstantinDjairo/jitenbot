from bot.entries.jitenon import JitenonEntry


class JitenonYojiEntry(JitenonEntry):
    columns = {
        "四字熟語": ["expression", ""],
        "読み方":   ["yomikata", ""],
        "意味":     ["imi", ""],
        "出典":     ["shutten", ""],
        "漢検級":   ["kankenkyuu", ""],
        "場面用途": ["bamenyouto", ""],
        "異形":     ["ikei", []],
        "類義語":   ["ruigigo", []],
    }

    def __init__(self, sequence):
        super().__init__(sequence)

    def yomichan_terms(self):
        terms = []
        for idx, headword in enumerate(self._headwords()):
            (expression, reading) = headword
            definition_tags = None
            inflection_rules = ""
            score = -idx
            glossary = self.yomichan_glossary
            sequence = self.sequence
            term_tags = self.__term_tags()
            term = [
                expression, reading, definition_tags, inflection_rules,
                score, glossary, sequence, term_tags
            ]
            terms.append(term)
        return terms

    def __term_tags(self):
        tags = self.kankenkyuu.replace(" ", "").split("/")
        return " ".join(tags)
