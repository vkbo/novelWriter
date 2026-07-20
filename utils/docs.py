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

from utils.common import ROOT_DIR, extractVersion, formatVersion, splitVersion, systemCall


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


def buildDocs(args: argparse.Namespace | None = None, *, pdf: bool = False) -> None:
    """Build the documentation files, either as HTML or PDF."""
    print("")
    print("Building Docs Manuals" if pdf else "Building HTML Docs")
    print("=====================" if pdf else "==================")
    print("")

    bldRoot = ROOT_DIR / "dist_doc" / "html"
    docsDir = ROOT_DIR / "docs"
    locsDir = ROOT_DIR / "docs" / "source" / "locales"
    pdfFile = ROOT_DIR / "docs" / "build" / "latex" / "manual.pdf"
    locsDir.mkdir(exist_ok=True)
    bldRoot.mkdir(exist_ok=True, parents=True)
    locConf = tomllib.loads((locsDir / "config.toml").read_text(encoding="utf-8"))

    currVersion = extractVersion()[0]
    major, minor, _ = splitVersion(currVersion)
    intVersion = major * 100 + minor
    cutoffVersion = intVersion - 200

    lang = args.lang if args else ["all"]
    build = []
    if lang == ["all"]:
        build = ["en"] + [i.stem for i in locsDir.iterdir() if i.is_dir()]
    else:
        build = lang

    for code in build:
        outDir = bldRoot / code
        env = os.environ.copy()
        env["SPHINX_I18N_VERSION"] = formatVersion(currVersion)
        cmd = "make clean latexpdf" if pdf else "make clean html"
        pdfName = "manual.pdf"
        if code != "en":
            if code not in locConf:
                print(f"ERROR: No config for language code '{code}' in config.toml")
                continue

            locVersion = locConf[code].get("version", "")
            locMajor, locMinor, _ = splitVersion(locVersion)
            locIntVersion = locMajor * 100 + locMinor
            if locIntVersion < cutoffVersion:
                print(f"WARNING: Skipping build for '{code}' because version is too old ({locVersion})")
                continue

            env["SPHINX_I18N_VERSION"] = formatVersion(locVersion)
            env["SPHINX_I18N_AUTHORS"] = ", ".join(locConf[code].get("authors", []))
            cmd += f" -e SPHINXOPTS=\"-D language='{code}'\""
            pdfName = f"manual_{code}.pdf"

        try:
            log = subprocess.check_output(cmd, cwd=docsDir, env=env, shell=True)
            print("\n".join(log.decode("utf-8", errors="replace").rstrip().splitlines()[-11:]))
            print("")
            if pdf:
                print("")
                pdfFile.rename(ROOT_DIR / "novelwriter" / "assets" / pdfName)
            else:
                if outDir.exists():
                    shutil.rmtree(outDir)
                (docsDir / "build" / "html").rename(outDir)
        except subprocess.CalledProcessError as ex:
            print(f"ERROR: Build returned error code {ex.returncode}")

    print("")


def buildHtmlDocs(args: argparse.Namespace | None = None) -> None:
    """Build the documentation files."""
    buildDocs(args, pdf=False)


def buildPdfDocAssets(args: argparse.Namespace | None = None) -> None:
    """Build the documentation PDF files."""
    buildDocs(args, pdf=True)
