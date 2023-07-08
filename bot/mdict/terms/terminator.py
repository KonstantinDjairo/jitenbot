from abc import abstractmethod, ABC


class Terminator(ABC):
    def __init__(self, target):
        self._target = target
        self._glossary_cache = {}
        self._media_dir = None

    def set_media_dir(self, media_dir):
        self._media_dir = media_dir

    def make_terms(self, entry):
        gid = entry.get_global_identifier()
        glossary = self.__full_glossary(entry)
        terms = [[gid, glossary]]
        keys = set()
        headwords = entry.get_headwords()
        for reading, expressions in headwords.items():
            if len(expressions) == 0:
                keys.add(reading)
            for expression in expressions:
                if expression.strip() == "":
                    keys.add(reading)
                    continue
                keys.add(expression)
                if reading.strip() == "":
                    continue
                if reading != expression:
                    keys.add(f"{reading}【{expression}】")
                else:
                    keys.add(reading)
        link = f"@@@LINK={gid}"
        for key in keys:
            if key.strip() != "":
                terms.append([key, link])
        for subentries in self._subentry_lists(entry):
            for subentry in subentries:
                for term in self.make_terms(subentry):
                    terms.append(term)
        return terms

    def __full_glossary(self, entry):
        glossary = []
        style_link = f"<link rel='stylesheet' href='{self._target.value}.css' type='text/css'>"
        glossary.append(style_link)
        glossary.append(self._glossary(entry))

        for x in self._link_glossary_parameters(entry):
            (subentries, list_title) = x
            if len(subentries) == 0:
                continue
            items = []
            for subentry in subentries:
                exp = subentry.get_first_expression()
                gid = subentry.get_global_identifier()
                item = f"<li><a href='entry://{gid}'>{exp}</a></li>"
                items.append(item)
            link_glossary = f"<div data-child-links='{list_title}'><span>{list_title}</span><ul>{''.join(items)}</ul></div>"
            glossary.append(link_glossary)
        return "\n".join(glossary)

    @abstractmethod
    def _glossary(self, entry):
        pass

    @abstractmethod
    def _link_glossary_parameters(self, entry):
        pass

    @abstractmethod
    def _subentry_lists(self, entry):
        pass
