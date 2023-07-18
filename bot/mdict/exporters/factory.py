from bot.targets import Targets

from bot.mdict.exporters.export import JitenonKokugoExporter
from bot.mdict.exporters.export import JitenonYojiExporter
from bot.mdict.exporters.export import JitenonKotowazaExporter
from bot.mdict.exporters.export import Smk8Exporter
from bot.mdict.exporters.export import Daijirin2Exporter
from bot.mdict.exporters.export import Sankoku8Exporter


def new_mdict_exporter(target):
    exporter_map = {
        Targets.JITENON_KOKUGO:   JitenonKokugoExporter,
        Targets.JITENON_YOJI:     JitenonYojiExporter,
        Targets.JITENON_KOTOWAZA: JitenonKotowazaExporter,
        Targets.SMK8:             Smk8Exporter,
        Targets.DAIJIRIN2:        Daijirin2Exporter,
        Targets.SANKOKU8:         Sankoku8Exporter,
    }
    return exporter_map[target](target)
