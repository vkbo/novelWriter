"""
novelWriter – GUI Document Viewer
=================================
GUI classes for the main document viewer

File History:
Created: 2019-05-10 [0.0.1] GuiDocViewer
Created: 2019-10-31 [0.3.2] GuiDocViewDetails
Created: 2020-04-25 [0.4.5] GuiDocViewHeader
Created: 2020-06-09 [0.8]   GuiDocViewFooter
Created: 2020-09-08 [1.0b1] GuiDocViewHistory

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

from enum import Enum

from PyQt5.QtCore import Qt, QUrl, QSize, pyqtSlot, pyqtSignal
from PyQt5.QtGui import (
    QTextOption, QFont, QPalette, QColor, QTextCursor, QIcon, QCursor
)
from PyQt5.QtWidgets import (
    qApp, QTextBrowser, QWidget, QScrollArea, QLabel, QHBoxLayout, QToolButton,
    QAction, QMenu, QFrame
)

from novelwriter.enum import nwItemType, nwDocAction, nwDocMode
from novelwriter.error import logException
from novelwriter.constants import nwUnicode
from novelwriter.core.tohtml import ToHtml

logger = logging.getLogger(__name__)


class GuiDocViewer(QTextBrowser):

    loadDocumentTagRequest = pyqtSignal(str, Enum)

    def __init__(self, mainGui):
        super().__init__(parent=mainGui)

        logger.debug("Initialising GuiDocViewer ...")

        # Class Variables
        self.mainConf   = novelwriter.CONFIG
        self.mainGui    = mainGui
        self.mainTheme  = mainGui.mainTheme
        self.theProject = mainGui.theProject

        # Internal Variables
        self._docHandle = None

        # Settings
        self.setMinimumWidth(self.mainConf.pxInt(300))
        self.setAutoFillBackground(True)
        self.setOpenExternalLinks(False)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFrameStyle(QFrame.NoFrame)

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

    def updateTheme(self):
        """Update theme elements.
        """
        self.docHeader.updateTheme()
        self.docFooter.updateTheme()
        return

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
        mainPalette.setColor(QPalette.Window, QColor(*self.mainTheme.colBack))
        mainPalette.setColor(QPalette.Base, QColor(*self.mainTheme.colBack))
        mainPalette.setColor(QPalette.Text, QColor(*self.mainTheme.colText))
        self.setPalette(mainPalette)

        docPalette = self.viewport().palette()
        docPalette.setColor(QPalette.Base, QColor(*self.mainTheme.colBack))
        docPalette.setColor(QPalette.Text, QColor(*self.mainTheme.colText))
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
        self.setTabStopDistance(self.mainConf.getTabWidth())

        # If we have a document open, we should reload it in case the font changed
        if self._docHandle is not None:
            self.reloadText()

        return True

    def loadText(self, tHandle, updateHistory=True):
        """Load text into the viewer from an item handle.
        """
        if not self.theProject.tree.checkType(tHandle, nwItemType.FILE):
            logger.warning("Item not found")
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
            logException()
            self.setText(self.tr("An error occurred while generating the preview."))
            qApp.restoreOverrideCursor()
            return False

        # Refresh the tab stops
        self.setTabStopDistance(self.mainConf.getTabWidth())

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
        self.theProject._data.setLastHandle(tHandle, "viewer")
        self.docHeader.setTitleFromHandle(self._docHandle)
        self.updateDocMargins()

        # Make sure the main GUI knows we changed the content
        self.mainGui.viewMeta.refreshReferences(tHandle)

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

    def docAction(self, theAction):
        """Wrapper function for various document actions on the current
        document.
        """
        logger.debug("Requesting action: '%s'", theAction.name)
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
            logger.debug("Moving to anchor '%s'", tAnchor)
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
        wW = self.width()
        wH = self.height()
        cM = self.mainConf.getTextMargin()

        vBar = self.verticalScrollBar()
        sW = vBar.width() if vBar.isVisible() else 0

        hBar = self.horizontalScrollBar()
        sH = hBar.height() if hBar.isVisible() else 0

        tM = cM
        if self.mainConf.textWidth > 0:
            tW = self.mainConf.getTextWidth()
            tM = max((wW - sW - tW)//2, cM)

        tB = self.frameWidth()
        tW = wW - 2*tB - sW
        tH = self.docHeader.height()
        fH = self.docFooter.height()
        fY = wH - fH - tB - sH

        self.docHeader.setGeometry(tB, tB, tW, tH)
        self.docFooter.setGeometry(tB, fY, tW, fH)
        self.setViewportMargins(tM, max(cM, tH), tM, max(cM, fH))

        return

    ##
    #  Setters
    ##

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

    def docHandle(self):
        """Return the handle of the currently open document. Returns
        None if no document is open.
        """
        return self._docHandle

    def getScrollPosition(self):
        """Get the scrollbar position. Returns 0 if no scrollbar.
        """
        vBar = self.verticalScrollBar()
        if vBar.isVisible():
            return vBar.value()
        return 0

    ##
    #  Public Slots
    ##

    @pyqtSlot(str)
    def updateDocInfo(self, tHandle):
        """Called when an item label is changed to check if the document
        title bar needs updating,
        """
        if tHandle == self._docHandle:
            self.docHeader.setTitleFromHandle(self._docHandle)
            self.updateDocMargins()
        return

    ##
    #  Private Slots
    ##

    @pyqtSlot("QUrl")
    def _linkClicked(self, theURL):
        """Process a clicked link internally in the document.
        """
        theLink = theURL.url()
        logger.debug("Clicked link: '%s'", theLink)
        if len(theLink) > 0:
            theBits = theLink.split("=")
            if len(theBits) == 2:
                self.loadDocumentTagRequest.emit(theBits[1], nwDocMode.VIEW)
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
        """If the text editor is resized, we must make sure the document
        has its margins adjusted according to user preferences.
        """
        self.updateDocMargins()
        super().resizeEvent(theEvent)
        return

    def mouseReleaseEvent(self, theEvent):
        """Capture mouse click events on the document.
        """
        if theEvent.button() == Qt.BackButton:
            self.navBackward()
        elif theEvent.button() == Qt.ForwardButton:
            self.navForward()
        else:
            super().mouseReleaseEvent(theEvent)
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
            tColR=self.mainTheme.colText[0],
            tColG=self.mainTheme.colText[1],
            tColB=self.mainTheme.colText[2],
            hColR=self.mainTheme.colHead[0],
            hColG=self.mainTheme.colHead[1],
            hColB=self.mainTheme.colHead[2],
            aColR=self.mainTheme.colVal[0],
            aColG=self.mainTheme.colVal[1],
            aColB=self.mainTheme.colVal[2],
            eColR=self.mainTheme.colEmph[0],
            eColG=self.mainTheme.colEmph[1],
            eColB=self.mainTheme.colEmph[2],
            kColR=self.mainTheme.colKey[0],
            kColG=self.mainTheme.colKey[1],
            kColB=self.mainTheme.colKey[2],
            cColR=self.mainTheme.colHidden[0],
            cColG=self.mainTheme.colHidden[1],
            cColB=self.mainTheme.colHidden[2],
            mColR=self.mainTheme.colMod[0],
            mColG=self.mainTheme.colMod[1],
            mColB=self.mainTheme.colMod[2],
        )
        self.document().setDefaultStyleSheet(styleSheet)

        return True

# END Class GuiDocViewer


class GuiDocViewHistory:

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
        logger.debug("View history cleared")
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
                logger.debug("Not updating view hsitory")
                return False

        self._truncateHistory(self._currPos)

        self._navHistory.append(tHandle)
        self._posHistory.append(0)

        self._prevPos = self._currPos
        self._currPos = len(self._navHistory) - 1
        self._updateScrollBar()
        self._updateNavButtons()

        self._dumpHistory()

        logger.debug("Added '%s' to view history", tHandle)

        return True

    def forward(self):
        """Navigate to the next entry in the view history.
        """
        newPos = self._currPos + 1
        if newPos < len(self._navHistory):
            logger.debug("Move forward in view history")
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
            logger.debug("Move backward in view history")
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
        for loop, it is skipped entirely if log level isn't DEBUG.
        """
        if logger.getEffectiveLevel() == logging.DEBUG:
            for i, (h, p) in enumerate(zip(self._navHistory, self._posHistory)):
                logger.debug(
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
        super().__init__(parent=docViewer)

        logger.debug("Initialising GuiDocViewHeader ...")

        self.mainConf   = novelwriter.CONFIG
        self.docViewer  = docViewer
        self.mainGui    = docViewer.mainGui
        self.theProject = docViewer.theProject
        self.mainTheme  = docViewer.mainTheme

        # Internal Variables
        self._docHandle = None

        fPx = int(0.9*self.mainTheme.fontPixelSize)
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
        lblFont.setPointSizeF(0.9*self.mainTheme.fontPointSize)
        self.theTitle.setFont(lblFont)

        # Buttons
        self.backButton = QToolButton(self)
        self.backButton.setContentsMargins(0, 0, 0, 0)
        self.backButton.setIconSize(QSize(fPx, fPx))
        self.backButton.setFixedSize(fPx, fPx)
        self.backButton.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.backButton.setVisible(False)
        self.backButton.setToolTip(self.tr("Go backward"))
        self.backButton.clicked.connect(self.docViewer.navBackward)

        self.forwardButton = QToolButton(self)
        self.forwardButton.setContentsMargins(0, 0, 0, 0)
        self.forwardButton.setIconSize(QSize(fPx, fPx))
        self.forwardButton.setFixedSize(fPx, fPx)
        self.forwardButton.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.forwardButton.setVisible(False)
        self.forwardButton.setToolTip(self.tr("Go forward"))
        self.forwardButton.clicked.connect(self.docViewer.navForward)

        self.refreshButton = QToolButton(self)
        self.refreshButton.setContentsMargins(0, 0, 0, 0)
        self.refreshButton.setIconSize(QSize(fPx, fPx))
        self.refreshButton.setFixedSize(fPx, fPx)
        self.refreshButton.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.refreshButton.setVisible(False)
        self.refreshButton.setToolTip(self.tr("Reload the document"))
        self.refreshButton.clicked.connect(self._refreshDocument)

        self.closeButton = QToolButton(self)
        self.closeButton.setContentsMargins(0, 0, 0, 0)
        self.closeButton.setIconSize(QSize(fPx, fPx))
        self.closeButton.setFixedSize(fPx, fPx)
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
        self.updateTheme()

        logger.debug("GuiDocViewHeader initialisation complete")

        return

    ##
    #  Methods
    ##

    def updateTheme(self):
        """Update theme elements.
        """
        self.backButton.setIcon(self.mainTheme.getIcon("backward"))
        self.forwardButton.setIcon(self.mainTheme.getIcon("forward"))
        self.refreshButton.setIcon(self.mainTheme.getIcon("refresh"))
        self.closeButton.setIcon(self.mainTheme.getIcon("close"))

        buttonStyle = (
            "QToolButton {{border: none; background: transparent;}} "
            "QToolButton:hover {{border: none; background: rgba({0},{1},{2},0.2);}}"
        ).format(*self.mainTheme.colText)

        self.backButton.setStyleSheet(buttonStyle)
        self.forwardButton.setStyleSheet(buttonStyle)
        self.refreshButton.setStyleSheet(buttonStyle)
        self.closeButton.setStyleSheet(buttonStyle)

        self.matchColours()

        return

    def matchColours(self):
        """Update the colours of the widget to match those of the syntax
        theme rather than the main GUI.
        """
        thePalette = QPalette()
        thePalette.setColor(QPalette.Window, QColor(*self.mainTheme.colBack))
        thePalette.setColor(QPalette.WindowText, QColor(*self.mainTheme.colText))
        thePalette.setColor(QPalette.Text, QColor(*self.mainTheme.colText))

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
            tTree = self.theProject.tree.getItemPath(tHandle)
            for aHandle in reversed(tTree):
                nwItem = self.theProject.tree[aHandle]
                if nwItem is not None:
                    tTitle.append(nwItem.itemName)
            sSep = "  %s  " % nwUnicode.U_RSAQUO
            self.theTitle.setText(sSep.join(tTitle))
        else:
            nwItem = self.theProject.tree[tHandle]
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

    @pyqtSlot()
    def _closeDocument(self):
        """Trigger the close editor/viewer on the main window.
        """
        self.mainGui.closeDocViewer()
        return

    @pyqtSlot()
    def _refreshDocument(self):
        """Reload the content of the document.
        """
        if self.docViewer.docHandle() == self.mainGui.docEditor.docHandle():
            self.mainGui.saveDocument()
        self.docViewer.reloadText()
        return

    ##
    #  Events
    ##

    def mousePressEvent(self, theEvent):
        """Capture a click on the title and ensure that the item is
        selected in the project tree.
        """
        self.mainGui.projView.setSelectedHandle(self._docHandle, doScroll=True)
        return

# END Class GuiDocViewHeader


# =============================================================================================== #
#  The Embedded Document Footer
#  Only used by DocViewer, and is at a fixed position in the QTextBrowser's viewport
# =============================================================================================== #

class GuiDocViewFooter(QWidget):

    def __init__(self, docViewer):
        super().__init__(parent=docViewer)

        logger.debug("Initialising GuiDocViewFooter ...")

        self.mainConf  = novelwriter.CONFIG
        self.docViewer = docViewer
        self.mainGui   = docViewer.mainGui
        self.mainTheme = docViewer.mainTheme
        self.viewMeta  = docViewer.mainGui.viewMeta

        # Internal Variables
        self._docHandle = None

        fPx = int(0.9*self.mainTheme.fontPixelSize)
        bSp = self.mainConf.pxInt(2)
        hSp = self.mainConf.pxInt(8)

        # Main Widget Settings
        self.setContentsMargins(0, 0, 0, 0)
        self.setAutoFillBackground(True)

        # Show/Hide Details
        self.showHide = QToolButton(self)
        self.showHide.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.showHide.setIconSize(QSize(fPx, fPx))
        self.showHide.setFixedSize(QSize(fPx, fPx))
        self.showHide.clicked.connect(self._doShowHide)
        self.showHide.setToolTip(self.tr("Show/hide the references panel"))

        # Sticky Button
        self.stickyRefs = QToolButton(self)
        self.stickyRefs.setCheckable(True)
        self.stickyRefs.setToolButtonStyle(Qt.ToolButtonIconOnly)
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
        self.showComments.setIconSize(QSize(fPx, fPx))
        self.showComments.setFixedSize(QSize(fPx, fPx))
        self.showComments.toggled.connect(self._doToggleComments)
        self.showComments.setToolTip(self.tr("Show comments"))

        # Show Synopsis
        self.showSynopsis = QToolButton(self)
        self.showSynopsis.setCheckable(True)
        self.showSynopsis.setChecked(self.mainConf.viewSynopsis)
        self.showSynopsis.setToolButtonStyle(Qt.ToolButtonIconOnly)
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
        lblFont.setPointSizeF(0.9*self.mainTheme.fontPointSize)
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
        self.updateTheme()

        logger.debug("GuiDocViewFooter initialisation complete")

        return

    ##
    #  Methods
    ##

    def updateTheme(self):
        """Update theme elements.
        """
        # Icons

        fPx = int(0.9*self.mainTheme.fontPixelSize)

        stickyOn  = self.mainTheme.getPixmap("sticky-on", (fPx, fPx))
        stickyOff = self.mainTheme.getPixmap("sticky-off", (fPx, fPx))
        stickyIcon = QIcon()
        stickyIcon.addPixmap(stickyOn, QIcon.Normal, QIcon.On)
        stickyIcon.addPixmap(stickyOff, QIcon.Normal, QIcon.Off)

        bulletOn  = self.mainTheme.getPixmap("bullet-on", (fPx, fPx))
        bulletOff = self.mainTheme.getPixmap("bullet-off", (fPx, fPx))
        bulletIcon = QIcon()
        bulletIcon.addPixmap(bulletOn, QIcon.Normal, QIcon.On)
        bulletIcon.addPixmap(bulletOff, QIcon.Normal, QIcon.Off)

        self.showHide.setIcon(self.mainTheme.getIcon("reference"))
        self.stickyRefs.setIcon(stickyIcon)
        self.showComments.setIcon(bulletIcon)
        self.showSynopsis.setIcon(bulletIcon)

        # StyleSheets

        buttonStyle = (
            "QToolButton {{border: none; background: transparent;}} "
            "QToolButton:hover {{border: none; background: rgba({0},{1},{2},0.2);}}"
        ).format(*self.mainTheme.colText)

        self.showHide.setStyleSheet(buttonStyle)
        self.stickyRefs.setStyleSheet(buttonStyle)
        self.showComments.setStyleSheet(buttonStyle)
        self.showSynopsis.setStyleSheet(buttonStyle)

        self.matchColours()

        return

    def matchColours(self):
        """Update the colours of the widget to match those of the syntax
        theme rather than the main GUI.
        """
        thePalette = QPalette()
        thePalette.setColor(QPalette.Window, QColor(*self.mainTheme.colBack))
        thePalette.setColor(QPalette.WindowText, QColor(*self.mainTheme.colText))
        thePalette.setColor(QPalette.Text, QColor(*self.mainTheme.colText))

        self.setPalette(thePalette)
        self.lblRefs.setPalette(thePalette)
        self.lblSticky.setPalette(thePalette)
        self.lblComments.setPalette(thePalette)
        self.lblSynopsis.setPalette(thePalette)

        return

    ##
    #  Slots
    ##

    @pyqtSlot()
    def _doShowHide(self):
        """Toggle the expand/collapse of the panel.
        """
        isVisible = self.viewMeta.isVisible()
        self.viewMeta.setVisible(not isVisible)
        return

    @pyqtSlot(bool)
    def _doToggleSticky(self, theState):
        """Toggle the sticky flag for the reference panel.
        """
        logger.debug("Reference sticky is %s", str(theState))
        self.docViewer.stickyRef = theState
        if not theState and self.docViewer.docHandle() is not None:
            self.viewMeta.refreshReferences(self.docViewer.docHandle())
        return

    @pyqtSlot(bool)
    def _doToggleComments(self, theState):
        """Toggle the view comment button and reload the document.
        """
        self.mainConf.viewComments = theState
        self.docViewer.reloadText()
        return

    @pyqtSlot(bool)
    def _doToggleSynopsis(self, theState):
        """Toggle the view synopsis button and reload the document.
        """
        self.mainConf.viewSynopsis = theState
        self.docViewer.reloadText()
        return

# END Class GuiDocViewFooter


# =============================================================================================== #
#  The Document Back-Reference Panel
#  Placed in a separate QSplitter position in the main GUI window
# =============================================================================================== #

class GuiDocViewDetails(QScrollArea):

    def __init__(self, mainGui):
        super().__init__(parent=mainGui)

        logger.debug("Initialising GuiDocViewDetails ...")
        self.mainConf   = novelwriter.CONFIG
        self.mainGui    = mainGui
        self.theProject = mainGui.theProject
        self.mainTheme  = mainGui.mainTheme

        self.refList = QLabel("")
        self.refList.setWordWrap(True)
        self.refList.setAlignment(Qt.AlignTop)
        self.refList.setScaledContents(True)
        self.refList.linkActivated.connect(self._linkClicked)

        self.linkStyle = "style='color: rgb({0},{1},{2})'".format(
            *self.mainTheme.colLink
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
        self.setFrameStyle(QFrame.NoFrame)

        logger.debug("GuiDocViewDetails initialisation complete")

        return

    def refreshReferences(self, tHandle):
        """Update the current list of document references from the
        project index.
        """
        if self.mainGui.docViewer.stickyRef:
            return

        theRefs = self.theProject.index.getBackReferenceList(tHandle)
        theList = []
        for tHandle in theRefs:
            tItem = self.theProject.tree[tHandle]
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
        logger.debug("Clicked link: '%s'", theLink)
        if len(theLink) == 21:
            tHandle = theLink[:13]
            tAnchor = theLink[13:]
            self.mainGui.viewDocument(tHandle, tAnchor)
        return

# END Class GuiDocViewDetails
