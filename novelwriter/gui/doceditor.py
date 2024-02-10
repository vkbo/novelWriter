"""
novelWriter – GUI Document Editor
=================================

File History:
Created:   2018-09-29 [0.0.1] GuiDocEditor
Created:   2019-04-22 [0.0.1] BackgroundWordCounter
Created:   2019-09-29 [0.2.1] GuiDocEditSearch
Created:   2020-04-25 [0.4.5] GuiDocEditHeader
Rewritten: 2020-06-15 [0.9]   GuiDocEditSearch
Created:   2020-06-27 [0.10]  GuiDocEditFooter
Rewritten: 2020-10-07 [1.0b3] BackgroundWordCounter
Created:   2023-11-06 [2.2b1] MetaCompleter
Created:   2023-11-07 [2.2b1] GuiDocToolBar

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

import bisect
import logging

from enum import Enum
from time import time
from typing import TYPE_CHECKING

from PyQt5.QtCore import (
    pyqtSignal, pyqtSlot, QObject, QPoint, QRegExp, QRegularExpression,
    QRunnable, QSize, Qt, QTimer
)
from PyQt5.QtGui import (
    QColor, QCursor, QFont, QKeyEvent, QKeySequence, QMouseEvent, QPalette,
    QPixmap, QResizeEvent, QTextBlock, QTextCursor, QTextDocument, QTextOption
)
from PyQt5.QtWidgets import (
    QAction, QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QMenu,
    QPlainTextEdit, QPushButton, QShortcut, QToolBar, QToolButton, QVBoxLayout,
    QWidget, qApp
)

from novelwriter import CONFIG, SHARED
from novelwriter.enum import nwDocAction, nwDocInsert, nwDocMode, nwItemClass, nwTrinary
from novelwriter.common import minmax, transferCase
from novelwriter.constants import nwKeyWords, nwLabels, nwShortcode, nwUnicode, trConst
from novelwriter.core.index import countWords
from novelwriter.tools.lipsum import GuiLipsum
from novelwriter.core.document import NWDocument
from novelwriter.gui.dochighlight import GuiDocHighlighter
from novelwriter.gui.editordocument import GuiTextDocument
from novelwriter.extensions.eventfilters import WheelEventFilter

if TYPE_CHECKING:  # pragma: no cover
    from novelwriter.guimain import GuiMain

logger = logging.getLogger(__name__)


class _SelectAction(Enum):

    NO_DECISION    = 0
    KEEP_SELECTION = 1
    KEEP_POSITION  = 2
    MOVE_AFTER     = 3

# END Class _SelectAction


class GuiDocEditor(QPlainTextEdit):
    """Gui Widget: Main Document Editor"""

    MOVE_KEYS = (
        Qt.Key.Key_Left, Qt.Key.Key_Right, Qt.Key.Key_Up, Qt.Key.Key_Down,
        Qt.Key.Key_PageUp, Qt.Key.Key_PageDown
    )

    # Custom Signals
    statusMessage = pyqtSignal(str)
    docCountsChanged = pyqtSignal(str, int, int, int)
    editedStatusChanged = pyqtSignal(bool)
    loadDocumentTagRequest = pyqtSignal(str, Enum)
    novelStructureChanged = pyqtSignal()
    novelItemMetaChanged = pyqtSignal(str)
    spellCheckStateChanged = pyqtSignal(bool)
    closeDocumentRequest = pyqtSignal()
    toggleFocusModeRequest = pyqtSignal()
    requestProjectItemSelected = pyqtSignal(str, bool)
    requestProjectItemRenamed = pyqtSignal(str, str)

    def __init__(self, mainGui: GuiMain) -> None:
        super().__init__(parent=mainGui)

        logger.debug("Create: GuiDocEditor")

        # Class Variables
        self.mainGui = mainGui

        self._nwDocument = None
        self._nwItem     = None

        self._docChanged = False  # Flag for changed status of document
        self._docHandle  = None   # The handle of the open document
        self._vpMargin   = 0      # The editor viewport margin, set during init

        # Document Variables
        self._lastEdit   = 0.0    # Timestamp of last edit
        self._lastActive = 0.0    # Timestamp of last activity
        self._lastFind   = None   # Position of the last found search word
        self._doReplace  = False  # Switch to temporarily disable auto-replace

        # Typography Cache
        self._typPadChar = " "
        self._typDQuoteO = '"'
        self._typDQuoteC = '"'
        self._typSQuoteO = "'"
        self._typSQuoteC = "'"
        self._typRepDQuote = False
        self._typRepSQuote = False
        self._typRepDash = False
        self._typRepDots = False
        self._typPadBefore = ""
        self._typPadAfter = ""

        # Completer
        self._completer = MetaCompleter(self)
        self._completer.complete.connect(self._insertCompletion)

        # Create Custom Document
        self._qDocument = GuiTextDocument(self)
        self.setDocument(self._qDocument)

        # Connect Signals
        self._qDocument.contentsChange.connect(self._docChange)
        self.selectionChanged.connect(self._updateSelectedStatus)
        self.spellCheckStateChanged.connect(self._qDocument.setSpellCheckState)

        # Document Title
        self.docHeader = GuiDocEditHeader(self)
        self.docFooter = GuiDocEditFooter(self)
        self.docSearch = GuiDocEditSearch(self)
        self.docToolBar = GuiDocToolBar(self)

        # Connect Signals
        self.docHeader.closeDocumentRequest.connect(self._closeCurrentDocument)
        self.docHeader.toggleToolBarRequest.connect(self._toggleToolBarVisibility)
        self.docToolBar.requestDocAction.connect(self.docAction)

        # Context Menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._openContextMenu)

        # Editor Settings
        self.setMinimumWidth(CONFIG.pxInt(300))
        self.setAutoFillBackground(True)
        self.setFrameStyle(QFrame.Shape.NoFrame)

        # Custom Shortcuts
        self.keyContext = QShortcut(self)
        self.keyContext.setKey("Ctrl+.")
        self.keyContext.setContext(Qt.ShortcutContext.WidgetShortcut)
        self.keyContext.activated.connect(self._openContextFromCursor)

        self.followTag1 = QShortcut(self)
        self.followTag1.setKey(Qt.Key.Key_Return | Qt.KeyboardModifier.ControlModifier)
        self.followTag1.setContext(Qt.ShortcutContext.WidgetShortcut)
        self.followTag1.activated.connect(self._processTag)

        self.followTag2 = QShortcut(self)
        self.followTag2.setKey(Qt.Key.Key_Enter | Qt.KeyboardModifier.ControlModifier)
        self.followTag2.setContext(Qt.ShortcutContext.WidgetShortcut)
        self.followTag2.activated.connect(self._processTag)

        # Set Up Document Word Counter
        self.wcTimerDoc = QTimer()
        self.wcTimerDoc.timeout.connect(self._runDocCounter)
        self.wcTimerDoc.setInterval(5000)

        self.wCounterDoc = BackgroundWordCounter(self)
        self.wCounterDoc.setAutoDelete(False)
        self.wCounterDoc.signals.countsReady.connect(self._updateDocCounts)

        # Set Up Selection Word Counter
        self.wcTimerSel = QTimer()
        self.wcTimerSel.timeout.connect(self._runSelCounter)
        self.wcTimerSel.setInterval(500)

        self.wCounterSel = BackgroundWordCounter(self, forSelection=True)
        self.wCounterSel.setAutoDelete(False)
        self.wCounterSel.signals.countsReady.connect(self._updateSelCounts)

        # Install Event Filter for Mouse Wheel
        self.wheelEventFilter = WheelEventFilter(self)
        self.installEventFilter(self.wheelEventFilter)

        # Finalise
        self.updateSyntaxColours()
        self.initEditor()

        logger.debug("Ready: GuiDocEditor")

        return

    ##
    #  Properties
    ##

    @property
    def docChanged(self) -> bool:
        """Return the changed status of the document."""
        return self._docChanged

    @property
    def docHandle(self) -> str | None:
        """Return the handle of the currently open document."""
        return self._docHandle

    @property
    def lastActive(self) -> float:
        """Return the last active timestamp for the user."""
        return self._lastActive

    @property
    def isEmpty(self) -> bool:
        """Check if the current document is empty."""
        return self._qDocument.isEmpty()

    ##
    #  Methods
    ##

    def clearEditor(self) -> None:
        """Clear the current document and reset all document-related
        flags and counters.
        """
        self._nwDocument = None
        self.setReadOnly(True)
        self.clear()
        self.wcTimerDoc.stop()
        self.wcTimerSel.stop()

        self._docHandle  = None
        self._lastEdit   = 0.0
        self._lastActive = 0.0
        self._lastFind   = None
        self._doReplace  = False

        self.setDocumentChanged(False)
        self.docHeader.setTitleFromHandle(self._docHandle)
        self.docFooter.setHandle(self._docHandle)
        self.docToolBar.setVisible(False)

        return

    def updateTheme(self) -> None:
        """Update theme elements."""
        self.docSearch.updateTheme()
        self.docHeader.updateTheme()
        self.docFooter.updateTheme()
        self.docToolBar.updateTheme()
        return

    def updateSyntaxColours(self) -> None:
        """Update the syntax highlighting theme."""
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

        self._qDocument.syntaxHighlighter.initHighlighter()

        return

    def initEditor(self) -> None:
        """Initialise or re-initialise the editor with the user's
        settings. This function is both called when the editor is
        created, and when the user changes the main editor preferences.
        """
        # Typography
        if CONFIG.fmtPadThin:
            self._typPadChar = nwUnicode.U_THNBSP
        else:
            self._typPadChar = nwUnicode.U_NBSP

        self._typSQuoteO = CONFIG.fmtSQuoteOpen
        self._typSQuoteC = CONFIG.fmtSQuoteClose
        self._typDQuoteO = CONFIG.fmtDQuoteOpen
        self._typDQuoteC = CONFIG.fmtDQuoteClose
        self._typRepDQuote = CONFIG.doReplaceDQuote
        self._typRepSQuote = CONFIG.doReplaceSQuote
        self._typRepDash = CONFIG.doReplaceDash
        self._typRepDots = CONFIG.doReplaceDots
        self._typPadBefore = CONFIG.fmtPadBefore
        self._typPadAfter = CONFIG.fmtPadAfter

        # Reload spell check and dictionaries
        SHARED.updateSpellCheckLanguage()

        # Set font
        font = QFont()
        font.setFamily(CONFIG.textFont)
        font.setPointSize(CONFIG.textSize)
        self.setFont(font)

        # Set default text margins
        # Due to cursor visibility, a part of the margin must be
        # allocated to the document itself. See issue #1112.
        self._qDocument.setDocumentMargin(4)
        self._vpMargin = max(CONFIG.getTextMargin() - 4, 0)
        self.setViewportMargins(self._vpMargin, self._vpMargin, self._vpMargin, self._vpMargin)

        # Also set the document text options for the document text flow
        options = QTextOption()

        if CONFIG.doJustify:
            options.setAlignment(Qt.AlignmentFlag.AlignJustify)
        if CONFIG.showTabsNSpaces:
            options.setFlags(options.flags() | QTextOption.Flag.ShowTabsAndSpaces)
        if CONFIG.showLineEndings:
            options.setFlags(options.flags() | QTextOption.Flag.ShowLineAndParagraphSeparators)

        self._qDocument.setDefaultTextOption(options)

        # Scrolling
        self.setCenterOnScroll(CONFIG.scrollPastEnd)
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

        # If we have a document open, we should refresh it in case the
        # font changed, otherwise we just clear the editor entirely,
        # which makes it read only.
        if self._docHandle:
            self._qDocument.syntaxHighlighter.rehighlight()
            self.docHeader.setTitleFromHandle(self._docHandle)
        else:
            self.clearEditor()

        return

    def loadText(self, tHandle: str, tLine=None) -> bool:
        """Load text from a document into the editor. If we have an I/O
        error, we must handle this and clear the editor so that we don't
        risk overwriting the file if it exists. This can for instance
        happen of the file contains binary elements or an encoding that
        novelWriter does not support. If loading is successful, or the
        document is new (empty string), we set up the editor for editing
        the file.
        """
        self._nwDocument = SHARED.project.storage.getDocument(tHandle)
        self._nwItem = self._nwDocument.nwItem

        docText = self._nwDocument.readDocument()
        if docText is None:
            # There was an I/O error
            self.clearEditor()
            return False

        qApp.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))
        self._docHandle = tHandle

        self._allowAutoReplace(False)
        self._qDocument.setTextContent(docText, tHandle)
        self._allowAutoReplace(True)
        qApp.processEvents()

        self._lastEdit = time()
        self._lastActive = time()
        self._runDocCounter()
        self.wcTimerDoc.start()

        self.setReadOnly(False)
        self.docHeader.setTitleFromHandle(self._docHandle)
        self.docFooter.setHandle(self._docHandle)
        self.updateDocMargins()

        if tLine is None and self._nwItem is not None:
            self.setCursorPosition(self._nwItem.cursorPos)
        elif isinstance(tLine, int):
            self.setCursorLine(tLine)

        self.docFooter.updateLineCount()

        # This is a hack to fix invisible cursor on an empty document
        if self._qDocument.characterCount() <= 1:
            self.setPlainText("\n")
            self.setPlainText("")
            self.setCursorPosition(0)

        qApp.processEvents()
        self.setDocumentChanged(False)
        self._qDocument.clearUndoRedoStacks()
        self.docToolBar.setVisible(CONFIG.showEditToolBar)

        qApp.restoreOverrideCursor()

        # Update the status bar
        if self._nwItem is not None:
            self.statusMessage.emit(self.tr("Opened Document: {0}").format(self._nwItem.itemName))

        return True

    def updateTagHighLighting(self) -> None:
        """Rerun the syntax highlighter on all meta data lines."""
        self._qDocument.syntaxHighlighter.rehighlightByType(GuiDocHighlighter.BLOCK_META)
        return

    def replaceText(self, text: str) -> None:
        """Replace the text of the current document with the provided
        text. This also clears undo history.
        """
        qApp.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))
        self.setPlainText(text)
        self.updateDocMargins()
        self.setDocumentChanged(True)
        qApp.restoreOverrideCursor()
        return

    def saveText(self) -> bool:
        """Save the text currently in the editor to the NWDocument
        object, and update the NWItem meta data.
        """
        if self._nwItem is None or self._nwDocument is None:
            logger.error("Cannot save text as no document is open")
            return False

        tHandle = self._nwItem.itemHandle
        if self._docHandle != tHandle:
            logger.error(
                "Editor handle '%s' and item handle '%s' do not match", self._docHandle, tHandle
            )
            return False

        docText = self.getText()
        cC, wC, pC = countWords(docText)
        self._updateDocCounts(cC, wC, pC)

        self.saveCursorPosition()
        if not self._nwDocument.writeDocument(docText):
            saveOk = False
            if self._nwDocument.hashError:
                msgYes = SHARED.question(self.tr(
                    "This document has been changed outside of novelWriter "
                    "while it was open. Overwrite the file on disk?"
                ))
                if msgYes:
                    saveOk = self._nwDocument.writeDocument(docText, forceWrite=True)

            if not saveOk:
                SHARED.error(
                    self.tr("Could not save document."),
                    info=self._nwDocument.getError()
                )

            return False

        self.setDocumentChanged(False)

        oldHeader = self._nwItem.mainHeading
        oldCount = SHARED.project.index.getHandleHeaderCount(tHandle)
        SHARED.project.index.scanText(tHandle, docText)
        newHeader = self._nwItem.mainHeading
        newCount = SHARED.project.index.getHandleHeaderCount(tHandle)

        if self._nwItem.itemClass == nwItemClass.NOVEL:
            if oldCount == newCount:
                self.novelItemMetaChanged.emit(tHandle)
            else:
                self.novelStructureChanged.emit()

        if oldHeader != newHeader:
            self.docFooter.updateInfo()

        # Update the status bar
        self.statusMessage.emit(self.tr("Saved Document: {0}").format(self._nwItem.itemName))

        return True

    def cursorIsVisible(self) -> bool:
        """Check if the cursor is visible in the editor."""
        return (
            0 < self.cursorRect().top()
            and self.cursorRect().bottom() < self.viewport().height()
        )

    def ensureCursorVisibleNoCentre(self) -> None:
        """Ensure cursor is visible, but don't force it to centre."""
        cT = self.cursorRect().top()
        cB = self.cursorRect().bottom()
        vH = self.viewport().height()
        if cT < 0:
            count = 0
            vBar = self.verticalScrollBar()
            while self.cursorRect().top() < 0 and count < 100000:
                vBar.setValue(vBar.value() - 1)
                count += 1
        elif cB > vH:
            count = 0
            vBar = self.verticalScrollBar()
            while self.cursorRect().bottom() > vH and count < 100000:
                vBar.setValue(vBar.value() + 1)
                count += 1
        qApp.processEvents()
        return

    def updateDocMargins(self) -> None:
        """Automatically adjust the margins so the text is centred if
        we have a text width set or we're in Focus Mode. Otherwise, just
        ensure the margins are set correctly.
        """
        wW = self.width()
        wH = self.height()

        vBar = self.verticalScrollBar()
        sW = vBar.width() if vBar.isVisible() else 0

        hBar = self.horizontalScrollBar()
        sH = hBar.height() if hBar.isVisible() else 0

        tM = self._vpMargin
        if CONFIG.textWidth > 0 or self.mainGui.isFocusMode:
            tW = CONFIG.getTextWidth(self.mainGui.isFocusMode)
            tM = max((wW - sW - tW)//2, self._vpMargin)

        tB = self.frameWidth()
        tW = wW - 2*tB - sW
        tH = self.docHeader.height()
        fH = self.docFooter.height()
        fY = wH - fH - tB - sH
        self.docHeader.setGeometry(tB, tB, tW, tH)
        self.docFooter.setGeometry(tB, fY, tW, fH)
        self.docToolBar.move(0, tH)

        rH = 0
        if self.docSearch.isVisible():
            rH = self.docSearch.height()
            rW = self.docSearch.width()
            rL = wW - sW - rW - 2*tB
            self.docSearch.move(rL, 2*tB)

        uM = max(self._vpMargin, tH, rH)
        lM = max(self._vpMargin, fH)
        self.setViewportMargins(tM, uM, tM, lM)

        return

    ##
    #  Getters
    ##

    def getText(self) -> str:
        """Get the text content of the current document. This method uses
        QTextDocument->toRawText instead of toPlainText. The former preserves
        non-breaking spaces, the latter does not. We still want to get rid of
        paragraph and line separators though.
        See: https://doc.qt.io/qt-5/qtextdocument.html#toPlainText
        """
        text = self._qDocument.toRawText()
        text = text.replace(nwUnicode.U_LSEP, "\n")  # Line separators
        text = text.replace(nwUnicode.U_PSEP, "\n")  # Paragraph separators
        return text

    def getCursorPosition(self) -> int:
        """Find the cursor position in the document. If the editor has a
        selection, return the position of the end of the selection.
        """
        return self.textCursor().selectionEnd()

    ##
    #  Setters
    ##

    def setDocumentChanged(self, state: bool) -> bool:
        """Keep track of the document changed variable, and emit the
        document change signal.
        """
        self._docChanged = state
        self.editedStatusChanged.emit(self._docChanged)
        return self._docChanged

    def setCursorPosition(self, position: int) -> None:
        """Move the cursor to a given position in the document."""
        nChars = self._qDocument.characterCount()
        if nChars > 1 and isinstance(position, int):
            cursor = self.textCursor()
            cursor.setPosition(minmax(position, 0, nChars-1))
            self.setTextCursor(cursor)
            self.centerCursor()
            self.docFooter.updateLineCount()
        return

    def saveCursorPosition(self) -> None:
        """Save the cursor position to the current project item."""
        if self._nwItem is not None:
            cursPos = self.getCursorPosition()
            self._nwItem.setCursorPos(cursPos)
        return

    def setCursorLine(self, line: int | None) -> None:
        """Move the cursor to a given line in the document."""
        if isinstance(line, int) and line > 0:
            block = self._qDocument.findBlockByNumber(line - 1)
            if block:
                self.setCursorPosition(block.position())
                logger.debug("Cursor moved to line %d", line)
        return

    ##
    #  Spell Checking
    ##

    def toggleSpellCheck(self, state: bool | None) -> None:
        """This is the main spell check setting function, and this one
        should call all other setSpellCheck functions in other classes.
        If the spell check state is not defined (None), then toggle the
        current status saved in this class.
        """
        if state is None:
            state = not SHARED.project.data.spellCheck

        if SHARED.spelling.spellLanguage is None:
            state = False

        if state and not CONFIG.hasEnchant:
            SHARED.info(self.tr(
                "Spell checking requires the package PyEnchant. "
                "It does not appear to be installed."
            ))
            state = False

        SHARED.project.data.setSpellCheck(state)
        self.spellCheckStateChanged.emit(state)
        self.spellCheckDocument()

        logger.debug("Spell check is set to '%s'", str(state))

        return

    def spellCheckDocument(self) -> None:
        """Rerun the highlighter to update spell checking status of the
        currently loaded text. The fastest way to do this, at least as
        of Qt 5.13, is to clear the text and put it back. This clears
        the undo stack, so we only do it for big documents.
        """
        logger.debug("Running spell checker")
        start = time()
        qApp.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))
        self._qDocument.syntaxHighlighter.rehighlight()
        qApp.restoreOverrideCursor()
        logger.debug("Document highlighted in %.3f ms", 1000*(time() - start))
        self.statusMessage.emit(self.tr("Spell check complete"))
        return

    ##
    #  General Class Methods
    ##

    def docAction(self, action: nwDocAction) -> bool:
        """Perform an action on the current document based on an action
        flag. This is just a single entry point wrapper function to
        ensure all the feature functions get the correct information
        passed to it without having to consider the internal logic of
        this class when calling these actions from other classes.
        """
        if self._docHandle is None:
            logger.error("No document open")
            return False

        if not isinstance(action, nwDocAction):
            logger.error("Not a document action")
            return False

        logger.debug("Requesting action: %s", action.name)

        self._allowAutoReplace(False)
        if action == nwDocAction.UNDO:
            self.undo()
        elif action == nwDocAction.REDO:
            self.redo()
        elif action == nwDocAction.CUT:
            self.cut()
        elif action == nwDocAction.COPY:
            self.copy()
        elif action == nwDocAction.PASTE:
            self.paste()
        elif action == nwDocAction.MD_ITALIC:
            self._toggleFormat(1, "_")
        elif action == nwDocAction.MD_BOLD:
            self._toggleFormat(2, "*")
        elif action == nwDocAction.MD_STRIKE:
            self._toggleFormat(2, "~")
        elif action == nwDocAction.S_QUOTE:
            self._wrapSelection(self._typSQuoteO, self._typSQuoteC)
        elif action == nwDocAction.D_QUOTE:
            self._wrapSelection(self._typDQuoteO, self._typDQuoteC)
        elif action == nwDocAction.SEL_ALL:
            self._makeSelection(QTextCursor.SelectionType.Document)
        elif action == nwDocAction.SEL_PARA:
            self._makeSelection(QTextCursor.SelectionType.BlockUnderCursor)
        elif action == nwDocAction.BLOCK_H1:
            self._formatBlock(nwDocAction.BLOCK_H1)
        elif action == nwDocAction.BLOCK_H2:
            self._formatBlock(nwDocAction.BLOCK_H2)
        elif action == nwDocAction.BLOCK_H3:
            self._formatBlock(nwDocAction.BLOCK_H3)
        elif action == nwDocAction.BLOCK_H4:
            self._formatBlock(nwDocAction.BLOCK_H4)
        elif action == nwDocAction.BLOCK_COM:
            self._iterFormatBlocks(nwDocAction.BLOCK_COM)
        elif action == nwDocAction.BLOCK_IGN:
            self._iterFormatBlocks(nwDocAction.BLOCK_IGN)
        elif action == nwDocAction.BLOCK_TXT:
            self._iterFormatBlocks(nwDocAction.BLOCK_TXT)
        elif action == nwDocAction.BLOCK_TTL:
            self._formatBlock(nwDocAction.BLOCK_TTL)
        elif action == nwDocAction.BLOCK_UNN:
            self._formatBlock(nwDocAction.BLOCK_UNN)
        elif action == nwDocAction.REPL_SNG:
            self._replaceQuotes("'", self._typSQuoteO, self._typSQuoteC)
        elif action == nwDocAction.REPL_DBL:
            self._replaceQuotes("\"", self._typDQuoteO, self._typDQuoteC)
        elif action == nwDocAction.RM_BREAKS:
            self._removeInParLineBreaks()
        elif action == nwDocAction.ALIGN_L:
            self._formatBlock(nwDocAction.ALIGN_L)
        elif action == nwDocAction.ALIGN_C:
            self._formatBlock(nwDocAction.ALIGN_C)
        elif action == nwDocAction.ALIGN_R:
            self._formatBlock(nwDocAction.ALIGN_R)
        elif action == nwDocAction.INDENT_L:
            self._formatBlock(nwDocAction.INDENT_L)
        elif action == nwDocAction.INDENT_R:
            self._formatBlock(nwDocAction.INDENT_R)
        elif action == nwDocAction.SC_ITALIC:
            self._wrapSelection(nwShortcode.ITALIC_O, nwShortcode.ITALIC_C)
        elif action == nwDocAction.SC_BOLD:
            self._wrapSelection(nwShortcode.BOLD_O, nwShortcode.BOLD_C)
        elif action == nwDocAction.SC_STRIKE:
            self._wrapSelection(nwShortcode.STRIKE_O, nwShortcode.STRIKE_C)
        elif action == nwDocAction.SC_ULINE:
            self._wrapSelection(nwShortcode.ULINE_O, nwShortcode.ULINE_C)
        elif action == nwDocAction.SC_SUP:
            self._wrapSelection(nwShortcode.SUP_O, nwShortcode.SUP_C)
        elif action == nwDocAction.SC_SUB:
            self._wrapSelection(nwShortcode.SUB_O, nwShortcode.SUB_C)
        else:
            logger.debug("Unknown or unsupported document action '%s'", str(action))
            self._allowAutoReplace(True)
            return False

        self._allowAutoReplace(True)
        self._lastActive = time()

        return True

    def anyFocus(self) -> bool:
        """Check if any widget or child widget has focus."""
        if self.hasFocus():
            return True
        if self.isAncestorOf(qApp.focusWidget()):
            return True
        return False

    def revealLocation(self) -> None:
        """Tell the user where on the file system the file in the editor
        is saved.
        """
        if isinstance(self._nwDocument, NWDocument):
            SHARED.info(
                "<br>".join([
                    self.tr("Document Details"),
                    "–"*40,
                    self.tr("Created: {0}").format(self._nwDocument.createdDate),
                    self.tr("Updated: {0}").format(self._nwDocument.updatedDate),
                ]),
                details=self.tr("File Location: {0}").format(self._nwDocument.fileLocation),
                log=False
            )
        return

    def insertText(self, insert: str | nwDocInsert) -> bool:
        """Insert a specific type of text at the cursor position."""
        if self._docHandle is None:
            logger.error("No document open")
            return False

        newBlock = False
        goAfter = False

        if isinstance(insert, str):
            text = insert
        elif isinstance(insert, nwDocInsert):
            if insert == nwDocInsert.QUOTE_LS:
                text = self._typSQuoteO
            elif insert == nwDocInsert.QUOTE_RS:
                text = self._typSQuoteC
            elif insert == nwDocInsert.QUOTE_LD:
                text = self._typDQuoteO
            elif insert == nwDocInsert.QUOTE_RD:
                text = self._typDQuoteC
            elif insert == nwDocInsert.SYNOPSIS:
                text = "%Synopsis: "
                newBlock = True
                goAfter = True
            elif insert == nwDocInsert.SHORT:
                text = "%Short: "
                newBlock = True
                goAfter = True
            elif insert == nwDocInsert.NEW_PAGE:
                text = "[newpage]"
                newBlock = True
                goAfter = False
            elif insert == nwDocInsert.VSPACE_S:
                text = "[vspace]"
                newBlock = True
                goAfter = False
            elif insert == nwDocInsert.VSPACE_M:
                text = "[vspace:2]"
                newBlock = True
                goAfter = False
            elif insert == nwDocInsert.LIPSUM:
                text = GuiLipsum.getLipsum(self)
                newBlock = True
                goAfter = False
            else:
                return False
        else:
            return False

        if text:
            if newBlock:
                self.insertNewBlock(text, defaultAfter=goAfter)
            else:
                cursor = self.textCursor()
                cursor.beginEditBlock()
                cursor.insertText(text)
                cursor.endEditBlock()

        return True

    def insertNewBlock(self, text: str, defaultAfter: bool = True) -> bool:
        """Insert a piece of text on a blank line."""
        cursor = self.textCursor()
        block = cursor.block()
        if not block.isValid():
            logger.error("Not a valid text block")
            return False

        sPos = block.position()
        sLen = block.length()

        cursor.beginEditBlock()

        if sLen > 1 and defaultAfter:
            cursor.setPosition(sPos + sLen - 1)
            cursor.insertText("\n")
        else:
            cursor.setPosition(sPos)

        cursor.insertText(text)

        if sLen > 1 and not defaultAfter:
            cursor.insertText("\n")

        cursor.endEditBlock()

        self.setTextCursor(cursor)

        return True

    def closeSearch(self) -> bool:
        """Close the search box."""
        self.docSearch.closeSearch()
        return self.docSearch.isVisible()

    ##
    #  Document Events and Maintenance
    ##

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Intercept key press events.
        We need to intercept a few key sequences:
          * The return and enter keys redirect here even if the search
            box has focus. Since we need these keys to continue search,
            we block any further interaction here while it has focus.
          * The undo/redo/select all sequences bypass the docAction
            pathway from the menu, so we redirect them back from here.
          * We also handle automatic scrolling here.
        """
        self._lastActive = time()
        isReturn  = event.key() == Qt.Key.Key_Return
        isReturn |= event.key() == Qt.Key.Key_Enter
        if isReturn and self.docSearch.anyFocus():
            return
        elif event == QKeySequence.StandardKey.Redo:
            self.docAction(nwDocAction.REDO)
            return
        elif event == QKeySequence.StandardKey.Undo:
            self.docAction(nwDocAction.UNDO)
            return
        elif event == QKeySequence.StandardKey.SelectAll:
            self.docAction(nwDocAction.SEL_ALL)
            return

        if CONFIG.autoScroll:
            cPos = self.cursorRect().topLeft().y()
            super().keyPressEvent(event)
            nPos = self.cursorRect().topLeft().y()
            kMod = event.modifiers()
            okMod = kMod in (Qt.KeyboardModifier.NoModifier, Qt.KeyboardModifier.ShiftModifier)
            okKey = event.key() not in self.MOVE_KEYS
            if nPos != cPos and okMod and okKey:
                mPos = CONFIG.autoScrollPos*0.01 * self.viewport().height()
                if cPos > mPos:
                    vBar = self.verticalScrollBar()
                    vBar.setValue(vBar.value() + (1 if nPos > cPos else -1))
        else:
            super().keyPressEvent(event)

        self.docFooter.updateLineCount()

        return

    def focusNextPrevChild(self, next: bool) -> bool:
        """Capture the focus request from the tab key on the text
        editor. If the editor has focus, we do not change focus and
        allow the editor to insert a tab. If the search bar has focus,
        we forward the call to the search object.
        """
        if self.hasFocus():
            return False
        elif self.docSearch.isVisible():
            return self.docSearch.cycleFocus(next)
        return True

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """If the mouse button is released and the control key is
        pressed, check if we're clicking on a tag, and trigger the
        follow tag function.
        """
        if qApp.keyboardModifiers() == Qt.KeyboardModifier.ControlModifier:
            self._processTag(self.cursorForPosition(event.pos()))
        super().mouseReleaseEvent(event)
        self.docFooter.updateLineCount()
        return

    def resizeEvent(self, event: QResizeEvent) -> None:
        """If the text editor is resized, we must make sure the document
        has its margins adjusted according to user preferences.
        """
        self.updateDocMargins()
        super().resizeEvent(event)
        return

    ##
    #  Public Slots
    ##

    @pyqtSlot(str)
    def updateDocInfo(self, tHandle: str) -> None:
        """Called when an item label is changed to check if the document
        title bar needs updating,
        """
        if tHandle == self._docHandle:
            self.docHeader.setTitleFromHandle(self._docHandle)
            self.docFooter.updateInfo()
            self.updateDocMargins()
        return

    @pyqtSlot(str)
    def insertKeyWord(self, keyword: str) -> bool:
        """Insert a keyword in the text editor, at the cursor position.
        If the insert line is not blank, a new line is started.
        """
        if keyword not in nwKeyWords.VALID_KEYS:
            logger.error("Invalid keyword '%s'", keyword)
            return False
        logger.debug("Inserting keyword '%s'", keyword)
        state = self.insertNewBlock("%s: " % keyword)
        return state

    @pyqtSlot()
    def toggleSearch(self) -> None:
        """Toggle the visibility of the search box."""
        if self.docSearch.isVisible():
            self.docSearch.closeSearch()
        else:
            self.beginSearch()
        return

    ##
    #  Private Slots
    ##

    @pyqtSlot(int, int, int)
    def _docChange(self, pos: int, removed: int, added: int) -> None:
        """Triggered by QTextDocument->contentsChanged. This also
        triggers the syntax highlighter.
        """
        self._lastEdit = time()
        self._lastFind = None

        if not self._docChanged:
            self.setDocumentChanged(removed != 0 or added != 0)

        if not self.wcTimerDoc.isActive():
            self.wcTimerDoc.start()

        block = self._qDocument.findBlock(pos)
        if not block.isValid():
            return

        text = block.text()
        if text.startswith("@") and added + removed == 1:
            # Only run on single keypresses, otherwise it will trigger
            # at unwanted times when other changes are made to the document
            cursor = self.textCursor()
            bPos = cursor.positionInBlock()
            if bPos > 0:
                show = self._completer.updateText(text, bPos)
                point = self.cursorRect().bottomRight()
                self._completer.move(self.viewport().mapToGlobal(point))
                self._completer.setVisible(show)
        else:
            self._completer.setVisible(False)

        if self._doReplace and added == 1:
            self._docAutoReplace(text)

        return

    @pyqtSlot(int, int, str)
    def _insertCompletion(self, pos: int, length: int, text: str) -> None:
        """Insert choice from the completer menu."""
        cursor = self.textCursor()
        block = cursor.block()
        if block.isValid():
            pos += block.position()
            cursor.setPosition(pos, QTextCursor.MoveMode.MoveAnchor)
            cursor.setPosition(pos + length, QTextCursor.MoveMode.KeepAnchor)
            cursor.insertText(text)
            self._completer.hide()
        return

    @pyqtSlot("QPoint")
    def _openContextMenu(self, pos: QPoint) -> None:
        """Open the editor context menu at a given coordinate."""
        uCursor = self.textCursor()
        pCursor = self.cursorForPosition(pos)
        pBlock = pCursor.block()

        ctxMenu = QMenu(self)
        ctxMenu.setObjectName("ContextMenu")
        if pBlock.userState() == GuiDocHighlighter.BLOCK_TITLE:
            action = ctxMenu.addAction(self.tr("Set as Document Name"))
            action.triggered.connect(lambda: self._emitRenameItem(pBlock))

        # Follow
        status = self._processTag(cursor=pCursor, follow=False)
        if status == nwTrinary.POSITIVE:
            action = ctxMenu.addAction(self.tr("Follow Tag"))
            action.triggered.connect(lambda: self._processTag(cursor=pCursor, follow=True))
            ctxMenu.addSeparator()
        elif status == nwTrinary.NEGATIVE:
            action = ctxMenu.addAction(self.tr("Create Note for Tag"))
            action.triggered.connect(lambda: self._processTag(cursor=pCursor, create=True))
            ctxMenu.addSeparator()

        # Cut, Copy and Paste
        if uCursor.hasSelection():
            action = ctxMenu.addAction(self.tr("Cut"))
            action.triggered.connect(lambda: self.docAction(nwDocAction.CUT))
            action = ctxMenu.addAction(self.tr("Copy"))
            action.triggered.connect(lambda: self.docAction(nwDocAction.COPY))

        action = ctxMenu.addAction(self.tr("Paste"))
        action.triggered.connect(lambda: self.docAction(nwDocAction.PASTE))
        ctxMenu.addSeparator()

        # Selections
        action = ctxMenu.addAction(self.tr("Select All"))
        action.triggered.connect(lambda: self.docAction(nwDocAction.SEL_ALL))
        action = ctxMenu.addAction(self.tr("Select Word"))
        action.triggered.connect(
            lambda: self._makePosSelection(QTextCursor.SelectionType.WordUnderCursor, pos)
        )
        action = ctxMenu.addAction(self.tr("Select Paragraph"))
        action.triggered.connect(lambda: self._makePosSelection(
            QTextCursor.SelectionType.BlockUnderCursor, pos)
        )

        # Spell Checking
        if SHARED.project.data.spellCheck:
            word, cPos, cLen, suggest = self._qDocument.spellErrorAtPos(pCursor.position())
            if word and cPos >= 0 and cLen > 0:
                logger.debug("Word '%s' is misspelled", word)
                block = pCursor.block()
                sCursor = self.textCursor()
                sCursor.setPosition(block.position() + cPos)
                sCursor.movePosition(
                    QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor, cLen
                )
                if suggest:
                    ctxMenu.addSeparator()
                    ctxMenu.addAction(self.tr("Spelling Suggestion(s)"))
                    for option in suggest[:15]:
                        action = ctxMenu.addAction(f"{nwUnicode.U_ENDASH} {option}")
                        action.triggered.connect(
                            lambda _, option=option: self._correctWord(sCursor, option)
                        )
                else:
                    ctxMenu.addAction("%s %s" % (nwUnicode.U_ENDASH, self.tr("No Suggestions")))

                ctxMenu.addSeparator()
                action = ctxMenu.addAction(self.tr("Add Word to Dictionary"))
                action.triggered.connect(lambda: self._addWord(word, block))

        # Execute the context menu
        ctxMenu.exec_(self.viewport().mapToGlobal(pos))
        ctxMenu.deleteLater()

        return

    @pyqtSlot("QTextCursor", str)
    def _correctWord(self, cursor: QTextCursor, word: str) -> None:
        """Slot for the spell check context menu triggering the
        replacement of a word with the word from the dictionary.
        """
        pos = cursor.selectionStart()
        cursor.beginEditBlock()
        cursor.removeSelectedText()
        cursor.insertText(word)
        cursor.endEditBlock()
        cursor.setPosition(pos)
        self.setTextCursor(cursor)
        return

    @pyqtSlot(str, "QTextBlock")
    def _addWord(self, word: str, block: QTextBlock) -> None:
        """Slot for the spell check context menu triggered when the user
        wants to add a word to the project dictionary.
        """
        logger.debug("Added '%s' to project dictionary", word)
        SHARED.spelling.addWord(word)
        self._qDocument.syntaxHighlighter.rehighlightBlock(block)
        return

    @pyqtSlot()
    def _runDocCounter(self) -> None:
        """Decide whether to run the word counter, or not due to
        inactivity.
        """
        if self._docHandle is None:
            return

        if self.wCounterDoc.isRunning():
            logger.debug("Word counter is busy")
            return

        if time() - self._lastEdit < 25.0:
            logger.debug("Running word counter")
            SHARED.runInThreadPool(self.wCounterDoc)

        return

    @pyqtSlot(int, int, int)
    def _updateDocCounts(self, cCount: int, wCount: int, pCount: int) -> None:
        """Process the word counter's finished signal."""
        if self._docHandle is None or self._nwItem is None:
            return

        logger.debug("Updating word count")

        self._nwItem.setCharCount(cCount)
        self._nwItem.setWordCount(wCount)
        self._nwItem.setParaCount(pCount)

        # Must not be emitted if docHandle is None!
        self.docCountsChanged.emit(self._docHandle, cCount, wCount, pCount)
        self.docFooter.updateCounts()

        return

    @pyqtSlot()
    def _updateSelectedStatus(self) -> None:
        """The user made a change in text selection. Forward this
        information to the footer, and start the selection word counter.
        """
        if self.textCursor().hasSelection():
            if not self.wcTimerSel.isActive():
                self.wcTimerSel.start()
            self.docFooter.setHasSelection(True)
        else:
            self.wcTimerSel.stop()
            self.docFooter.setHasSelection(False)
            self.docFooter.updateCounts()
        return

    @pyqtSlot()
    def _runSelCounter(self) -> None:
        """Update the selection word count."""
        if self._docHandle is None:
            return

        if self.wCounterSel.isRunning():
            logger.debug("Selection word counter is busy")
            return

        SHARED.runInThreadPool(self.wCounterSel)

        return

    @pyqtSlot(int, int, int)
    def _updateSelCounts(self, cCount: int, wCount: int, pCount: int) -> None:
        """Update the counts on the counter's finished signal."""
        if self._docHandle is None or self._nwItem is None:
            return

        logger.debug("User selected %d words", wCount)
        self.docFooter.updateCounts(wCount=wCount, cCount=cCount)
        self.wcTimerSel.stop()

        return

    @pyqtSlot()
    def _closeCurrentDocument(self) -> None:
        """Close the document. Forwarded to the main Gui."""
        self.closeDocumentRequest.emit()
        self.docToolBar.setVisible(False)
        return

    @pyqtSlot()
    def _toggleToolBarVisibility(self) -> None:
        """Toggle the visibility of the tool bar."""
        state = not self.docToolBar.isVisible()
        self.docToolBar.setVisible(state)
        CONFIG.showEditToolBar = state
        return

    ##
    #  Search & Replace
    ##

    def beginSearch(self) -> None:
        """Set the selected text as the search text."""
        cursor = self.textCursor()
        if cursor.hasSelection():
            self.docSearch.setSearchText(cursor.selectedText())
        else:
            self.docSearch.setSearchText(None)
        resS, _ = self.findAllOccurences()
        self.docSearch.setResultCount(None, len(resS))
        return

    def beginReplace(self) -> None:
        """Initialise the search box and reset the replace text box."""
        self.beginSearch()
        self.docSearch.setReplaceText("")
        self.updateDocMargins()
        return

    def findNext(self, goBack: bool = False) -> None:
        """Search for the next or previous occurrence of the search bar
        text in the document. Wrap around if not found and loop is
        enabled, or continue to next file if next file is enabled.
        """
        if not self.anyFocus():
            logger.debug("Editor does not have focus")
            return

        if not self.docSearch.isVisible():
            self.beginSearch()
            return

        resS, resE = self.findAllOccurences()
        if len(resS) == 0 and self._docHandle:
            self.docSearch.setResultCount(0, 0)
            self._lastFind = None
            if self.docSearch.doNextFile and not goBack:
                self.mainGui.openNextDocument(
                    self._docHandle, wrapAround=self.docSearch.doLoop
                )
                self.beginSearch()
            return

        cursor = self.textCursor()
        resIdx = bisect.bisect_left(resS, cursor.position())

        doLoop = self.docSearch.doLoop
        maxIdx = len(resS) - 1

        if goBack:
            resIdx -= 2

        if resIdx < 0:
            resIdx = maxIdx if doLoop else 0

        if resIdx > maxIdx and self._docHandle:
            if self.docSearch.doNextFile and not goBack:
                self.mainGui.openNextDocument(
                    self._docHandle, wrapAround=self.docSearch.doLoop
                )
                self.beginSearch()
                return
            else:
                resIdx = 0 if doLoop else maxIdx

        cursor.setPosition(resS[resIdx], QTextCursor.MoveMode.MoveAnchor)
        cursor.setPosition(resE[resIdx], QTextCursor.MoveMode.KeepAnchor)
        self.setTextCursor(cursor)

        self.docFooter.updateLineCount()
        self.docSearch.setResultCount(resIdx + 1, len(resS))
        self._lastFind = (resS[resIdx], resE[resIdx])

        return

    def findAllOccurences(self) -> tuple[list[int], list[int]]:
        """Create a list of all search results of the current search
        text in the document.
        """
        resS = []
        resE = []
        cursor = self.textCursor()
        hasSelection = cursor.hasSelection()
        if hasSelection:
            origA = cursor.selectionStart()
            origB = cursor.selectionEnd()
        else:
            origA = cursor.position()
            origB = cursor.position()

        findOpt = QTextDocument.FindFlag(0)
        if self.docSearch.isCaseSense:
            findOpt |= QTextDocument.FindFlag.FindCaseSensitively
        if self.docSearch.isWholeWord:
            findOpt |= QTextDocument.FindFlag.FindWholeWords

        searchFor = self.docSearch.getSearchObject()
        cursor.setPosition(0)
        self.setTextCursor(cursor)

        # Search up to a maximum of 1000, and make sure certain special
        # searches like a regex search for .* don't loop infinitely
        while self.find(searchFor, findOpt) and len(resE) <= 1000:
            cursor = self.textCursor()
            if cursor.hasSelection():
                resS.append(cursor.selectionStart())
                resE.append(cursor.selectionEnd())
            else:
                logger.warning("The search returned an empty result")
                break

        if hasSelection:
            cursor.setPosition(origA, QTextCursor.MoveMode.MoveAnchor)
            cursor.setPosition(origB, QTextCursor.MoveMode.KeepAnchor)
        else:
            cursor.setPosition(origA)

        self.setTextCursor(cursor)

        return resS, resE

    def replaceNext(self) -> None:
        """Search for the next occurrence of the search bar text in the
        document and replace it with the replace text. Call search next
        automatically when done.
        """
        if not self.anyFocus():
            logger.debug("Editor does not have focus")
            return

        if not self.docSearch.isVisible():
            # The search tool is not active, so we activate it.
            self.beginSearch()
            return

        cursor = self.textCursor()
        if not cursor.hasSelection():
            # We have no text selected at all, so just make this a
            # regular find next call.
            self.findNext()
            return

        if self._lastFind is None and cursor.hasSelection():
            # If we have a selection but no search, it may have been the
            # text we triggered the search with, in which case we search
            # again from the beginning of that selection to make sure we
            # have a valid result.
            sPos = cursor.selectionStart()
            cursor.clearSelection()
            cursor.setPosition(sPos)
            self.setTextCursor(cursor)
            self.findNext()
            cursor = self.textCursor()

        if self._lastFind is None:
            # In case the above didn't find a result, we give up here.
            return

        searchFor = self.docSearch.searchText
        replWith = self.docSearch.replaceText

        if self.docSearch.doMatchCap:
            replWith = transferCase(cursor.selectedText(), replWith)

        # Make sure the selected text was selected by an actual find
        # call, and not the user.
        try:
            isFind  = self._lastFind[0] == cursor.selectionStart()
            isFind &= self._lastFind[1] == cursor.selectionEnd()
        except Exception:
            isFind = False

        if isFind:
            cursor.beginEditBlock()
            cursor.removeSelectedText()
            cursor.insertText(replWith)
            cursor.endEditBlock()
            cursor.setPosition(cursor.selectionEnd())
            self.setTextCursor(cursor)
            logger.debug(
                "Replaced occurrence of '%s' with '%s' on line %d",
                searchFor, replWith, cursor.blockNumber()
            )
        else:
            logger.error("The selected text is not a search result, skipping replace")

        self.findNext()

        return

    ##
    #  Internal Functions : Text Manipulation
    ##

    def _toggleFormat(self, fLen: int, fChar: str) -> bool:
        """Toggle the formatting of a specific type for a piece of text.
        If more than one block is selected, the formatting is applied to
        the first block.
        """
        cursor = self.textCursor()
        posO = cursor.position()
        if cursor.hasSelection():
            select = _SelectAction.KEEP_SELECTION
        else:
            cursor = self._autoSelect()
            if cursor.hasSelection() and posO == cursor.selectionEnd():
                select = _SelectAction.MOVE_AFTER
            else:
                select = _SelectAction.KEEP_POSITION

        posS = cursor.selectionStart()
        posE = cursor.selectionEnd()
        if self._qDocument.characterAt(posO - 1) == fChar:
            logger.warning("Format repetition, cancelling action")
            cursor.clearSelection()
            cursor.setPosition(posO)
            self.setTextCursor(cursor)
            return False

        blockS = self._qDocument.findBlock(posS)
        blockE = self._qDocument.findBlock(posE)
        if blockS != blockE:
            posE = blockS.position() + blockS.length() - 1
            cursor.clearSelection()
            cursor.setPosition(posS, QTextCursor.MoveMode.MoveAnchor)
            cursor.setPosition(posE, QTextCursor.MoveMode.KeepAnchor)
            self.setTextCursor(cursor)

        numB = 0
        for n in range(fLen):
            if self._qDocument.characterAt(posS-n-1) == fChar:
                numB += 1
            else:
                break

        numA = 0
        for n in range(fLen):
            if self._qDocument.characterAt(posE+n) == fChar:
                numA += 1
            else:
                break

        if fLen == min(numA, numB):
            cursor.clearSelection()
            cursor.beginEditBlock()
            cursor.setPosition(posS)
            for i in range(fLen):
                cursor.deletePreviousChar()
            cursor.setPosition(posE)
            for i in range(fLen):
                cursor.deletePreviousChar()
            cursor.endEditBlock()
            cursor.clearSelection()
            cursor.setPosition(posO - fLen)
            self.setTextCursor(cursor)

        else:
            self._wrapSelection(fChar*fLen, pos=posO, select=select)

        return True

    def _wrapSelection(self, before: str, after: str | None = None, pos: int | None = None,
                       select: _SelectAction = _SelectAction.NO_DECISION) -> bool:
        """Wrap the selected text in whatever is in tBefore and tAfter.
        If there is no selection, the autoSelect setting decides the
        action. AutoSelect will select the word under the cursor before
        wrapping it. If this feature is disabled, nothing is done.
        """
        if after is None:
            after = before

        cursor = self.textCursor()
        posO = pos if isinstance(pos, int) else cursor.position()
        if select == _SelectAction.NO_DECISION:
            if cursor.hasSelection():
                select = _SelectAction.KEEP_SELECTION
            else:
                cursor = self._autoSelect()
                if cursor.hasSelection() and posO == cursor.selectionEnd():
                    select = _SelectAction.MOVE_AFTER
                else:
                    select = _SelectAction.KEEP_POSITION

        posS = cursor.selectionStart()
        posE = cursor.selectionEnd()

        blockS = self._qDocument.findBlock(posS)
        blockE = self._qDocument.findBlock(posE)
        if blockS != blockE:
            posE = blockS.position() + blockS.length() - 1

        cursor.clearSelection()
        cursor.beginEditBlock()
        cursor.setPosition(posE)
        cursor.insertText(after)
        cursor.setPosition(posS)
        cursor.insertText(before)
        cursor.endEditBlock()

        if select == _SelectAction.MOVE_AFTER:
            cursor.setPosition(posE + len(before + after))
        elif select == _SelectAction.KEEP_SELECTION:
            cursor.setPosition(posE + len(before), QTextCursor.MoveMode.MoveAnchor)
            cursor.setPosition(posS + len(before), QTextCursor.MoveMode.KeepAnchor)
        elif select == _SelectAction.KEEP_POSITION:
            cursor.setPosition(posO + len(before))

        self.setTextCursor(cursor)

        return True

    def _replaceQuotes(self, sQuote: str, oQuote: str, cQuote: str) -> bool:
        """Replace all straight quotes in the selected text."""
        cursor = self.textCursor()
        if not cursor.hasSelection():
            SHARED.error(self.tr("Please select some text before calling replace quotes."))
            return False

        posS = cursor.selectionStart()
        posE = cursor.selectionEnd()
        closeCheck = (" ", "\n", nwUnicode.U_LSEP, nwUnicode.U_PSEP)

        self._allowAutoReplace(False)
        for posC in range(posS, posE+1):
            cursor.setPosition(posC)
            cursor.movePosition(
                QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.KeepAnchor, 2
            )
            selText = cursor.selectedText()

            nS = len(selText)
            if nS == 2:
                pC = selText[0]
                cC = selText[1]
            elif nS == 1:
                pC = " "
                cC = selText[0]
            else:  # pragma: no cover
                continue

            if cC != sQuote:
                continue

            cursor.clearSelection()
            cursor.setPosition(posC)
            if pC in closeCheck:
                cursor.beginEditBlock()
                cursor.movePosition(
                    QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.KeepAnchor, 1
                )
                cursor.insertText(oQuote)
                cursor.endEditBlock()
            else:
                cursor.beginEditBlock()
                cursor.movePosition(
                    QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.KeepAnchor, 1
                )
                cursor.insertText(cQuote)
                cursor.endEditBlock()

        self._allowAutoReplace(True)

        return True

    def _processBlockFormat(
        self, action: nwDocAction, text: str, toggle: bool = True
    ) -> tuple[nwDocAction, str, int]:
        """Process the formatting of a single text block."""
        # Remove existing format first, if any
        if text.startswith("@"):
            logger.error("Cannot apply block format to keyword/value line")
            return nwDocAction.NO_ACTION, "", 0
        elif text.startswith("%~"):
            temp = text[2:].lstrip()
            offset = len(text) - len(temp)
            if toggle and action == nwDocAction.BLOCK_IGN:
                action = nwDocAction.BLOCK_TXT
        elif text.startswith("%"):
            temp = text[1:].lstrip()
            offset = len(text) - len(temp)
            if toggle and action == nwDocAction.BLOCK_COM:
                action = nwDocAction.BLOCK_TXT
        elif text.startswith("# "):
            temp = text[2:]
            offset = 2
        elif text.startswith("## "):
            temp = text[3:]
            offset = 3
        elif text.startswith("### "):
            temp = text[4:]
            offset = 4
        elif text.startswith("#### "):
            temp = text[5:]
            offset = 5
        elif text.startswith("#! "):
            temp = text[3:]
            offset = 3
        elif text.startswith("##! "):
            temp = text[4:]
            offset = 4
        elif text.startswith(">> "):
            temp = text[3:]
            offset = 3
        elif text.startswith("> ") and action != nwDocAction.INDENT_R:
            temp = text[2:]
            offset = 2
        elif text.startswith(">>"):
            temp = text[2:]
            offset = 2
        elif text.startswith(">") and action != nwDocAction.INDENT_R:
            temp = text[1:]
            offset = 1
        else:
            temp = text
            offset = 0

        # Also remove formatting tags at the end
        if text.endswith(" <<"):
            temp = temp[:-3]
        elif text.endswith(" <") and action != nwDocAction.INDENT_L:
            temp = temp[:-2]
        elif text.endswith("<<"):
            temp = temp[:-2]
        elif text.endswith("<") and action != nwDocAction.INDENT_L:
            temp = temp[:-1]

        # Apply new format
        if action == nwDocAction.BLOCK_COM:
            text = f"% {temp}"
            offset -= 2
        elif action == nwDocAction.BLOCK_IGN:
            text = f"%~ {temp}"
            offset -= 3
        elif action == nwDocAction.BLOCK_H1:
            text = f"# {temp}"
            offset -= 2
        elif action == nwDocAction.BLOCK_H2:
            text = f"## {temp}"
            offset -= 3
        elif action == nwDocAction.BLOCK_H3:
            text = f"### {temp}"
            offset -= 4
        elif action == nwDocAction.BLOCK_H4:
            text = f"#### {temp}"
            offset -= 5
        elif action == nwDocAction.BLOCK_TTL:
            text = f"#! {temp}"
            offset -= 3
        elif action == nwDocAction.BLOCK_UNN:
            text = f"##! {temp}"
            offset -= 4
        elif action == nwDocAction.ALIGN_L:
            text = f"{temp} <<"
        elif action == nwDocAction.ALIGN_C:
            text = f">> {temp} <<"
            offset -= 3
        elif action == nwDocAction.ALIGN_R:
            text = f">> {temp}"
            offset -= 3
        elif action == nwDocAction.INDENT_L:
            text = f"> {temp}"
            offset -= 2
        elif action == nwDocAction.INDENT_R:
            text = f"{temp} <"
        elif action == nwDocAction.BLOCK_TXT:
            text = temp
        else:
            logger.error("Unknown or unsupported block format requested: '%s'", str(action))
            return nwDocAction.NO_ACTION, "", 0

        return action, text, offset

    def _formatBlock(self, action: nwDocAction) -> bool:
        """Change the block format of the block under the cursor."""
        cursor = self.textCursor()
        block = cursor.block()
        if not block.isValid():
            logger.debug("Invalid block selected for action '%s'", str(action))
            return False

        action, text, offset = self._processBlockFormat(action, block.text())
        if action == nwDocAction.NO_ACTION:
            return False

        pos = cursor.position()

        cursor.beginEditBlock()
        self._makeSelection(QTextCursor.SelectionType.BlockUnderCursor, cursor)
        cursor.insertText(text)
        cursor.endEditBlock()

        if (move := pos - offset) >= 0:
            cursor.setPosition(move)
        self.setTextCursor(cursor)

        return True

    def _iterFormatBlocks(self, action: nwDocAction) -> bool:
        """Iterate over all selected blocks and apply format. If no
        selection is made, just forward the call to the single block
        formatter function.
        """
        cursor = self.textCursor()
        blocks = self._selectedBlocks(cursor)
        if len(blocks) < 2:
            return self._formatBlock(action)

        toggle = True
        cursor.beginEditBlock()
        for block in blocks:
            blockText = block.text()
            pAction, text, _ = self._processBlockFormat(action, blockText, toggle)
            if pAction != nwDocAction.NO_ACTION and blockText.strip():
                action = pAction  # First block decides further actions
                cursor.setPosition(block.position())
                self._makeSelection(QTextCursor.SelectionType.BlockUnderCursor, cursor)
                cursor.insertText(text)
                toggle = False

        cursor.endEditBlock()

        return True

    def _selectedBlocks(self, cursor: QTextCursor) -> list[QTextBlock]:
        """Return a list of all blocks selected by a cursor."""
        if cursor.hasSelection():
            iS = self._qDocument.findBlock(cursor.selectionStart()).blockNumber()
            iE = self._qDocument.findBlock(cursor.selectionEnd()).blockNumber()
            return [self._qDocument.findBlockByNumber(i) for i in range(iS, iE+1)]
        return []

    def _removeInParLineBreaks(self) -> None:
        """Strip line breaks within paragraphs in the selected text."""
        cursor = self.textCursor()
        if not cursor.hasSelection():
            cursor.select(QTextCursor.SelectionType.Document)

        rS = 0
        rE = self._qDocument.characterCount()
        if sBlocks := self._selectedBlocks(cursor):
            rS = sBlocks[0].position()
            rE = sBlocks[-1].position() + sBlocks[-1].length()

        # Clean up the text
        currPar = []
        cleanText = ""
        for cBlock in sBlocks:
            cText = cBlock.text()
            if cText.strip() == "":
                if currPar:
                    cleanText += " ".join(currPar) + "\n\n"
                else:
                    cleanText += "\n"
                currPar = []
            elif cText.startswith(("# ", "## ", "### ", "#### ", "@", "%")):
                cleanText += cText + "\n"
            else:
                currPar.append(cText)

        if currPar:
            cleanText += " ".join(currPar) + "\n\n"

        # Replace the text with the cleaned up text
        cursor.beginEditBlock()
        cursor.clearSelection()
        cursor.setPosition(rS)
        cursor.movePosition(
            QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor, rE-rS
        )
        cursor.insertText(cleanText.rstrip() + "\n")
        cursor.endEditBlock()

        return

    ##
    #  Internal Functions
    ##

    def _processTag(self, cursor: QTextCursor | None = None,
                    follow: bool = True, create: bool = False) -> nwTrinary:
        """Activated by Ctrl+Enter. Checks that we're in a block
        starting with '@'. We then find the tag under the cursor and
        check that it is not the tag itself. If all this is fine, we
        have a tag and can tell the document viewer to try and find and
        load the file where the tag is defined.
        """
        if cursor is None:
            cursor = self.textCursor()

        block = cursor.block()
        text = block.text()
        if len(text) == 0:
            return nwTrinary.NEUTRAL

        if text.startswith("@") and self._docHandle:

            isGood, tBits, tPos = SHARED.project.index.scanThis(text)
            if not isGood or not tBits or tBits[0] == nwKeyWords.TAG_KEY:
                return nwTrinary.NEUTRAL

            tag = ""
            exist = False
            cPos = cursor.selectionStart() - block.position()
            tExist = SHARED.project.index.checkThese(tBits, self._docHandle)
            for sTag, sPos, sExist in zip(reversed(tBits), reversed(tPos), reversed(tExist)):
                if cPos >= sPos:
                    # The cursor is between the start of two tags
                    if cPos <= sPos + len(sTag):
                        # The cursor is inside or at the edge of the tag
                        tag = sTag
                        exist = sExist
                    break

            if not tag or tag.startswith("@"):
                # The keyword cannot be looked up, so we ignore that
                return nwTrinary.NEUTRAL

            if follow and exist:
                logger.debug("Attempting to follow tag '%s'", tag)
                self.loadDocumentTagRequest.emit(tag, nwDocMode.VIEW)
            elif create and not exist:
                if SHARED.question(self.tr(
                    "Do you want to create a new project note for the tag '{0}'?"
                ).format(tag)):
                    itemClass = nwKeyWords.KEY_CLASS.get(tBits[0], nwItemClass.NO_CLASS)
                    if SHARED.mainGui.projView.createNewNote(tag, itemClass):
                        self._qDocument.syntaxHighlighter.rehighlightBlock(block)
                    else:
                        SHARED.error(self.tr(
                            "Could not create note in a root folder for '{0}'. "
                            "If one doesn't exist, you must create one first."
                        ).format(trConst(nwLabels.CLASS_NAME[itemClass])))

            return nwTrinary.POSITIVE if exist else nwTrinary.NEGATIVE

        return nwTrinary.NEUTRAL

    def _emitRenameItem(self, block: QTextBlock) -> None:
        """Emit a signal to request an item be renamed."""
        if self._docHandle:
            text = block.text().lstrip("#").lstrip("!").strip()
            self.requestProjectItemRenamed.emit(self._docHandle, text)
        return

    def _openContextFromCursor(self) -> None:
        """Open the spell check context menu at the cursor."""
        self._openContextMenu(self.cursorRect().center())
        return

    def _docAutoReplace(self, text: str) -> None:
        """Auto-replace text elements based on main configuration."""
        cursor = self.textCursor()
        tPos = cursor.positionInBlock()
        tLen = len(text)

        if tLen < 1 or tPos-1 > tLen:
            return

        tOne = text[tPos-1:tPos]
        tTwo = text[tPos-2:tPos]
        tThree = text[tPos-3:tPos]

        if not tOne:
            return

        nDelete = 0
        tInsert = tOne

        if self._typRepDQuote and tTwo[:1].isspace() and tTwo.endswith('"'):
            nDelete = 1
            tInsert = self._typDQuoteO

        elif self._typRepDQuote and tOne == '"':
            nDelete = 1
            if tPos == 1:
                tInsert = self._typDQuoteO
            elif tPos == 2 and tTwo == '>"':
                tInsert = self._typDQuoteO
            elif tPos == 3 and tThree == '>>"':
                tInsert = self._typDQuoteO
            else:
                tInsert = self._typDQuoteC

        elif self._typRepSQuote and tTwo[:1].isspace() and tTwo.endswith("'"):
            nDelete = 1
            tInsert = self._typSQuoteO

        elif self._typRepSQuote and tOne == "'":
            nDelete = 1
            if tPos == 1:
                tInsert = self._typSQuoteO
            elif tPos == 2 and tTwo == ">'":
                tInsert = self._typSQuoteO
            elif tPos == 3 and tThree == ">>'":
                tInsert = self._typSQuoteO
            else:
                tInsert = self._typSQuoteC

        elif self._typRepDash and tThree == "---":
            nDelete = 3
            tInsert = nwUnicode.U_EMDASH

        elif self._typRepDash and tTwo == "--":
            nDelete = 2
            tInsert = nwUnicode.U_ENDASH

        elif self._typRepDash and tTwo == nwUnicode.U_ENDASH + "-":
            nDelete = 2
            tInsert = nwUnicode.U_EMDASH

        elif self._typRepDots and tThree == "...":
            nDelete = 3
            tInsert = nwUnicode.U_HELLIP

        elif tOne == nwUnicode.U_LSEP:
            # This resolves issue #1150
            nDelete = 1
            tInsert = nwUnicode.U_PSEP

        tCheck = tInsert
        if self._typPadBefore and tCheck in self._typPadBefore:
            if self._allowSpaceBeforeColon(text, tCheck):
                nDelete = max(nDelete, 1)
                chkPos = tPos - nDelete - 1
                if chkPos >= 0 and text[chkPos].isspace():
                    # Strip existing space before inserting a new (#1061)
                    nDelete += 1
                tInsert = self._typPadChar + tInsert

        if self._typPadAfter and tCheck in self._typPadAfter:
            if self._allowSpaceBeforeColon(text, tCheck):
                nDelete = max(nDelete, 1)
                tInsert = tInsert + self._typPadChar

        if nDelete > 0:
            cursor.movePosition(
                QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.KeepAnchor, nDelete
            )
            cursor.insertText(tInsert)

        return

    @staticmethod
    def _allowSpaceBeforeColon(text: str, char: str) -> bool:
        """Special checker function only used by the insert space
        feature for French, Spanish, etc, so it doesn't insert a
        space before colons in meta data lines. See issue #1090.
        """
        if char == ":" and len(text) > 1:
            if text[0] == "@":
                return False
            if text[0] == "%":
                if text[1:].lstrip()[:9].lower() == "synopsis:":
                    return False
        return True

    def _autoSelect(self) -> QTextCursor:
        """Return a cursor which may or may not have a selection based
        on user settings and document action. The selection will be the
        word closest to the cursor consisting of alphanumerical unicode
        characters.
        """
        cursor = self.textCursor()
        if CONFIG.autoSelect and not cursor.hasSelection():
            cPos = cursor.position()
            bPos = cursor.block().position()
            bLen = cursor.block().length()
            apos = nwUnicode.U_APOS + nwUnicode.U_RSQUO

            # Scan backward
            sPos = cPos
            for i in range(cPos - bPos):
                sPos = cPos - i - 1
                cOne = self._qDocument.characterAt(sPos)
                cTwo = self._qDocument.characterAt(sPos - 1)
                if not (cOne.isalnum() or cOne in apos and cTwo.isalnum()):
                    sPos += 1
                    break

            # Scan forward
            ePos = cPos
            for i in range(bPos + bLen - cPos):
                ePos = cPos + i
                cOne = self._qDocument.characterAt(ePos)
                cTwo = self._qDocument.characterAt(ePos + 1)
                if not (cOne.isalnum() or cOne in apos and cTwo.isalnum()):
                    break

            if ePos - sPos <= 0:
                # No selection possible
                return cursor

            cursor.clearSelection()
            cursor.setPosition(sPos, QTextCursor.MoveMode.MoveAnchor)
            cursor.setPosition(ePos, QTextCursor.MoveMode.KeepAnchor)

            self.setTextCursor(cursor)

        return cursor

    def _makeSelection(self, mode: QTextCursor.SelectionType,
                       cursor: QTextCursor | None = None) -> None:
        """Select text based on selection mode."""
        if cursor is None:
            cursor = self.textCursor()
        cursor.clearSelection()
        cursor.select(mode)

        if mode == QTextCursor.SelectionType.WordUnderCursor:
            cursor = self._autoSelect()

        elif mode == QTextCursor.SelectionType.BlockUnderCursor:
            # This selection mode also selects the preceding paragraph
            # separator, which we want to avoid.
            posS = cursor.selectionStart()
            posE = cursor.selectionEnd()
            selTxt = cursor.selectedText()
            if selTxt.startswith(nwUnicode.U_PSEP):
                cursor.setPosition(posS+1, QTextCursor.MoveMode.MoveAnchor)
                cursor.setPosition(posE, QTextCursor.MoveMode.KeepAnchor)

        self.setTextCursor(cursor)

        return

    def _makePosSelection(self, mode: QTextCursor.SelectionType, pos: QPoint) -> None:
        """Select text based on selection mode, but first move cursor."""
        cursor = self.cursorForPosition(pos)
        self.setTextCursor(cursor)
        self._makeSelection(mode)
        return

    def _allowAutoReplace(self, state: bool) -> None:
        """Enable/disable the auto-replace feature temporarily."""
        if state:
            self._doReplace = CONFIG.doReplace
        else:
            self._doReplace = False
        return

