"""
novelWriter – GUI Document Viewer
=================================

File History:
Created: 2019-05-10 [0.0.1] GuiDocViewer
Created: 2020-04-25 [0.4.5] GuiDocViewHeader
Created: 2020-06-09 [0.8]   GuiDocViewFooter
Created: 2020-09-08 [1.0b1] GuiDocViewHistory

This file is a part of novelWriter
Copyright 2018–2024, Veronica Berglyd Olsen

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

from PyQt5.QtCore import QPoint, Qt, QUrl, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QCursor, QMouseEvent, QPalette, QResizeEvent, QTextCursor
from PyQt5.QtWidgets import (
    QAction, QApplication, QFrame, QHBoxLayout, QMenu, QTextBrowser,
    QToolButton, QWidget
)

from novelwriter import CONFIG, SHARED
from novelwriter.constants import nwHeaders, nwUnicode
from novelwriter.core.toqdoc import TextDocumentTheme, ToQTextDocument
from novelwriter.enum import nwDocAction, nwDocMode, nwItemType
from novelwriter.error import logException
from novelwriter.extensions.configlayout import NColourLabel
from novelwriter.extensions.eventfilters import WheelEventFilter
from novelwriter.extensions.modified import NIconToolButton
from novelwriter.gui.theme import STYLES_MIN_TOOLBUTTON
from novelwriter.types import QtAlignCenterTop, QtKeepAnchor, QtMouseLeft, QtMoveAnchor

logger = logging.getLogger(__name__)


class GuiDocViewer(QTextBrowser):

    documentLoaded = pyqtSignal(str)
    loadDocumentTagRequest = pyqtSignal(str, Enum)
    closeDocumentRequest = pyqtSignal()
    reloadDocumentRequest = pyqtSignal()
    togglePanelVisibility = pyqtSignal()
    requestProjectItemSelected = pyqtSignal(str, bool)

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)

        logger.debug("Create: GuiDocViewer")

        # Internal Variables
        self._docHandle = None
        self._docTheme = TextDocumentTheme()

        # Settings
        self.setMinimumWidth(CONFIG.pxInt(300))
        self.setAutoFillBackground(True)
        self.setOpenExternalLinks(False)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFrameStyle(QFrame.Shape.NoFrame)

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
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._openContextMenu)

        # Function Mapping
        self.changeFocusState = self.docHeader.changeFocusState

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
        self.docHeader.clearHeader()
        return

    def updateTheme(self) -> None:
        """Update theme elements."""
        self.docHeader.updateTheme()
        self.docFooter.updateTheme()
        return

    def initViewer(self) -> None:
        """Set editor settings from main config."""
        # Set the font. See issues #1862 and #1875.
        self.setFont(CONFIG.textFont)
        self.docHeader.updateFont()
        self.docFooter.updateFont()

        # Set the widget colours to match syntax theme
        mainPalette = self.palette()
        mainPalette.setColor(QPalette.ColorRole.Window, SHARED.theme.colBack)
        mainPalette.setColor(QPalette.ColorRole.Base, SHARED.theme.colBack)
        mainPalette.setColor(QPalette.ColorRole.Text, SHARED.theme.colText)
        self.setPalette(mainPalette)

        docPalette = self.viewport().palette()
        docPalette.setColor(QPalette.ColorRole.Base, SHARED.theme.colBack)
        docPalette.setColor(QPalette.ColorRole.Text, SHARED.theme.colText)
        self.viewport().setPalette(docPalette)
        self.docHeader.matchColours()
        self.docFooter.matchColours()

        # Update theme colours
        self._docTheme.text      = SHARED.theme.colText
        self._docTheme.highlight = SHARED.theme.colMark
        self._docTheme.head      = SHARED.theme.colHead
        self._docTheme.comment   = SHARED.theme.colHidden
        self._docTheme.note      = SHARED.theme.colNote
        self._docTheme.code      = SHARED.theme.colCode
        self._docTheme.modifier  = SHARED.theme.colMod
        self._docTheme.keyword   = SHARED.theme.colKey
        self._docTheme.tag       = SHARED.theme.colTag
        self._docTheme.optional  = SHARED.theme.colOpt
        self._docTheme.dialog    = SHARED.theme.colDialN
        self._docTheme.altdialog = SHARED.theme.colDialA

        # Set default text margins
        self.document().setDocumentMargin(0)

        # Scroll bars
        if CONFIG.hideVScroll:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        else:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        if CONFIG.hideHScroll:
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        else:
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Refresh the tab stops
        self.setTabStopDistance(CONFIG.getTabWidth())

        # If we have a document open, we should reload it in case the font changed
        self.reloadText()

        return

    def loadText(self, tHandle: str, updateHistory: bool = True) -> bool:
        """Load text into the viewer from an item handle."""
        if not SHARED.project.tree.checkType(tHandle, nwItemType.FILE):
            logger.warning("Item not found")
            self.documentLoaded.emit("")
            return False

        logger.debug("Generating preview for item '%s'", tHandle)
        QApplication.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))

        sPos = self.verticalScrollBar().value()
        qDoc = ToQTextDocument(SHARED.project)
        qDoc.setJustify(CONFIG.doJustify)
        qDoc.setDialogueHighlight(True)
        qDoc.initDocument(CONFIG.textFont, self._docTheme)
        qDoc.setKeywords(True)
        qDoc.setComments(CONFIG.viewComments)
        qDoc.setSynopsis(CONFIG.viewSynopsis)

        # Be extra careful here to prevent crashes when first opening a
        # project as a crash here leaves no way of recovering.
        # See issue #298
        try:
            qDoc.setText(tHandle)
            qDoc.doPreProcessing()
            qDoc.tokenizeText()
            qDoc.doConvert()
            qDoc.appendFootnotes()
        except Exception:
            logger.error("Failed to generate preview for document with handle '%s'", tHandle)
            logException()
            self.setText(self.tr("An error occurred while generating the preview."))
            QApplication.restoreOverrideCursor()
            return False

        # Must be before setDocument
        if updateHistory:
            self.docHistory.append(tHandle)

        self.setDocumentTitle(tHandle)
        self.setDocument(qDoc.document)
        self.setTabStopDistance(CONFIG.getTabWidth())

        if self._docHandle == tHandle:
            # This is a refresh, so we set the scrollbar back to where it was
            self.verticalScrollBar().setValue(sPos)

        self._docHandle = tHandle
        SHARED.project.data.setLastHandle(tHandle, "viewer")
        self.docHeader.setHandle(tHandle)
        self.docHeader.setOutline({
            sTitle: (hItem.title, nwHeaders.H_LEVEL.get(hItem.level, 0))
            for sTitle, hItem in SHARED.project.index.iterItemHeadings(tHandle)
        })
        self.updateDocMargins()

        QApplication.restoreOverrideCursor()
        self.documentLoaded.emit(tHandle)

        return True

    def reloadText(self) -> None:
        """Reload the text in the current document."""
        if self._docHandle:
            self.loadText(self._docHandle, updateHistory=False)
        return

    def docAction(self, action: nwDocAction) -> bool:
        """Process document actions on the current document."""
        logger.debug("Requesting action: '%s'", action.name)
        if self._docHandle is None:
            logger.error("No document open")
            return False
        if action == nwDocAction.CUT:
            self.copy()
        elif action == nwDocAction.COPY:
            self.copy()
        elif action == nwDocAction.SEL_ALL:
            self._makeSelection(QTextCursor.SelectionType.Document)
        elif action == nwDocAction.SEL_PARA:
            self._makeSelection(QTextCursor.SelectionType.BlockUnderCursor)
        else:
            logger.debug("Unknown or unsupported document action '%s'", str(action))
            return False
        return True

    def anyFocus(self) -> bool:
        """Check if any widget or child widget has focus."""
        return self.hasFocus() or self.isAncestorOf(QApplication.focusWidget())

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
        """Update the header title bar if needed."""
        if tHandle and tHandle == self._docHandle:
            self.docHeader.setHandle(tHandle)
            self.updateDocMargins()
        return

    @pyqtSlot(str)
    def navigateTo(self, anchor: str) -> None:
        """Go to a specific #link in the document."""
        if isinstance(anchor, str) and anchor.startswith("#"):
            logger.debug("Moving to anchor '%s'", anchor)
            self.setSource(QUrl(anchor))
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
        """Process a clicked link in the document."""
        if link := url.url():
            logger.debug("Clicked link: '%s'", link)
            if (bits := link.partition("_")) and bits[0] == "#tag" and bits[2]:
                self.loadDocumentTagRequest.emit(bits[2], nwDocMode.VIEW)
            else:
                self.navigateTo(link)
        return

    @pyqtSlot("QPoint")
    def _openContextMenu(self, point: QPoint) -> None:
        """Open context menu at location."""
        userCursor = self.textCursor()
        userSelection = userCursor.hasSelection()

        ctxMenu = QMenu(self)

        if userSelection:
            mnuCopy = QAction(self.tr("Copy"), ctxMenu)
            mnuCopy.triggered.connect(lambda: self.docAction(nwDocAction.COPY))
            ctxMenu.addAction(mnuCopy)

            ctxMenu.addSeparator()

        mnuSelAll = QAction(self.tr("Select All"), ctxMenu)
        mnuSelAll.triggered.connect(lambda: self.docAction(nwDocAction.SEL_ALL))
        ctxMenu.addAction(mnuSelAll)

        mnuSelWord = QAction(self.tr("Select Word"), ctxMenu)
        mnuSelWord.triggered.connect(
            lambda: self._makePosSelection(QTextCursor.SelectionType.WordUnderCursor, point)
        )
        ctxMenu.addAction(mnuSelWord)

        mnuSelPara = QAction(self.tr("Select Paragraph"), ctxMenu)
        mnuSelPara.triggered.connect(
            lambda: self._makePosSelection(QTextCursor.SelectionType.BlockUnderCursor, point)
        )
        ctxMenu.addAction(mnuSelPara)

        # Open the context menu
        ctxMenu.exec(self.viewport().mapToGlobal(point))
        ctxMenu.deleteLater()

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
        if event.button() == Qt.MouseButton.BackButton:
            self.navBackward()
        elif event.button() == Qt.MouseButton.ForwardButton:
            self.navForward()
        else:
            super().mouseReleaseEvent(event)
        return

    ##
    #  Internal Functions
    ##

    def _makeSelection(self, selType: QTextCursor.SelectionType) -> None:
        """Handle selection of text based on a selection mode."""
        cursor = self.textCursor()
        cursor.clearSelection()
        cursor.select(selType)

        if selType == QTextCursor.SelectionType.BlockUnderCursor:
            # This selection mode also selects the preceding paragraph
            # separator, which we want to avoid.
            posS = cursor.selectionStart()
            posE = cursor.selectionEnd()
            selTxt = cursor.selectedText()
            if selTxt.startswith(nwUnicode.U_PSEP):
                cursor.setPosition(posS+1, QtMoveAnchor)
                cursor.setPosition(posE, QtKeepAnchor)

        self.setTextCursor(cursor)

        return

    def _makePosSelection(self, selType: QTextCursor.SelectionType, pos: QPoint) -> None:
        """Handle text selection at a given location."""
        self.setTextCursor(self.cursorForPosition(pos))
        self._makeSelection(selType)
        return


