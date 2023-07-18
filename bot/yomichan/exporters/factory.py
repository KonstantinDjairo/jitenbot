from bot.targets import Targets

from bot.yomichan.exporters.export import JitenonKokugoExporter
from bot.yomichan.exporters.export import JitenonYojiExporter
from bot.yomichan.exporters.export import JitenonKotowazaExporter
from bot.yomichan.exporters.export import Smk8Exporter
from bot.yomichan.exporters.export import Daijirin2Exporter
from bot.yomichan.exporters.export import Sankoku8Exporter


def new_yomi_exporter(target):
    exporter_map = {
        Targets.JITENON_KOKUGO:   JitenonKokugoExporter,
        Targets.JITENON_YOJI:     JitenonYojiExporter,
        Targets.JITENON_KOTOWAZA: JitenonKotowazaExporter,
        Targets.SMK8:             Smk8Exporter,
        Targets.DAIJIRIN2:        Daijirin2Exporter,
        Targets.SANKOKU8:         Sankoku8Exporter,
    }
    return exporter_map[target](target)
