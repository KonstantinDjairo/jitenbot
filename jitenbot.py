""" jitenbot
Copyright (C) 2023 Stephen Kraus

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""

import argparse
from bot.crawlers import JitenonYojiCrawler
from bot.crawlers import JitenonKotowazaCrawler


crawlers = {
    "jitenon-yoji": JitenonYojiCrawler,
    "jitenon-kotowaza": JitenonKotowazaCrawler,
}


def add_target_argument(parser):
    target_argument_params = {
        "choices": crawlers.keys(),
        "help": "Dictionary to convert."
    }
    parser.add_argument("target", **target_argument_params)


def make_parser():
    argument_parser_params = {
        "prog": "jitenbot",
        "description": "Convert Japanese dictionary files to new formats.",
    }
    parser = argparse.ArgumentParser(**argument_parser_params)
    return parser


def parse_args():
    parser = make_parser()
    add_target_argument(parser)
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    crawler_class = crawlers[args.target]
    crawler = crawler_class()
    crawler.crawl()
    crawler.read_entries()
    crawler.make_yomichan_dictionary()


if __name__ == "__main__":
    main()
