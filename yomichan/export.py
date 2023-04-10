import json
import os
import shutil
import uuid
from pathlib import Path


def jitenon_yoji(entries):
    terms, modified_date, attribution = __terms(entries)
    index = {
        "title": "四字熟語辞典オンライン",
        "revision": f"jitenon-yoji.{modified_date}",
        "sequenced": True,
        "format": 3,
        "url": "https://yoji.jitenon.jp/",
        "attribution": attribution,
    }
    tags = [
        ["１級", "frequent", 0, "漢字検定（漢検）１級の四字熟語", 0],
        ["準１級", "frequent", 0, "漢字検定（漢検）準１級の四字熟語", 0],
        ["２級", "frequent", 0, "漢字検定（漢検）２級の四字熟語", 0],
        ["準２級", "frequent", 0, "漢字検定（漢検）準２級の四字熟語", 0],
        ["３級", "frequent", 0, "漢字検定（漢検）３級の四字熟語", 0],
        ["４級", "frequent", 0, "漢字検定（漢検）４級の四字熟語", 0],
        ["５級", "frequent", 0, "漢字検定（漢検）５級の四字熟語", 0],
    ]
    __create_zip(terms, index, tags)


def jitenon_kotowaza(entries):
    terms, modified_date, attribution = __terms(entries)
    index = {
        "title": "故事・ことわざ・慣用句オンライン",
        "revision": f"jitenon-kotowaza.{modified_date}",
        "sequenced": True,
        "format": 3,
        "url": "https://kotowaza.jitenon.jp/",
        "attribution": attribution,
    }
    __create_zip(terms, index)


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


def __create_zip(terms, index, tags=[]):
    build_directory = str(uuid.uuid4())
    os.mkdir(build_directory)

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
    out_dir = "output"
    out_file = os.path.join(out_dir, zip_file)
    if not Path(out_dir).is_dir():
        os.mkdir(out_dir)
    elif Path(out_file).is_file():
        os.remove(out_file)
    shutil.move(zip_file, out_dir)
    shutil.rmtree(build_directory)
