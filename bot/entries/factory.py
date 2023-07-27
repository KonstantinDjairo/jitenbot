import importlib


def new_entry(target, page_id):
    module_path = f"bot.entries.{target.name.lower()}.entry"
    module = importlib.import_module(module_path)
    return module.Entry(target, page_id)
