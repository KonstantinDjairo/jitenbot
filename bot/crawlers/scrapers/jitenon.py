import re
from bot.crawlers.scrapers.scraper import BaseScraper


class Jitenon(BaseScraper):
    def _get_netloc_re(self):
        domain = r"jitenon\.jp"
        pattern = r"^(?:([A-Za-z0-9.\-]+)\.)?" + domain + r"$"
        netloc_re = re.compile(pattern)
        return netloc_re
