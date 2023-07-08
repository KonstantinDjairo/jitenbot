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
import sys
import argparse
import subprocess
from bot.targets import Targets
from bot.crawlers.factory import new_crawler


def filename(f):
    if not os.path.isfile(f):
        raise argparse.ArgumentTypeError(f"`{f}` is not a valid filename")
    elif not os.access(f, os.R_OK):
        raise argparse.ArgumentTypeError(f"Cannot access file `{f}`")
    else:
        return f


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
        epilog="See README.md for details regarding media directory structures",
    )
    parser.add_argument(
        "target",
        choices=target_names,
        help="name of dictionary to convert",
    )
    parser.add_argument(
        "-p", "--page-dir",
        help="path to directory containing XML page files",
        type=directory,
    )
    parser.add_argument(
        "-m", "--media-dir",
        help="path to directory containing media folders (gaiji, graphics, audio, etc.)",
        type=directory,
    )
    parser.add_argument(
        "-i", "--mdict-icon",
        help="path to icon file to be used with MDict",
        type=filename,
    )
    parser.add_argument(
        "--no-yomichan-export",
        help="skip export of dictionary data to Yomichan format",
        action='store_true',
    )
    parser.add_argument(
        "--no-mdict-export",
        help="skip export of dictionary data to MDict format",
        action='store_true',
    )
    args = parser.parse_args()
    return args


def test_mdict():
    try:
        subprocess.run(
            ["mdict", "--version"],
            check=True,
            stdout=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        print("Could not find `mdict` pack tool.")
        print("Ensure that mdict-utils is installed and")
        print("included in the environment PATH.\n")
        print("Mdict export functionality may also be")
        print("disabled with the --no-mdict-export flag.")
        sys.exit()


def main():
    target_names = [x.value for x in Targets]
    args = parse_args(target_names)
    if not args.no_mdict_export:
        test_mdict()
    selected_target = Targets(args.target)
    crawler = new_crawler(selected_target)
    crawler.collect_pages(args.page_dir)
    crawler.read_pages()
    if not args.no_yomichan_export:
        crawler.make_yomichan_dictionary(args.media_dir)
    if not args.no_mdict_export:
        crawler.make_mdict_dictionary(args.media_dir, args.mdict_icon)


if __name__ == "__main__":
    main()
