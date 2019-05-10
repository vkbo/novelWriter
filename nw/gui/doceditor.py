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
import enchant

from time                import time

from PyQt5.QtWidgets     import QTextEdit, QAction, QMenu, QShortcut
from PyQt5.QtGui         import QTextCursor, QTextOption, QIcon, QKeySequence
from PyQt5.QtCore        import Qt, QTimer

from nw.gui.dochighlight import GuiDocHighlighter
from nw.gui.wordcounter  import WordCounter
from nw.enum             import nwDocAction

logger = logging.getLogger(__name__)

class GuiDocEditor(QTextEdit):

    def __init__(self, theParent):
        QTextEdit.__init__(self)

        logger.debug("Initialising DocEditor ...")

        # Class Variables
        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.docChanged = False

        # Document Variables
        self.charCount = 0
        self.wordCount = 0
        self.paraCount = 0
        self.lastEdit  = 0

        # Typography
        self.typDQOpen  = self.mainConf.fmtDoubleQuotes[0]
        self.typDQClose = self.mainConf.fmtDoubleQuotes[1]
        self.typSQOpen  = self.mainConf.fmtSingleQuotes[0]
        self.typSQClose = self.mainConf.fmtSingleQuotes[1]
        self.typApos    = self.mainConf.fmtApostrophe

        # Core Elements
        self.theDoc  = self.document()
        self.theDict = enchant.Dict(self.mainConf.spellLanguage)
        self.hLight  = GuiDocHighlighter(self.theDoc, self.theDict)

        # Context Menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._openContextMenu)

        # Editor State
        self.hasSelection = False

        if self.mainConf.textFixedW:
            self.setLineWrapMode(QTextEdit.FixedPixelWidth)
            self.setLineWrapColumnOrWidth(self.mainConf.textWidth)
        else:
            mTB = self.mainConf.textMargin[0]
            mLR = self.mainConf.textMargin[1]
            self.setViewportMargins(mLR,mTB,mLR,mTB)

        self.theDoc.setDocumentMargin(0)
        self.theDoc.contentsChange.connect(self._docChange)
        if self.mainConf.doJustify:
            self.theDoc.setDefaultTextOption(QTextOption(Qt.AlignJustify))

        self.setMinimumWidth(400)
        self.setAcceptRichText(False)
        self.setFontPointSize(self.mainConf.textSize)

        # Custom Shortcuts
        QShortcut(QKeySequence("Ctrl+."), self, context=Qt.WidgetShortcut, activated=self._openSpellContext)

        # Set Up Word Count Thread and Timer
        self.wcInterval = self.mainConf.wordCountTimer
        self.wcTimer = QTimer()
        self.wcTimer.setInterval(int(self.wcInterval*1000))
        self.wcTimer.timeout.connect(self._runCounter)

        self.wCounter = WordCounter(self)
        self.wCounter.finished.connect(self._updateCounts)

        logger.debug("DocEditor initialisation complete")

        return

    ##
    #  Class Methods
    ##

    def setDocumentChanged(self, bValue):
        self.docChanged = bValue
        self.theParent.statusBar.setDocumentStatus(self.docChanged)
        return

    def setText(self, theText):
        self.setPlainText(theText)
        self.lastEdit = time()
        self._runCounter()
        self.wcTimer.start()
        self.setDocumentChanged(False)
        return True

    def getText(self):
        theText = self.toPlainText()
        return theText

    def changeWidth(self):
        """Automatically adjust the margins so the text is centred, but only if Config.textFixedW is
        set to True.
        """
        if self.mainConf.textFixedW:
            tW  = self.width()
            sW  = self.verticalScrollBar().width()
            tM  = int((tW - sW - self.mainConf.textWidth)/2)
            mTB = self.mainConf.textMargin[0]
            self.setViewportMargins(tM,mTB,0,mTB)
        return

    def docAction(self, theAction):
        logger.verbose("Requesting action: %s" % theAction.name)
        if   theAction == nwDocAction.UNDO:     self.undo()
        elif theAction == nwDocAction.REDO:     self.redo()
        elif theAction == nwDocAction.CUT:      self.cut()
        elif theAction == nwDocAction.COPY:     self.copy()
        elif theAction == nwDocAction.PASTE:    self.paste()
        elif theAction == nwDocAction.BOLD:     self._wrapSelection("**","**")
        elif theAction == nwDocAction.ITALIC:   self._wrapSelection("_","_")
        elif theAction == nwDocAction.U_LINE:   self._wrapSelection("__","__")
        elif theAction == nwDocAction.S_QUOTE:  self._wrapSelection(self.typSQOpen,self.typSQClose)
        elif theAction == nwDocAction.D_QUOTE:  self._wrapSelection(self.typDQOpen,self.typDQClose)
        elif theAction == nwDocAction.SEL_ALL:  self._makeSelection(QTextCursor.Document)
        elif theAction == nwDocAction.SEL_PARA: self._makeSelection(QTextCursor.BlockUnderCursor)
        else:
            logger.error("Unknown or unsupported document action %s" % str(theAction))
        return

    ##
    #  Document Events and Maintenance
    ##

    def keyPressEvent(self, keyEvent):
        """Intercept key press events.
        We need to intercept key presses briefly to record the state of selection. This is in order
        to know whether we had a selection prior to triggering the _docChange slot, as we do not
        want to trigger autoreplace on selections. Autoreplace on selections messes with undo/redo
        history.
        """
        self.hasSelection = self.textCursor().hasSelection()
        QTextEdit.keyPressEvent(self, keyEvent)
        return

    ##
    #  Internal Functions
    ##

    def _openSpellContext(self):
        self._openContextMenu(self.cursorRect().center())
        return

    def _openContextMenu(self, thePos):

        theCursor = self.cursorForPosition(thePos)
        theCursor.select(QTextCursor.WordUnderCursor)
        theText = theCursor.selectedText()
        if theText == "":
            return

        mnuSuggest = QMenu()
        spIcon = QIcon.fromTheme("tools-check-spelling")
        if self.theDict.check(theText):
            mnuHead = QAction(spIcon,"No Suggestion", mnuSuggest)
            mnuSuggest.addAction(mnuHead)
        else:
            mnuHead = QAction(spIcon,"Spelling Suggestion", mnuSuggest)
            mnuSuggest.addAction(mnuHead)
            mnuSuggest.addSeparator()
            for aWord in self.theDict.suggest(theText):
                mnuWord = QAction(aWord, mnuSuggest)
                mnuWord.triggered.connect(lambda thePos, aWord=aWord : self._correctWord(theCursor, aWord))
                mnuSuggest.addAction(mnuWord)

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

    def _docChange(self, thePos, charsRemoved, charsAdded):
        self.lastEdit = time()
        self.setDocumentChanged(True)
        if not self.wcTimer.isActive():
            self.wcTimer.start()
        if self.mainConf.doReplace and not self.hasSelection:
            self._docAutoReplace(self.theDoc.findBlock(thePos))
        # logger.verbose("Doc change signal took %.3f µs" % ((time()-self.lastEdit)*1e6))
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
            theCursor.insertText("–")

        elif self.mainConf.doReplaceDash and theTwo == "–-":
            theCursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor, 2)
            theCursor.insertText("—")

        elif self.mainConf.doReplaceDots and theThree == "...":
            theCursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor, 3)
            theCursor.insertText("…")

        return

    def _runCounter(self):
        """Decide whether to run the word counter, or stop the timer due to inactivity.
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

        tHandle = self.theParent.theDocument.docHandle
        self.charCount = self.wCounter.charCount
        self.wordCount = self.wCounter.wordCount
        self.paraCount = self.wCounter.paraCount
        self.theParent.statusBar.setCounts(self.charCount,self.wordCount,self.paraCount)
        self.theParent.treeView.propagateCount(tHandle, self.wordCount)

        return

    def _wrapSelection(self, tBefore, tAfter):
        """Wraps the selected text in whatever is in tBefore and tAfter. If there is no selection, the autoSelect setting decides
        the action. AutoSelect will select the word under the cursor before wrapping it. If this feature is disabled, nothing is
        done.
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

# END Class GuiDocEditor
