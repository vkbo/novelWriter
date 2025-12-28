"""
novelWriter – Documentation
===========================

This file is a part of novelWriter
Copyright (C) 2025 Veronica Berglyd Olsen and novelWriter contributors

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""  # noqa
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import tomllib

from utils.common import ROOT_DIR, systemCall


def updateDocsTranslationSources(args: argparse.Namespace) -> None:
    """Build the documentation .po files."""
    print("")
    print("Building Docs Translation Files")
    print("===============================")
    print("")

    docsDir = ROOT_DIR / "docs"
    locsDir = ROOT_DIR / "docs" / "source" / "locales"
    locsDir.mkdir(exist_ok=True)

    print("Generating POT Files")
    systemCall(["make", "gettext"], cwd=docsDir)
    print("")

    lang = args.lang
    update = []
    if lang == ["all"]:
        update = [i.stem for i in locsDir.iterdir() if i.is_dir()]
    else:
        update = lang

    print("Generating PO Files")
    print("Languages: ", update)
    print("")

    for code in update:
        systemCall(["sphinx-intl", "update", "-p", "build/gettext", "-l", code], cwd=docsDir)
        print("")

    print("Done")
    print("")


def buildHtmlDocs(args: argparse.Namespace | None = None) -> None:
    """Build the documentation files."""
    print("")
    print("Building HTML Docs")
    print("==================")
    print("")

    bldRoot = ROOT_DIR / "dist_doc" / "html"
    docsDir = ROOT_DIR / "docs"
    locsDir = ROOT_DIR / "docs" / "source" / "locales"
    locsDir.mkdir(exist_ok=True)
    bldRoot.mkdir(exist_ok=True, parents=True)
    locConf = tomllib.loads((locsDir / "config.toml").read_text(encoding="utf-8"))

    lang = args.lang if args else ["all"]
    build = []
    if lang == ["all"]:
        build = ["en"] + [i.stem for i in locsDir.iterdir() if i.is_dir()]
    else:
        build = lang

    for code in build:
        outDir = bldRoot / code
        env = os.environ.copy()
        cmd = "make clean html"
        if code != "en":
            if code not in locConf:
                print(f"ERROR: No config for language code '{code}' in config.toml")
            env["SPHINX_I18N_VERSION"] = locConf[code].get("version", "")
            env["SPHINX_I18N_AUTHORS"] = ", ".join(locConf[code].get("authors", []))
            cmd += f" -e SPHINXOPTS=\"-D language='{code}'\""

        if (ex := subprocess.call(cmd, cwd=docsDir, env=env, shell=True)) == 0:
            print("")
            if outDir.exists():
                shutil.rmtree(outDir)
            (docsDir / "build" / "html").rename(outDir)
        else:
            raise Exception(f"Build returned error code {ex}")

    print("")


def buildPdfDocAssets(args: argparse.Namespace | None = None) -> None:
    """Build the documentation PDF files."""
    print("")
    print("Building Docs Manuals")
    print("=====================")
    print("")

    docsDir = ROOT_DIR / "docs"
    locsDir = ROOT_DIR / "docs" / "source" / "locales"
    pdfFile = ROOT_DIR / "docs" / "build" / "latex" / "manual.pdf"
    locsDir.mkdir(exist_ok=True)
    locConf = tomllib.loads((locsDir / "config.toml").read_text(encoding="utf-8"))

    lang = args.lang if args else ["all"]
    build = []
    if lang == ["all"]:
        build = ["en"] + [i.stem for i in locsDir.iterdir() if i.is_dir()]
    else:
        build = lang

    for code in build:
        env = os.environ.copy()
        cmd = "make clean latexpdf"
        name = "manual.pdf"
        if code != "en":
            if code not in locConf:
                print(f"ERROR: No config for language code '{code}' in config.toml")
            env["SPHINX_I18N_VERSION"] = locConf[code].get("version", "")
            env["SPHINX_I18N_AUTHORS"] = ", ".join(locConf[code].get("authors", []))
            cmd += f" -e SPHINXOPTS=\"-D language='{code}'\""
            name = f"manual_{code}.pdf"

        if (ex := subprocess.call(cmd, cwd=docsDir, env=env, shell=True)) == 0:
            print("")
            pdfFile.rename(ROOT_DIR / "novelwriter" / "assets" / name)
        else:
            raise Exception(f"Build returned error code {ex}")

    print("")
