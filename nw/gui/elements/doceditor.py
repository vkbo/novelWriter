# -*- coding: utf-8 -*-
"""novelWriter GUI Document Editor

 novelWriter – GUI Document Editor
===================================
 Class holding the document editor

 File History:
 Created: 2018-09-29 [0.0.1]

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

from PyQt5.QtCore import Qt, QTimer, pyqtSlot
from PyQt5.QtWidgets import (
    qApp, QTextEdit, QAction, QMenu, QShortcut, QMessageBox
)
from PyQt5.QtGui import (
    QTextCursor, QTextOption, QKeySequence, QFont, QColor, QPalette,
    QTextDocument, QCursor
)

from nw.core import NWDoc
from nw.gui.tools import GuiDocHighlighter, WordCounter
from nw.gui.elements.doctitlebar import GuiDocTitleBar
from nw.core import NWSpellSimple
from nw.constants import nwUnicode, nwDocAction

logger = logging.getLogger(__name__)

class GuiDocEditor(QTextEdit):

    def __init__(self, theParent, theProject):
        QTextEdit.__init__(self)

        logger.debug("Initialising DocEditor ...")

        # Class Variables
        self.mainConf   = nw.CONFIG
        self.theProject = theProject
        self.theParent  = theParent
        self.theTheme   = theParent.theTheme
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
        self.nonWord   = "\"'"

        # Typography
        self.typDQOpen  = self.mainConf.fmtDoubleQuotes[0]
        self.typDQClose = self.mainConf.fmtDoubleQuotes[1]
        self.typSQOpen  = self.mainConf.fmtSingleQuotes[0]
        self.typSQClose = self.mainConf.fmtSingleQuotes[1]

        # Core Elements
        self.qDocument = self.document()
        self.qDocument.setDocumentMargin(self.mainConf.textMargin)
        self.qDocument.contentsChange.connect(self._docChange)

        # Document Title
        self.docTitle = GuiDocTitleBar(self, self.theProject)
        self.docTitle.setGeometry(0, 0, self.docTitle.width(), self.docTitle.height())
        self.setViewportMargins(0, self.docTitle.height(), 0, 0)

        # Syntax
        self.hLight = GuiDocHighlighter(self.qDocument, self.theParent)

        # Context Menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._openContextMenu)

        # Editor State
        self.hasSelection = False
        self.setMinimumWidth(300)
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

        self.wCounter = WordCounter(self)
        self.wCounter.finished.connect(self._updateCounts)

        self.initEditor()

        logger.debug("DocEditor initialisation complete")

        # Connect Functions
        self.setSelectedHandle = self.theParent.treeView.setSelectedHandle

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

        self.hasSelection = False

        self.setDocumentChanged(False)
        self.theParent.noticeBar.hideNote()
        self.docTitle.setTitleFromHandle(self.theHandle)

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
        docPalette.setColor(QPalette.Base, QColor(*self.theTheme.colBack))
        docPalette.setColor(QPalette.Text, QColor(*self.theTheme.colText))
        self.setPalette(docPalette)

        # Set default text margins
        self.qDocument.setDocumentMargin(self.mainConf.textMargin)

        # Also set the document text options for the document text flow
        theOpt = QTextOption()

        if self.mainConf.tabWidth is not None:
            if self.mainConf.verQtValue >= 51000:
                theOpt.setTabStopDistance(self.mainConf.tabWidth)
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
        self.setPlainText(theDoc)
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

        if self.nwDocument.docEditable:
            self.setReadOnly(False)
        else:
            self.theParent.noticeBar.showNote("This document is read only.")

        self.docTitle.setTitleFromHandle(self.theHandle)
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
        Config.textFixedW is enabled or we're in Zen mode. Otherwise,
        just ensure the margins are set correctly.
        """
        if self.mainConf.textFixedW or self.theParent.isZenMode:
            vBar = self.verticalScrollBar()
            if vBar.isVisible():
                sW = vBar.width()
            else:
                sW = 0
            if self.theParent.isZenMode:
                tW = self.mainConf.zenWidth
            else:
                tW = self.mainConf.textWidth
            wW = self.width()
            tM = int((wW - sW - tW)/2)
            if tM < self.mainConf.textMargin:
                tM = self.mainConf.textMargin
        else:
            tM = self.mainConf.textMargin

        tB = self.lineWidth()
        tW = self.width() - 2*tB
        tH = self.docTitle.height()
        tT = self.mainConf.textMargin - tH
        self.docTitle.setGeometry(tB, tB, tW, tH)
        self.setViewportMargins(0, tH, 0, 0)

        docFormat = self.qDocument.rootFrame().frameFormat()
        docFormat.setLeftMargin(tM)
        docFormat.setRightMargin(tM)
        if tT > 0:
            docFormat.setTopMargin(tT)
        else:
            docFormat.setTopMargin(0)

        # Updating root frame triggers a QTextDocument->contentsChange
        # signal, which we do not want as it re-runs the syntax
        # highlighter and spell checker, so we block it briefly.
        # We then emit a signal that does not trigger re-highlighting.
        self.qDocument.blockSignals(True)
        self.qDocument.rootFrame().setFrameFormat(docFormat)
        self.qDocument.blockSignals(False)

        # The line below causes issues with large documents as it
        # triggers an early repaint that seems to only render a part of
        # the document. Leaving it here as a warning for now.
        # self.qDocument.contentsChange.emit(0, 0, 0)

        return

    def updateDocTitle(self, tHandle):
        """Called when an item label is changed to check if the document
        title bar needs updating,
        """
        if tHandle == self.theHandle:
            self.docTitle.setTitleFromHandle(self.theHandle)
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
            theText = theText.replace("\u2028", "\n") # Line separators
            theText = theText.replace("\u2029", "\n") # Paragraph separators
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
        elif theAction == nwDocAction.BOLD:
            self._wrapSelection("**","**")
        elif theAction == nwDocAction.ITALIC:
            self._wrapSelection("_","_")
        elif theAction == nwDocAction.U_LINE:
            self._wrapSelection("__","__")
        elif theAction == nwDocAction.S_QUOTE:
            self._wrapSelection(self.typSQOpen,self.typSQClose)
        elif theAction == nwDocAction.D_QUOTE:
            self._wrapSelection(self.typDQOpen,self.typDQClose)
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
            self._findPrev()
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
        else:
            logger.debug("Unknown or unsupported document action %s" % str(theAction))
            return False
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

    ##
    #  Document Events and Maintenance
    ##

    def keyPressEvent(self, keyEvent):
        """Intercept key press events.
        We need to intercept key presses briefly to record the state of
        selection. This is in order to know whether we had a selection
        prior to triggering the _docChange slot, as we do not want to
        trigger autoreplace on selections. Autoreplace on selections
        messes with undo/redo history.
        We also need to intercept the Shift key modifier for certain key
        combinations that modifies standard keys like enter and space.
        However, we don't want to spend a lot of time in this function
        as it is triggered on every keypress when typing.
        """
        self.hasSelection = self.textCursor().hasSelection()

        if keyEvent.modifiers() == Qt.ShiftModifier:
            theKey = keyEvent.key()
            if theKey == Qt.Key_Return:
                self._insertHardBreak()
            elif theKey == Qt.Key_Enter:
                self._insertHardBreak()
            elif theKey == Qt.Key_Space:
                self._insertNonBreakingSpace()
            else:
                QTextEdit.keyPressEvent(self, keyEvent)
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
        if self.mainConf.doReplace and not self.hasSelection:
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

        self.theParent.statusBar.setCounts(self.charCount, self.wordCount, self.paraCount)
        self.theParent.treeView.propagateCount(self.theHandle, self.wordCount)
        self.theParent.treeView.projectWordCount()
        self.theParent.treeMeta.updateCounts(
            self.theHandle, self.charCount, self.wordCount, self.paraCount
        )
        self._checkDocSize(self.charCount)

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

    def _insertHardBreak(self):
        """Inserts a hard line break at the cursor position.
        """
        theCursor = self.textCursor()
        theCursor.beginEditBlock()
        theCursor.insertText("  \n")
        theCursor.endEditBlock()
        return

    def _insertNonBreakingSpace(self):
        """Inserts a non-breaking space at the cursor position.
        """
        theCursor = self.textCursor()
        theCursor.beginEditBlock()
        theCursor.insertText(nwUnicode.U_NBSP)
        theCursor.endEditBlock()
        return

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

    def _wrapSelection(self, tBefore, tAfter):
        """Wraps the selected text in whatever is in tBefore and tAfter.
        If there is no selection, the autoSelect setting decides the
        action. AutoSelect will select the word under the cursor before
        wrapping it. If this feature is disabled, nothing is done.
        """
        theCursor = self.textCursor()
        if self.mainConf.autoSelect and not theCursor.hasSelection():
            theCursor.select(QTextCursor.WordUnderCursor)
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
        else:
            logger.warning("No selection made, nothing to do")
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
        self.theParent.searchBar.setSearchText(selText)
        return

    def _beginReplace(self):
        """Opens the replace line of the search bar and sets the replace
        text.
        """
        self._beginSearch()
        self.theParent.searchBar.setReplaceText("")
        return

    def _findNext(self):
        """Searches for the next occurrence of the search bar text in
        the document. Wraps back to the top if not found.
        """
        searchFor = self.theParent.searchBar.getSearchText()
        wasFound  = self.find(searchFor)
        if not wasFound:
            theCursor = self.textCursor()
            theCursor.movePosition(QTextCursor.Start)
            self.setTextCursor(theCursor)
        return

    def _findPrev(self):
        """Searches for the previous occurrence of the search bar text
        in the document. Wraps back to the end if not found.
        """
        searchFor = self.theParent.searchBar.getSearchText()
        wasFound  = self.find(searchFor, QTextDocument.FindBackward)
        if not wasFound:
            theCursor = self.textCursor()
            theCursor.movePosition(QTextCursor.End)
            self.setTextCursor(theCursor)
        return

    def _replaceNext(self):
        """Searches for the next occurrence of the search bar text in
        the document and replaces it with the replace text. Wraps back
        to the top if not found.
        """
        theCursor = self.textCursor()
        searchFor = self.theParent.searchBar.getSearchText()
        replWith  = self.theParent.searchBar.getReplaceText()
        if theCursor.hasSelection() and theCursor.selectedText() == searchFor:
            xPos = theCursor.selectionStart()
            theCursor.beginEditBlock()
            theCursor.removeSelectedText()
            theCursor.insertText(replWith)
            theCursor.endEditBlock()
            theCursor.setPosition(xPos)
            self.setTextCursor(theCursor)
            logger.verbose("Replaced occurrence of '%s' with '%s' on line %d" % (
                searchFor, replWith, theCursor.blockNumber()
            ))
        if searchFor != "":
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

# END Class GuiDocEditor
