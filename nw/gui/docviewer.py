"""
novelWriter – GUI Document Viewer
=================================
GUI classes for the main document viewer

File History:
Created: 2019-05-10 [0.0.1] GuiDocViewer
Created: 2019-10-31 [0.3.2] GuiDocViewDetails
Created: 2020-04-25 [0.4.5] GuiDocViewHeader
Created: 2020-06-09 [0.8.0] GuiDocViewFooter
Created: 2020-09-08 [1.0b1] GuiDocViewHistory

This file is a part of novelWriter
Copyright 2018–2021, Veronica Berglyd Olsen

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

import nw
import logging

from PyQt5.QtCore import Qt, QUrl, QSize, pyqtSlot
from PyQt5.QtGui import (
    QTextOption, QFont, QPalette, QColor, QTextCursor, QIcon, QCursor
)
from PyQt5.QtWidgets import (
    qApp, QTextBrowser, QWidget, QScrollArea, QLabel, QHBoxLayout, QToolButton,
    QAction, QMenu
)

from nw.core import ToHtml
from nw.enum import nwAlert, nwItemType, nwDocAction
from nw.constants import nwUnicode

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

        # Internal Variables
        self._docHandle = None

        # Settings
        self.setMinimumWidth(self.mainConf.pxInt(300))
        self.setAutoFillBackground(True)
        self.setOpenExternalLinks(False)
        self.setFocusPolicy(Qt.StrongFocus)

        # Document Header and Footer
        self.docHeader  = GuiDocViewHeader(self)
        self.docFooter  = GuiDocViewFooter(self)
        self.docHistory = GuiDocViewHistory(self)
        self.stickyRef  = False

        # Signals
        self.anchorClicked.connect(self._linkClicked)

        # Context Menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._openContextMenu)

        self.initViewer()

        logger.debug("GuiDocViewer initialisation complete")

        return

    def clearViewer(self):
        """Clear the content of the document and reset key variables.
        """
        self.clear()
        self.setSearchPaths([""])
        self._docHandle = None
        self.docHeader.setTitleFromHandle(self._docHandle)
        return True

    def initViewer(self):
        """Set editor settings from main config.
        """
        self._makeStyleSheet()

        # Set Font
        theFont = QFont()
        if self.mainConf.textFont is None:
            # If none is defined, set the default back to config
            self.mainConf.textFont = self.document().defaultFont().family()
        theFont.setFamily(self.mainConf.textFont)
        theFont.setPointSize(self.mainConf.textSize)
        self.setFont(theFont)

        # Set the widget colours to match syntax theme
        mainPalette = self.palette()
        mainPalette.setColor(QPalette.Window, QColor(*self.theTheme.colBack))
        mainPalette.setColor(QPalette.Base, QColor(*self.theTheme.colBack))
        mainPalette.setColor(QPalette.Text, QColor(*self.theTheme.colText))
        self.setPalette(mainPalette)

        docPalette = self.viewport().palette()
        docPalette.setColor(QPalette.Base, QColor(*self.theTheme.colBack))
        docPalette.setColor(QPalette.Text, QColor(*self.theTheme.colText))
        self.viewport().setPalette(docPalette)

        self.docHeader.matchColours()
        self.docFooter.matchColours()

        # Set default text margins
        self.document().setDocumentMargin(0)
        theOpt = QTextOption()
        if self.mainConf.doJustify:
            theOpt.setAlignment(Qt.AlignJustify)
        self.document().setDefaultTextOption(theOpt)

        # Scroll bars
        if self.mainConf.hideVScroll:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        else:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        if self.mainConf.hideHScroll:
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        else:
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Refresh the tab stops
        if self.mainConf.verQtValue >= 51000:
            self.setTabStopDistance(self.mainConf.getTabWidth())
        else:
            self.setTabStopWidth(self.mainConf.getTabWidth())

        # If we have a document open, we should reload it in case the font changed
        if self._docHandle is not None:
            self.reloadText()

        return True

    def loadText(self, tHandle, updateHistory=True):
        """Load text into the viewer from an item handle.
        """
        tItem = self.theProject.projTree[tHandle]
        if tItem is None:
            logger.warning("Item not found")
            return False

        if tItem.itemType != nwItemType.FILE:
            return False

        logger.debug("Generating preview for item '%s'", tHandle)
        qApp.setOverrideCursor(QCursor(Qt.WaitCursor))

        sPos = self.verticalScrollBar().value()
        aDoc = ToHtml(self.theProject)
        aDoc.setPreview(self.mainConf.viewComments, self.mainConf.viewSynopsis)
        aDoc.setLinkHeaders(True)

        # Be extra careful here to prevent crashes when first opening a
        # project as a crash here leaves no way of recovering.
        # See issue #298
        try:
            aDoc.setText(tHandle)
            aDoc.doPreProcessing()
            aDoc.tokenizeText()
            aDoc.doConvert()
            aDoc.doPostProcessing()
        except Exception:
            logger.error("Failed to generate preview for document with handle '%s'", tHandle)
            nw.logException()
            self.setText(self.tr("An error occurred while generating the preview."))
            return False

        # Refresh the tab stops
        if self.mainConf.verQtValue >= 51000:
            self.setTabStopDistance(self.mainConf.getTabWidth())
        else:
            self.setTabStopWidth(self.mainConf.getTabWidth())

        # Must be before setHtml
        if updateHistory:
            self.docHistory.append(tHandle)

        self.setHtml(aDoc.theResult.replace("\t", "!!tab!!"))
        self.setDocumentTitle(tHandle)

        # Loop through the text and put back in the tabs. Tabs are removed by
        # the setHtml function, so the ToHtml class puts in a placeholder.
        while self.find("!!tab!!"):
            theCursor = self.textCursor()
            theCursor.insertText("\t")

        if self._docHandle == tHandle:
            # This is a refresh, so we set the scrollbar back to where it was
            self.verticalScrollBar().setValue(sPos)

        self._docHandle = tHandle
        self.theProject.setLastViewed(tHandle)
        self.docHeader.setTitleFromHandle(self._docHandle)
        self.updateDocMargins()

        # Make sure the main GUI knows we changed the content
        self.theParent.viewMeta.refreshReferences(tHandle)

        # Since we change the content while it may still be rendering, we mark
        # the document dirty again to make sure it's re-rendered properly.
        self.redrawText()
        qApp.restoreOverrideCursor()

        return True

    def reloadText(self):
        """Reload the text in the current document.
        """
        self.loadText(self._docHandle, updateHistory=False)
        return

    def redrawText(self):
        """Redraw the text by marking the document content as "dirty".
        """
        self.document().markContentsDirty(0, self.document().characterCount())
        self.updateDocMargins()
        return

    def loadFromTag(self, theTag):
        """Load text in the document from a reference given by a meta
        tag rather than a known handle. This function depends on the
        index being up to date.
        """
        logger.debug("Loading document from tag '%s'", theTag)
        tHandle, _, sTitle = self.theParent.theIndex.getTagSource(theTag)
        if tHandle is None:
            self.theParent.makeAlert(self.tr(
                "Could not find the reference for tag '{0}'. It either doesn't "
                "exist, or the index is out of date. The index can be updated "
                "from the Tools menu, or by pressing {1}."
            ).format(
                theTag, "F9"
            ), nwAlert.ERROR)
            return False
        else:
            # Let the parent handle the opening as it also ensures that
            # the doc view panel is visible in case this request comes
            # from outside this class.
            logger.verbose("Tag points to '%s#%s'", tHandle, sTitle)
            self.theParent.viewDocument(tHandle, "#%s" % sTitle)
        return True

    def docAction(self, theAction):
        """Wrapper function for various document actions on the current
        document.
        """
        logger.verbose("Requesting action: '%s'", theAction.name)
        if self._docHandle is None:
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
            logger.debug("Unknown or unsupported document action '%s'", str(theAction))
            return False
        return True

    def navigateTo(self, tAnchor):
        """Go to a specific #link in the document.
        """
        if not isinstance(tAnchor, str):
            return False
        if tAnchor.startswith("#"):
            logger.verbose("Moving to anchor '%s'", tAnchor)
            self.setSource(QUrl(tAnchor))
        return True

    def navBackward(self):
        """Navigate backwards in the document view history.
        """
        self.docHistory.backward()
        return

    def navForward(self):
        """Navigate forwards in the document view history.
        """
        self.docHistory.forward()
        return

    def clearNavHistory(self):
        """Clear the navigation history.
        """
        self.docHistory.clear()
        return

    def updateDocMargins(self):
        """Automatically adjust the margins so the text is centred.
        """
        vBar = self.verticalScrollBar()
        sW = vBar.width() if vBar.isVisible() else 0

        hBar = self.horizontalScrollBar()
        sH = hBar.height() if hBar.isVisible() else 0

        cM = self.mainConf.getTextMargin()
        tB = self.frameWidth()
        tW = self.width() - 2*tB - sW
        tH = self.docHeader.height()
        fH = self.docFooter.height()
        fY = self.height() - fH - tB - sH

        self.docHeader.setGeometry(tB, tB, tW, tH)
        self.docFooter.setGeometry(tB, fY, tW, fH)
        self.setViewportMargins(cM, max(cM, tH), cM, max(cM, fH))

        return

    def updateDocInfo(self, tHandle):
        """Called when an item label is changed to check if the document
        title bar needs updating,
        """
        if tHandle == self._docHandle:
            self.docHeader.setTitleFromHandle(self._docHandle)
            self.updateDocMargins()
        return

    ##
    #  Properties
    ##

    def docHandle(self):
        """Return the handle of the currently open document. Returns
        None if no document is open.
        """
        return self._docHandle

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
            theBlock = self.document().findBlockByLineNumber(theLine)
            if theBlock:
                self.setCursorPosition(theBlock.position())
                logger.verbose("Cursor moved to line %d", theLine)
        return True

    def setScrollPosition(self, thePos):
        """Set the scrollbar position.
        """
        vBar = self.verticalScrollBar()
        if vBar.isVisible():
            vBar.setValue(thePos)
        return

    ##
    #  Getters
    ##

    def getScrollPosition(self):
        """Get the scrollbar position. Returns 0 if no scrollbar.
        """
        vBar = self.verticalScrollBar()
        if vBar.isVisible():
            return vBar.value()
        return 0

    ##
    #  Slots
    ##

    @pyqtSlot("QUrl")
    def _linkClicked(self, theURL):
        """Slot for a link in the document being clicked.
        """
        theLink = theURL.url()
        logger.verbose("Clicked link: '%s'", theLink)
        if len(theLink) > 0:
            theBits = theLink.split("=")
            if len(theBits) == 2:
                self.loadFromTag(theBits[1])
        return

    @pyqtSlot("QPoint")
    def _openContextMenu(self, thePos):
        """Triggered by right click to open the context menu.
        """
        userCursor = self.textCursor()
        userSelection = userCursor.hasSelection()

        mnuContext = QMenu()

        # Cut, Copy and Paste
        # ===================

        if userSelection:
            mnuCopy = QAction(self.tr("Copy"), mnuContext)
            mnuCopy.triggered.connect(lambda: self.docAction(nwDocAction.COPY))
            mnuContext.addAction(mnuCopy)

            mnuContext.addSeparator()

        # Selections
        # ==========

        mnuSelAll = QAction(self.tr("Select All"), mnuContext)
        mnuSelAll.triggered.connect(lambda: self.docAction(nwDocAction.SEL_ALL))
        mnuContext.addAction(mnuSelAll)

        mnuSelWord = QAction(self.tr("Select Word"), mnuContext)
        mnuSelWord.triggered.connect(
            lambda: self._makePosSelection(QTextCursor.WordUnderCursor, thePos)
        )
        mnuContext.addAction(mnuSelWord)

        mnuSelPara = QAction(self.tr("Select Paragraph"), mnuContext)
        mnuSelPara.triggered.connect(
            lambda: self._makePosSelection(QTextCursor.BlockUnderCursor, thePos)
        )
        mnuContext.addAction(mnuSelPara)

        # Open the context menu
        mnuContext.exec_(self.viewport().mapToGlobal(thePos))

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

    def mouseReleaseEvent(self, theEvent):
        """Capture mouse click events on the document.
        """
        if theEvent.button() == Qt.BackButton:
            self.navBackward()
        elif theEvent.button() == Qt.ForwardButton:
            self.navForward()
        else:
            QTextBrowser.mouseReleaseEvent(self, theEvent)
        return

    ##
    #  Internal Functions
    ##

    def _makeSelection(self, selMode):
        """Wrapper function to select text based on a selection mode.
        """
        theCursor = self.textCursor()
        theCursor.clearSelection()
        theCursor.select(selMode)

        if selMode == QTextCursor.BlockUnderCursor:
            # This selection mode also selects the preceding oaragraph
            # separator, which we want to avoid.
            posS = theCursor.selectionStart()
            posE = theCursor.selectionEnd()
            selTxt = theCursor.selectedText()
            if selTxt.startswith(nwUnicode.U_PSEP):
                theCursor.setPosition(posS+1, QTextCursor.MoveAnchor)
                theCursor.setPosition(posE, QTextCursor.KeepAnchor)

        self.setTextCursor(theCursor)

        return

    def _makePosSelection(self, selMode, thePos):
        """Wrapper function to select text based on selection mode, but
        first move cursor to given position.
        """
        theCursor = self.cursorForPosition(thePos)
        self.setTextCursor(theCursor)
        self._makeSelection(selMode)
        return

    def _makeStyleSheet(self):
        """Generate an appropriate style sheet for the document viewer,
        based on the current syntax highlighter theme,
        """
        styleSheet = (
            "body {{"
            "  color: rgb({tColR}, {tColG}, {tColB});"
            "}}\n"
            "h1, h2, h3, h4 {{"
            "  color: rgb({hColR}, {hColG}, {hColB});"
            "}}\n"
            "a {{"
            "  color: rgb({aColR}, {aColG}, {aColB});"
            "}}\n"
            "mark {{"
            "  color: rgb({eColR}, {eColG}, {eColB});"
            "}}\n"
            ".tags {{"
            "  color: rgb({kColR}, {kColG}, {kColB});"
            "}}\n"
            ".comment {{"
            "  color: rgb({cColR}, {cColG}, {cColB});"
            "}}\n"
            ".synopsis {{"
            "  color: rgb({mColR}, {mColG}, {mColB});"
            "}}\n"
            ".title {{"
            "  text-align: center;"
            "}}\n"
        ).format(
            tColR=self.theTheme.colText[0],
            tColG=self.theTheme.colText[1],
            tColB=self.theTheme.colText[2],
            hColR=self.theTheme.colHead[0],
            hColG=self.theTheme.colHead[1],
            hColB=self.theTheme.colHead[2],
            aColR=self.theTheme.colVal[0],
            aColG=self.theTheme.colVal[1],
            aColB=self.theTheme.colVal[2],
            eColR=self.theTheme.colEmph[0],
            eColG=self.theTheme.colEmph[1],
            eColB=self.theTheme.colEmph[2],
            kColR=self.theTheme.colKey[0],
            kColG=self.theTheme.colKey[1],
            kColB=self.theTheme.colKey[2],
            cColR=self.theTheme.colHidden[0],
            cColG=self.theTheme.colHidden[1],
            cColB=self.theTheme.colHidden[2],
            mColR=self.theTheme.colMod[0],
            mColG=self.theTheme.colMod[1],
            mColB=self.theTheme.colMod[2],
        )
        self.document().setDefaultStyleSheet(styleSheet)

        return True

# END Class GuiDocViewer


class GuiDocViewHistory():

    def __init__(self, docViewer):

        self.docViewer = docViewer

        self._navHistory = []
        self._posHistory = []
        self._currPos = -1
        self._prevPos = -1

        return

    def clear(self):
        """Clear the view history.
        """
        logger.verbose("View history cleared")
        self._navHistory = []
        self._posHistory = []
        self._currPos = -1
        self._prevPos = -1
        return

    def append(self, tHandle):
        """Append a document handle and its scroll bar position to the
        history, but only if the document is different than the current
        active entry. Any further entries are truncated.
        """
        if self._currPos >= 0 and self._currPos < len(self._navHistory):
            if tHandle == self._navHistory[self._currPos]:
                logger.verbose("Not updating view hsitory")
                return False

        self._truncateHistory(self._currPos)

        self._navHistory.append(tHandle)
        self._posHistory.append(0)

        self._prevPos = self._currPos
        self._currPos = len(self._navHistory) - 1
        self._updateScrollBar()
        self._updateNavButtons()

        self._dumpHistory()

        logger.verbose("Added '%s' to view history", tHandle)

        return True

    def forward(self):
        """Navigate to the next entry in the view history.
        """
        newPos = self._currPos + 1
        if newPos < len(self._navHistory):
            logger.verbose("Move forward in view history")
            self._prevPos = self._currPos
            self._updateScrollBar()

            self.docViewer.loadText(self._navHistory[newPos], updateHistory=False)
            self.docViewer.setScrollPosition(self._posHistory[newPos])
            self._currPos = newPos
            self._updateNavButtons()

            self._dumpHistory()

        return

    def backward(self):
        """Navigate to the previous entry in the view history.
        """
        newPos = self._currPos - 1
        if newPos >= 0:
            logger.verbose("Move backward in view history")
            self._prevPos = self._currPos
            self._updateScrollBar()

            self.docViewer.loadText(self._navHistory[newPos], updateHistory=False)
            self.docViewer.setScrollPosition(self._posHistory[newPos])
            self._currPos = newPos
            self._updateNavButtons()

            self._dumpHistory()

        return

    ##
    #  Internal Functions
    ##

    def _updateScrollBar(self):
        """Update the scrollbar position of the previous entry.
        """
        if self._prevPos >= 0 and self._prevPos < len(self._posHistory):
            self._posHistory[self._prevPos] = self.docViewer.getScrollPosition()
        return

    def _updateNavButtons(self):
        """Update the navigation buttons in the document header.
        """
        self.docViewer.docHeader.updateNavButtons(0, len(self._navHistory) - 1, self._currPos)
        return

    def _truncateHistory(self, atPos):
        """Truncate the navigation history to the given position. Also
        enforces a maximum length of the navigation history to 20.
        """
        nSkip = 1 if atPos > 19 else 0

        self._navHistory = self._navHistory[nSkip:atPos + 1]
        self._posHistory = self._posHistory[nSkip:atPos + 1]

        self._currPos -= nSkip
        self._prevPos -= nSkip

        return

    def _dumpHistory(self):
        """Debug function to dump history to the logger. Since it is a
        for loop, it is skipped entirely if log level isn't VERBOSE.
        """
        if logger.getEffectiveLevel() < logging.DEBUG:
            for i, (h, p) in enumerate(zip(self._navHistory, self._posHistory)):
                logger.verbose(
                    "History %02d: %s %13s [x:%d]" % (
                        i + 1, ">" if i == self._currPos else " ", h, p
                    )
                )
        return

# END Class GuiDocViewHistory


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

        # Internal Variables
        self._docHandle = None

        fPx = int(0.9*self.theTheme.fontPixelSize)
        hSp = self.mainConf.pxInt(6)

        # Main Widget Settings
        self.setAutoFillBackground(True)

        # Title Label
        self.theTitle = QLabel()
        self.theTitle.setText("")
        self.theTitle.setIndent(0)
        self.theTitle.setMargin(0)
        self.theTitle.setContentsMargins(0, 0, 0, 0)
        self.theTitle.setAutoFillBackground(True)
        self.theTitle.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.theTitle.setFixedHeight(fPx)

        lblFont = self.theTitle.font()
        lblFont.setPointSizeF(0.9*self.theTheme.fontPointSize)
        self.theTitle.setFont(lblFont)

        buttonStyle = (
            "QToolButton {{border: none; background: transparent;}} "
            "QToolButton:hover {{border: none; background: rgba({0},{1},{2},0.2);}}"
        ).format(*self.theTheme.colText)

        # Buttons
        self.backButton = QToolButton(self)
        self.backButton.setIcon(self.theTheme.getIcon("backward"))
        self.backButton.setContentsMargins(0, 0, 0, 0)
        self.backButton.setIconSize(QSize(fPx, fPx))
        self.backButton.setFixedSize(fPx, fPx)
        self.backButton.setStyleSheet(buttonStyle)
        self.backButton.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.backButton.setVisible(False)
        self.backButton.setToolTip(self.tr("Go backward"))
        self.backButton.clicked.connect(self.docViewer.navBackward)

        self.forwardButton = QToolButton(self)
        self.forwardButton.setIcon(self.theTheme.getIcon("forward"))
        self.forwardButton.setContentsMargins(0, 0, 0, 0)
        self.forwardButton.setIconSize(QSize(fPx, fPx))
        self.forwardButton.setFixedSize(fPx, fPx)
        self.forwardButton.setStyleSheet(buttonStyle)
        self.forwardButton.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.forwardButton.setVisible(False)
        self.forwardButton.setToolTip(self.tr("Go forward"))
        self.forwardButton.clicked.connect(self.docViewer.navForward)

        self.refreshButton = QToolButton(self)
        self.refreshButton.setIcon(self.theTheme.getIcon("refresh"))
        self.refreshButton.setContentsMargins(0, 0, 0, 0)
        self.refreshButton.setIconSize(QSize(fPx, fPx))
        self.refreshButton.setFixedSize(fPx, fPx)
        self.refreshButton.setStyleSheet(buttonStyle)
        self.refreshButton.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.refreshButton.setVisible(False)
        self.refreshButton.setToolTip(self.tr("Reload the document"))
        self.refreshButton.clicked.connect(self._refreshDocument)

        self.closeButton = QToolButton(self)
        self.closeButton.setIcon(self.theTheme.getIcon("close"))
        self.closeButton.setContentsMargins(0, 0, 0, 0)
        self.closeButton.setIconSize(QSize(fPx, fPx))
        self.closeButton.setFixedSize(fPx, fPx)
        self.closeButton.setStyleSheet(buttonStyle)
        self.closeButton.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.closeButton.setVisible(False)
        self.closeButton.setToolTip(self.tr("Close the document"))
        self.closeButton.clicked.connect(self._closeDocument)

        # Assemble Layout
        self.outerBox = QHBoxLayout()
        self.outerBox.setSpacing(hSp)
        self.outerBox.addWidget(self.backButton, 0)
        self.outerBox.addWidget(self.forwardButton, 0)
        self.outerBox.addWidget(self.theTitle, 1)
        self.outerBox.addWidget(self.refreshButton, 0)
        self.outerBox.addWidget(self.closeButton, 0)
        self.setLayout(self.outerBox)

        # Fix Margins and Size
        # This is needed for high DPI systems. See issue #499.
        cM = self.mainConf.pxInt(8)
        self.setContentsMargins(0, 0, 0, 0)
        self.outerBox.setContentsMargins(cM, cM, cM, cM)
        self.setMinimumHeight(fPx + 2*cM)

        # Fix the Colours
        self.matchColours()

        logger.debug("GuiDocViewHeader initialisation complete")

        return

    ##
    #  Methods
    ##

    def matchColours(self):
        """Update the colours of the widget to match those of the syntax
        theme rather than the main GUI.
        """
        thePalette = QPalette()
        thePalette.setColor(QPalette.Window, QColor(*self.theTheme.colBack))
        thePalette.setColor(QPalette.WindowText, QColor(*self.theTheme.colText))
        thePalette.setColor(QPalette.Text, QColor(*self.theTheme.colText))

        self.setPalette(thePalette)
        self.theTitle.setPalette(thePalette)

        return

    def setTitleFromHandle(self, tHandle):
        """Sets the document title from the handle, or alternatively,
        set the whole document path.
        """
        self._docHandle = tHandle
        if tHandle is None:
            self.theTitle.setText("")
            self.backButton.setVisible(False)
            self.forwardButton.setVisible(False)
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

        self.backButton.setVisible(True)
        self.forwardButton.setVisible(True)
        self.closeButton.setVisible(True)
        self.refreshButton.setVisible(True)

        return True

    def updateNavButtons(self, firstIdx, lastIdx, currIdx):
        """Enable and disable nav buttons based on index in history.
        """
        self.backButton.setEnabled(currIdx > firstIdx)
        self.forwardButton.setEnabled(currIdx < lastIdx)
        return

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
        if self.docViewer.docHandle() == self.theParent.docEditor.docHandle():
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
        self.theParent.treeView.setSelectedHandle(self._docHandle, doScroll=True)
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

        # Internal Variables
        self._docHandle = None

        fPx = int(0.9*self.theTheme.fontPixelSize)
        bSp = self.mainConf.pxInt(2)
        hSp = self.mainConf.pxInt(8)

        # Icons
        stickyOn  = self.theTheme.getPixmap("sticky-on", (fPx, fPx))
        stickyOff = self.theTheme.getPixmap("sticky-off", (fPx, fPx))
        stickyIcon = QIcon()
        stickyIcon.addPixmap(stickyOn, QIcon.Normal, QIcon.On)
        stickyIcon.addPixmap(stickyOff, QIcon.Normal, QIcon.Off)

        bulletOn  = self.theTheme.getPixmap("bullet-on", (fPx, fPx))
        bulletOff = self.theTheme.getPixmap("bullet-off", (fPx, fPx))
        bulletIcon = QIcon()
        bulletIcon.addPixmap(bulletOn, QIcon.Normal, QIcon.On)
        bulletIcon.addPixmap(bulletOff, QIcon.Normal, QIcon.Off)

        # Main Widget Settings
        self.setContentsMargins(0, 0, 0, 0)
        self.setAutoFillBackground(True)

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
        self.showHide.setToolTip(self.tr("Show/hide the references panel"))

        # Sticky Button
        self.stickyRefs = QToolButton(self)
        self.stickyRefs.setCheckable(True)
        self.stickyRefs.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.stickyRefs.setStyleSheet(buttonStyle)
        self.stickyRefs.setIcon(stickyIcon)
        self.stickyRefs.setIconSize(QSize(fPx, fPx))
        self.stickyRefs.setFixedSize(QSize(fPx, fPx))
        self.stickyRefs.toggled.connect(self._doToggleSticky)
        self.stickyRefs.setToolTip(self.tr(
            "Activate to freeze the content of the references panel when changing document"
        ))

        # Show Comments
        self.showComments = QToolButton(self)
        self.showComments.setCheckable(True)
        self.showComments.setChecked(self.mainConf.viewComments)
        self.showComments.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.showComments.setStyleSheet(buttonStyle)
        self.showComments.setIcon(bulletIcon)
        self.showComments.setIconSize(QSize(fPx, fPx))
        self.showComments.setFixedSize(QSize(fPx, fPx))
        self.showComments.toggled.connect(self._doToggleComments)
        self.showComments.setToolTip(self.tr("Show comments"))

        # Show Synopsis
        self.showSynopsis = QToolButton(self)
        self.showSynopsis.setCheckable(True)
        self.showSynopsis.setChecked(self.mainConf.viewSynopsis)
        self.showSynopsis.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.showSynopsis.setStyleSheet(buttonStyle)
        self.showSynopsis.setIcon(bulletIcon)
        self.showSynopsis.setIconSize(QSize(fPx, fPx))
        self.showSynopsis.setFixedSize(QSize(fPx, fPx))
        self.showSynopsis.toggled.connect(self._doToggleSynopsis)
        self.showSynopsis.setToolTip(self.tr("Show synopsis comments"))

        # Labels
        self.lblRefs = QLabel(self.tr("References"))
        self.lblRefs.setBuddy(self.showHide)
        self.lblRefs.setIndent(0)
        self.lblRefs.setMargin(0)
        self.lblRefs.setContentsMargins(0, 0, 0, 0)
        self.lblRefs.setAutoFillBackground(True)
        self.lblRefs.setFixedHeight(fPx)
        self.lblRefs.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        self.lblSticky = QLabel(self.tr("Sticky"))
        self.lblSticky.setBuddy(self.stickyRefs)
        self.lblSticky.setIndent(0)
        self.lblSticky.setMargin(0)
        self.lblSticky.setContentsMargins(0, 0, 0, 0)
        self.lblSticky.setAutoFillBackground(True)
        self.lblSticky.setFixedHeight(fPx)
        self.lblSticky.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        self.lblComments = QLabel(self.tr("Comments"))
        self.lblComments.setBuddy(self.showComments)
        self.lblComments.setIndent(0)
        self.lblComments.setMargin(0)
        self.lblComments.setContentsMargins(0, 0, 0, 0)
        self.lblComments.setAutoFillBackground(True)
        self.lblComments.setFixedHeight(fPx)
        self.lblComments.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        self.lblSynopsis = QLabel(self.tr("Synopsis"))
        self.lblSynopsis.setBuddy(self.showSynopsis)
        self.lblSynopsis.setIndent(0)
        self.lblSynopsis.setMargin(0)
        self.lblSynopsis.setContentsMargins(0, 0, 0, 0)
        self.lblSynopsis.setAutoFillBackground(True)
        self.lblSynopsis.setFixedHeight(fPx)
        self.lblSynopsis.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        lblFont = self.font()
        lblFont.setPointSizeF(0.9*self.theTheme.fontPointSize)
        self.lblRefs.setFont(lblFont)
        self.lblSticky.setFont(lblFont)
        self.lblComments.setFont(lblFont)
        self.lblSynopsis.setFont(lblFont)

        # Assemble Layout
        self.outerBox = QHBoxLayout()
        self.outerBox.setSpacing(bSp)
        self.outerBox.addWidget(self.showHide, 0)
        self.outerBox.addWidget(self.lblRefs, 0)
        self.outerBox.addSpacing(hSp)
        self.outerBox.addWidget(self.stickyRefs, 0)
        self.outerBox.addWidget(self.lblSticky, 0)
        self.outerBox.addStretch(1)
        self.outerBox.addWidget(self.showComments, 0)
        self.outerBox.addWidget(self.lblComments, 0)
        self.outerBox.addSpacing(hSp)
        self.outerBox.addWidget(self.showSynopsis, 0)
        self.outerBox.addWidget(self.lblSynopsis, 0)
        self.setLayout(self.outerBox)

        # Fix Margins and Size
        # This is needed for high DPI systems. See issue #499.
        cM = self.mainConf.pxInt(8)
        self.setContentsMargins(0, 0, 0, 0)
        self.outerBox.setContentsMargins(cM, cM, cM, cM)
        self.setMinimumHeight(fPx + 2*cM)

        # Fix the Colours
        self.matchColours()

        logger.debug("GuiDocViewFooter initialisation complete")

        return

    ##
    #  Methods
    ##

    def matchColours(self):
        """Update the colours of the widget to match those of the syntax
        theme rather than the main GUI.
        """
        thePalette = QPalette()
        thePalette.setColor(QPalette.Window, QColor(*self.theTheme.colBack))
        thePalette.setColor(QPalette.WindowText, QColor(*self.theTheme.colText))
        thePalette.setColor(QPalette.Text, QColor(*self.theTheme.colText))

        self.setPalette(thePalette)
        self.lblRefs.setPalette(thePalette)
        self.lblSticky.setPalette(thePalette)
        self.lblComments.setPalette(thePalette)
        self.lblSynopsis.setPalette(thePalette)

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
        logger.verbose("Reference sticky is %s", str(theState))
        self.docViewer.stickyRef = theState
        if not theState and self.docViewer.docHandle() is not None:
            self.viewMeta.refreshReferences(self.docViewer.docHandle())
        return

    def _doToggleComments(self, theState):
        """Toggle the view comment button and reload the document.
        """
        self.mainConf.setViewComments(theState)
        self.docViewer.reloadText()
        return

    def _doToggleSynopsis(self, theState):
        """Toggle the view synopsis button and reload the document.
        """
        self.mainConf.setViewSynopsis(theState)
        self.docViewer.reloadText()
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

        self.refList = QLabel("")
        self.refList.setWordWrap(True)
        self.refList.setAlignment(Qt.AlignTop)
        self.refList.setScaledContents(True)
        self.refList.linkActivated.connect(self._linkClicked)

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
        if self.theParent.docViewer.stickyRef:
            return

        theRefs = self.theParent.theIndex.getBackReferenceList(tHandle)
        theList = []
        for tHandle in theRefs:
            tItem = self.theProject.projTree[tHandle]
            if tItem is not None:
                theList.append("<a href='%s#%s' %s>%s</a>" % (
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
        logger.verbose("Clicked link: '%s'", theLink)
        if len(theLink) == 21:
            tHandle = theLink[:13]
            tAnchor = theLink[13:]
            self.theParent.viewDocument(tHandle, tAnchor)
        return

# END Class GuiDocViewDetails
