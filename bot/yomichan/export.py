import json
import os
import shutil
from pathlib import Path
from datetime import datetime
from platformdirs import user_documents_dir, user_cache_dir

import bot.data as Data


def jitenon_yoji(entries):
    __jitenon(entries, "jitenon-yoji")


def jitenon_kotowaza(entries):
    __jitenon(entries, "jitenon-kotowaza")


def __jitenon(entries, name):
    terms, modified_date, attribution = __terms(entries)
    meta = Data.yomichan_metadata()

    index = meta[name]["index"]
    index["revision"] = f"{name}.{modified_date}"
    index["attribution"] = attribution
    tags = meta[name]["tags"]

    __create_zip(terms, index, tags)


def __terms(entries):
    terms = []
    modified_date = None
    attribution = ""
    for entry in entries:
        if modified_date is None or entry.modified_date > modified_date:
            modified_date = entry.modified_date
            attribution = entry.attribution
        for term in entry.yomichan_terms():
            terms.append(term)
    return terms, modified_date, attribution


def __create_zip(terms, index, tags):
    cache_dir = user_cache_dir("jitenbot")
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    build_directory = os.path.join(cache_dir, f"build_{timestamp}")
    if Path(build_directory).is_dir():
        shutil.rmtree(build_directory)
    os.makedirs(build_directory)

    terms_per_file = 1000
    max_i = int(len(terms) / terms_per_file) + 1
    for i in range(max_i):
        term_file = os.path.join(build_directory, f"term_bank_{i+1}.json")
        with open(term_file, "w", encoding='utf8') as f:
            start = terms_per_file * i
            end = terms_per_file * (i + 1)
            json.dump(terms[start:end], f, indent=4, ensure_ascii=False)

    index_file = os.path.join(build_directory, "index.json")
    with open(index_file, 'w', encoding='utf8') as f:
        json.dump(index, f, indent=4, ensure_ascii=False)

    if len(tags) > 0:
        tag_file = os.path.join(build_directory, "tag_bank_1.json")
        with open(tag_file, 'w', encoding='utf8') as f:
            json.dump(tags, f, indent=4, ensure_ascii=False)

    zip_filename = index["title"]
    zip_file = f"{zip_filename}.zip"
    shutil.make_archive(zip_filename, "zip", build_directory)

    out_dir = os.path.join(user_documents_dir(), "jitenbot")
    out_file = os.path.join(out_dir, zip_file)
    if not Path(out_dir).is_dir():
        os.mkdir(out_dir)
    elif Path(out_file).is_file():
        os.remove(out_file)
    shutil.move(zip_file, out_dir)
    shutil.rmtree(build_directory)
