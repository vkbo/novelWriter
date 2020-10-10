# -*- coding: utf-8 -*-
"""novelWriter GUI Document Editor

 novelWriter – GUI Document Editor
===================================
 Class holding the document editor

 File History:
 Created:   2018-09-29 [0.0.1]  GuiDocEditor
 Created:   2019-04-22 [0.0.1]  BackgroundWordCounter
 Created:   2019-09-29 [0.2.1]  GuiDocEditSearch
 Created:   2020-04-25 [0.4.5]  GuiDocEditHeader
 Rewritten: 2020-06-15 [0.9.0]  GuiDocEditSearch
 Created:   2020-06-27 [0.10.0] GuiDocEditFooter
 Rewritten: 2020-10-07 [1.0b3]  BackgroundWordCounter

 This file is a part of novelWriter
 Copyright 2018–2020, Veronica Berglyd Olsen

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
    QPointF, QObject, QRunnable
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

from nw.core import NWDoc, NWSpellCheck, NWSpellSimple, countWords
from nw.gui.dochighlight import GuiDocHighlighter
from nw.common import transferCase
from nw.constants import (
    nwConst, nwAlert, nwUnicode, nwDocAction, nwDocInsert, nwItemClass
)

logger = logging.getLogger(__name__)

class GuiDocEditor(QTextEdit):

    def __init__(self, theParent):
        QTextEdit.__init__(self, theParent)

        logger.debug("Initialising GuiDocEditor ...")

        # Class Variables
        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theTheme   = theParent.theTheme
        self.theProject = theParent.theProject
        self.nwDocument = NWDoc(self.theProject, self.theParent)

        self.docChanged = False # Flag for changed status of document
        self.spellCheck = False # Flag for spell checking enabled
        self.theHandle  = None  # The handle of the open file
        self.theDict    = None  # The current spell check dictionary
        self.nonWord    = "\"'" # Characters to not include in spell checking

        # Document Variables
        self.charCount  = 0     # Character count
        self.wordCount  = 0     # Word count
        self.paraCount  = 0     # Paragraph count
        self.lastEdit   = 0     # Time stamp of last edit
        self.lastFind   = None  # Position of the last found search word
        self.bigDoc     = False # Flag for very large document size
        self.doReplace  = False # Switch to temporarily disable auto-replace
        self.queuePos   = None  # Used for delayed change of cursor position

        # Typography
        self.typDQOpen  = self.mainConf.fmtDoubleQuotes[0]
        self.typDQClose = self.mainConf.fmtDoubleQuotes[1]
        self.typSQOpen  = self.mainConf.fmtSingleQuotes[0]
        self.typSQClose = self.mainConf.fmtSingleQuotes[1]

        # Core Elements and Signals
        self.qDocument = self.document()
        self.qDocument.contentsChange.connect(self._docChange)
        self.qDocument.documentLayout().documentSizeChanged.connect(self._docSizeChanged)

        # Document Title
        self.docHeader = GuiDocEditHeader(self)
        self.docFooter = GuiDocEditFooter(self)
        self.docSearch = GuiDocEditSearch(self)

        # Syntax
        self.hLight = GuiDocHighlighter(self.qDocument, self.theParent)

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
        self.wcInterval = self.mainConf.wordCountTimer
        self.wcTimer = QTimer()
        self.wcTimer.setInterval(int(self.wcInterval*1000))
        self.wcTimer.timeout.connect(self._runCounter)

        self.wCounter = BackgroundWordCounter(self)
        self.wCounter.setAutoDelete(False)
        self.wCounter.signals.countsReady.connect(self._updateCounts)

        self.initEditor()

        logger.debug("GuiDocEditor initialisation complete")

        return

    def clearEditor(self):
        """Clear the current document and reset all document related
        flags and counters.
        """
        self.nwDocument.clearDocument()
        self.setReadOnly(True)
        self.clear()
        self.wcTimer.stop()

        self.theHandle = None
        self.charCount = 0
        self.wordCount = 0
        self.paraCount = 0
        self.lastEdit  = 0
        self.lastFind  = None
        self.bigDoc    = False
        self.doReplace = False
        self.queuePos  = None

        self.setDocumentChanged(False)
        self.docHeader.setTitleFromHandle(self.theHandle)
        self.docFooter.setHandle(self.theHandle)

        return True

    def initEditor(self):
        """Initialise or re-initialise the editor with the user's
        settings. This function is both called when the editor is
        created, and when the user changes the main editor preferences.
        """
        # Some Constants
        self.nonWord  = "\"'"
        self.nonWord += "".join(self.mainConf.fmtDoubleQuotes)
        self.nonWord += "".join(self.mainConf.fmtSingleQuotes)

        # Reload spell check and dictionaries
        self._setupSpellChecking()
        self.setDictionaries()

        # Set font
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

        # Set default text margins
        cM = self.mainConf.getTextMargin()
        self.qDocument.setDocumentMargin(0)
        self.setViewportMargins(cM, cM, cM, cM)

        # Also set the document text options for the document text flow
        theOpt = QTextOption()

        if self.mainConf.doJustify:
            theOpt.setAlignment(Qt.AlignJustify)
        if self.mainConf.showTabsNSpaces:
            theOpt.setFlags(theOpt.flags() | QTextOption.ShowTabsAndSpaces)
        if self.mainConf.showLineEndings:
            theOpt.setFlags(theOpt.flags() | QTextOption.ShowLineAndParagraphSeparators)

        self.qDocument.setDefaultTextOption(theOpt)

        # Refresh the tab stops
        if self.mainConf.verQtValue >= 51000:
            self.setTabStopDistance(self.mainConf.getTabWidth())
        else:
            self.setTabStopWidth(self.mainConf.getTabWidth())

        # Initialise the syntax highlighter
        self.hLight.initHighlighter()

        # If we have a document open, we should reload it in case the
        # font changed, otherwise we just clear the editor entirely,
        # which makes it read only.
        if self.theHandle is not None:
            self.redrawText()
        else:
            self.clearEditor()

        return True

    def loadText(self, tHandle, tLine=None, showStatus=True):
        """Load text from a document into the editor. If we have an io
        error, we must handle this and clear the editor so that we don't
        risk overwriting the file if it exists. This can for instance
        happen of the file contains binary elements or an encoding that
        novelWriter does not support. If load is successful, or the
        document is new (empty string), we set up the editor for editing
        the file.
        """
        theDoc = self.nwDocument.openDocument(tHandle, showStatus=showStatus)
        if theDoc is None:
            # There was an io error
            self.clearEditor()
            return False

        docSize = len(theDoc)
        if docSize > nwConst.maxDocSize:
            self.theParent.makeAlert((
                "The document you are trying to open is too big. "
                "The document size is %.2f\u202fMB. "
                "The maximum size allowed is %.2f\u202fMB."
            ) % (docSize/1.0e6, nwConst.maxDocSize/1.0e6), nwAlert.ERROR)
            self.clearEditor()
            return False

        qApp.setOverrideCursor(QCursor(Qt.WaitCursor))
        self.hLight.setHandle(tHandle)

        # Check that the document is not too big for full, initial spell
        # checking. If it is too big, we switch to only check as we type
        self._checkDocSize(docSize)
        spTemp = self.hLight.spellCheck
        if self.bigDoc:
            self.hLight.spellCheck = False

        bfTime = time()
        self._allowAutoReplace(False)
        self.setPlainText(theDoc)
        qApp.processEvents()

        self._allowAutoReplace(True)
        afTime = time()
        logger.debug("Document highlighted in %.3f ms" % (1000*(afTime-bfTime)))

        self.lastEdit = time()
        self._runCounter()
        self.wcTimer.start()
        self.setDocumentChanged(False)
        self.theHandle = tHandle

        self.setReadOnly(False)
        self.docHeader.setTitleFromHandle(self.theHandle)
        self.docFooter.setHandle(self.theHandle)
        self.updateDocMargins()
        self.hLight.spellCheck = spTemp

        theItem = self.nwDocument.getCurrentItem()
        if tLine is None and theItem is not None:
            # For large documents we queue the repositioning until the
            # document layout has grown past the point we want to move
            # the cursor to. This makes the loading significantly
            # faster.
            if docSize > 50000:
                self.queuePos = theItem.cursorPos
            else:
                self.setCursorPosition(theItem.cursorPos)
        else:
            self.setCursorLine(tLine)

        self.docFooter.updateLineCount()

        qApp.restoreOverrideCursor()

        return True

    def updateTagHighLighting(self, forceBigDoc=False):
        """Rerun the syntax highlighter on all meta data lines.
        """
        self.hLight.rehighlightByType(GuiDocHighlighter.BLOCK_META)
        return

    def redrawText(self):
        """Redraw the text by marking the document content as "dirty".
        """
        self.qDocument.markContentsDirty(0, self.qDocument.characterCount())
        return

    def replaceText(self, theText):
        """Replaces the text of the current document with the provided
        text. This also clears undo history.
        """
        docSize = len(theText)
        if docSize > nwConst.maxDocSize:
            self.theParent.makeAlert((
                "The text you are trying to add is too big. "
                "The text size is %.2f\u202fMB. "
                "The maximum size allowed is %.2f\u202fMB."
            ) % (docSize/1.0e6, nwConst.maxDocSize/1.0e6), nwAlert.ERROR)
            return False

        qApp.setOverrideCursor(QCursor(Qt.WaitCursor))
        self.setPlainText(theText)
        self.setDocumentChanged(True)
        self.updateDocMargins()
        qApp.restoreOverrideCursor()

        return True

    def saveText(self):
        """Save the text currently in the editor to the NWDoc object,
        and update the NWItem meta data.
        """
        theItem = self.nwDocument.getCurrentItem()
        if theItem is None:
            return False

        docText = self.getText()
        theItem.setCharCount(self.charCount)
        theItem.setWordCount(self.wordCount)
        theItem.setParaCount(self.paraCount)
        self.saveCursorPosition()
        self.nwDocument.saveDocument(docText)
        self.setDocumentChanged(False)

        self.theParent.theIndex.scanText(theItem.itemHandle, docText)

        return True

    def updateDocMargins(self):
        """Automatically adjust the margins so the text is centred if
        Config.textFixedW is enabled or we're in Focus Mode. Otherwise,
        just ensure the margins are set correctly.
        """
        wW = self.width()
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
        fY = self.height() - fH - tB - sH
        self.docHeader.setGeometry(tB, tB, tW, tH)
        self.docFooter.setGeometry(tB, fY, tW, fH)

        if self.docSearch.isVisible():
            rH = self.docSearch.height()
            rW = self.docSearch.width()
            rL = wW - sW - rW - 2*tB
            self.docSearch.move(rL, 2*tB)
        else:
            rH = 0

        self.setViewportMargins(tM, max(cM, tH, rH), tM, max(cM, fH))

        return

    def updateDocInfo(self, tHandle):
        """Called when an item label is changed to check if the document
        title bar needs updating,
        """
        if tHandle == self.theHandle:
            self.docHeader.setTitleFromHandle(self.theHandle)
            self.docFooter.updateInfo()
            self.updateDocMargins()
        return

    ##
    #  Setters and Getters
    ##

    def setDocumentChanged(self, bValue):
        """Keeps track of the document changed variable, and ensures
        that the corresponding icon on the status bar shows the same
        status.
        """
        self.docChanged = bValue
        self.theParent.statusBar.setDocumentStatus(self.docChanged)
        return self.docChanged

    def getText(self):
        """Get the text content of the current document. This method
        uses QTextEdit->toPlainText for Qt versions lower than 5.9, and
        the QDocument->toRawText for higher version. The latter
        preserves non-breaking spaces, which the former does not.
        We still want to get rid of page and line separators though.
        See: https://doc.qt.io/qt-5/qtextdocument.html#toPlainText
        """
        if self.mainConf.verQtValue >= 50900:
            theText = self.qDocument.toRawText()
            theText = theText.replace(nwUnicode.U_LSEP, "\n") # Line separators
            theText = theText.replace(nwUnicode.U_PSEP, "\n") # Paragraph separators
        else:
            theText = self.toPlainText()
        return theText

    def setCursorPosition(self, thePosition):
        """Move the cursor to a given position in the document.
        """
        if not isinstance(thePosition, int):
            return False
        if thePosition >= 0:
            theCursor = self.textCursor()
            theCursor.setPosition(thePosition)
            self.setTextCursor(theCursor)
            self.docFooter.updateLineCount()
        return True

    def getCursorPosition(self):
        """Find the cursor position in the document. If the editor has a
        selection, return the position of the end of the selection.
        """
        return self.textCursor().selectionEnd()

    def saveCursorPosition(self):
        """Save the cursor position to the current project item object.
        """
        theItem = self.nwDocument.getCurrentItem()
        if theItem is not None:
            cursPos = self.getCursorPosition()
            theItem.setCursorPos(cursPos)
        return

    def setCursorLine(self, theLine):
        """Move the cursor to a given line in the document.
        """
        if not isinstance(theLine, int):
            return False
        if theLine >= 0:
            theBlock = self.qDocument.findBlockByLineNumber(theLine)
            if theBlock:
                self.setCursorPosition(theBlock.position())
                self.docFooter.updateLineCount()
                logger.verbose("Cursor moved to line %d" % theLine)
        return True

    ##
    #  Spell Checking
    ##

    def setDictionaries(self):
        """Set the spell checker dictionary language, and update the
        status bar to show the one actually loaded by the spell checker
        class.
        """
        if self.theProject.projLang is None:
            theLang = self.mainConf.spellLanguage
        else:
            theLang = self.theProject.projLang

        self.theDict.setLanguage(theLang, self.theProject.projDict)

        aLang, aName = self.theDict.describeDict()
        self.theParent.statusBar.setLanguage(
            aLang, "%s [%s]" % (self.mainConf.spellTool.title(), aName.title())
        )

        if not self.bigDoc:
            self.spellCheckDocument()

        return True

    def setSpellCheck(self, theMode):
        """This is the master spell check setting function, and this one
        should call all other setSpellCheck functions in other classes.
        If the spell check mode (theMode) is not defined (None), then
        toggle the current status saved in this class.
        """
        if theMode is None:
            theMode = not self.spellCheck

        if self.theDict.spellLanguage is None:
            theMode = False

        self.spellCheck = theMode
        self.theParent.mainMenu.setSpellCheck(theMode)
        self.theProject.setSpellCheck(theMode)
        self.hLight.setSpellCheck(theMode)
        if not self.bigDoc:
            self.spellCheckDocument()

        logger.verbose("Spell check is set to %s" % str(theMode))

        return True

    def spellCheckDocument(self):
        """Rerun the highlighter to update spell checking status of the
        currently loaded text. The fastest way to do this, at least as
        of Qt 5.13, is to clear the text and put it back.
        """
        logger.verbose("Running spell checker")
        if self.spellCheck:
            bfTime = time()
            qApp.setOverrideCursor(QCursor(Qt.WaitCursor))
            if self.bigDoc:
                theText = self.getText()
                self.setPlainText(theText)
            else:
                self.hLight.rehighlight()
            qApp.restoreOverrideCursor()
            afTime = time()
            logger.debug(
                "Document highlighted in %.3f ms" % (1000*(afTime-bfTime))
            )
            self.theParent.statusBar.showMessage("Spell check complete")

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
        logger.verbose("Requesting action: %s" % theAction.name)
        if not self.theParent.hasProject:
            logger.error("No project open")
            return False
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
            self._wrapSelection(self.typSQOpen, self.typSQClose)
        elif theAction == nwDocAction.D_QUOTE:
            self._wrapSelection(self.typDQOpen, self.typDQClose)
        elif theAction == nwDocAction.SEL_ALL:
            self._makeSelection(QTextCursor.Document)
        elif theAction == nwDocAction.SEL_PARA:
            self._makeSelection(QTextCursor.BlockUnderCursor)
        elif theAction == nwDocAction.FIND:
            self._beginSearch()
        elif theAction == nwDocAction.REPLACE:
            self._beginReplace()
        elif theAction == nwDocAction.GO_NEXT:
            self._findNext()
        elif theAction == nwDocAction.GO_PREV:
            self._findNext(isBackward=True)
        elif theAction == nwDocAction.REPL_NEXT:
            self._replaceNext()
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
            self._replaceQuotes("'", self.typSQOpen, self.typSQClose)
        elif theAction == nwDocAction.REPL_DBL:
            self._replaceQuotes("\"", self.typDQOpen, self.typDQClose)
        else:
            logger.debug("Unknown or unsupported document action %s" % str(theAction))
            self._allowAutoReplace(True)
            return False
        self._allowAutoReplace(True)
        return True

    def isEmpty(self):
        """Wrapper function to check if the current document is empty.
        """
        return self.qDocument.isEmpty()

    def revealLocation(self):
        """Tell the user where on the file system the file in the editor
        is saved.
        """
        if self.theHandle is not None:
            msgBox = QMessageBox()
            msgBox.information(self, "File Location", (
                "File details for the currently open file<br>"
                "Handle: {handle:s}<br>"
                "Location: {fileLoc:s}"
            ).format(
                handle  = self.theHandle,
                fileLoc = str(self.nwDocument.getFileLocation())
            ))
        return

    def insertText(self, theInsert):
        """Insert a specific type of text at the cursor position.
        """
        if isinstance(theInsert, str):
            theText = theInsert
        elif isinstance(theInsert, nwDocInsert):
            if theInsert == nwDocInsert.HARD_BREAK:
                theText = "  \n"
            elif theInsert == nwDocInsert.NB_SPACE:
                theText = nwUnicode.U_NBSP
            elif theInsert == nwDocInsert.THIN_SPACE:
                theText = nwUnicode.U_THNSP
            elif theInsert == nwDocInsert.THIN_NB_SPACE:
                theText = nwUnicode.U_THNBSP
            elif theInsert == nwDocInsert.SHORT_DASH:
                theText = nwUnicode.U_ENDASH
            elif theInsert == nwDocInsert.LONG_DASH:
                theText = nwUnicode.U_EMDASH
            elif theInsert == nwDocInsert.ELLIPSIS:
                theText = nwUnicode.U_HELLIP
            elif theInsert == nwDocInsert.MODAPOS_S:
                theText = nwUnicode.U_MAPOSS
            elif theInsert == nwDocInsert.QUOTE_LS:
                theText = self.typSQOpen
            elif theInsert == nwDocInsert.QUOTE_RS:
                theText = self.typSQClose
            elif theInsert == nwDocInsert.QUOTE_LD:
                theText = self.typDQOpen
            elif theInsert == nwDocInsert.QUOTE_RD:
                theText = self.typDQClose
            else:
                return False
        else:
            return False

        theCursor = self.textCursor()
        theCursor.beginEditBlock()
        theCursor.insertText(theText)
        theCursor.endEditBlock()

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
            self._beginSearch()
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
          * The undo/redo sequences bypasses the doAction pathway from
            the menu, so we redirect them back from here.
        """
        isReturn  = keyEvent.key() == Qt.Key_Return
        isReturn |= keyEvent.key() == Qt.Key_Enter
        if isReturn and self.docSearch.anyFocus():
            return
        elif keyEvent == QKeySequence.Redo:
            self.docAction(nwDocAction.REDO)
        elif keyEvent == QKeySequence.Undo:
            self.docAction(nwDocAction.UNDO)
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

    def mouseReleaseEvent(self, mEvent):
        """If the mouse button is released and the control key is
        pressed, check if we're clicking on a tag, and trigger the
        follow tag function.
        """
        if qApp.keyboardModifiers() == Qt.ControlModifier:
            theCursor = self.cursorForPosition(mEvent.pos())
            self._followTag(theCursor)

        QTextEdit.mouseReleaseEvent(self, mEvent)
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
    #  Signals and Slots
    ##

    @pyqtSlot(int, int, int)
    def _docChange(self, thePos, charsRemoved, charsAdded):
        """Triggered by QTextDocument->contentsChanged. This also
        triggers the syntax highlighter.
        """
        self.lastEdit = time()
        self.lastFind = None
        if self.qDocument.characterCount() > nwConst.maxDocSize:
            self.theParent.makeAlert((
                "The document has grown too big and you cannot add more text to it. "
                "The maximum size of a single novelWriter document is %.2f\u202fMB."
            ) % (nwConst.maxDocSize/1.0e6), nwAlert.ERROR)
            self.undo()
            return
        if not self.docChanged:
            self.setDocumentChanged(True)
        if not self.wcTimer.isActive():
            self.wcTimer.start()
        if self.doReplace and charsAdded == 1:
            self._docAutoReplace(self.qDocument.findBlock(thePos))
        return

    @pyqtSlot("QPoint")
    def _openContextMenu(self, thePos):
        """Triggered by right click to open the context menu. Also
        triggered by the Ctrl+. shortcut.
        """
        userCursor = self.textCursor()
        userSelection = userCursor.hasSelection()

        mnuContext = QMenu()

        # Cut, Copy and Paste
        # ===================

        if userSelection:
            mnuCut = QAction("Cut", mnuContext)
            mnuCut.triggered.connect(lambda: self.docAction(nwDocAction.CUT))
            mnuContext.addAction(mnuCut)

            mnuCopy = QAction("Copy", mnuContext)
            mnuCopy.triggered.connect(lambda: self.docAction(nwDocAction.COPY))
            mnuContext.addAction(mnuCopy)

        mnuPaste = QAction("Paste", mnuContext)
        mnuPaste.triggered.connect(lambda: self.docAction(nwDocAction.PASTE))
        mnuContext.addAction(mnuPaste)

        mnuContext.addSeparator()

        # Selections
        # ==========

        mnuSelAll = QAction("Select All", mnuContext)
        mnuSelAll.triggered.connect(lambda: self.docAction(nwDocAction.SEL_ALL))
        mnuContext.addAction(mnuSelAll)

        mnuSelWord = QAction("Select Word", mnuContext)
        mnuSelWord.triggered.connect(
            lambda: self._makePosSelection(QTextCursor.WordUnderCursor, thePos)
        )
        mnuContext.addAction(mnuSelWord)

        mnuSelPara = QAction("Select Paragraph", mnuContext)
        mnuSelPara.triggered.connect(
            lambda: self._makePosSelection(QTextCursor.BlockUnderCursor, thePos)
        )
        mnuContext.addAction(mnuSelPara)

        # Spell Checking
        # ==============

        spellCheck = self.spellCheck

        if spellCheck:
            posCursor = self.cursorForPosition(thePos)
            posCursor.select(QTextCursor.WordUnderCursor)
            theWord = posCursor.selectedText().strip().strip(self.nonWord)
            spellCheck &= theWord != ""

        if spellCheck:
            logger.verbose("Looking up '%s' in the dictionary" % theWord)
            spellCheck &= not self.theDict.checkWord(theWord)

        if spellCheck:
            mnuContext.addSeparator()
            mnuHead = QAction("Spelling Suggestion(s)", mnuContext)
            mnuContext.addAction(mnuHead)

            theSuggest = self.theDict.suggestWords(theWord)[:15]
            if len(theSuggest) > 0:
                for aWord in theSuggest:
                    mnuWord = QAction("%s %s" % (nwUnicode.U_ENDASH, aWord), mnuContext)
                    mnuWord.triggered.connect(
                        lambda thePos, aWord=aWord : self._correctWord(posCursor, aWord)
                    )
                    mnuContext.addAction(mnuWord)
                mnuContext.addSeparator()
                mnuAdd = QAction("Add Word to Dictionary", mnuContext)
                mnuAdd.triggered.connect(lambda thePos : self._addWord(posCursor))
                mnuContext.addAction(mnuAdd)

            else:
                mnuHead = QAction("No Suggestions", mnuContext)
                mnuContext.addAction(mnuHead)

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
        theWord = theCursor.selectedText().strip().strip(self.nonWord)
        logger.debug("Added '%s' to project dictionary" % theWord)
        self.theDict.addWord(theWord)
        self.hLight.setDict(self.theDict)
        self.hLight.rehighlightBlock(theCursor.block())
        return

    @pyqtSlot()
    def _runCounter(self):
        """Decide whether to run the word counter, or stop the timer due
        to inactivity.
        """
        if self.wCounter.isRunning():
            logger.verbose("Word counter is busy")
            return

        if time() - self.lastEdit < 5*self.wcInterval:
            logger.verbose("Running word counter")
            self.theParent.threadPool.start(self.wCounter)

        return

    @pyqtSlot(int, int, int)
    def _updateCounts(self, cCount, wCount, pCount):
        """Slot for the word counter's finished signal
        """
        theItem = self.nwDocument.getCurrentItem()
        if self.theHandle is None or theItem is None:
            return

        logger.verbose("Updating word count")

        self.charCount = cCount
        self.wordCount = wCount
        self.paraCount = pCount
        theItem.setCharCount(cCount)
        theItem.setWordCount(wCount)
        theItem.setParaCount(pCount)

        self.theParent.treeView.propagateCount(self.theHandle, wCount)
        self.theParent.treeView.projectWordCount()
        self.theParent.treeMeta.updateCounts(self.theHandle, cCount, wCount, pCount)
        self._checkDocSize(self.qDocument.characterCount())
        self.docFooter.updateCounts()

        return

    @pyqtSlot("QSizeF")
    def _docSizeChanged(self, theSize):
        """Called whenever the underlying document layout size changes.
        This is used to queue the repositioning of the cursor for very
        large documents to ensure the region where the cursor is being
        moved to has been drawn before the move is made.
        """
        if self.queuePos is not None:
            thePos = self.qDocument.documentLayout().hitTest(
                QPointF(theSize.width(), theSize.height()), Qt.FuzzyHit
            )
            if self.queuePos <= thePos:
                logger.verbose(
                    "Allowed cursor move to %d <= %d" % (self.queuePos, thePos)
                )
                self.setCursorPosition(self.queuePos)
                self.queuePos = None
            else:
                logger.verbose(
                    "Denied cursor move to %d > %d" % (self.queuePos, thePos)
                )
        return

    ##
    #  Internal Functions
    ##

    def _followTag(self, theCursor=None):
        """Activated by Ctrl+Enter. Checks that we're in a block
        starting with '@'. We then find the word under the cursor and
        check that it is after the ':'. If all this is fine, we have a
        tag and can tell the document viewer to try and find and load
        the file where the tag is defined.
        """
        if theCursor is None:
            theCursor = self.textCursor()

        theBlock = theCursor.block()
        theText  = theBlock.text()

        if len(theText) == 0:
            return False

        if theText.startswith("@"):

            theCursor.select(QTextCursor.WordUnderCursor)
            theWord = theCursor.selectedText()
            cPos = theText.find(":")
            wPos = theCursor.selectionStart() - theBlock.position()
            if wPos <= cPos:
                return False

            logger.verbose("Attempting to follow tag '%s'" % theWord)
            self.theParent.docViewer.loadFromTag(theWord)

        return True

    def _openSpellContext(self):
        """Opens the spell check context menu at the current point of
        the cursor.
        """
        self._openContextMenu(self.cursorRect().center())
        return

    def _docAutoReplace(self, theBlock):
        """Autoreplace text elements based on main configuration.
        """
        if not theBlock.isValid():
            return

        theText   = theBlock.text()
        theCursor = self.textCursor()
        thePos    = theCursor.positionInBlock()
        theLen    = len(theText)

        if theLen < 1 or thePos-1 > theLen:
            return

        theOne   = theText[thePos-1:thePos]
        theTwo   = theText[thePos-2:thePos]
        theThree = theText[thePos-3:thePos]

        if self.mainConf.doReplaceDQuote and theTwo == " \"":
            theCursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor, 1)
            theCursor.insertText(self.typDQOpen)

        elif self.mainConf.doReplaceDQuote and theOne == "\"":
            theCursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor, 1)
            if thePos == 1:
                theCursor.insertText(self.typDQOpen)
            else:
                theCursor.insertText(self.typDQClose)

        elif self.mainConf.doReplaceSQuote and theTwo == " '":
            theCursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor, 1)
            theCursor.insertText(self.typSQOpen)

        elif self.mainConf.doReplaceSQuote and theOne == "'":
            theCursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor, 1)
            if thePos == 1:
                theCursor.insertText(self.typSQOpen)
            else:
                theCursor.insertText(self.typSQClose)

        elif self.mainConf.doReplaceDash and theThree == "---":
            theCursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor, 3)
            theCursor.insertText(nwUnicode.U_EMDASH)

        elif self.mainConf.doReplaceDash and theTwo == "--":
            theCursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor, 2)
            theCursor.insertText(nwUnicode.U_ENDASH)

        elif self.mainConf.doReplaceDash and theTwo == nwUnicode.U_ENDASH+"-":
            theCursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor, 2)
            theCursor.insertText(nwUnicode.U_EMDASH)

        elif self.mainConf.doReplaceDots and theThree == "...":
            theCursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor, 3)
            theCursor.insertText(nwUnicode.U_HELLIP)

        return

    def _replaceQuotes(self, sQuote, oQuote, cQuote):
        """Replace all straight quotes in the selected text.
        """
        theCursor = self.textCursor()
        if theCursor.hasSelection():
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
                else:
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

        else:
            self.theParent.makeAlert(
                "Please selection some text before calling replace quotes.", nwAlert.ERROR
            )

        return

    def _checkDocSize(self, theSize):
        """Check if document size crosses the big document limit set in
        config. If so, we will set the big document flag to True.
        """
        newState = theSize > self.mainConf.bigDocLimit*1000

        if newState != self.bigDoc:
            if newState:
                logger.info(
                    "The document size is {:n} > {:n}, big doc mode has been enabled".format(
                        theSize, self.mainConf.bigDocLimit*1000
                    )
                )
            else:
                logger.info(
                    "The document size is {:n} <= {:n}, big doc mode has been disabled".format(
                        theSize, self.mainConf.bigDocLimit*1000
                    )
                )

        self.bigDoc = newState

        return

    def _wrapSelection(self, tBefore, tAfter=None):
        """Wraps the selected text in whatever is in tBefore and tAfter.
        If there is no selection, the autoSelect setting decides the
        action. AutoSelect will select the word under the cursor before
        wrapping it. If this feature is disabled, nothing is done.
        """
        if tAfter is None:
            tAfter = tBefore

        theCursor = self._autoSelect()
        if theCursor.hasSelection():
            posS = theCursor.selectionStart()
            posE = theCursor.selectionEnd()

            theCursor.clearSelection()
            theCursor.beginEditBlock()
            theCursor.setPosition(posE)
            theCursor.insertText(tAfter)
            theCursor.setPosition(posS)
            theCursor.insertText(tBefore)
            theCursor.endEditBlock()

            theCursor.setPosition(posE + len(tBefore))
            theCursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor, posE-posS)
            self.setTextCursor(theCursor)

        else:
            logger.warning("No selection made, nothing to do")
        return

    def _clearSurrounding(self, theCursor, nChars):
        """Clears n characters before and after the cursor.
        """
        if theCursor.hasSelection():
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
        else:
            logger.warning("No selection made, nothing to do")
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
            if self.qDocument.characterAt(posS) == "_":
                posS += 1
                reSelect = True
            if self.qDocument.characterAt(posE) == "_":
                posE -= 1
                reSelect = True
            if reSelect:
                theCursor.clearSelection()
                theCursor.setPosition(posE-1)
                theCursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor, posE-posS-1)

            self.setTextCursor(theCursor)
        return theCursor

    def _toggleFormat(self, fLen, fChar):
        """Toggle strikethrough text.
        """
        theCursor = self._autoSelect()
        if theCursor.hasSelection():
            posS = theCursor.selectionStart()
            posE = theCursor.selectionEnd()

            numB = 0
            for n in range(fLen):
                if self.qDocument.characterAt(posS-n-1) == fChar:
                    numB += 1
                else:
                    break

            numA = 0
            for n in range(fLen):
                if self.qDocument.characterAt(posE+n) == fChar:
                    numA += 1
                else:
                    break

            cLevel = min(numB, numA)
            if cLevel == fLen:
                self._clearSurrounding(theCursor, fLen)
            else:
                self._wrapSelection(fChar*fLen)

        return

    def _formatBlock(self, docAction):
        """Changes the block format of the block under the cursor.
        """
        theCursor = self.textCursor()
        theBlock = theCursor.block()
        if not theBlock.isValid():
            logger.debug("Invalid block selected for action %s" % str(docAction))
            return False

        theText = theBlock.text()
        if len(theText.strip()) == 0:
            logger.debug("Empty block selected for action %s" % str(docAction))
            return False

        # Remove existing format first, if any
        if theText.startswith("@"):
            logger.error("Cannot apply block format to keyword/value line")
            return False
        elif theText.startswith("% "):
            newText = theText[2:]
            cOffset = 2
        elif theText.startswith("%"):
            newText = theText[1:]
            cOffset = 1
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
        else:
            newText = theText
            cOffset = 0

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
        elif docAction == nwDocAction.BLOCK_TXT:
            theText = newText
            cOffset -= 0
        else:
            logger.error(
                "Unknown or unsupported block format requested: %s" % str(docAction)
            )
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

    def _beginSearch(self):
        """Sets the selected text as the search text for the search bar.
        """
        theCursor = self.textCursor()
        if theCursor.hasSelection():
            self.docSearch.setSearchText(theCursor.selectedText())
        else:
            self.docSearch.setSearchText(None)
        self.updateDocMargins()
        return

    def _beginReplace(self):
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

    def _findNext(self, isBackward=False):
        """Searches for the next or previous occurrence of the search
        bar text in the document. Wraps around if not found and loop is
        enabled, or continues to next file if next file is enabled.
        """
        if not self.docSearch.isVisible():
            self._beginSearch()
            return

        findOpt = QTextDocument.FindFlag(0)
        if isBackward:
            findOpt |= QTextDocument.FindBackward
        if self.docSearch.isCaseSense:
            findOpt |= QTextDocument.FindCaseSensitively
        if self.docSearch.isWholeWord:
            findOpt |= QTextDocument.FindWholeWords

        searchFor = self.docSearch.getSearchObject()
        wasFound  = self.find(searchFor, findOpt)
        if not wasFound:
            if self.docSearch.doNextFile and not isBackward:
                self.theParent.openNextDocument(
                    self.theHandle, wrapAround=self.docSearch.doLoop
                )
            elif self.docSearch.doLoop:
                theCursor = self.textCursor()
                theCursor.movePosition(
                    QTextCursor.End if isBackward else QTextCursor.Start
                )
                self.setTextCursor(theCursor)
                wasFound = self.find(searchFor, findOpt)

        if wasFound:
            theCursor = self.textCursor()
            self.lastFind = (theCursor.selectionStart(), theCursor.selectionEnd())

        return

    def _replaceNext(self):
        """Searches for the next occurrence of the search bar text in
        the document and replaces it with the replace text. Calls search
        next automatically when done.
        """
        if not self.docSearch.isVisible():
            # The search tool is not active, so we activate it.
            self._beginSearch()
            return

        theCursor = self.textCursor()
        if not theCursor.hasSelection():
            # We have no text selected at all, so just make this a
            # regular find next call.
            self._findNext()
            return

        if self.lastFind is None and theCursor.hasSelection():
            # If we have a selection but no search, it may have been the
            # text we triggered the search with, in which case we search
            # again from the beginning of that selection to make sure we
            # have a valid result.
            sPos = theCursor.selectionStart()
            theCursor.clearSelection()
            theCursor.setPosition(sPos)
            self.setTextCursor(theCursor)
            self._findNext()
            theCursor = self.textCursor()

        if self.lastFind is None:
            # In case the above didn't find a result, we give up here.
            return

        searchFor = self.docSearch.getSearchText()
        replWith  = self.docSearch.getReplaceText()

        if self.docSearch.doMatchCap:
            replWith = transferCase(theCursor.selectedText(), replWith)

        # Make sure the selected text was selected by an actual find
        # call, and not the user.
        try:
            isFind  = self.lastFind[0] == theCursor.selectionStart()
            isFind &= self.lastFind[1] == theCursor.selectionEnd()
        except Exception:
            isFind = False

        if isFind:
            theCursor.beginEditBlock()
            theCursor.removeSelectedText()
            theCursor.insertText(replWith)
            theCursor.endEditBlock()
            theCursor.setPosition(theCursor.selectionEnd())
            self.setTextCursor(theCursor)
            logger.verbose("Replaced occurrence of '%s' with '%s' on line %d" % (
                searchFor, replWith, theCursor.blockNumber()
            ))
        else:
            logger.error("The selected text is not a search result, skipping replace")

        self._findNext()

        return

    def _setupSpellChecking(self):
        """Create the spell checking object based on the spellTool
        setting in config.
        """
        if self.mainConf.spellTool == NWSpellCheck.SP_ENCHANT:
            from nw.core.spellcheck import NWSpellEnchant
            self.theDict = NWSpellEnchant()
        else:
            self.theDict = NWSpellSimple()

        self.hLight.setDict(self.theDict)

        return

    def _allowAutoReplace(self, theState):
        """used to enable/disable the auto-replace feature temporarily.
        """
        if theState:
            self.doReplace = self.mainConf.doReplace
        else:
            self.doReplace = False
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

