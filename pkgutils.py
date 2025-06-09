#!/usr/bin/env python3
"""
novelWriter – Packaging Utils
=============================

File History:
Created: 2019-05-16 [0.5.1]
Renamed: 2023-07-26 [2.1b1]
Split:   2025-01-16 [2.7b1]

This file is a part of novelWriter
Copyright (C) 2019 Veronica Berglyd Olsen and novelWriter contributors

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
"""
from __future__ import annotations

import argparse
import datetime
import shutil
import subprocess
import sys

import utils.assets
import utils.build_appimage
import utils.build_binary
import utils.build_debian
import utils.build_windows
import utils.docs
import utils.icon_themes

from utils.common import ROOT_DIR, SETUP_DIR, extractVersion, readFile, stripVersion, writeFile

OS_LINUX = sys.platform.startswith("linux")
OS_DARWIN = sys.platform.startswith("darwin")
OS_WIN = sys.platform.startswith("win32")


def printVersion(args: argparse.Namespace) -> None:
    """Print the novelWriter version and exit."""
    print(extractVersion(beQuiet=True)[0], end=None)
    return


def installPackages(args: argparse.Namespace) -> None:
    """Install package dependencies both for this script and for running
    novelWriter itself.
    """
    print("")
    print("Installing Dependencies")
    print("=======================")
    print("")

    installQueue = ["pip", "-r requirements.txt"]
    if args.mac:
        installQueue.append("pyobjc")
    elif args.win:
        installQueue.append("pywin32")

    pyCmd = [sys.executable, "-m"]
    pipCmd = ["pip", "install", "--user", "--upgrade"]
    for stepCmd in installQueue:
        pkgCmd = stepCmd.split(" ")
        try:
            subprocess.call(pyCmd + pipCmd + pkgCmd)
        except Exception as exc:
            print("Failed with error:")
            print(str(exc))
            sys.exit(1)

    return


def cleanBuildDirs(args: argparse.Namespace) -> None:
    """Recursively delete the 'build' and 'dist' folders."""
    print("")
    print("Cleaning up build environment ...")
    print("")

    folders = [
        ROOT_DIR / "build_bin",
        ROOT_DIR / "build",
        ROOT_DIR / "dist_appimage",
        ROOT_DIR / "dist_bin",
        ROOT_DIR / "dist_deb",
        ROOT_DIR / "dist_doc",
        ROOT_DIR / "dist",
        ROOT_DIR / "novelWriter.egg-info",
    ]

    for folder in folders:
        if folder.is_dir():
            try:
                shutil.rmtree(folder)
                print(f"Deleted: {folder}")
            except OSError:
                print(f"Failed:  {folder}")
        else:
            print(f"Missing: {folder}")

    print("")

    return


def genMacOSPlist(args: argparse.Namespace) -> None:
    """Set necessary values for .plist file for MacOS build."""
    outDir = SETUP_DIR / "macos"
    numVers = stripVersion(extractVersion()[0])
    copyrightYear = datetime.datetime.now().year

    # These keys are no longer used but are present for compatibility
    pkgVersMaj, pkgVersMin = numVers.split(".")[:2]

    plistXML = readFile(outDir / "Info.plist.template").format(
        macosBundleSVers=numVers,
        macosBundleVers=numVers,
        macosBundleVersMajor=pkgVersMaj,
        macosBundleVersMinor=pkgVersMin,
        macosBundleCopyright=f"Copyright 2018–{copyrightYear}, Veronica Berglyd Olsen",
    )

    print(f"Writing Info.plist to {outDir}/Info.plist")
    writeFile(outDir / "Info.plist", plistXML)

    return


