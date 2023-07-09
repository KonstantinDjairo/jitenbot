import os
import sys
import json
import csv
from functools import cache
from pathlib import Path

from platformdirs import user_config_dir


@cache
def get_adobe_glyph(code):
    adobe_glyphs = __load_adobe_glyphs()
    override_adobe_glyphs = __load_override_adobe_glyphs()
    if code in override_adobe_glyphs:
        return override_adobe_glyphs[code]
    if len(adobe_glyphs[code]) > 1:
        raise Exception(f"Multiple glyphs available for code {code}")
    return adobe_glyphs[code][0]


@cache
def load_config():
    config_dir = user_config_dir("jitenbot")
    if not Path(config_dir).is_dir():
        os.makedirs(config_dir)
    config_file = os.path.join(config_dir, "config.json")
    if Path(config_file).is_file():
        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)
    else:
        config = __load_default_config()
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
    return config


@cache
def load_yomichan_inflection_categories():
    file_name = os.path.join("yomichan", "inflection_categories.json")
    data = __load_json(file_name)
    return data


@cache
def load_yomichan_metadata():
    file_name = os.path.join("yomichan", "index.json")
    data = __load_json(file_name)
    return data


@cache
def load_variant_kanji():
    def loader(data, row):
        data[row[0]] = row[1]
    file_name = os.path.join("entries", "variant_kanji.csv")
    data = {}
    __load_csv(file_name, loader, data)
    return data


@cache
def load_smk8_phrase_readings():
    def loader(data, row):
        entry_id = (int(row[0]), int(row[1]))
        reading = row[2]
        data[entry_id] = reading
    file_name = os.path.join("entries", "smk8", "phrase_readings.csv")
    data = {}
    __load_csv(file_name, loader, data)
    return data


@cache
def load_daijirin2_phrase_readings():
    def loader(data, row):
        entry_id = (int(row[0]), int(row[1]))
        reading = row[2]
        data[entry_id] = reading
    file_name = os.path.join("entries", "daijirin2", "phrase_readings.csv")
    data = {}
    __load_csv(file_name, loader, data)
    return data


@cache
def load_daijirin2_kana_abbreviations():
    def loader(data, row):
        entry_id = (int(row[0]), int(row[1]))
        abbreviations = []
        for abbr in row[2:]:
            if abbr.strip() != "":
                abbreviations.append(abbr)
        data[entry_id] = abbreviations
    file_name = os.path.join("entries", "daijirin2", "kana_abbreviations.csv")
    data = {}
    __load_csv(file_name, loader, data)
    return data


@cache
def load_yomichan_name_conversion(target):
    file_name = os.path.join("yomichan", "name_conversion", f"{target.value}.json")
    data = __load_json(file_name)
    return data


@cache
def load_mdict_name_conversion(target):
    file_name = os.path.join("mdict", "name_conversion", f"{target.value}.json")
    data = __load_json(file_name)
    return data


@cache
def __load_default_config():
    file_name = "default_config.json"
    data = __load_json(file_name)
    return data


@cache
def __load_adobe_glyphs():
    def loader(data, row):
        if row[0].startswith("#"):
            return
        character = chr(int(row[0].split(" ")[0], 16))
        code = int(row[2].removeprefix(" CID+"))
        if code in data:
            if character not in data[code]:
                data[code].append(character)
        else:
            data[code] = [character]
    file_name = os.path.join("entries", "adobe", "Adobe-Japan1_sequences.txt")
    data = {}
    __load_csv(file_name, loader, data, delim=';')
    return data


@cache
def __load_override_adobe_glyphs():
    file_name = os.path.join("entries", "adobe", "override_glyphs.json")
    json_data = __load_json(file_name)
    data = {}
    for key, val in json_data.items():
        data[int(key)] = val
    return data


def __load_json(file_name):
    file_path = os.path.join("data", file_name)
    if not Path(file_path).is_file():
        print(f"Missing data file: {file_path}")
        sys.exit(1)
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def __load_csv(file_name, loader, data, delim=',', quote='"'):
    file_path = os.path.join("data", file_name)
    if not Path(file_path).is_file():
        print(f"Missing data file: {file_path}")
        sys.exit(1)
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=delim, quotechar=quote)
        for row in reader:
            loader(data, row)
    return data
