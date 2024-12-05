import json
import os
import shutil
import copy
from pathlib import Path
from abc import ABC, abstractmethod

import fastjsonschema
from platformdirs import user_documents_dir, user_cache_dir

from bot.time import timestamp
from bot.data import load_yomichan_metadata
from bot.data import load_yomichan_term_schema
from bot.factory import new_yomichan_terminator


class BaseExporter(ABC):
    def __init__(self, target):
        self._target = target
        self._terminator = new_yomichan_terminator(target)
        self._build_dir = None
        self._terms_per_file = 2000

    def export(self, entries, image_dir, validate):
        self.__init_build_image_dir(image_dir)
        meta = load_yomichan_metadata()
        index = meta[self._target.value]["index"]
        index["revision"] = self._get_revision(entries)
        index["attribution"] = self._get_attribution(entries)
        tags = meta[self._target.value]["tags"]
        terms = self.__get_terms(entries)
        if validate:
            self.__validate_terms(terms)
        self.__make_dictionary(terms, index, tags)

    @abstractmethod
    def _get_revision(self, entries):
        raise NotImplementedError

    @abstractmethod
    def _get_attribution(self, entries):
        raise NotImplementedError

    def _get_build_dir(self):
        if self._build_dir is not None:
            return self._build_dir
        cache_dir = user_cache_dir("jitenbot")
        build_directory = os.path.join(cache_dir, "yomichan_build")
        print(f"{timestamp()} Initializing build directory `{build_directory}`")
        if Path(build_directory).is_dir():
            shutil.rmtree(build_directory)
        os.makedirs(build_directory)
        self._build_dir = build_directory
        return self._build_dir

    def __get_invalid_term_dir(self):
        cache_dir = user_cache_dir("jitenbot")
        log_dir = os.path.join(cache_dir, "invalid_yomichan_terms")
        if Path(log_dir).is_dir():
            shutil.rmtree(log_dir)
        os.makedirs(log_dir)
        return log_dir

    def __init_build_image_dir(self, image_dir):
        build_dir = self._get_build_dir()
        build_img_dir = os.path.join(build_dir, self._target.value)
        if image_dir is not None:
            print(f"{timestamp()} Copying media files to build directory...")
            shutil.copytree(image_dir, build_img_dir)
            print(f"{timestamp()} Finished copying files")
        else:
            os.makedirs(build_img_dir)
        self._terminator.set_image_dir(build_img_dir)

    def __get_terms(self, entries):
        terms = []
        entries_len = len(entries)
        for idx, entry in enumerate(entries):
            update = f"\tCreating Yomichan terms for entry {idx+1}/{entries_len}"
            print(update, end='\r', flush=True)
            new_terms = self._terminator.make_terms(entry)
            for term in new_terms:
                terms.append(term)
        print()
        return terms

    def __validate_terms(self, terms):
        print(f"{timestamp()} Making a copy of term data for validation...")
        terms_copy = copy.deepcopy(terms)  # because validator will alter data!
        term_count = len(terms_copy)
        log_dir = self.__get_invalid_term_dir()
        schema = load_yomichan_term_schema()
        validator = fastjsonschema.compile(schema)
        failure_count = 0
        for idx, term in enumerate(terms_copy):
            update = f"\tValidating term {idx+1}/{term_count}"
            print(update, end='\r', flush=True)
            try:
                validator([term])
            except fastjsonschema.JsonSchemaException:
                failure_count += 1
                term_file = os.path.join(log_dir, f"{idx}.json")
                with open(term_file, "w", encoding='utf8') as f:
                    json.dump([term], f, indent=4, ensure_ascii=False)
        print(f"\n{timestamp()} Finished validating with {failure_count} error{'' if failure_count == 1 else 's'}")
        if failure_count > 0:
            print(f"{timestamp()} Invalid terms saved to `{log_dir}` for debugging")

    def __make_dictionary(self, terms, index, tags):
        self.__write_term_banks(terms)
        self.__write_index(index)
        self.__write_tag_bank(tags)
        self.__write_archive(index["title"])
        self.__rm_build_dir()

    def __write_term_banks(self, terms):
        print(f"{timestamp()} Exporting {len(terms)} JSON terms")
        build_dir = self._get_build_dir()
        max_i = int(len(terms) / self._terms_per_file) + 1
        for i in range(max_i):
            update = f"\tWriting terms to term bank {i+1}/{max_i}"
            print(update, end='\r', flush=True)
            start = self._terms_per_file * i
            end = self._terms_per_file * (i + 1)
            term_file = os.path.join(build_dir, f"term_bank_{i+1}.json")
            with open(term_file, "w", encoding='utf8') as f:
                json.dump(terms[start:end], f, indent=4, ensure_ascii=False)
        print()

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
        print(f"{timestamp()} Archiving data to {archive_format.upper()} file...")
        out_dir = os.path.join(user_documents_dir(), "jitenbot", "yomichan")
        if not Path(out_dir).is_dir():
            os.makedirs(out_dir)
        out_file = f"{filename}.{archive_format}"
        out_filepath = os.path.join(out_dir, out_file)
        if Path(out_filepath).is_file():
            os.remove(out_filepath)
        base_filename = os.path.join(out_dir, filename)
        build_dir = self._get_build_dir()
        shutil.make_archive(base_filename, archive_format, build_dir)
        print(f"{timestamp()} Dictionary file saved to `{out_filepath}`")

    def __rm_build_dir(self):
        build_dir = self._get_build_dir()
        shutil.rmtree(build_dir)
