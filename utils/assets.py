"""
novelWriter - Assets
====================

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
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

from pathlib import Path

from utils.common import ROOT_DIR, writeFile
from utils.docs import buildPdfDocAssets


def _normaliseTsLocations(tsFile: Path) -> tuple[int, int]:
    """Strip volatile TS line locations and merge duplicate file locations."""
    tree = ET.parse(tsFile)
    root = tree.getroot()

    nLines = 0
    nMerged = 0

    for message in root.findall("./context/message"):
        seenFiles: set[str] = set()
        for location in list(message.findall("location")):
            if "line" in location.attrib:
                del location.attrib["line"]
                nLines += 1

            if (filename := location.attrib.get("filename", "")) in seenFiles:
                message.remove(location)
                nMerged += 1
            else:
                seenFiles.add(filename)

    if nLines > 0 or nMerged > 0:
        ET.indent(tree, space="  ")
        header = '<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE TS>\n'
        xmlBody = ET.tostring(root, encoding="unicode", short_empty_elements=True)
        tsFile.write_text(f"{header}{xmlBody}\n", encoding="utf-8")

    return nLines, nMerged


def buildSampleZip(args: argparse.Namespace | None = None) -> None:
    """Bundle the sample project into a single zip file to be saved into
    the novelwriter/assets folder for further bundling into builds.
    """
    print("")
    print("Building Sample ZIP File")
    print("========================")
    print("")

    srcSample = ROOT_DIR / "sample"
    dstSample = ROOT_DIR / "novelwriter" / "assets" / "sample.zip"

    if srcSample.is_dir():
        dstSample.unlink(missing_ok=True)
        with zipfile.ZipFile(dstSample, mode="w", compression=zipfile.ZIP_DEFLATED, compresslevel=3) as zipObj:
            print("Compressing: nwProject.nwx")
            zipObj.write(srcSample / "nwProject.nwx", "nwProject.nwx")
            for doc in (srcSample / "content").iterdir():
                print(f"Compressing: content/{doc.name}")
                zipObj.write(doc, f"content/{doc.name}")

    else:
        print("Error: Could not find sample project source directory.")
        sys.exit(1)

    print("")
    print(f"Built file: {dstSample}")
    print("")


def importI18nUpdates(args: argparse.Namespace) -> None:
    """Import new translation files from a zip file."""
    print("")
    print("Import Updated Translations")
    print("===========================")
    print("")

    fileName = Path(args.file).absolute()
    if not fileName.is_file():
        print("File not found ...")
        sys.exit(1)

    dstPath = ROOT_DIR / "novelwriter" / "assets" / "i18n"
    srcPath = ROOT_DIR / "i18n"

    print(f"Loading file: {fileName}")
    with zipfile.ZipFile(fileName) as zipObj:
        for item in zipObj.namelist():
            if item.startswith("nw_") and item.endswith(".ts"):
                zipObj.extract(item, srcPath)
                print(f"Extracted: {item} > {srcPath / item}")
            elif item.startswith("project_") and item.endswith(".json"):
                zipObj.extract(item, dstPath)
                print(f"Extracted: {item} > {dstPath / item}")
            else:
                print(f"Skipped: {item}")

    print("")


def updateTranslationSources(args: argparse.Namespace) -> None:
    """Build the lang.ts files for Qt Linguist."""
    print("")
    print("Building Qt Translation Files")
    print("=============================")

    try:
        from PyQt6.lupdate.lupdate import lupdate
    except ImportError:
        print("ERROR: This command requires lupdate from PyQt6")
        print("On Debian/Ubuntu, install: pyqt6-dev-tools")
        sys.exit(1)

    print("")
    print("Scanning Source Tree:")
    print("")

    sources = list((ROOT_DIR / "novelwriter").glob("**/*.py"))
    for source in sources:
        print(source.relative_to(ROOT_DIR))

    print("")
    print("TS Files to Update:")
    print("")

    translations = []
    for item in [Path(str(f)).absolute() for f in args.files]:
        if not (item.name.startswith("nw_") and item.suffix == ".ts"):
            print(f"Skipped: {item}")
            continue

        if item.is_file():
            translations.append(item)
            print(f"Added: {item}")
        elif item.exists():
            continue
        else:  # Create an empty new language file
            langCode = item.name[3:-3]
            writeFile(
                item,
                (
                    '<?xml version="1.0" encoding="utf-8"?>\n'
                    "<!DOCTYPE TS>\n"
                    f'<TS version="2.0" language="{langCode}" sourcelanguage="en_GB"/>\n'
                ),
            )
            translations.append(item)
            print(f"Created: {item}")

    print("")
    print("Updating Language Files:")
    print("")

    lupdate(
        sources=[str(f) for f in sources],
        translation_files=[str(f) for f in translations],
        no_obsolete=True,
        no_summary=False,
    )

    print("")
    print("Normalising TS Location Metadata:")
    print("")

    for item in translations:
        nLines, nMerged = _normaliseTsLocations(item)
        if nLines > 0 or nMerged > 0:
            print(f"Updated: {item} ({nLines} line refs, {nMerged} merged)")
        else:
            print(f"No Change: {item}")

    print("")


def getLReleaseExec() -> str | None:
    """Look for the lrelease executable."""
    for entry in ["lrelease-qt6", "lrelease"]:
        if subprocess.call(f"type {entry}", shell=True) == 0:
            return entry
    return None


def buildTranslationAssets(args: argparse.Namespace | None = None) -> None:
    """Build the lang.qm files for Qt Linguist."""
    print("")
    print("Building Qt Localisation Files")
    print("==============================")

    print("")
    print("TS Files to Build:")
    print("")

    srcDir = ROOT_DIR / "i18n"
    dstDir = ROOT_DIR / "novelwriter" / "assets" / "i18n"

    srcList = []
    for item in srcDir.iterdir():
        if item.is_file() and item.suffix == ".ts" and item.name != "nw_base.ts":
            srcList.append(item)
            print(item)

    print("")
    print("Building Translation Files:")
    print("")

    try:
        if lrelease := getLReleaseExec():
            subprocess.call([lrelease, "-verbose", *srcList])
        else:
            raise FileNotFoundError("No lrelease executable found")
    except Exception as exc:
        print("Qt Linguist tools seem to be missing")
        print("On Debian/Ubuntu, install: qttools5-dev-tools")
        print(str(exc))
        sys.exit(1)

    print("")
    print("Moving QM Files to Assets")
    print("")

    dstRel = dstDir.relative_to(ROOT_DIR)
    for item in srcDir.iterdir():
        if item.is_file() and item.suffix == ".qm":
            item.rename(dstDir / item.name)
            print(f"Moved: {item.relative_to(ROOT_DIR)} -> {dstRel / item.name}")

    print("")


def cleanBuiltAssets(args: argparse.Namespace | None = None) -> None:
    """Remove assets built by this script."""
    print("")
    print("Removing Built Assets")
    print("=====================")
    print("")

    assets = [ROOT_DIR / "novelwriter" / "assets" / "sample.zip"]
    assets.extend((ROOT_DIR / "novelwriter" / "assets").glob("manual*.pdf"))
    assets.extend((ROOT_DIR / "novelwriter" / "assets" / "i18n").glob("*.qm"))
    for asset in assets:
        if asset.is_file():
            asset.unlink()
            print(f"Deleted: {asset.relative_to(ROOT_DIR)}")

    print("")


def buildAllAssets(args: argparse.Namespace) -> None:
    """Build all assets."""
    cleanBuiltAssets()
    buildSampleZip()
    buildTranslationAssets()
    buildPdfDocAssets()
