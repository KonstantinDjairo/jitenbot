import bot.entries.base.expressions as Expressions
from bot.entries.base.jitenon_entry import JitenonEntry


class Entry(JitenonEntry):
    def __init__(self, target, entry_id):
        super().__init__(target, entry_id)
        self.origin = ""
        self.kanken_level = ""
        self.category = ""
        self.related_expressions = []

    def _get_column_map(self):
        return {
            "四字熟語": "expression",
            "読み方":   "yomikata",
            "意味":     "definition",
            "異形":     "other_forms",
            "出典":     "origin",
            "漢検級":   "kanken_level",
            "場面用途": "category",
            "類義語":   "related_expressions",
        }

    def _add_variant_expressions(self, headwords):
        for expressions in headwords.values():
            Expressions.add_variant_kanji(expressions)
