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
from novelwriter.error import formatException
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

    def __init__(self, project: NWProject, build: BuildSettings):
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

    def addDocument(self, tHandle: str):
        """Add a document to the build queue manually."""
        self._queue.append(tHandle)
        return

    def queueAll(self):
        """Queue all document as defined by the build settings."""
        filtered = self._build.buildItemFilter(self._project)
        noteTitles = self._build.getBool("text.addNoteHeadings")
        for item in self._project.tree:
            if not item.itemHandle:
                continue
            if filtered.get(item.itemHandle, False):
                self._queue.append(item.itemHandle)
            elif item.isRootType() and noteTitles:
                self._queue.append(item.itemHandle)
        return

    def iterBuild(self, path: Path, bFormat: str) -> Iterable[tuple[int, bool]]:
        """Wrapper for builder based on format."""
        if bFormat in ("odt", "fodt"):
            yield from self.iterBuildOpenDocument(path, bFormat == "fodt")
        elif bFormat in ("html", "jhtml"):
            yield from self.iterBuildHTML(path if bFormat == "html" else None)
        elif bFormat in ("md", "md+"):
            yield from self.iterBuildMarkdown(path, bFormat == "md+")
        elif bFormat in ("nwd", "jnwd"):
            yield from self.iterBuildNovelWriter(path if bFormat == "nwd" else None)
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
            self._error = formatException(exc)

        return

    def iterBuildHTML(self, path: Path | None) -> Iterable[tuple[int, bool]]:
        """Build an HTML file. If path is None, no file is saved. This
        is used for generating build previews.
        """
        makeObj = ToHtml(self._project)
        filtered = self._setupBuild(makeObj)

        if self._build.getBool("format.replaceTabs"):
            makeObj.replaceTabs()

        for i, tHandle in enumerate(self._queue):
            self._error = None
            if filtered.get(tHandle, (False, 0))[0]:
                yield i, self._doBuild(makeObj, tHandle)
            else:
                yield i, False

        self._error = None
        self._cache = makeObj

        if isinstance(path, Path):
            try:
                makeObj.saveHTML5(path)
            except Exception as exc:
                self._error = formatException(exc)

        return

    def iterBuildMarkdown(self, path: Path, extendedMd: bool) -> Iterable[tuple[int, bool]]:
        """Build a Markdown file."""
        makeObj = ToMarkdown(self._project)
        filtered = self._setupBuild(makeObj)

        if extendedMd:
            makeObj.setGitHubMarkdown()
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
            self._error = formatException(exc)

        return

    def iterBuildNovelWriter(self, path: Path | None) -> Iterable[tuple[int, bool]]:
        """Build a novelWriter Markdown file."""
        makeObj = ToMarkdown(self._project)
        filtered = self._setupBuild(makeObj)

        makeObj.setKeepMarkdown(True)
        if self._build.getBool("format.replaceTabs"):
            makeObj.replaceTabs(nSpaces=4, spaceChar=" ")

        for i, tHandle in enumerate(self._queue):
            self._error = None
            if filtered.get(tHandle, (False, 0))[0]:
                yield i, self._doBuild(makeObj, tHandle, convert=False)
            else:
                yield i, False

        self._error = None
        self._cache = makeObj

        if isinstance(path, Path):
            try:
                makeObj.saveRawMarkdown(path)
            except Exception as exc:
                self._error = formatException(exc)

        return

    ##
    #  Internal Functions
    ##

    def _setupBuild(self, bldObj: Tokenizer) -> dict:
        """Configure the build object."""
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
        incBodyText   = self._build.getBool("text.includeBodyText")
        noteHeadings  = self._build.getBool("text.addNoteHeadings")

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

        bldFont = QFont(textFont, textSize)
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
        bldObj.setBodyText(incBodyText)

        if isinstance(bldObj, ToHtml):
            bldObj.setStyles(htmlAddStyles)
            bldObj.setReplaceUnicode(replaceUCode)

        if isinstance(bldObj, ToOdt):
            bldObj.setColourHeaders(odtAddColours)
            bldObj.setLanguage(buildLang)

        filtered = self._build.buildItemFilter(self._project, withRoots=noteHeadings)

        return filtered

    def _doBuild(self, bldObj: Tokenizer, tHandle: str, convert: bool = True) -> bool:
        """Build a single document and add it to the build object."""
        tItem = self._project.tree[tHandle]
        if tItem is None:
            self._error = f"Build: Unknown item '{tHandle}'"
            logger.error(self._error)
            return False

        try:
            if tItem.isRootType() and not tItem.isNovelLike():
                bldObj.addRootHeading(tItem.itemHandle)
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
