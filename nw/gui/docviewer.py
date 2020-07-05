# -*- coding: utf-8 -*-
"""novelWriter GUI Document Viewer

 novelWriter – GUI Document Viewer
===================================
 Class holding the document html viewer

 File History:
 Created: 2019-05-10 [0.0.1] GuiDocViewer
 Created: 2019-10-31 [0.3.2] GuiDocViewDetails
 Created: 2020-04-25 [0.4.5] GuiDocViewHeader
 Created: 2020-06-09 [0.8.0] GuiDocViewFooter

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

from PyQt5.QtCore import Qt, QUrl, QSize
from PyQt5.QtGui import (
    QTextOption, QFont, QPalette, QColor, QTextCursor, QIcon
)
from PyQt5.QtWidgets import (
    QTextBrowser, QWidget, QScrollArea, QLabel, QHBoxLayout, QToolButton
)

from nw.core import ToHtml
from nw.constants import nwAlert, nwItemType, nwDocAction, nwUnicode

logger = logging.getLogger(__name__)

class GuiDocViewer(QTextBrowser):

    def __init__(self, theParent):
        QTextBrowser.__init__(self, theParent)

        logger.debug("Initialising GuiDocViewer ...")

        # Class Variables
        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theTheme   = theParent.theTheme
        self.theProject = theParent.theProject
        self.theHandle  = None

        self.qDocument = self.document()
        self.setMinimumWidth(self.mainConf.pxInt(300))
        self.setAutoFillBackground(True)
        self.setOpenExternalLinks(False)
        self.initViewer()

        # Document Header and Footer
        self.docHeader = GuiDocViewHeader(self)
        self.docFooter = GuiDocViewFooter(self)
        self.stickyRef = False

        theOpt = QTextOption()
        if self.mainConf.doJustify:
            theOpt.setAlignment(Qt.AlignJustify)
        self.qDocument.setDefaultTextOption(theOpt)

        self.anchorClicked.connect(self._linkClicked)
        self.setFocusPolicy(Qt.StrongFocus)

        logger.debug("GuiDocViewer initialisation complete")

        return

    def clearViewer(self):
        """Clear the content of the document and reset key variables.
        """
        self.clear()
        self.setSearchPaths([""])
        self.theHandle = None
        self.docHeader.setTitleFromHandle(self.theHandle)
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
        docPalette.setColor(QPalette.Window, QColor(*self.theTheme.colBack))
        docPalette.setColor(QPalette.Base, QColor(*self.theTheme.colBack))
        docPalette.setColor(QPalette.Text, QColor(*self.theTheme.colText))
        self.setPalette(docPalette)

        self.qDocument.setDocumentMargin(0)
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
        aDoc.setPreview(True, self.mainConf.viewComments, self.mainConf.viewSynopsis)
        aDoc.setLinkHeaders(True)

        # Be extra careful here to prevent crashes when first opening a
        # project as a crash here leaves no way of recovering.
        # See issue #298
        try:
            aDoc.setText(tHandle)
            aDoc.doAutoReplace()
            aDoc.tokenizeText()
            aDoc.doConvert()
            aDoc.doPostProcessing()
        except Exception as e:
            logger.error("Failed to generate preview for document with handle '%s'" % tHandle)
            logger.error(str(e))
            self.setText("An error occurred while generating the preview.")
            return False

        self.setHtml(aDoc.theResult)
        if self.theHandle == tHandle:
            self.verticalScrollBar().setValue(sPos)
        self.theHandle = tHandle
        self.theProject.setLastViewed(tHandle)
        self.docHeader.setTitleFromHandle(self.theHandle)
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
            # Let the parent handle the opening as it also ensures that
            # the doc view panel is visible in case this request comes
            # from outside this class.
            self.theParent.viewDocument(tHandle)
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
        Config.textFixedW is enabled or we're in Focus Mode. Otherwise,
        just ensure the margins are set correctly.
        """
        vBar = self.verticalScrollBar()
        if vBar.isVisible():
            sW = vBar.width()
        else:
            sW = 0

        cM = self.mainConf.getTextMargin()
        tB = self.frameWidth()
        tW = self.width() - 2*tB - sW
        tH = self.docHeader.height()
        fH = self.docFooter.height()
        fY = self.height() - fH - tB

        self.docHeader.setGeometry(tB, tB, tW, tH)
        self.docFooter.setGeometry(tB, fY, tW, fH)
        self.setViewportMargins(cM, max(cM, tH), cM, max(cM, fH))

        return

    def updateDocInfo(self, tHandle):
        """Called when an item label is changed to check if the document
        title bar needs updating,
        """
        if tHandle == self.theHandle:
            self.docHeader.setTitleFromHandle(self.theHandle)
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
    #  Slots
    ##

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
            ".synopsis {{"
            "  color: rgb({mColR},{mColG},{mColB});"
            "  font-wright: bold;"
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
            mColR = self.theTheme.colMod[0],
            mColG = self.theTheme.colMod[1],
            mColB = self.theTheme.colMod[2],
        )
        self.qDocument.setDefaultStyleSheet(styleSheet)

        return True

