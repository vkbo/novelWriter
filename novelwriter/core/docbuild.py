"""
novelWriter – Build Document Tool
=================================
A class to build one or more novelWriter files to a single document

File History:
Created: 2022-12-01 [2.1b1]

This file is a part of novelWriter
Copyright 2018–2023, Veronica Berglyd Olsen

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

import logging
from pathlib import Path
from typing import Iterable

from PyQt5.QtGui import QFont, QFontDatabase, QFontInfo

from novelwriter import CONFIG
from novelwriter.core.tokenizer import Tokenizer
from novelwriter.error import formatException
from novelwriter.core.tomd import ToMarkdown
from novelwriter.core.toodt import ToOdt
from novelwriter.core.tohtml import ToHtml
from novelwriter.core.project import NWProject
from novelwriter.core.buildsettings import BuildSettings

logger = logging.getLogger(__name__)


class NWBuildDocument:

    def __init__(self, project: NWProject, build: BuildSettings):

        self._project = project
        self._build = build
        self._queue = []
        self._error = None

        return

    ##
    #  Properties
    ##

    @property
    def error(self) -> str | None:
        return self._error

    @property
    def buildLength(self) -> int:
        return len(self._queue)

    ##
    #  Methods
    ##

    def addDocument(self, tHandle: str):
        """Add a document to the build queue manually.
        """
        self._queue.append(tHandle)
        return

    def queueAll(self):
        """Queue all document as defined by the build setup.
        """
        filtered = self._build.buildItemFilter(self._project)
        noteTitles = self._build.getValue("text.addNoteHeadings")
        for item in self._project.tree:
            if filtered.get(item.itemHandle, False):
                self._queue.append(item.itemHandle)
            elif item.isRootType() and noteTitles:
                self._queue.append(item.itemHandle)
        return

    def iterBuildOpenDocument(self, savePath: Path, isFlat: bool) -> Iterable[tuple[int, bool]]:
        """Build an Open Document file.
        """
        makeOdt = ToOdt(self._project, isFlat=isFlat)
        self._setupBuild(makeOdt)
        makeOdt.initDocument()

        for i, tHandle in enumerate(self._queue):
            yield i, self._doBuild(makeOdt, tHandle)

        makeOdt.closeDocument()

        self._error = None
        try:
            if isFlat:
                makeOdt.saveFlatXML(savePath)
            else:
                makeOdt.saveOpenDocText(savePath)
        except Exception as exc:
            self._error = formatException(exc)

        return

    def iterBuildHTML(self, savePath: Path) -> Iterable[tuple[int, bool]]:
        """Build an HTML file.
        """
        makeHtml = ToHtml(self._project)
        self._setupBuild(makeHtml)

        if self._build.getValue("format.replaceTabs"):
            makeHtml.replaceTabs()

        for i, tHandle in enumerate(self._queue):
            yield i, self._doBuild(makeHtml, tHandle)

        self._error = None
        try:
            makeHtml.saveHTML5(savePath)
        except Exception as exc:
            self._error = formatException(exc)

        return

    def iterBuildMarkdown(self, savePath: Path, extendedMd: bool) -> Iterable[tuple[int, bool]]:
        """Build a Markdown file.
        """
        makeMd = ToMarkdown(self._project)
        self._setupBuild(makeMd)

        if extendedMd:
            makeMd.setGitHubMarkdown()
        else:
            makeMd.setStandardMarkdown()

        if self._build.getValue("format.replaceTabs"):
            makeMd.replaceTabs(nSpaces=4, spaceChar=" ")

        for i, tHandle in enumerate(self._queue):
            yield i, self._doBuild(makeMd, tHandle)

        self._error = None
        try:
            makeMd.saveMarkdown(savePath)
        except Exception as exc:
            self._error = formatException(exc)

        return

    ##
    #  Internal Functions
    ##

    def _setupBuild(self, bldObj: Tokenizer):
        """Configure the build object.
        """
        # Get Settings
        fmtTitle      = self._build.getStr("headings.fmtTitle")
        fmtChapter    = self._build.getStr("headings.fmtChapter")
        fmtUnnumbered = self._build.getStr("headings.fmtUnnumbered")
        fmtScene      = self._build.getStr("headings.fmtScene")
        fmtSection    = self._build.getStr("headings.fmtSection")
        hideScene     = self._build.getBool("headings.hideScene")
        hideSection   = self._build.getBool("headings.hideSection")

        incSynopsis   = self._build.getBool("text.includeSynopsis")
        incComments   = self._build.getBool("text.includeComments")
        incKeywords   = self._build.getBool("text.includeKeywords")
        includeBody   = self._build.getBool("text.includeBody")

        buildLang     = self._build.getStr("format.buildLang")
        textFont      = self._build.getStr("format.textFont")
        textSize      = self._build.getInt("format.textSize")
        lineHeight    = self._build.getFloat("format.lineHeight")
        justifyText   = self._build.getBool("format.justifyText")
        replaceUCode  = self._build.getBool("format.stripUnicode")

        odtAddColours = self._build.getBool("odt.addColours")
        htmlAddStyles = self._build.getBool("html.addStyles")

        # The language lookup dict is reloaded if needed
        self._project.setProjectLang(buildLang)

        # Get font information
        if not textFont:
            textFont = str(CONFIG.textFont)
        if not textFont:
            textFont = QFontDatabase.systemFont(QFontDatabase.GeneralFont).family()

        bldFont = QFont(family=textFont, pointSize=textSize)
        fontInfo = QFontInfo(bldFont)
        textFixed = fontInfo.fixedPitch()

        bldObj.setTitleFormat(fmtTitle)
        bldObj.setChapterFormat(fmtChapter)
        bldObj.setUnNumberedFormat(fmtUnnumbered)
        bldObj.setSceneFormat(fmtScene, hideScene)
        bldObj.setSectionFormat(fmtSection, hideSection)

        bldObj.setFont(textFont, textSize, textFixed)
        bldObj.setJustify(justifyText)
        bldObj.setLineHeight(lineHeight)

        bldObj.setSynopsis(incSynopsis)
        bldObj.setComments(incComments)
        bldObj.setKeywords(incKeywords)
        bldObj.setBodyText(includeBody)

        if isinstance(bldObj, ToHtml):
            bldObj.setStyles(htmlAddStyles)
            bldObj.setReplaceUnicode(replaceUCode)

        if isinstance(bldObj, ToOdt):
            bldObj.setColourHeaders(odtAddColours)
            bldObj.setLanguage(buildLang)

        return

    def _doBuild(self, bldObj: Tokenizer, tHandle: str) -> bool:
        """Build a single document and add it to the build object.
        """
        self._error = None
        tItem = self._project.tree[tHandle]
        if tItem is None:
            self._error = f"Build: Unknown item '{tHandle}'"
            logger.error(self._error)
            return False

        try:
            if tItem.isRootType() and not tItem.isNovelLike():
                bldObj.addRootHeading(tItem.itemHandle)
                bldObj.doConvert()
            elif tItem.isFileType():
                bldObj.setText(tHandle)
                bldObj.doPreProcessing()
                bldObj.tokenizeText()
                bldObj.doHeaders()
                bldObj.doConvert()
            else:
                logger.info(f"Build: Skipping '{tHandle}'")

        except Exception:
            self._error = f"Build: Failed to build '{tHandle}'"
            logger.error(self._error)
            return False

        return True

# END Class NWBuildDocument
