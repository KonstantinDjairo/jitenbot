from bot.entries.base.jitenon_entry import JitenonEntry
import bot.entries.base.expressions as Expressions


class Entry(JitenonEntry):
    def __init__(self, target, entry_id):
        super().__init__(target, entry_id)
        self.origin = ""
        self.example = ""
        self.related_expressions = []

    def _get_column_map(self):
        return {
            "言葉":   "expression",
            "読み方": "yomikata",
            "意味":   "definition",
            "異形":   "other_forms",
            "出典":   "origin",
            "例文":   "example",
            "類句":   "related_expressions",
        }

    def _get_headwords(self):
        if self.expression == "金棒引き・鉄棒引き":
            headwords = {
                "かなぼうひき": ["金棒引き", "鉄棒引き"]
            }
        else:
            headwords = super()._get_headwords()
        return headwords

    def _add_variant_expressions(self, headwords):
        for expressions in headwords.values():
            Expressions.add_variant_kanji(expressions)
            Expressions.add_fullwidth(expressions)
