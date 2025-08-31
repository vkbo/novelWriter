"""
novelWriter – GUI Document Editor
=================================

File History:
Created:   2018-09-29 [0.0.1]  GuiDocEditor
Created:   2019-04-22 [0.0.1]  BackgroundWordCounter
Created:   2019-09-29 [0.2.1]  GuiDocEditSearch
Created:   2020-04-25 [0.4.5]  GuiDocEditHeader
Rewritten: 2020-06-15 [0.9]    GuiDocEditSearch
Created:   2020-06-27 [0.10]   GuiDocEditFooter
Rewritten: 2020-10-07 [1.0b3]  BackgroundWordCounter
Created:   2023-11-06 [2.2b1]  MetaCompleter
Created:   2023-11-07 [2.2b1]  GuiDocToolBar
Extended:  2025-05-18 [2.7rc1] CommandCompleter

This file is a part of novelWriter
Copyright (C) 2018 Veronica Berglyd Olsen and novelWriter contributors

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
"""  # noqa
from __future__ import annotations

import bisect
import logging

from enum import Enum, IntFlag
from time import time

from PyQt6.QtCore import (
    QObject, QPoint, QRegularExpression, QRunnable, Qt, QTimer, pyqtSignal,
    pyqtSlot
)
from PyQt6.QtGui import (
    QAction, QCursor, QDragEnterEvent, QDragMoveEvent, QDropEvent, QKeyEvent,
    QKeySequence, QMouseEvent, QPalette, QPixmap, QResizeEvent, QShortcut,
    QTextBlock, QTextCursor, QTextDocument, QTextFormat, QTextOption
)
from PyQt6.QtWidgets import (
    QApplication, QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QMenu,
    QPlainTextEdit, QTextEdit, QToolBar, QVBoxLayout, QWidget
)

from novelwriter import CONFIG, SHARED
from novelwriter.common import (
    decodeMimeHandles, fontMatcher, minmax, qtAddAction, qtLambda, transferCase
)
from novelwriter.constants import (
    nwConst, nwKeyWords, nwLabels, nwShortcode, nwStats, nwUnicode, trStats
)
from novelwriter.core.document import NWDocument
from novelwriter.enum import (
    nwChange, nwComment, nwDocAction, nwDocInsert, nwDocMode, nwItemClass,
    nwItemType, nwVimMode
)
from novelwriter.extensions.configlayout import NColorLabel
from novelwriter.extensions.eventfilters import WheelEventFilter
from novelwriter.extensions.modified import NIconToggleButton, NIconToolButton
from novelwriter.gui.dochighlight import BLOCK_META, BLOCK_TITLE
from novelwriter.gui.editordocument import GuiTextDocument
from novelwriter.gui.theme import STYLES_MIN_TOOLBUTTON
from novelwriter.text.counting import standardCounter
from novelwriter.tools.lipsum import GuiLipsum
from novelwriter.types import (
    QtAlignCenterTop, QtAlignJustify, QtAlignLeft, QtAlignLeftTop,
    QtAlignRight, QtKeepAnchor, QtModCtrl, QtModNone, QtModShift, QtMouseLeft,
    QtMoveAnchor, QtMoveLeft, QtMoveRight, QtScrollAlwaysOff, QtScrollAsNeeded,
    QtTransparent
)

logger = logging.getLogger(__name__)


class _SelectAction(Enum):

    NO_DECISION    = 0
    KEEP_SELECTION = 1
    KEEP_POSITION  = 2
    MOVE_AFTER     = 3


class _TagAction(IntFlag):

    NONE   = 0b00
    FOLLOW = 0b01
    CREATE = 0b10


