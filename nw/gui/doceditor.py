"""
novelWriter – GUI Document Editor
=================================
GUI classes for the main document editor

File History:
Created:   2018-09-29 [0.0.1]  GuiDocEditor
Created:   2019-04-22 [0.0.1]  BackgroundWordCounter
Created:   2019-09-29 [0.2.1]  GuiDocEditSearch
Created:   2020-04-25 [0.4.5]  GuiDocEditHeader
Rewritten: 2020-06-15 [0.9.0]  GuiDocEditSearch
Created:   2020-06-27 [0.10.0] GuiDocEditFooter
Rewritten: 2020-10-07 [1.0b3]  BackgroundWordCounter

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

from time import time

from PyQt5.QtCore import (
    Qt, QSize, QTimer, pyqtSlot, pyqtSignal, QRegExp, QRegularExpression,
    QPointF, QObject, QRunnable, QPropertyAnimation
)
from PyQt5.QtGui import (
    QTextCursor, QTextOption, QKeySequence, QFont, QColor, QPalette,
    QTextDocument, QCursor, QPixmap
)
from PyQt5.QtWidgets import (
    qApp, QTextEdit, QAction, QMenu, QShortcut, QMessageBox, QWidget, QLabel,
    QToolBar, QToolButton, QHBoxLayout, QGridLayout, QLineEdit, QPushButton,
    QFrame
)

from nw.core import NWDoc, NWSpellSimple, countWords
from nw.enum import nwAlert, nwDocAction, nwDocInsert, nwItemClass
from nw.common import transferCase
from nw.constants import nwConst, trConst, nwKeyWords, nwLabels, nwUnicode
from nw.gui.dochighlight import GuiDocHighlighter

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

    def __init__(self, theParent):
        QTextEdit.__init__(self, theParent)

        logger.debug("Initialising GuiDocEditor ...")

        # Class Variables
        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theTheme   = theParent.theTheme
        self.theIndex   = theParent.theIndex
        self.theProject = theParent.theProject

        self._nwDocument = None
        self._nwItem     = None

        self._docChanged = False  # Flag for changed status of document
        self._docHandle  = None   # The handle of the open file
        self._docHeaders = []     # Record of headers in the file

        self._spellCheck = False  # Flag for spell checking enabled
        self._theDict    = None   # The current spell check dictionary
        self._nonWord    = "\"'"  # Characters to not include in spell checking

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

        # Typography
        self._typDQOpen  = '"'
        self._typDQClose = '"'
        self._typSQOpen  = "'"
        self._typSQClose = "'"
        self._typPadChar = " "

        # Core Elements and Signals
        qDoc = self.document()
        qDoc.contentsChange.connect(self._docChange)
        qDoc.documentLayout().documentSizeChanged.connect(self._docSizeChanged)

        # Document Title
        self.docHeader = GuiDocEditHeader(self)
        self.docFooter = GuiDocEditFooter(self)
        self.docSearch = GuiDocEditSearch(self)

        # Syntax
        self.hLight = GuiDocHighlighter(qDoc, self.theParent)

        # Context Menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._openContextMenu)

        # Editor Settings
        self.setMinimumWidth(self.mainConf.pxInt(300))
        self.setAutoFillBackground(True)
        self.setAcceptRichText(False)

        # Custom Shortcuts
        QShortcut(
            QKeySequence("Ctrl+."),
            self,
            context=Qt.WidgetShortcut,
            activated=self._openSpellContext
        )
        QShortcut(
            Qt.Key_Return | Qt.ControlModifier,
            self,
            context=Qt.WidgetShortcut,
            activated=self._followTag
        )
        QShortcut(
            Qt.Key_Enter | Qt.ControlModifier,
            self,
            context=Qt.WidgetShortcut,
            activated=self._followTag
        )

        # Set Up Word Counter
        self.wcTimer = QTimer()
        self.wcTimer.timeout.connect(self._runCounter)

        self.wCounter = BackgroundWordCounter(self)
        self.wCounter.setAutoDelete(False)
        self.wCounter.signals.countsReady.connect(self._updateCounts)

        self.wcInterval = self.mainConf.wordCountTimer

        self.initEditor()

        logger.debug("GuiDocEditor initialisation complete")

        return

    def clearEditor(self):
        """Clear the current document and reset all document related
        flags and counters.
        """
        self._nwDocument = None
        self.setReadOnly(True)
        self.clear()
        self.wcTimer.stop()

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

    def initEditor(self):
        """Initialise or re-initialise the editor with the user's
        settings. This function is both called when the editor is
        created, and when the user changes the main editor preferences.
        """
        # Some Constants
        self._nonWord  = "\"'"
        self._nonWord += "".join(self.mainConf.fmtDoubleQuotes)
        self._nonWord += "".join(self.mainConf.fmtSingleQuotes)

        # Typography
        if self.mainConf.fmtPadThin:
            self._typPadChar = nwUnicode.U_THNBSP
        else:
            self._typPadChar = nwUnicode.U_NBSP

        self._typDQOpen  = self.mainConf.fmtDoubleQuotes[0]
        self._typDQClose = self.mainConf.fmtDoubleQuotes[1]
        self._typSQOpen  = self.mainConf.fmtSingleQuotes[0]
        self._typSQClose = self.mainConf.fmtSingleQuotes[1]

        # Reload spell check and dictionaries
        self._setupSpellChecking()
        self.setDictionaries()

        # Set font
        theFont = QFont()
        qDoc = self.document()
        if self.mainConf.textFont is None:
            # If none is defined, set the default back to config
            self.mainConf.textFont = qDoc.defaultFont().family()

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
        cM = self.mainConf.getTextMargin()
        qDoc.setDocumentMargin(0)
        self.setViewportMargins(cM, cM, cM, cM)

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
        if self.mainConf.verQtValue >= 51000:
            self.setTabStopDistance(self.mainConf.getTabWidth())
        else:  # pragma: no cover
            self.setTabStopWidth(self.mainConf.getTabWidth())

        # Initialise the syntax highlighter
        self.hLight.initHighlighter()

        # Configure word count timer
        self.wcInterval = self.mainConf.wordCountTimer
        self.wcTimer.setInterval(int(self.wcInterval*1000))

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
        novelWriter does not support. If load is successful, or the
        document is new (empty string), we set up the editor for editing
        the file.
        """
        self._nwDocument = NWDoc(self.theProject, tHandle)
        self._nwItem = self._nwDocument.getCurrentItem()

        theDoc = self._nwDocument.readDocument()
        if theDoc is None:
            # There was an io error
            self.clearEditor()
            return False

        docSize = len(theDoc)
        if docSize > nwConst.MAX_DOCSIZE:
            self.theParent.makeAlert(self.tr(
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
        self.hLight.setHandle(tHandle)

        # Check that the document is not too big for full, initial spell
        # checking. If it is too big, we switch to only check as we type
        self._checkDocSize(docSize)
        spTemp = self.hLight.spellCheck
        if self._bigDoc:
            self.hLight.spellCheck = False

        bfTime = time()
        self._allowAutoReplace(False)
        self.setPlainText(theDoc)
        qApp.processEvents()

        self._allowAutoReplace(True)
        afTime = time()
        logger.debug("Document highlighted in %.3f ms", 1000*(afTime-bfTime))

        self._lastEdit = time()
        self._lastActive = time()
        self._runCounter()
        self.wcTimer.start()
        self._docHandle = tHandle

        self.setReadOnly(False)
        self.docHeader.setTitleFromHandle(self._docHandle)
        self.docFooter.setHandle(self._docHandle)
        self.updateDocMargins()
        self.hLight.spellCheck = spTemp

        if tLine is None and self._nwItem is not None:
            # For large documents we queue the repositioning until the
            # document layout has grown past the point we want to move
            # the cursor to. This makes the loading significantly
            # faster.
            if docSize > 50000:
                self._queuePos = self._nwItem.cursorPos
            else:
                self.setCursorPosition(self._nwItem.cursorPos)
        else:
            self.setCursorLine(tLine)

        self.docFooter.updateLineCount()
        self._docHeaders = self.theIndex.getHandleHeaders(self._docHandle)

        qApp.processEvents()
        self.setDocumentChanged(False)
        qApp.restoreOverrideCursor()

        # This is a hack to fix invisble cursor on an empty document
        if self.document().characterCount() <= 1:
            self.setPlainText("\n")
            self.setPlainText("")
            self.setCursorPosition(0)

        # Update the status bar
        if self._nwItem is not None:
            self.theParent.setStatus(
                self.tr("Opened Document: {0}").format(self._nwItem.itemName)
            )

        return True

    def updateTagHighLighting(self):
        """Rerun the syntax highlighter on all meta data lines.
        """
        self.hLight.rehighlightByType(GuiDocHighlighter.BLOCK_META)
        return

    def redrawText(self):
        """Redraw the text by marking the document content as "dirty".
        """
        self.document().markContentsDirty(0, self.document().characterCount())
        self.updateDocMargins()
        return

    def replaceText(self, theText):
        """Replaces the text of the current document with the provided
        text. This also clears undo history.
        """
        docSize = len(theText)
        if docSize > nwConst.MAX_DOCSIZE:
            self.theParent.makeAlert(self.tr(
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
        """Save the text currently in the editor to the NWDoc object,
        and update the NWItem meta data.
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
        self._updateCounts(cC, wC, pC)

        self._nwItem.setCharCount(self._charCount)
        self._nwItem.setWordCount(self._wordCount)
        self._nwItem.setParaCount(self._paraCount)

        self.saveCursorPosition()
        if not self._nwDocument.writeDocument(docText):
            self.theParent.makeAlert([
                self.tr("Could not save document."), self._nwDocument.getError()
            ], nwAlert.ERROR)
            return False

        self.setDocumentChanged(False)

        self.theIndex.scanText(tHandle, docText)

        if self._updateHeaders(checkLevel=True):
            self.theParent.requestNovelTreeRefresh()
        else:
            self.theParent.novelView.updateWordCounts(tHandle)

        hLevel = "H0"
        if self._docHeaders:
            hLevel = self._docHeaders[0][1]

        if self.theProject.projTree.updateItemLayout(tHandle, hLevel):
            self.theParent.treeView.setTreeItemValues(tHandle)
            self._nwDocument.writeDocument(docText)
            self.docFooter.updateInfo()

        # Update the status bar
        self.theParent.setStatus(
            self.tr("Saved Document: {0}").format(self._nwItem.itemName)
        )

        return True

    def updateDocMargins(self):
        """Automatically adjust the margins so the text is centred if
        Config.textFixedW is enabled or we're in Focus Mode. Otherwise,
        just ensure the margins are set correctly.
        """
        wW = self.width()
        wH = self.height()
        cM = self.mainConf.getTextMargin()

        vBar = self.verticalScrollBar()
        sW = vBar.width() if vBar.isVisible() else 0

        hBar = self.horizontalScrollBar()
        sH = hBar.height() if hBar.isVisible() else 0

        if self.mainConf.textFixedW or self.theParent.isFocusMode:
            if self.theParent.isFocusMode:
                tW = self.mainConf.getFocusWidth()
            else:
                tW = self.mainConf.getTextWidth()
            tM = (wW - sW - tW)//2
            if tM < cM:
                tM = cM
        else:
            tM = cM

        tB = self.frameWidth()
        tW = wW - 2*tB - sW
        tH = self.docHeader.height()
        fH = self.docFooter.height()
        fY = wH - fH - tB - sH
        self.docHeader.setGeometry(tB, tB, tW, tH)
        self.docFooter.setGeometry(tB, fY, tW, fH)

        if self.docSearch.isVisible():
            rH = self.docSearch.height()
            rW = self.docSearch.width()
            rL = wW - sW - rW - 2*tB
            self.docSearch.move(rL, 2*tB)
        else:
            rH = 0

        uM = max(cM, tH, rH)
        lM = max(cM, fH)
        self.setViewportMargins(tM, uM, tM, lM)

        tmpDocChanged = self._docChanged
        if self.mainConf.scrollPastEnd:
            docFrame = self.document().rootFrame().frameFormat()
            docFrame.setBottomMargin(max(0, 0.9*(wH - uM - lM - 4*tB)))
            self.document().rootFrame().setFrameFormat(docFrame)

        # This is needed as the setFrameFormat function itself will
        # trigger the contetsChanged signal which sets _docChanged, so we
        # set it back to whatever it was before.
        self.setDocumentChanged(tmpDocChanged)

        return

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
    #  Properties
    ##

    def docChanged(self):
        """Return the changed status of the document in the editor.
        """
        return self._docChanged

    def docHandle(self):
        """Return the handle of the currently open document. Returns
        None if no document is open.
        """
        return self._docHandle

    def lastActive(self):
        """Eeturn the last active timestamp for the user.
        """
        return self._lastActive

    def isEmpty(self):
        """Wrapper function to check if the current document is empty.
        """
        return self.document().isEmpty()

    def currentDictionary(self):
        """Return the current dictionary object.
        """
        return self._theDict

    ##
    #  Getters
    ##

    def getText(self):
        """Get the text content of the current document. This method
        uses QTextEdit->toPlainText for Qt versions lower than 5.9, and
        the QTextDocument->toRawText for higher version. The latter
        preserves non-breaking spaces, which the former does not.
        We still want to get rid of page and line separators though.
        See: https://doc.qt.io/qt-5/qtextdocument.html#toPlainText
        """
        if self.mainConf.verQtValue >= 50900:
            theText = self.document().toRawText()
            theText = theText.replace(nwUnicode.U_LSEP, "\n")  # Line separators
            theText = theText.replace(nwUnicode.U_PSEP, "\n")  # Paragraph separators
        else:
            theText = self.toPlainText()
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
        """Keeps track of the document changed variable, and ensures
        that the corresponding icon on the status bar shows the same
        status.
        """
        self._docChanged = bValue
        self.docEditedStatusChanged.emit(self._docChanged)
        return self._docChanged

    def setCursorPosition(self, thePosition):
        """Move the cursor to a given position in the document.
        """
        if not isinstance(thePosition, int):
            return False

        nChars = self.document().characterCount()
        if nChars > 1:
            theCursor = self.textCursor()
            theCursor.setPosition(min(max(thePosition, 0), nChars-1))
            self.setTextCursor(theCursor)
            self.docFooter.updateLineCount()

        return True

    def saveCursorPosition(self):
        """Save the cursor position to the current project item object.
        """
        if self._nwItem is not None:
            cursPos = self.getCursorPosition()
            self._nwItem.setCursorPos(cursPos)
        return

    def setCursorLine(self, theLine):
        """Move the cursor to a given line in the document.
        """
        if not isinstance(theLine, int):
            return False

        if theLine >= 0:
            theBlock = self.document().findBlockByLineNumber(theLine)
            if theBlock:
                self.setCursorPosition(theBlock.position())
                self.docFooter.updateLineCount()
                logger.verbose("Cursor moved to line %d", theLine)

        return True

    ##
    #  Spell Checking
    ##

    def setDictionaries(self):
        """Set the spell checker dictionary language, and update the
        status bar to show the one actually loaded by the spell checker
        class.
        """
        if self.theProject.projSpell is None:
            theLang = self.mainConf.spellLanguage
        else:
            theLang = self.theProject.projSpell

        self._theDict.setLanguage(theLang, self.theProject.projDict)
        _, theProvider = self._theDict.describeDict()

        self.spellDictionaryChanged.emit(str(theLang), str(theProvider))

        if not self._bigDoc:
            self.spellCheckDocument()

        return True

    def setSpellCheck(self, theMode):
        """This is the master spell check setting function, and this one
        should call all other setSpellCheck functions in other classes.
        If the spell check mode (theMode) is not defined (None), then
        toggle the current status saved in this class.
        """
        if theMode is None:
            theMode = not self._spellCheck

        if self._theDict.spellLanguage is None:
            theMode = False

        self._spellCheck = theMode
        self.theParent.mainMenu.setSpellCheck(theMode)
        self.theProject.setSpellCheck(theMode)
        self.hLight.setSpellCheck(theMode)
        if not self._bigDoc:
            self.spellCheckDocument()

        logger.verbose("Spell check is set to '%s'", str(theMode))

        return True

    def spellCheckDocument(self):
        """Rerun the highlighter to update spell checking status of the
        currently loaded text. The fastest way to do this, at least as
        of Qt 5.13, is to clear the text and put it back. This clears
        the undo stack, so we only do it for big documents.
        """
        logger.verbose("Running spell checker")
        if self._spellCheck:
            bfTime = time()
            qApp.setOverrideCursor(QCursor(Qt.WaitCursor))
            if self._bigDoc:
                theText = self.getText()
                self.setPlainText(theText)
            else:
                self.hLight.rehighlight()
            qApp.restoreOverrideCursor()
            afTime = time()
            logger.debug("Document highlighted in %.3f ms", 1000*(afTime-bfTime))
            self.theParent.statusBar.setStatus(self.tr("Spell check complete"))

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

        logger.verbose("Requesting action: %s", theAction.name)

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
            self._wrapSelection(self._typSQOpen, self._typSQClose)
        elif theAction == nwDocAction.D_QUOTE:
            self._wrapSelection(self._typDQOpen, self._typDQClose)
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
        elif theAction == nwDocAction.REPL_SNG:
            self._replaceQuotes("'", self._typSQOpen, self._typSQClose)
        elif theAction == nwDocAction.REPL_DBL:
            self._replaceQuotes("\"", self._typDQOpen, self._typDQClose)
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

        if isinstance(theInsert, str):
            theText = theInsert
        elif isinstance(theInsert, nwDocInsert):
            if theInsert == nwDocInsert.QUOTE_LS:
                theText = self._typSQOpen
            elif theInsert == nwDocInsert.QUOTE_RS:
                theText = self._typSQClose
            elif theInsert == nwDocInsert.QUOTE_LD:
                theText = self._typDQOpen
            elif theInsert == nwDocInsert.QUOTE_RD:
                theText = self._typDQClose
            else:
                return False
        else:
            return False

        theCursor = self.textCursor()
        theCursor.beginEditBlock()
        theCursor.insertText(theText)
        theCursor.endEditBlock()

        return True

    def insertKeyWord(self, keyWord):
        """Insert a keyword in the text editor, at the cursor position.
        If the insert line is not blank, a new line is started.
        """
        if keyWord not in nwKeyWords.VALID_KEYS:
            logger.error("Invalid keyword '%s'", keyWord)
            return False

        logger.verbose("Inserting keyword '%s'", keyWord)

        theCursor = self.textCursor()
        theBlock = theCursor.block()
        if not theBlock.isValid():
            logger.error("Failed to insert keyword '%s'", keyWord)
            return False

        theCursor.beginEditBlock()

        if theBlock.length() > 1:
            theCursor.setPosition(theBlock.position() + theBlock.length() - 1)
            theCursor.insertText("\n")

        theCursor.insertText("%s: " % keyWord)
        theCursor.endEditBlock()

        self.setTextCursor(theCursor)

        return True

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
          * The return and enter key redirects here even if the search
            box has focus. Since we need these keys to continue search,
            we block any further interaction here while it's in focus.
          * The undo/redo/select all sequences bypasses the docAction
            pathway from the menu, so we redirect them back from here.
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
            QTextEdit.keyPressEvent(self, keyEvent)

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
            QTextEdit.keyPressEvent(self, keyEvent)

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

        QTextEdit.mouseReleaseEvent(self, theEvent)
        self.docFooter.updateLineCount()

        return

    def resizeEvent(self, theEvent):
        """If the text editor is resize, we must make sure the document
        has its margins adjusted according to user preferences.
        """
        QTextEdit.resizeEvent(self, theEvent)
        self.updateDocMargins()
        return

    ##
    #  Slots
    ##

    @pyqtSlot(int, int, int)
    def _docChange(self, thePos, chrRem, chrAdd):
        """Triggered by QTextDocument->contentsChanged. This also
        triggers the syntax highlighter.
        """
        self._lastEdit = time()
        self._lastFind = None

        if self.document().characterCount() > nwConst.MAX_DOCSIZE:
            self.theParent.makeAlert(self.tr(
                "The document has grown too big and you cannot add more text to it. "
                "The maximum size of a single novelWriter document is {0} MB."
            ).format(
                f"{nwConst.MAX_DOCSIZE/1.0e6:.2f}"
            ), nwAlert.ERROR)
            self.undo()
            return

        if not self._docChanged:
            self.setDocumentChanged(chrRem != 0 or chrAdd != 0)

        if not self.wcTimer.isActive():
            self.wcTimer.start()

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

        if posCursor.block().text().startswith("@"):
            spellCheck = False

        if spellCheck:
            posCursor.select(QTextCursor.WordUnderCursor)
            theWord = posCursor.selectedText().strip().strip(self._nonWord)
            spellCheck &= theWord != ""

        if spellCheck:
            logger.verbose("Looking up '%s' in the dictionary", theWord)
            spellCheck &= not self._theDict.checkWord(theWord)

        if spellCheck:
            mnuContext.addSeparator()
            mnuHead = QAction(self.tr("Spelling Suggestion(s)"), mnuContext)
            mnuContext.addAction(mnuHead)

            theSuggest = self._theDict.suggestWords(theWord)[:15]
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
        self._theDict.addWord(theWord)
        self.hLight.setDict(self._theDict)
        self.hLight.rehighlightBlock(theCursor.block())
        return

    @pyqtSlot()
    def _runCounter(self):
        """Decide whether to run the word counter, or not due to
        inactivity.
        """
        if self._docHandle is None:
            return

        if self.wCounter.isRunning():
            logger.verbose("Word counter is busy")
            return

        if time() - self._lastEdit < 5 * self.wcInterval:
            logger.verbose("Running word counter")
            self.theParent.threadPool.start(self.wCounter)

        return

    @pyqtSlot(int, int, int)
    def _updateCounts(self, cCount, wCount, pCount):
        """Slot for the word counter's finished signal
        """
        if self._docHandle is None or self._nwItem is None:
            return

        logger.verbose("Updating word count")

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
                logger.verbose("Allowed cursor move to %d <= %d", self._queuePos, thePos)
                self.setCursorPosition(self._queuePos)
                self._queuePos = None
            else:
                logger.verbose("Denied cursor move to %d > %d", self._queuePos, thePos)
        return

    ##
    #  Search & Replace
    ##

    def beginSearch(self):
        """Sets the selected text as the search text for the search bar.
        """
        theCursor = self.textCursor()
        if theCursor.hasSelection():
            self.docSearch.setSearchText(theCursor.selectedText())
        else:
            self.docSearch.setSearchText(None)
        self.updateDocMargins()
        return

    def beginReplace(self):
        """Opens the replace line of the search bar and sets the find
        text if a selection has been made, and resets the replace text.
        """
        theCursor = self.textCursor()
        if theCursor.hasSelection():
            self.docSearch.setSearchText(theCursor.selectedText())
        else:
            self.docSearch.setSearchText(None)
        self.docSearch.setReplaceText("")
        self.updateDocMargins()
        return

    def findNext(self, goBack=False):
        """Searches for the next or previous occurrence of the search
        bar text in the document. Wraps around if not found and loop is
        enabled, or continues to next file if next file is enabled.
        """
        if not self.anyFocus():
            logger.debug("Editor does not have focus")
            return False

        if not self.docSearch.isVisible():
            self.beginSearch()
            return

        findOpt = QTextDocument.FindFlag(0)
        if goBack:
            findOpt |= QTextDocument.FindBackward
        if self.docSearch.isCaseSense:
            findOpt |= QTextDocument.FindCaseSensitively
        if self.docSearch.isWholeWord:
            findOpt |= QTextDocument.FindWholeWords

        searchFor = self.docSearch.getSearchObject()
        wasFound = self.find(searchFor, findOpt)
        if not wasFound:
            if self.docSearch.doNextFile and not goBack:
                self.theParent.openNextDocument(
                    self._docHandle, wrapAround=self.docSearch.doLoop
                )
            elif self.docSearch.doLoop:
                theCursor = self.textCursor()
                theCursor.movePosition(
                    QTextCursor.End if goBack else QTextCursor.Start
                )
                self.setTextCursor(theCursor)
                wasFound = self.find(searchFor, findOpt)

        if wasFound:
            theCursor = self.textCursor()
            self._lastFind = (theCursor.selectionStart(), theCursor.selectionEnd())

        return

    def replaceNext(self):
        """Searches for the next occurrence of the search bar text in
        the document and replaces it with the replace text. Calls search
        next automatically when done.
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
            logger.verbose(
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
        """Clears n characters before and after the cursor.
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
        """Wraps the selected text in whatever is in tBefore and tAfter.
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
            self.theParent.makeAlert(self.tr(
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
        """Changes the block format of the block under the cursor.
        """
        theCursor = self.textCursor()
        theBlock = theCursor.block()
        if not theBlock.isValid():
            logger.debug("Invalid block selected for action '%s'", str(docAction))
            return False

        theText = theBlock.text()
        if len(theText.strip()) == 0:
            logger.debug("Empty block selected for action '%s'", str(docAction))
            return False

        # Remove existing format first, if any
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
        starting with '@'. We then find the word under the cursor and
        check that it is after the ':'. If all this is fine, we have a
        tag and can tell the document viewer to try and find and load
        the file where the tag is defined.
        """
        if theCursor is None:
            theCursor = self.textCursor()

        theBlock = theCursor.block()
        theText = theBlock.text()

        if len(theText) == 0:
            return False

        if theText.startswith("@"):

            theCursor.select(QTextCursor.WordUnderCursor)
            theWord = theCursor.selectedText()
            cPos = theText.find(":")
            wPos = theCursor.selectionStart() - theBlock.position()
            if wPos <= cPos:
                return False

            if loadTag:
                logger.verbose("Attempting to follow tag '%s'", theWord)
                self.theParent.docViewer.loadFromTag(theWord)
            else:
                logger.verbose("Potential tag '%s'", theWord)

            return True

        return False

    def _openSpellContext(self):
        """Opens the spell check context menu at the current point of
        the cursor.
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

        if self.mainConf.doReplaceDQuote and theTwo == ' "':
            nDelete = 1
            tInsert = self._typDQOpen

        elif self.mainConf.doReplaceDQuote and theOne == '"':
            nDelete = 1
            if thePos == 1:
                tInsert = self._typDQOpen
            else:
                tInsert = self._typDQClose

        elif self.mainConf.doReplaceSQuote and theTwo == " '":
            nDelete = 1
            tInsert = self._typSQOpen

        elif self.mainConf.doReplaceSQuote and theOne == "'":
            nDelete = 1
            if thePos == 1:
                tInsert = self._typSQOpen
            else:
                tInsert = self._typSQClose

        elif self.mainConf.doReplaceDash and theThree == "---":
            nDelete = 3
            tInsert = nwUnicode.U_EMDASH

        elif self.mainConf.doReplaceDash and theTwo == "--":
            nDelete = 2
            tInsert = nwUnicode.U_ENDASH

        elif self.mainConf.doReplaceDash and theTwo == nwUnicode.U_ENDASH + "-":
            nDelete = 2
            tInsert = nwUnicode.U_EMDASH

        elif self.mainConf.doReplaceDots and theThree == "...":
            nDelete = 3
            tInsert = nwUnicode.U_HELLIP

        tCheck = tInsert
        if tCheck in self.mainConf.fmtPadBefore:
            nDelete = max(nDelete, 1)
            tInsert = self._typPadChar + tInsert

        if tCheck in self.mainConf.fmtPadAfter:
            nDelete = max(nDelete, 1)
            tInsert = tInsert + self._typPadChar

        if nDelete > 0:
            theCursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor, nDelete)
            theCursor.insertText(tInsert)

        return

    def _updateHeaders(self, checkPos=False, checkLevel=False):
        """Update the headers record and return True if anything
        changed, if a check flag was provided.
        """
        if self._docHandle is None:
            return False

        newHeaders = self.theIndex.getHandleHeaders(self._docHandle)
        if checkPos:
            newPos = [x[0] for x in newHeaders]
            oldPos = [x[0] for x in self._docHeaders]
        if checkLevel:
            newLev = [x[1] for x in newHeaders]
            oldLev = [x[1] for x in self._docHeaders]

        self._docHeaders = newHeaders

        if checkPos:
            return newPos != oldPos
        if checkLevel:
            return newLev != oldLev

        return False

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
        """Returns a cursor which may or may not have a selection based
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

    def _setupSpellChecking(self):
        """Create the spell checking object based on the spellTool
        setting in config.
        """
        if self.mainConf.spellTool == nwConst.SP_ENCHANT:
            from nw.core.spellcheck import NWSpellEnchant
            self._theDict = NWSpellEnchant()
        else:
            self._theDict = NWSpellSimple()

        self.hLight.setDict(self._theDict)

        return

    def _allowAutoReplace(self, theState):
        """used to enable/disable the auto-replace feature temporarily.
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

    def __init__(self, docEditor):
        QRunnable.__init__(self)
        self.docEditor = docEditor
        self.signals = BackgroundWordCounterSignals()
        self._isRunning = False
        return

    def isRunning(self):
        return self._isRunning

    @pyqtSlot()
    def run(self):
        """Overloaded run function for the word counter, forwarding the
        call to the function that does the actual counting.
        """
        self._isRunning = True
        theText = self.docEditor.getText()
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
        QFrame.__init__(self, docEditor)

        logger.debug("Initialising GuiDocEditSearch ...")

        self.mainConf   = nw.CONFIG
        self.docEditor  = docEditor
        self.theParent  = docEditor.theParent
        self.theProject = docEditor.theProject
        self.theTheme   = docEditor.theTheme

        self.repVisible  = False
        self.isCaseSense = self.mainConf.searchCase
        self.isWholeWord = self.mainConf.searchWord
        self.isRegEx     = self.mainConf.searchRegEx
        self.doLoop      = self.mainConf.searchLoop
        self.doNextFile  = self.mainConf.searchNextFile
        self.doMatchCap  = self.mainConf.searchMatchCap

        mPx = self.mainConf.pxInt(6)
        tPx = int(0.8*self.theTheme.fontPixelSize)
        boxFont = self.theTheme.guiFont
        boxFont.setPointSizeF(0.9*self.theTheme.fontPointSize)

        self.setContentsMargins(0, 0, 0, 0)
        self.setAutoFillBackground(True)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)

        self.mainBox = QGridLayout(self)
        self.setLayout(self.mainBox)

        # Text Boxes
        # ==========
        self.searchBox = QLineEdit(self)
        self.searchBox.setFont(boxFont)
        self.searchBox.setPlaceholderText(self.tr("Search"))
        self.searchBox.returnPressed.connect(self._doSearch)

        self.replaceBox = QLineEdit(self)
        self.replaceBox.setFont(boxFont)
        self.replaceBox.setPlaceholderText(self.tr("Replace"))
        self.replaceBox.returnPressed.connect(self._doReplace)

        self.searchOpt = QToolBar(self)
        self.searchOpt.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.searchOpt.setIconSize(QSize(tPx, tPx))
        self.searchOpt.setContentsMargins(0, 0, 0, 0)
        self.searchOpt.setStyleSheet("QToolBar {padding: 0;}")

        self.searchLabel = QLabel(self.tr("Search"))
        self.searchLabel.setFont(boxFont)
        self.searchLabel.setIndent(self.mainConf.pxInt(6))

        self.toggleCase = QAction(self.tr("Case Sensitive"), self)
        self.toggleCase.setToolTip(self.tr("Match case"))
        self.toggleCase.setIcon(self.theTheme.getIcon("search_case"))
        self.toggleCase.setCheckable(True)
        self.toggleCase.setChecked(self.isCaseSense)
        self.toggleCase.toggled.connect(self._doToggleCase)
        self.searchOpt.addAction(self.toggleCase)

        self.toggleWord = QAction(self.tr("Whole Words Only"), self)
        self.toggleWord.setToolTip(self.tr("Match whole words"))
        self.toggleWord.setIcon(self.theTheme.getIcon("search_word"))
        self.toggleWord.setCheckable(True)
        self.toggleWord.setChecked(self.isWholeWord)
        self.toggleWord.toggled.connect(self._doToggleWord)
        self.searchOpt.addAction(self.toggleWord)

        self.toggleRegEx = QAction(self.tr("RegEx Mode"), self)
        self.toggleRegEx.setToolTip(self.tr("Search using regular expressions"))
        self.toggleRegEx.setIcon(self.theTheme.getIcon("search_regex"))
        self.toggleRegEx.setCheckable(True)
        self.toggleRegEx.setChecked(self.isRegEx)
        self.toggleRegEx.toggled.connect(self._doToggleRegEx)
        self.searchOpt.addAction(self.toggleRegEx)

        self.toggleLoop = QAction(self.tr("Loop Search"), self)
        self.toggleLoop.setToolTip(self.tr("Loop the search when reaching the end"))
        self.toggleLoop.setIcon(self.theTheme.getIcon("search_loop"))
        self.toggleLoop.setCheckable(True)
        self.toggleLoop.setChecked(self.doLoop)
        self.toggleLoop.toggled.connect(self._doToggleLoop)
        self.searchOpt.addAction(self.toggleLoop)

        self.toggleProject = QAction(self.tr("Search Next File"), self)
        self.toggleProject.setToolTip(self.tr("Continue searching in the next file"))
        self.toggleProject.setIcon(self.theTheme.getIcon("search_project"))
        self.toggleProject.setCheckable(True)
        self.toggleProject.setChecked(self.doNextFile)
        self.toggleProject.toggled.connect(self._doToggleProject)
        self.searchOpt.addAction(self.toggleProject)

        self.searchOpt.addSeparator()

        self.toggleMatchCap = QAction(self.tr("Preserve Case"), self)
        self.toggleMatchCap.setToolTip(self.tr("Preserve case on replace"))
        self.toggleMatchCap.setIcon(self.theTheme.getIcon("search_preserve"))
        self.toggleMatchCap.setCheckable(True)
        self.toggleMatchCap.setChecked(self.doMatchCap)
        self.toggleMatchCap.toggled.connect(self._doToggleMatchCap)
        self.searchOpt.addAction(self.toggleMatchCap)

        self.searchOpt.addSeparator()

        self.cancelSearch = QAction(self.tr("Close Search"), self)
        self.cancelSearch.setToolTip(self.tr("Close the search box [{0}]").format("Esc"))
        self.cancelSearch.setIcon(self.theTheme.getIcon("search_cancel"))
        self.cancelSearch.triggered.connect(self._doClose)
        self.searchOpt.addAction(self.cancelSearch)

        # Buttons
        # =======
        bPx = self.searchBox.sizeHint().height()

        self.showReplace = QToolButton(self)
        self.showReplace.setArrowType(Qt.RightArrow)
        self.showReplace.setCheckable(True)
        self.showReplace.setToolTip(self.tr("Show/hide the replace text box"))
        self.showReplace.setStyleSheet("QToolButton {border: none; background: transparent;}")
        self.showReplace.toggled.connect(self._doToggleReplace)

        self.searchButton = QPushButton(self.theTheme.getIcon("search"), "")
        self.searchButton.setFixedSize(QSize(bPx, bPx))
        self.searchButton.setToolTip(self.tr("Find in current document"))
        self.searchButton.clicked.connect(self._doSearch)

        self.replaceButton = QPushButton(self.theTheme.getIcon("search-replace"), "")
        self.replaceButton.setFixedSize(QSize(bPx, bPx))
        self.replaceButton.setToolTip(self.tr("Find and replace in current document"))
        self.replaceButton.clicked.connect(self._doReplace)

        self.mainBox.addWidget(self.searchLabel,   0, 0, 1, 2, Qt.AlignLeft)
        self.mainBox.addWidget(self.searchOpt,     0, 2, 1, 2, Qt.AlignRight)
        self.mainBox.addWidget(self.showReplace,   1, 0, 1, 1)
        self.mainBox.addWidget(self.searchBox,     1, 1, 1, 2)
        self.mainBox.addWidget(self.searchButton,  1, 3, 1, 1)
        self.mainBox.addWidget(self.replaceBox,    2, 1, 1, 2)
        self.mainBox.addWidget(self.replaceButton, 2, 3, 1, 1)

        self.mainBox.setColumnStretch(0, 1)
        self.mainBox.setColumnStretch(1, 0)
        self.mainBox.setColumnStretch(2, 0)
        self.mainBox.setColumnStretch(3, 0)
        self.mainBox.setColumnStretch(4, 0)
        self.mainBox.setSpacing(self.mainConf.pxInt(2))
        self.mainBox.setContentsMargins(mPx, mPx, mPx, mPx)

        boxWidth = self.mainConf.pxInt(200)
        self.searchBox.setFixedWidth(boxWidth)
        self.replaceBox.setFixedWidth(boxWidth)
        self.replaceBox.setVisible(False)
        self.replaceButton.setVisible(False)
        self.adjustSize()

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

        logger.debug("GuiDocEditSearch initialisation complete")

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
                self.replaceBox.setFocus(True)
                return True
            elif self.replaceBox.hasFocus():
                self.searchBox.setFocus(True)
                return True
        return False

    def anyFocus(self):
        """Returns true if any of the input boxes have focus.
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
        logger.verbose("Setting search text to '%s'", theText)
        return True

    def setReplaceText(self, theText):
        """Set the replace text.
        """
        self.showReplace.setChecked(True)
        self.replaceBox.setFocus()
        self.replaceBox.setText(theText)
        return True

    def getSearchObject(self):
        """Return the current search text either as text or as a regular
        expression object.
        """
        theText = self.searchBox.text()
        if self.isRegEx:
            # Using the Unicode-capable QRegularExpression class was
            # only added in Qt 5.13. Otherwise, 5.3 and up supports
            # only the QRegExp class.
            if self.mainConf.verQtValue >= 51300:
                rxOpt = QRegularExpression.UseUnicodePropertiesOption
                if not self.isCaseSense:
                    rxOpt |= QRegularExpression.CaseInsensitiveOption
                theRegEx = QRegularExpression(theText, rxOpt)
                self._alertSearchValid(theRegEx.isValid())
                return theRegEx

            else:  # >= 50300 to < 51300
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

    def _doClose(self):
        """Hide the search/replace bar.
        """
        self.closeSearch()
        return

    def _doSearch(self):
        """Call the search action function for the document editor.
        """
        modKey = qApp.keyboardModifiers()
        if modKey == Qt.ShiftModifier:
            self.docEditor.findNext(goBack=True)
        else:
            self.docEditor.findNext()
        return

    def _doReplace(self):
        """Call the replace action function for the document editor.
        """
        self.docEditor.replaceNext()
        return

    def _doToggleReplace(self, theState):
        """Toggle the show/hide of the
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

    def _doToggleCase(self, theState):
        """Enable/disable case sensitive mode.
        """
        self.isCaseSense = theState
        return

    def _doToggleWord(self, theState):
        """Enable/disable whole word search mode.
        """
        self.isWholeWord = theState
        return

    def _doToggleRegEx(self, theState):
        """Enable/disable regular expression search mode.
        """
        self.isRegEx = theState
        return

    def _doToggleLoop(self, theState):
        """Enable/disable looping the search.
        """
        self.doLoop = theState
        return

    def _doToggleProject(self, theState):
        """Enable/disable continuing search in next project file.
        """
        self.doNextFile = theState
        return

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
        QWidget.__init__(self, docEditor)

        logger.debug("Initialising GuiDocEditHeader ...")

        self.mainConf   = nw.CONFIG
        self.docEditor  = docEditor
        self.theParent  = docEditor.theParent
        self.theProject = docEditor.theProject
        self.theTheme   = docEditor.theTheme

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
        self.editButton = QToolButton(self)
        self.editButton.setIcon(self.theTheme.getIcon("edit"))
        self.editButton.setContentsMargins(0, 0, 0, 0)
        self.editButton.setIconSize(QSize(fPx, fPx))
        self.editButton.setFixedSize(fPx, fPx)
        self.editButton.setStyleSheet(buttonStyle)
        self.editButton.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.editButton.setVisible(False)
        self.editButton.setToolTip(self.tr("Edit document meta"))
        self.editButton.clicked.connect(self._editDocument)

        self.searchButton = QToolButton(self)
        self.searchButton.setIcon(self.theTheme.getIcon("search"))
        self.searchButton.setContentsMargins(0, 0, 0, 0)
        self.searchButton.setIconSize(QSize(fPx, fPx))
        self.searchButton.setFixedSize(fPx, fPx)
        self.searchButton.setStyleSheet(buttonStyle)
        self.searchButton.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.searchButton.setVisible(False)
        self.searchButton.setToolTip(self.tr("Search document"))
        self.searchButton.clicked.connect(self._searchDocument)

        self.minmaxButton = QToolButton(self)
        self.minmaxButton.setIcon(self.theTheme.getIcon("maximise"))
        self.minmaxButton.setContentsMargins(0, 0, 0, 0)
        self.minmaxButton.setIconSize(QSize(fPx, fPx))
        self.minmaxButton.setFixedSize(fPx, fPx)
        self.minmaxButton.setStyleSheet(buttonStyle)
        self.minmaxButton.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.minmaxButton.setVisible(False)
        self.minmaxButton.setToolTip(self.tr("Toggle Focus Mode"))
        self.minmaxButton.clicked.connect(self._minmaxDocument)

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

        # Fix the Colours
        self.matchColours()

        logger.debug("GuiDocEditHeader initialisation complete")

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
            self.editButton.setVisible(False)
            self.searchButton.setVisible(False)
            self.closeButton.setVisible(False)
            self.minmaxButton.setVisible(False)
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
        if self.theParent.isFocusMode:
            self.minmaxButton.setIcon(self.theTheme.getIcon("minimise"))
        else:
            self.minmaxButton.setIcon(self.theTheme.getIcon("maximise"))
        return

    ##
    #  Slots
    ##

    def _editDocument(self):
        """Open the edit item dialog from the main GUI.
        """
        self.theParent.editItem(self._docHandle)
        return

    def _searchDocument(self):
        """Toggle the visibility of the search box.
        """
        self.docEditor.toggleSearch()
        return

    def _closeDocument(self):
        """Trigger the close editor on the main window.
        """
        self.theParent.closeDocEditor()
        self.editButton.setVisible(False)
        self.searchButton.setVisible(False)
        self.closeButton.setVisible(False)
        self.minmaxButton.setVisible(False)
        return

    def _minmaxDocument(self):
        """Switch on or off Focus Mode.
        """
        self.theParent.toggleFocusMode()
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

# END Class GuiDocEditHeader


# =============================================================================================== #
#  The Embedded Document Footer
#  Only used by DocEditor, and is at a fixed position in the QTextEdit's viewport
# =============================================================================================== #

class GuiDocEditFooter(QWidget):

    def __init__(self, docEditor):
        QWidget.__init__(self, docEditor)

        logger.debug("Initialising GuiDocEditFooter ...")

        self.mainConf   = nw.CONFIG
        self.docEditor  = docEditor
        self.theParent  = docEditor.theParent
        self.theProject = docEditor.theProject
        self.theTheme   = docEditor.theTheme
        self.optState   = docEditor.theProject.optState

        self._theItem   = None
        self._docHandle = None

        self.sPx = int(round(0.9*self.theTheme.baseIconSize))
        fPx = int(0.9*self.theTheme.fontPixelSize)
        bSp = self.mainConf.pxInt(4)
        hSp = self.mainConf.pxInt(6)

        lblFont = self.font()
        lblFont.setPointSizeF(0.9*self.theTheme.fontPointSize)

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
        self.linesIcon.setPixmap(self.theTheme.getPixmap("status_lines", (self.sPx, self.sPx)))
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
        self.wordsIcon.setPixmap(self.theTheme.getPixmap("status_stats", (self.sPx, self.sPx)))
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
        self.matchColours()
        self.updateLineCount()
        self.updateCounts()

        logger.debug("GuiDocEditFooter initialisation complete")

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
        self.statusText.setPalette(thePalette)
        self.linesText.setPalette(thePalette)
        self.wordsText.setPalette(thePalette)

        return

    def setHandle(self, tHandle):
        """Set the handle that will populate the footer's data.
        """
        self._docHandle = tHandle
        if self._docHandle is None:
            logger.verbose("No handle set, so clearing the editor footer")
            self._theItem = None
        else:
            self._theItem = self.theProject.projTree[self._docHandle]

        self.updateInfo()
        self.updateCounts()

        return

    def updateInfo(self):
        """Update the content of text labels.
        """
        if self._theItem is None:
            sIcon = QPixmap()
            sText = ""
        else:
            iStatus = self._theItem.itemStatus
            if self._theItem.itemClass == nwItemClass.NOVEL:
                iStatus = self.theProject.statusItems.checkEntry(iStatus)
                theIcon = self.theParent.statusIcons[iStatus]
            else:
                iStatus = self.theProject.importItems.checkEntry(iStatus)
                theIcon = self.theParent.importIcons[iStatus]

            sIcon = theIcon.pixmap(self.sPx, self.sPx)
            sClass = trConst(nwLabels.CLASS_NAME[self._theItem.itemClass])
            sLayout = trConst(nwLabels.LAYOUT_NAME[self._theItem.itemLayout])
            sText = f"{self._theItem.itemStatus} / {sClass} / {sLayout}"

        self.statusIcon.setPixmap(sIcon)
        self.statusText.setText(sText)

        return

    def updateLineCount(self):
        """Update the word count.
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

    def updateCounts(self):
        """Update the word count.
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

# END Class GuiDocEditFooter
