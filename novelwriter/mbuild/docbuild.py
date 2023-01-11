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

import logging
import novelwriter

from PyQt5.QtGui import QFont, QFontInfo

from novelwriter.error import formatException
from novelwriter.core.tomd import ToMarkdown
from novelwriter.core.toodt import ToOdt
from novelwriter.core.tohtml import ToHtml

logger = logging.getLogger(__name__)


class NWBuildDocument:

    def __init__(self, project):

        self._conf = novelwriter.CONFIG
        self._project = project
        self._build = {}
        self._documents = []
        self._error = None

        return

    ##
    #  Properties
    ##

    @property
    def error(self):
        return self._error

    @property
    def buildLength(self):
        return len(self._documents)

    ##
    #  Setters
    ##

    def setBuildConfig(self, config):
        """Set the build config dictionary.
        """
        self._build = config
        return

    def addDocument(self, tHandle):
        """Add a document to the build queue.
        """
        self._documents.append(tHandle)
        return

    ##
    #  Methods
    ##

    def buildOpenDocument(self, savePath, isFlat):
        """Build an Open Document file.
        """
        makeOdt = ToOdt(self._project, isFlat=isFlat)
        self._setupBuild(makeOdt)
        makeOdt.initDocument()

        for i, tHandle in enumerate(self._documents):
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

    def buildHTML(self, savePath):
        """Build an HTML file.
        """
        makeHtml = ToHtml(self._project)
        self._setupBuild(makeHtml)

        if self._build.get("process.replaceTabs", False):
            makeHtml.replaceTabs()

        for i, tHandle in enumerate(self._documents):
            yield i, self._doBuild(makeHtml, tHandle)

        self._error = None
        try:
            makeHtml.saveHTML5(savePath)
        except Exception as exc:
            self._error = formatException(exc)

        return

    def buildMarkdown(self, savePath, extendedMd):
        """Build a Markdown file.
        """
        makeMd = ToMarkdown(self._project)
        self._setupBuild(makeMd)

        if extendedMd:
            makeMd.setGitHubMarkdown()
        else:
            makeMd.setStandardMarkdown()

        if self._build.get("process.replaceTabs", False):
            makeMd.replaceTabs(nSpaces=4, spaceChar=" ")

        for i, tHandle in enumerate(self._documents):
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

    def _setupBuild(self, bldObj):
        """Configure the build object.
        """
        # Get Settings
        fmtTitle      = self._build.get("format.fmtTitle", "%title%")
        fmtChapter    = self._build.get("format.fmtChapter", "%title%")
        fmtUnnumbered = self._build.get("format.fmtUnnumbered", "%title%")
        fmtScene      = self._build.get("format.fmtScene", "%title%")
        fmtSection    = self._build.get("format.fmtSection", "%title%")
        buildLang     = self._build.get("format.buildLang", "en_GB")
        hideScene     = self._build.get("format.hideScene", False)
        hideSection   = self._build.get("format.hideSection", False)
        textFont      = self._build.get("format.textFont", self._conf.textFont)
        textSize      = self._build.get("format.textSize", self._conf.textSize)
        lineHeight    = self._build.get("format.lineHeight", 1.15)
        justifyText   = self._build.get("format.justifyText", False)
        noStyling     = self._build.get("format.noStyling", False)
        replaceUCode  = self._build.get("format.replaceUCode", False)
        incSynopsis   = self._build.get("filter.includeSynopsis", False)
        incComments   = self._build.get("filter.includeComments", False)
        incKeywords   = self._build.get("filter.includeKeywords", False)
        includeBody   = self._build.get("filter.includeBody", True)

        # The language lookup dict is reloaded if needed
        self._project.setProjectLang(buildLang)

        # Get font information
        fontInfo = QFontInfo(QFont(textFont, textSize))
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
            bldObj.setStyles(not noStyling)
            bldObj.setReplaceUnicode(replaceUCode)

        if isinstance(bldObj, ToOdt):
            bldObj.setColourHeaders(not noStyling)
            bldObj.setLanguage(buildLang)

        return

    def _doBuild(self, bldObj, tHandle):
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
                bldObj.doPostProcessing()
            else:
                logger.info(f"Build: Skipping '{tHandle}'")

        except Exception:
            self._error = f"Build: Failed to build '{tHandle}'"
            logger.error(self._error)
            return False

        return True

# END Class NWBuildDocument