class GuiDocEditor(QPlainTextEdit):
    """Gui Widget: Main Document Editor."""

    __slots__ = (
        "_autoReplace", "_completer", "_doReplace", "_docChanged", "_docHandle", "_followTag1",
        "_followTag2", "_keyContext", "_lastActive", "_lastEdit", "_lastFind", "_nwDocument",
        "_nwItem", "_qDocument", "_timerDoc", "_timerSel", "_vpMargin", "_wCounterDoc",
        "_wCounterSel",
    )

    MOVE_KEYS = (
        Qt.Key.Key_Left, Qt.Key.Key_Right, Qt.Key.Key_Up, Qt.Key.Key_Down,
        Qt.Key.Key_PageUp, Qt.Key.Key_PageDown
    )
    ENTER_KEYS = (Qt.Key.Key_Return, Qt.Key.Key_Enter)

    # Custom Signals
    closeEditorRequest = pyqtSignal()
    docTextChanged = pyqtSignal(str, float)
    editedStatusChanged = pyqtSignal(bool)
    itemHandleChanged = pyqtSignal(str)
    loadDocumentTagRequest = pyqtSignal(str, Enum)
    openDocumentRequest = pyqtSignal(str, Enum, str, bool)
    requestNewNoteCreation = pyqtSignal(str, nwItemClass)
    requestNextDocument = pyqtSignal(str, bool)
    requestProjectItemRenamed = pyqtSignal(str, str)
    requestProjectItemSelected = pyqtSignal(str, bool)
    spellCheckStateChanged = pyqtSignal(bool)
    toggleFocusModeRequest = pyqtSignal()
    updateStatusMessage = pyqtSignal(str)

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)

        logger.debug("Create: GuiDocEditor")

        # Class Variables
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
        self._lineColor  = QtTransparent
        self._selection  = QTextEdit.ExtraSelection()

        # Auto-Replace
        self._autoReplace = TextAutoReplace()

        # Completer
        self._completer = CommandCompleter(self)
        self._completer.complete.connect(self._insertCompletion)

        # Create Custom Document
        self._qDocument = GuiTextDocument(self)
        self.setDocument(self._qDocument)

        # Connect Editor and Document Signals
        self._qDocument.contentsChange.connect(self._docChange)
        self.selectionChanged.connect(self._updateSelectedStatus)
        self.cursorPositionChanged.connect(self._cursorMoved)
        self.spellCheckStateChanged.connect(self._qDocument.setSpellCheckState)

        # Document Title
        self.docHeader = GuiDocEditHeader(self)
        self.docFooter = GuiDocEditFooter(self)
        self.docSearch = GuiDocEditSearch(self)
        self.docToolBar = GuiDocToolBar(self)

        # Connect Widget Signals
        self.docHeader.closeDocumentRequest.connect(self._closeCurrentDocument)
        self.docHeader.toggleToolBarRequest.connect(self._toggleToolBarVisibility)
        self.docToolBar.requestDocAction.connect(self.docAction)

        # Context Menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._openContextMenu)

        # Editor Settings
        self.setMinimumWidth(300)
        self.setAutoFillBackground(True)
        self.setFrameStyle(QFrame.Shape.NoFrame)
        self.setAcceptDrops(True)

        # Custom Shortcuts
        self._keyContext = QShortcut(self)
        self._keyContext.setKey("Ctrl+.")
        self._keyContext.setContext(Qt.ShortcutContext.WidgetShortcut)
        self._keyContext.activated.connect(self._openContextFromCursor)

        self._followTag1 = QShortcut(self)
        self._followTag1.setKey("Ctrl+Return")
        self._followTag1.setContext(Qt.ShortcutContext.WidgetShortcut)
        self._followTag1.activated.connect(self._processTag)

        self._followTag2 = QShortcut(self)
        self._followTag2.setKey("Ctrl+Enter")
        self._followTag2.setContext(Qt.ShortcutContext.WidgetShortcut)
        self._followTag2.activated.connect(self._processTag)

        # Set Up Document Word Counter
        self._timerDoc = QTimer(self)
        self._timerDoc.timeout.connect(self._runDocumentTasks)
        self._timerDoc.setInterval(5000)

        self._wCounterDoc = BackgroundWordCounter(self)
        self._wCounterDoc.setAutoDelete(False)
        self._wCounterDoc.signals.countsReady.connect(self._updateDocCounts)

        # Set Up Selection Word Counter
        self._timerSel = QTimer(self)
        self._timerSel.timeout.connect(self._runSelCounter)
        self._timerSel.setInterval(500)

        self._wCounterSel = BackgroundWordCounter(self, forSelection=True)
        self._wCounterSel.setAutoDelete(False)
        self._wCounterSel.signals.countsReady.connect(self._updateSelCounts)

        # Install Event Filter for Mouse Wheel
        self.wheelEventFilter = WheelEventFilter(self)
        self.installEventFilter(self.wheelEventFilter)

        # Function Mapping
        self.closeSearch = self.docSearch.closeSearch
        self.searchVisible = self.docSearch.isVisible
        self.changeFocusState = self.docHeader.changeFocusState

        # Vim state for vim mode
        self.vim = VimState()
        if CONFIG.vimModeEnabled:
            self.setVimMode(nwVimMode.NORMAL)

        # Finalise
        self.updateSyntaxColors()
        self.initEditor()

        logger.debug("Ready: GuiDocEditor")

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
        self._timerDoc.stop()
        self._timerSel.stop()

        self._docHandle  = None
        self._lastEdit   = 0.0
        self._lastActive = 0.0
        self._lastFind   = None
        self._doReplace  = False

        self.setDocumentChanged(False)
        self.docHeader.clearHeader()
        self.docFooter.setHandle(self._docHandle)
        self.docToolBar.setVisible(False)
        self.setExtraSelections([])

        self.itemHandleChanged.emit("")

    def updateTheme(self) -> None:
        """Update theme elements."""
        self.docSearch.updateTheme()
        self.docHeader.updateTheme()
        self.docFooter.updateTheme()
        self.docToolBar.updateTheme()

    def updateSyntaxColors(self) -> None:
        """Update the syntax highlighting theme."""
        syntax = SHARED.theme.syntaxTheme

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, syntax.back)
        palette.setColor(QPalette.ColorRole.Base, syntax.back)
        palette.setColor(QPalette.ColorRole.Text, syntax.text)
        self.setPalette(palette)

        if viewport := self.viewport():
            palette = viewport.palette()
            palette.setColor(QPalette.ColorRole.Base, syntax.back)
            palette.setColor(QPalette.ColorRole.Text, syntax.text)
            viewport.setPalette(palette)

        self.docHeader.matchColors()
        self.docFooter.matchColors()

        self._lineColor = syntax.line
        self._selection.format.setBackground(self._lineColor)
        self._selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)

    def initEditor(self) -> None:
        """Initialise or re-initialise the editor with the user's
        settings. This function is both called when the editor is
        created, and when the user changes the main editor preferences.
        """
        # Auto-Replace
        self._autoReplace.initSettings()
        self.docFooter.initSettings()

        # Reload spell check and dictionaries
        SHARED.updateSpellCheckLanguage()

        # Set the font. See issues #1862 and #1875.
        font = fontMatcher(CONFIG.textFont)
        self.setFont(font)
        self._qDocument.setDefaultFont(font)
        self.docHeader.updateFont()
        self.docFooter.updateFont()
        self.docSearch.updateFont()

        # Update highlighter settings
        self._qDocument.syntaxHighlighter.initHighlighter()

        # Set default text margins
        # Due to cursor visibility, a part of the margin must be
        # allocated to the document itself. See issue #1112.
        self._qDocument.setDocumentMargin(4)
        self._vpMargin = max(CONFIG.textMargin - 4, 0)
        self.setViewportMargins(self._vpMargin, self._vpMargin, self._vpMargin, self._vpMargin)

        # Also set the document text options for the document text flow
        options = QTextOption()
        if CONFIG.doJustify:
            options.setAlignment(QtAlignJustify)
        if CONFIG.showTabsNSpaces:
            options.setFlags(options.flags() | QTextOption.Flag.ShowTabsAndSpaces)
        if CONFIG.showLineEndings:
            options.setFlags(options.flags() | QTextOption.Flag.ShowLineAndParagraphSeparators)
        self._qDocument.setDefaultTextOption(options)

        # Scrolling
        self.setCenterOnScroll(CONFIG.scrollPastEnd)
        if CONFIG.hideVScroll:
            self.setVerticalScrollBarPolicy(QtScrollAlwaysOff)
        else:
            self.setVerticalScrollBarPolicy(QtScrollAsNeeded)

        if CONFIG.hideHScroll:
            self.setHorizontalScrollBarPolicy(QtScrollAlwaysOff)
        else:
            self.setHorizontalScrollBarPolicy(QtScrollAsNeeded)

        # Refresh sizes
        self.setTabStopDistance(CONFIG.tabWidth)
        self.setCursorWidth(CONFIG.cursorWidth)
        self.setExtraSelections([])
        self._cursorMoved()

        # If we have a document open, we should refresh it in case the
        # font changed, otherwise we just clear the editor entirely,
        # which makes it read only.
        if self._docHandle:
            self._qDocument.syntaxHighlighter.rehighlight()
            self.docHeader.setHandle(self._docHandle)
        else:
            self.clearEditor()

    def loadText(self, tHandle: str, tLine: int | None = None) -> bool:
        """Load text from a document into the editor. If we have an I/O
        error, we must handle this and clear the editor so that we don't
        risk overwriting the file if it exists. This can for instance
        happen if the file contains binary elements or an encoding that
        novelWriter does not support. If loading is successful, or the
        document is new (empty string), we set up the editor for editing
        the file.
        """
        self._nwDocument = SHARED.project.storage.getDocument(tHandle)
        self._nwItem = self._nwDocument.nwItem
        if not (self._nwItem and self._nwItem.itemType == nwItemType.FILE):
            logger.debug("Requested item '%s' is not a document", tHandle)
            self.clearEditor()
            return False

        if (text := self._nwDocument.readDocument()) is None:
            # There was an I/O error
            self.clearEditor()
            return False

        QApplication.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))
        self._docHandle = tHandle

        self._allowAutoReplace(False)
        self._qDocument.setTextContent(text, tHandle)
        self._allowAutoReplace(True)
        QApplication.processEvents()

        self._lastEdit = time()
        self._lastActive = time()
        self._runDocumentTasks()
        self._timerDoc.start()

        self.setReadOnly(False)
        self.updateDocMargins()

        if isinstance(tLine, int):
            self.setCursorLine(tLine)
        else:
            self.setCursorPosition(self._nwItem.cursorPos)

        self.docHeader.setHandle(tHandle)
        self.docFooter.setHandle(tHandle)

        # This is a hack to fix invisible cursor on an empty document
        if self._qDocument.characterCount() <= 1:
            self.setPlainText("\n")
            self.setPlainText("")
            self.setCursorPosition(0)

        QApplication.processEvents()
        self.setDocumentChanged(False)
        self._qDocument.clearUndoRedoStacks()
        self.docToolBar.setVisible(CONFIG.showEditToolBar)

        # Process State Changes
        SHARED.project.data.setLastHandle(tHandle, "editor")
        self.itemHandleChanged.emit(tHandle)

        # Finalise
        QApplication.restoreOverrideCursor()
        self.updateStatusMessage.emit(
            self.tr("Opened Document: {0}").format(self._nwItem.itemName)
        )

        return True

    def replaceText(self, text: str) -> None:
        """Replace the text of the current document with the provided
        text. This also clears undo history.
        """
        QApplication.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))
        self.setPlainText(text)
        self.updateDocMargins()
        self.setDocumentChanged(True)
        QApplication.restoreOverrideCursor()

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

        text = self.getText()
        cC, wC, pC = standardCounter(text)
        self._updateDocCounts(cC, wC, pC)

        if not self._nwDocument.writeDocument(text):
            saveOk = False
            if self._nwDocument.hashError and SHARED.question(self.tr(
                "This document has been changed outside of novelWriter "
                "while it was open. Overwrite the file on disk?"
            )):
                saveOk = self._nwDocument.writeDocument(text, forceWrite=True)

            if not saveOk:
                SHARED.error(
                    self.tr("Could not save document."),
                    info=self._nwDocument.getError()
                )

            return False

        self.setDocumentChanged(False)
        self.docTextChanged.emit(self._docHandle, self._lastEdit)
        SHARED.project.index.scanText(tHandle, text)

        self.updateStatusMessage.emit(self.tr("Saved Document: {0}").format(self._nwItem.itemName))

        return True

    def cursorIsVisible(self) -> bool:
        """Check if the cursor is visible in the editor."""
        viewport = self.viewport()
        height = viewport.height() if viewport else 0
        return 0 < self.cursorRect().top() and self.cursorRect().bottom() < height

    def ensureCursorVisibleNoCentre(self) -> None:
        """Ensure cursor is visible, but don't force it to centre."""
        if (viewport := self.viewport()) and (vBar := self.verticalScrollBar()):
            cT = self.cursorRect().top()
            cB = self.cursorRect().bottom()
            vH = viewport.height()
            if cT < 0:
                count = 0
                while self.cursorRect().top() < 0 and count < 100000:
                    vBar.setValue(vBar.value() - 1)
                    count += 1
            elif cB > vH:
                count = 0
                while self.cursorRect().bottom() > vH and count < 100000:
                    vBar.setValue(vBar.value() + 1)
                    count += 1
            QApplication.processEvents()

    def updateDocMargins(self) -> None:
        """Automatically adjust the margins so the text is centred if
        we have a text width set or we're in Focus Mode. Otherwise, just
        ensure the margins are set correctly.
        """
        wW = self.width()
        wH = self.height()

        vBar = self.verticalScrollBar()
        sW = vBar.width() if vBar and vBar.isVisible() else 0

        hBar = self.horizontalScrollBar()
        sH = hBar.height() if hBar and hBar.isVisible() else 0

        tM = self._vpMargin
        if CONFIG.textWidth > 0 or SHARED.focusMode:
            tW = CONFIG.getTextWidth(SHARED.focusMode)
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

    ##
    #  Getters
    ##

    def getText(self) -> str:
        """Get the text content of the current document. This method uses
        QTextDocument->toRawText instead of toPlainText. The former preserves
        non-breaking spaces, the latter does not. We still want to get rid of
        paragraph and line separators though.

        See: https://doc.qt.io/qt-6/qtextdocument.html#toPlainText
        """
        text = self._qDocument.toRawText()
        text = text.replace(nwUnicode.U_LSEP, "\n")  # Line separators
        return text.replace(nwUnicode.U_PSEP, "\n")  # Paragraph separators

    def getSelectedText(self) -> str:
        """Get currently selected text."""
        if (cursor := self.textCursor()).hasSelection():
            text = cursor.selectedText()
            text = text.replace(nwUnicode.U_LSEP, "\n")  # Line separators
            return text.replace(nwUnicode.U_PSEP, "\n")  # Paragraph separators
        return ""

    def getCursorPosition(self) -> int:
        """Find the cursor position in the document. If the editor has a
        selection, return the position of the end of the selection.
        """
        return self.textCursor().selectionEnd()

    ##
    #  Setters
    ##

    def setVimMode(self, mode: nwVimMode) -> None:
        """Change the vim mode."""
        if CONFIG.vimModeEnabled:
            if mode == nwVimMode.NORMAL:
                cursor = self.textCursor()
                cursor.clearSelection()
                self.setTextCursor(cursor)
            self.vim.setMode(mode)
            self._updateVimModeStatusBar(mode.name)

    def setDocumentChanged(self, state: bool) -> None:
        """Keep track of the document changed variable, and emit the
        document change signal.
        """
        if self._docChanged != state:
            logger.debug("Document changed status is '%s'", state)
            self._docChanged = state
            self.editedStatusChanged.emit(self._docChanged)

    def setCursorPosition(self, position: int) -> None:
        """Move the cursor to a given position in the document."""
        if (chars := self._qDocument.characterCount()) > 1 and isinstance(position, int):
            cursor = self.textCursor()
            cursor.setPosition(minmax(position, 0, chars-1))
            self.setTextCursor(cursor)
            self.centerCursor()

    def saveCursorPosition(self) -> None:
        """Save the cursor position to the current project item."""
        if self._nwItem is not None:
            cursPos = self.getCursorPosition()
            self._nwItem.setCursorPos(cursPos)

    def setCursorLine(self, line: int | None) -> None:
        """Move the cursor to a given line in the document."""
        if isinstance(line, int) and line > 0:
            block = self._qDocument.findBlockByNumber(line - 1)
            if block:
                self.setCursorPosition(block.position())
                logger.debug("Cursor moved to line %d", line)

    def setCursorSelection(self, start: int, length: int) -> None:
        """Make a text selection."""
        if start >= 0 and length > 0:
            cursor = self.textCursor()
            cursor.setPosition(start, QtMoveAnchor)
            cursor.setPosition(start + length, QtKeepAnchor)
            self.setTextCursor(cursor)

    ##
    #  Spell Checking
    ##

    def toggleSpellCheck(self, state: bool | None) -> None:
        """Toggle spell checking.

        This is the main spell check setting function, and this one
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

    def spellCheckDocument(self) -> None:
        """Rerun the highlighter to update spell checking status of the
        currently loaded text.
        """
        start = time()
        logger.debug("Running spell checker")
        QApplication.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))
        self._qDocument.syntaxHighlighter.rehighlight()
        QApplication.restoreOverrideCursor()
        logger.debug("Document highlighted in %.3f ms", 1000*(time() - start))
        self.updateStatusMessage.emit(self.tr("Spell check complete"))

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
        elif action == nwDocAction.MD_MARK:
            self._toggleFormat(2, "=")
        elif action == nwDocAction.S_QUOTE:
            self._wrapSelection(CONFIG.fmtSQuoteOpen, CONFIG.fmtSQuoteClose)
        elif action == nwDocAction.D_QUOTE:
            self._wrapSelection(CONFIG.fmtDQuoteOpen, CONFIG.fmtDQuoteClose)
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
        elif action == nwDocAction.BLOCK_HSC:
            self._formatBlock(nwDocAction.BLOCK_HSC)
        elif action == nwDocAction.REPL_SNG:
            self._replaceQuotes("'", CONFIG.fmtSQuoteOpen, CONFIG.fmtSQuoteClose)
        elif action == nwDocAction.REPL_DBL:
            self._replaceQuotes('"', CONFIG.fmtDQuoteOpen, CONFIG.fmtDQuoteClose)
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
        elif action == nwDocAction.SC_MARK:
            self._wrapSelection(nwShortcode.MARK_O, nwShortcode.MARK_C)
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
        return self.hasFocus() or self.isAncestorOf(QApplication.focusWidget())

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

    def insertText(self, insert: str | nwDocInsert) -> None:
        """Insert a specific type of text at the cursor position."""
        if self._docHandle is None:
            logger.error("No document open")
            return

        text = ""
        block = False
        after = False

        if isinstance(insert, str):
            text = insert
        elif isinstance(insert, nwDocInsert):
            if insert == nwDocInsert.QUOTE_LS:
                text = CONFIG.fmtSQuoteOpen
            elif insert == nwDocInsert.QUOTE_RS:
                text = CONFIG.fmtSQuoteClose
            elif insert == nwDocInsert.QUOTE_LD:
                text = CONFIG.fmtDQuoteOpen
            elif insert == nwDocInsert.QUOTE_RD:
                text = CONFIG.fmtDQuoteClose
            elif insert == nwDocInsert.SYNOPSIS:
                text = "%Synopsis: "
                block = True
                after = True
            elif insert == nwDocInsert.SHORT:
                text = "%Short: "
                block = True
                after = True
            elif insert == nwDocInsert.NEW_PAGE:
                text = "[newpage]"
                block = True
                after = False
            elif insert == nwDocInsert.VSPACE_S:
                text = "[vspace]"
                block = True
                after = False
            elif insert == nwDocInsert.VSPACE_M:
                text = "[vspace:2]"
                block = True
                after = False
            elif insert == nwDocInsert.LIPSUM:
                text = GuiLipsum.getLipsum(self)
                block = True
                after = False
            elif insert == nwDocInsert.FOOTNOTE:
                self._insertCommentStructure(nwComment.FOOTNOTE)
            elif insert == nwDocInsert.LINE_BRK:
                text = nwShortcode.BREAK

        if text:
            if block:
                self.insertNewBlock(text, defaultAfter=after)
            else:
                cursor = self.textCursor()
                cursor.beginEditBlock()
                cursor.insertText(text)
                cursor.endEditBlock()

        return

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

        if CONFIG.vimModeEnabled:
            self._handleVimKeyPress(event)
            return

        if self.docSearch.anyFocus() and event.key() in self.ENTER_KEYS:
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
            okMod = kMod in (QtModNone, QtModShift)

            okKey = event.key() not in self.MOVE_KEYS
            if nPos != cPos and okMod and okKey and (viewport := self.viewport()):
                mPos = CONFIG.autoScrollPos*0.01 * viewport.height()
                if cPos > mPos and (vBar := self.verticalScrollBar()):
                    vBar.setValue(vBar.value() + (1 if nPos > cPos else -1))
        else:
            super().keyPressEvent(event)

        return

    def _handleVimKeyPress(self, event: QKeyEvent) -> bool:
        """Handle key events for Vim mode.
        If vim mode is not enabled, it returns false and typing
        behaves as normal.
        """
        # --- INSERT mode, bypass ---
        if self.vim.getMode() == nwVimMode.INSERT:
            super().keyPressEvent(event)
            return True  # Normal typing

        # --- NORMAL mode, mode switching ---
        if event.text() == "i":
            self.setVimMode(nwVimMode.INSERT)
        elif event.text() == "I":
            cursor = self.textCursor()
            cursor.movePosition(cursor.MoveOperation.StartOfLine)
            self.setTextCursor(cursor)
            self.setVimMode(nwVimMode.INSERT)
            return True
        elif event.text() == "v":
            self.setVimMode(nwVimMode.VISUAL)
            cursor = self.textCursor()
            self._visualAnchor = cursor.position()
            cursor.movePosition(cursor.MoveOperation.Right, cursor.MoveMode.KeepAnchor, 1)
            self.setTextCursor(cursor)
            return True
        elif event.text() == "V":
            self.setVimMode(nwVimMode.VLINE)
            cursor = self.textCursor()
            self._visualAnchor = cursor.anchor()
            cursor.select(cursor.SelectionType.LineUnderCursor)
            self.setTextCursor(cursor)
            return True

        key = event.text()
        cursor = self.textCursor()

        # -- VISUAL mode PREFIX
        if self.vim.getMode() in (nwVimMode.VISUAL, nwVimMode.VLINE):
            if key in self.vim.VISUAL_PREFIX_KEYS:
                self.vim.pushCommandKey(key)
            else:
                self.vim.setCommand(key)
            if self.vim.command() in self.vim.VISUAL_PREFIX_KEYS:
                return True  # Leave command enqueued

        # --- VISUAL / VISUALLINE mode ---
        if self.vim.getMode() in (nwVimMode.VISUAL, nwVimMode.VLINE):
            if self.vim.command() in ("d", "x"):
                cursor.beginEditBlock()
                self.vim.yankToInternal(cursor.selectedText())
                cursor.removeSelectedText()
                cursor.endEditBlock()
                self.setTextCursor(cursor)
                self.setVimMode(nwVimMode.NORMAL)
                return True

            if self.vim.command() == "y":
                self.vim.yankToInternal(cursor.selectedText())
                cursor.clearSelection()
                self.setTextCursor(cursor)
                self.setVimMode(nwVimMode.NORMAL)
                return True

            # Handle motions (extend selection)
            move_mode = cursor.MoveMode.KeepAnchor
            if self.vim.command() == "h":
                cursor.movePosition(cursor.MoveOperation.Left, move_mode)
            elif self.vim.command() == "l":
                cursor.movePosition(cursor.MoveOperation.Right, move_mode)
            elif self.vim.command() == "j":
                cursor.movePosition(cursor.MoveOperation.Down, move_mode)
            elif self.vim.command() == "k":
                cursor.movePosition(cursor.MoveOperation.Up, move_mode)
            elif self.vim.command() == "$":
                cursor.movePosition(cursor.MoveOperation.EndOfLine, move_mode)
            elif self.vim.command() == "0":
                cursor.movePosition(cursor.MoveOperation.StartOfLine, move_mode)
            elif self.vim.command() == "gg":
                cursor.movePosition(cursor.MoveOperation.Start, move_mode)
            elif self.vim.command() == "G":
                cursor.movePosition(cursor.MoveOperation.End, move_mode)
            else:
                return True
            self.setTextCursor(cursor)
            return True

        # --- NORMAL mode, commands
        # -- NORMAL mode PREFIX
        if self.vim.getMode() is nwVimMode.NORMAL:
            if key in self.vim.PREFIX_KEYS:
                self.vim.pushCommandKey(key)
            else:
                self.vim.setCommand(key)
            if self.vim.command() in self.vim.PREFIX_KEYS:
                return True  # Leave command enqueued

        if self.vim.command() == "dd":
            cursor.beginEditBlock()
            cursor.select(cursor.SelectionType.LineUnderCursor)
            self.vim.yankToInternal(cursor.selectedText())
            cursor.removeSelectedText()
            cursor.endEditBlock()
            cursor.setPosition(cursor.selectionEnd())
            self.setTextCursor(cursor)
            self.vim.resetCommand()
            return True

        if self.vim.command() == "x":
            cursor.movePosition(cursor.MoveOperation.Right, cursor.MoveMode.KeepAnchor, 1)
            self.vim.yankToInternal(cursor.selectedText())
            cursor.removeSelectedText()
            self.setTextCursor(cursor)
            self.vim.resetCommand()
            return True

        if self.vim.command() == "gg":
            cursor.movePosition(cursor.MoveOperation.Start)
            self.setTextCursor(cursor)
            self.vim.resetCommand()
            return True

        if self.vim.command() == "G":
            cursor.movePosition(cursor.MoveOperation.End)
            self.setTextCursor(cursor)
            self.vim.resetCommand()
            return True

        if self.vim.command() == "yy":
            cursor.select(cursor.SelectionType.LineUnderCursor)
            self.vim.yankToInternal(cursor.selectedText())
            cursor.clearSelection()
            self.setTextCursor(cursor)
            self.vim.resetCommand()
            return True

        if self.vim.command() == "p":
            text = self.vim.pasteFromInternal()
            if text:
                cursor.beginEditBlock()
                cursor.movePosition(cursor.MoveOperation.EndOfLine)
                cursor.insertText("\n" + text)
                cursor.endEditBlock()
                self.setTextCursor(cursor)
            self.vim.resetCommand()
            return True

        if self.vim.command() == "P":
            text = self.vim.pasteFromInternal()
            if text:
                cursor.beginEditBlock()
                cursor.movePosition(cursor.MoveOperation.StartOfLine)
                cursor.insertText(text + "\n")
                cursor.endEditBlock()
                self.setTextCursor(cursor)
            self.vim.resetCommand()
            return True

        if self.vim.command() == "o":
            cursor.beginEditBlock()
            cursor.movePosition(cursor.MoveOperation.EndOfLine)
            cursor.insertText("\n")
            cursor.endEditBlock()
            self.setTextCursor(cursor)
            self.setVimMode(nwVimMode.INSERT)
            return True

        if self.vim.command() == "O":
            cursor.beginEditBlock()
            cursor.movePosition(cursor.MoveOperation.StartOfLine)
            cursor.insertText("\n")
            cursor.movePosition(cursor.MoveOperation.Up)
            cursor.endEditBlock()
            self.setTextCursor(cursor)
            self.setVimMode(nwVimMode.INSERT)

        if self.vim.command() == "$":
            cursor.movePosition(cursor.MoveOperation.EndOfLine)
            self.setTextCursor(cursor)
            self.vim.resetCommand()
            return True

        if self.vim.command() == "a":
            cursor.movePosition(cursor.MoveOperation.Right)
            self.setTextCursor(cursor)
            self.setVimMode(nwVimMode.INSERT)
            self.vim.resetCommand()
            return True

        if self.vim.command() == "A":
            cursor.movePosition(cursor.MoveOperation.EndOfLine)
            self.setTextCursor(cursor)
            self.setVimMode(nwVimMode.INSERT)
            self.vim.resetCommand()
            return True

        if self.vim.command() == "u":
            self.docAction(nwDocAction.UNDO)
            self.vim.resetCommand()
            return True

        # hjkl  (single-step navigation)
        if self.vim.command() == "h":
            cursor.movePosition(cursor.MoveOperation.Left)
        elif self.vim.command() == "j":
            cursor.movePosition(cursor.MoveOperation.Down)
        elif self.vim.command() == "k":
            cursor.movePosition(cursor.MoveOperation.Up)
        elif self.vim.command() == "l":
            cursor.movePosition(cursor.MoveOperation.Right)
        else:
            return True  # Normal mode, unmapped keys do nothing

        self.setTextCursor(cursor)
        self.vim.resetCommand()
        return True

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """Overload drag enter event to handle dragged items."""
        if (data := event.mimeData()) and data.hasFormat(nwConst.MIME_HANDLE):
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event: QDragMoveEvent) -> None:
        """Overload drag move event to handle dragged items."""
        if (data := event.mimeData()) and data.hasFormat(nwConst.MIME_HANDLE):
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event: QDropEvent) -> None:
        """Overload drop event to handle dragged items."""
        if (data := event.mimeData()) and data.hasFormat(nwConst.MIME_HANDLE):
            if handles := decodeMimeHandles(data):
                if SHARED.project.tree.checkType(handles[0], nwItemType.FILE):
                    self.openDocumentRequest.emit(handles[0], nwDocMode.EDIT, "", True)
        else:
            super().dropEvent(event)

    def focusNextPrevChild(self, _next: bool) -> bool:
        """Capture the focus request from the tab key on the text
        editor. If the editor has focus, we do not change focus and
        allow the editor to insert a tab. If the search bar has focus,
        we forward the call to the search object.
        """
        if self.hasFocus():
            return False
        elif self.docSearch.isVisible():
            return self.docSearch.cycleFocus()
        return True

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """If the mouse button is released and the control key is
        pressed, check if we're clicking on a tag, and trigger the
        follow tag function.
        """
        if event.modifiers() & QtModCtrl == QtModCtrl:
            cursor = self.cursorForPosition(event.pos())
            mData, mType = self._qDocument.metaDataAtPos(cursor.position())
            if mData and mType == "url":
                SHARED.openWebsite(mData)
            else:
                self._processTag(cursor)
        super().mouseReleaseEvent(event)

    def resizeEvent(self, event: QResizeEvent) -> None:
        """If the text editor is resized, we must make sure the document
        has its margins adjusted according to user preferences.
        """
        self.updateDocMargins()
        super().resizeEvent(event)

    ##
    #  Public Slots
    ##

    @pyqtSlot(str, Enum)
    def onProjectItemChanged(self, tHandle: str, change: nwChange) -> None:
        """Process project item change. Called when an item label is
        changed to check if the document title bar needs updating.
        """
        if tHandle == self._docHandle and change == nwChange.UPDATE:
            self.docHeader.setHandle(tHandle)
            self.docFooter.updateInfo()
            self.updateDocMargins()

    @pyqtSlot(str)
    def insertKeyWord(self, keyword: str) -> bool:
        """Insert a keyword in the text editor, at the cursor position.
        If the insert line is not blank, a new line is started.
        """
        if keyword not in nwKeyWords.VALID_KEYS:
            logger.error("Invalid keyword '%s'", keyword)
            return False
        logger.debug("Inserting keyword '%s'", keyword)
        return self.insertNewBlock(f"{keyword}: ")

    @pyqtSlot()
    def toggleSearch(self) -> None:
        """Toggle the visibility of the search box."""
        if self.searchVisible():
            self.closeSearch()
        else:
            self.beginSearch()

    @pyqtSlot(list, list)
    def updateChangedTags(self, updated: list[str], deleted: list[str]) -> None:
        """Tags have changed, so just in case we rehighlight them."""
        if updated or deleted:
            self._qDocument.syntaxHighlighter.rehighlightByType(BLOCK_META)

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

        if not self._timerDoc.isActive():
            self._timerDoc.start()

        if (block := self._qDocument.findBlock(pos)).isValid():
            text = block.text()
            if text and text[0] in "@%" and added + removed == 1:
                # Only run on single character changes, or it will trigger
                # at unwanted times when other changes are made to the document
                cursor = self.textCursor()
                bPos = cursor.positionInBlock()
                if bPos > 0 and (viewport := self.viewport()):
                    if text[0] == "@":
                        show = self._completer.updateMetaText(text, bPos)
                    else:
                        show = self._completer.updateCommentText(text, bPos)
                    if show:
                        point = self.cursorRect().bottomRight()
                        self._completer.move(viewport.mapToGlobal(point))
                        self._completer.show()
                    else:
                        self._completer.close()
            else:
                self._completer.close()

            if self._doReplace and added == 1:
                cursor = self.textCursor()
                if self._autoReplace.process(text, cursor):
                    self._qDocument.syntaxHighlighter.rehighlightBlock(cursor.block())

    @pyqtSlot()
    def _cursorMoved(self) -> None:
        """Triggered when the cursor moved in the editor."""
        self.docFooter.updateLineCount(self.textCursor())
        if CONFIG.lineHighlight:
            self._selection.cursor = self.textCursor()
            self._selection.cursor.clearSelection()
            self.setExtraSelections([self._selection])

    @pyqtSlot(int, int, str)
    def _insertCompletion(self, pos: int, length: int, text: str) -> None:
        """Insert choice from the completer menu."""
        cursor = self.textCursor()
        if (block := cursor.block()).isValid():
            check = pos + block.position()
            cursor.setPosition(check, QtMoveAnchor)
            cursor.setPosition(check + length, QtKeepAnchor)
            cursor.insertText(text)
            self._completer.hide()

    @pyqtSlot()
    def _openContextFromCursor(self) -> None:
        """Open the spell check context menu at the cursor."""
        self._openContextMenu(self.cursorRect().center())

    @pyqtSlot("QPoint")
    def _openContextMenu(self, pos: QPoint) -> None:
        """Open the editor context menu at a given coordinate."""
        uCursor = self.textCursor()
        pCursor = self.cursorForPosition(pos)
        pBlock = pCursor.block()

        ctxMenu = QMenu(self)
        ctxMenu.setObjectName("ContextMenu")
        if pBlock.userState() == BLOCK_TITLE:
            action = qtAddAction(ctxMenu, self.tr("Set as Document Name"))
            action.triggered.connect(qtLambda(self._emitRenameItem, pBlock))

        # URL
        (mData, mType) = self._qDocument.metaDataAtPos(pCursor.position())
        if mData and mType == "url":
            action = qtAddAction(ctxMenu, self.tr("Open URL"))
            action.triggered.connect(qtLambda(SHARED.openWebsite, mData))
            ctxMenu.addSeparator()

        # Follow
        status = self._processTag(cursor=pCursor, follow=False)
        if status & _TagAction.FOLLOW:
            action = qtAddAction(ctxMenu, self.tr("Follow Tag"))
            action.triggered.connect(qtLambda(self._processTag, cursor=pCursor, follow=True))
            ctxMenu.addSeparator()
        elif status & _TagAction.CREATE:
            action = qtAddAction(ctxMenu, self.tr("Create Note for Tag"))
            action.triggered.connect(qtLambda(self._processTag, cursor=pCursor, create=True))
            ctxMenu.addSeparator()

        # Cut, Copy and Paste
        if uCursor.hasSelection():
            action = qtAddAction(ctxMenu, self.tr("Cut"))
            action.triggered.connect(qtLambda(self.docAction, nwDocAction.CUT))
            action = qtAddAction(ctxMenu, self.tr("Copy"))
            action.triggered.connect(qtLambda(self.docAction, nwDocAction.COPY))

        action = qtAddAction(ctxMenu, self.tr("Paste"))
        action.triggered.connect(qtLambda(self.docAction, nwDocAction.PASTE))
        ctxMenu.addSeparator()

        # Selections
        action = qtAddAction(ctxMenu, self.tr("Select All"))
        action.triggered.connect(qtLambda(self.docAction, nwDocAction.SEL_ALL))
        action = qtAddAction(ctxMenu, self.tr("Select Word"))
        action.triggered.connect(qtLambda(
            self._makePosSelection, QTextCursor.SelectionType.WordUnderCursor, pos,
        ))
        action = qtAddAction(ctxMenu, self.tr("Select Paragraph"))
        action.triggered.connect(qtLambda(
            self._makePosSelection, QTextCursor.SelectionType.BlockUnderCursor, pos
        ))

        # Spell Checking
        if SHARED.project.data.spellCheck:
            word, offset, suggest = self._qDocument.spellErrorAtPos(pCursor.position())
            if word and offset >= 0:
                logger.debug("Word '%s' is misspelled", word)
                block = pCursor.block()
                sCursor = self.textCursor()
                sCursor.setPosition(block.position() + offset)
                sCursor.movePosition(QtMoveRight, QtKeepAnchor, len(word))
                if suggest:
                    ctxMenu.addSeparator()
                    qtAddAction(ctxMenu, self.tr("Spelling Suggestion(s)"))
                    for option in suggest[:15]:
                        action = qtAddAction(ctxMenu, f"{nwUnicode.U_ENDASH} {option}")
                        action.triggered.connect(qtLambda(self._correctWord, sCursor, option))
                else:
                    trNone = self.tr("No Suggestions")
                    qtAddAction(ctxMenu, f"{nwUnicode.U_ENDASH} {trNone}")

                ctxMenu.addSeparator()
                action = qtAddAction(ctxMenu, self.tr("Ignore Word"))
                action.triggered.connect(qtLambda(self._addWord, word, block, False))
                action = qtAddAction(ctxMenu, self.tr("Add Word to Dictionary"))
                action.triggered.connect(qtLambda(self._addWord, word, block, True))

        # Execute the context menu
        if viewport := self.viewport():
            ctxMenu.exec(viewport.mapToGlobal(pos))

        ctxMenu.setParent(None)

    @pyqtSlot()
    def _runDocumentTasks(self) -> None:
        """Run timer document tasks."""
        if self._docHandle is None:
            return

        if time() - self._lastEdit < 25.0:
            logger.debug("Running document tasks")
            if not self._wCounterDoc.isRunning():
                SHARED.runInThreadPool(self._wCounterDoc)

            self.docHeader.setOutline({
                block.blockNumber(): block.text()
                for block in self._qDocument.iterBlockByType(BLOCK_TITLE, maxCount=30)
            })

            if self._docChanged:
                self.docTextChanged.emit(self._docHandle, self._lastEdit)

        return

    @pyqtSlot(int, int, int)
    def _updateDocCounts(self, cCount: int, wCount: int, pCount: int) -> None:
        """Process the word counter's finished signal."""
        if self._docHandle and self._nwItem:
            logger.debug("Updating word count")
            mCount = cCount if CONFIG.useCharCount else wCount
            needsRefresh = mCount != self._nwItem.mainCount
            self._nwItem.setCharCount(cCount)
            self._nwItem.setWordCount(wCount)
            self._nwItem.setParaCount(pCount)
            if needsRefresh:
                self._nwItem.notifyToRefresh()
                if not self.textCursor().hasSelection():
                    # Selection counter should take precedence (#2155)
                    self.docFooter.updateMainCount(mCount, False)

    @pyqtSlot()
    def _updateSelectedStatus(self) -> None:
        """Process user change in text selection. Forward this
        information to the footer, and start the selection word counter.
        """
        if self.textCursor().hasSelection():
            if not self._timerSel.isActive():
                self._timerSel.start()
        else:
            self._timerSel.stop()
            self.docFooter.updateMainCount(0, False)

    @pyqtSlot()
    def _updateVimModeStatusBar(self, modeName: str) -> None:
        if CONFIG.vimModeEnabled:
            self.docFooter.updateVimModeStatusBar(modeName)

    @pyqtSlot()
    def _runSelCounter(self) -> None:
        """Update the selection word count."""
        if self._docHandle:
            if self._wCounterSel.isRunning():
                logger.debug("Selection word counter is busy")
                return
            SHARED.runInThreadPool(self._wCounterSel)
        return

    @pyqtSlot(int, int, int)
    def _updateSelCounts(self, cCount: int, wCount: int, pCount: int) -> None:
        """Update the counts on the counter's finished signal."""
        if self._docHandle and self._nwItem:
            self.docFooter.updateMainCount(cCount if CONFIG.useCharCount else wCount, True)
            self._timerSel.stop()

    @pyqtSlot()
    def _closeCurrentDocument(self) -> None:
        """Close the document. Forwarded to the main Gui."""
        self.closeEditorRequest.emit()
        self.docToolBar.setVisible(False)

    @pyqtSlot()
    def _toggleToolBarVisibility(self) -> None:
        """Toggle the visibility of the tool bar."""
        state = not self.docToolBar.isVisible()
        self.docToolBar.setVisible(state)
        CONFIG.showEditToolBar = state

    ##
    #  Search & Replace
    ##

    def beginSearch(self) -> None:
        """Set the selected text as the search text."""
        self.docSearch.setSearchText(self.getSelectedText() or None)
        resS, _ = self.findAllOccurences()
        self.docSearch.setResultCount(None, len(resS))

    def beginReplace(self) -> None:
        """Initialise the search box and reset the replace text box."""
        self.beginSearch()
        self.docSearch.setReplaceText("")
        self.updateDocMargins()

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

        prevFocus = QApplication.focusWidget() or self
        resS, resE = self.findAllOccurences()
        if len(resS) == 0 and self._docHandle:
            self.docSearch.setResultCount(0, 0)
            self._lastFind = None
            if CONFIG.searchNextFile and not goBack:
                self.requestNextDocument.emit(self._docHandle, CONFIG.searchLoop)
                QApplication.processEvents()
                self.beginSearch()
                prevFocus.setFocus()
            return

        cursor = self.textCursor()
        resIdx = bisect.bisect_left(resS, cursor.position())

        doLoop = CONFIG.searchLoop
        maxIdx = len(resS) - 1

        if goBack:
            resIdx -= 2

        if resIdx < 0:
            resIdx = maxIdx if doLoop else 0

        if resIdx > maxIdx and self._docHandle:
            if CONFIG.searchNextFile and not goBack:
                self.requestNextDocument.emit(self._docHandle, CONFIG.searchLoop)
                QApplication.processEvents()
                self.beginSearch()
                prevFocus.setFocus()
                return
            else:
                resIdx = 0 if doLoop else maxIdx

        cursor.setPosition(resS[resIdx], QtMoveAnchor)
        cursor.setPosition(resE[resIdx], QtKeepAnchor)
        self.setTextCursor(cursor)

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
        if CONFIG.searchCase:
            findOpt |= QTextDocument.FindFlag.FindCaseSensitively
        if CONFIG.searchWord:
            findOpt |= QTextDocument.FindFlag.FindWholeWords

        searchFor = self.docSearch.getSearchObject()
        cursor.setPosition(0)
        self.setTextCursor(cursor)

        # Search up to a maximum of MAX_SEARCH_RESULT, and make sure
        # certain special searches like a regex search for .* don't loop
        # infinitely
        while self.find(searchFor, findOpt) and len(resE) <= nwConst.MAX_SEARCH_RESULT:
            cursor = self.textCursor()
            if cursor.hasSelection():
                resS.append(cursor.selectionStart())
                resE.append(cursor.selectionEnd())
            else:
                logger.warning("The search returned an empty result")
                break

        if hasSelection:
            cursor.setPosition(origA, QtMoveAnchor)
            cursor.setPosition(origB, QtKeepAnchor)
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

        if CONFIG.searchMatchCap:
            replWith = transferCase(cursor.selectedText(), replWith)

        # Make sure the selected text was selected by an actual find
        # call, and not the user.
        if self._lastFind == (cursor.selectionStart(), cursor.selectionEnd()):
            cursor.beginEditBlock()
            cursor.removeSelectedText()
            cursor.insertText(replWith)
            cursor.endEditBlock()
            cursor.setPosition(cursor.selectionEnd())
            self.setTextCursor(cursor)
            logger.debug(
                "Replaced occurrence of '%s' with '%s' on line %d",
                searchFor, replWith, cursor.blockNumber() + 1
            )

        self.findNext()

        return

    ##
    #  Internal Functions : Text Manipulation
    ##

    def _toggleFormat(self, fLen: int, fChar: str) -> None:
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
        if posS == posE and self._qDocument.characterAt(posO - 1) == fChar:
            logger.warning("Format repetition, cancelling action")
            cursor.clearSelection()
            cursor.setPosition(posO)
            self.setTextCursor(cursor)
            return

        blockS = self._qDocument.findBlock(posS)
        blockE = self._qDocument.findBlock(posE)
        if blockS != blockE:
            posE = blockS.position() + blockS.length() - 1
            cursor.clearSelection()
            cursor.setPosition(posS, QtMoveAnchor)
            cursor.setPosition(posE, QtKeepAnchor)
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
            cursor.beginEditBlock()
            cursor.setPosition(posS)
            for _ in range(fLen):
                cursor.deletePreviousChar()
            cursor.setPosition(posE)
            for _ in range(fLen):
                cursor.deletePreviousChar()
            cursor.endEditBlock()

            if select != _SelectAction.KEEP_SELECTION:
                cursor.clearSelection()
                cursor.setPosition(posO - fLen)
                self.setTextCursor(cursor)

        else:
            self._wrapSelection(fChar*fLen, pos=posO, select=select)

        return

    def _wrapSelection(
        self, before: str, after: str | None = None, pos: int | None = None,
        select: _SelectAction = _SelectAction.NO_DECISION
    ) -> None:
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
            cursor.setPosition(posS + len(before), QtMoveAnchor)
            cursor.setPosition(posE + len(before), QtKeepAnchor)
        elif select == _SelectAction.KEEP_POSITION:
            cursor.setPosition(posO + len(before))

        self.setTextCursor(cursor)

    def _replaceQuotes(self, sQuote: str, oQuote: str, cQuote: str) -> None:
        """Replace all straight quotes in the selected text."""
        cursor = self.textCursor()
        if not cursor.hasSelection():
            SHARED.error(self.tr("Please select some text before calling replace quotes."))
            return

        posS = cursor.selectionStart()
        posE = cursor.selectionEnd()
        closeCheck = (" ", "\n", nwUnicode.U_LSEP, nwUnicode.U_PSEP)

        self._allowAutoReplace(False)
        for posC in range(posS, posE+1):
            cursor.setPosition(posC)
            cursor.movePosition(QtMoveLeft, QtKeepAnchor, 2)
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
                cursor.movePosition(QtMoveLeft, QtKeepAnchor, 1)
                cursor.insertText(oQuote)
                cursor.endEditBlock()
            else:
                cursor.beginEditBlock()
                cursor.movePosition(QtMoveLeft, QtKeepAnchor, 1)
                cursor.insertText(cQuote)
                cursor.endEditBlock()

        self._allowAutoReplace(True)

        return

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
        elif text.startswith("###! "):
            temp = text[5:]
            offset = 5
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
        elif action == nwDocAction.BLOCK_HSC:
            text = f"###! {temp}"
            offset -= 5
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
        cursor.movePosition(QtMoveRight, QtKeepAnchor, rE-rS)
        cursor.insertText(cleanText.rstrip() + "\n")
        cursor.endEditBlock()

    def _insertCommentStructure(self, style: nwComment) -> None:
        """Insert a shortcut/comment combo."""
        if self._docHandle and style == nwComment.FOOTNOTE:
            self.saveText()  # Index must be up to date
            key = SHARED.project.index.newCommentKey(self._docHandle, style)
            code = nwShortcode.COMMENT_STYLES[nwComment.FOOTNOTE]

            cursor = self.textCursor()
            block = cursor.block()
            text = block.text().rstrip()
            if not text or text.startswith("@"):
                logger.error("Invalid footnote location")
                return

            cursor.beginEditBlock()
            cursor.insertText(code.format(key))
            cursor.setPosition(block.position() + block.length() - 1)
            cursor.insertBlock()
            cursor.insertBlock()
            cursor.insertText(f"%Footnote.{key}: ")
            cursor.endEditBlock()

            self.setTextCursor(cursor)

        return

    ##
    #  Internal Functions
    ##

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

    def _addWord(self, word: str, block: QTextBlock, save: bool) -> None:
        """Slot for the spell check context menu triggered when the user
        wants to add a word to the project dictionary.
        """
        logger.debug("Added '%s' to project dictionary, %s", word, "saved" if save else "unsaved")
        SHARED.spelling.addWord(word, save=save)
        self._qDocument.syntaxHighlighter.rehighlightBlock(block)

    def _processTag(
        self, cursor: QTextCursor | None = None, follow: bool = True, create: bool = False
    ) -> _TagAction:
        """Activated by Ctrl+Enter. Checks that we're in a block
        starting with '@'. We then find the tag under the cursor and
        check that it is not the tag itself. If all this is fine, we
        have a tag and can tell the document viewer to try and find and
        load the file where the tag is defined.
        """
        if cursor is None:
            cursor = self.textCursor()

        status = _TagAction.NONE
        block = cursor.block()
        text = block.text()
        if len(text) == 0:
            return status

        if text.startswith("@") and self._docHandle:

            isGood, tBits, tPos = SHARED.project.index.scanThis(text)
            if (
                not isGood
                or not tBits
                or (key := tBits[0]) == nwKeyWords.TAG_KEY
                or key not in nwKeyWords.VALID_KEYS
            ):
                return status

            tag = ""
            exist = False
            cPos = cursor.selectionStart() - block.position()
            tExist = SHARED.project.index.checkThese(tBits, self._docHandle)
            for sTag, sPos, sExist in zip(
                reversed(tBits), reversed(tPos), reversed(tExist), strict=False
            ):
                if cPos >= sPos:
                    # The cursor is between the start of two tags
                    if cPos <= sPos + len(sTag):
                        # The cursor is inside or at the edge of the tag
                        tag = sTag
                        exist = sExist
                    break

            if not tag or tag.startswith("@"):
                # The keyword cannot be looked up, so we ignore that
                return status

            if not exist and key in nwKeyWords.CAN_CREATE:
                # Must only be set if we have a tag selected
                status |= _TagAction.CREATE

            if exist:
                status |= _TagAction.FOLLOW

            if follow and exist:
                logger.debug("Attempting to follow tag '%s'", tag)
                self.loadDocumentTagRequest.emit(tag, nwDocMode.VIEW)
            elif create and not exist:
                if SHARED.question(self.tr(
                    "Do you want to create a new project note for the tag '{0}'?"
                ).format(tag)):
                    itemClass = nwKeyWords.KEY_CLASS.get(tBits[0], nwItemClass.NO_CLASS)
                    self.requestNewNoteCreation.emit(tag, itemClass)

        return status

    def _emitRenameItem(self, block: QTextBlock) -> None:
        """Emit a signal to request an item be renamed."""
        if self._docHandle:
            text = block.text().lstrip("#").lstrip("!").strip()
            self.requestProjectItemRenamed.emit(self._docHandle, text)

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
                cOne = str(self._qDocument.characterAt(sPos))
                cTwo = str(self._qDocument.characterAt(sPos - 1))
                if not (cOne.isalnum() or (cOne in apos and cTwo.isalnum())):
                    sPos += 1
                    break

            # Scan forward
            ePos = cPos
            for i in range(bPos + bLen - cPos):
                ePos = cPos + i
                cOne = str(self._qDocument.characterAt(ePos))
                cTwo = str(self._qDocument.characterAt(ePos + 1))
                if not (cOne.isalnum() or (cOne in apos and cTwo.isalnum())):
                    break

            if ePos - sPos <= 0:
                # No selection possible
                return cursor

            cursor.clearSelection()
            cursor.setPosition(sPos, QtMoveAnchor)
            cursor.setPosition(ePos, QtKeepAnchor)

            self.setTextCursor(cursor)

        return cursor

    def _makeSelection(
        self, mode: QTextCursor.SelectionType, cursor: QTextCursor | None = None
    ) -> None:
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
                cursor.setPosition(posS+1, QtMoveAnchor)
                cursor.setPosition(posE, QtKeepAnchor)

        self.setTextCursor(cursor)

    def _makePosSelection(self, mode: QTextCursor.SelectionType, pos: QPoint) -> None:
        """Select text based on selection mode, but first move cursor."""
        cursor = self.cursorForPosition(pos)
        self.setTextCursor(cursor)
        self._makeSelection(mode)

    def _allowAutoReplace(self, state: bool) -> None:
        """Enable/disable the auto-replace feature temporarily."""
        if state:
            self._doReplace = CONFIG.doReplace
        else:
            self._doReplace = False


