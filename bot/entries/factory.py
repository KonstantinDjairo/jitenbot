from bot.targets import Targets

from bot.entries.jitenon import JitenonKokugoEntry
from bot.entries.jitenon import JitenonYojiEntry
from bot.entries.jitenon import JitenonKotowazaEntry
from bot.entries.smk8 import Smk8Entry
from bot.entries.daijirin2 import Daijirin2Entry


def new_entry(target, page_id):
    entry_map = {
        Targets.JITENON_KOKUGO:   JitenonKokugoEntry,
        Targets.JITENON_YOJI:     JitenonYojiEntry,
        Targets.JITENON_KOTOWAZA: JitenonKotowazaEntry,
        Targets.SMK8:             Smk8Entry,
        Targets.DAIJIRIN2:        Daijirin2Entry,
    }
    return entry_map[target](page_id)