# END Class GuiDocEditor


class MetaCompleter(QMenu):
    """GuiWidget: Meta Completer Menu

    This is a context menu with options populated from the user's
    defined tags. It also helps to type the meta data keyword on a new
    line starting with an @. The updateText function should be called on
    every keystroke on a line starting with @.
    """

    complete = pyqtSignal(int, int, str)

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)
        return

    def updateText(self, text: str, pos: int) -> bool:
        """Update the menu options based on the line of text."""
        self.clear()
        kw, sep, _ = text.partition(":")
        if pos <= len(kw):
            offset = 0
            length = len(kw.rstrip())
            suffix = "" if sep else ":"
            options = list(filter(
                lambda x: x.startswith(kw.rstrip()), nwKeyWords.VALID_KEYS
            ))
        else:
            status, tBits, tPos = SHARED.project.index.scanThis(text)
            if not status:
                return False
            index = bisect.bisect_right(tPos, pos) - 1
            lookup = tBits[index].lower() if index > 0 else ""
            offset = tPos[index] if lookup else pos
            length = len(lookup)
            suffix = ""
            options = list(filter(
                lambda x: lookup in x.lower(), SHARED.project.index.getClassTags(
                    nwKeyWords.KEY_CLASS.get(kw.strip(), nwItemClass.NO_CLASS)
                )
            ))[:15]

        if not options:
            return False

        for value in sorted(options):
            rep = value + suffix
            action = self.addAction(value)
            action.triggered.connect(lambda _, r=rep: self._emitComplete(offset, length, r))

        return True

    ##
    #  Events
    ##

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Capture keypresses and forward most of them to the editor."""
        parent = self.parent()
        if event.key() in (
            Qt.Key.Key_Up, Qt.Key.Key_Down, Qt.Key.Key_Return,
            Qt.Key.Key_Enter, Qt.Key.Key_Escape
        ):
            super().keyPressEvent(event)
        elif isinstance(parent, GuiDocEditor):
            parent.keyPressEvent(event)
        return

    ##
    #  Internal Functions
    ##

    def _emitComplete(self, pos: int, length: int, value: str):
        """Emit the signal to indicate a selection has been made."""
        self.complete.emit(pos, length, value)
        return

# END Class MetaCompleter


# =============================================================================================== #
#  The Off-GUI Thread Word Counter
#  A runnable for the word counter to be run in the thread pool off the main GUI thread.
# =============================================================================================== #

class BackgroundWordCounter(QRunnable):

    def __init__(self, docEditor: GuiDocEditor, forSelection: bool = False) -> None:
        super().__init__()

        self._docEditor = docEditor
        self._forSelection = forSelection
        self._isRunning = False

        self.signals = BackgroundWordCounterSignals()

        return

    def isRunning(self) -> bool:
        return self._isRunning

    @pyqtSlot()
    def run(self) -> None:
        """Overloaded run function for the word counter, forwarding the
        call to the function that does the actual counting.
        """
        self._isRunning = True
        if self._forSelection:
            text = self._docEditor.textCursor().selectedText()
        else:
            text = self._docEditor.getText()

        cC, wC, pC = countWords(text)
        self.signals.countsReady.emit(cC, wC, pC)
        self._isRunning = False

        return

# END Class BackgroundWordCounter


class BackgroundWordCounterSignals(QObject):
    """The QRunnable cannot emit a signal, so we need a simple QObject
    to hold the word counter signal.
    """
    countsReady = pyqtSignal(int, int, int)

# END Class BackgroundWordCounterSignals


# =============================================================================================== #
#  The Formatting and Options Fold Out Menu
#  Only used by DocEditor, and is opened by the first button in the header
# =============================================================================================== #

class GuiDocToolBar(QWidget):

    requestDocAction = pyqtSignal(nwDocAction)

    def __init__(self, docEditor: GuiDocEditor) -> None:
        super().__init__(parent=docEditor)

        logger.debug("Create: GuiDocToolBar")

        cM = CONFIG.pxInt(4)
        tPx = int(0.8*SHARED.theme.fontPixelSize)
        iconSize = QSize(tPx, tPx)
        self.setContentsMargins(0, 0, 0, 0)

        # General Buttons
        # ===============

        self.tbBoldMD = QToolButton(self)
        self.tbBoldMD.setIconSize(iconSize)
        self.tbBoldMD.setToolTip(self.tr("Markdown Bold"))
        self.tbBoldMD.clicked.connect(
            lambda: self.requestDocAction.emit(nwDocAction.MD_BOLD)
        )

        self.tbItalicMD = QToolButton(self)
        self.tbItalicMD.setIconSize(iconSize)
        self.tbItalicMD.setToolTip(self.tr("Markdown Italic"))
        self.tbItalicMD.clicked.connect(
            lambda: self.requestDocAction.emit(nwDocAction.MD_ITALIC)
        )

        self.tbStrikeMD = QToolButton(self)
        self.tbStrikeMD.setIconSize(iconSize)
        self.tbStrikeMD.setToolTip(self.tr("Markdown Strikethrough"))
        self.tbStrikeMD.clicked.connect(
            lambda: self.requestDocAction.emit(nwDocAction.MD_STRIKE)
        )

        self.tbBold = QToolButton(self)
        self.tbBold.setIconSize(iconSize)
        self.tbBold.setToolTip(self.tr("Shortcode Bold"))
        self.tbBold.clicked.connect(
            lambda: self.requestDocAction.emit(nwDocAction.SC_BOLD)
        )

        self.tbItalic = QToolButton(self)
        self.tbItalic.setIconSize(iconSize)
        self.tbItalic.setToolTip(self.tr("Shortcode Italic"))
        self.tbItalic.clicked.connect(
            lambda: self.requestDocAction.emit(nwDocAction.SC_ITALIC)
        )

        self.tbStrike = QToolButton(self)
        self.tbStrike.setIconSize(iconSize)
        self.tbStrike.setToolTip(self.tr("Shortcode Strikethrough"))
        self.tbStrike.clicked.connect(
            lambda: self.requestDocAction.emit(nwDocAction.SC_STRIKE)
        )

        self.tbUnderline = QToolButton(self)
        self.tbUnderline.setIconSize(iconSize)
        self.tbUnderline.setToolTip(self.tr("Shortcode Underline"))
        self.tbUnderline.clicked.connect(
            lambda: self.requestDocAction.emit(nwDocAction.SC_ULINE)
        )

        self.tbSuperscript = QToolButton(self)
        self.tbSuperscript.setIconSize(iconSize)
        self.tbSuperscript.setToolTip(self.tr("Shortcode Superscript"))
        self.tbSuperscript.clicked.connect(
            lambda: self.requestDocAction.emit(nwDocAction.SC_SUP)
        )

        self.tbSubscript = QToolButton(self)
        self.tbSubscript.setIconSize(iconSize)
        self.tbSubscript.setToolTip(self.tr("Shortcode Subscript"))
        self.tbSubscript.clicked.connect(
            lambda: self.requestDocAction.emit(nwDocAction.SC_SUB)
        )

        # Assemble
        # ========

        self.outerBox = QVBoxLayout()
        self.outerBox.addWidget(self.tbBoldMD)
        self.outerBox.addWidget(self.tbItalicMD)
        self.outerBox.addWidget(self.tbStrikeMD)
        self.outerBox.addSpacing(cM)
        self.outerBox.addWidget(self.tbBold)
        self.outerBox.addWidget(self.tbItalic)
        self.outerBox.addWidget(self.tbStrike)
        self.outerBox.addWidget(self.tbUnderline)
        self.outerBox.addWidget(self.tbSuperscript)
        self.outerBox.addWidget(self.tbSubscript)
        self.outerBox.setContentsMargins(cM, cM, cM, cM)
        self.outerBox.setSpacing(cM)

        self.setLayout(self.outerBox)
        self.updateTheme()

        # Starts as Invisible
        self.setVisible(False)

        logger.debug("Ready: GuiDocToolBar")

        return

    def updateTheme(self) -> None:
        """Initialise GUI elements that depend on specific settings."""
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, SHARED.theme.colBack)
        palette.setColor(QPalette.ColorRole.WindowText, SHARED.theme.colText)
        palette.setColor(QPalette.ColorRole.Text, SHARED.theme.colText)
        self.setPalette(palette)

        self.tbBoldMD.setIcon(SHARED.theme.getIcon("fmt_bold-md"))
        self.tbItalicMD.setIcon(SHARED.theme.getIcon("fmt_italic-md"))
        self.tbStrikeMD.setIcon(SHARED.theme.getIcon("fmt_strike-md"))
        self.tbBold.setIcon(SHARED.theme.getIcon("fmt_bold"))
        self.tbItalic.setIcon(SHARED.theme.getIcon("fmt_italic"))
        self.tbStrike.setIcon(SHARED.theme.getIcon("fmt_strike"))
        self.tbUnderline.setIcon(SHARED.theme.getIcon("fmt_underline"))
        self.tbSuperscript.setIcon(SHARED.theme.getIcon("fmt_superscript"))
        self.tbSubscript.setIcon(SHARED.theme.getIcon("fmt_subscript"))

        return

# END Class GuiDocToolBar


# =============================================================================================== #
#  The Embedded Document Search/Replace Feature
#  Only used by DocEditor, and is at a fixed position in the QTextEdit's viewport
# =============================================================================================== #

class GuiDocEditSearch(QFrame):

    def __init__(self, docEditor: GuiDocEditor) -> None:
        super().__init__(parent=docEditor)

        logger.debug("Create: GuiDocEditSearch")

        self.docEditor = docEditor

        self.repVisible  = False
        self.isCaseSense = CONFIG.searchCase
        self.isWholeWord = CONFIG.searchWord
        self.isRegEx     = CONFIG.searchRegEx
        self.doLoop      = CONFIG.searchLoop
        self.doNextFile  = CONFIG.searchNextFile
        self.doMatchCap  = CONFIG.searchMatchCap

        mPx = CONFIG.pxInt(6)
        tPx = int(0.8*SHARED.theme.fontPixelSize)
        self.boxFont = SHARED.theme.guiFont
        self.boxFont.setPointSizeF(0.9*SHARED.theme.fontPointSize)

        self.setContentsMargins(0, 0, 0, 0)
        self.setAutoFillBackground(True)
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Plain)

        self.mainBox = QGridLayout(self)
        self.setLayout(self.mainBox)

        # Text Boxes
        # ==========

        self.searchBox = QLineEdit(self)
        self.searchBox.setFont(self.boxFont)
        self.searchBox.setPlaceholderText(self.tr("Search"))
        self.searchBox.returnPressed.connect(self._doSearch)

        self.replaceBox = QLineEdit(self)
        self.replaceBox.setFont(self.boxFont)
        self.replaceBox.setPlaceholderText(self.tr("Replace"))
        self.replaceBox.returnPressed.connect(self._doReplace)

        self.searchOpt = QToolBar(self)
        self.searchOpt.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.searchOpt.setIconSize(QSize(tPx, tPx))
        self.searchOpt.setContentsMargins(0, 0, 0, 0)

        self.searchLabel = QLabel(self.tr("Search"))
        self.searchLabel.setFont(self.boxFont)
        self.searchLabel.setIndent(CONFIG.pxInt(6))

        self.resultLabel = QLabel("?/?")
        self.resultLabel.setFont(self.boxFont)
        self.resultLabel.setMinimumWidth(SHARED.theme.getTextWidth("?/?", self.boxFont))

        self.toggleCase = QAction(self.tr("Case Sensitive"), self)
        self.toggleCase.setCheckable(True)
        self.toggleCase.setChecked(self.isCaseSense)
        self.toggleCase.toggled.connect(self._doToggleCase)
        self.searchOpt.addAction(self.toggleCase)

        self.toggleWord = QAction(self.tr("Whole Words Only"), self)
        self.toggleWord.setCheckable(True)
        self.toggleWord.setChecked(self.isWholeWord)
        self.toggleWord.toggled.connect(self._doToggleWord)
        self.searchOpt.addAction(self.toggleWord)

        self.toggleRegEx = QAction(self.tr("RegEx Mode"), self)
        self.toggleRegEx.setCheckable(True)
        self.toggleRegEx.setChecked(self.isRegEx)
        self.toggleRegEx.toggled.connect(self._doToggleRegEx)
        self.searchOpt.addAction(self.toggleRegEx)

        self.toggleLoop = QAction(self.tr("Loop Search"), self)
        self.toggleLoop.setCheckable(True)
        self.toggleLoop.setChecked(self.doLoop)
        self.toggleLoop.toggled.connect(self._doToggleLoop)
        self.searchOpt.addAction(self.toggleLoop)

        self.toggleProject = QAction(self.tr("Search Next File"), self)
        self.toggleProject.setCheckable(True)
        self.toggleProject.setChecked(self.doNextFile)
        self.toggleProject.toggled.connect(self._doToggleProject)
        self.searchOpt.addAction(self.toggleProject)

        self.searchOpt.addSeparator()

        self.toggleMatchCap = QAction(self.tr("Preserve Case"), self)
        self.toggleMatchCap.setCheckable(True)
        self.toggleMatchCap.setChecked(self.doMatchCap)
        self.toggleMatchCap.toggled.connect(self._doToggleMatchCap)
        self.searchOpt.addAction(self.toggleMatchCap)

        self.searchOpt.addSeparator()

        self.cancelSearch = QAction(self.tr("Close Search"), self)
        self.cancelSearch.triggered.connect(self._doClose)
        self.searchOpt.addAction(self.cancelSearch)

        # Buttons
        # =======

        bPx = self.searchBox.sizeHint().height()

        self.showReplace = QToolButton(self)
        self.showReplace.setArrowType(Qt.ArrowType.RightArrow)
        self.showReplace.setCheckable(True)
        self.showReplace.toggled.connect(self._doToggleReplace)

        self.searchButton = QPushButton("")
        self.searchButton.setFixedSize(QSize(bPx, bPx))
        self.searchButton.setToolTip(self.tr("Find in current document"))
        self.searchButton.clicked.connect(self._doSearch)

        self.replaceButton = QPushButton("")
        self.replaceButton.setFixedSize(QSize(bPx, bPx))
        self.replaceButton.setToolTip(self.tr("Find and replace in current document"))
        self.replaceButton.clicked.connect(self._doReplace)

        self.mainBox.addWidget(self.searchLabel,   0, 0, 1, 2, Qt.AlignmentFlag.AlignLeft)
        self.mainBox.addWidget(self.searchOpt,     0, 2, 1, 3, Qt.AlignmentFlag.AlignRight)
        self.mainBox.addWidget(self.showReplace,   1, 0, 1, 1)
        self.mainBox.addWidget(self.searchBox,     1, 1, 1, 2)
        self.mainBox.addWidget(self.searchButton,  1, 3, 1, 1)
        self.mainBox.addWidget(self.resultLabel,   1, 4, 1, 1)
        self.mainBox.addWidget(self.replaceBox,    2, 1, 1, 2)
        self.mainBox.addWidget(self.replaceButton, 2, 3, 1, 1)

        self.mainBox.setColumnStretch(0, 0)
        self.mainBox.setColumnStretch(1, 0)
        self.mainBox.setColumnStretch(2, 1)
        self.mainBox.setColumnStretch(3, 0)
        self.mainBox.setColumnStretch(4, 0)
        self.mainBox.setColumnStretch(5, 0)
        self.mainBox.setSpacing(CONFIG.pxInt(2))
        self.mainBox.setContentsMargins(mPx, mPx, mPx, mPx)

        boxWidth = CONFIG.pxInt(200)
        self.searchBox.setFixedWidth(boxWidth)
        self.replaceBox.setFixedWidth(boxWidth)
        self.replaceBox.setVisible(False)
        self.replaceButton.setVisible(False)
        self.adjustSize()

        self.updateTheme()

        logger.debug("Ready: GuiDocEditSearch")

        return

    ##
    #  Properties
    ##

    @property
    def searchText(self) -> str:
        """Return the current search text."""
        return self.searchBox.text()

    @property
    def replaceText(self) -> str:
        """Return the current replace text."""
        return self.replaceBox.text()

    ##
    #  Getters
    ##

    def getSearchObject(self) -> str | QRegularExpression | QRegExp:
        """Return the current search text either as text or as a regular
        expression object.
        """
        text = self.searchBox.text()
        if self.isRegEx:
            # Using the Unicode-capable QRegularExpression class was
            # only added in Qt 5.13. Otherwise, 5.3 and up supports
            # only the QRegExp class.
            if CONFIG.verQtValue >= 0x050d00:
                rxOpt = QRegularExpression.PatternOption.UseUnicodePropertiesOption
                if not self.isCaseSense:
                    rxOpt |= QRegularExpression.PatternOption.CaseInsensitiveOption
                regEx = QRegularExpression(text, rxOpt)
                self._alertSearchValid(regEx.isValid())
                return regEx
            else:  # pragma: no cover
                # >= 50300 to < 51300
                if self.isCaseSense:
                    rxOpt = Qt.CaseSensitivity.CaseSensitive
                else:
                    rxOpt = Qt.CaseSensitivity.CaseInsensitive
                regEx = QRegExp(text, rxOpt)
                self._alertSearchValid(regEx.isValid())
                return regEx

        return text

    ##
    #  Setters
    ##

    def setSearchText(self, text: str | None) -> None:
        """Open the search bar and set the search text to the text
        provided, if any.
        """
        if not self.isVisible():
            self.setVisible(True)
        if text is not None:
            self.searchBox.setText(text)
        self.searchBox.setFocus()
        self.searchBox.selectAll()
        if self.isRegEx:
            self._alertSearchValid(True)
        return

    def setReplaceText(self, text: str) -> None:
        """Set the replace text."""
        self.showReplace.setChecked(True)
        self.replaceBox.setFocus()
        self.replaceBox.setText(text)
        return

    def setResultCount(self, currRes: int | None, resCount: int | None) -> None:
        """Set the count values for the current search."""
        sCurrRes = "?" if currRes is None else str(currRes)
        sResCount = "?" if resCount is None else "1000+" if resCount > 1000 else str(resCount)
        minWidth = SHARED.theme.getTextWidth(f"{sResCount}//{sResCount}", self.boxFont)
        self.resultLabel.setText(f"{sCurrRes}/{sResCount}")
        self.resultLabel.setMinimumWidth(minWidth)
        self.adjustSize()
        self.docEditor.updateDocMargins()
        return

    ##
    #  Methods
    ##

    def updateTheme(self) -> None:
        """Update theme elements."""
        qPalette = qApp.palette()
        self.setPalette(qPalette)
        self.searchBox.setPalette(qPalette)
        self.replaceBox.setPalette(qPalette)

        # Set icons
        self.toggleCase.setIcon(SHARED.theme.getIcon("search_case"))
        self.toggleWord.setIcon(SHARED.theme.getIcon("search_word"))
        self.toggleRegEx.setIcon(SHARED.theme.getIcon("search_regex"))
        self.toggleLoop.setIcon(SHARED.theme.getIcon("search_loop"))
        self.toggleProject.setIcon(SHARED.theme.getIcon("search_project"))
        self.toggleMatchCap.setIcon(SHARED.theme.getIcon("search_preserve"))
        self.cancelSearch.setIcon(SHARED.theme.getIcon("search_cancel"))
        self.searchButton.setIcon(SHARED.theme.getIcon("search"))
        self.replaceButton.setIcon(SHARED.theme.getIcon("search_replace"))

        # Set stylesheets
        self.searchOpt.setStyleSheet("QToolBar {padding: 0;}")
        self.showReplace.setStyleSheet("QToolButton {border: none; background: transparent;}")

        # Construct Box Colours
        qPalette = self.searchBox.palette()
        baseCol = qPalette.base().color()
        rCol = baseCol.redF() + 0.1
        gCol = baseCol.greenF() - 0.1
        bCol = baseCol.blueF() - 0.1

        mCol = max(rCol, gCol, bCol, 1.0)
        errCol = QColor()
        errCol.setRedF(rCol/mCol)
        errCol.setGreenF(gCol/mCol)
        errCol.setBlueF(bCol/mCol)

        self.rxCol = {
            True: baseCol,
            False: errCol
        }

        return

    def closeSearch(self) -> None:
        """Close the search box."""
        CONFIG.searchCase = self.isCaseSense
        CONFIG.searchWord = self.isWholeWord
        CONFIG.searchRegEx = self.isRegEx
        CONFIG.searchLoop = self.doLoop
        CONFIG.searchNextFile = self.doNextFile
        CONFIG.searchMatchCap = self.doMatchCap

        self.showReplace.setChecked(False)
        self.setVisible(False)
        self.docEditor.updateDocMargins()
        self.docEditor.setFocus()

        return

    def cycleFocus(self, next: bool) -> bool:
        """The tab key just alternates focus between the two input
        boxes, if the replace box is visible.
        """
        if self.replaceBox.isVisible():
            if self.searchBox.hasFocus():
                self.replaceBox.setFocus()
                return True
            elif self.replaceBox.hasFocus():
                self.searchBox.setFocus()
                return True
        return False

    def anyFocus(self) -> bool:
        """Return True if any of the input boxes have focus."""
        return self.searchBox.hasFocus() | self.replaceBox.hasFocus()

    ##
    #  Private Slots
    ##

    @pyqtSlot()
    def _doClose(self) -> None:
        """Hide the search/replace bar."""
        self.closeSearch()
        return

    @pyqtSlot()
    def _doSearch(self) -> None:
        """Call the search action function for the document editor."""
        modKey = qApp.keyboardModifiers()
        if modKey == Qt.KeyboardModifier.ShiftModifier:
            self.docEditor.findNext(goBack=True)
        else:
            self.docEditor.findNext()
        return

    @pyqtSlot()
    def _doReplace(self) -> None:
        """Call the replace action function for the document editor."""
        self.docEditor.replaceNext()
        return

    @pyqtSlot(bool)
    def _doToggleReplace(self, state: bool) -> None:
        """Toggle the show/hide of the replace box."""
        if state:
            self.showReplace.setArrowType(Qt.ArrowType.DownArrow)
        else:
            self.showReplace.setArrowType(Qt.ArrowType.RightArrow)
        self.replaceBox.setVisible(state)
        self.replaceButton.setVisible(state)
        self.repVisible = state
        self.adjustSize()
        self.docEditor.updateDocMargins()
        return

    @pyqtSlot(bool)
    def _doToggleCase(self, state: bool) -> None:
        """Enable/disable case sensitive mode."""
        self.isCaseSense = state
        return

    @pyqtSlot(bool)
    def _doToggleWord(self, state: bool) -> None:
        """Enable/disable whole word search mode."""
        self.isWholeWord = state
        return

    @pyqtSlot(bool)
    def _doToggleRegEx(self, state: bool) -> None:
        """Enable/disable regular expression search mode."""
        self.isRegEx = state
        return

    @pyqtSlot(bool)
    def _doToggleLoop(self, state: bool) -> None:
        """Enable/disable looping the search."""
        self.doLoop = state
        return

    @pyqtSlot(bool)
    def _doToggleProject(self, state: bool) -> None:
        """Enable/disable continuing search in next project file."""
        self.doNextFile = state
        return

    @pyqtSlot(bool)
    def _doToggleMatchCap(self, state: bool) -> None:
        """Enable/disable preserving capitalisation when replacing."""
        self.doMatchCap = state
        return

    ##
    #  Internal Functions
    ##

    def _alertSearchValid(self, isValid: bool) -> None:
        """Highlight the search box to indicate the search string is or
        isn't valid. Take the colour from the replace box.
        """
        qPalette = self.replaceBox.palette()
        qPalette.setColor(QPalette.ColorRole.Base, self.rxCol[isValid])
        self.searchBox.setPalette(qPalette)
        return

# END Class GuiDocEditSearch


# =============================================================================================== #
#  The Embedded Document Header
#  Only used by DocEditor, and is at a fixed position in the QTextEdit's viewport
# =============================================================================================== #

class GuiDocEditHeader(QWidget):

    closeDocumentRequest = pyqtSignal()
    toggleToolBarRequest = pyqtSignal()

    def __init__(self, docEditor: GuiDocEditor) -> None:
        super().__init__(parent=docEditor)

        logger.debug("Create: GuiDocEditHeader")

        self.docEditor = docEditor
        self.mainGui   = docEditor.mainGui

        self._docHandle = None

        fPx = int(0.9*SHARED.theme.fontPixelSize)
        hSp = CONFIG.pxInt(6)
        iconSize = QSize(fPx, fPx)

        # Main Widget Settings
        self.setAutoFillBackground(True)

        # Title Label
        self.itemTitle = QLabel()
        self.itemTitle.setText("")
        self.itemTitle.setIndent(0)
        self.itemTitle.setMargin(0)
        self.itemTitle.setContentsMargins(0, 0, 0, 0)
        self.itemTitle.setAutoFillBackground(True)
        self.itemTitle.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        self.itemTitle.setFixedHeight(fPx)

        lblFont = self.itemTitle.font()
        lblFont.setPointSizeF(0.9*SHARED.theme.fontPointSize)
        self.itemTitle.setFont(lblFont)

        # Buttons
        self.tbButton = QToolButton(self)
        self.tbButton.setContentsMargins(0, 0, 0, 0)
        self.tbButton.setIconSize(iconSize)
        self.tbButton.setFixedSize(fPx, fPx)
        self.tbButton.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.tbButton.setVisible(False)
        self.tbButton.setToolTip(self.tr("Toggle Tool Bar"))
        self.tbButton.clicked.connect(lambda: self.toggleToolBarRequest.emit())

        self.searchButton = QToolButton(self)
        self.searchButton.setContentsMargins(0, 0, 0, 0)
        self.searchButton.setIconSize(iconSize)
        self.searchButton.setFixedSize(fPx, fPx)
        self.searchButton.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.searchButton.setVisible(False)
        self.searchButton.setToolTip(self.tr("Search"))
        self.searchButton.clicked.connect(self.docEditor.toggleSearch)

        self.minmaxButton = QToolButton(self)
        self.minmaxButton.setContentsMargins(0, 0, 0, 0)
        self.minmaxButton.setIconSize(iconSize)
        self.minmaxButton.setFixedSize(fPx, fPx)
        self.minmaxButton.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.minmaxButton.setVisible(False)
        self.minmaxButton.setToolTip(self.tr("Toggle Focus Mode"))
        self.minmaxButton.clicked.connect(lambda: self.docEditor.toggleFocusModeRequest.emit())

        self.closeButton = QToolButton(self)
        self.closeButton.setContentsMargins(0, 0, 0, 0)
        self.closeButton.setIconSize(iconSize)
        self.closeButton.setFixedSize(fPx, fPx)
        self.closeButton.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.closeButton.setVisible(False)
        self.closeButton.setToolTip(self.tr("Close"))
        self.closeButton.clicked.connect(self._closeDocument)

        # Assemble Layout
        self.outerBox = QHBoxLayout()
        self.outerBox.setSpacing(hSp)
        self.outerBox.addWidget(self.tbButton, 0)
        self.outerBox.addWidget(self.searchButton, 0)
        self.outerBox.addWidget(self.itemTitle, 1)
        self.outerBox.addWidget(self.minmaxButton, 0)
        self.outerBox.addWidget(self.closeButton, 0)
        self.setLayout(self.outerBox)

        # Fix Margins and Size
        # This is needed for high DPI systems. See issue #499.
        cM = CONFIG.pxInt(8)
        self.setContentsMargins(0, 0, 0, 0)
        self.outerBox.setContentsMargins(cM, cM, cM, cM)
        self.setMinimumHeight(fPx + 2*cM)

        self.updateTheme()

        logger.debug("Ready: GuiDocEditHeader")

        return

    ##
    #  Methods
    ##

    def updateTheme(self) -> None:
        """Update theme elements."""
        self.tbButton.setIcon(SHARED.theme.getIcon("menu"))
        self.searchButton.setIcon(SHARED.theme.getIcon("search"))
        self.minmaxButton.setIcon(SHARED.theme.getIcon("maximise"))
        self.closeButton.setIcon(SHARED.theme.getIcon("close"))

        colText = SHARED.theme.colText
        buttonStyle = (
            "QToolButton {{border: none; background: transparent;}} "
            "QToolButton:hover {{border: none; background: rgba({0}, {1}, {2}, 0.2);}}"
        ).format(colText.red(), colText.green(), colText.blue())

        self.tbButton.setStyleSheet(buttonStyle)
        self.searchButton.setStyleSheet(buttonStyle)
        self.minmaxButton.setStyleSheet(buttonStyle)
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
        self.itemTitle.setPalette(palette)

        return

    def setTitleFromHandle(self, tHandle: str | None) -> bool:
        """Set the document title from the handle, or alternatively, set
        the whole document path within the project.
        """
        self._docHandle = tHandle
        if tHandle is None:
            self.itemTitle.setText("")
            self.tbButton.setVisible(False)
            self.searchButton.setVisible(False)
            self.closeButton.setVisible(False)
            self.minmaxButton.setVisible(False)
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
            self.itemTitle.setText(sSep.join(tTitle))
        else:
            nwItem = pTree[tHandle]
            if nwItem is None:
                return False
            self.itemTitle.setText(nwItem.itemName)

        self.tbButton.setVisible(True)
        self.searchButton.setVisible(True)
        self.closeButton.setVisible(True)
        self.minmaxButton.setVisible(True)

        return True

    def updateFocusMode(self) -> None:
        """Update the minimise/maximise icon of the Focus Mode button.
        This function is called by the GuiMain class via the
        toggleFocusMode function and should not be activated directly.
        """
        if self.mainGui.isFocusMode:
            self.minmaxButton.setIcon(SHARED.theme.getIcon("minimise"))
        else:
            self.minmaxButton.setIcon(SHARED.theme.getIcon("maximise"))
        return

    ##
    #  Private Slots
    ##

    @pyqtSlot()
    def _closeDocument(self) -> None:
        """Trigger the close editor on the main window."""
        self.closeDocumentRequest.emit()
        self.tbButton.setVisible(False)
        self.searchButton.setVisible(False)
        self.closeButton.setVisible(False)
        self.minmaxButton.setVisible(False)
        return

    ##
    #  Events
    ##

    def mousePressEvent(self, event: QMouseEvent):
        """Capture a click on the title and ensure that the item is
        selected in the project tree.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.docEditor.requestProjectItemSelected.emit(self._docHandle, True)
        return

