"""
novelWriter – GUI Document Viewer
=================================

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
from __future__ import annotations

import logging

from enum import Enum
from typing import TYPE_CHECKING

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QPoint, QSize, Qt, QUrl
from PyQt5.QtGui import (
    QColor, QCursor, QFont, QMouseEvent, QPalette, QResizeEvent, QTextCursor,
    QTextOption
)
from PyQt5.QtWidgets import (
    QAction, qApp, QFrame, QHBoxLayout, QLabel, QMenu, QScrollArea,
    QTextBrowser, QToolButton, QWidget
)

from novelwriter import CONFIG, SHARED
from novelwriter.enum import nwItemType, nwDocAction, nwDocMode
from novelwriter.error import logException
from novelwriter.constants import nwUnicode
from novelwriter.core.tohtml import ToHtml
from novelwriter.extensions.wheeleventfilter import WheelEventFilter

if TYPE_CHECKING:  # pragma: no cover
    from novelwriter.guimain import GuiMain

logger = logging.getLogger(__name__)


class GuiDocViewer(QTextBrowser):

    loadDocumentTagRequest = pyqtSignal(str, Enum)

    def __init__(self, mainGui: GuiMain) -> None:
        super().__init__(parent=mainGui)

        logger.debug("Create: GuiDocViewer")

        # Class Variables
        self.mainGui = mainGui

        # Internal Variables
        self._docHandle = None

        # Settings
        self.setMinimumWidth(CONFIG.pxInt(300))
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

        # Install Event Filter for Mouse Wheel
        self.wheelEventFilter = WheelEventFilter(self)
        self.installEventFilter(self.wheelEventFilter)

        # Context Menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._openContextMenu)

        self.initViewer()

        logger.debug("Ready: GuiDocViewer")

        return

    ##
    #  Properties
    ##

    @property
    def docHandle(self) -> str | None:
        """Return the handle of the currently open document."""
        return self._docHandle

    @property
    def scrollPosition(self) -> int:
        """Return the scrollbar position."""
        vBar = self.verticalScrollBar()
        if vBar.isVisible():
            return vBar.value()
        return 0

    ##
    #  Methods
    ##

    def clearViewer(self) -> None:
        """Clear the content of the document and reset key variables."""
        self.clear()
        self.setSearchPaths([""])
        self._docHandle = None
        self.docHeader.setTitleFromHandle(self._docHandle)
        return

    def updateTheme(self) -> None:
        """Update theme elements."""
        self.docHeader.updateTheme()
        self.docFooter.updateTheme()
        return

    def initViewer(self) -> None:
        """Set editor settings from main config."""
        self._makeStyleSheet()

        # Set Font
        textFont = QFont()
        textFont.setFamily(CONFIG.textFont)
        textFont.setPointSize(CONFIG.textSize)
        self.setFont(textFont)

        # Set the widget colours to match syntax theme
        mainPalette = self.palette()
        mainPalette.setColor(QPalette.Window, QColor(*SHARED.theme.colBack))
        mainPalette.setColor(QPalette.Base, QColor(*SHARED.theme.colBack))
        mainPalette.setColor(QPalette.Text, QColor(*SHARED.theme.colText))
        self.setPalette(mainPalette)

        docPalette = self.viewport().palette()
        docPalette.setColor(QPalette.Base, QColor(*SHARED.theme.colBack))
        docPalette.setColor(QPalette.Text, QColor(*SHARED.theme.colText))
        self.viewport().setPalette(docPalette)

        self.docHeader.matchColours()
        self.docFooter.matchColours()

        # Set default text margins
        self.document().setDocumentMargin(0)
        theOpt = QTextOption()
        if CONFIG.doJustify:
            theOpt.setAlignment(Qt.AlignJustify)
        self.document().setDefaultTextOption(theOpt)

        # Scroll bars
        if CONFIG.hideVScroll:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        else:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        if CONFIG.hideHScroll:
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        else:
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Refresh the tab stops
        self.setTabStopDistance(CONFIG.getTabWidth())

        # If we have a document open, we should reload it in case the font changed
        if self._docHandle is not None:
            self.reloadText()

        return

    def loadText(self, tHandle: str, updateHistory: bool = True) -> bool:
        """Load text into the viewer from an item handle."""
        if not SHARED.project.tree.checkType(tHandle, nwItemType.FILE):
            logger.warning("Item not found")
            return False

        logger.debug("Generating preview for item '%s'", tHandle)
        qApp.setOverrideCursor(QCursor(Qt.WaitCursor))

        sPos = self.verticalScrollBar().value()
        aDoc = ToHtml(SHARED.project)
        aDoc.setPreview(CONFIG.viewComments, CONFIG.viewSynopsis)
        aDoc.setLinkHeaders(True)

        # Be extra careful here to prevent crashes when first opening a
        # project as a crash here leaves no way of recovering.
        # See issue #298
        try:
            aDoc.setText(tHandle)
            aDoc.doPreProcessing()
            aDoc.tokenizeText()
            aDoc.doConvert()
        except Exception:
            logger.error("Failed to generate preview for document with handle '%s'", tHandle)
            logException()
            self.setText(self.tr("An error occurred while generating the preview."))
            qApp.restoreOverrideCursor()
            return False

        # Refresh the tab stops
        self.setTabStopDistance(CONFIG.getTabWidth())

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
        SHARED.project.data.setLastHandle(tHandle, "viewer")
        self.docHeader.setTitleFromHandle(self._docHandle)
        self.updateDocMargins()

        # Make sure the main GUI knows we changed the content
        self.mainGui.viewMeta.refreshReferences(tHandle)

        # Since we change the content while it may still be rendering, we mark
        # the document dirty again to make sure it's re-rendered properly.
        self.redrawText()
        qApp.restoreOverrideCursor()

        return True

    def reloadText(self) -> None:
        """Reload the text in the current document."""
        if self._docHandle:
            self.loadText(self._docHandle, updateHistory=False)
        return

    def redrawText(self) -> None:
        """Redraw the text by marking the content as "dirty"."""
        self.document().markContentsDirty(0, self.document().characterCount())
        self.updateDocMargins()
        return

    def docAction(self, theAction: nwDocAction) -> bool:
        """Process document actions on the current document."""
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

    def navigateTo(self, tAnchor: str) -> bool:
        """Go to a specific #link in the document."""
        if not isinstance(tAnchor, str):
            return False
        if tAnchor.startswith("#"):
            logger.debug("Moving to anchor '%s'", tAnchor)
            self.setSource(QUrl(tAnchor))
        return True

    def clearNavHistory(self) -> None:
        """Clear the navigation history."""
        self.docHistory.clear()
        return

    def updateDocMargins(self) -> None:
        """Automatically adjust the margins so the text is centred."""
        wW = self.width()
        wH = self.height()
        cM = CONFIG.getTextMargin()

        vBar = self.verticalScrollBar()
        sW = vBar.width() if vBar.isVisible() else 0

        hBar = self.horizontalScrollBar()
        sH = hBar.height() if hBar.isVisible() else 0

        tM = cM
        if CONFIG.textWidth > 0:
            tW = CONFIG.getTextWidth()
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

    def setScrollPosition(self, pos: int) -> None:
        """Set the scrollbar position."""
        vBar = self.verticalScrollBar()
        if vBar.isVisible():
            vBar.setValue(pos)
        return

    ##
    #  Public Slots
    ##

    @pyqtSlot(str)
    def updateDocInfo(self, tHandle: str) -> None:
        """Update the header titlebar if needed."""
        if tHandle == self._docHandle:
            self.docHeader.setTitleFromHandle(self._docHandle)
            self.updateDocMargins()
        return

    ##
    #  Private Slots
    ##

    @pyqtSlot()
    def navBackward(self) -> None:
        """Navigate backwards in the document view history."""
        self.docHistory.backward()
        return

    @pyqtSlot()
    def navForward(self) -> None:
        """Navigate forwards in the document view history."""
        self.docHistory.forward()
        return

    @pyqtSlot("QUrl")
    def _linkClicked(self, url: QUrl) -> None:
        """Process a clicked link internally in the document."""
        theLink = url.url()
        logger.debug("Clicked link: '%s'", theLink)
        if len(theLink) > 0:
            theBits = theLink.split("=")
            if len(theBits) == 2:
                self.loadDocumentTagRequest.emit(theBits[1], nwDocMode.VIEW)
        return

    @pyqtSlot("QPoint")
    def _openContextMenu(self, point: QPoint) -> None:
        """Open context menu at location."""
        userCursor = self.textCursor()
        userSelection = userCursor.hasSelection()

        mnuContext = QMenu(self)

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
            lambda: self._makePosSelection(QTextCursor.WordUnderCursor, point)
        )
        mnuContext.addAction(mnuSelWord)

        mnuSelPara = QAction(self.tr("Select Paragraph"), mnuContext)
        mnuSelPara.triggered.connect(
            lambda: self._makePosSelection(QTextCursor.BlockUnderCursor, point)
        )
        mnuContext.addAction(mnuSelPara)

        # Open the context menu
        mnuContext.exec_(self.viewport().mapToGlobal(point))

        return

    ##
    #  Events
    ##

    def resizeEvent(self, event: QResizeEvent) -> None:
        """Update document margins when widget is resized."""
        self.updateDocMargins()
        super().resizeEvent(event)
        return

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Capture mouse click events on the document."""
        if event.button() == Qt.BackButton:
            self.navBackward()
        elif event.button() == Qt.ForwardButton:
            self.navForward()
        else:
            super().mouseReleaseEvent(event)
        return

    ##
    #  Internal Functions
    ##

    def _makeSelection(self, selType: QTextCursor.SelectionType) -> None:
        """Handle select of text based on a selection mode."""
        theCursor = self.textCursor()
        theCursor.clearSelection()
        theCursor.select(selType)

        if selType == QTextCursor.BlockUnderCursor:
            # This selection mode also selects the preceding paragraph
            # separator, which we want to avoid.
            posS = theCursor.selectionStart()
            posE = theCursor.selectionEnd()
            selTxt = theCursor.selectedText()
            if selTxt.startswith(nwUnicode.U_PSEP):
                theCursor.setPosition(posS+1, QTextCursor.MoveAnchor)
                theCursor.setPosition(posE, QTextCursor.KeepAnchor)

        self.setTextCursor(theCursor)

        return

    def _makePosSelection(self, selType: QTextCursor.SelectionType, pos: QPoint) -> None:
        """Handle text selection at a given location."""
        theCursor = self.cursorForPosition(pos)
        self.setTextCursor(theCursor)
        self._makeSelection(selType)
        return

    def _makeStyleSheet(self) -> None:
        """Generate an appropriate style sheet for the document viewer,
        based on the current syntax highlighter theme,
        """
        pTheme = SHARED.theme
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
            tColR=pTheme.colText[0],
            tColG=pTheme.colText[1],
            tColB=pTheme.colText[2],
            hColR=pTheme.colHead[0],
            hColG=pTheme.colHead[1],
            hColB=pTheme.colHead[2],
            aColR=pTheme.colVal[0],
            aColG=pTheme.colVal[1],
            aColB=pTheme.colVal[2],
            eColR=pTheme.colEmph[0],
            eColG=pTheme.colEmph[1],
            eColB=pTheme.colEmph[2],
            kColR=pTheme.colKey[0],
            kColG=pTheme.colKey[1],
            kColB=pTheme.colKey[2],
            cColR=pTheme.colHidden[0],
            cColG=pTheme.colHidden[1],
            cColB=pTheme.colHidden[2],
            mColR=pTheme.colMod[0],
            mColG=pTheme.colMod[1],
            mColB=pTheme.colMod[2],
        )
        self.document().setDefaultStyleSheet(styleSheet)

        return

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
            self._posHistory[self._prevPos] = self.docViewer.scrollPosition
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

        logger.debug("Create: GuiDocViewHeader")

        self.docViewer = docViewer
        self.mainGui   = docViewer.mainGui

        # Internal Variables
        self._docHandle = None

        fPx = int(0.9*SHARED.theme.fontPixelSize)
        hSp = CONFIG.pxInt(6)

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
        lblFont.setPointSizeF(0.9*SHARED.theme.fontPointSize)
        self.theTitle.setFont(lblFont)

        # Buttons
        self.backButton = QToolButton(self)
        self.backButton.setContentsMargins(0, 0, 0, 0)
        self.backButton.setIconSize(QSize(fPx, fPx))
        self.backButton.setFixedSize(fPx, fPx)
        self.backButton.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.backButton.setVisible(False)
        self.backButton.setToolTip(self.tr("Go Backward"))
        self.backButton.clicked.connect(self.docViewer.navBackward)

        self.forwardButton = QToolButton(self)
        self.forwardButton.setContentsMargins(0, 0, 0, 0)
        self.forwardButton.setIconSize(QSize(fPx, fPx))
        self.forwardButton.setFixedSize(fPx, fPx)
        self.forwardButton.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.forwardButton.setVisible(False)
        self.forwardButton.setToolTip(self.tr("Go Forward"))
        self.forwardButton.clicked.connect(self.docViewer.navForward)

        self.refreshButton = QToolButton(self)
        self.refreshButton.setContentsMargins(0, 0, 0, 0)
        self.refreshButton.setIconSize(QSize(fPx, fPx))
        self.refreshButton.setFixedSize(fPx, fPx)
        self.refreshButton.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.refreshButton.setVisible(False)
        self.refreshButton.setToolTip(self.tr("Reload"))
        self.refreshButton.clicked.connect(self._refreshDocument)

        self.closeButton = QToolButton(self)
        self.closeButton.setContentsMargins(0, 0, 0, 0)
        self.closeButton.setIconSize(QSize(fPx, fPx))
        self.closeButton.setFixedSize(fPx, fPx)
        self.closeButton.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.closeButton.setVisible(False)
        self.closeButton.setToolTip(self.tr("Close"))
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
        cM = CONFIG.pxInt(8)
        self.setContentsMargins(0, 0, 0, 0)
        self.outerBox.setContentsMargins(cM, cM, cM, cM)
        self.setMinimumHeight(fPx + 2*cM)

        # Fix the Colours
        self.updateTheme()

        logger.debug("Ready: GuiDocViewHeader")

        return

    ##
    #  Methods
    ##

    def updateTheme(self):
        """Update theme elements.
        """
        self.backButton.setIcon(SHARED.theme.getIcon("backward"))
        self.forwardButton.setIcon(SHARED.theme.getIcon("forward"))
        self.refreshButton.setIcon(SHARED.theme.getIcon("refresh"))
        self.closeButton.setIcon(SHARED.theme.getIcon("close"))

        buttonStyle = (
            "QToolButton {{border: none; background: transparent;}} "
            "QToolButton:hover {{border: none; background: rgba({0},{1},{2},0.2);}}"
        ).format(*SHARED.theme.colText)

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
        thePalette.setColor(QPalette.Window, QColor(*SHARED.theme.colBack))
        thePalette.setColor(QPalette.WindowText, QColor(*SHARED.theme.colText))
        thePalette.setColor(QPalette.Text, QColor(*SHARED.theme.colText))

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

        pTree = SHARED.project.tree
        if CONFIG.showFullPath:
            tTitle = []
            tTree = pTree.getItemPath(tHandle)
            for aHandle in reversed(tTree):
                nwItem = pTree[aHandle]
                if nwItem is not None:
                    tTitle.append(nwItem.itemName)
            sSep = "  %s  " % nwUnicode.U_RSAQUO
            self.theTitle.setText(sSep.join(tTitle))
        else:
            nwItem = pTree[tHandle]
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
        if self.docViewer.docHandle == self.mainGui.docEditor.docHandle:
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

        logger.debug("Create: GuiDocViewFooter")

        self.docViewer = docViewer
        self.mainGui   = docViewer.mainGui
        self.viewMeta  = docViewer.mainGui.viewMeta

        # Internal Variables
        self._docHandle = None

        fPx = int(0.9*SHARED.theme.fontPixelSize)
        bSp = CONFIG.pxInt(2)
        hSp = CONFIG.pxInt(8)

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
        self.showComments.setChecked(CONFIG.viewComments)
        self.showComments.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.showComments.setIconSize(QSize(fPx, fPx))
        self.showComments.setFixedSize(QSize(fPx, fPx))
        self.showComments.toggled.connect(self._doToggleComments)
        self.showComments.setToolTip(self.tr("Show comments"))

        # Show Synopsis
        self.showSynopsis = QToolButton(self)
        self.showSynopsis.setCheckable(True)
        self.showSynopsis.setChecked(CONFIG.viewSynopsis)
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
        lblFont.setPointSizeF(0.9*SHARED.theme.fontPointSize)
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
        cM = CONFIG.pxInt(8)
        self.setContentsMargins(0, 0, 0, 0)
        self.outerBox.setContentsMargins(cM, cM, cM, cM)
        self.setMinimumHeight(fPx + 2*cM)

        # Fix the Colours
        self.updateTheme()

        logger.debug("Ready: GuiDocViewFooter")

        return

    ##
    #  Methods
    ##

    def updateTheme(self) -> None:
        """Update theme elements."""
        # Icons
        fPx = int(0.9*SHARED.theme.fontPixelSize)
        stickyIcon = SHARED.theme.getToggleIcon("sticky", (fPx, fPx))
        bulletIcon = SHARED.theme.getToggleIcon("bullet", (fPx, fPx))

        self.showHide.setIcon(SHARED.theme.getIcon("reference"))
        self.stickyRefs.setIcon(stickyIcon)
        self.showComments.setIcon(bulletIcon)
        self.showSynopsis.setIcon(bulletIcon)

        # StyleSheets

        buttonStyle = (
            "QToolButton {{border: none; background: transparent;}} "
            "QToolButton:hover {{border: none; background: rgba({0},{1},{2},0.2);}}"
        ).format(*SHARED.theme.colText)

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
        thePalette.setColor(QPalette.Window, QColor(*SHARED.theme.colBack))
        thePalette.setColor(QPalette.WindowText, QColor(*SHARED.theme.colText))
        thePalette.setColor(QPalette.Text, QColor(*SHARED.theme.colText))

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
        if not theState and self.docViewer.docHandle is not None:
            self.viewMeta.refreshReferences(self.docViewer.docHandle)
        return

    @pyqtSlot(bool)
    def _doToggleComments(self, theState):
        """Toggle the view comment button and reload the document.
        """
        CONFIG.viewComments = theState
        self.docViewer.reloadText()
        return

    @pyqtSlot(bool)
    def _doToggleSynopsis(self, theState):
        """Toggle the view synopsis button and reload the document.
        """
        CONFIG.viewSynopsis = theState
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

        logger.debug("Create: GuiDocViewDetails")

        self.mainGui = mainGui

        self.refList = QLabel("")
        self.refList.setWordWrap(True)
        self.refList.setAlignment(Qt.AlignTop)
        self.refList.setScaledContents(True)
        self.refList.linkActivated.connect(self._linkClicked)

        self.linkStyle = "style='color: rgb({0},{1},{2})'".format(*SHARED.theme.colLink)

        # Assemble
        self.outerWidget = QWidget()
        self.outerBox = QHBoxLayout()
        self.outerBox.addWidget(self.refList, 1)

        self.outerWidget.setLayout(self.outerBox)
        self.setWidget(self.outerWidget)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setWidgetResizable(True)
        self.setMinimumHeight(CONFIG.pxInt(50))
        self.setFrameStyle(QFrame.NoFrame)

        logger.debug("Ready: GuiDocViewDetails")

        return

    def refreshReferences(self, tHandle):
        """Update the current list of document references from the
        project index.
        """
        if self.mainGui.docViewer.stickyRef:
            return

        theRefs = SHARED.project.index.getBackReferenceList(tHandle)
        theList = []
        for tHandle in theRefs:
            tItem = SHARED.project.tree[tHandle]
            if tItem is not None:
                theList.append("<a href='%s#%s' %s>%s</a>" % (
                    tHandle, theRefs[tHandle], self.linkStyle, tItem.itemName
                ))

        self.refList.setText(", ".join(theList))

        return

    ##
    #  Private Slots
    ##

    @pyqtSlot(str)
    def _linkClicked(self, theLink):
        """Capture the link-click and forward it to the document viewer
        class for handling.
        """
        logger.debug("Clicked link: '%s'", theLink)
        if len(theLink) >= 13:
            tHandle = theLink[:13]
            tAnchor = theLink[13:] or None
            self.mainGui.viewDocument(tHandle, tAnchor)
        return

# END Class GuiDocViewDetails
