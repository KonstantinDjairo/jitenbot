# pylint: disable=too-few-public-methods

import subprocess
import os
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from datetime import datetime
from platformdirs import user_documents_dir, user_cache_dir

from bot.mdict.terms.factory import new_terminator


class Exporter(ABC):
    def __init__(self, target):
        self._target = target
        self._terminator = new_terminator(target)
        self._build_dir = None
        self._build_media_dir = None
        self._description_file = None
        self._out_dir = None

    def export(self, entries, media_dir, icon_file):
        self._init_build_media_dir(media_dir)
        self._init_description_file(entries)
        self._write_mdx_file(entries)
        self._write_mdd_file()
        self._write_icon_file(icon_file)
        self._write_css_file()
        self._rm_build_dir()

    def _get_build_dir(self):
        if self._build_dir is not None:
            return self._build_dir
        cache_dir = user_cache_dir("jitenbot")
        build_directory = os.path.join(cache_dir, "mdict_build")
        print(f"Initializing build directory `{build_directory}`")
        if Path(build_directory).is_dir():
            shutil.rmtree(build_directory)
        os.makedirs(build_directory)
        self._build_dir = build_directory
        return self._build_dir

    def _init_build_media_dir(self, media_dir):
        build_dir = self._get_build_dir()
        build_media_dir = os.path.join(build_dir, self._target.value)
        if media_dir is not None:
            print("Copying media files to build directory...")
            shutil.copytree(media_dir, build_media_dir)
        else:
            os.makedirs(build_media_dir)
        css_file = self._get_css_file()
        shutil.copy(css_file, build_media_dir)
        self._terminator.set_media_dir(build_media_dir)
        self._build_media_dir = build_media_dir

    def _init_description_file(self, entries):
        description_template_file = self._get_description_template_file()
        with open(description_template_file, "r", encoding="utf8") as f:
            description = f.read()
        description = description.replace(
            "{{revision}}", self._get_revision(entries))
        description = description.replace(
            "{{attribution}}", self._get_attribution(entries))
        build_dir = self._get_build_dir()
        description_file = os.path.join(
            build_dir, f"{self._target.value}.mdx.description.html")
        with open(description_file, "w", encoding="utf8") as f:
            f.write(description)
        self._description_file = description_file

    def _write_mdx_file(self, entries):
        terms = self._get_terms(entries)
        print(f"Exporting {len(terms)} Mdict keys...")
        out_dir = self._get_out_dir()
        out_file = os.path.join(out_dir, f"{self._target.value}.mdx")
        params = [
            "mdict",
            "-a", self._get_term_file(terms),
            "--title", self._get_title_file(),
            "--description", self._description_file,
            out_file
        ]
        subprocess.run(params, check=True)

    def _get_terms(self, entries):
        terms = []
        entries_len = len(entries)
        for idx, entry in enumerate(entries):
            update = f"Creating Mdict terms for entry {idx+1}/{entries_len}"
            print(update, end='\r', flush=True)
            new_terms = self._terminator.make_terms(entry)
            for term in new_terms:
                terms.append(term)
        print()
        return terms

    def _write_mdd_file(self):
        out_dir = self._get_out_dir()
        out_file = os.path.join(out_dir, f"{self._target.value}.mdd")
        params = [
            "mdict",
            "-a", self._build_media_dir,
            "--title", self._get_title_file(),
            "--description", self._description_file,
            out_file
        ]
        subprocess.run(params, check=True)

    def _write_icon_file(self, icon_file):
        premade_icon_file = self._get_premade_icon_file()
        out_dir = self._get_out_dir()
        out_file = os.path.join(out_dir, f"{self._target.value}.png")
        if icon_file is not None and Path(icon_file).is_file():
            shutil.copy(icon_file, out_file)
        elif Path(premade_icon_file).is_file():
            shutil.copy(premade_icon_file, out_file)

    def _write_css_file(self):
        css_file = self._get_css_file()
        out_dir = self._get_out_dir()
        shutil.copy(css_file, out_dir)

    def _get_out_dir(self):
        if self._out_dir is not None:
            return self._out_dir
        out_dir = os.path.join(
            user_documents_dir(), "jitenbot", "mdict", self._target.value)
        print(f"Initializing output directory `{out_dir}`")
        if Path(out_dir).is_dir():
            shutil.rmtree(out_dir)
        os.makedirs(out_dir)
        self._out_dir = out_dir
        return out_dir

    def _get_term_file(self, terms):
        build_dir = self._get_build_dir()
        term_file = os.path.join(build_dir, f"{self._target.value}.mdx.txt")
        with open(term_file, "w", encoding="utf8") as f:
            for term in terms:
                f.write("\n".join(term))
                f.write("\n</>\n")
        return term_file

    def _get_title_file(self):
        return os.path.join(
            "data", "mdict", "title",
            f"{self._target.value}.mdx.title.html")

    def _get_css_file(self):
        return os.path.join(
            "data", "mdict", "css",
            f"{self._target.value}.css")

    def _get_premade_icon_file(self):
        return os.path.join(
            "data", "mdict", "icon",
            f"{self._target.value}.png")

    def _get_description_template_file(self):
        return os.path.join(
            "data", "mdict", "description",
            f"{self._target.value}.mdx.description.html")

    def _rm_build_dir(self):
        build_dir = self._get_build_dir()
        shutil.rmtree(build_dir)

    @abstractmethod
    def _get_revision(self, entries):
        pass

    @abstractmethod
    def _get_attribution(self, entries):
        pass


class _JitenonExporter(Exporter):
    def _get_revision(self, entries):
        modified_date = None
        for entry in entries:
            if modified_date is None or entry.modified_date > modified_date:
                modified_date = entry.modified_date
        revision = modified_date.strftime("%Y年%m月%d日閲覧")
        return revision

    def _get_attribution(self, entries):
        modified_date = None
        for entry in entries:
            if modified_date is None or entry.modified_date > modified_date:
                attribution = entry.attribution
        return attribution


class JitenonKokugoExporter(_JitenonExporter):
    pass


class JitenonYojiExporter(_JitenonExporter):
    pass


class JitenonKotowazaExporter(_JitenonExporter):
    pass


class _MonokakidoExporter(Exporter):
    def _get_revision(self, entries):
        timestamp = datetime.now().strftime("%Y年%m月%d日作成")
        return timestamp


class Smk8Exporter(_MonokakidoExporter):
    def _get_attribution(self, entries):
        return "© Sanseido Co., LTD. 2020"


class Daijirin2Exporter(_MonokakidoExporter):
    def _get_attribution(self, entries):
        return "© Sanseido Co., LTD. 2019"
