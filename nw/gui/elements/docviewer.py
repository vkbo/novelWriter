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

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTextBrowser
from PyQt5.QtGui import QTextOption, QFont, QPalette, QColor, QTextCursor

from nw.convert import ToHtml
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
        self.docTitle.setGeometry(0,0,self.docTitle.width(),self.docTitle.height())

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

        # Make sure the main GUI knows we changed the content
        self.theParent.viewMeta.refreshReferences(tHandle)

        return True

    def reloadText(self):
        self.loadText(self.theHandle)
        return

    def loadFromTag(self, theTag):

        logger.debug("Loading document from tag '%s'" % theTag)

        if theTag in self.theParent.theIndex.tagIndex.keys():
            theTarget = self.theParent.theIndex.tagIndex[theTag]
        else:
            logger.debug("The tag was not found in the index")
            return False

        if len(theTarget) != 3:
            # Just to make sure the index is not messed up
            return False

        self.loadText(theTarget[1])

        return True

    def docAction(self, theAction):
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

    ##
    #  Events
    ##

    def resizeEvent(self, theEvent):
        """Make sure the document title is the same width as the window.
        """
        QTextBrowser.resizeEvent(self, theEvent)

        tB = self.lineWidth()
        tW = self.width() - 2*tB
        tH = self.docTitle.height()
        self.docTitle.setGeometry(tB, tB, tW, tH)

        docFormat = self.qDocument.rootFrame().frameFormat()
        if docFormat.topMargin() < tH:
            docFormat.setTopMargin(tH + 2)

        return

    ##
    #  Internal Functions
    ##

    def _makeSelection(self, selMode):
        theCursor = self.textCursor()
        theCursor.clearSelection()
        theCursor.select(selMode)
        self.setTextCursor(theCursor)
        return

    def _linkClicked(self, theURL):

        theLink = theURL.url()
        tHandle = None
        onLine  = 0
        theTag  = ""
        if len(theLink) > 0:
            theBits = theLink.split("=")
            if len(theBits) == 2:
                theTag = theBits[1]
                tHandle, onLine = self.theParent.theIndex.getTagSource(theBits[1])

        if tHandle is None:
            self.theParent.makeAlert((
                "Could not find the reference for tag '%s'. It either doesn't exist, or the index "
                "is out of date. The index can be updated from the Tools menu.") % theTag,
                nwAlert.ERROR
            )
            return
        else:
            self.loadText(tHandle)

        return

    def _makeStyleSheet(self):

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
