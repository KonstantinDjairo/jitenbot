import importlib


def new_crawler(target):
    module_path = f"bot.crawlers.{target.name.lower()}"
    module = importlib.import_module(module_path)
    return module.Crawler(target)


def new_entry(target, page_id):
    module_path = f"bot.entries.{target.name.lower()}.entry"
    module = importlib.import_module(module_path)
    return module.Entry(target, page_id)


def new_yomichan_exporter(target):
    module_path = f"bot.yomichan.exporters.{target.name.lower()}"
    module = importlib.import_module(module_path)
    return module.Exporter(target)


def new_yomichan_terminator(target):
    module_path = f"bot.yomichan.terms.{target.name.lower()}"
    module = importlib.import_module(module_path)
    return module.Terminator(target)


def new_mdict_exporter(target):
    module_path = f"bot.mdict.exporters.{target.name.lower()}"
    module = importlib.import_module(module_path)
    return module.Exporter(target)


def new_mdict_terminator(target):
    module_path = f"bot.mdict.terms.{target.name.lower()}"
    module = importlib.import_module(module_path)
    return module.Terminator(target)
