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
import bot.crawlers as Crawlers


choices = {
    'all': Crawlers.run_all,
    'jitenon-yoji': Crawlers.jitenon_yoji,
    'jitenon-kotowaza': Crawlers.jitenon_kotowaza,
}


def parse_args():
    parser = argparse.ArgumentParser(
        prog='jitenbot',
        description='Crawl and convert Japanese web dictionaries.')
    parser.add_argument(
        'target',
        choices=choices.keys(),
        help='website to crawl')
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    crawler = choices[args.target]
    crawler()


if __name__ == "__main__":
    main()
