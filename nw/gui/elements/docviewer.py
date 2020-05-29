# -*- coding: utf-8 -*-
"""novelWriter GUI Document Viewer

 novelWriter – GUI Document Viewer
===================================
 Class holding the document html viewer

 File History:
 Created: 2019-05-10 [0.0.1]

 This file is a part of novelWriter
 Copyright 2020, Veronica Berglyd Olsen

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
import nw

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWidgets import QTextBrowser
from PyQt5.QtGui import QTextOption, QFont, QPalette, QColor, QTextCursor

from nw.core import ToHtml
from nw.constants import nwAlert, nwItemType, nwDocAction
from nw.gui.elements.doctitlebar import GuiDocTitleBar

logger = logging.getLogger(__name__)

class GuiDocViewer(QTextBrowser):

    def __init__(self, theParent, theProject):
        QTextBrowser.__init__(self)

        logger.debug("Initialising DocViewer ...")

        # Class Variables
        self.mainConf   = nw.CONFIG
        self.theProject = theProject
        self.theParent  = theParent
        self.theTheme   = theParent.theTheme
        self.theHandle  = None

        self.qDocument = self.document()
        self.setMinimumWidth(300)
        self.setOpenExternalLinks(False)
        self.initViewer()

        # Document Title
        self.docTitle = GuiDocTitleBar(self, self.theProject)
        self.docTitle.setGeometry(0, 0, self.docTitle.width(), self.docTitle.height())
        self.setViewportMargins(0, self.docTitle.height(), 0, 0)

        theOpt = QTextOption()
        if self.mainConf.doJustify:
            theOpt.setAlignment(Qt.AlignJustify)
        self.qDocument.setDefaultTextOption(theOpt)

        self.anchorClicked.connect(self._linkClicked)
        self.setFocusPolicy(Qt.StrongFocus)

        logger.debug("DocViewer initialisation complete")

        # Connect Functions
        self.setSelectedHandle = self.theParent.treeView.setSelectedHandle

        return

    def clearViewer(self):
        """Clear the content of the document and reset key variables.
        """
        self.clear()
        self.setSearchPaths([""])
        self.theHandle = None
        self.docTitle.setTitleFromHandle(self.theHandle)
        return True

    def initViewer(self):
        """Set editor settings from main config.
        """
        self._makeStyleSheet()

        # Set Font
        theFont = QFont()
        if self.mainConf.textFont is None:
            # If none is defined, set the default back to config
            self.mainConf.textFont = self.qDocument.defaultFont().family()
        theFont.setFamily(self.mainConf.textFont)
        theFont.setPointSize(self.mainConf.textSize)
        self.setFont(theFont)

        docPalette = self.palette()
        docPalette.setColor(QPalette.Base, QColor(*self.theTheme.colBack))
        docPalette.setColor(QPalette.Text, QColor(*self.theTheme.colText))
        self.setPalette(docPalette)

        self.qDocument.setDocumentMargin(self.mainConf.textMargin)
        theOpt = QTextOption()
        if self.mainConf.doJustify:
            theOpt.setAlignment(Qt.AlignJustify)
        self.qDocument.setDefaultTextOption(theOpt)

        # If we have a document open, we should reload it in case the font changed
        if self.theHandle is not None:
            tHandle = self.theHandle
            self.clearViewer()
            self.loadText(tHandle)

        return True

    def loadText(self, tHandle):
        """Load text into the viewer from an item handle.
        """
        tItem = self.theProject.projTree[tHandle]
        if tItem is None:
            logger.warning("Item not found")
            return False

        if tItem.itemType != nwItemType.FILE:
            return False

        logger.debug("Generating preview for item %s" % tHandle)
        sPos = self.verticalScrollBar().value()
        aDoc = ToHtml(self.theProject, self.theParent)
        aDoc.setPreview(True, self.mainConf.viewComments)
        aDoc.setLinkHeaders(True)
        aDoc.setText(tHandle)
        aDoc.doAutoReplace()
        aDoc.tokenizeText()
        aDoc.doConvert()
        aDoc.doPostProcessing()
        self.setHtml(aDoc.theResult)
        if self.theHandle == tHandle:
            self.verticalScrollBar().setValue(sPos)
        self.theHandle = tHandle
        self.theProject.setLastViewed(tHandle)
        self.docTitle.setTitleFromHandle(self.theHandle)
        self.updateDocMargins()

        # Make sure the main GUI knows we changed the content
        self.theParent.viewMeta.refreshReferences(tHandle)

        return True

    def reloadText(self):
        """Reload the text in the current document.
        """
        self.loadText(self.theHandle)
        return

    def loadFromTag(self, theTag):
        """Load text in the document from a reference given by a meta
        tag rather than a known handle. This function depends on the
        index being up to date.
        """
        logger.debug("Loading document from tag '%s'" % theTag)
        tHandle, onLine, sTitle = self.theParent.theIndex.getTagSource(theTag)
        if tHandle is None:
            self.theParent.makeAlert((
                "Could not find the reference for tag '%s'. It either doesn't "
                "exist, or the index is out of date. The index can be updated "
                "from the Tools menu, or by pressing F9."
            ) % theTag, nwAlert.ERROR)
            return
        else:
            self.loadText(tHandle)
            self.navigateTo("#head_%s:%s" % (tHandle, sTitle))
        return True

    def docAction(self, theAction):
        """Wrapper function for various document actions on the current
        document.
        """
        logger.verbose("Requesting action: %s" % theAction.name)
        if self.theHandle is None:
            logger.error("No document open")
            return False
        if theAction == nwDocAction.CUT:
            self.copy()
        elif theAction == nwDocAction.COPY:
            self.copy()
        elif theAction == nwDocAction.SEL_ALL:
            self._makeSelection(QTextCursor.Document)
        elif theAction == nwDocAction.SEL_PARA:
            self._makeSelection(QTextCursor.BlockUnderCursor)
        else:
            logger.debug("Unknown or unsupported document action %s" % str(theAction))
            return False
        return True

    def navigateTo(self, navLink):
        """Go to a specific #link in the document.
        """
        if not isinstance(navLink, str):
            return False
        if navLink.startswith("#"):
            self.setSource(QUrl(navLink))
        return True

    def updateDocMargins(self):
        """Automatically adjust the margins so the text is centred if
        Config.textFixedW is enabled or we're in Zen mode. Otherwise,
        just ensure the margins are set correctly.
        """
        tB = self.lineWidth()
        tW = self.width() - 2*tB
        tH = self.docTitle.height()
        tT = self.mainConf.textMargin - tH
        self.docTitle.setGeometry(tB, tB, tW, tH)
        self.setViewportMargins(0, tH, 0, 0)

        docFormat = self.qDocument.rootFrame().frameFormat()
        if tT > 0:
            docFormat.setTopMargin(tT)
        else:
            docFormat.setTopMargin(0)

        self.qDocument.blockSignals(True)
        self.qDocument.rootFrame().setFrameFormat(docFormat)
        self.qDocument.blockSignals(False)

        return

    def updateDocTitle(self, tHandle):
        """Called when an item label is changed to check if the document
        title bar needs updating,
        """
        if tHandle == self.theHandle:
            self.docTitle.setTitleFromHandle(self.theHandle)
            self.updateDocMargins()
        return

    ##
    #  Setters
    ##

    def setCursorPosition(self, thePosition):
        """Move the cursor to a given position in the document.
        """
        if not isinstance(thePosition, int):
            return False
        if thePosition >= 0:
            theCursor = self.textCursor()
            theCursor.setPosition(thePosition)
            self.setTextCursor(theCursor)
        return True

    def setCursorLine(self, theLine):
        """Move the cursor to a given line in the document.
        """
        if not isinstance(theLine, int):
            return False
        if theLine >= 0:
            theBlock = self.qDocument.findBlockByLineNumber(theLine)
            if theBlock:
                self.setCursorPosition(theBlock.position())
                logger.verbose("Cursor moved to line %d" % theLine)
        return True

    ##
    #  Events
    ##

    def resizeEvent(self, theEvent):
        """Make sure the document title is the same width as the window.
        """
        QTextBrowser.resizeEvent(self, theEvent)
        self.updateDocMargins()
        return

    ##
    #  Internal Functions
    ##

    def _makeSelection(self, selMode):
        """Wrapper function for making a selection based on a specific
        selection mode.
        """
        theCursor = self.textCursor()
        theCursor.clearSelection()
        theCursor.select(selMode)
        self.setTextCursor(theCursor)
        return

    def _linkClicked(self, theURL):
        """Slot for a link in the document being clicked.
        """
        theLink = theURL.url()
        logger.verbose("Clicked link: '%s'" % theLink)
        if len(theLink) > 0:
            theBits = theLink.split("=")
            if len(theBits) == 2:
                self.loadFromTag(theBits[1])
        return

    def _makeStyleSheet(self):
        """Generate an appropriate style sheet for the document viewer,
        based on the current syntax highlighter theme,
        """
        styleSheet = (
            "body {{"
            "  color: rgb({tColR},{tColG},{tColB});"
            "  font-size: {textSize:.1f}pt;"
            "}}\n"
            "h1, h2, h3, h4 {{"
            "  color: rgb({hColR},{hColG},{hColB});"
            "}}\n"
            "a {{"
            "  color: rgb({aColR},{aColG},{aColB});"
            "}}\n"
            "mark {{"
            "  color: rgb({eColR},{eColG},{eColB});"
            "}}\n"
            "table {{"
            "  margin: 10px 0px;"
            "}}\n"
            "td {{"
            "  padding: 0px 4px;"
            "}}\n"
            ".tags {{"
            "  color: rgb({kColR},{kColG},{kColB});"
            "  font-wright: bold;"
            "}}\n"
            ".comment {{"
            "  color: rgb({cColR},{cColG},{cColB});"
            "  margin-left: 1em;"
            "  margin-right: 1em;"
            "}}\n"
        ).format(
            textSize = self.mainConf.textSize,
            preSize  = self.mainConf.textSize*0.9,
            tColR = self.theTheme.colText[0],
            tColG = self.theTheme.colText[1],
            tColB = self.theTheme.colText[2],
            hColR = self.theTheme.colHead[0],
            hColG = self.theTheme.colHead[1],
            hColB = self.theTheme.colHead[2],
            cColR = self.theTheme.colComm[0],
            cColG = self.theTheme.colComm[1],
            cColB = self.theTheme.colComm[2],
            eColR = self.theTheme.colEmph[0],
            eColG = self.theTheme.colEmph[1],
            eColB = self.theTheme.colEmph[2],
            aColR = self.theTheme.colVal[0],
            aColG = self.theTheme.colVal[1],
            aColB = self.theTheme.colVal[2],
            kColR = self.theTheme.colKey[0],
            kColG = self.theTheme.colKey[1],
            kColB = self.theTheme.colKey[2],
        )
        self.qDocument.setDefaultStyleSheet(styleSheet)

        return True

# END Class GuiDocViewer
