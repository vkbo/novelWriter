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

from PyQt5.QtWidgets     import QWidget, QTextEdit, QVBoxLayout, QToolBar, QAction
from PyQt5.QtCore        import Qt, QSize, QTimer
from PyQt5.QtGui         import QIcon

from nw.gui.dochighlight import GuiDocHighlighter
from nw.gui.wordcounter  import WordCounter

logger = logging.getLogger(__name__)

class GuiDocEditor(QWidget):

    def __init__(self, theParent):
        QWidget.__init__(self)

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

        self.outerBox  = QVBoxLayout()
        self.guiEditor = QTextEdit()
        if self.mainConf.textFixedW:
            self.guiEditor.setLineWrapMode(QTextEdit.FixedPixelWidth)
            self.guiEditor.setLineWrapColumnOrWidth(self.mainConf.textWidth)
        else:
            mTB = self.mainConf.textMargin[0]
            mLR = self.mainConf.textMargin[1]
            self.guiEditor.setViewportMargins(mLR,mTB,mLR,mTB)

        self.hLight = GuiDocHighlighter(self.guiEditor.document())

        self.setLayout(self.outerBox)

        self.editToolBar = QToolBar()
        self._buildTabToolBar()

        self.outerBox.addWidget(self.editToolBar)
        self.outerBox.addWidget(self.guiEditor)

        self.guiEditor.setMinimumWidth(400)
        self.guiEditor.setAcceptRichText(False)
        self.guiEditor.keyPressEvent = self.keyPressEvent

        self.theDoc = self.guiEditor.document()
        self.theDoc.setDocumentMargin(0)
        self.theDoc.contentsChange.connect(self._docChange)

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
        self.guiEditor.setPlainText(theText)
        self.lastEdit = time()
        self._runCounter()
        self.wcTimer.start()
        return True

    def getText(self):
        theText = self.guiEditor.toPlainText()
        return theText

    def changeWidth(self):
        """Automatically adjust the margins so the text is centred, but only if Config.textFixedW is
        set to True.
        """
        if self.mainConf.textFixedW:
            tW  = self.guiEditor.width()
            sW  = self.guiEditor.verticalScrollBar().width()
            tM  = int((tW - sW - self.mainConf.textWidth)/2)
            mTB = self.mainConf.textMargin[0]
            self.guiEditor.setViewportMargins(tM,mTB,0,mTB)
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
        self.hasSelection = self.guiEditor.textCursor().hasSelection()
        QTextEdit.keyPressEvent(self.guiEditor, keyEvent)
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
        theCursor = self.guiEditor.textCursor()
        thePos    = theCursor.positionInBlock()
        theLen    = len(theText)

        if theLen < 1 or thePos-1 > theLen:
            return

        theOne   = theText[thePos-1:thePos]
        theTwo   = theText[thePos-2:thePos]
        theThree = theText[thePos-3:thePos]

        if self.mainConf.doReplaceDQuote and theTwo == " \"":
            self.guiEditor.textCursor().deletePreviousChar()
            self.guiEditor.textCursor().insertText(self.typSQOpen)

        elif self.mainConf.doReplaceDQuote and theOne == "\"":
            self.guiEditor.textCursor().deletePreviousChar()
            if thePos == 1:
                self.guiEditor.textCursor().insertText(self.typDQOpen)
            else:
                self.guiEditor.textCursor().insertText(self.typDQClose)

        elif self.mainConf.doReplaceSQuote and theTwo == " '":
            self.guiEditor.textCursor().deletePreviousChar()
            self.guiEditor.textCursor().insertText(self.typSQOpen)

        elif self.mainConf.doReplaceSQuote and theOne == "'":
            self.guiEditor.textCursor().deletePreviousChar()
            if thePos == 1:
                self.guiEditor.textCursor().insertText(self.typSQOpen)
            else:
                self.guiEditor.textCursor().insertText(self.typSQClose)

        elif self.mainConf.doReplaceDash and theTwo == "--":
            self.guiEditor.textCursor().deletePreviousChar()
            self.guiEditor.textCursor().deletePreviousChar()
            self.guiEditor.textCursor().insertText("–")

        elif self.mainConf.doReplaceDash and theTwo == "–-":
            self.guiEditor.textCursor().deletePreviousChar()
            self.guiEditor.textCursor().deletePreviousChar()
            self.guiEditor.textCursor().insertText("—")

        elif self.mainConf.doReplaceDots and theThree == "...":
            self.guiEditor.textCursor().deletePreviousChar()
            self.guiEditor.textCursor().deletePreviousChar()
            self.guiEditor.textCursor().deletePreviousChar()
            self.guiEditor.textCursor().insertText("…")

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

    ##
    #  GUI Builder
    ##

    def _buildTabToolBar(self):
        toolBar = self.editToolBar
        toolBar.setToolButtonStyle(Qt.ToolButtonIconOnly)
        toolBar.setIconSize(QSize(16,16))

        # Text > Bold
        tbTextBold = QAction(QIcon.fromTheme("format-text-bold"), "Bold (Ctrl+B)", toolBar)
        tbTextBold.setShortcut("Ctrl+B")
        tbTextBold.setStatusTip("Toggle Selected Text Bold")
        toolBar.addAction(tbTextBold)

        # Text > Italics
        tbTextItalic = QAction(QIcon.fromTheme("format-text-italic"), "Italic (Ctrl+I)", toolBar)
        tbTextItalic.setShortcut("Ctrl+I")
        tbTextItalic.setStatusTip("Toggle Selected Text Italic")
        toolBar.addAction(tbTextItalic)

        # Text > Underline
        tbTextUnderline = QAction(QIcon.fromTheme("format-text-underline"), "Underline (Ctrl+U)", toolBar)
        tbTextUnderline.setShortcut("Ctrl+U")
        tbTextUnderline.setStatusTip("Toggle Selected Text Underline")
        toolBar.addAction(tbTextUnderline)

        # Text > Strikethrough
        tbTextStrikethrough = QAction(QIcon.fromTheme("format-text-strikethrough"), "Strikethrough (Ctrl+D)", toolBar)
        tbTextStrikethrough.setShortcut("Ctrl+D")
        tbTextStrikethrough.setStatusTip("Toggle Selected Text Strikethrough")
        toolBar.addAction(tbTextStrikethrough)

        # --------------------
        toolBar.addSeparator()

        # Edit > Cut
        tbEditCut = QAction(QIcon.fromTheme("edit-cut"), "Cut (Ctrl+X)", toolBar)
        tbEditCut.setShortcut("Ctrl+X")
        tbEditCut.setStatusTip("Cut Selected Text")
        toolBar.addAction(tbEditCut)

        # Edit > Copy
        tbEditCopy = QAction(QIcon.fromTheme("edit-copy"), "Copy (Ctrl+C)", toolBar)
        tbEditCopy.setShortcut("Ctrl+C")
        tbEditCopy.setStatusTip("Copy Selected Text")
        toolBar.addAction(tbEditCopy)

        # Edit > Paste
        tbEditPaste = QAction(QIcon.fromTheme("edit-paste"), "Paste (Ctrl+V)", toolBar)
        tbEditPaste.setShortcut("Ctrl+V")
        tbEditPaste.setStatusTip("Paste Text")
        toolBar.addAction(tbEditPaste)

        # --------------------
        toolBar.addSeparator()

        # Edit > Undo
        tbEditUndo = QAction(QIcon.fromTheme("edit-undo"), "Undo (Ctrl+Z)", toolBar)
        tbEditUndo.setShortcut("Ctrl+Z")
        tbEditUndo.setStatusTip("Undo Last Change")
        toolBar.addAction(tbEditUndo)

        # Edit > Redo
        tbEditRedo = QAction(QIcon.fromTheme("edit-redo"), "Redo (Ctrl+Y)", toolBar)
        tbEditRedo.setShortcut("Ctrl+Y")
        tbEditRedo.setStatusTip("Revert Last Undo")
        toolBar.addAction(tbEditRedo)

        return

# END Class GuiDocEditor
