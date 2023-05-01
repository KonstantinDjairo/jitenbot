class Terminator:
    def __init__(self, name):
        self._name = name
        self._glossary_cache = {}
        self._image_dir = None

    def set_image_dir(self, image_dir):
        self._image_dir = image_dir

    def make_terms(self, entry):
        terms = []
        headwords = entry.get_headwords()
        for reading, expressions in headwords.items():
            for expression in expressions:
                definition_tags = self._definition_tags(entry)
                inflection_rules = self._inflection_rules(entry, expression)
                score = -len(terms)
                glossary = self._glossary(entry)
                sequence = self._sequence(entry)
                term_tags = self._term_tags(entry)
                term = [
                    expression, reading, definition_tags, inflection_rules,
                    score, glossary, sequence, term_tags
                ]
                terms.append(term)

                for x in self._link_glossary_parameters(entry):
                    (subentries, definition_tags) = x
                    if len(subentries) == 0:
                        continue
                    score = -len(terms)
                    glossary = self.__links_glossary(subentries)
                    term = [
                        expression, reading, definition_tags, inflection_rules,
                        score, glossary, sequence, term_tags
                    ]
                    terms.append(term)

        for subentries in self._subentry_lists(entry):
            for subentry in subentries:
                for term in self.make_terms(subentry):
                    terms.append(term)
        return terms

    @staticmethod
    def __links_glossary(subentries):
        glossary = []
        for subentry in subentries:
            exp = subentry.get_first_expression()
            gloss = {
                "type": "structured-content",
                "content": {
                    "tag": "a",
                    "href": f"?query={exp}&wildcards=off",
                    "content": exp,
                }
            }
            glossary.append(gloss)
        return glossary