# END Class GuiDocViewer

# =============================================================================================== #
#  The Embedded Document Header
#  Only used by DocViewer, and is at a fixed position in the QTextBrowser's viewport
# =============================================================================================== #

class GuiDocViewHeader(QWidget):

    def __init__(self, docViewer):
        QWidget.__init__(self, docViewer)

        logger.debug("Initialising GuiDocViewHeader ...")

        self.mainConf   = nw.CONFIG
        self.docViewer  = docViewer
        self.theParent  = docViewer.theParent
        self.theProject = docViewer.theProject
        self.theTheme   = docViewer.theTheme
        self.theHandle  = None

        # Make a QPalette that matches the Syntax Theme
        self.thePalette = QPalette()
        self.thePalette.setColor(QPalette.Window, QColor(*self.theTheme.colBack))
        self.thePalette.setColor(QPalette.Text, QColor(*self.theTheme.colText))

        fPx = int(0.9*self.theTheme.fontPixelSize)
        hSp = self.mainConf.pxInt(6)
        self.buttonSize = fPx + hSp

        # Main Widget Settings
        self.setContentsMargins(2*self.buttonSize, 0, 0, 0)
        self.setAutoFillBackground(True)
        self.setPalette(self.thePalette)

        # Title Label
        self.theTitle = QLabel()
        self.theTitle.setText("")
        self.theTitle.setIndent(0)
        self.theTitle.setMargin(0)
        self.theTitle.setContentsMargins(0, 0, 0, 0)
        self.theTitle.setAutoFillBackground(True)
        self.theTitle.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.theTitle.setFixedHeight(fPx)
        self.theTitle.setPalette(self.thePalette)

        lblFont = self.theTitle.font()
        lblFont.setPointSizeF(0.9*self.theTheme.fontPointSize)
        self.theTitle.setFont(lblFont)

        buttonStyle = (
            "QToolButton {{border: none; background: transparent;}} "
            "QToolButton:hover {{border: none; background: rgba({0},{1},{2},0.2);}}"
        ).format(*self.theTheme.colText)

        # Buttons
        self.refreshButton = QToolButton(self)
        self.refreshButton.setIcon(self.theTheme.getIcon("refresh"))
        self.refreshButton.setContentsMargins(0, 0, 0, 0)
        self.refreshButton.setIconSize(QSize(fPx, fPx))
        self.refreshButton.setFixedSize(fPx, fPx)
        self.refreshButton.setStyleSheet(buttonStyle)
        self.refreshButton.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.refreshButton.setVisible(False)
        self.refreshButton.setToolTip("Reload the document")
        self.refreshButton.clicked.connect(self._refreshDocument)

        self.closeButton = QToolButton(self)
        self.closeButton.setIcon(self.theTheme.getIcon("close"))
        self.closeButton.setContentsMargins(0, 0, 0, 0)
        self.closeButton.setIconSize(QSize(fPx, fPx))
        self.closeButton.setFixedSize(fPx, fPx)
        self.closeButton.setStyleSheet(buttonStyle)
        self.closeButton.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.closeButton.setVisible(False)
        self.closeButton.setToolTip("Close the document")
        self.closeButton.clicked.connect(self._closeDocument)

        # Assemble Layout
        self.outerBox = QHBoxLayout()
        self.outerBox.setSpacing(hSp)
        self.outerBox.addWidget(self.theTitle, 1)
        self.outerBox.addWidget(self.refreshButton, 0)
        self.outerBox.addWidget(self.closeButton, 0)
        self.setLayout(self.outerBox)

        logger.debug("GuiDocViewHeader initialisation complete")

        return

    ##
    #  Setters
    ##

    def setTitleFromHandle(self, tHandle):
        """Sets the document title from the handle, or alternatively,
        set the whole document path.
        """
        self.theHandle = tHandle
        if tHandle is None:
            self.theTitle.setText("")
            self.closeButton.setVisible(False)
            self.refreshButton.setVisible(False)
            return True

        if self.mainConf.showFullPath:
            tTitle = []
            tTree = self.theProject.projTree.getItemPath(tHandle)
            for aHandle in reversed(tTree):
                nwItem = self.theProject.projTree[aHandle]
                if nwItem is not None:
                    tTitle.append(nwItem.itemName)
            sSep = "  %s  " % nwUnicode.U_RSAQUO
            self.theTitle.setText(sSep.join(tTitle))
        else:
            nwItem = self.theProject.projTree[tHandle]
            if nwItem is None:
                return False
            self.theTitle.setText(nwItem.itemName)

        self.closeButton.setVisible(True)
        self.refreshButton.setVisible(True)

        return True

    ##
    #  Slots
    ##

    def _closeDocument(self):
        """Trigger the close editor/viewer on the main window.
        """
        self.theParent.closeDocViewer()
        return

    def _refreshDocument(self):
        """Reload the content of the document.
        """
        if self.docViewer.theHandle == self.theParent.docEditor.theHandle:
            self.theParent.saveDocument()
        self.docViewer.reloadText()
        return

    ##
    #  Events
    ##

    def mousePressEvent(self, theEvent):
        """Capture a click on the title and ensure that the item is
        selected in the project tree.
        """
        self.theParent.treeView.setSelectedHandle(self.theHandle, doScroll=True)
        return

