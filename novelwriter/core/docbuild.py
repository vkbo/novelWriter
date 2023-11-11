"""
novelWriter – Manuscript Document Builder
=========================================

File History:
Created: 2022-12-01 [2.1b1] NWBuildDocument

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

from typing import Iterable
from pathlib import Path

from PyQt5.QtGui import QFont, QFontInfo

from novelwriter import CONFIG
from novelwriter.enum import nwBuildFmt
from novelwriter.error import formatException, logException
from novelwriter.constants import nwLabels
from novelwriter.core.item import NWItem
from novelwriter.core.tomd import ToMarkdown
from novelwriter.core.toodt import ToOdt
from novelwriter.core.tohtml import ToHtml
from novelwriter.core.project import NWProject
from novelwriter.core.tokenizer import Tokenizer
from novelwriter.core.buildsettings import BuildSettings

logger = logging.getLogger(__name__)


class NWBuildDocument:
    """Core: Manuscript Document Build Class

    This is the core tool that assembles a project and outputs a
    manuscript, based on a build definition object (BuildSettings).
    """

    __slots__ = ("_project", "_build", "_queue", "_error", "_cache")

    def __init__(self, project: NWProject, build: BuildSettings) -> None:
        self._project = project
        self._build = build
        self._queue = []
        self._error = None
        self._cache = None
        return

    ##
    #  Properties
    ##

    @property
    def error(self) -> str | None:
        """Return the last error, if any."""
        return self._error

    @property
    def lastBuild(self) -> Tokenizer | None:
        """Return the build object of the last build process, if any.
        This is useful for accessing build details and data after the
        build job is completed.
        """
        return self._cache

    ##
    #  Special Methods
    ##

    def __len__(self) -> int:
        """Return the length of the build queue."""
        return len(self._queue)

    ##
    #  Methods
    ##

    def addDocument(self, tHandle: str) -> None:
        """Add a document to the build queue manually."""
        self._queue.append(tHandle)
        return

    def queueAll(self) -> None:
        """Queue all document as defined by the build settings."""
        self._queue = []
        filtered = self._build.buildItemFilter(self._project)
        for item in self._project.tree:
            if filtered.get(item.itemHandle, False):
                self._queue.append(item.itemHandle)
        return

    def iterBuild(self, path: Path, bFormat: nwBuildFmt) -> Iterable[tuple[int, bool]]:
        """Wrapper for builders based on format."""
        if bFormat in (nwBuildFmt.ODT, nwBuildFmt.FODT):
            yield from self.iterBuildOpenDocument(path, bFormat == nwBuildFmt.FODT)
        elif bFormat in (nwBuildFmt.HTML, nwBuildFmt.J_HTML):
            yield from self.iterBuildHTML(path, asJson=bFormat == nwBuildFmt.J_HTML)
        elif bFormat in (nwBuildFmt.STD_MD, nwBuildFmt.EXT_MD):
            yield from self.iterBuildMarkdown(path, bFormat == nwBuildFmt.EXT_MD)
        elif bFormat in (nwBuildFmt.NWD, nwBuildFmt.J_NWD):
            yield from self.iterBuildNWD(path, asJson=bFormat == nwBuildFmt.J_NWD)
        return

    def iterBuildOpenDocument(self, path: Path, isFlat: bool) -> Iterable[tuple[int, bool]]:
        """Build an Open Document file."""
        makeObj = ToOdt(self._project, isFlat=isFlat)
        filtered = self._setupBuild(makeObj)
        makeObj.initDocument()

        for i, tHandle in enumerate(self._queue):
            self._error = None
            if filtered.get(tHandle, (False, 0))[0]:
                yield i, self._doBuild(makeObj, tHandle)
            else:
                yield i, False

        makeObj.closeDocument()

        self._error = None
        self._cache = makeObj

        try:
            if isFlat:
                makeObj.saveFlatXML(path)
            else:
                makeObj.saveOpenDocText(path)
        except Exception as exc:
            logException()
            self._error = formatException(exc)

        return

    def iterBuildHTML(self, path: Path | None, asJson: bool = False) -> Iterable[tuple[int, bool]]:
        """Build an HTML file. If path is None, no file is saved. This
        is used for generating build previews.
        """
        makeObj = ToHtml(self._project)
        filtered = self._setupBuild(makeObj)

        for i, tHandle in enumerate(self._queue):
            self._error = None
            if filtered.get(tHandle, (False, 0))[0]:
                yield i, self._doBuild(makeObj, tHandle)
            else:
                yield i, False

        if self._build.getBool("format.replaceTabs"):
            makeObj.replaceTabs()

        self._error = None
        self._cache = makeObj

        if isinstance(path, Path):
            try:
                if asJson:
                    makeObj.saveHtmlJson(path)
                else:
                    makeObj.saveHtml5(path)
            except Exception as exc:
                logException()
                self._error = formatException(exc)

        return

    def iterBuildMarkdown(self, path: Path, extendedMd: bool) -> Iterable[tuple[int, bool]]:
        """Build a Markdown file."""
        makeObj = ToMarkdown(self._project)
        filtered = self._setupBuild(makeObj)

        if extendedMd:
            makeObj.setExtendedMarkdown()
        else:
            makeObj.setStandardMarkdown()

        if self._build.getBool("format.replaceTabs"):
            makeObj.replaceTabs(nSpaces=4, spaceChar=" ")

        for i, tHandle in enumerate(self._queue):
            self._error = None
            if filtered.get(tHandle, (False, 0))[0]:
                yield i, self._doBuild(makeObj, tHandle)
            else:
                yield i, False

        self._error = None
        self._cache = makeObj

        try:
            makeObj.saveMarkdown(path)
        except Exception as exc:
            logException()
            self._error = formatException(exc)

        return

    def iterBuildNWD(self, path: Path | None, asJson: bool = False) -> Iterable[tuple[int, bool]]:
        """Build a novelWriter Markdown file."""
        makeObj = ToMarkdown(self._project)
        filtered = self._setupBuild(makeObj)

        makeObj.setKeepMarkdown(True)

        for i, tHandle in enumerate(self._queue):
            self._error = None
            if filtered.get(tHandle, (False, 0))[0]:
                yield i, self._doBuild(makeObj, tHandle, convert=False)
            else:
                yield i, False

        if self._build.getBool("format.replaceTabs"):
            makeObj.replaceTabs(nSpaces=4, spaceChar=" ")

        self._error = None
        self._cache = makeObj

        if isinstance(path, Path):
            try:
                if asJson:
                    makeObj.saveRawMarkdownJSON(path)
                else:
                    makeObj.saveRawMarkdown(path)
            except Exception as exc:
                logException()
                self._error = formatException(exc)

        return

    ##
    #  Internal Functions
    ##

    def _setupBuild(self, bldObj: Tokenizer) -> dict:
        """Configure the build object."""
        # Get Settings
        textFont  = self._build.getStr("format.textFont")
        textSize  = self._build.getInt("format.textSize")

        fontFamily = textFont or CONFIG.textFont
        bldFont = QFont(fontFamily, textSize)
        fontInfo = QFontInfo(bldFont)
        textFixed = fontInfo.fixedPitch()

        bldObj.setTitleFormat(self._build.getStr("headings.fmtTitle"))
        bldObj.setChapterFormat(self._build.getStr("headings.fmtChapter"))
        bldObj.setUnNumberedFormat(self._build.getStr("headings.fmtUnnumbered"))
        bldObj.setSceneFormat(
            self._build.getStr("headings.fmtScene"),
            self._build.getBool("headings.hideScene")
        )
        bldObj.setSectionFormat(
            self._build.getStr("headings.fmtSection"),
            self._build.getBool("headings.hideSection")
        )

        bldObj.setFont(fontFamily, textSize, textFixed)
        bldObj.setJustify(self._build.getBool("format.justifyText"))
        bldObj.setLineHeight(self._build.getFloat("format.lineHeight"))

        bldObj.setSynopsis(self._build.getBool("text.includeSynopsis"))
        bldObj.setComments(self._build.getBool("text.includeComments"))
        bldObj.setKeywords(self._build.getBool("text.includeKeywords"))
        bldObj.setBodyText(self._build.getBool("text.includeBodyText"))

        if isinstance(bldObj, ToHtml):
            bldObj.setStyles(self._build.getBool("html.addStyles"))
            bldObj.setReplaceUnicode(self._build.getBool("format.stripUnicode"))

        if isinstance(bldObj, ToOdt):
            bldObj.setColourHeaders(self._build.getBool("odt.addColours"))
            bldObj.setLanguage(self._project.data.language)

            scale = nwLabels.UNIT_SCALE.get(self._build.getStr("format.pageUnit"), 1.0)
            pW, pH = nwLabels.PAPER_SIZE.get(self._build.getStr("format.pageSize"), (-1.0, -1.0))
            bldObj.setPageLayout(
                pW if pW > 0.0 else scale*self._build.getFloat("format.pageWidth"),
                pH if pH > 0.0 else scale*self._build.getFloat("format.pageHeight"),
                scale*self._build.getFloat("format.topMargin"),
                scale*self._build.getFloat("format.bottomMargin"),
                scale*self._build.getFloat("format.leftMargin"),
                scale*self._build.getFloat("format.rightMargin"),
            )

        filtered = self._build.buildItemFilter(
            self._project, withRoots=self._build.getBool("text.addNoteHeadings")
        )

        return filtered

    def _doBuild(self, bldObj: Tokenizer, tHandle: str, convert: bool = True) -> bool:
        """Build a single document and add it to the build object."""
        tItem = self._project.tree[tHandle]
        if isinstance(tItem, NWItem):
            try:
                if tItem.isRootType() and not tItem.isNovelLike():
                    bldObj.addRootHeading(tHandle)
                    if convert:
                        bldObj.doConvert()
                elif tItem.isFileType():
                    bldObj.setText(tHandle)
                    bldObj.doPreProcessing()
                    bldObj.tokenizeText()
                    bldObj.doHeaders()
                    if convert:
                        bldObj.doConvert()
                else:
                    logger.info(f"Build: Skipping '{tHandle}'")

            except Exception:
                self._error = f"Build: Failed to build '{tHandle}'"
                logger.error(self._error)
                return False

        return True

# END Class NWBuildDocument
