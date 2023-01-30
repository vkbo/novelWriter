"""
novelWriter – GUI Document Editor
=================================
GUI classes for the main document editor

File History:
Created:   2018-09-29 [0.0.1] GuiDocEditor
Created:   2019-04-22 [0.0.1] BackgroundWordCounter
Created:   2019-09-29 [0.2.1] GuiDocEditSearch
Created:   2020-04-25 [0.4.5] GuiDocEditHeader
Rewritten: 2020-06-15 [0.9]   GuiDocEditSearch
Created:   2020-06-27 [0.10]  GuiDocEditFooter
Rewritten: 2020-10-07 [1.0b3] BackgroundWordCounter

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

import bisect
import logging
import novelwriter

from enum import Enum
from time import time

from PyQt5.QtCore import (
    Qt, QSize, QTimer, pyqtSlot, pyqtSignal, QRegExp, QRegularExpression,
    QPointF, QObject, QRunnable, QPropertyAnimation
)
from PyQt5.QtGui import (
    QFontMetrics, QTextCursor, QTextOption, QKeySequence, QFont, QColor,
    QPalette, QTextDocument, QCursor, QPixmap
)
from PyQt5.QtWidgets import (
    qApp, QTextEdit, QAction, QMenu, QShortcut, QMessageBox, QWidget, QLabel,
    QToolBar, QToolButton, QHBoxLayout, QGridLayout, QLineEdit, QPushButton,
    QFrame
)

from novelwriter.enum import nwAlert, nwDocAction, nwDocInsert, nwDocMode, nwItemClass
from novelwriter.common import minmax, transferCase
from novelwriter.constants import nwConst, nwFiles, nwKeyWords, nwUnicode
from novelwriter.core.index import countWords
from novelwriter.core.spellcheck import NWSpellEnchant
from novelwriter.gui.dochighlight import GuiDocHighlighter

logger = logging.getLogger(__name__)


class GuiDocEditor(QTextEdit):

    MOVE_KEYS = (
        Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down,
        Qt.Key_PageUp, Qt.Key_PageDown
    )

    # Custom Signals
    spellDictionaryChanged = pyqtSignal(str, str)
    docEditedStatusChanged = pyqtSignal(bool)
    docCountsChanged = pyqtSignal(str, int, int, int)
    loadDocumentTagRequest = pyqtSignal(str, Enum)
    novelStructureChanged = pyqtSignal()
    novelItemMetaChanged = pyqtSignal(str)

    def __init__(self, mainGui):
        super().__init__(parent=mainGui)

        logger.debug("Initialising GuiDocEditor ...")

        # Class Variables
        self.mainConf   = novelwriter.CONFIG
        self.mainGui    = mainGui
        self.mainTheme  = mainGui.mainTheme
        self.theProject = mainGui.theProject

        self._nwDocument = None
        self._nwItem     = None

        self._docChanged = False  # Flag for changed status of document
        self._docHandle  = None   # The handle of the open file

        self._spellCheck = False  # Flag for spell checking enabled
        self._nonWord    = "\"'"  # Characters to not include in spell checking
        self._vpMargin   = 0      # The editor viewport margin, set during init

        # Document Variables
        self._charCount  = 0      # Character count
        self._wordCount  = 0      # Word count
        self._paraCount  = 0      # Paragraph count
        self._lastEdit   = 0      # Time stamp of last edit
        self._lastActive = 0      # Time stamp of last activity
        self._lastFind   = None   # Position of the last found search word
        self._bigDoc     = False  # Flag for very large document size
        self._doReplace  = False  # Switch to temporarily disable auto-replace
        self._queuePos   = None   # Used for delayed change of cursor position

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

        # Core Elements and Signals
        qDoc = self.document()
        qDoc.contentsChange.connect(self._docChange)
        qDoc.documentLayout().documentSizeChanged.connect(self._docSizeChanged)
        self.selectionChanged.connect(self._updateSelectedStatus)

        # Document Title
        self.docHeader = GuiDocEditHeader(self)
        self.docFooter = GuiDocEditFooter(self)
        self.docSearch = GuiDocEditSearch(self)

        # Syntax
        self.spEnchant = NWSpellEnchant()
        self.highLight = GuiDocHighlighter(qDoc, self.mainGui, self.spEnchant)

        # Context Menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._openContextMenu)

        # Editor Settings
        self.setMinimumWidth(self.mainConf.pxInt(300))
        self.setAcceptRichText(False)
        self.setAutoFillBackground(True)
        self.setFrameStyle(QFrame.NoFrame)

        # Custom Shortcuts
        self.keyContext = QShortcut(self)
        self.keyContext.setKey("Ctrl+.")
        self.keyContext.setContext(Qt.WidgetShortcut)
        self.keyContext.activated.connect(self._openSpellContext)

        self.followTag1 = QShortcut(self)
        self.followTag1.setKey(Qt.Key_Return | Qt.ControlModifier)
        self.followTag1.setContext(Qt.WidgetShortcut)
        self.followTag1.activated.connect(self._followTag)

        self.followTag2 = QShortcut(self)
        self.followTag2.setKey(Qt.Key_Enter | Qt.ControlModifier)
        self.followTag2.setContext(Qt.WidgetShortcut)
        self.followTag2.activated.connect(self._followTag)

        # Set Up Document Word Counter
        self.wcTimerDoc = QTimer()
        self.wcTimerDoc.timeout.connect(self._runDocCounter)

        self.wCounterDoc = BackgroundWordCounter(self)
        self.wCounterDoc.setAutoDelete(False)
        self.wCounterDoc.signals.countsReady.connect(self._updateDocCounts)

        self.wcInterval = self.mainConf.wordCountTimer

        # Set Up Selection Word Counter
        self.wcTimerSel = QTimer()
        self.wcTimerSel.timeout.connect(self._runSelCounter)
        self.wcTimerSel.setInterval(500)

        self.wCounterSel = BackgroundWordCounter(self, forSelection=True)
        self.wCounterSel.setAutoDelete(False)
        self.wCounterSel.signals.countsReady.connect(self._updateSelCounts)

        # Finalise
        self.updateSyntaxColours()
        self.initEditor()

        logger.debug("GuiDocEditor initialisation complete")

        return

    def clearEditor(self):
        """Clear the current document and reset all document-related
        flags and counters.
        """
        self._nwDocument = None
        self.setReadOnly(True)
        self.clear()
        self.wcTimerDoc.stop()
        self.wcTimerSel.stop()

        self._docHandle  = None
        self._charCount  = 0
        self._wordCount  = 0
        self._paraCount  = 0
        self._lastEdit   = 0
        self._lastActive = 0
        self._lastFind   = None
        self._bigDoc     = False
        self._doReplace  = False
        self._queuePos   = None

        self.setDocumentChanged(False)
        self.docHeader.setTitleFromHandle(self._docHandle)
        self.docFooter.setHandle(self._docHandle)

        return True

    def updateTheme(self):
        """Update theme elements
        """
        self.docSearch.updateTheme()
        self.docHeader.updateTheme()
        self.docFooter.updateTheme()
        return

    def updateSyntaxColours(self):
        """Update the syntax highlighting theme.
        """
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

        self.highLight.initHighlighter()

        return

    def initEditor(self):
        """Initialise or re-initialise the editor with the user's
        settings. This function is both called when the editor is
        created, and when the user changes the main editor preferences.
        """
        # Some Constants
        self._nonWord = (
            "\"'"
            f"{self.mainConf.fmtSQuoteOpen}{self.mainConf.fmtSQuoteClose}"
            f"{self.mainConf.fmtDQuoteOpen}{self.mainConf.fmtDQuoteClose}"
        )

        # Typography
        if self.mainConf.fmtPadThin:
            self._typPadChar = nwUnicode.U_THNBSP
        else:
            self._typPadChar = nwUnicode.U_NBSP

        self._typSQuoteO = self.mainConf.fmtSQuoteOpen
        self._typSQuoteC = self.mainConf.fmtSQuoteClose
        self._typDQuoteO = self.mainConf.fmtDQuoteOpen
        self._typDQuoteC = self.mainConf.fmtDQuoteClose
        self._typRepDQuote = self.mainConf.doReplaceDQuote
        self._typRepSQuote = self.mainConf.doReplaceSQuote
        self._typRepDash = self.mainConf.doReplaceDash
        self._typRepDots = self.mainConf.doReplaceDots
        self._typPadBefore = self.mainConf.fmtPadBefore
        self._typPadAfter = self.mainConf.fmtPadAfter

        # Reload spell check and dictionaries
        self.setDictionaries()

        # Set font
        theFont = QFont()
        qDoc = self.document()
        if self.mainConf.textFont is None:
            # If none is defined, set a default font
            theFont = QFont()
            if self.mainConf.osWindows and "Arial" in self.mainTheme.guiFontDB.families():
                theFont.setFamily("Arial")
                theFont.setPointSize(12)
            elif self.mainConf.osDarwin and "Courier" in self.mainTheme.guiFontDB.families():
                theFont.setFamily("Courier")
                theFont.setPointSize(12)
            else:
                theFont = qDoc.defaultFont()

            self.mainConf.textFont = theFont.family()
            self.mainConf.textSize = theFont.pointSize()

        theFont.setFamily(self.mainConf.textFont)
        theFont.setPointSize(self.mainConf.textSize)
        self.setFont(theFont)

        # Set default text margins
        # Due to cursor visibility, a part of the margin must be
        # allocated to the document itself. See issue #1112.
        cW = self.cursorWidth()
        qDoc.setDocumentMargin(cW)
        self._vpMargin = max(self.mainConf.getTextMargin() - cW, 0)
        self.setViewportMargins(self._vpMargin, self._vpMargin, self._vpMargin, self._vpMargin)

        # Also set the document text options for the document text flow
        theOpt = QTextOption()

        if self.mainConf.doJustify:
            theOpt.setAlignment(Qt.AlignJustify)
        if self.mainConf.showTabsNSpaces:
            theOpt.setFlags(theOpt.flags() | QTextOption.ShowTabsAndSpaces)
        if self.mainConf.showLineEndings:
            theOpt.setFlags(theOpt.flags() | QTextOption.ShowLineAndParagraphSeparators)

        qDoc.setDefaultTextOption(theOpt)

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

        # Configure word count timer
        self.wcInterval = self.mainConf.wordCountTimer
        self.wcTimerDoc.setInterval(int(self.wcInterval*1000))

        # If we have a document open, we should reload it in case the
        # font changed, otherwise we just clear the editor entirely,
        # which makes it read only.
        if self._docHandle is None:
            self.clearEditor()
        else:
            self.redrawText()

        return True

    def loadText(self, tHandle, tLine=None):
        """Load text from a document into the editor. If we have an io
        error, we must handle this and clear the editor so that we don't
        risk overwriting the file if it exists. This can for instance
        happen of the file contains binary elements or an encoding that
        novelWriter does not support. If loading is successful, or the
        document is new (empty string), we set up the editor for editing
        the file.
        """
        self._nwDocument = self.theProject.storage.getDocument(tHandle)
        self._nwItem = self._nwDocument.getCurrentItem()

        theDoc = self._nwDocument.readDocument()
        if theDoc is None:
            # There was an io error
            self.clearEditor()
            return False

        docSize = len(theDoc)
        if docSize > nwConst.MAX_DOCSIZE:
            self.mainGui.makeAlert(self.tr(
                "The document you are trying to open is too big. "
                "The document size is {0} MB. "
                "The maximum size allowed is {1} MB."
            ).format(
                f"{docSize/1.0e6:.2f}",
                f"{nwConst.MAX_DOCSIZE/1.0e6:.2f}"
            ), nwAlert.ERROR)
            self.clearEditor()
            return False

        qApp.setOverrideCursor(QCursor(Qt.WaitCursor))
        self.highLight.setHandle(tHandle)

        # Check that the document is not too big for full, initial spell
        # checking. If it is too big, we switch to only check as we type
        self._checkDocSize(docSize)
        spTemp = self.highLight.spellCheck
        if self._bigDoc:
            self.highLight.spellCheck = False

        bfTime = time()
        self._allowAutoReplace(False)
        self.setPlainText(theDoc)
        qApp.processEvents()

        self._allowAutoReplace(True)
        afTime = time()
        logger.debug("Document highlighted in %.3f ms", 1000*(afTime-bfTime))

        self._lastEdit = time()
        self._lastActive = time()
        self._runDocCounter()
        self.wcTimerDoc.start()
        self._docHandle = tHandle

        self.setReadOnly(False)
        self.docHeader.setTitleFromHandle(self._docHandle)
        self.docFooter.setHandle(self._docHandle)
        self.updateDocMargins()
        self.highLight.spellCheck = spTemp

        if tLine is None and self._nwItem is not None:
            # For large documents, we queue the repositioning until the
            # document layout has grown past the point we want to move
            # the cursor to. This makes the loading significantly
            # faster.
            if docSize > 50000:
                self._queuePos = self._nwItem.cursorPos
            else:
                self.setCursorPosition(self._nwItem.cursorPos)
        elif isinstance(tLine, int):
            self.setCursorLine(tLine)

        if self.mainConf.scrollPastEnd > 0:
            fSize = QFontMetrics(self.font()).lineSpacing()
            docFrame = self.document().rootFrame().frameFormat()
            docFrame.setBottomMargin(round(self.mainConf.scrollPastEnd * fSize))
            self.document().rootFrame().setFrameFormat(docFrame)

        self.docFooter.updateLineCount()

        qApp.processEvents()
        self.document().clearUndoRedoStacks()
        self.setDocumentChanged(False)
        qApp.restoreOverrideCursor()

        # This is a hack to fix invisble cursor on an empty document
        if self.document().characterCount() <= 1:
            self.setPlainText("\n")
            self.setPlainText("")
            self.setCursorPosition(0)

        # Update the status bar
        if self._nwItem is not None:
            self.mainGui.setStatus(
                self.tr("Opened Document: {0}").format(self._nwItem.itemName)
            )

        return True

    def updateTagHighLighting(self):
        """Rerun the syntax highlighter on all meta data lines.
        """
        self.highLight.rehighlightByType(GuiDocHighlighter.BLOCK_META)
        return

    def redrawText(self):
        """Redraw the text by marking the document content as "dirty".
        """
        self.document().markContentsDirty(0, self.document().characterCount())
        self.updateDocMargins()
        return

    def replaceText(self, theText):
        """Replace the text of the current document with the provided
        text. This also clears undo history.
        """
        docSize = len(theText)
        if docSize > nwConst.MAX_DOCSIZE:
            self.mainGui.makeAlert(self.tr(
                "The text you are trying to add is too big. "
                "The text size is {0} MB. "
                "The maximum size allowed is {1} MB."
            ).format(
                f"{docSize/1.0e6:.2f}",
                f"{nwConst.MAX_DOCSIZE/1.0e6:.2f}"
            ), nwAlert.ERROR)
            return False

        qApp.setOverrideCursor(QCursor(Qt.WaitCursor))
        self.setPlainText(theText)
        self.updateDocMargins()
        self.setDocumentChanged(True)
        qApp.restoreOverrideCursor()

        return True

    def saveText(self):
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

        self._nwItem.setCharCount(self._charCount)
        self._nwItem.setWordCount(self._wordCount)
        self._nwItem.setParaCount(self._paraCount)

        self.saveCursorPosition()
        if not self._nwDocument.writeDocument(docText):
            saveOk = False
            if self._nwDocument._currHash != self._nwDocument._prevHash:
                msgYes = self.mainGui.askQuestion(
                    self.tr("File Changed on Disk"),
                    self.tr(
                        "This document has been changed outside of novelWriter "
                        "while it was open. Overwrite the file on disk?"
                    )
                )
                if msgYes:
                    saveOk = self._nwDocument.writeDocument(docText, forceWrite=True)

            if not saveOk:
                self.mainGui.makeAlert([
                    self.tr("Could not save document."), self._nwDocument.getError()
                ], nwAlert.ERROR)

            return False

        self.setDocumentChanged(False)

        oldHeader = self._nwItem.mainHeading
        oldCount = self.theProject.index.getHandleHeaderCount(tHandle)
        self.theProject.index.scanText(tHandle, docText)
        newHeader = self._nwItem.mainHeading
        newCount = self.theProject.index.getHandleHeaderCount(tHandle)

        if self._nwItem.itemClass == nwItemClass.NOVEL:
            if oldCount == newCount:
                self.novelItemMetaChanged.emit(tHandle)
            else:
                self.novelStructureChanged.emit()

        # ToDo: This should be a signal
        if oldHeader != newHeader:
            self.mainGui.projView.setTreeItemValues(tHandle)
            self.mainGui.itemDetails.updateViewBox(tHandle)
            self.docFooter.updateInfo()

        # Update the status bar
        self.mainGui.setStatus(
            self.tr("Saved Document: {0}").format(self._nwItem.itemName)
        )

        return True

    def updateDocMargins(self):
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
        if self.mainConf.textWidth > 0 or self.mainGui.isFocusMode:
            tW = self.mainConf.getTextWidth(self.mainGui.isFocusMode)
            tM = max((wW - sW - tW)//2, self._vpMargin)

        tB = self.frameWidth()
        tW = wW - 2*tB - sW
        tH = self.docHeader.height()
        fH = self.docFooter.height()
        fY = wH - fH - tB - sH
        self.docHeader.setGeometry(tB, tB, tW, tH)
        self.docFooter.setGeometry(tB, fY, tW, fH)

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
    #  Properties
    ##

    def docChanged(self):
        """Return the changed status of the document in the editor.
        """
        return self._docChanged

    def docHandle(self):
        """Return the handle of the currently open document. Return
        None if no document is open.
        """
        return self._docHandle

    def lastActive(self):
        """Return the last active timestamp for the user.
        """
        return self._lastActive

    def isEmpty(self):
        """Wrapper function to check if the current document is empty.
        """
        return self.document().isEmpty()

    ##
    #  Getters
    ##

    def getText(self):
        """Get the text content of the current document. This method uses
        QTextDocument->toRawText instead of toPlainText(). The former preserves
        non-breaking spaces, the latter does not. We still want to get rid of
        page and line separators though.
        See: https://doc.qt.io/qt-5/qtextdocument.html#toPlainText
        """
        theText = self.document().toRawText()
        theText = theText.replace(nwUnicode.U_LSEP, "\n")  # Line separators
        theText = theText.replace(nwUnicode.U_PSEP, "\n")  # Paragraph separators
        return theText

    def getCursorPosition(self):
        """Find the cursor position in the document. If the editor has a
        selection, return the position of the end of the selection.
        """
        return self.textCursor().selectionEnd()

    ##
    #  Setters
    ##

    def setDocumentChanged(self, bValue):
        """Keep track of the document changed variable, and emit the
        document change signal.
        """
        self._docChanged = bValue
        self.docEditedStatusChanged.emit(self._docChanged)
        return self._docChanged

    def setCursorPosition(self, position):
        """Move the cursor to a given position in the document.
        """
        if not isinstance(position, int):
            return False

        nChars = self.document().characterCount()
        if nChars > 1:
            theCursor = self.textCursor()
            theCursor.setPosition(minmax(position, 0, nChars-1))
            self.setTextCursor(theCursor)

            # By default, the editor scrolls so the cursor is on the
            # last line, so we must correct it. The user setting for
            # auto-scroll is used to determine the scroll distance. This
            # makes it compatible with the typewriter scrolling feature
            # when it is enabled. By default, it's 30% of viewport.
            vPos = self.verticalScrollBar().value()
            cPos = self.cursorRect().topLeft().y()
            mPos = int(self.mainConf.autoScrollPos*0.01 * self.viewport().height())
            if cPos > mPos:
                # Only scroll if the cursor is past the auto-scroll limit
                self.verticalScrollBar().setValue(max(0, vPos + cPos - mPos))

            self.docFooter.updateLineCount()

        return True

    def saveCursorPosition(self):
        """Save the cursor position to the current project item object.
        """
        if self._nwItem is not None:
            cursPos = self.getCursorPosition()
            self._nwItem.setCursorPos(cursPos)
        return

    def setCursorLine(self, lineNo):
        """Move the cursor to a given line in the document.
        """
        if not isinstance(lineNo, int):
            return False

        lineIdx = lineNo - 1  # Block index is 0 offset, lineNo is 1 offset
        if lineIdx >= 0:
            theBlock = self.document().findBlockByLineNumber(lineIdx)
            if theBlock:
                self.setCursorPosition(theBlock.position())
                logger.debug("Cursor moved to line %d", lineNo)

        return True

    ##
    #  Spell Checking
    ##

    def setDictionaries(self):
        """Set the spell checker dictionary language, and emit the
        dictionary changed signal.
        """
        if self.theProject.data.spellLang is None:
            theLang = self.mainConf.spellLanguage
        else:
            theLang = self.theProject.data.spellLang

        projDict = self.theProject.storage.getMetaFile(nwFiles.PROJ_DICT)
        self.spEnchant.setLanguage(theLang, projDict)
        _, theProvider = self.spEnchant.describeDict()

        self.spellDictionaryChanged.emit(str(theLang), str(theProvider))

        if not self._bigDoc:
            self.spellCheckDocument()

        return True

    def toggleSpellCheck(self, theMode):
        """This is the master spell check setting function, and this one
        should call all other setSpellCheck functions in other classes.
        If the spell check mode (theMode) is not defined (None), then
        toggle the current status saved in this class.
        """
        if theMode is None:
            theMode = not self._spellCheck

        if not self.mainConf.hasEnchant:
            if theMode:
                self.mainGui.makeAlert(self.tr(
                    "Spell checking requires the package PyEnchant. "
                    "It does not appear to be installed."
                ), nwAlert.INFO)
            theMode = False

        if self.spEnchant.spellLanguage is None:
            theMode = False

        self._spellCheck = theMode
        self.mainGui.mainMenu.setSpellCheck(theMode)
        self.theProject.data.setSpellCheck(theMode)
        self.highLight.setSpellCheck(theMode)
        if not self._bigDoc:
            self.spellCheckDocument()

        logger.debug("Spell check is set to '%s'", str(theMode))

        return True

    def spellCheckDocument(self):
        """Rerun the highlighter to update spell checking status of the
        currently loaded text. The fastest way to do this, at least as
        of Qt 5.13, is to clear the text and put it back. This clears
        the undo stack, so we only do it for big documents.
        """
        logger.debug("Running spell checker")
        if self._spellCheck:
            bfTime = time()
            qApp.setOverrideCursor(QCursor(Qt.WaitCursor))
            if self._bigDoc:
                theText = self.getText()
                self.setPlainText(theText)
            else:
                self.highLight.rehighlight()
            qApp.restoreOverrideCursor()
            afTime = time()
            logger.debug("Document highlighted in %.3f ms", 1000*(afTime-bfTime))
            self.mainGui.mainStatus.setStatus(self.tr("Spell check complete"))

        return True

    ##
    #  General Class Methods
    ##

    def docAction(self, theAction):
        """Perform an action on the current document based on an action
        flag. This is just a single entry point wrapper function to
        ensure all the feature functions get the correct information
        passed to it without having to consider the internal logic of
        this class when calling these actions from other classes.
        """
        if self._docHandle is None:
            logger.error("No document open")
            return False

        if not isinstance(theAction, nwDocAction):
            logger.error("Not a document action")
            return False

        logger.debug("Requesting action: %s", theAction.name)

        self._allowAutoReplace(False)
        if theAction == nwDocAction.UNDO:
            self.undo()
        elif theAction == nwDocAction.REDO:
            self.redo()
        elif theAction == nwDocAction.CUT:
            self.cut()
        elif theAction == nwDocAction.COPY:
            self.copy()
        elif theAction == nwDocAction.PASTE:
            self.paste()
        elif theAction == nwDocAction.EMPH:
            self._toggleFormat(1, "_")
        elif theAction == nwDocAction.STRONG:
            self._toggleFormat(2, "*")
        elif theAction == nwDocAction.STRIKE:
            self._toggleFormat(2, "~")
        elif theAction == nwDocAction.S_QUOTE:
            self._wrapSelection(self._typSQuoteO, self._typSQuoteC)
        elif theAction == nwDocAction.D_QUOTE:
            self._wrapSelection(self._typDQuoteO, self._typDQuoteC)
        elif theAction == nwDocAction.SEL_ALL:
            self._makeSelection(QTextCursor.Document)
        elif theAction == nwDocAction.SEL_PARA:
            self._makeSelection(QTextCursor.BlockUnderCursor)
        elif theAction == nwDocAction.BLOCK_H1:
            self._formatBlock(nwDocAction.BLOCK_H1)
        elif theAction == nwDocAction.BLOCK_H2:
            self._formatBlock(nwDocAction.BLOCK_H2)
        elif theAction == nwDocAction.BLOCK_H3:
            self._formatBlock(nwDocAction.BLOCK_H3)
        elif theAction == nwDocAction.BLOCK_H4:
            self._formatBlock(nwDocAction.BLOCK_H4)
        elif theAction == nwDocAction.BLOCK_COM:
            self._formatBlock(nwDocAction.BLOCK_COM)
        elif theAction == nwDocAction.BLOCK_TXT:
            self._formatBlock(nwDocAction.BLOCK_TXT)
        elif theAction == nwDocAction.BLOCK_TTL:
            self._formatBlock(nwDocAction.BLOCK_TTL)
        elif theAction == nwDocAction.BLOCK_UNN:
            self._formatBlock(nwDocAction.BLOCK_UNN)
        elif theAction == nwDocAction.REPL_SNG:
            self._replaceQuotes("'", self._typSQuoteO, self._typSQuoteC)
        elif theAction == nwDocAction.REPL_DBL:
            self._replaceQuotes("\"", self._typDQuoteO, self._typDQuoteC)
        elif theAction == nwDocAction.RM_BREAKS:
            self._removeInParLineBreaks()
        elif theAction == nwDocAction.ALIGN_L:
            self._formatBlock(nwDocAction.ALIGN_L)
        elif theAction == nwDocAction.ALIGN_C:
            self._formatBlock(nwDocAction.ALIGN_C)
        elif theAction == nwDocAction.ALIGN_R:
            self._formatBlock(nwDocAction.ALIGN_R)
        elif theAction == nwDocAction.INDENT_L:
            self._formatBlock(nwDocAction.INDENT_L)
        elif theAction == nwDocAction.INDENT_R:
            self._formatBlock(nwDocAction.INDENT_R)
        else:
            logger.debug("Unknown or unsupported document action '%s'", str(theAction))
            self._allowAutoReplace(True)
            return False

        self._allowAutoReplace(True)
        self._lastActive = time()

        return True

    def anyFocus(self):
        """Check if any widget or child widget has focus.
        """
        if self.hasFocus():
            return True
        if self.isAncestorOf(qApp.focusWidget()):
            return True
        return False

    def revealLocation(self):
        """Tell the user where on the file system the file in the editor
        is saved.
        """
        if self._nwDocument is None:
            logger.error("No document open")
            return False

        msgBox = QMessageBox()
        msgBox.information(
            self,
            self.tr("File Location"),
            "%s<br>%s" % (
                self.tr("The currently open file is saved in:"),
                self._nwDocument.getFileLocation()
            ),
        )

        return

    def insertText(self, theInsert):
        """Insert a specific type of text at the cursor position.
        """
        if self._docHandle is None:
            logger.error("No document open")
            return False

        newBlock = False
        goAfter = False

        if isinstance(theInsert, str):
            theText = theInsert
        elif isinstance(theInsert, nwDocInsert):
            if theInsert == nwDocInsert.QUOTE_LS:
                theText = self._typSQuoteO
            elif theInsert == nwDocInsert.QUOTE_RS:
                theText = self._typSQuoteC
            elif theInsert == nwDocInsert.QUOTE_LD:
                theText = self._typDQuoteO
            elif theInsert == nwDocInsert.QUOTE_RD:
                theText = self._typDQuoteC
            elif theInsert == nwDocInsert.SYNOPSIS:
                theText = "% Synopsis: "
                newBlock = True
                goAfter = True
            elif theInsert == nwDocInsert.NEW_PAGE:
                theText = "[NEW PAGE]"
                newBlock = True
                goAfter = False
            elif theInsert == nwDocInsert.VSPACE_S:
                theText = "[VSPACE]"
                newBlock = True
                goAfter = False
            elif theInsert == nwDocInsert.VSPACE_M:
                theText = "[VSPACE:2]"
                newBlock = True
                goAfter = False
            else:
                return False
        else:
            return False

        if newBlock:
            self.insertNewBlock(theText, defaultAfter=goAfter)
        else:
            theCursor = self.textCursor()
            theCursor.beginEditBlock()
            theCursor.insertText(theText)
            theCursor.endEditBlock()

        return True

    def insertNewBlock(self, theText, defaultAfter=True):
        """Insert a piece of text on a blank line.
        """
        theCursor = self.textCursor()
        theBlock = theCursor.block()
        if not theBlock.isValid():
            logger.error("Not a valid text block")
            return False

        sPos = theBlock.position()
        sLen = theBlock.length()

        theCursor.beginEditBlock()

        if sLen > 1 and defaultAfter:
            theCursor.setPosition(sPos + sLen - 1)
            theCursor.insertText("\n")
        else:
            theCursor.setPosition(sPos)

        theCursor.insertText(theText)

        if sLen > 1 and not defaultAfter:
            theCursor.insertText("\n")

        theCursor.endEditBlock()

        self.setTextCursor(theCursor)

        return True

    def insertKeyWord(self, keyWord):
        """Insert a keyword in the text editor, at the cursor position.
        If the insert line is not blank, a new line is started.
        """
        if keyWord not in nwKeyWords.VALID_KEYS:
            logger.error("Invalid keyword '%s'", keyWord)
            return False

        logger.debug("Inserting keyword '%s'", keyWord)
        theState = self.insertNewBlock("%s: " % keyWord)

        return theState

    def closeSearch(self):
        """Close the search box.
        """
        self.docSearch.closeSearch()
        return self.docSearch.isVisible()

    def toggleSearch(self):
        """Toggle the visibility of the search box.
        """
        if self.docSearch.isVisible():
            self.docSearch.closeSearch()
        else:
            self.beginSearch()
        return

    ##
    #  Document Events and Maintenance
    ##

    def keyPressEvent(self, keyEvent):
        """Intercept key press events.
        We need to intercept a few key sequences:
          * The return and enter keys redirect here even if the search
            box has focus. Since we need these keys to continue search,
            we block any further interaction here while ithas focus.
          * The undo/redo/select all sequences bypass the docAction
            pathway from the menu, so we redirect them back from here.
          * We also handle automatic scrolling here.
        """
        self._lastActive = time()
        isReturn  = keyEvent.key() == Qt.Key_Return
        isReturn |= keyEvent.key() == Qt.Key_Enter
        if isReturn and self.docSearch.anyFocus():
            return
        elif keyEvent == QKeySequence.Redo:
            self.docAction(nwDocAction.REDO)
            return
        elif keyEvent == QKeySequence.Undo:
            self.docAction(nwDocAction.UNDO)
            return
        elif keyEvent == QKeySequence.SelectAll:
            self.docAction(nwDocAction.SEL_ALL)
            return

        if self.mainConf.autoScroll:

            cOld = self.cursorRect().center().y()
            super().keyPressEvent(keyEvent)

            kMod = keyEvent.modifiers()
            okMod = kMod == Qt.NoModifier or kMod == Qt.ShiftModifier
            okKey = keyEvent.key() not in self.MOVE_KEYS
            if okMod and okKey:
                cNew = self.cursorRect().center().y()
                cMov = cNew - cOld
                mPos = self.mainConf.autoScrollPos*0.01 * self.viewport().height()
                if abs(cMov) > 0 and cOld > mPos:
                    # Move the scroll bar
                    vBar = self.verticalScrollBar()
                    doAnim = QPropertyAnimation(vBar, b"value", self)
                    doAnim.setDuration(120)
                    doAnim.setStartValue(vBar.value())
                    doAnim.setEndValue(vBar.value() + cMov)
                    doAnim.start()

        else:
            super().keyPressEvent(keyEvent)

        self.docFooter.updateLineCount()

        return

    def focusNextPrevChild(self, toNext):
        """Capture the focus request from the tab key on the text
        editor. If the editor has focus, we do not change focus and
        allow the editor to insert a tab. If the search bar has focus,
        we forward the call to the search object.
        """
        if self.hasFocus():
            return False
        elif self.docSearch.isVisible():
            return self.docSearch.cycleFocus(toNext)
        return True

    def mouseReleaseEvent(self, theEvent):
        """If the mouse button is released and the control key is
        pressed, check if we're clicking on a tag, and trigger the
        follow tag function.
        """
        if qApp.keyboardModifiers() == Qt.ControlModifier:
            theCursor = self.cursorForPosition(theEvent.pos())
            self._followTag(theCursor)

        super().mouseReleaseEvent(theEvent)
        self.docFooter.updateLineCount()

        return

    def resizeEvent(self, theEvent):
        """If the text editor is resized, we must make sure the document
        has its margins adjusted according to user preferences.
        """
        self.updateDocMargins()
        super().resizeEvent(theEvent)
        return

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
            self.docFooter.updateInfo()
            self.updateDocMargins()
        return

    ##
    #  Private Slots
    ##

    @pyqtSlot(int, int, int)
    def _docChange(self, thePos, chrRem, chrAdd):
        """Triggered by QTextDocument->contentsChanged. This also
        triggers the syntax highlighter.
        """
        self._lastEdit = time()
        self._lastFind = None

        if self.document().characterCount() > nwConst.MAX_DOCSIZE:
            self.mainGui.makeAlert(self.tr(
                "The document has grown too big and you cannot add more text to it. "
                "The maximum size of a single novelWriter document is {0} MB."
            ).format(
                f"{nwConst.MAX_DOCSIZE/1.0e6:.2f}"
            ), nwAlert.ERROR)
            self.undo()
            return

        if not self._docChanged:
            self.setDocumentChanged(chrRem != 0 or chrAdd != 0)

        if not self.wcTimerDoc.isActive():
            self.wcTimerDoc.start()

        if self._doReplace and chrAdd == 1:
            self._docAutoReplace(self.document().findBlock(thePos))

        return

    @pyqtSlot("QPoint")
    def _openContextMenu(self, thePos):
        """Triggered by right click to open the context menu. Also
        triggered by the Ctrl+. shortcut.
        """
        userCursor = self.textCursor()
        userSelection = userCursor.hasSelection()
        posCursor = self.cursorForPosition(thePos)

        mnuContext = QMenu()

        # Follow, Cut, Copy and Paste
        # ===========================

        if self._followTag(theCursor=posCursor, loadTag=False):
            mnuTag = QAction(self.tr("Follow Tag"), mnuContext)
            mnuTag.triggered.connect(lambda: self._followTag(theCursor=posCursor))
            mnuContext.addAction(mnuTag)
            mnuContext.addSeparator()

        if userSelection:
            mnuCut = QAction(self.tr("Cut"), mnuContext)
            mnuCut.triggered.connect(lambda: self.docAction(nwDocAction.CUT))
            mnuContext.addAction(mnuCut)

            mnuCopy = QAction(self.tr("Copy"), mnuContext)
            mnuCopy.triggered.connect(lambda: self.docAction(nwDocAction.COPY))
            mnuContext.addAction(mnuCopy)

        mnuPaste = QAction(self.tr("Paste"), mnuContext)
        mnuPaste.triggered.connect(lambda: self.docAction(nwDocAction.PASTE))
        mnuContext.addAction(mnuPaste)

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

        # Spell Checking
        # ==============

        posCursor = self.cursorForPosition(thePos)
        spellCheck = self._spellCheck
        theWord = ""

        if posCursor.block().text().startswith("@"):
            spellCheck = False

        if spellCheck:
            posCursor.select(QTextCursor.WordUnderCursor)
            theWord = posCursor.selectedText().strip().strip(self._nonWord)
            spellCheck &= theWord != ""

        if spellCheck:
            logger.debug("Looking up '%s' in the dictionary", theWord)
            spellCheck &= not self.spEnchant.checkWord(theWord)

        if spellCheck:
            mnuContext.addSeparator()
            mnuHead = QAction(self.tr("Spelling Suggestion(s)"), mnuContext)
            mnuContext.addAction(mnuHead)

            theSuggest = self.spEnchant.suggestWords(theWord)[:15]
            if len(theSuggest) > 0:
                for aWord in theSuggest:
                    mnuWord = QAction("%s %s" % (nwUnicode.U_ENDASH, aWord), mnuContext)
                    mnuWord.triggered.connect(
                        lambda thePos, aWord=aWord: self._correctWord(posCursor, aWord)
                    )
                    mnuContext.addAction(mnuWord)
            else:
                mnuHead = QAction(
                    "%s %s" % (nwUnicode.U_ENDASH, self.tr("No Suggestions")), mnuContext
                )
                mnuContext.addAction(mnuHead)

            mnuContext.addSeparator()
            mnuAdd = QAction(self.tr("Add Word to Dictionary"), mnuContext)
            mnuAdd.triggered.connect(lambda thePos: self._addWord(posCursor))
            mnuContext.addAction(mnuAdd)

        # Open the context menu
        mnuContext.exec_(self.viewport().mapToGlobal(thePos))

        return

    @pyqtSlot("QTextCursor", str)
    def _correctWord(self, theCursor, theWord):
        """Slot for the spell check context menu triggering the
        replacement of a word with the word from the dictionary.
        """
        xPos = theCursor.selectionStart()
        theCursor.beginEditBlock()
        theCursor.removeSelectedText()
        theCursor.insertText(theWord)
        theCursor.endEditBlock()
        theCursor.setPosition(xPos)
        self.setTextCursor(theCursor)
        return

    @pyqtSlot("QTextCursor")
    def _addWord(self, theCursor):
        """Slot for the spell check context menu triggered when the user
        wants to add a word to the project dictionary.
        """
        theWord = theCursor.selectedText().strip().strip(self._nonWord)
        logger.debug("Added '%s' to project dictionary", theWord)
        self.spEnchant.addWord(theWord)
        self.highLight.rehighlightBlock(theCursor.block())
        return

    @pyqtSlot()
    def _runDocCounter(self):
        """Decide whether to run the word counter, or not due to
        inactivity.
        """
        if self._docHandle is None:
            return

        if self.wCounterDoc.isRunning():
            logger.debug("Word counter is busy")
            return

        if time() - self._lastEdit < 5 * self.wcInterval:
            logger.debug("Running word counter")
            self.mainGui.threadPool.start(self.wCounterDoc)

        return

    @pyqtSlot(int, int, int)
    def _updateDocCounts(self, cCount, wCount, pCount):
        """Slot for the word counter's finished signal
        """
        if self._docHandle is None or self._nwItem is None:
            return

        logger.debug("Updating word count")

        self._charCount = cCount
        self._wordCount = wCount
        self._paraCount = pCount

        self._nwItem.setCharCount(cCount)
        self._nwItem.setWordCount(wCount)
        self._nwItem.setParaCount(pCount)

        # Must not be emitted if docHandle is None!
        self.docCountsChanged.emit(self._docHandle, cCount, wCount, pCount)

        self._checkDocSize(self.document().characterCount())
        self.docFooter.updateCounts()

        return

    @pyqtSlot()
    def _updateSelectedStatus(self):
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
    def _runSelCounter(self):
        """Update the selection word count.
        """
        if self._docHandle is None:
            return

        if self.wCounterSel.isRunning():
            logger.debug("Selection word counter is busy")
            return

        self.mainGui.threadPool.start(self.wCounterSel)

        return

    @pyqtSlot(int, int, int)
    def _updateSelCounts(self, cCount, wCount, pCount):
        """Slot for the word counter's finished signal
        """
        if self._docHandle is None or self._nwItem is None:
            return

        logger.debug("User selectee %d words", wCount)
        self.docFooter.updateCounts(wCount=wCount, cCount=cCount)
        self.wcTimerSel.stop()

        return

    @pyqtSlot("QSizeF")
    def _docSizeChanged(self, theSize):
        """Called whenever the underlying document layout size changes.
        This is used to queue the repositioning of the cursor for very
        large documents to ensure the region where the cursor is being
        moved to has been drawn before the move is made.
        """
        if self._queuePos is not None:
            thePos = self.document().documentLayout().hitTest(
                QPointF(theSize.width(), theSize.height()), Qt.FuzzyHit
            )
            if self._queuePos <= thePos:
                logger.debug("Allowed cursor move to %d <= %d", self._queuePos, thePos)
                self.setCursorPosition(self._queuePos)
                self._queuePos = None
            else:
                logger.debug("Denied cursor move to %d > %d", self._queuePos, thePos)

        return

    ##
    #  Search & Replace
    ##

    def beginSearch(self):
        """Set the selected text as the search text for the search bar.
        """
        theCursor = self.textCursor()
        if theCursor.hasSelection():
            self.docSearch.setSearchText(theCursor.selectedText())
        else:
            self.docSearch.setSearchText(None)
        resS, _ = self.findAllOccurences()
        self.docSearch.setResultCount(None, len(resS))
        return

    def beginReplace(self):
        """Initialise the search box and reset the replace text box.
        """
        self.beginSearch()
        self.docSearch.setReplaceText("")
        self.updateDocMargins()
        return

    def findNext(self, goBack=False):
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
        if len(resS) == 0:
            self.docSearch.setResultCount(0, 0)
            self._lastFind = None
            if self.docSearch.doNextFile and not goBack:
                self.mainGui.openNextDocument(
                    self._docHandle, wrapAround=self.docSearch.doLoop
                )
                self.beginSearch()
            return

        theCursor = self.textCursor()
        resIdx = bisect.bisect_left(resS, theCursor.position())

        doLoop = self.docSearch.doLoop
        maxIdx = len(resS) - 1

        if goBack:
            resIdx -= 2

        if resIdx < 0:
            resIdx = maxIdx if doLoop else 0

        if resIdx > maxIdx:
            if self.docSearch.doNextFile and not goBack:
                self.mainGui.openNextDocument(
                    self._docHandle, wrapAround=self.docSearch.doLoop
                )
                self.beginSearch()
                return
            else:
                resIdx = 0 if doLoop else maxIdx

        theCursor.setPosition(resS[resIdx], QTextCursor.MoveAnchor)
        theCursor.setPosition(resE[resIdx], QTextCursor.KeepAnchor)
        self.setTextCursor(theCursor)

        self.docFooter.updateLineCount()
        self.docSearch.setResultCount(resIdx + 1, len(resS))
        self._lastFind = (resS[resIdx], resE[resIdx])

        return

    def findAllOccurences(self):
        """Create a list of all search results of the current search
        text in the document.
        """
        resS = []
        resE = []
        theCursor = self.textCursor()
        hasSelection = theCursor.hasSelection()
        if hasSelection:
            origA = theCursor.selectionStart()
            origB = theCursor.selectionEnd()
        else:
            origA = theCursor.position()
            origB = theCursor.position()

        findOpt = QTextDocument.FindFlag(0)
        if self.docSearch.isCaseSense:
            findOpt |= QTextDocument.FindCaseSensitively
        if self.docSearch.isWholeWord:
            findOpt |= QTextDocument.FindWholeWords

        searchFor = self.docSearch.getSearchObject()
        theCursor.setPosition(0)
        self.setTextCursor(theCursor)

        # Search up to a maximum of 1000, and make sure certain special
        # searches like a regex search for .* turns into an infinite loop
        while self.find(searchFor, findOpt) and len(resE) <= 1000:
            theCursor = self.textCursor()
            if theCursor.hasSelection():
                resS.append(theCursor.selectionStart())
                resE.append(theCursor.selectionEnd())
            else:
                logger.warning("The search returned an empty result")
                break

        if hasSelection:
            theCursor.setPosition(origA, QTextCursor.MoveAnchor)
            theCursor.setPosition(origB, QTextCursor.KeepAnchor)
        else:
            theCursor.setPosition(origA)

        self.setTextCursor(theCursor)

        return resS, resE

    def replaceNext(self):
        """Search for the next occurrence of the search bar text in the
        document and replace it with the replace text. Call search next
        automatically when done.
        """
        if not self.anyFocus():
            logger.debug("Editor does not have focus")
            return False

        if not self.docSearch.isVisible():
            # The search tool is not active, so we activate it.
            self.beginSearch()
            return

        theCursor = self.textCursor()
        if not theCursor.hasSelection():
            # We have no text selected at all, so just make this a
            # regular find next call.
            self.findNext()
            return

        if self._lastFind is None and theCursor.hasSelection():
            # If we have a selection but no search, it may have been the
            # text we triggered the search with, in which case we search
            # again from the beginning of that selection to make sure we
            # have a valid result.
            sPos = theCursor.selectionStart()
            theCursor.clearSelection()
            theCursor.setPosition(sPos)
            self.setTextCursor(theCursor)
            self.findNext()
            theCursor = self.textCursor()

        if self._lastFind is None:
            # In case the above didn't find a result, we give up here.
            return

        searchFor = self.docSearch.getSearchText()
        replWith = self.docSearch.getReplaceText()

        if self.docSearch.doMatchCap:
            replWith = transferCase(theCursor.selectedText(), replWith)

        # Make sure the selected text was selected by an actual find
        # call, and not the user.
        try:
            isFind  = self._lastFind[0] == theCursor.selectionStart()
            isFind &= self._lastFind[1] == theCursor.selectionEnd()
        except Exception:
            isFind = False

        if isFind:
            theCursor.beginEditBlock()
            theCursor.removeSelectedText()
            theCursor.insertText(replWith)
            theCursor.endEditBlock()
            theCursor.setPosition(theCursor.selectionEnd())
            self.setTextCursor(theCursor)
            logger.debug(
                "Replaced occurrence of '%s' with '%s' on line %d",
                searchFor, replWith, theCursor.blockNumber()
            )
        else:
            logger.error("The selected text is not a search result, skipping replace")

        self.findNext()

        return

    ##
    #  Internal Functions : Text Manipulation
    ##

    def _toggleFormat(self, fLen, fChar):
        """Toggle the formatting of a specific type for a piece of text.
        If more than one block is selected, the formatting is applied to
        the first block.
        """
        theCursor = self._autoSelect()
        if not theCursor.hasSelection():
            logger.warning("No selection made, nothing to do")
            return False

        posS = theCursor.selectionStart()
        posE = theCursor.selectionEnd()

        blockS = self.document().findBlock(posS)
        blockE = self.document().findBlock(posE)

        if blockS != blockE:
            posE = blockS.position() + blockS.length() - 1
            theCursor.clearSelection()
            theCursor.setPosition(posS, QTextCursor.MoveAnchor)
            theCursor.setPosition(posE, QTextCursor.KeepAnchor)
            self.setTextCursor(theCursor)

        numB = 0
        for n in range(fLen):
            if self.document().characterAt(posS-n-1) == fChar:
                numB += 1
            else:
                break

        numA = 0
        for n in range(fLen):
            if self.document().characterAt(posE+n) == fChar:
                numA += 1
            else:
                break

        if fLen == min(numA, numB):
            self._clearSurrounding(theCursor, fLen)
        else:
            self._wrapSelection(fChar*fLen)

        return True

    def _clearSurrounding(self, theCursor, nChars):
        """Clear n characters before and after the cursor.
        """
        if not theCursor.hasSelection():
            logger.warning("No selection made, nothing to do")
            return False

        posS = theCursor.selectionStart()
        posE = theCursor.selectionEnd()
        theCursor.clearSelection()
        theCursor.beginEditBlock()
        theCursor.setPosition(posS)
        for i in range(nChars):
            theCursor.deletePreviousChar()
        theCursor.setPosition(posE)
        for i in range(nChars):
            theCursor.deletePreviousChar()
        theCursor.endEditBlock()
        theCursor.clearSelection()

        return True

    def _wrapSelection(self, tBefore, tAfter=None):
        """Wrap the selected text in whatever is in tBefore and tAfter.
        If there is no selection, the autoSelect setting decides the
        action. AutoSelect will select the word under the cursor before
        wrapping it. If this feature is disabled, nothing is done.
        """
        if tAfter is None:
            tAfter = tBefore

        theCursor = self._autoSelect()
        if not theCursor.hasSelection():
            logger.warning("No selection made, nothing to do")
            return False

        posS = theCursor.selectionStart()
        posE = theCursor.selectionEnd()

        qDoc = self.document()
        blockS = qDoc.findBlock(posS)
        blockE = qDoc.findBlock(posE)
        if blockS != blockE:
            posE = blockS.position() + blockS.length() - 1

        theCursor.clearSelection()
        theCursor.beginEditBlock()
        theCursor.setPosition(posE)
        theCursor.insertText(tAfter)
        theCursor.setPosition(posS)
        theCursor.insertText(tBefore)
        theCursor.endEditBlock()

        theCursor.setPosition(posE + len(tBefore), QTextCursor.MoveAnchor)
        theCursor.setPosition(posS + len(tBefore), QTextCursor.KeepAnchor)
        self.setTextCursor(theCursor)

        return True

    def _replaceQuotes(self, sQuote, oQuote, cQuote):
        """Replace all straight quotes in the selected text.
        """
        theCursor = self.textCursor()
        if not theCursor.hasSelection():
            self.mainGui.makeAlert(self.tr(
                "Please select some text before calling replace quotes."
            ), nwAlert.ERROR)
            return False

        posS = theCursor.selectionStart()
        posE = theCursor.selectionEnd()
        closeCheck = (
            " ", "\n", nwUnicode.U_LSEP, nwUnicode.U_PSEP
        )

        self._allowAutoReplace(False)
        for posC in range(posS, posE+1):
            theCursor.setPosition(posC)
            theCursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor, 2)
            selText = theCursor.selectedText()

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

            theCursor.clearSelection()
            theCursor.setPosition(posC)
            if pC in closeCheck:
                theCursor.beginEditBlock()
                theCursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor, 1)
                theCursor.insertText(oQuote)
                theCursor.endEditBlock()
            else:
                theCursor.beginEditBlock()
                theCursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor, 1)
                theCursor.insertText(cQuote)
                theCursor.endEditBlock()

        self._allowAutoReplace(True)

        return True

    def _formatBlock(self, docAction):
        """Change the block format of the block under the cursor.
        """
        theCursor = self.textCursor()
        theBlock = theCursor.block()
        if not theBlock.isValid():
            logger.debug("Invalid block selected for action '%s'", str(docAction))
            return False

        # Remove existing format first, if any
        theText = theBlock.text()
        if theText.startswith("@"):
            logger.error("Cannot apply block format to keyword/value line")
            return False
        elif theText.startswith("% "):
            newText = theText[2:]
            cOffset = 2
            if docAction == nwDocAction.BLOCK_COM:
                docAction = nwDocAction.BLOCK_TXT
        elif theText.startswith("%"):
            newText = theText[1:]
            cOffset = 1
            if docAction == nwDocAction.BLOCK_COM:
                docAction = nwDocAction.BLOCK_TXT
        elif theText.startswith("# "):
            newText = theText[2:]
            cOffset = 2
        elif theText.startswith("## "):
            newText = theText[3:]
            cOffset = 3
        elif theText.startswith("### "):
            newText = theText[4:]
            cOffset = 4
        elif theText.startswith("#### "):
            newText = theText[5:]
            cOffset = 5
        elif theText.startswith("#! "):
            newText = theText[3:]
            cOffset = 3
        elif theText.startswith("##! "):
            newText = theText[4:]
            cOffset = 4
        elif theText.startswith(">> "):
            newText = theText[3:]
            cOffset = 3
        elif theText.startswith("> ") and docAction != nwDocAction.INDENT_R:
            newText = theText[2:]
            cOffset = 2
        elif theText.startswith(">>"):
            newText = theText[2:]
            cOffset = 2
        elif theText.startswith(">") and docAction != nwDocAction.INDENT_R:
            newText = theText[1:]
            cOffset = 1
        else:
            newText = theText
            cOffset = 0

        # Also remove formatting tags at the end
        if theText.endswith(" <<"):
            newText = newText[:-3]
        elif theText.endswith(" <") and docAction != nwDocAction.INDENT_L:
            newText = newText[:-2]
        elif theText.endswith("<<"):
            newText = newText[:-2]
        elif theText.endswith("<") and docAction != nwDocAction.INDENT_L:
            newText = newText[:-1]

        # Apply new format
        if docAction == nwDocAction.BLOCK_COM:
            theText = "% "+newText
            cOffset -= 2
        elif docAction == nwDocAction.BLOCK_H1:
            theText = "# "+newText
            cOffset -= 2
        elif docAction == nwDocAction.BLOCK_H2:
            theText = "## "+newText
            cOffset -= 3
        elif docAction == nwDocAction.BLOCK_H3:
            theText = "### "+newText
            cOffset -= 4
        elif docAction == nwDocAction.BLOCK_H4:
            theText = "#### "+newText
            cOffset -= 5
        elif docAction == nwDocAction.BLOCK_TTL:
            theText = "#! "+newText
            cOffset -= 3
        elif docAction == nwDocAction.BLOCK_UNN:
            theText = "##! "+newText
            cOffset -= 4
        elif docAction == nwDocAction.ALIGN_L:
            theText = newText+" <<"
        elif docAction == nwDocAction.ALIGN_C:
            theText = ">> "+newText+" <<"
            cOffset -= 3
        elif docAction == nwDocAction.ALIGN_R:
            theText = ">> "+newText
            cOffset -= 3
        elif docAction == nwDocAction.INDENT_L:
            theText = "> "+newText
            cOffset -= 2
        elif docAction == nwDocAction.INDENT_R:
            theText = newText+" <"
        elif docAction == nwDocAction.BLOCK_TXT:
            theText = newText
        else:
            logger.error("Unknown or unsupported block format requested: '%s'", str(docAction))
            return False

        # Replace the block text
        theCursor.beginEditBlock()
        posO = theCursor.position()
        theCursor.select(QTextCursor.BlockUnderCursor)
        posS = theCursor.selectionStart()
        theCursor.removeSelectedText()
        theCursor.setPosition(posS)
        if posS > 0:
            theCursor.insertBlock()
        theCursor.insertText(theText)
        if posO - cOffset >= 0:
            theCursor.setPosition(posO - cOffset)
        theCursor.endEditBlock()
        self.setTextCursor(theCursor)

        return True

    def _removeInParLineBreaks(self):
        """Strip line breaks within paragraphs in the selected text.
        """
        theCursor = self.textCursor()
        theDoc = self.document()

        iS = 0
        iE = theDoc.blockCount() - 1
        rS = 0
        rE = theDoc.characterCount()
        if theCursor.hasSelection():
            sBlock = theDoc.findBlock(theCursor.selectionStart())
            eBlock = theDoc.findBlock(theCursor.selectionEnd())
            iS = sBlock.blockNumber()
            iE = eBlock.blockNumber()
            rS = sBlock.position()
            rE = eBlock.position() + eBlock.length()

        # Clean up the text
        currPar = []
        cleanText = ""
        for i in range(iS, iE+1):
            cBlock = theDoc.findBlockByNumber(i)
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
        theCursor.beginEditBlock()
        theCursor.clearSelection()
        theCursor.setPosition(rS)
        theCursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, rE-rS)
        theCursor.insertText(cleanText.rstrip() + "\n")
        theCursor.endEditBlock()

        return True

    ##
    #  Internal Functions
    ##

    def _followTag(self, theCursor=None, loadTag=True):
        """Activated by Ctrl+Enter. Checks that we're in a block
        starting with '@'. We then find the tag under the cursor and
        check that it is not the tag itself. If all this is fine, we
        have a tag and can tell the document viewer to try and find and
        load the file where the tag is defined.
        """
        if theCursor is None:
            theCursor = self.textCursor()

        theBlock = theCursor.block()
        theText = theBlock.text()

        if len(theText) == 0:
            return False

        if theText.startswith("@"):

            isGood, tBits, tPos = self.theProject.index.scanThis(theText)
            if not isGood:
                return False

            theTag = ""
            cPos = theCursor.selectionStart() - theBlock.position()
            for sTag, sPos in zip(reversed(tBits), reversed(tPos)):
                if cPos >= sPos:
                    # The cursor is between the start of two tags
                    if cPos <= sPos + len(sTag):
                        # The cursor is inside or at the edge of the tag
                        theTag = sTag
                    break

            if not theTag or theTag.startswith("@"):
                # The keyword cannot be looked up, so we ignore that
                return False

            if loadTag:
                logger.debug("Attempting to follow tag '%s'", theTag)
                self.loadDocumentTagRequest.emit(theTag, nwDocMode.VIEW)
            else:
                logger.debug("Potential tag '%s'", theTag)

            return True

        return False

    def _openSpellContext(self):
        """Open the spell check context menu at the current point of the
        cursor.
        """
        self._openContextMenu(self.cursorRect().center())
        return

    def _docAutoReplace(self, theBlock):
        """Auto-replace text elements based on main configuration.
        """
        if not theBlock.isValid():
            return

        theText = theBlock.text()
        theCursor = self.textCursor()
        thePos = theCursor.positionInBlock()
        theLen = len(theText)

        if theLen < 1 or thePos-1 > theLen:
            return

        theOne = theText[thePos-1:thePos]
        theTwo = theText[thePos-2:thePos]
        theThree = theText[thePos-3:thePos]

        if not theOne:
            # Sorry, Neo and Zathras
            return

        nDelete = 0
        tInsert = theOne

        if self._typRepDQuote and theTwo[:1].isspace() and theTwo.endswith('"'):
            nDelete = 1
            tInsert = self._typDQuoteO

        elif self._typRepDQuote and theOne == '"':
            nDelete = 1
            if thePos == 1:
                tInsert = self._typDQuoteO
            elif thePos == 2 and theTwo == '>"':
                tInsert = self._typDQuoteO
            elif thePos == 3 and theThree == '>>"':
                tInsert = self._typDQuoteO
            else:
                tInsert = self._typDQuoteC

        elif self._typRepSQuote and theTwo[:1].isspace() and theTwo.endswith("'"):
            nDelete = 1
            tInsert = self._typSQuoteO

        elif self._typRepSQuote and theOne == "'":
            nDelete = 1
            if thePos == 1:
                tInsert = self._typSQuoteO
            elif thePos == 2 and theTwo == ">'":
                tInsert = self._typSQuoteO
            elif thePos == 3 and theThree == ">>'":
                tInsert = self._typSQuoteO
            else:
                tInsert = self._typSQuoteC

        elif self._typRepDash and theThree == "---":
            nDelete = 3
            tInsert = nwUnicode.U_EMDASH

        elif self._typRepDash and theTwo == "--":
            nDelete = 2
            tInsert = nwUnicode.U_ENDASH

        elif self._typRepDash and theTwo == nwUnicode.U_ENDASH + "-":
            nDelete = 2
            tInsert = nwUnicode.U_EMDASH

        elif self._typRepDots and theThree == "...":
            nDelete = 3
            tInsert = nwUnicode.U_HELLIP

        elif theOne == nwUnicode.U_LSEP:
            # This resolves issue #1150
            nDelete = 1
            tInsert = nwUnicode.U_PSEP

        tCheck = tInsert
        if self._typPadBefore and tCheck in self._typPadBefore:
            if self._allowSpaceBeforeColon(theText, tCheck):
                nDelete = max(nDelete, 1)
                chkPos = thePos - nDelete - 1
                if chkPos >= 0 and theText[chkPos].isspace():
                    # Strip existing space before inserting a new (#1061)
                    nDelete += 1
                tInsert = self._typPadChar + tInsert

        if self._typPadAfter and tCheck in self._typPadAfter:
            if self._allowSpaceBeforeColon(theText, tCheck):
                nDelete = max(nDelete, 1)
                tInsert = tInsert + self._typPadChar

        if nDelete > 0:
            theCursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor, nDelete)
            theCursor.insertText(tInsert)

        return

    @staticmethod
    def _allowSpaceBeforeColon(text, char):
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

    def _checkDocSize(self, theSize):
        """Check if document size crosses the big document limit set in
        config. If so, we will set the big document flag to True.
        """
        bigLim = round(self.mainConf.bigDocLimit*1000)
        newState = theSize > bigLim

        if newState != self._bigDoc:
            if newState:
                logger.info(
                    f"The document size is {theSize:n} > {bigLim:n}, "
                    f"big doc mode has been enabled"
                )
            else:
                logger.info(
                    f"The document size is {theSize:n} <= {bigLim:n}, "
                    f"big doc mode has been disabled"
                )

        self._bigDoc = newState

        return

    def _autoSelect(self):
        """Return a cursor which may or may not have a selection based
        on user settings and document action.
        """
        theCursor = self.textCursor()
        if self.mainConf.autoSelect and not theCursor.hasSelection():
            theCursor.select(QTextCursor.WordUnderCursor)
            posS = theCursor.selectionStart()
            posE = theCursor.selectionEnd()

            # Underscore counts as a part of the word, so check that the
            # selection isn't wrapped in italics markers.
            reSelect = False
            qDoc = self.document()
            if qDoc.characterAt(posS) == "_":
                posS += 1
                reSelect = True
            if qDoc.characterAt(posE) == "_":
                posE -= 1
                reSelect = True
            if reSelect:
                theCursor.clearSelection()
                theCursor.setPosition(posS, QTextCursor.MoveAnchor)
                theCursor.setPosition(posE-1, QTextCursor.KeepAnchor)

            self.setTextCursor(theCursor)

        return theCursor

    def _makeSelection(self, selMode):
        """Wrapper function to select text based on a selection mode.
        """
        theCursor = self.textCursor()
        theCursor.clearSelection()
        theCursor.select(selMode)

        if selMode == QTextCursor.WordUnderCursor:
            theCursor = self._autoSelect()

        elif selMode == QTextCursor.BlockUnderCursor:
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

    def _makePosSelection(self, selMode, thePos):
        """Wrapper function to select text based on selection mode, but
        first move cursor to given position.
        """
        theCursor = self.cursorForPosition(thePos)
        self.setTextCursor(theCursor)
        self._makeSelection(selMode)
        return

    def _allowAutoReplace(self, theState):
        """Enable/disable the auto-replace feature temporarily.
        """
        if theState:
            self._doReplace = self.mainConf.doReplace
        else:
            self._doReplace = False
        return

# END Class GuiDocEditor


# =============================================================================================== #
#  The Off-GUI Thread Word Counter
#  A runnable for the word counter to be run in the thread pool off the main GUI thread.
# =============================================================================================== #

class BackgroundWordCounter(QRunnable):

    def __init__(self, docEditor, forSelection=False):
        super().__init__()

        self._docEditor = docEditor
        self._forSelection = forSelection
        self._isRunning = False

        self.signals = BackgroundWordCounterSignals()

        return

    def isRunning(self):
        return self._isRunning

    @pyqtSlot()
    def run(self):
        """Overloaded run function for the word counter, forwarding the
        call to the function that does the actual counting.
        """
        self._isRunning = True
        if self._forSelection:
            theText = self._docEditor.textCursor().selectedText()
        else:
            theText = self._docEditor.getText()

        cC, wC, pC = countWords(theText)
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
#  The Embedded Document Search/Replace Feature
#  Only used by DocEditor, and is at a fixed position in the QTextEdit's viewport
# =============================================================================================== #

class GuiDocEditSearch(QFrame):

    def __init__(self, docEditor):
        super().__init__(parent=docEditor)

        logger.debug("Initialising GuiDocEditSearch ...")

        self.mainConf   = novelwriter.CONFIG
        self.docEditor  = docEditor
        self.mainGui    = docEditor.mainGui
        self.theProject = docEditor.theProject
        self.mainTheme  = docEditor.mainTheme

        self.repVisible  = False
        self.isCaseSense = self.mainConf.searchCase
        self.isWholeWord = self.mainConf.searchWord
        self.isRegEx     = self.mainConf.searchRegEx
        self.doLoop      = self.mainConf.searchLoop
        self.doNextFile  = self.mainConf.searchNextFile
        self.doMatchCap  = self.mainConf.searchMatchCap

        mPx = self.mainConf.pxInt(6)
        tPx = int(0.8*self.mainTheme.fontPixelSize)
        self.boxFont = self.mainTheme.guiFont
        self.boxFont.setPointSizeF(0.9*self.mainTheme.fontPointSize)

        self.setContentsMargins(0, 0, 0, 0)
        self.setAutoFillBackground(True)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)

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
        self.searchOpt.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.searchOpt.setIconSize(QSize(tPx, tPx))
        self.searchOpt.setContentsMargins(0, 0, 0, 0)

        self.searchLabel = QLabel(self.tr("Search"))
        self.searchLabel.setFont(self.boxFont)
        self.searchLabel.setIndent(self.mainConf.pxInt(6))

        self.resultLabel = QLabel("?/?")
        self.resultLabel.setFont(self.boxFont)
        self.resultLabel.setMinimumWidth(self.mainTheme.getTextWidth("?/?", self.boxFont))

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
        self.showReplace.setArrowType(Qt.RightArrow)
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

        self.mainBox.addWidget(self.searchLabel,   0, 0, 1, 2, Qt.AlignLeft)
        self.mainBox.addWidget(self.searchOpt,     0, 2, 1, 3, Qt.AlignRight)
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
        self.mainBox.setSpacing(self.mainConf.pxInt(2))
        self.mainBox.setContentsMargins(mPx, mPx, mPx, mPx)

        boxWidth = self.mainConf.pxInt(200)
        self.searchBox.setFixedWidth(boxWidth)
        self.replaceBox.setFixedWidth(boxWidth)
        self.replaceBox.setVisible(False)
        self.replaceButton.setVisible(False)
        self.adjustSize()

        self.updateTheme()

        logger.debug("GuiDocEditSearch initialisation complete")

        return

    def updateTheme(self):
        """Update theme elements.
        """
        qPalette = qApp.palette()
        self.setPalette(qPalette)
        self.searchBox.setPalette(qPalette)
        self.replaceBox.setPalette(qPalette)

        # Set icons
        self.toggleCase.setIcon(self.mainTheme.getIcon("search_case"))
        self.toggleWord.setIcon(self.mainTheme.getIcon("search_word"))
        self.toggleRegEx.setIcon(self.mainTheme.getIcon("search_regex"))
        self.toggleLoop.setIcon(self.mainTheme.getIcon("search_loop"))
        self.toggleProject.setIcon(self.mainTheme.getIcon("search_project"))
        self.toggleMatchCap.setIcon(self.mainTheme.getIcon("search_preserve"))
        self.cancelSearch.setIcon(self.mainTheme.getIcon("search_cancel"))
        self.searchButton.setIcon(self.mainTheme.getIcon("search"))
        self.replaceButton.setIcon(self.mainTheme.getIcon("search_replace"))

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

    def closeSearch(self):
        """Close the search box.
        """
        self.mainConf.searchCase = self.isCaseSense
        self.mainConf.searchWord = self.isWholeWord
        self.mainConf.searchRegEx = self.isRegEx
        self.mainConf.searchLoop = self.doLoop
        self.mainConf.searchNextFile = self.doNextFile
        self.mainConf.searchMatchCap = self.doMatchCap

        self.showReplace.setChecked(False)
        self.setVisible(False)
        self.docEditor.updateDocMargins()
        self.docEditor.setFocus()

        return

    def cycleFocus(self, toNext):
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

    def anyFocus(self):
        """Return True if any of the input boxes have focus.
        """
        return self.searchBox.hasFocus() | self.replaceBox.hasFocus()

    ##
    #  Get and Set Functions
    ##

    def setSearchText(self, theText):
        """Open the search bar and set the search text to the text
        provided, if any.
        """
        if not self.isVisible():
            self.setVisible(True)
        if theText is not None:
            self.searchBox.setText(theText)
        self.searchBox.setFocus()
        self.searchBox.selectAll()
        if self.isRegEx:
            self._alertSearchValid(True)
        return True

    def setReplaceText(self, theText):
        """Set the replace text.
        """
        self.showReplace.setChecked(True)
        self.replaceBox.setFocus()
        self.replaceBox.setText(theText)
        return True

    def setResultCount(self, currRes, resCount):
        """Set the count values for the current search.
        """
        currRes = "?" if currRes is None else currRes
        resCount = "?" if resCount is None else "1000+" if resCount > 1000 else resCount
        minWidth = self.mainTheme.getTextWidth(f"{resCount}//{resCount}", self.boxFont)
        self.resultLabel.setText(f"{currRes}/{resCount}")
        self.resultLabel.setMinimumWidth(minWidth)
        self.adjustSize()
        self.docEditor.updateDocMargins()
        return

    def getSearchObject(self):
        """Return the current search text either as text or as a regular
        expression object.
        """
        theText = self.searchBox.text()
        if self.isRegEx:
            # Using the Unicode-capable QRegularExpression class was
            # only added in Qt 5.13. Otherwise, 5.3 and up supports
            # only the QRegExp class.
            if self.mainConf.verQtValue >= 0x050d00:
                rxOpt = QRegularExpression.UseUnicodePropertiesOption
                if not self.isCaseSense:
                    rxOpt |= QRegularExpression.CaseInsensitiveOption
                theRegEx = QRegularExpression(theText, rxOpt)
                self._alertSearchValid(theRegEx.isValid())
                return theRegEx

            else:  # pragma: no cover
                # >= 50300 to < 51300
                if self.isCaseSense:
                    rxOpt = Qt.CaseSensitive
                else:
                    rxOpt = Qt.CaseInsensitive
                theRegEx = QRegExp(theText, rxOpt)
                self._alertSearchValid(theRegEx.isValid())
                return theRegEx

        return theText

    def getSearchText(self):
        """Return the current search text.
        """
        return self.searchBox.text()

    def getReplaceText(self):
        """Return the current replace text.
        """
        return self.replaceBox.text()

    ##
    #  Slots
    ##

    @pyqtSlot()
    def _doClose(self):
        """Hide the search/replace bar.
        """
        self.closeSearch()
        return

    @pyqtSlot()
    def _doSearch(self):
        """Call the search action function for the document editor.
        """
        modKey = qApp.keyboardModifiers()
        if modKey == Qt.ShiftModifier:
            self.docEditor.findNext(goBack=True)
        else:
            self.docEditor.findNext()
        return

    @pyqtSlot()
    def _doReplace(self):
        """Call the replace action function for the document editor.
        """
        self.docEditor.replaceNext()
        return

    @pyqtSlot(bool)
    def _doToggleReplace(self, theState):
        """Toggle the show/hide of the replace box.
        """
        if theState:
            self.showReplace.setArrowType(Qt.DownArrow)
        else:
            self.showReplace.setArrowType(Qt.RightArrow)
        self.replaceBox.setVisible(theState)
        self.replaceButton.setVisible(theState)
        self.repVisible = theState
        self.adjustSize()
        self.docEditor.updateDocMargins()
        return

    @pyqtSlot(bool)
    def _doToggleCase(self, theState):
        """Enable/disable case sensitive mode.
        """
        self.isCaseSense = theState
        return

    @pyqtSlot(bool)
    def _doToggleWord(self, theState):
        """Enable/disable whole word search mode.
        """
        self.isWholeWord = theState
        return

    @pyqtSlot(bool)
    def _doToggleRegEx(self, theState):
        """Enable/disable regular expression search mode.
        """
        self.isRegEx = theState
        return

    @pyqtSlot(bool)
    def _doToggleLoop(self, theState):
        """Enable/disable looping the search.
        """
        self.doLoop = theState
        return

    @pyqtSlot(bool)
    def _doToggleProject(self, theState):
        """Enable/disable continuing search in next project file.
        """
        self.doNextFile = theState
        return

    @pyqtSlot(bool)
    def _doToggleMatchCap(self, theState):
        """Enable/disable preserving capitalisation when replacing.
        """
        self.doMatchCap = theState
        return

    ##
    #  Internal Functions
    ##

    def _alertSearchValid(self, isValid):
        """Highlight the search box to indicate the search string is or
        isn't valid. Take the colour from the replace box.
        """
        qPalette = self.replaceBox.palette()
        qPalette.setColor(QPalette.Base, self.rxCol[isValid])
        self.searchBox.setPalette(qPalette)
        return

# END Class GuiDocEditSearch


# =============================================================================================== #
#  The Embedded Document Header
#  Only used by DocEditor, and is at a fixed position in the QTextEdit's viewport
# =============================================================================================== #

class GuiDocEditHeader(QWidget):

    def __init__(self, docEditor):
        super().__init__(parent=docEditor)

        logger.debug("Initialising GuiDocEditHeader ...")

        self.mainConf   = novelwriter.CONFIG
        self.docEditor  = docEditor
        self.mainGui    = docEditor.mainGui
        self.theProject = docEditor.theProject
        self.mainTheme  = docEditor.mainTheme

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
        self.editButton = QToolButton(self)
        self.editButton.setContentsMargins(0, 0, 0, 0)
        self.editButton.setIconSize(QSize(fPx, fPx))
        self.editButton.setFixedSize(fPx, fPx)
        self.editButton.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.editButton.setVisible(False)
        self.editButton.setToolTip(self.tr("Edit document label"))
        self.editButton.clicked.connect(self._editDocument)

        self.searchButton = QToolButton(self)
        self.searchButton.setContentsMargins(0, 0, 0, 0)
        self.searchButton.setIconSize(QSize(fPx, fPx))
        self.searchButton.setFixedSize(fPx, fPx)
        self.searchButton.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.searchButton.setVisible(False)
        self.searchButton.setToolTip(self.tr("Search document"))
        self.searchButton.clicked.connect(self._searchDocument)

        self.minmaxButton = QToolButton(self)
        self.minmaxButton.setContentsMargins(0, 0, 0, 0)
        self.minmaxButton.setIconSize(QSize(fPx, fPx))
        self.minmaxButton.setFixedSize(fPx, fPx)
        self.minmaxButton.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.minmaxButton.setVisible(False)
        self.minmaxButton.setToolTip(self.tr("Toggle Focus Mode"))
        self.minmaxButton.clicked.connect(self._minmaxDocument)

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
        self.outerBox.addWidget(self.editButton, 0)
        self.outerBox.addWidget(self.searchButton, 0)
        self.outerBox.addWidget(self.theTitle, 1)
        self.outerBox.addWidget(self.minmaxButton, 0)
        self.outerBox.addWidget(self.closeButton, 0)
        self.setLayout(self.outerBox)

        # Fix Margins and Size
        # This is needed for high DPI systems. See issue #499.
        cM = self.mainConf.pxInt(8)
        self.setContentsMargins(0, 0, 0, 0)
        self.outerBox.setContentsMargins(cM, cM, cM, cM)
        self.setMinimumHeight(fPx + 2*cM)

        self.updateTheme()

        logger.debug("GuiDocEditHeader initialisation complete")

        return

    ##
    #  Methods
    ##

    def updateTheme(self):
        """Update theme elements.
        """
        self.editButton.setIcon(self.mainTheme.getIcon("edit"))
        self.searchButton.setIcon(self.mainTheme.getIcon("search"))
        self.minmaxButton.setIcon(self.mainTheme.getIcon("maximise"))
        self.closeButton.setIcon(self.mainTheme.getIcon("close"))

        buttonStyle = (
            "QToolButton {{border: none; background: transparent;}} "
            "QToolButton:hover {{border: none; background: rgba({0},{1},{2},0.2);}}"
        ).format(*self.mainTheme.colText)

        self.editButton.setStyleSheet(buttonStyle)
        self.searchButton.setStyleSheet(buttonStyle)
        self.minmaxButton.setStyleSheet(buttonStyle)
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
        """Set the document title from the handle, or alternatively, set
        the whole document path within the project.
        """
        self._docHandle = tHandle
        if tHandle is None:
            self.theTitle.setText("")
            self.editButton.setVisible(False)
            self.searchButton.setVisible(False)
            self.closeButton.setVisible(False)
            self.minmaxButton.setVisible(False)
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

        self.editButton.setVisible(True)
        self.searchButton.setVisible(True)
        self.closeButton.setVisible(True)
        self.minmaxButton.setVisible(True)

        return True

    def updateFocusMode(self):
        """Update the minimise/maximise icon of the Focus Mode button.
        This function is called by the GuiMain class via the
        toggleFocusMode function and should not be activated directly.
        """
        if self.mainGui.isFocusMode:
            self.minmaxButton.setIcon(self.mainTheme.getIcon("minimise"))
        else:
            self.minmaxButton.setIcon(self.mainTheme.getIcon("maximise"))
        return

    ##
    #  Slots
    ##

    @pyqtSlot()
    def _editDocument(self):
        """Open the edit item dialog from the main GUI.
        """
        self.mainGui.editItemLabel(self._docHandle)
        return

    @pyqtSlot()
    def _searchDocument(self):
        """Toggle the visibility of the search box.
        """
        self.docEditor.toggleSearch()
        return

    @pyqtSlot()
    def _closeDocument(self):
        """Trigger the close editor on the main window.
        """
        self.mainGui.closeDocEditor()
        self.editButton.setVisible(False)
        self.searchButton.setVisible(False)
        self.closeButton.setVisible(False)
        self.minmaxButton.setVisible(False)
        return

    @pyqtSlot()
    def _minmaxDocument(self):
        """Switch on or off Focus Mode.
        """
        self.mainGui.toggleFocusMode()
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

# END Class GuiDocEditHeader


# =============================================================================================== #
#  The Embedded Document Footer
#  Only used by DocEditor, and is at a fixed position in the QTextEdit's viewport
# =============================================================================================== #

class GuiDocEditFooter(QWidget):

    def __init__(self, docEditor):
        super().__init__(parent=docEditor)

        logger.debug("Initialising GuiDocEditFooter ...")

        self.mainConf   = novelwriter.CONFIG
        self.docEditor  = docEditor
        self.mainGui    = docEditor.mainGui
        self.theProject = docEditor.theProject
        self.mainTheme  = docEditor.mainTheme

        self._theItem   = None
        self._docHandle = None

        self._docSelection = False

        self.sPx = int(round(0.9*self.mainTheme.baseIconSize))
        fPx = int(0.9*self.mainTheme.fontPixelSize)
        bSp = self.mainConf.pxInt(4)
        hSp = self.mainConf.pxInt(6)

        lblFont = self.font()
        lblFont.setPointSizeF(0.9*self.mainTheme.fontPointSize)

        # Main Widget Settings
        self.setContentsMargins(0, 0, 0, 0)
        self.setAutoFillBackground(True)

        # Status
        self.statusIcon = QLabel("")
        self.statusIcon.setContentsMargins(0, 0, 0, 0)
        self.statusIcon.setFixedHeight(self.sPx)
        self.statusIcon.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        self.statusText = QLabel(self.tr("Status"))
        self.statusText.setIndent(0)
        self.statusText.setMargin(0)
        self.statusText.setContentsMargins(0, 0, 0, 0)
        self.statusText.setAutoFillBackground(True)
        self.statusText.setFixedHeight(fPx)
        self.statusText.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.statusText.setFont(lblFont)

        # Lines
        self.linesIcon = QLabel("")
        self.linesIcon.setContentsMargins(0, 0, 0, 0)
        self.linesIcon.setFixedHeight(self.sPx)
        self.linesIcon.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        self.linesText = QLabel("")
        self.linesText.setIndent(0)
        self.linesText.setMargin(0)
        self.linesText.setContentsMargins(0, 0, 0, 0)
        self.linesText.setAutoFillBackground(True)
        self.linesText.setFixedHeight(fPx)
        self.linesText.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.linesText.setFont(lblFont)

        # Words
        self.wordsIcon = QLabel("")
        self.wordsIcon.setContentsMargins(0, 0, 0, 0)
        self.wordsIcon.setFixedHeight(self.sPx)
        self.wordsIcon.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        self.wordsText = QLabel("")
        self.wordsText.setIndent(0)
        self.wordsText.setMargin(0)
        self.wordsText.setContentsMargins(0, 0, 0, 0)
        self.wordsText.setAutoFillBackground(True)
        self.wordsText.setFixedHeight(fPx)
        self.wordsText.setAlignment(Qt.AlignLeft | Qt.AlignTop)
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
        cM = self.mainConf.pxInt(8)
        self.setContentsMargins(0, 0, 0, 0)
        self.outerBox.setContentsMargins(cM, cM, cM, cM)
        self.setMinimumHeight(fPx + 2*cM)

        # Fix the Colours
        self.updateTheme()
        self.updateLineCount()
        self.updateCounts()

        logger.debug("GuiDocEditFooter initialisation complete")

        return

    ##
    #  Methods
    ##

    def updateTheme(self):
        """Update theme elements.
        """
        self.linesIcon.setPixmap(self.mainTheme.getPixmap("status_lines", (self.sPx, self.sPx)))
        self.wordsIcon.setPixmap(self.mainTheme.getPixmap("status_stats", (self.sPx, self.sPx)))

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
        self.statusText.setPalette(thePalette)
        self.linesText.setPalette(thePalette)
        self.wordsText.setPalette(thePalette)

        return

    def setHandle(self, tHandle):
        """Set the handle that will populate the footer's data.
        """
        self._docHandle = tHandle
        if self._docHandle is None:
            logger.debug("No handle set, so clearing the editor footer")
            self._theItem = None
        else:
            self._theItem = self.theProject.tree[self._docHandle]

        self.setHasSelection(False)
        self.updateInfo()
        self.updateCounts()

        return

    def setHasSelection(self, hasSelection):
        """Toggle the word counter mode between full count and selection
        count mode.
        """
        self._docSelection = hasSelection
        return

    def updateInfo(self):
        """Update the content of text labels.
        """
        if self._theItem is None:
            sIcon = QPixmap()
            sText = ""
        else:
            theStatus, theIcon = self._theItem.getImportStatus()
            sIcon = theIcon.pixmap(self.sPx, self.sPx)
            sText = f"{theStatus} / {self._theItem.describeMe()}"

        self.statusIcon.setPixmap(sIcon)
        self.statusText.setText(sText)

        return

    def updateLineCount(self):
        """Update the line counter.
        """
        if self._theItem is None:
            iLine = 0
            iDist = 0
        else:
            theCursor = self.docEditor.textCursor()
            iLine = theCursor.blockNumber() + 1
            iDist = 100*iLine/self.docEditor.document().blockCount()

        self.linesText.setText(
            self.tr("Line: {0} ({1})").format(f"{iLine:n}", f"{iDist:.0f} %")
        )

        return

    def updateCounts(self, wCount=None, cCount=None):
        """Select which word count display mode to use.
        """
        if self._docSelection:
            self._updateSelectionWordCounts(wCount, cCount)
        else:
            self._updateWordCounts()
        return

    ##
    #  Internal Functions
    ##

    def _updateWordCounts(self):
        """Update the word count for the whole document.
        """
        if self._theItem is None:
            wCount = 0
            wDiff = 0
        else:
            wCount = self._theItem.wordCount
            wDiff = wCount - self._theItem.initCount

        self.wordsText.setText(
            self.tr("Words: {0} ({1})").format(f"{wCount:n}", f"{wDiff:+n}")
        )

        byteSize = self.docEditor.document().characterCount()
        self.wordsText.setToolTip(
            self.tr("Document size is {0} bytes").format(f"{byteSize:n}")
        )

        return

    def _updateSelectionWordCounts(self, wCount, cCount):
        """Update the word count for a selection.
        """
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