# END Class GuiDocViewHeader

# =============================================================================================== #
#  The Embedded Document Footer
#  Only used by DocViewer, and is at a fixed position in the QTextBrowser's viewport
# =============================================================================================== #

class GuiDocViewFooter(QWidget):

    def __init__(self, docViewer):
        QWidget.__init__(self, docViewer)

        logger.debug("Initialising GuiDocViewFooter ...")

        self.mainConf  = nw.CONFIG
        self.docViewer = docViewer
        self.theParent = docViewer.theParent
        self.theTheme  = docViewer.theTheme
        self.viewMeta  = docViewer.theParent.viewMeta
        self.theHandle = None

        # Make a QPalette that matches the Syntax Theme
        self.thePalette = QPalette()
        self.thePalette.setColor(QPalette.Window, QColor(*self.theTheme.colBack))
        self.thePalette.setColor(QPalette.Text, QColor(*self.theTheme.colText))

        fPx = int(0.9*self.theTheme.fontPixelSize)
        bSp = self.mainConf.pxInt(2)
        hSp = self.mainConf.pxInt(8)

        # Main Widget Settings
        self.setContentsMargins(0, 0, 0, 0)
        self.setAutoFillBackground(True)
        self.setPalette(self.thePalette)

        buttonStyle = (
            "QToolButton {{border: none; background: transparent;}} "
            "QToolButton:hover {{border: none; background: rgba({0},{1},{2},0.2);}}"
        ).format(*self.theTheme.colText)

        # Show/Hide Details
        self.showHide = QToolButton(self)
        self.showHide.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.showHide.setStyleSheet(buttonStyle)
        self.showHide.setIcon(self.theTheme.getIcon("reference"))
        self.showHide.setIconSize(QSize(fPx, fPx))
        self.showHide.setFixedSize(QSize(fPx, fPx))
        self.showHide.clicked.connect(self._doShowHide)
        self.showHide.setToolTip("Show/hide the references panel")

        # Sticky Button
        stickyOn  = self.theTheme.getPixmap("sticky-on", (fPx, fPx))
        stickyOff = self.theTheme.getPixmap("sticky-off", (fPx, fPx))
        stickyIcon = QIcon()
        stickyIcon.addPixmap(stickyOn, QIcon.Normal, QIcon.On)
        stickyIcon.addPixmap(stickyOff, QIcon.Normal, QIcon.Off)
        self.stickyRefs = QToolButton(self)
        self.stickyRefs.setCheckable(True)
        self.stickyRefs.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.stickyRefs.setStyleSheet(buttonStyle)
        self.stickyRefs.setIcon(stickyIcon)
        self.stickyRefs.setIconSize(QSize(fPx, fPx))
        self.stickyRefs.setFixedSize(QSize(fPx, fPx))
        self.stickyRefs.toggled.connect(self._doToggleSticky)
        self.stickyRefs.setToolTip(
            "Activate to freeze the content of the references panel when changing document"
        )

        # Labels
        self.lblRefs = QLabel("References")
        self.lblRefs.setBuddy(self.showHide)
        self.lblRefs.setIndent(0)
        self.lblRefs.setMargin(0)
        self.lblRefs.setContentsMargins(0, 0, 0, 0)
        self.lblRefs.setAutoFillBackground(True)
        self.lblRefs.setFixedHeight(fPx)
        self.lblRefs.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.lblRefs.setPalette(self.thePalette)

        self.lblSticky = QLabel("Sticky")
        self.lblSticky.setBuddy(self.stickyRefs)
        self.lblSticky.setIndent(0)
        self.lblSticky.setMargin(0)
        self.lblSticky.setContentsMargins(0, 0, 0, 0)
        self.lblSticky.setAutoFillBackground(True)
        self.lblSticky.setFixedHeight(fPx)
        self.lblSticky.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.lblSticky.setPalette(self.thePalette)

        lblFont = self.font()
        lblFont.setPointSizeF(0.9*self.theTheme.fontPointSize)
        self.lblRefs.setFont(lblFont)
        self.lblSticky.setFont(lblFont)

        # Assemble Layout
        self.outerBox = QHBoxLayout()
        self.outerBox.setSpacing(bSp)
        self.outerBox.addWidget(self.showHide, 0)
        self.outerBox.addWidget(self.lblRefs, 0)
        self.outerBox.addSpacing(hSp)
        self.outerBox.addWidget(self.stickyRefs, 0)
        self.outerBox.addWidget(self.lblSticky, 0)
        self.outerBox.addStretch(1)
        self.setLayout(self.outerBox)

        logger.debug("GuiDocViewFooter initialisation complete")

        return

    ##
    #  Slots
    ##

    def _doShowHide(self):
        """Toggle the expand/collapse of the panel.
        """
        isVisible = self.viewMeta.isVisible()
        self.viewMeta.setVisible(not isVisible)
        return

    def _doToggleSticky(self, theState):
        """Toggle the sticky flag for the reference panel.
        """
        logger.verbose("Reference sticky is %s" % str(theState))
        self.docViewer.stickyRef = theState
        if not theState and self.docViewer.theHandle is not None:
            self.viewMeta.refreshReferences(self.docViewer.theHandle)
        return