# END Class GuiDocEditHeader


# =============================================================================================== #
#  The Embedded Document Footer
#  Only used by DocEditor, and is at a fixed position in the QTextEdit's viewport
# =============================================================================================== #

class GuiDocEditFooter(QWidget):

    def __init__(self, docEditor: GuiDocEditor) -> None:
        super().__init__(parent=docEditor)

        logger.debug("Create: GuiDocEditFooter")

        self.docEditor = docEditor

        self._tItem     = None
        self._docHandle = None

        self._docSelection = False

        self.sPx = int(round(0.9*SHARED.theme.baseIconSize))
        fPx = int(0.9*SHARED.theme.fontPixelSize)
        bSp = CONFIG.pxInt(4)
        hSp = CONFIG.pxInt(6)

        lblFont = self.font()
        lblFont.setPointSizeF(0.9*SHARED.theme.fontPointSize)

        # Main Widget Settings
        self.setContentsMargins(0, 0, 0, 0)
        self.setAutoFillBackground(True)

        alLeftTop = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop

        # Status
        self.statusIcon = QLabel("")
        self.statusIcon.setContentsMargins(0, 0, 0, 0)
        self.statusIcon.setFixedHeight(self.sPx)
        self.statusIcon.setAlignment(alLeftTop)

        self.statusText = QLabel(self.tr("Status"))
        self.statusText.setIndent(0)
        self.statusText.setMargin(0)
        self.statusText.setContentsMargins(0, 0, 0, 0)
        self.statusText.setAutoFillBackground(True)
        self.statusText.setFixedHeight(fPx)
        self.statusText.setAlignment(alLeftTop)
        self.statusText.setFont(lblFont)

        # Lines
        self.linesIcon = QLabel("")
        self.linesIcon.setContentsMargins(0, 0, 0, 0)
        self.linesIcon.setFixedHeight(self.sPx)
        self.linesIcon.setAlignment(alLeftTop)

        self.linesText = QLabel("")
        self.linesText.setIndent(0)
        self.linesText.setMargin(0)
        self.linesText.setContentsMargins(0, 0, 0, 0)
        self.linesText.setAutoFillBackground(True)
        self.linesText.setFixedHeight(fPx)
        self.linesText.setAlignment(alLeftTop)
        self.linesText.setFont(lblFont)

        # Words
        self.wordsIcon = QLabel("")
        self.wordsIcon.setContentsMargins(0, 0, 0, 0)
        self.wordsIcon.setFixedHeight(self.sPx)
        self.wordsIcon.setAlignment(alLeftTop)

        self.wordsText = QLabel("")
        self.wordsText.setIndent(0)
        self.wordsText.setMargin(0)
        self.wordsText.setContentsMargins(0, 0, 0, 0)
        self.wordsText.setAutoFillBackground(True)
        self.wordsText.setFixedHeight(fPx)
        self.wordsText.setAlignment(alLeftTop)
        self.wordsText.setFont(lblFont)

        # Assemble Layout
        self.outerBox = QHBoxLayout()
        self.outerBox.setSpacing(bSp)
        self.outerBox.addWidget(self.statusIcon)
        self.outerBox.addWidget(self.statusText)
        self.outerBox.addStretch(1)
        self.outerBox.addWidget(self.linesIcon)
        self.outerBox.addWidget(self.linesText)
        self.outerBox.addSpacing(hSp)
        self.outerBox.addWidget(self.wordsIcon)
        self.outerBox.addWidget(self.wordsText)
        self.setLayout(self.outerBox)

        # Fix Margins and Size
        # This is needed for high DPI systems. See issue #499.
        cM = CONFIG.pxInt(8)
        self.setContentsMargins(0, 0, 0, 0)
        self.outerBox.setContentsMargins(cM, cM, cM, cM)
        self.setMinimumHeight(fPx + 2*cM)

        # Fix the Colours
        self.updateTheme()
        self.updateLineCount()
        self.updateCounts()

        logger.debug("Ready: GuiDocEditFooter")

        return

    ##
    #  Methods
    ##

    def updateTheme(self) -> None:
        """Update theme elements."""
        self.linesIcon.setPixmap(SHARED.theme.getPixmap("status_lines", (self.sPx, self.sPx)))
        self.wordsIcon.setPixmap(SHARED.theme.getPixmap("status_stats", (self.sPx, self.sPx)))
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
        self.statusText.setPalette(palette)
        self.linesText.setPalette(palette)
        self.wordsText.setPalette(palette)

        return

    def setHandle(self, tHandle: str | None) -> None:
        """Set the handle that will populate the footer's data."""
        self._docHandle = tHandle
        if self._docHandle is None:
            logger.debug("No handle set, so clearing the editor footer")
            self._tItem = None
        else:
            self._tItem = SHARED.project.tree[self._docHandle]

        self.setHasSelection(False)
        self.updateInfo()
        self.updateCounts()

        return

    def setHasSelection(self, hasSelection: bool) -> None:
        """Toggle the word counter mode between full count and selection
        count mode.
        """
        self._docSelection = hasSelection
        return

    def updateInfo(self) -> None:
        """Update the content of text labels."""
        if self._tItem is None:
            sIcon = QPixmap()
            sText = ""
        else:
            status, icon = self._tItem.getImportStatus(incIcon=True)
            sIcon = icon.pixmap(self.sPx, self.sPx)
            sText = f"{status} / {self._tItem.describeMe()}"

        self.statusIcon.setPixmap(sIcon)
        self.statusText.setText(sText)

        return

    def updateLineCount(self) -> None:
        """Update the line counter."""
        if self._tItem is None:
            iLine = 0
            iDist = 0
        else:
            cursor = self.docEditor.textCursor()
            iLine = cursor.blockNumber() + 1
            iDist = 100*iLine/self.docEditor._qDocument.blockCount()
        self.linesText.setText(
            self.tr("Line: {0} ({1})").format(f"{iLine:n}", f"{iDist:.0f} %")
        )
        return

    def updateCounts(self, wCount: int | None = None, cCount: int | None = None) -> None:
        """Select which word count display mode to use."""
        if self._docSelection:
            self._updateSelectionWordCounts(wCount, cCount)
        else:
            self._updateWordCounts()
        return

    ##
    #  Internal Functions
    ##

    def _updateWordCounts(self) -> None:
        """Update the word count for the whole document."""
        if self._tItem is None:
            wCount = 0
            wDiff = 0
        else:
            wCount = self._tItem.wordCount
            wDiff = wCount - self._tItem.initCount

        self.wordsText.setText(
            self.tr("Words: {0} ({1})").format(f"{wCount:n}", f"{wDiff:+n}")
        )

        byteSize = self.docEditor._qDocument.characterCount()
        self.wordsText.setToolTip(
            self.tr("Document size is {0} bytes").format(f"{byteSize:n}")
        )

        return

    def _updateSelectionWordCounts(self, wCount: int | None, cCount: int | None) -> None:
        """Update the word count for a selection."""
        if wCount is None or cCount is None:
            return
        self.wordsText.setText(
            self.tr("Words: {0} selected").format(f"{wCount:n}")
        )
        self.wordsText.setToolTip(
            self.tr("Character count: {0}").format(f"{cCount:n}")
        )
        return

# END Class GuiDocEditFooter
