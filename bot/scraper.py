import time
import requests
import re
import os
import hashlib
from datetime import datetime
from pathlib import Path

from platformdirs import user_cache_dir
from urllib.parse import urlparse
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from bot.data import load_config


class Scraper():
    def __init__(self):
        self._config = load_config()
        pattern = r"^(?:([A-Za-z0-9.\-]+)\.)?" + self.domain + r"$"
        self.netloc_re = re.compile(pattern)
        self.__set_session()

    def scrape(self, urlstring):
        url = urlparse(urlstring, scheme='https://', allow_fragments=True)
        self.__validate_url(url)
        cache_path = self.__cache_path(url)
        html = self.__read_cache(cache_path)
        if html is None:
            html = self.__get(urlstring)
            with open(cache_path, "w") as f:
                f.write(html)
        else:
            print("Discovering cached files...", end='\r', flush=True)
        return html, cache_path

    def __set_session(self):
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        headers = self._config["http-request-headers"]
        self.session = requests.Session()
        self.session.mount("https://", adapter)
        self.session.headers.update(headers)

    def __validate_url(self, url):
        valid = False
        if self.netloc_re.match(url.netloc):
            valid = True
        # may add more validators later
        if not valid:
            raise Exception(f"Invalid URL: {url.geturl()}")

    def __cache_path(self, url):
        class_name = self.__class__.__name__.lower()
        cache_dir = user_cache_dir("jitenbot")
        cache_dir = os.path.join(cache_dir, class_name)
        netloc_match = self.netloc_re.match(url.netloc)
        if netloc_match.group(1) is not None:
            subdomain = netloc_match.group(1)
            cache_dir = os.path.join(cache_dir, subdomain)
        paths = re.findall(r"/([^/]+)", url.path)
        if len(paths) < 1:
            raise Exception(f"Invalid path in URL: {url.geturl()}")
        for x in paths[:len(paths)-1]:
            cache_dir = os.path.join(cache_dir, x)
        if not Path(cache_dir).is_dir():
            os.makedirs(cache_dir)
        basename = paths[-1].replace(".", "_")
        urlstring_hash = hashlib.md5(url.geturl().encode()).hexdigest()
        filename = f"{basename}-{urlstring_hash}.html"
        cache_path = os.path.join(cache_dir, filename)
        return cache_path

    def __read_cache(self, cache_path):
        if Path(cache_path).is_file():
            with open(cache_path, "r") as f:
                file_contents = f.read()
        else:
            file_contents = None
        return file_contents

    def __get(self, urlstring):
        delay = 10
        time.sleep(delay)
        now = datetime.now().strftime("%H:%M:%S")
        print(f"{now} scraping {urlstring} ...", end='')
        try:
            response = self.session.get(urlstring, timeout=10)
            print("OK")
            return response.text
        except Exception:
            print("failed")
            print("resetting session and trying again")
            self.__set_session()
            response = self.session.get(urlstring, timeout=10)
            return response.text


class Jitenon(Scraper):
    def __init__(self):
        self.domain = r"jitenon\.jp"
        super().__init__()
