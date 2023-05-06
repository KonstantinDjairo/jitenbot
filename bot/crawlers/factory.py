from bot.targets import Targets

from bot.crawlers.crawlers import JitenonKokugoCrawler
from bot.crawlers.crawlers import JitenonYojiCrawler
from bot.crawlers.crawlers import JitenonKotowazaCrawler
from bot.crawlers.crawlers import Smk8Crawler
from bot.crawlers.crawlers import Daijirin2Crawler


def new_crawler(target):
    crawler_map = {
        Targets.JITENON_KOKUGO:   JitenonKokugoCrawler,
        Targets.JITENON_YOJI:     JitenonYojiCrawler,
        Targets.JITENON_KOTOWAZA: JitenonKotowazaCrawler,
        Targets.SMK8:             Smk8Crawler,
        Targets.DAIJIRIN2:        Daijirin2Crawler,
    }
    return crawler_map[target](target)