class CommandCompleter(QMenu):
    """GuiWidget: Command Completer Menu.

    This is a context menu with options populated from the user's
    defined tags and keys. It also helps to type the meta data keyword
    on a new line starting with @ or %. The update functions should be
    called on every keystroke on a line starting with @ or %.
    """

    complete = pyqtSignal(int, int, str)

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)

    def updateMetaText(self, text: str, pos: int) -> bool:
        """Update the menu options based on the line of text."""
        self.clear()
        kw, sep, _ = text.partition(":")
        if pos <= len(kw):
            offset = 0
            length = len(kw.rstrip())
            suffix = "" if sep else ":"
            options = sorted(filter(
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
            options = sorted(filter(
                lambda x: lookup in x.lower(), SHARED.project.index.getKeyWordTags(kw.strip())
            ))[:15]

        if not options:
            return False

        for value in options:
            rep = value + suffix
            action = qtAddAction(self, value)
            action.triggered.connect(qtLambda(self._emitComplete, offset, length, rep))

        return True

    def updateCommentText(self, text: str, pos: int) -> bool:
        """Update the menu options based on the line of text."""
        self.clear()
        cmd, sep, _ = text.partition(":")
        if pos <= len(cmd):
            clean = text[1:].lstrip()[:6].lower()
            if clean[:6] == "story.":
                pre, _, key = cmd.partition(".")
                offset = len(pre) + 1
                length = len(key)
                suffix = "" if sep else ": "
                options = sorted(filter(
                    lambda x: x.startswith(key.rstrip()),
                    SHARED.project.index.getStoryKeys(),
                ))
            elif clean[:5] == "note.":
                pre, _, key = cmd.partition(".")
                offset = len(pre) + 1
                length = len(key)
                suffix = "" if sep else ": "
                options = sorted(filter(
                    lambda x: x.startswith(key.rstrip()),
                    SHARED.project.index.getNoteKeys(),
                ))
            elif pos < 12:
                offset = 0
                length = len(cmd.rstrip())
                suffix = ""
                options = list(filter(
                    lambda x: x.startswith(cmd.rstrip()),
                    ["%Synopsis: ", "%Short: ", "%Story", "%Note"],
                ))
            else:
                return False

            if options:
                for value in options:
                    rep = value + suffix
                    action = qtAddAction(self, rep.rstrip(":. "))
                    action.triggered.connect(qtLambda(self._emitComplete, offset, length, rep))
                return True

        return False

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

    ##
    #  Internal Functions
    ##

    def _emitComplete(self, pos: int, length: int, value: str) -> None:
        """Emit the signal to indicate a selection has been made."""
        self.complete.emit(pos, length, value)


class BackgroundWordCounter(QRunnable):
    """The Off-GUI Thread Word Counter.

    A runnable for the word counter to be run in the thread pool off the
    main GUI thread.
    """

    def __init__(self, docEditor: GuiDocEditor, forSelection: bool = False) -> None:
        super().__init__()
        self._docEditor = docEditor
        self._forSelection = forSelection
        self._isRunning = False
        self.signals = BackgroundWordCounterSignals()

    def isRunning(self) -> bool:
        """Return True if the word counter is already running."""
        return self._isRunning

    @pyqtSlot()
    def run(self) -> None:
        """Overloaded run function for the word counter, forwarding the
        call to the function that does the actual counting.
        """
        self._isRunning = True
        if self._forSelection:
            text = self._docEditor.getSelectedText()
        else:
            text = self._docEditor.getText()

        cC, wC, pC = standardCounter(text)
        self.signals.countsReady.emit(cC, wC, pC)
        self._isRunning = False


class BackgroundWordCounterSignals(QObject):
    """The QRunnable cannot emit a signal, so we need a simple QObject
    to hold the word counter signal.
    """

    countsReady = pyqtSignal(int, int, int)


class TextAutoReplace:
    """Encapsulates the editor auto replace feature."""

    __slots__ = (
        "_doPadAfter", "_doPadBefore", "_padAfter", "_padBefore", "_padChar",
        "_quoteDC", "_quoteDO", "_quoteSC", "_quoteSO", "_replaceDQuote",
        "_replaceDash", "_replaceDots", "_replaceSQuote",
    )

    def __init__(self) -> None:
        self.initSettings()

    def initSettings(self) -> None:
        """Initialise the auto-replace settings from config."""
        self._quoteSO = CONFIG.fmtSQuoteOpen
        self._quoteSC = CONFIG.fmtSQuoteClose
        self._quoteDO = CONFIG.fmtDQuoteOpen
        self._quoteDC = CONFIG.fmtDQuoteClose

        self._replaceSQuote = CONFIG.doReplaceSQuote
        self._replaceDQuote = CONFIG.doReplaceDQuote
        self._replaceDash   = CONFIG.doReplaceDash
        self._replaceDots   = CONFIG.doReplaceDots

        self._padChar     = nwUnicode.U_THNBSP if CONFIG.fmtPadThin else nwUnicode.U_NBSP
        self._padBefore   = CONFIG.fmtPadBefore
        self._padAfter    = CONFIG.fmtPadAfter
        self._doPadBefore = bool(CONFIG.fmtPadBefore)
        self._doPadAfter  = bool(CONFIG.fmtPadAfter)

    def process(self, text: str, cursor: QTextCursor) -> bool:
        """Auto-replace text elements based on main configuration.
        Returns True if anything was changed.
        """
        aPos = cursor.position()
        bPos = cursor.positionInBlock()
        block = cursor.block()
        length = block.length() - 1
        if length < 1 or bPos-1 > length:
            return False

        cursor.movePosition(QtMoveLeft, QtKeepAnchor, min(4, bPos))
        last = cursor.selectedText()
        delete, insert = self._determine(last, bPos)

        check = insert
        if self._doPadBefore and check in self._padBefore:
            if not (check == ":" and length > 1 and text[0] == "@"):
                delete = max(delete, 1)
                chkPos = len(last) - delete - 1
                if chkPos >= 0 and last[chkPos].isspace():
                    # Strip existing space before inserting a new (#1061)
                    delete += 1
                insert = self._padChar + insert

        if self._doPadAfter and check in self._padAfter:
            if not (check == ":" and length > 1 and text[0] == "@"):
                delete = max(delete, 1)
                insert = insert + self._padChar

        if delete > 0:
            cursor.setPosition(aPos)
            cursor.movePosition(QtMoveLeft, QtKeepAnchor, delete)
            cursor.insertText(insert)
            return True

        return False

    def _determine(self, text: str, pos: int) -> tuple[int, str]:
        """Determine what to replace, if anything."""
        t1 = text[-1:]
        t2 = text[-2:]
        t3 = text[-3:]
        t4 = text[-4:]

        if self._replaceDQuote and t1 == '"':
            # Process Double Quote
            if pos == 1:
                return 1, self._quoteDO
            elif t2[:1].isspace() and t2.endswith('"'):
                return 1, self._quoteDO
            elif pos == 2 and t2 == '>"':
                return 1, self._quoteDO
            elif pos == 3 and t3 == '>>"':
                return 1, self._quoteDO
            elif pos == 2 and t2 == '_"':
                return 1, self._quoteDO
            elif t3[:1].isspace() and t3.endswith('_"'):
                return 1, self._quoteDO
            elif pos == 3 and t3 in ('**"', '=="', '~~"'):
                return 1, self._quoteDO
            elif t4[:1].isspace() and t4.endswith(('**"', '=="', '~~"')):
                return 1, self._quoteDO
            else:
                return 1, self._quoteDC

        if self._replaceSQuote and t1 == "'":
            # Process Single Quote
            if pos == 1:
                return 1, self._quoteSO
            elif t2[:1].isspace() and t2.endswith("'"):
                return 1, self._quoteSO
            elif pos == 2 and t2 == ">'":
                return 1, self._quoteSO
            elif pos == 3 and t3 == ">>'":
                return 1, self._quoteSO
            elif pos == 2 and t2 == "_'":
                return 1, self._quoteSO
            elif t3[:1].isspace() and t3.endswith("_'"):
                return 1, self._quoteSO
            elif pos == 3 and t3 in ("**'", "=='", "~~'"):
                return 1, self._quoteSO
            elif t4[:1].isspace() and t4.endswith(("**'", "=='", "~~'")):
                return 1, self._quoteSO
            else:
                return 1, self._quoteSC

        if self._replaceDash and t1 == "-":
            # Process Dashes
            if t4 == "----":
                return 4, "\u2015"  # Horizontal bar
            elif t3 == "---":
                return 3, "\u2014"  # Long dash
            elif t2 == "--":
                return 2, "\u2013"  # Short dash
            elif t2 == "\u2013-":
                return 2, "\u2014"  # Long dash
            elif t2 == "\u2014-":
                return 2, "\u2015"  # Horizontal bar

        if self._replaceDots and t3 == "...":
            # Process Dots
            return 3, "\u2026"  # Ellipsis

        if t1 == "\u2028":  # Line separator
            # This resolves issue #1150
            return 1, "\u2029"  # Paragraph separator

        return 0, t1


class GuiDocToolBar(QWidget):
    """The Formatting and Options Fold Out Menu.

    Only used by DocEditor, and is opened by the first button in the
    header.
    """

    requestDocAction = pyqtSignal(nwDocAction)

    def __init__(self, docEditor: GuiDocEditor) -> None:
        super().__init__(parent=docEditor)

        logger.debug("Create: GuiDocToolBar")

        iSz = SHARED.theme.baseIconSize
        self.setContentsMargins(0, 0, 0, 0)

        # General Buttons
        # ===============

        self.tbBoldMD = NIconToolButton(self, iSz)
        self.tbBoldMD.setToolTip(self.tr("Markdown Bold"))
        self.tbBoldMD.clicked.connect(
            qtLambda(self.requestDocAction.emit, nwDocAction.MD_BOLD)
        )

        self.tbItalicMD = NIconToolButton(self, iSz)
        self.tbItalicMD.setToolTip(self.tr("Markdown Italic"))
        self.tbItalicMD.clicked.connect(
            qtLambda(self.requestDocAction.emit, nwDocAction.MD_ITALIC)
        )

        self.tbStrikeMD = NIconToolButton(self, iSz)
        self.tbStrikeMD.setToolTip(self.tr("Markdown Strikethrough"))
        self.tbStrikeMD.clicked.connect(
            qtLambda(self.requestDocAction.emit, nwDocAction.MD_STRIKE)
        )

        self.tbMarkMD = NIconToolButton(self, iSz)
        self.tbMarkMD.setToolTip(self.tr("Markdown Highlight"))
        self.tbMarkMD.clicked.connect(
            qtLambda(self.requestDocAction.emit, nwDocAction.MD_MARK)
        )

        self.tbBold = NIconToolButton(self, iSz)
        self.tbBold.setToolTip(self.tr("Shortcode Bold"))
        self.tbBold.clicked.connect(
            qtLambda(self.requestDocAction.emit, nwDocAction.SC_BOLD)
        )

        self.tbItalic = NIconToolButton(self, iSz)
        self.tbItalic.setToolTip(self.tr("Shortcode Italic"))
        self.tbItalic.clicked.connect(
            qtLambda(self.requestDocAction.emit, nwDocAction.SC_ITALIC)
        )

        self.tbStrike = NIconToolButton(self, iSz)
        self.tbStrike.setToolTip(self.tr("Shortcode Strikethrough"))
        self.tbStrike.clicked.connect(
            qtLambda(self.requestDocAction.emit, nwDocAction.SC_STRIKE)
        )

        self.tbUnderline = NIconToolButton(self, iSz)
        self.tbUnderline.setToolTip(self.tr("Shortcode Underline"))
        self.tbUnderline.clicked.connect(
            qtLambda(self.requestDocAction.emit, nwDocAction.SC_ULINE)
        )

        self.tbMark = NIconToolButton(self, iSz)
        self.tbMark.setToolTip(self.tr("Shortcode Highlight"))
        self.tbMark.clicked.connect(
            qtLambda(self.requestDocAction.emit, nwDocAction.SC_MARK)
        )

        self.tbSuperscript = NIconToolButton(self, iSz)
        self.tbSuperscript.setToolTip(self.tr("Shortcode Superscript"))
        self.tbSuperscript.clicked.connect(
            qtLambda(self.requestDocAction.emit, nwDocAction.SC_SUP)
        )

        self.tbSubscript = NIconToolButton(self, iSz)
        self.tbSubscript.setToolTip(self.tr("Shortcode Subscript"))
        self.tbSubscript.clicked.connect(
            qtLambda(self.requestDocAction.emit, nwDocAction.SC_SUB)
        )

        # Assemble
        # ========

        self.outerBox = QVBoxLayout()
        self.outerBox.addWidget(self.tbBoldMD)
        self.outerBox.addWidget(self.tbItalicMD)
        self.outerBox.addWidget(self.tbStrikeMD)
        self.outerBox.addWidget(self.tbMarkMD)
        self.outerBox.addSpacing(4)
        self.outerBox.addWidget(self.tbBold)
        self.outerBox.addWidget(self.tbItalic)
        self.outerBox.addWidget(self.tbStrike)
        self.outerBox.addWidget(self.tbUnderline)
        self.outerBox.addWidget(self.tbMark)
        self.outerBox.addWidget(self.tbSuperscript)
        self.outerBox.addWidget(self.tbSubscript)
        self.outerBox.setContentsMargins(4, 4, 4, 4)
        self.outerBox.setSpacing(4)

        self.setLayout(self.outerBox)
        self.updateTheme()

        # Starts as Invisible
        self.setVisible(False)

        logger.debug("Ready: GuiDocToolBar")

    def updateTheme(self) -> None:
        """Initialise GUI elements that depend on specific settings."""
        syntax = SHARED.theme.syntaxTheme

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, syntax.back)
        palette.setColor(QPalette.ColorRole.WindowText, syntax.text)
        palette.setColor(QPalette.ColorRole.Text, syntax.text)
        self.setPalette(palette)

        self.tbBoldMD.setThemeIcon("fmt_bold", "orange")
        self.tbItalicMD.setThemeIcon("fmt_italic", "orange")
        self.tbStrikeMD.setThemeIcon("fmt_strike", "orange")
        self.tbMarkMD.setThemeIcon("fmt_mark", "orange")
        self.tbBold.setThemeIcon("fmt_bold")
        self.tbItalic.setThemeIcon("fmt_italic")
        self.tbStrike.setThemeIcon("fmt_strike")
        self.tbUnderline.setThemeIcon("fmt_underline")
        self.tbMark.setThemeIcon("fmt_mark")
        self.tbSuperscript.setThemeIcon("fmt_superscript")
        self.tbSubscript.setThemeIcon("fmt_subscript")


class GuiDocEditSearch(QFrame):
    """The Embedded Document Search/Replace Feature.

    Only used by DocEditor, and is at a fixed position in the
    QTextEdit's viewport.
    """

    def __init__(self, docEditor: GuiDocEditor) -> None:
        super().__init__(parent=docEditor)

        logger.debug("Create: GuiDocEditSearch")

        self.docEditor = docEditor

        iSz = SHARED.theme.baseIconSize

        self.setContentsMargins(0, 0, 0, 0)
        self.setAutoFillBackground(True)
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Plain)

        self.mainBox = QGridLayout(self)
        self.setLayout(self.mainBox)

        # Text Boxes
        # ==========

        self.searchBox = QLineEdit(self)
        self.searchBox.setPlaceholderText(self.tr("Search for"))
        self.searchBox.returnPressed.connect(self._doSearch)

        self.replaceBox = QLineEdit(self)
        self.replaceBox.setPlaceholderText(self.tr("Replace with"))
        self.replaceBox.returnPressed.connect(self._doReplace)

        self.searchOpt = QToolBar(self)
        self.searchOpt.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.searchOpt.setIconSize(iSz)
        self.searchOpt.setContentsMargins(0, 0, 0, 0)

        self.searchLabel = QLabel(self.tr("Search"), self)
        self.searchLabel.setIndent(6)

        self.resultLabel = QLabel("?/?", self)

        self.toggleCase = QAction(self.tr("Case Sensitive"), self)
        self.toggleCase.setCheckable(True)
        self.toggleCase.setChecked(CONFIG.searchCase)
        self.toggleCase.toggled.connect(self._doToggleCase)
        self.searchOpt.addAction(self.toggleCase)

        self.toggleWord = QAction(self.tr("Whole Words Only"), self)
        self.toggleWord.setCheckable(True)
        self.toggleWord.setChecked(CONFIG.searchWord)
        self.toggleWord.toggled.connect(self._doToggleWord)
        self.searchOpt.addAction(self.toggleWord)

        self.toggleRegEx = QAction(self.tr("RegEx Mode"), self)
        self.toggleRegEx.setCheckable(True)
        self.toggleRegEx.setChecked(CONFIG.searchRegEx)
        self.toggleRegEx.toggled.connect(self._doToggleRegEx)
        self.searchOpt.addAction(self.toggleRegEx)

        self.toggleLoop = QAction(self.tr("Loop Search"), self)
        self.toggleLoop.setCheckable(True)
        self.toggleLoop.setChecked(CONFIG.searchLoop)
        self.toggleLoop.toggled.connect(self._doToggleLoop)
        self.searchOpt.addAction(self.toggleLoop)

        self.toggleProject = QAction(self.tr("Search Next File"), self)
        self.toggleProject.setCheckable(True)
        self.toggleProject.setChecked(CONFIG.searchNextFile)
        self.toggleProject.toggled.connect(self._doToggleProject)
        self.searchOpt.addAction(self.toggleProject)

        self.searchOpt.addSeparator()

        self.toggleMatchCap = QAction(self.tr("Preserve Case"), self)
        self.toggleMatchCap.setCheckable(True)
        self.toggleMatchCap.setChecked(CONFIG.searchMatchCap)
        self.toggleMatchCap.toggled.connect(self._doToggleMatchCap)
        self.searchOpt.addAction(self.toggleMatchCap)

        self.searchOpt.addSeparator()

        self.cancelSearch = QAction(self.tr("Close Search"), self)
        self.cancelSearch.triggered.connect(self.closeSearch)
        self.searchOpt.addAction(self.cancelSearch)

        # Buttons
        # =======

        self.showReplace = NIconToggleButton(self, iSz, "unfold")
        self.showReplace.toggled.connect(self._doToggleReplace)

        self.searchButton = NIconToolButton(self, iSz)
        self.searchButton.setToolTip(self.tr("Find in current document"))
        self.searchButton.clicked.connect(self._doSearch)

        self.replaceButton = NIconToolButton(self, iSz)
        self.replaceButton.setToolTip(self.tr("Find and replace in current document"))
        self.replaceButton.clicked.connect(self._doReplace)

        self.mainBox.addWidget(self.searchLabel,   0, 0, 1, 2, QtAlignLeft)
        self.mainBox.addWidget(self.searchOpt,     0, 2, 1, 3, QtAlignRight)
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
        self.mainBox.setSpacing(2)
        self.mainBox.setContentsMargins(6, 6, 6, 6)

        self.searchBox.setFixedWidth(200)
        self.replaceBox.setFixedWidth(200)
        self.replaceBox.setVisible(False)
        self.replaceButton.setVisible(False)
        self.adjustSize()

        self.updateFont()
        self.updateTheme()

        logger.debug("Ready: GuiDocEditSearch")

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

    def getSearchObject(self) -> str | QRegularExpression:
        """Return the current search text either as text or as a regular
        expression object.
        """
        text = self.searchBox.text()
        if CONFIG.searchRegEx:
            rxOpt = QRegularExpression.PatternOption.UseUnicodePropertiesOption
            if not CONFIG.searchCase:
                rxOpt |= QRegularExpression.PatternOption.CaseInsensitiveOption
            regEx = QRegularExpression(text, rxOpt)
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
        if CONFIG.searchRegEx:
            self._alertSearchValid(True)

    def setReplaceText(self, text: str) -> None:
        """Set the replace text."""
        self.showReplace.setChecked(True)
        self.replaceBox.setFocus()
        self.replaceBox.setText(text)

    def setResultCount(self, currRes: int | None, resCount: int | None) -> None:
        """Set the count values for the current search."""
        lim = nwConst.MAX_SEARCH_RESULT
        numCount = f"{lim:n}+" if (resCount or 0) > lim else f"{resCount:n}"
        sCurrRes = "?" if currRes is None else str(currRes)
        sResCount = "?" if resCount is None else numCount
        minWidth = SHARED.theme.getTextWidth(
            f"{sResCount}//{sResCount}", SHARED.theme.guiFontSmall
        )
        self.resultLabel.setText(f"{sCurrRes}/{sResCount}")
        self.resultLabel.setMinimumWidth(minWidth)
        self.adjustSize()
        self.docEditor.updateDocMargins()

    ##
    #  Methods
    ##

    def updateFont(self) -> None:
        """Update the font settings."""
        self.setFont(SHARED.theme.guiFont)
        self.searchBox.setFont(SHARED.theme.guiFontSmall)
        self.replaceBox.setFont(SHARED.theme.guiFontSmall)
        self.searchLabel.setFont(SHARED.theme.guiFontSmall)
        self.resultLabel.setFont(SHARED.theme.guiFontSmall)
        self.resultLabel.setMinimumWidth(
            SHARED.theme.getTextWidth("?/?", SHARED.theme.guiFontSmall)
        )

    def updateTheme(self) -> None:
        """Update theme elements."""
        palette = QApplication.palette()

        self.setPalette(palette)
        self.searchBox.setPalette(palette)
        self.replaceBox.setPalette(palette)

        # Set icons
        self.toggleCase.setIcon(SHARED.theme.getIcon("search_case"))
        self.toggleWord.setIcon(SHARED.theme.getIcon("search_word"))
        self.toggleRegEx.setIcon(SHARED.theme.getIcon("search_regex"))
        self.toggleLoop.setIcon(SHARED.theme.getIcon("search_loop"))
        self.toggleProject.setIcon(SHARED.theme.getIcon("search_project"))
        self.toggleMatchCap.setIcon(SHARED.theme.getIcon("search_preserve"))
        self.cancelSearch.setIcon(SHARED.theme.getIcon("search_cancel"))
        self.searchButton.setThemeIcon("search", "green")
        self.replaceButton.setThemeIcon("search_replace", "green")

        # Set stylesheets
        self.searchOpt.setStyleSheet("QToolBar {padding: 0;}")
        self.showReplace.setStyleSheet("QToolButton {border: none; background: transparent;}")

    def cycleFocus(self) -> bool:
        """Cycle focus on tab key press. This just alternates focus
        between the two input boxes, if the replace box is visible.
        """
        if self.searchBox.hasFocus():
            self.replaceBox.setFocus()
            return True
        elif self.replaceBox.hasFocus():
            self.searchBox.setFocus()
            return True
        return False

    def anyFocus(self) -> bool:
        """Return True if any of the input boxes have focus."""
        return self.hasFocus() or self.isAncestorOf(QApplication.focusWidget())

    ##
    #  Public Slots
    ##

    @pyqtSlot()
    def closeSearch(self) -> None:
        """Close the search box."""
        self.showReplace.setChecked(False)
        self.setVisible(False)
        self.docEditor.updateDocMargins()
        self.docEditor.setFocus()

    ##
    #  Private Slots
    ##

    @pyqtSlot()
    def _doSearch(self) -> None:
        """Call the search action function for the document editor."""
        self.docEditor.findNext(goBack=(QApplication.keyboardModifiers() == QtModShift))

    @pyqtSlot()
    def _doReplace(self) -> None:
        """Call the replace action function for the document editor."""
        self.docEditor.replaceNext()

    @pyqtSlot(bool)
    def _doToggleReplace(self, state: bool) -> None:
        """Toggle the show/hide of the replace box."""
        self.replaceBox.setVisible(state)
        self.replaceButton.setVisible(state)
        self.adjustSize()
        self.docEditor.updateDocMargins()

    @pyqtSlot(bool)
    def _doToggleCase(self, state: bool) -> None:
        """Enable/disable case sensitive mode."""
        CONFIG.searchCase = state

    @pyqtSlot(bool)
    def _doToggleWord(self, state: bool) -> None:
        """Enable/disable whole word search mode."""
        CONFIG.searchWord = state

    @pyqtSlot(bool)
    def _doToggleRegEx(self, state: bool) -> None:
        """Enable/disable regular expression search mode."""
        CONFIG.searchRegEx = state

    @pyqtSlot(bool)
    def _doToggleLoop(self, state: bool) -> None:
        """Enable/disable looping the search."""
        CONFIG.searchLoop = state

    @pyqtSlot(bool)
    def _doToggleProject(self, state: bool) -> None:
        """Enable/disable continuing search in next project file."""
        CONFIG.searchNextFile = state

    @pyqtSlot(bool)
    def _doToggleMatchCap(self, state: bool) -> None:
        """Enable/disable preserving capitalisation when replacing."""
        CONFIG.searchMatchCap = state

    ##
    #  Internal Functions
    ##

    def _alertSearchValid(self, isValid: bool) -> None:
        """Highlight the search box to indicate the search string is or
        isn't valid. Take the colour from the replace box.
        """
        palette = self.replaceBox.palette()
        palette.setColor(
            QPalette.ColorRole.Text,
            palette.text().color() if isValid else SHARED.theme.errorText
        )
        self.searchBox.setPalette(palette)


