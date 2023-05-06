import json
import os
import shutil
from pathlib import Path
from datetime import datetime
from platformdirs import user_documents_dir, user_cache_dir

from bot.data import load_yomichan_metadata
from bot.yomichan.terms.factory import new_terminator


class Exporter:
    def __init__(self, target):
        self._target = target
        self._terminator = new_terminator(target)
        self._build_dir = None
        self._terms_per_file = 2000

    def export(self, entries, image_dir):
        self.__init_build_image_dir(image_dir)
        meta = load_yomichan_metadata()
        index = meta[self._target.value]["index"]
        index["revision"] = self._get_revision(entries)
        index["attribution"] = self._get_attribution(entries)
        tags = meta[self._target.value]["tags"]
        terms = self.__get_terms(entries)
        self.__make_dictionary(terms, index, tags)

    def _get_build_dir(self):
        if self._build_dir is not None:
            return self._build_dir
        cache_dir = user_cache_dir("jitenbot")
        build_directory = os.path.join(cache_dir, "yomichan_build")
        if Path(build_directory).is_dir():
            shutil.rmtree(build_directory)
        os.makedirs(build_directory)
        self._build_dir = build_directory
        return self._build_dir

    def __init_build_image_dir(self, image_dir):
        build_dir = self._get_build_dir()
        build_img_dir = os.path.join(build_dir, self._target.value)
        if image_dir is not None:
            print("Copying image files to build directory...")
            shutil.copytree(image_dir, build_img_dir)
        else:
            os.makedirs(build_img_dir)
        self._terminator.set_image_dir(build_img_dir)

    def __get_terms(self, entries):
        terms = []
        entries_len = len(entries)
        for idx, entry in enumerate(entries):
            update = f"Creating Yomichan terms for entry {idx+1}/{entries_len}"
            print(update, end='\r', flush=True)
            new_terms = self._terminator.make_terms(entry)
            for term in new_terms:
                terms.append(term)
        print()
        return terms

    def __make_dictionary(self, terms, index, tags):
        print(f"Exporting {len(terms)} Yomichan terms...")
        self.__write_term_banks(terms)
        self.__write_index(index)
        self.__write_tag_bank(tags)
        self.__write_archive(index["title"])
        self.__rm_build_dir()

    def __write_term_banks(self, terms):
        build_dir = self._get_build_dir()
        max_i = int(len(terms) / self._terms_per_file) + 1
        for i in range(max_i):
            term_file = os.path.join(build_dir, f"term_bank_{i+1}.json")
            with open(term_file, "w", encoding='utf8') as f:
                start = self._terms_per_file * i
                end = self._terms_per_file * (i + 1)
                json.dump(terms[start:end], f, indent=4, ensure_ascii=False)

    def __write_index(self, index):
        build_dir = self._get_build_dir()
        index_file = os.path.join(build_dir, "index.json")
        with open(index_file, 'w', encoding='utf8') as f:
            json.dump(index, f, indent=4, ensure_ascii=False)

    def __write_tag_bank(self, tags):
        if len(tags) == 0:
            return
        build_dir = self._get_build_dir()
        tag_file = os.path.join(build_dir, "tag_bank_1.json")
        with open(tag_file, 'w', encoding='utf8') as f:
            json.dump(tags, f, indent=4, ensure_ascii=False)

    def __write_archive(self, filename):
        archive_format = "zip"
        out_dir = os.path.join(user_documents_dir(), "jitenbot")
        if not Path(out_dir).is_dir():
            os.makedirs(out_dir)
        out_file = f"{filename}.{archive_format}"
        out_filepath = os.path.join(out_dir, out_file)
        if Path(out_filepath).is_file():
            os.remove(out_filepath)
        base_filename = os.path.join(out_dir, filename)
        build_dir = self._get_build_dir()
        shutil.make_archive(base_filename, archive_format, build_dir)
        print(f"Dictionary file saved to {out_filepath}")

    def __rm_build_dir(self):
        build_dir = self._get_build_dir()
        shutil.rmtree(build_dir)


class JitenonExporter(Exporter):
    def __init__(self, target):
        super().__init__(target)

    def _get_revision(self, entries):
        modified_date = None
        for entry in entries:
            if modified_date is None or entry.modified_date > modified_date:
                modified_date = entry.modified_date
        revision = f"{self._target.value};{modified_date}"
        return revision

    def _get_attribution(self, entries):
        modified_date = None
        for entry in entries:
            if modified_date is None or entry.modified_date > modified_date:
                attribution = entry.attribution
        return attribution


class JitenonKokugoExporter(JitenonExporter):
    def __init__(self, target):
        super().__init__(target)


class JitenonYojiExporter(JitenonExporter):
    def __init__(self, target):
        super().__init__(target)


class JitenonKotowazaExporter(JitenonExporter):
    def __init__(self, target):
        super().__init__(target)


class Smk8Exporter(Exporter):
    def __init__(self, target):
        super().__init__(target)

    def _get_revision(self, entries):
        timestamp = datetime.now().strftime("%Y-%m-%d")
        return f"{self._target.value};{timestamp}"

    def _get_attribution(self, entries):
        return "© Sanseido Co., LTD. 2020"


class Daijirin2Exporter(Exporter):
    def __init__(self, target):
        super().__init__(target)

    def _get_revision(self, entries):
        timestamp = datetime.now().strftime("%Y-%m-%d")
        return f"{self._target.value};{timestamp}"

    def _get_attribution(self, entries):
        return "© Sanseido Co., LTD. 2019"
