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

from time import time

from PyQt5.QtCore import (
    Qt, QSize, QThread, QTimer, pyqtSlot, QRegExp, QRegularExpression
)
from PyQt5.QtGui import (
    QTextCursor, QTextOption, QKeySequence, QFont, QColor, QPalette, QIcon,
    QTextDocument, QCursor, QPixmap
)
from PyQt5.QtWidgets import (
    qApp, QTextEdit, QAction, QMenu, QShortcut, QMessageBox, QWidget, QLabel,
    QToolBar, QToolButton, QHBoxLayout, QGridLayout, QLineEdit, QPushButton,
    QFrame
)

from nw.core import NWDoc, NWSpellSimple, countWords
from nw.gui.dochighlight import GuiDocHighlighter
from nw.common import transferCase
from nw.constants import (
    nwAlert, nwUnicode, nwDocAction, nwDocInsert, nwInsertSymbols, nwItemClass
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
        self.docChanged = False
        self.spellCheck = False
        self.nwDocument = NWDoc(self.theProject, self.theParent)
        self.theHandle  = None

        # Document Variables
        self.charCount = 0
        self.wordCount = 0
        self.paraCount = 0
        self.lastEdit  = 0
        self.bigDoc    = False
        self.doReplace = False
        self.nonWord   = "\"'"

        # Typography
        self.typDQOpen  = self.mainConf.fmtDoubleQuotes[0]
        self.typDQClose = self.mainConf.fmtDoubleQuotes[1]
        self.typSQOpen  = self.mainConf.fmtSingleQuotes[0]
        self.typSQClose = self.mainConf.fmtSingleQuotes[1]

        # Core Elements
        self.qDocument = self.document()
        self.qDocument.contentsChange.connect(self._docChange)

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

        # Set Up Word Count Thread and Timer
        self.wcInterval = self.mainConf.wordCountTimer
        self.wcTimer = QTimer()
        self.wcTimer.setInterval(int(self.wcInterval*1000))
        self.wcTimer.timeout.connect(self._runCounter)

        self.wCounter = BackgroundWordCounter(self)
        self.wCounter.finished.connect(self._updateCounts)

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
        self.bigDoc    = False
        self.doReplace = False

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

        if self.mainConf.verQtValue >= 51000:
            theOpt.setTabStopDistance(self.mainConf.getTabWidth())
        if self.mainConf.doJustify:
            theOpt.setAlignment(Qt.AlignJustify)
        if self.mainConf.showTabsNSpaces:
            theOpt.setFlags(theOpt.flags() | QTextOption.ShowTabsAndSpaces)
        if self.mainConf.showLineEndings:
            theOpt.setFlags(theOpt.flags() | QTextOption.ShowLineAndParagraphSeparators)

        self.qDocument.setDefaultTextOption(theOpt)

        # Initialise the syntax highlighter
        self.hLight.initHighlighter()

        # If we have a document open, we should reload it in case the
        # font changed, otherwise we just clear the editor entirely,
        # which makes it read only.
        if self.theHandle is not None:
            self.reloadText()
        else:
            self.clearEditor()

        return True

    def reloadText(self):
        """Reloads the document currently being edited.
        """
        if self.theHandle is not None:
            tHandle = self.theHandle
            self.clearEditor()
            self.loadText(tHandle, showStatus=False)
        return

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

        qApp.setOverrideCursor(QCursor(Qt.WaitCursor))
        self.hLight.setHandle(tHandle)

        # Check that the document is not too big for full, initial spell
        # checking. If it is too big, we switch to only check as we type
        self._checkDocSize(len(theDoc))
        spTemp = self.hLight.spellCheck
        if self.bigDoc:
            self.hLight.spellCheck = False

        bfTime = time()
        self._allowAutoReplace(False)
        self.setPlainText(theDoc)
        self._allowAutoReplace(True)
        afTime = time()
        logger.debug("Document highlighted in %.3f milliseconds" % (1000*(afTime-bfTime)))

        if tLine is None:
            self.setCursorPosition(self.nwDocument.theItem.cursorPos)
        else:
            self.setCursorLine(tLine)
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
        qApp.restoreOverrideCursor()

        return True

    def replaceText(self, theText):
        """Replaces the text of the current document with the provided
        text. This also clears undo history.
        """
        self.setPlainText(theText)
        self.setDocumentChanged(True)
        self.updateDocMargins()
        return

    def saveText(self):
        """Save the text currently in the editor to the NWDoc object,
        and update the NWItem meta data.
        """
        if self.nwDocument.theItem is None:
            return False

        docText = self.getText()
        cursPos = self.getCursorPosition()
        self.nwDocument.theItem.setCharCount(self.charCount)
        self.nwDocument.theItem.setWordCount(self.wordCount)
        self.nwDocument.theItem.setParaCount(self.paraCount)
        self.nwDocument.theItem.setCursorPos(cursPos)
        self.nwDocument.saveDocument(docText)
        self.setDocumentChanged(False)

        self.theParent.theIndex.scanText(
            self.nwDocument.theItem.itemHandle, docText
        )

        return True

    def updateDocMargins(self):
        """Automatically adjust the margins so the text is centred if
        Config.textFixedW is enabled or we're in Focus Mode. Otherwise,
        just ensure the margins are set correctly.
        """
        wW = self.width()
        cM = self.mainConf.getTextMargin()

        vBar = self.verticalScrollBar()
        if vBar.isVisible():
            sW = vBar.width()
        else:
            sW = 0

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
        fY = self.height() - fH - tB
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
        return True

    def getCursorPosition(self):
        """Find the cursor position in the document.
        """
        theCursor = self.textCursor()
        return theCursor.position()

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
    #  Spell Checking
    ##

    def setDictionaries(self):
        """Set the spell checker dictionary language, and update the
        status bar to show the one actually loaded by the spell checker
        class.
        """
        self.theDict.setLanguage(self.mainConf.spellLanguage, self.theProject.projDict)
        self.theParent.statusBar.setLanguage(self.theDict.spellLanguage)
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
                "Document re-highlighted in %.3f milliseconds" % (1000*(afTime-bfTime))
            )

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
                fileLoc = str(self.nwDocument.fileLoc)
            ))
        return

    def insertText(self, theInsert):
        """Insert a specific type of text at the cursor position.
        """
        if isinstance(theInsert, str):
            theText = theInsert
        elif theInsert in nwInsertSymbols.SYMBOLS:
            theText = nwInsertSymbols.SYMBOLS[theInsert]
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

    ##
    #  Document Events and Maintenance
    ##

    def keyPressEvent(self, keyEvent):
        """Intercept key press events.
        We need to intercept a few key sequences:
          * The return key redirects here even if the search box has
            focus. Since we need the return key to continue search, we
            block any further interaction here while it's in focus.
          * The undo sequence bypasses the doAction pathway from the
            menu, so we redirect it back from here.
          * The default redo sequence is Ctrl+Shift+Z, which we don't
            use, so we block it.
        """
        if self.docSearch.searchBox.hasFocus():
            return
        elif keyEvent == QKeySequence.Redo:
            return
        elif keyEvent == QKeySequence.Undo:
            self.docAction(nwDocAction.UNDO)
        else:
            QTextEdit.keyPressEvent(self, keyEvent)
        return

    def mouseReleaseEvent(self, mEvent):
        """If the mouse button is released and the control key is
        pressed, check if we're clicking on a tag, and trigger the
        follow tag function.
        """
        if qApp.keyboardModifiers() == Qt.ControlModifier:
            theCursor = self.cursorForPosition(mEvent.pos())
            self._followTag(theCursor)
        QTextEdit.mouseReleaseEvent(self, mEvent)
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
        if not self.spellCheck:
            return

        theCursor = self.cursorForPosition(thePos)
        theCursor.select(QTextCursor.WordUnderCursor)

        theWord = theCursor.selectedText().strip().strip(self.nonWord)
        if theWord == "":
            return

        logger.verbose("Looking up '%s' in the dictionary" % theWord)
        if self.theDict.checkWord(theWord):
            return

        mnuSuggest = QMenu()
        mnuHead = QAction("Spelling Suggestion(s)", mnuSuggest)
        mnuSuggest.addAction(mnuHead)
        mnuSuggest.addSeparator()
        theSuggest = self.theDict.suggestWords(theWord)
        if len(theSuggest) > 0:
            for aWord in theSuggest:
                mnuWord = QAction(aWord, mnuSuggest)
                mnuWord.triggered.connect(
                    lambda thePos, aWord=aWord : self._correctWord(theCursor, aWord)
                )
                mnuSuggest.addAction(mnuWord)
            mnuSuggest.addSeparator()
            mnuAdd = QAction("Add Word to Dictionary", mnuSuggest)
            mnuAdd.triggered.connect(lambda thePos : self._addWord(theCursor))
            mnuSuggest.addAction(mnuAdd)
        else:
            mnuHead = QAction("No Suggestions", mnuSuggest)
            mnuSuggest.addAction(mnuHead)

        mnuSuggest.exec_(self.viewport().mapToGlobal(thePos))

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
        sinceActive = time()-self.lastEdit
        if sinceActive > 5*self.wcInterval:
            logger.debug(
                "Stopping word count timer: no activity last %.1f seconds" % sinceActive
            )
            self.wcTimer.stop()
        elif self.wCounter.isRunning():
            logger.verbose("Word counter thread is busy")
        else:
            logger.verbose("Starting word counter")
            self.wCounter.start()
        return

    @pyqtSlot()
    def _updateCounts(self):
        """Slot for the word counter's finished signal
        """
        if self.theHandle is None or self.nwDocument.theItem is None:
            return

        logger.verbose("Updating word count")

        self.charCount = self.wCounter.charCount
        self.wordCount = self.wCounter.wordCount
        self.paraCount = self.wCounter.paraCount
        self.nwDocument.theItem.setCharCount(self.charCount)
        self.nwDocument.theItem.setWordCount(self.wordCount)
        self.nwDocument.theItem.setParaCount(self.paraCount)

        self.theParent.treeView.propagateCount(self.theHandle, self.wordCount)
        self.theParent.treeView.projectWordCount()
        self.theParent.treeMeta.updateCounts(
            self.theHandle, self.charCount, self.wordCount, self.paraCount
        )
        self._checkDocSize(self.charCount)
        self.docFooter.updateCounts()

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
        if theSize > self.mainConf.bigDocLimit*1000:
            logger.info(
                "The document size is %d > %d, big doc mode is enabled" % (
                theSize, self.mainConf.bigDocLimit*1000
            ))
            self.bigDoc = True
        else:
            self.bigDoc = False
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
            return

        theText = theBlock.text()
        if len(theText.strip()) == 0:
            logger.debug("Empty block selected for action %s" % str(docAction))
            return

        # Remove existing format first, if any
        if theText.startswith("@"):
            logger.error("Cannot apply block format to keyword/value line")
            return
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
            return

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

        return

    def _makeSelection(self, selMode):
        """Wrapper function to select a word based on a selection mode.
        """
        theCursor = self.textCursor()
        theCursor.clearSelection()
        theCursor.select(selMode)
        self.setTextCursor(theCursor)
        return

    def _beginSearch(self):
        """Sets the selected text as the search text for the search bar.
        """
        theCursor = self.textCursor()
        if theCursor.hasSelection():
            selText = theCursor.selectedText()
        else:
            selText = ""
        self.docSearch.setSearchText(selText)
        self.updateDocMargins()
        return

    def _beginReplace(self):
        """Opens the replace line of the search bar and sets the replace
        text.
        """
        self._beginSearch()
        self.docSearch.setReplaceText("")
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

        searchFor = self.docSearch.getSearchText()
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
                self.find(searchFor, findOpt)

        return

    def _replaceNext(self):
        """Searches for the next occurrence of the search bar text in
        the document and replaces it with the replace text. Calls search
        next automatically when done.
        """
        if not self.docSearch.isVisible():
            self._beginSearch()
            return

        theCursor = self.textCursor()
        if not theCursor.hasSelection():
            return

        searchFor = self.docSearch.getSearchText()
        replWith  = self.docSearch.getReplaceText()
        selText   = theCursor.selectedText()

        if self.docSearch.doMatchCap:
            replWith = transferCase(selText, replWith)

        if not self.docSearch.isCaseSense:
            isMatch = searchFor.lower() == selText.lower()
        else:
            isMatch = searchFor == selText

        if isMatch:
            theCursor.beginEditBlock()
            theCursor.removeSelectedText()
            theCursor.insertText(replWith)
            theCursor.endEditBlock()
            theCursor.setPosition(theCursor.selectionEnd())
            self.setTextCursor(theCursor)
            logger.verbose("Replaced occurrence of '%s' with '%s' on line %d" % (
                searchFor, replWith, theCursor.blockNumber()
            ))

        if searchFor:
            self._findNext()

        return

    def _setupSpellChecking(self):
        """Create the spell checking object based on the spellTool
        setting in config.
        """
        if self.mainConf.spellTool == "enchant":
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
#  The Off GUI Thread Word Counter
#  Runs the word counter in the background for the DocEditor
# =============================================================================================== #