class GuiDocEditHeader(QWidget):
    """The Embedded Document Header.

    Only used by DocEditor, and is at a fixed position in the
    QTextEdit's viewport.
    """

    closeDocumentRequest = pyqtSignal()
    toggleToolBarRequest = pyqtSignal()

    def __init__(self, docEditor: GuiDocEditor) -> None:
        super().__init__(parent=docEditor)

        logger.debug("Create: GuiDocEditHeader")

        self.docEditor = docEditor

        self._docHandle = None
        self._docOutline: dict[int, str] = {}

        iPx = SHARED.theme.baseIconHeight
        iSz = SHARED.theme.baseIconSize

        # Main Widget Settings
        self.setAutoFillBackground(True)

        # Title Label
        self.itemTitle = NColorLabel("", self, faded=SHARED.theme.fadedText)
        self.itemTitle.setMargin(0)
        self.itemTitle.setContentsMargins(0, 0, 0, 0)
        self.itemTitle.setAutoFillBackground(True)
        self.itemTitle.setAlignment(QtAlignCenterTop)
        self.itemTitle.setFixedHeight(iPx)

        # Other Widgets
        self.outlineMenu = QMenu(self)

        # Buttons
        self.tbButton = NIconToolButton(self, iSz)
        self.tbButton.setVisible(False)
        self.tbButton.setToolTip(self.tr("Toggle Tool Bar"))
        self.tbButton.clicked.connect(qtLambda(self.toggleToolBarRequest.emit))

        self.outlineButton = NIconToolButton(self, iSz)
        self.outlineButton.setVisible(False)
        self.outlineButton.setToolTip(self.tr("Outline"))
        self.outlineButton.setMenu(self.outlineMenu)

        self.searchButton = NIconToolButton(self, iSz)
        self.searchButton.setVisible(False)
        self.searchButton.setToolTip(self.tr("Search"))
        self.searchButton.clicked.connect(self.docEditor.toggleSearch)

        self.minmaxButton = NIconToolButton(self, iSz)
        self.minmaxButton.setVisible(False)
        self.minmaxButton.setToolTip(self.tr("Toggle Focus Mode"))
        self.minmaxButton.clicked.connect(qtLambda(self.docEditor.toggleFocusModeRequest.emit))

        self.closeButton = NIconToolButton(self, iSz)
        self.closeButton.setVisible(False)
        self.closeButton.setToolTip(self.tr("Close"))
        self.closeButton.clicked.connect(self._closeDocument)

        # Assemble Layout
        self.outerBox = QHBoxLayout()
        self.outerBox.addWidget(self.tbButton, 0)
        self.outerBox.addWidget(self.outlineButton, 0)
        self.outerBox.addWidget(self.searchButton, 0)
        self.outerBox.addSpacing(4)
        self.outerBox.addWidget(self.itemTitle, 1)
        self.outerBox.addSpacing(4)
        self.outerBox.addSpacing(iPx)
        self.outerBox.addWidget(self.minmaxButton, 0)
        self.outerBox.addWidget(self.closeButton, 0)
        self.outerBox.setContentsMargins(4, 4, 4, 4)
        self.outerBox.setSpacing(0)

        self.setLayout(self.outerBox)

        # Other Signals
        SHARED.focusModeChanged.connect(self._focusModeChanged)

        # Fix Margins and Size
        # This is needed for high DPI systems. See issue #499.
        self.setContentsMargins(0, 0, 0, 0)
        self.setMinimumHeight(iPx + 8)

        self.updateFont()
        self.updateTheme()

        logger.debug("Ready: GuiDocEditHeader")

    ##
    #  Methods
    ##

    def clearHeader(self) -> None:
        """Clear the header."""
        self._docHandle = None
        self._docOutline = {}

        self.itemTitle.setText("")
        self.outlineMenu.clear()
        self.tbButton.setVisible(False)
        self.outlineButton.setVisible(False)
        self.searchButton.setVisible(False)
        self.closeButton.setVisible(False)
        self.minmaxButton.setVisible(False)

    def setOutline(self, data: dict[int, str]) -> None:
        """Set the document outline dataset."""
        if data != self._docOutline:
            tStart = time()
            self.outlineMenu.clear()
            for number, text in data.items():
                action = qtAddAction(self.outlineMenu, text)
                action.triggered.connect(qtLambda(self._gotoBlock, number))
            self._docOutline = data
            logger.debug("Document outline updated in %.3f ms", 1000*(time() - tStart))

    def updateFont(self) -> None:
        """Update the font settings."""
        self.setFont(SHARED.theme.guiFont)
        self.itemTitle.setFont(SHARED.theme.guiFontSmall)

    def updateTheme(self) -> None:
        """Update theme elements."""
        self.tbButton.setThemeIcon("fmt_toolbar", "blue")
        self.outlineButton.setThemeIcon("list", "blue")
        self.searchButton.setThemeIcon("search", "blue")
        self.minmaxButton.setThemeIcon("maximise", "blue")
        self.closeButton.setThemeIcon("close", "red")

        buttonStyle = SHARED.theme.getStyleSheet(STYLES_MIN_TOOLBUTTON)
        self.tbButton.setStyleSheet(buttonStyle)
        self.outlineButton.setStyleSheet(buttonStyle)
        self.searchButton.setStyleSheet(buttonStyle)
        self.minmaxButton.setStyleSheet(buttonStyle)
        self.closeButton.setStyleSheet(buttonStyle)

        self.matchColors()

    def matchColors(self) -> None:
        """Update the colours of the widget to match those of the syntax
        theme rather than the main GUI.
        """
        syntax = SHARED.theme.syntaxTheme
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, syntax.back)
        palette.setColor(QPalette.ColorRole.WindowText, syntax.text)
        palette.setColor(QPalette.ColorRole.Text, syntax.text)
        self.setPalette(palette)
        self.itemTitle.setTextColors(
            color=palette.windowText().color(), faded=SHARED.theme.fadedText
        )

    def changeFocusState(self, state: bool) -> None:
        """Toggle focus state."""
        self.itemTitle.setColorState(state)

    def setHandle(self, tHandle: str) -> None:
        """Set the document title from the handle, or alternatively, set
        the whole document path within the project.
        """
        self._docHandle = tHandle

        if CONFIG.showFullPath:
            self.itemTitle.setText(f"  {nwUnicode.U_RSAQUO}  ".join(reversed(
                [name for name in SHARED.project.tree.itemPath(tHandle, asName=True)]
            )))
        else:
            self.itemTitle.setText(i.itemName if (i := SHARED.project.tree[tHandle]) else "")

        self.tbButton.setVisible(True)
        self.searchButton.setVisible(True)
        self.outlineButton.setVisible(True)
        self.closeButton.setVisible(True)
        self.minmaxButton.setVisible(True)

    ##
    #  Private Slots
    ##

    @pyqtSlot()
    def _closeDocument(self) -> None:
        """Trigger the close editor on the main window."""
        self.clearHeader()
        self.closeDocumentRequest.emit()

    @pyqtSlot(int)
    def _gotoBlock(self, blockNumber: int) -> None:
        """Move cursor to a specific heading."""
        self.docEditor.setCursorLine(blockNumber + 1)

    @pyqtSlot(bool)
    def _focusModeChanged(self, focusMode: bool) -> None:
        """Update minimise/maximise icon of the Focus Mode button."""
        self.minmaxButton.setThemeIcon("minimise" if focusMode else "maximise", "blue")

    ##
    #  Events
    ##

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Capture a click on the title and ensure that the item is
        selected in the project tree.
        """
        if event.button() == QtMouseLeft:
            self.docEditor.requestProjectItemSelected.emit(self._docHandle or "", True)


class GuiDocEditFooter(QWidget):
    """The Embedded Document Footer.

    Only used by DocEditor, and is at a fixed position in the
    QTextEdit's viewport.
    """

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)

        logger.debug("Create: GuiDocEditFooter")

        self._tItem = None
        self._docHandle = None

        iPx = round(0.9*SHARED.theme.baseIconHeight)
        fPx = int(0.9*SHARED.theme.fontPixelSize)

        # Cached Translations
        self.initSettings()
        self._trLineCount = self.tr("Line: {0} ({1})")
        self._trSelectCount = self.tr("Selected: {0}")

        # Main Widget Settings
        self.setContentsMargins(0, 0, 0, 0)
        self.setAutoFillBackground(True)

        # Status
        self.statusIcon = QLabel("", self)
        self.statusIcon.setFixedHeight(iPx)
        self.statusIcon.setAlignment(QtAlignLeftTop)

        self.statusText = QLabel("", self)
        self.statusText.setAutoFillBackground(True)
        self.statusText.setFixedHeight(fPx)
        self.statusText.setAlignment(QtAlignLeftTop)

        # Lines
        self.linesIcon = QLabel("", self)
        self.linesIcon.setFixedHeight(iPx)
        self.linesIcon.setAlignment(QtAlignLeftTop)

        self.linesText = QLabel("", self)
        self.linesText.setAutoFillBackground(True)
        self.linesText.setFixedHeight(fPx)
        self.linesText.setAlignment(QtAlignLeftTop)

        # Words
        self.wordsIcon = QLabel("", self)
        self.wordsIcon.setFixedHeight(iPx)
        self.wordsIcon.setAlignment(QtAlignLeftTop)

        self.wordsText = QLabel("", self)
        self.wordsText.setAutoFillBackground(True)
        self.wordsText.setFixedHeight(fPx)
        self.wordsText.setAlignment(QtAlignLeftTop)

        # Vim mode status bar
        self.vimStatus = QLabel("", self)
        self.vimStatus.setAutoFillBackground(True)
        self.vimStatus.setFixedHeight(fPx)
        self.vimStatus.setAlignment(QtAlignLeftTop)

        # Assemble Layout
        self.outerBox = QHBoxLayout()
        self.outerBox.setSpacing(4)
        self.outerBox.addWidget(self.statusIcon)
        self.outerBox.addWidget(self.statusText)
        self.outerBox.addStretch(1)
        self.outerBox.addSpacing(2)  # TODO when not maximized spacing issues
        self.outerBox.addWidget(self.vimStatus)
        self.outerBox.addWidget(self.linesIcon)
        self.outerBox.addWidget(self.linesText)
        self.outerBox.addSpacing(6)
        self.outerBox.addWidget(self.wordsIcon)
        self.outerBox.addWidget(self.wordsText)
        self.outerBox.setContentsMargins(8, 8, 8, 8)

        self.setLayout(self.outerBox)

        # Fix Margins and Size
        # This is needed for high DPI systems. See issue #499.
        self.setContentsMargins(0, 0, 0, 0)
        self.setMinimumHeight(fPx + 16)

        # Fix the Colours
        self.updateFont()
        self.updateTheme()

        # Initialise Info
        self.updateMainCount(0, False)

        logger.debug("Ready: GuiDocEditFooter")

    ##
    #  Methods
    ##

    def initSettings(self) -> None:
        """Apply user settings."""
        self._trMainCount = trStats(nwLabels.STATS_DISPLAY[
            nwStats.CHARS if CONFIG.useCharCount else nwStats.WORDS
        ])

    def updateFont(self) -> None:
        """Update the font settings."""
        self.setFont(SHARED.theme.guiFont)
        self.statusText.setFont(SHARED.theme.guiFontSmall)
        self.linesText.setFont(SHARED.theme.guiFontSmall)
        self.wordsText.setFont(SHARED.theme.guiFontSmall)
        self.vimStatus.setFont(SHARED.theme.guiFontSmall)

    def updateTheme(self) -> None:
        """Update theme elements."""
        iPx = round(0.9*SHARED.theme.baseIconHeight)
        self.linesIcon.setPixmap(SHARED.theme.getPixmap("lines", (iPx, iPx)))
        self.wordsIcon.setPixmap(SHARED.theme.getPixmap("stats", (iPx, iPx)))
        self.matchColors()

    def matchColors(self) -> None:
        """Update the colours of the widget to match those of the syntax
        theme rather than the main GUI.
        """
        syntax = SHARED.theme.syntaxTheme

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, syntax.back)
        palette.setColor(QPalette.ColorRole.WindowText, syntax.text)
        palette.setColor(QPalette.ColorRole.Text, syntax.text)

        self.setPalette(palette)
        self.statusText.setPalette(palette)
        self.linesText.setPalette(palette)
        self.wordsText.setPalette(palette)

    def setHandle(self, tHandle: str | None) -> None:
        """Set the handle that will populate the footer's data."""
        self._docHandle = tHandle
        if self._docHandle is None:
            logger.debug("No handle set, so clearing the editor footer")
            self._tItem = None
        else:
            self._tItem = SHARED.project.tree[self._docHandle]

        self.updateInfo()
        self.updateMainCount(0, False)

    def updateInfo(self) -> None:
        """Update the content of text labels."""
        if self._tItem is None:
            sIcon = QPixmap()
            sText = ""
        else:
            iPx = round(0.9*SHARED.theme.baseIconHeight)
            status, icon = self._tItem.getImportStatus()
            sIcon = icon.pixmap(iPx, iPx)
            sText = f"{status} / {self._tItem.describeMe()}"

        self.statusIcon.setPixmap(sIcon)
        self.statusText.setText(sText)

    def updateLineCount(self, cursor: QTextCursor) -> None:
        """Update the line and document position counter."""
        if document := cursor.document():
            cPos = cursor.position() + 1
            cLine = cursor.blockNumber() + 1
            cCount = max(document.characterCount(), 1)
            self.linesText.setText(
                self._trLineCount.format(f"{cLine:n}", f"{100*cPos//cCount:d} %")
            )

    def updateMainCount(self, count: int, selection: bool) -> None:
        """Update main counter information."""
        if selection and count:
            text = self._trSelectCount.format(f"{count:n}")
        elif self._tItem:
            count = self._tItem.mainCount
            diff = count - self._tItem.initCount
            text = self._trMainCount.format(f"{count:n}", f"{diff:+n}")
        else:
            text = self._trMainCount.format("0", "+0")
        self.wordsText.setText(text)

    def updateVimModeStatusBar(self, modeName: str) -> None:
        """Update the vim Mode status information."""
        self.vimStatus.setText(self.tr(modeName))


