from bot.targets import Targets

from bot.yomichan.terms.jitenon import JitenonKokugoTerminator
from bot.yomichan.terms.jitenon import JitenonYojiTerminator
from bot.yomichan.terms.jitenon import JitenonKotowazaTerminator
from bot.yomichan.terms.smk8 import Smk8Terminator
from bot.yomichan.terms.daijirin2 import Daijirin2Terminator
from bot.yomichan.terms.sankoku8 import Sankoku8Terminator


def new_terminator(target):
    terminator_map = {
        Targets.JITENON_KOKUGO:   JitenonKokugoTerminator,
        Targets.JITENON_YOJI:     JitenonYojiTerminator,
        Targets.JITENON_KOTOWAZA: JitenonKotowazaTerminator,
        Targets.SMK8:             Smk8Terminator,
        Targets.DAIJIRIN2:        Daijirin2Terminator,
        Targets.SANKOKU8:         Sankoku8Terminator,
    }
    return terminator_map[target](target)