class BackgroundWordCounter(QThread):

    def __init__(self, docEditor):
        QThread.__init__(self, docEditor)
        self.docEditor = docEditor
        self.charCount = 0
        self.wordCount = 0
        self.paraCount = 0
        return

    def run(self):
        """Overloaded run function for the word counter, forwarding the
        call to the function that does the actual counting.
        """
        theText = self.docEditor.getText()
        cC, wC, pC = countWords(theText)
        self.charCount = cC
        self.wordCount = wC
        self.paraCount = pC
        return

## END Class BackgroundWordCounter

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
        fPx = int(0.9*self.theTheme.fontPixelSize)
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
        self.searchBox = QLineEdit()
        self.searchBox.setFont(boxFont)
        self.searchBox.setPlaceholderText("Search")
        self.searchBox.returnPressed.connect(self._doSearch)

        self.replaceBox = QLineEdit()
        self.replaceBox.setFont(boxFont)
        self.replaceBox.setPlaceholderText("Replace")
        self.replaceBox.returnPressed.connect(self._doSearch)

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

        self.searchButton = QPushButton(self.theTheme.getIcon("search"),"")
        self.searchButton.setFixedSize(QSize(bPx, bPx))
        self.searchButton.setToolTip("Find in current document")
        self.searchButton.clicked.connect(self._doSearch)

        self.replaceButton = QPushButton(self.theTheme.getIcon("search-replace"),"")
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

    ##
    #  Get and Set Functions
    ##

    def setSearchText(self, theText):
        """Open the search bar and set the search text to the text
        provided, if any.
        """
        if not self.isVisible():
            self.setVisible(True)
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

    def getSearchText(self):
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

        self.closeButton.setVisible(True)
        self.minmaxButton.setVisible(True)

        return True

    ##
    #  Slots
    ##

    def _closeDocument(self):
        """Trigger the close editor/viewer on the main window.
        """
        self.theParent.closeDocEditor()
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
            self.closeButton.setVisible(False)
        else:
            self.minmaxButton.setIcon(self.theTheme.getIcon("maximise"))
            self.setContentsMargins(2*self.buttonSize, 0, 0, 0)
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

        # Make a QPalette that matches the Syntax Theme
        self.thePalette = QPalette()
        self.thePalette.setColor(QPalette.Window, QColor(*self.theTheme.colBack))
        self.thePalette.setColor(QPalette.Text, QColor(*self.theTheme.colText))

        self.sPx = int(round(0.9*self.theTheme.baseIconSize))
        fPx = int(0.9*self.theTheme.fontPixelSize)
        bSp = self.mainConf.pxInt(4)
        hSp = self.mainConf.pxInt(8)

        lblFont = self.font()
        lblFont.setPointSizeF(0.9*self.theTheme.fontPointSize)

        # Main Widget Settings
        self.setContentsMargins(0, 0, 0, 0)
        self.setAutoFillBackground(True)
        self.setPalette(self.thePalette)

        buttonStyle = (
            "QToolButton {{border: none; background: transparent;}} "
            "QToolButton:hover {{border: none; background: rgba({0},{1},{2},0.2);}}"
        ).format(*self.theTheme.colText)

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
        self.updateInfo()
        self.updateCounts()
        return

    def updateInfo(self):
        """Update the content of text labels.
        """
        nwItem = self.theProject.projTree[self.theHandle]
        if nwItem is None:
            sIcon  = QPixmap()
            sText  = ""
        else:
            iStatus = nwItem.itemStatus
            if nwItem.itemClass == nwItemClass.NOVEL:
                iStatus = self.theProject.statusItems.checkEntry(iStatus)
                theIcon = self.theParent.statusIcons[iStatus]
            else:
                iStatus = self.theProject.importItems.checkEntry(iStatus)
                theIcon = self.theParent.importIcons[iStatus]
            sIcon = theIcon.pixmap(self.sPx, self.sPx)
            sText = nwItem.itemStatus

        self.statusIcon.setPixmap(sIcon)
        self.statusText.setText(sText)

        return

    def updateCounts(self):
        """Update the word counts.
        """
        nwItem = self.theProject.projTree[self.theHandle]
        if nwItem is None:
            wCount = 0
            wDiff  = 0
        else:
            wCount = nwItem.wordCount
            wDiff  = wCount - nwItem.initCount

        self.wordsText.setText("Words: {:n} ({:+n})".format(wCount, wDiff))

        return

# END Class GuiDocEditFooter