class VimState:
    """Minimal Vim state machine."""

    __slots__ = (
        "PREFIX_KEYS",
        "VISUAL_PREFIX_KEYS",
        "_internalClipboard",
        "_mode",
        "_normalCommand",
        "_visualCommand",
    )

    def __init__(self) -> None:
        self.PREFIX_KEYS = ["d", "y", "g"]
        self.VISUAL_PREFIX_KEYS = ["g"]
        self._mode: nwVimMode = nwVimMode.NORMAL
        self._normalCommand: str = ""
        self._visualCommand: str = ""
        self._internalClipboard = ""

    def resetCommand(self) -> None:
        """Reset internal vim command."""
        self._normalCommand = ""
        self._visualCommand = ""

    def setMode(self, new_mode: nwVimMode) -> None:
        """Switch vim mode."""
        self._mode = new_mode
        self.resetCommand()

    def getMode(self) -> nwVimMode:
        """Return current vim mode."""
        return self._mode

    def pushCommandKey(self, key: str) -> None:
        """Push key to the current command building stack."""
        if self._mode is nwVimMode.NORMAL:
            self._normalCommand += key
        elif self._mode in (nwVimMode.VISUAL, nwVimMode.VLINE):
            self._visualCommand += key

    def setCommand(self, key: str) -> None:
        """Set the state of the current vim command."""
        if self._mode is nwVimMode.NORMAL:
            self._normalCommand = key
        elif self._mode in (nwVimMode.VISUAL, nwVimMode.VLINE):
            self._visualCommand = key

    def command(self) -> str:
        """Return the current vim command."""
        if self._mode in (nwVimMode.VISUAL, nwVimMode.VLINE):
            return self._visualCommand
        else:
            return self._normalCommand

    def yankToInternal(self, text: str) -> None:
        """Put text into internal vim buffer."""
        self._internalClipboard = text

    def pasteFromInternal(self) -> str:
        """Paste from the internal vim clipboard."""
        return self._internalClipboard
