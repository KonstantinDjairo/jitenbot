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

import os
import argparse
from bot.targets import Targets
from bot.crawlers.factory import new_crawler


def directory(d):
    if not os.path.isdir(d):
        raise argparse.ArgumentTypeError(f"`{d}` is not a valid directory")
    elif not os.access(d, os.R_OK):
        raise argparse.ArgumentTypeError(f"Cannot access directory `{d}`")
    else:
        return d


def parse_args(target_names):
    parser = argparse.ArgumentParser(
        prog="jitenbot",
        description="Convert Japanese dictionary files to new formats.",
    )
    parser.add_argument(
        "target",
        choices=target_names,
        help="name of dictionary to convert"
    )
    parser.add_argument(
        "-p", "--page-dir",
        help="path to directory containing XML page files",
        type=directory
    )
    parser.add_argument(
        "-i", "--image-dir",
        help="path to directory containing image folders (gaiji, graphics, etc.)",
        type=directory
    )
    args = parser.parse_args()
    return args


def main():
    target_names = [x.value for x in Targets]
    args = parse_args(target_names)
    selected_target = Targets(args.target)
    crawler = new_crawler(selected_target)
    crawler.collect_pages(args.page_dir)
    crawler.read_pages()
    crawler.make_yomichan_dictionary(args.image_dir)


if __name__ == "__main__":
    main()
