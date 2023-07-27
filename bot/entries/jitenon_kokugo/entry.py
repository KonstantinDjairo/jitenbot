from bot.entries.base.jitenon_entry import JitenonEntry
import bot.entries.base.expressions as Expressions


class Entry(JitenonEntry):
    def __init__(self, target, entry_id):
        super().__init__(target, entry_id)
        self.example = ""
        self.alt_expression = ""
        self.antonym = ""
        self.attachments = ""
        self.compounds = ""
        self.related_words = ""

    def _get_column_map(self):
        return {
            "言葉":   "expression",
            "読み方": "yomikata",
            "意味":   "definition",
            "例文":   "example",
            "別表記": "alt_expression",
            "対義語": "antonym",
            "活用":   "attachments",
            "用例":   "compounds",
            "類語":   "related_words",
        }

    def _get_headwords(self):
        headwords = {}
        for reading in self.yomikata.split("・"):
            if reading not in headwords:
                headwords[reading] = []
            for expression in self.expression.split("・"):
                headwords[reading].append(expression)
            if self.alt_expression.strip() != "":
                for expression in self.alt_expression.split("・"):
                    headwords[reading].append(expression)
        return headwords

    def _add_variant_expressions(self, headwords):
        for expressions in headwords.values():
            Expressions.add_variant_kanji(expressions)
            Expressions.add_fullwidth(expressions)
            Expressions.remove_iteration_mark(expressions)
            Expressions.add_iteration_mark(expressions)