if __name__ == "__main__":
    """Parse command line options and run the commands."""
    parser = argparse.ArgumentParser(
        usage="pkgutils.py [command] [--flags]",
        description=(
            "This tool provides setup and build commands for installing or distributing "
            "novelWriter as a package on Linux, Mac and Windows, as well as developer tools "
            "for internationalisation."
        )
    )
    parsers = parser.add_subparsers()

    # Version
    cmdVersion = parsers.add_parser(
        "version", help="Print the novelWriter version."
    )
    cmdVersion.set_defaults(func=printVersion)

    # General
    # =======

    # Pip Install
    cmdPipInstall = parsers.add_parser(
        "pip", help="Install all package dependencies for novelWriter using pip."
    )
    cmdPipInstall.add_argument("--linux", action="store_true", help="For Linux.", default=OS_LINUX)
    cmdPipInstall.add_argument("--mac", action="store_true", help="For MacOS.", default=OS_DARWIN)
    cmdPipInstall.add_argument("--win", action="store_true", help="For Windows.", default=OS_WIN)
    cmdPipInstall.set_defaults(func=installPackages)

    # Additional Builds
    # =================

    # Build Icons
    cmdIcons = parsers.add_parser(
        "icons", help="Build icon theme files from source."
    )
    cmdIcons.add_argument("sources", help="Working directory for sources.")
    cmdIcons.add_argument("style", help="What icon style to build.")
    cmdIcons.set_defaults(func=utils.icon_themes.main)

    # Import Translations
    cmdImportTS = parsers.add_parser(
        "qtlimport", help="Import updated i18n files from a Crowdin zip file."
    )
    cmdImportTS.add_argument("file", help="Path to zip file from Crowdin")
    cmdImportTS.set_defaults(func=utils.assets.importI18nUpdates)

    # Update i18n Sources
    cmdUpdateTS = parsers.add_parser(
        "qtlupdate", help=(
            "Update translation files for internationalisation. "
            "The files to be updated must be provided as arguments. "
            "New files can be created by giving a 'nw_<lang>.ts' file name "
            "where <lang> is a valid language code."
        )
    )
    cmdUpdateTS.add_argument("files", nargs="+")
    cmdUpdateTS.set_defaults(func=utils.assets.updateTranslationSources)

    # Build i18n Files
    cmdBuildQM = parsers.add_parser(
        "qtlrelease", help="Build the language files for internationalisation."
    )
    cmdBuildQM.set_defaults(func=utils.assets.buildTranslationAssets)

    # Update Docs i18n Sources
    cmdUpdateDocsPo = parsers.add_parser(
        "docs-lupdate", help=(
            "Update translation files for internationalisation of the docs. "
            "The langauges to be updated can be added as arguments, "
            "or set to all to update all existing translations."
        )
    )
    cmdUpdateDocsPo.add_argument("lang", nargs="+")
    cmdUpdateDocsPo.set_defaults(func=utils.docs.updateDocsTranslationSources)

    # Build PDF Docs
    cmdBuildPdfDocs = parsers.add_parser(
        "docs-pdf", help="Build the PDF manual files."
    )
    cmdBuildPdfDocs.add_argument("lang", nargs="+")
    cmdBuildPdfDocs.set_defaults(func=utils.docs.buildPdfDocAssets)

    # Build HTML Docs
    cmdBuildHtmlDocs = parsers.add_parser(
        "docs-html", help="Build the HTML docs."
    )
    cmdBuildHtmlDocs.add_argument("lang", nargs="+")
    cmdBuildHtmlDocs.set_defaults(func=utils.docs.buildHtmlDocs)

    # Build Sample
    cmdBuildSample = parsers.add_parser(
        "sample", help="Build the sample project zip file and add it to assets."
    )
    cmdBuildSample.set_defaults(func=utils.assets.buildSampleZip)

    # Clean Assets
    cmdCleanAssets = parsers.add_parser(
        "clean-assets", help="Delete assets built by docs-pdf, sample and qtlrelease."
    )
    cmdCleanAssets.set_defaults(func=utils.assets.cleanBuiltAssets)

    # Build Assets
    cmdBuildAssets = parsers.add_parser(
        "build-assets", help="Build all assets. Includes docs-pdf, sample and qtlrelease."
    )
    cmdBuildAssets.set_defaults(func=utils.assets.buildAllAssets)

    # Python Packaging
    # ================

    # Build Debian Package
    cmdBuildDeb = parsers.add_parser(
        "build-deb", help=(
            "Build a .deb package for Debian and Ubuntu. "
            "Add --sign to sign package."
        )
    )
    cmdBuildDeb.add_argument("--sign", action="store_true", help="Sign the package.")
    cmdBuildDeb.set_defaults(func=utils.build_debian.debian)

    # Build Ubuntu Packages
    cmdBuildUbuntu = parsers.add_parser(
        "build-ubuntu", help=(
            "Build a .deb package for Debian and Ubuntu. "
            "Add --sign to sign package. "
            "Add --first to set build number to 0."
        )
    )
    cmdBuildUbuntu.add_argument("--sign", action="store_true", help="Sign the package.")
    cmdBuildUbuntu.add_argument("--build", type=int, help="Set build number.")
    cmdBuildUbuntu.set_defaults(func=utils.build_debian.launchpad)

    # Build AppImage
    # See https://github.com/pypa/manylinux
    # See https://python-appimage.readthedocs.io/en/latest/#available-python-appimages
    cmdBuildAppImage = parsers.add_parser("build-appimage", help="Build an AppImage.")
    cmdBuildAppImage.add_argument("linux", help="Manylinux version, e.g. manylinux_2_28.")
    cmdBuildAppImage.add_argument("arch", help="Architecture, e.g. x86_64.")
    cmdBuildAppImage.add_argument("python", help="Python version, e.g. 3.13.")
    cmdBuildAppImage.set_defaults(func=utils.build_appimage.appImage)

    # Build Windows Inno Setup Installer
    cmdBuildSetupExe = parsers.add_parser(
        "build-win-exe", help="Build a setup.exe file with Python embedded for Windows."
    )
    cmdBuildSetupExe.set_defaults(func=utils.build_windows.main)

    # Build Binary
    cmdBuildBinary = parsers.add_parser(
        "build-bin", help="Build a standalone binary package."
    )
    cmdBuildBinary.set_defaults(func=utils.build_binary.main)

    # Build Clean
    cmdBuildClean = parsers.add_parser(
        "build-clean", help="Recursively delete all build folders."
    )
    cmdBuildClean.set_defaults(func=cleanBuildDirs)

    # Generate MacOS PList File
    cmdBuildMacOSPlist = parsers.add_parser(
        "gen-plist", help="Generate an Info.plist for use in a MacOS Bundle."
    )
    cmdBuildMacOSPlist.set_defaults(func=genMacOSPlist)

    args = parser.parse_args()
    args.func(args)
