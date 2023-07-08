from bot.targets import Targets

from bot.mdict.terms.jitenon import JitenonKokugoTerminator
from bot.mdict.terms.jitenon import JitenonYojiTerminator
from bot.mdict.terms.jitenon import JitenonKotowazaTerminator
from bot.mdict.terms.smk8 import Smk8Terminator
from bot.mdict.terms.daijirin2 import Daijirin2Terminator


def new_terminator(target):
    terminator_map = {
        Targets.JITENON_KOKUGO:   JitenonKokugoTerminator,
        Targets.JITENON_YOJI:     JitenonYojiTerminator,
        Targets.JITENON_KOTOWAZA: JitenonKotowazaTerminator,
        Targets.SMK8:             Smk8Terminator,
        Targets.DAIJIRIN2:        Daijirin2Terminator,
    }
    return terminator_map[target](target)
