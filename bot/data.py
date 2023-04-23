import os
import sys
import json
import csv
from pathlib import Path

from platformdirs import user_config_dir


def load_config():
    config_dir = user_config_dir("jitenbot")
    if not Path(config_dir).is_dir():
        os.makedirs(config_dir)
    config_file = os.path.join(config_dir, "config.json")
    if Path(config_file).is_file():
        with open(config_file, "r") as f:
            config = json.load(f)
    else:
        config = __load_default_config()
        with open(config_file, "w") as f:
            json.dump(config, f, indent=4)
    return config


def load_yomichan_inflection_categories():
    file_name = "yomichan_inflection_categories.json"
    data = __load_json(file_name)
    return data


def load_yomichan_metadata():
    file_name = "yomichan_metadata.json"
    data = __load_json(file_name)
    return data


def load_variant_kanji():
    def loader(data, row):
        data[row[0]] = row[1]
    file_name = "variant_kanji.csv"
    data = {}
    __load_csv(file_name, loader, data)
    return data


def __load_default_config():
    file_name = "default_config.json"
    data = __load_json(file_name)
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
