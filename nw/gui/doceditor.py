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

from time                import time

from PyQt5.QtWidgets     import QTextEdit
from PyQt5.QtCore        import QTimer
from PyQt5.QtGui         import QTextCursor

from nw.gui.dochighlight import GuiDocHighlighter
from nw.gui.wordcounter  import WordCounter
from nw.enum             import nwDocAction

logger = logging.getLogger(__name__)

class GuiDocEditor(QTextEdit):

    def __init__(self, theParent):
        QTextEdit.__init__(self)

        logger.debug("Initialising DocEditor ...")
        
        # Class Variables
        self.mainConf  = nw.CONFIG
        self.theParent = theParent

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

        # Editor State
        self.hasSelection = False

        if self.mainConf.textFixedW:
            self.setLineWrapMode(QTextEdit.FixedPixelWidth)
            self.setLineWrapColumnOrWidth(self.mainConf.textWidth)
        else:
            mTB = self.mainConf.textMargin[0]
            mLR = self.mainConf.textMargin[1]
            self.setViewportMargins(mLR,mTB,mLR,mTB)

        self.theDoc = self.document()
        self.theDoc.setDocumentMargin(0)
        self.theDoc.contentsChange.connect(self._docChange)
        self.hLight = GuiDocHighlighter(self.theDoc)

        self.setMinimumWidth(400)
        self.setAcceptRichText(False)

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

    def setText(self, theText):
        self.setPlainText(theText)
        self.lastEdit = time()
        self._runCounter()
        self.wcTimer.start()
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
        if   theAction == nwDocAction.UNDO:    self.undo()
        elif theAction == nwDocAction.REDO:    self.redo()
        elif theAction == nwDocAction.CUT:     self.cut()
        elif theAction == nwDocAction.COPY:    self.copy()
        elif theAction == nwDocAction.PASTE:   self.paste()
        elif theAction == nwDocAction.BOLD:    self._wrapSelection("**","**")
        elif theAction == nwDocAction.ITALIC:  self._wrapSelection("_","_")
        elif theAction == nwDocAction.U_LINE:  self._wrapSelection("__","__")
        elif theAction == nwDocAction.S_QUOTE: self._wrapSelection(self.typSQOpen,self.typSQClose)
        elif theAction == nwDocAction.D_QUOTE: self._wrapSelection(self.typDQOpen,self.typDQClose)
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

    def _docChange(self, thePos, charsRemoved, charsAdded):
        self.lastEdit = time()
        if not self.wcTimer.isActive():
            self.wcTimer.start()
        if self.mainConf.doReplace and not self.hasSelection:
            self._docAutoReplace(self.theDoc.findBlock(thePos))
        logger.verbose("Doc change signal took %.3f µs" % ((time()-self.lastEdit)*1e6))
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
            theCursor.beginEditBlock()
            theCursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor, 1)
            theCursor.insertText(self.typDQOpen)
            theCursor.endEditBlock()

        elif self.mainConf.doReplaceDQuote and theOne == "\"":
            theCursor.beginEditBlock()
            theCursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor, 1)
            if thePos == 1:
                theCursor.insertText(self.typDQOpen)
            else:
                theCursor.insertText(self.typDQClose)
            theCursor.endEditBlock()

        elif self.mainConf.doReplaceSQuote and theTwo == " '":
            theCursor.beginEditBlock()
            theCursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor, 1)
            theCursor.insertText(self.typSQOpen)
            theCursor.endEditBlock()

        elif self.mainConf.doReplaceSQuote and theOne == "'":
            theCursor.beginEditBlock()
            theCursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor, 1)
            if thePos == 1:
                theCursor.insertText(self.typSQOpen)
            else:
                theCursor.insertText(self.typSQClose)
            theCursor.endEditBlock()

        elif self.mainConf.doReplaceDash and theTwo == "--":
            theCursor.beginEditBlock()
            theCursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor, 2)
            theCursor.insertText("–")
            theCursor.endEditBlock()

        elif self.mainConf.doReplaceDash and theTwo == "–-":
            theCursor.beginEditBlock()
            theCursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor, 2)
            theCursor.insertText("—")
            theCursor.endEditBlock()

        elif self.mainConf.doReplaceDots and theThree == "...":
            theCursor.beginEditBlock()
            theCursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor, 3)
            theCursor.insertText("…")
            theCursor.endEditBlock()

        return

    def _runCounter(self):
        """Decide whether to run the word counter, or stop the timer due to inactivity.
        """
        sinceActive = time()-self.lastEdit
        if sinceActive > 5*self.wcInterval:
            logger.verbose("Stopping word count timer due to no activity over the last %.3f seconds" % sinceActive)
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

# END Class GuiDocEditor