# END Class GuiDocViewFooter

# =============================================================================================== #
#  The Document Back-Reference Panel
#  Placed in a separate QSplitter position in the main GUI window
# =============================================================================================== #

class GuiDocViewDetails(QScrollArea):

    def __init__(self, theParent):
        QScrollArea.__init__(self, theParent)

        logger.debug("Initialising GuiDocViewDetails ...")
        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theProject = theParent.theProject
        self.theTheme   = theParent.theTheme
        self.currHandle = None

        self.refList = QLabel("")
        self.refList.setWordWrap(True)
        self.refList.setAlignment(Qt.AlignTop)
        self.refList.setScaledContents(True)
        self.refList.linkActivated.connect(self._linkClicked)

        hCol = self.palette().highlight().color()
        self.linkStyle = "style='color: rgb({0},{1},{2})'".format(
            *self.theTheme.colLink
        )

        # Assemble
        self.outerWidget = QWidget()
        self.outerBox = QHBoxLayout()
        self.outerBox.addWidget(self.refList, 1)

        self.outerWidget.setLayout(self.outerBox)
        self.setWidget(self.outerWidget)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setWidgetResizable(True)
        self.setMinimumHeight(self.mainConf.pxInt(50))

        logger.debug("GuiDocViewDetails initialisation complete")

        return

    def refreshReferences(self, tHandle):
        """Update the current list of document references from the
        project index.
        """
        self.currHandle = tHandle
        if self.theParent.docViewer.stickyRef:
            return

        theRefs = self.theParent.theIndex.getBackReferenceList(tHandle)
        theList = []
        for tHandle in theRefs:
            tItem = self.theProject.projTree[tHandle]
            if tItem is not None:
                theList.append("<a href='#head_%s:%s' %s>%s</a>" % (
                    tHandle, theRefs[tHandle], self.linkStyle, tItem.itemName
                ))

        self.refList.setText(", ".join(theList))

        return

    ##
    #  Internal Functions
    ##

    def _linkClicked(self, theLink):
        """Capture the link-click and forward it to the document viewer
        class for handling.
        """
        logger.verbose("Clicked link: '%s'" % theLink)
        if len(theLink) == 27:
            tHandle = theLink[6:19]
            self.theParent.viewDocument(tHandle, theLink)
        return

# END Class GuiDocViewDetails