class GuiDocViewHistory:

    def __init__(self, docViewer: GuiDocViewer) -> None:
        self.docViewer = docViewer
        self._navHistory = []
        self._posHistory = []
        self._currPos = -1
        self._prevPos = -1
        return

    def clear(self) -> None:
        """Clear the view history."""
        logger.debug("View history cleared")
        self._navHistory = []
        self._posHistory = []
        self._currPos = -1
        self._prevPos = -1
        return

    def append(self, tHandle: str) -> bool:
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

    def forward(self) -> None:
        """Navigate to the next entry in the view history."""
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

    def backward(self) -> None:
        """Navigate to the previous entry in the view history."""
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

    def _updateScrollBar(self) -> None:
        """Update the scrollbar position of the previous entry."""
        if self._prevPos >= 0 and self._prevPos < len(self._posHistory):
            self._posHistory[self._prevPos] = self.docViewer.scrollPosition
        return

    def _updateNavButtons(self) -> None:
        """Update the navigation buttons in the document header."""
        self.docViewer.docHeader.updateNavButtons(0, len(self._navHistory) - 1, self._currPos)
        return

    def _truncateHistory(self, atPos: int) -> None:
        """Truncate the navigation history to the given position. Also
        enforces a maximum length of the navigation history to 20.
        """
        nSkip = 1 if atPos > 19 else 0
        self._navHistory = self._navHistory[nSkip:atPos + 1]
        self._posHistory = self._posHistory[nSkip:atPos + 1]
        self._currPos -= nSkip
        self._prevPos -= nSkip
        return

    def _dumpHistory(self) -> None:
        """Debug function to dump history to the logger. Since it is a
        for loop, it is skipped entirely if log level isn't DEBUG.
        """
        if CONFIG.isDebug:  # pragma: no cover
            for i, (h, p) in enumerate(zip(self._navHistory, self._posHistory)):
                logger.debug(
                    "History %02d: %s %13s [x:%d]" % (
                        i + 1, ">" if i == self._currPos else " ", h, p
                    )
                )
        return


