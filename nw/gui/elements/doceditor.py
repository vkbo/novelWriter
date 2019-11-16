# -*- coding: utf-8 -*-
"""novelWriter GUI Document Editor

 novelWriter – GUI Document Editor
===================================
 Class holding the document editor

 File History:
 Created: 2018-09-29 [0.0.1]

"""

import logging
import nw

from time import time

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (
    qApp, QTextEdit, QAction, QMenu, QShortcut, QMessageBox
)
from PyQt5.QtGui import (
    QTextCursor, QTextOption, QKeySequence, QFont, QColor, QPalette,
    QTextDocument
)

from nw.project import NWDoc
from nw.gui.tools import GuiDocHighlighter, WordCounter
from nw.tools import NWSpellCheck, NWSpellSimple
from nw.constants import nwFiles, nwUnicode, nwDocAction, nwAlert

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

        return

    def clearEditor(self):

        self.nwDocument.clearDocument()
        self.setReadOnly(True)
        self.clear()
        self.wcTimer.stop()

        self.theHandle    = None
        self.charCount    = 0
        self.wordCount    = 0
        self.paraCount    = 0
        self.lastEdit     = 0
        self.hasSelection = False

        self.setDocumentChanged(False)
        self.theParent.noticeBar.hideNote()

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
            # We must save the current handle as clearEditor() sets it
            # to None
            tHandle = self.theHandle
            self.clearEditor()
            self.loadText(tHandle)
            self.updateDocMargins()
        else:
            self.clearEditor()

        return True

    def loadText(self, tHandle):
        """Load text from a document into the editor. If we have an io
        error, we must handle this and clear the editor so that we don't
        risk overwriting the file if it exists. This can for instance
        happen of the file contains binary elements or an encoding that
        novelWriter does not support. If load is successful, or the
        document is new (empty string) we set up the editor for editing
        the file.
        """

        theDoc = self.nwDocument.openDocument(tHandle)
        if theDoc is None:
            # There was an io error
            self.clearEditor()
            return False

        self.hLight.setHandle(tHandle)
        self.setPlainText(theDoc)
        self.setCursorPosition(self.nwDocument.theItem.cursorPos)
        self.lastEdit = time()
        self._runCounter()
        self.wcTimer.start()
        self.setDocumentChanged(False)
        self.theHandle = tHandle

        if self.nwDocument.docEditable:
            self.setReadOnly(False)
        else:
            self.theParent.noticeBar.showNote("This document is read only.")

        return True

    def saveText(self):

        if self.nwDocument.theItem is None:
            return False

        docText = self.getText()
        cursPos = self.getCursorPosition()
        theItem = self.nwDocument.theItem
        theItem.setCharCount(self.charCount)
        theItem.setWordCount(self.wordCount)
        theItem.setParaCount(self.paraCount)
        theItem.setCursorPos(cursPos)
        self.nwDocument.saveDocument(docText)
        self.setDocumentChanged(False)

        self.theParent.theIndex.scanText(theItem.itemHandle, docText)

        return True

    def updateDocMargins(self):
        """Automatically adjust the margins so the text is centred, but
        only if Config.textFixedW is set to True.
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

        docFormat = self.qDocument.rootFrame().frameFormat()
        docFormat.setLeftMargin(tM)
        docFormat.setRightMargin(tM)
        self.qDocument.rootFrame().setFrameFormat(docFormat)

        return

    ##
    #  Setters and Getters
    ##

    def setDocumentChanged(self, bValue):
        self.docChanged = bValue
        self.theParent.statusBar.setDocumentStatus(self.docChanged)
        return self.docChanged

    def getText(self):
        """Get the text content of the current document. This method
        uses QTextEdit->toPlainText for Qt versions lower than 5.9, and
        the QDocument->toRawText for higher version. The latter
        preserves non-breaking spaces, which the former does not.
        """
        if self.mainConf.verQtValue >= 50900:
            theText = self.qDocument.toRawText().replace(nwUnicode.U_PARA,"\n")
        else:
            theText = self.toPlainText()
        return theText

    def setCursorPosition(self, thePosition):
        if thePosition > 0:
            theCursor = self.textCursor()
            theCursor.setPosition(thePosition)
            self.setTextCursor(theCursor)
        return True

    def getCursorPosition(self):
        theCursor = self.textCursor()
        return theCursor.position()

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
        If the spell check mode is not defined, then toggle the current
        status saved in the class.
        """

        if theMode is None:
            theMode = not self.spellCheck

        if self.theDict.spellLanguage is None:
            theMode = False

        self.spellCheck = theMode
        self.theParent.mainMenu.setSpellCheck(theMode)
        self.theProject.setSpellCheck(theMode)
        self.hLight.setSpellCheck(theMode)
        self.hLight.rehighlight()

        logger.verbose("Spell check is set to %s" % str(theMode))

        return True

    def updateSpellCheck(self):
        """Rerun the highlighter to update spell checking status of the
        currently loaded text.
        """
        if self.spellCheck:
            self.hLight.rehighlight()
        return True

    ##
    #  General Class Methods
    ##

    def docAction(self, theAction):
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
        else:
            logger.error("Unknown or unsupported document action %s" % str(theAction))
            return False
        return True

    def isEmpty(self):
        return self.qDocument.isEmpty()

    def revealLocation(self):
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
        theCursor = self.textCursor()
        theCursor.beginEditBlock()
        theCursor.insertText("  \n")
        theCursor.endEditBlock()
        return

    def _insertNonBreakingSpace(self):
        theCursor = self.textCursor()
        theCursor.beginEditBlock()
        theCursor.insertText(nwUnicode.U_NBSP)
        theCursor.endEditBlock()
        return

    def _openSpellContext(self):
        self._openContextMenu(self.cursorRect().center())
        return

    def _openContextMenu(self, thePos):

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

    def _correctWord(self, theCursor, theWord):
        xPos = theCursor.selectionStart()
        theCursor.beginEditBlock()
        theCursor.removeSelectedText()
        theCursor.insertText(theWord)
        theCursor.endEditBlock()
        theCursor.setPosition(xPos)
        self.setTextCursor(theCursor)
        return

    def _addWord(self, theCursor):
        theWord = theCursor.selectedText().strip().strip(self.nonWord)
        logger.debug("Added '%s' to project dictionary" % theWord)
        self.theDict.addWord(theWord)
        self.hLight.setDict(self.theDict)
        self.hLight.rehighlightBlock(theCursor.block())
        return

    def _docChange(self, thePos, charsRemoved, charsAdded):
        self.lastEdit = time()
        if not self.docChanged:
            self.setDocumentChanged(True)
        if not self.wcTimer.isActive():
            self.wcTimer.start()
        if self.mainConf.doReplace and not self.hasSelection:
            self._docAutoReplace(self.qDocument.findBlock(thePos))
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

    def _runCounter(self):
        """Decide whether to run the word counter, or stop the timer due
        to inactivity.
        """
        sinceActive = time()-self.lastEdit
        if sinceActive > 5*self.wcInterval:
            logger.debug("Stopping word count timer: no activity last %.1f seconds" % sinceActive)
            self.wcTimer.stop()
        elif self.wCounter.isRunning():
            logger.verbose("Word counter thread is busy")
        else:
            logger.verbose("Starting word counter")
            self.wCounter.start()
        return

    def _updateCounts(self):
        """Slot for the word counter's finished signal
        """
        logger.verbose("Updating word count")

        tHandle = self.nwDocument.docHandle
        self.charCount = self.wCounter.charCount
        self.wordCount = self.wCounter.wordCount
        self.paraCount = self.wCounter.paraCount
        self.theParent.statusBar.setCounts(self.charCount,self.wordCount,self.paraCount)
        self.theParent.treeView.propagateCount(tHandle, self.wordCount)
        self.theParent.treeView.projectWordCount()

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

    def _makeSelection(self, selMode):
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
            from nw.tools.spellenchant import NWSpellEnchant
            self.theDict = NWSpellEnchant()
        else:
            self.theDict = NWSpellSimple()

        self.hLight.setDict(self.theDict)

        return

# END Class GuiDocEditor