## END Class BackgroundWordCounter

class BackgroundWordCounterSignals(QObject):

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
        self.searchBox.setPlaceholderText("Search")
        self.searchBox.returnPressed.connect(self._doSearch)

        self.replaceBox = QLineEdit(self)
        self.replaceBox.setFont(boxFont)
        self.replaceBox.setPlaceholderText("Replace")
        self.replaceBox.returnPressed.connect(self._doReplace)

        self.searchOpt = QToolBar(self)
        self.searchOpt.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.searchOpt.setIconSize(QSize(tPx, tPx))
        self.searchOpt.setContentsMargins(0, 0, 0, 0)
        self.searchOpt.setStyleSheet(r"QToolBar {padding: 0;}")

        self.searchLabel = QLabel("Search")
        self.searchLabel.setFont(boxFont)
        self.searchLabel.setIndent(self.mainConf.pxInt(6))

        self.toggleCase = QAction("Case Sensitive", self)
        self.toggleCase.setToolTip("Match case")
        self.toggleCase.setIcon(self.theTheme.getIcon("search_case"))
        self.toggleCase.setCheckable(True)
        self.toggleCase.setChecked(self.isCaseSense)
        self.toggleCase.toggled.connect(self._doToggleCase)
        self.searchOpt.addAction(self.toggleCase)

        self.toggleWord = QAction("Whole Words Only", self)
        self.toggleWord.setToolTip("Match whole words")
        self.toggleWord.setIcon(self.theTheme.getIcon("search_word"))
        self.toggleWord.setCheckable(True)
        self.toggleWord.setChecked(self.isWholeWord)
        self.toggleWord.toggled.connect(self._doToggleWord)
        self.searchOpt.addAction(self.toggleWord)

        self.toggleRegEx = QAction("RegEx Mode", self)
        self.toggleRegEx.setToolTip("Use regular expressions (requires Qt 5.3)")
        self.toggleRegEx.setIcon(self.theTheme.getIcon("search_regex"))
        self.toggleRegEx.setCheckable(True)
        self.toggleRegEx.setChecked(self.isRegEx)
        self.toggleRegEx.toggled.connect(self._doToggleRegEx)
        self.searchOpt.addAction(self.toggleRegEx)

        self.toggleLoop = QAction("Loop Search", self)
        self.toggleLoop.setToolTip("Loop the search when reaching the end")
        self.toggleLoop.setIcon(self.theTheme.getIcon("search_loop"))
        self.toggleLoop.setCheckable(True)
        self.toggleLoop.setChecked(self.doLoop)
        self.toggleLoop.toggled.connect(self._doToggleLoop)
        self.searchOpt.addAction(self.toggleLoop)

        self.toggleProject = QAction("Search Next File", self)
        self.toggleProject.setToolTip("Continue searching in the next file")
        self.toggleProject.setIcon(self.theTheme.getIcon("search_project"))
        self.toggleProject.setCheckable(True)
        self.toggleProject.setChecked(self.doNextFile)
        self.toggleProject.toggled.connect(self._doToggleProject)
        self.searchOpt.addAction(self.toggleProject)

        self.searchOpt.addSeparator()

        self.toggleMatchCap = QAction("Preserve Case", self)
        self.toggleMatchCap.setToolTip("Preserve case on replace")
        self.toggleMatchCap.setIcon(self.theTheme.getIcon("search_preserve"))
        self.toggleMatchCap.setCheckable(True)
        self.toggleMatchCap.setChecked(self.doMatchCap)
        self.toggleMatchCap.toggled.connect(self._doToggleMatchCap)
        self.searchOpt.addAction(self.toggleMatchCap)

        self.searchOpt.addSeparator()

        self.cancelSearch = QAction("Close Search", self)
        self.cancelSearch.setToolTip("Close the search box [Esc]")
        self.cancelSearch.setIcon(self.theTheme.getIcon("search_cancel"))
        self.cancelSearch.triggered.connect(self._doClose)
        self.searchOpt.addAction(self.cancelSearch)

        # Buttons
        # =======
        bPx = self.searchBox.sizeHint().height()

        self.showReplace = QToolButton(self)
        self.showReplace.setArrowType(Qt.RightArrow)
        self.showReplace.setCheckable(True)
        self.showReplace.setToolTip("Show/hide the replace text box")
        self.showReplace.setStyleSheet(r"QToolButton {border: none; background: transparent;}")
        self.showReplace.toggled.connect(self._doToggleReplace)

        self.searchButton = QPushButton(self.theTheme.getIcon("search"), "")
        self.searchButton.setFixedSize(QSize(bPx, bPx))
        self.searchButton.setToolTip("Find in current document")
        self.searchButton.clicked.connect(self._doSearch)

        self.replaceButton = QPushButton(self.theTheme.getIcon("search-replace"), "")
        self.replaceButton.setFixedSize(QSize(bPx, bPx))
        self.replaceButton.setToolTip("Find and replace in current document")
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
        rCol = baseCol.redF()   + 0.1
        gCol = baseCol.greenF() - 0.1
        bCol = baseCol.blueF()  - 0.1

        mCol = max(rCol, gCol, bCol, 1.0)
        errCol = QColor()
        errCol.setRedF(rCol/mCol)
        errCol.setGreenF(gCol/mCol)
        errCol.setBlueF(bCol/mCol)

        self.rxCol = {
            True  : baseCol,
            False : errCol
        }

        logger.debug("GuiDocEditSearch initialisation complete")

        return

    def closeSearch(self):
        """Close the search box.
        """
        self.mainConf.searchCase     = self.isCaseSense
        self.mainConf.searchWord     = self.isWholeWord
        self.mainConf.searchRegEx    = self.isRegEx
        self.mainConf.searchLoop     = self.doLoop
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
        if self.isRegEx:
            self._alertSearchValid(True)
        logger.verbose("Setting search text to '%s'" % theText)
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

            elif self.mainConf.verQtValue >= 50300:
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
            self.docEditor.docAction(nwDocAction.GO_PREV)
        else:
            self.docEditor.docAction(nwDocAction.GO_NEXT)
        return

    def _doReplace(self):
        """Call the replace action function for the document editor.
        """
        self.docEditor.docAction(nwDocAction.REPL_NEXT)
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
        self.theHandle  = None

        # Make a QPalette that matches the Syntax Theme
        self.thePalette = QPalette()
        self.thePalette.setColor(QPalette.Window, QColor(*self.theTheme.colBack))
        self.thePalette.setColor(QPalette.Text, QColor(*self.theTheme.colText))

        fPx = int(0.9*self.theTheme.fontPixelSize)
        hSp = self.mainConf.pxInt(6)
        self.buttonSize = fPx + hSp

        # Main Widget Settings
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
        self.editButton = QToolButton(self)
        self.editButton.setIcon(self.theTheme.getIcon("edit"))
        self.editButton.setContentsMargins(0, 0, 0, 0)
        self.editButton.setIconSize(QSize(fPx, fPx))
        self.editButton.setFixedSize(fPx, fPx)
        self.editButton.setStyleSheet(buttonStyle)
        self.editButton.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.editButton.setVisible(False)
        self.editButton.setToolTip("Edit document meta")
        self.editButton.clicked.connect(self._editDocument)

        self.searchButton = QToolButton(self)
        self.searchButton.setIcon(self.theTheme.getIcon("search"))
        self.searchButton.setContentsMargins(0, 0, 0, 0)
        self.searchButton.setIconSize(QSize(fPx, fPx))
        self.searchButton.setFixedSize(fPx, fPx)
        self.searchButton.setStyleSheet(buttonStyle)
        self.searchButton.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.searchButton.setVisible(False)
        self.searchButton.setToolTip("Search document")
        self.searchButton.clicked.connect(self._searchDocument)

        self.minmaxButton = QToolButton(self)
        self.minmaxButton.setIcon(self.theTheme.getIcon("maximise"))
        self.minmaxButton.setContentsMargins(0, 0, 0, 0)
        self.minmaxButton.setIconSize(QSize(fPx, fPx))
        self.minmaxButton.setFixedSize(fPx, fPx)
        self.minmaxButton.setStyleSheet(buttonStyle)
        self.minmaxButton.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.minmaxButton.setVisible(False)
        self.minmaxButton.setToolTip("Toggle Focus Mode")
        self.minmaxButton.clicked.connect(self._minmaxDocument)

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
        self.outerBox.addWidget(self.editButton, 0)
        self.outerBox.addWidget(self.searchButton, 0)
        self.outerBox.addWidget(self.theTitle, 1)
        self.outerBox.addWidget(self.minmaxButton, 0)
        self.outerBox.addWidget(self.closeButton, 0)
        self.setLayout(self.outerBox)

        logger.debug("GuiDocEditHeader initialisation complete")

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

    ##
    #  Slots
    ##

    def _editDocument(self):
        """Open the edit item dialog from the main GUI.
        """
        self.theParent.editItem(self.theHandle)
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
        if self.theParent.isFocusMode:
            self.minmaxButton.setIcon(self.theTheme.getIcon("minimise"))
            self.setContentsMargins(self.buttonSize, 0, 0, 0)
            self.editButton.setVisible(False)
            self.searchButton.setVisible(False)
            self.closeButton.setVisible(False)
        else:
            self.minmaxButton.setIcon(self.theTheme.getIcon("maximise"))
            self.setContentsMargins(0, 0, 0, 0)
            self.editButton.setVisible(True)
            self.searchButton.setVisible(True)
            self.closeButton.setVisible(True)
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
        self.theHandle  = None
        self.theItem    = None

        # Make a QPalette that matches the Syntax Theme
        self.thePalette = QPalette()
        self.thePalette.setColor(QPalette.Window, QColor(*self.theTheme.colBack))
        self.thePalette.setColor(QPalette.Text, QColor(*self.theTheme.colText))

        self.sPx = int(round(0.9*self.theTheme.baseIconSize))
        fPx = int(0.9*self.theTheme.fontPixelSize)
        bSp = self.mainConf.pxInt(4)
        hSp = self.mainConf.pxInt(6)

        lblFont = self.font()
        lblFont.setPointSizeF(0.9*self.theTheme.fontPointSize)

        # Main Widget Settings
        self.setContentsMargins(0, 0, 0, 0)
        self.setAutoFillBackground(True)
        self.setPalette(self.thePalette)

        # Status
        self.statusIcon = QLabel("")
        self.statusIcon.setContentsMargins(0, 0, 0, 0)
        self.statusIcon.setFixedHeight(self.sPx)
        self.statusIcon.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        self.statusText = QLabel("Status")
        self.statusText.setIndent(0)
        self.statusText.setMargin(0)
        self.statusText.setContentsMargins(0, 0, 0, 0)
        self.statusText.setAutoFillBackground(True)
        self.statusText.setFixedHeight(fPx)
        self.statusText.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.statusText.setPalette(self.thePalette)
        self.statusText.setFont(lblFont)

        # Lines
        self.linesIcon = QLabel("")
        self.linesIcon.setPixmap(self.theTheme.getPixmap("status_lines", (self.sPx, self.sPx)))
        self.linesIcon.setContentsMargins(0, 0, 0, 0)
        self.linesIcon.setFixedHeight(self.sPx)
        self.linesIcon.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        self.linesText = QLabel("Line: 0")
        self.linesText.setIndent(0)
        self.linesText.setMargin(0)
        self.linesText.setContentsMargins(0, 0, 0, 0)
        self.linesText.setAutoFillBackground(True)
        self.linesText.setFixedHeight(fPx)
        self.linesText.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.linesText.setPalette(self.thePalette)
        self.linesText.setFont(lblFont)

        # Words
        self.wordsIcon = QLabel("")
        self.wordsIcon.setPixmap(self.theTheme.getPixmap("status_stats", (self.sPx, self.sPx)))
        self.wordsIcon.setContentsMargins(0, 0, 0, 0)
        self.wordsIcon.setFixedHeight(self.sPx)
        self.wordsIcon.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        self.wordsText = QLabel("Words: 0")
        self.wordsText.setIndent(0)
        self.wordsText.setMargin(0)
        self.wordsText.setContentsMargins(0, 0, 0, 0)
        self.wordsText.setAutoFillBackground(True)
        self.wordsText.setFixedHeight(fPx)
        self.wordsText.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.wordsText.setPalette(self.thePalette)
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

        logger.debug("GuiDocEditFooter initialisation complete")

        return

    ##
    #  Methods
    ##

    def setHandle(self, tHandle):
        """Set the handle that will populate the footer's data.
        """
        self.theHandle = tHandle
        if self.theHandle is None:
            logger.verbose("No handle set, so clearing the editor footer")
            self.theItem = None
        else:
            self.theItem = self.theProject.projTree[self.theHandle]

        self.updateInfo()
        self.updateCounts()

        return

    def updateInfo(self):
        """Update the content of text labels.
        """
        if self.theItem is None:
            sIcon = QPixmap()
            sText = ""
        else:
            iStatus = self.theItem.itemStatus
            if self.theItem.itemClass == nwItemClass.NOVEL:
                iStatus = self.theProject.statusItems.checkEntry(iStatus)
                theIcon = self.theParent.statusIcons[iStatus]
            else:
                iStatus = self.theProject.importItems.checkEntry(iStatus)
                theIcon = self.theParent.importIcons[iStatus]
            sIcon = theIcon.pixmap(self.sPx, self.sPx)
            sText = self.theItem.itemStatus

        self.statusIcon.setPixmap(sIcon)
        self.statusText.setText(sText)

        return

    def updateLineCount(self):
        """Update the word count.
        """
        if self.theItem is None:
            iLine = 0
        else:
            theCursor = self.docEditor.textCursor()
            iLine = theCursor.blockNumber() + 1

        self.linesText.setText(f"Line: {iLine:n}")

        return

    def updateCounts(self):
        """Update the word count.
        """
        if self.theItem is None:
            wCount = 0
            wDiff  = 0
        else:
            wCount = self.theItem.wordCount
            wDiff  = wCount - self.theItem.initCount

        self.wordsText.setText(f"Words: {wCount:n} ({wDiff:+n})")

        byteSize = self.docEditor.qDocument.characterCount()
        self.wordsText.setToolTip(f"Document size is {byteSize:n} bytes")

        return

# END Class GuiDocEditFooter