class GuiDocViewHeader(QWidget):
    """The Embedded Document Header

    Only used by DocViewer, and is at a fixed position in the
    QTextBrowser's viewport.
    """

    def __init__(self, docViewer: GuiDocViewer) -> None:
        super().__init__(parent=docViewer)

        logger.debug("Create: GuiDocViewHeader")

        self.docViewer = docViewer

        # Internal Variables
        self._docHandle = None
        self._docOutline: dict[str, tuple[str, int]] = {}

        iPx = SHARED.theme.baseIconHeight
        iSz = SHARED.theme.baseIconSize
        mPx = CONFIG.pxInt(4)

        # Main Widget Settings
        self.setAutoFillBackground(True)

        # Title Label
        self.itemTitle = NColourLabel("", self, faded=SHARED.theme.fadedText)
        self.itemTitle.setMargin(0)
        self.itemTitle.setContentsMargins(0, 0, 0, 0)
        self.itemTitle.setAutoFillBackground(True)
        self.itemTitle.setAlignment(QtAlignCenterTop)
        self.itemTitle.setFixedHeight(iPx)

        # Other Widgets
        self.outlineMenu = QMenu(self)

        # Buttons
        self.outlineButton = NIconToolButton(self, iSz)
        self.outlineButton.setVisible(False)
        self.outlineButton.setToolTip(self.tr("Outline"))
        self.outlineButton.setMenu(self.outlineMenu)

        self.backButton = NIconToolButton(self, iSz)
        self.backButton.setVisible(False)
        self.backButton.setToolTip(self.tr("Go Backward"))
        self.backButton.clicked.connect(self.docViewer.navBackward)

        self.forwardButton = NIconToolButton(self, iSz)
        self.forwardButton.setVisible(False)
        self.forwardButton.setToolTip(self.tr("Go Forward"))
        self.forwardButton.clicked.connect(self.docViewer.navForward)

        self.refreshButton = NIconToolButton(self, iSz)
        self.refreshButton.setVisible(False)
        self.refreshButton.setToolTip(self.tr("Reload"))
        self.refreshButton.clicked.connect(self._refreshDocument)

        self.closeButton = NIconToolButton(self, iSz)
        self.closeButton.setVisible(False)
        self.closeButton.setToolTip(self.tr("Close"))
        self.closeButton.clicked.connect(self._closeDocument)

        # Assemble Layout
        self.outerBox = QHBoxLayout()
        self.outerBox.addWidget(self.outlineButton, 0)
        self.outerBox.addWidget(self.backButton, 0)
        self.outerBox.addWidget(self.forwardButton, 0)
        self.outerBox.addSpacing(mPx)
        self.outerBox.addWidget(self.itemTitle, 1)
        self.outerBox.addSpacing(mPx)
        self.outerBox.addSpacing(iPx)
        self.outerBox.addWidget(self.refreshButton, 0)
        self.outerBox.addWidget(self.closeButton, 0)
        self.outerBox.setSpacing(0)

        self.setLayout(self.outerBox)

        # Fix Margins and Size
        # This is needed for high DPI systems. See issue #499.
        self.setContentsMargins(0, 0, 0, 0)
        self.outerBox.setContentsMargins(mPx, mPx, mPx, mPx)
        self.setMinimumHeight(iPx + 2*mPx)

        self.updateFont()
        self.updateTheme()

        logger.debug("Ready: GuiDocViewHeader")

        return

    ##
    #  Methods
    ##

    def clearHeader(self) -> None:
        """Clear the header."""
        self._docHandle = None
        self._docOutline = {}

        self.itemTitle.setText("")
        self.outlineMenu.clear()
        self.outlineButton.setVisible(False)
        self.backButton.setVisible(False)
        self.forwardButton.setVisible(False)
        self.closeButton.setVisible(False)
        self.refreshButton.setVisible(False)
        return

    def setOutline(self, data: dict[str, tuple[str, int]]) -> None:
        """Set the document outline dataset."""
        tHandle = self._docHandle
        if data != self._docOutline and tHandle:
            self.outlineMenu.clear()
            entries = []
            minLevel = 5
            for title, (text, level) in data.items():
                if title != "T0000":
                    entries.append((title, text, level))
                    minLevel = min(minLevel, level)
            for title, text, level in entries[:30]:
                indent = "    "*(level - minLevel)
                action = self.outlineMenu.addAction(f"{indent}{text}")
                action.triggered.connect(
                    lambda _, title=title: self.docViewer.navigateTo(f"#{tHandle}:{title}")
                )
            self._docOutline = data
        return

    def updateFont(self) -> None:
        """Update the font settings."""
        self.setFont(SHARED.theme.guiFont)
        self.itemTitle.setFont(SHARED.theme.guiFontSmall)
        return

    def updateTheme(self) -> None:
        """Update theme elements."""
        self.outlineButton.setThemeIcon("list")
        self.backButton.setThemeIcon("backward")
        self.forwardButton.setThemeIcon("forward")
        self.refreshButton.setThemeIcon("refresh")
        self.closeButton.setThemeIcon("close")

        buttonStyle = SHARED.theme.getStyleSheet(STYLES_MIN_TOOLBUTTON)
        self.outlineButton.setStyleSheet(buttonStyle)
        self.backButton.setStyleSheet(buttonStyle)
        self.forwardButton.setStyleSheet(buttonStyle)
        self.refreshButton.setStyleSheet(buttonStyle)
        self.closeButton.setStyleSheet(buttonStyle)

        self.matchColours()

        return

    def matchColours(self) -> None:
        """Update the colours of the widget to match those of the syntax
        theme rather than the main GUI.
        """
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, SHARED.theme.colBack)
        palette.setColor(QPalette.ColorRole.WindowText, SHARED.theme.colText)
        palette.setColor(QPalette.ColorRole.Text, SHARED.theme.colText)
        self.setPalette(palette)
        self.itemTitle.setTextColors(
            color=palette.windowText().color(), faded=SHARED.theme.fadedText
        )
        return

    def changeFocusState(self, state: bool) -> None:
        """Toggle focus state."""
        self.itemTitle.setColorState(state)
        return

    def setHandle(self, tHandle: str) -> None:
        """Sets the document title from the handle, or alternatively,
        set the whole document path.
        """
        self._docHandle = tHandle

        if CONFIG.showFullPath:
            self.itemTitle.setText(f"  {nwUnicode.U_RSAQUO}  ".join(reversed(
                [name for name in SHARED.project.tree.getItemPath(tHandle, asName=True)]
            )))
        else:
            self.itemTitle.setText(i.itemName if (i := SHARED.project.tree[tHandle]) else "")

        self.backButton.setVisible(True)
        self.forwardButton.setVisible(True)
        self.outlineButton.setVisible(True)
        self.closeButton.setVisible(True)
        self.refreshButton.setVisible(True)

        return

    def updateNavButtons(self, firstIdx: int, lastIdx: int, currIdx: int) -> None:
        """Enable and disable nav buttons based on index in history."""
        self.backButton.setEnabled(currIdx > firstIdx)
        self.forwardButton.setEnabled(currIdx < lastIdx)
        return

    ##
    #  Private Slots
    ##

    @pyqtSlot()
    def _closeDocument(self) -> None:
        """Trigger the close editor/viewer on the main window."""
        self.clearHeader()
        self.docViewer.closeDocumentRequest.emit()
        return

    @pyqtSlot()
    def _refreshDocument(self) -> None:
        """Reload the content of the document."""
        self.docViewer.reloadDocumentRequest.emit()
        return

    ##
    #  Events
    ##

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Capture a click on the title and ensure that the item is
        selected in the project tree.
        """
        if event.button() == QtMouseLeft:
            self.docViewer.requestProjectItemSelected.emit(self._docHandle, True)
        return


class GuiDocViewFooter(QWidget):
    """The Embedded Document Footer

    Only used by DocViewer, and is at a fixed position in the
    QTextBrowser's viewport.
    """

    def __init__(self, docViewer: GuiDocViewer) -> None:
        super().__init__(parent=docViewer)

        logger.debug("Create: GuiDocViewFooter")

        self.docViewer = docViewer

        # Internal Variables
        self._docHandle = None

        iPx = SHARED.theme.baseIconHeight
        iSz = SHARED.theme.baseIconSize
        hSp = CONFIG.pxInt(4)
        mPx = CONFIG.pxInt(4)

        # Main Widget Settings
        self.setContentsMargins(0, 0, 0, 0)
        self.setAutoFillBackground(True)

        # Show/Hide Details
        self.showHide = NIconToolButton(self, iSz)
        self.showHide.clicked.connect(lambda: self.docViewer.togglePanelVisibility.emit())
        self.showHide.setToolTip(self.tr("Show/Hide Viewer Panel"))

        # Show Comments
        self.showComments = QToolButton(self)
        self.showComments.setText(self.tr("Comments"))
        self.showComments.setCheckable(True)
        self.showComments.setChecked(CONFIG.viewComments)
        self.showComments.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.showComments.setIconSize(iSz)
        self.showComments.toggled.connect(self._doToggleComments)
        self.showComments.setToolTip(self.tr("Show Comments"))

        # Show Synopsis
        self.showSynopsis = QToolButton(self)
        self.showSynopsis.setText(self.tr("Synopsis"))
        self.showSynopsis.setCheckable(True)
        self.showSynopsis.setChecked(CONFIG.viewSynopsis)
        self.showSynopsis.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.showSynopsis.setIconSize(iSz)
        self.showSynopsis.toggled.connect(self._doToggleSynopsis)
        self.showSynopsis.setToolTip(self.tr("Show Synopsis Comments"))

        # Assemble Layout
        self.outerBox = QHBoxLayout()
        self.outerBox.addWidget(self.showHide, 0)
        self.outerBox.addStretch(1)
        self.outerBox.addWidget(self.showComments, 0)
        self.outerBox.addWidget(self.showSynopsis, 0)
        self.outerBox.setSpacing(hSp)
        self.setLayout(self.outerBox)

        # Fix Margins and Size
        # This is needed for high DPI systems. See issue #499.
        self.setContentsMargins(0, 0, 0, 0)
        self.outerBox.setContentsMargins(mPx, mPx, mPx, mPx)
        self.setMinimumHeight(iPx + 2*mPx)

        self.updateFont()
        self.updateTheme()

        logger.debug("Ready: GuiDocViewFooter")

        return

    ##
    #  Methods
    ##

    def updateFont(self) -> None:
        """Update the font settings."""
        self.setFont(SHARED.theme.guiFont)
        self.showComments.setFont(SHARED.theme.guiFontSmall)
        self.showSynopsis.setFont(SHARED.theme.guiFontSmall)
        return

    def updateTheme(self) -> None:
        """Update theme elements."""
        # Icons
        fPx = int(0.9*SHARED.theme.fontPixelSize)
        bulletIcon = SHARED.theme.getToggleIcon("bullet", (fPx, fPx))

        self.showHide.setThemeIcon("panel")
        self.showComments.setIcon(bulletIcon)
        self.showSynopsis.setIcon(bulletIcon)

        buttonStyle = SHARED.theme.getStyleSheet(STYLES_MIN_TOOLBUTTON)
        self.showHide.setStyleSheet(buttonStyle)
        self.showComments.setStyleSheet(buttonStyle)
        self.showSynopsis.setStyleSheet(buttonStyle)

        self.matchColours()

        return

    def matchColours(self) -> None:
        """Update the colours of the widget to match those of the syntax
        theme rather than the main GUI.
        """
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, SHARED.theme.colBack)
        palette.setColor(QPalette.ColorRole.WindowText, SHARED.theme.colText)
        palette.setColor(QPalette.ColorRole.Text, SHARED.theme.colText)
        self.setPalette(palette)
        return

    ##
    #  Private Slots
    ##

    @pyqtSlot(bool)
    def _doToggleComments(self, state: bool) -> None:
        """Toggle the view comment button and reload the document."""
        CONFIG.viewComments = state
        self.docViewer.reloadText()
        return

    @pyqtSlot(bool)
    def _doToggleSynopsis(self, state: bool) -> None:
        """Toggle the view synopsis button and reload the document."""
        CONFIG.viewSynopsis = state
        self.docViewer.reloadText()
        return
