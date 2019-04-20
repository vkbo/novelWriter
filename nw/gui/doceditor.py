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

from PyQt5.QtWidgets     import QWidget, QTextEdit, QHBoxLayout, QVBoxLayout, QFrame, QSplitter, QToolBar, QAction, QScrollArea
from PyQt5.QtCore        import Qt, QSize, QSizeF
from PyQt5.QtGui         import QIcon, QFont, QTextCursor, QTextFormat, QTextBlockFormat

from nw.gui.dochighlight import GuiDocHighlighter

logger = logging.getLogger(__name__)

class GuiDocEditor(QWidget):

    def __init__(self, theParent):
        QWidget.__init__(self)

        logger.debug("Initialising DocEditor ...")
        self.mainConf  = nw.CONFIG
        self.theParent = theParent
        self.charCount = 0
        self.wordCount = 0
        self.lineCount = 0

        # Internal Temps
        self.blockWords = {}
        self.currEditBlock = -1
        self.currEditStart =  0
        self.currEditFinal =  0

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

        self.theDoc = self.guiEditor.document()
        self.theDoc.setDocumentMargin(0)
        self.theDoc.contentsChange.connect(self._docChange)

        logger.debug("DocEditor initialisation complete")

        return

    def setText(self, theText):

        self.guiEditor.setPlainText(theText)

        self.charCount = self.theDoc.characterCount()
        self.wordCount = 0

        self.currEditBlock = -1
        self.currEditWords =  0

        tStart = time()
        self.blockWords = {}
        for n in range(self.theDoc.blockCount()):
            self._countWords(self.theDoc.findBlockByNumber(n))
        self.wordCount = sum(self.blockWords.values())
        logger.verbose("Doc word count took %.3f µs" % ((time()-tStart)*1e6))

        self.theParent.statusBar.setCharCount(self.charCount)
        self.theParent.statusBar.setWordCount(self.wordCount)

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

    def _docChange(self, thePos, charsRemoved, charsAdded):

        tStart = time()

        self.charCount = self.theDoc.characterCount()
        self.lineCount = self.theDoc.lineCount()
        self.theParent.statusBar.setCharCount(self.charCount)

        currBlock = self.theDoc.findBlock(thePos)
        self._countWords(currBlock)
        self.wordCount = sum(self.blockWords.values())
        self.theParent.statusBar.setWordCount(self.wordCount)

        if self.mainConf.doReplace:
            self._docAutoReplace(currBlock)

        logger.verbose("Doc change signal took %.3f µs" % ((time()-tStart)*1e6))

        return

    def _docAutoReplace(self, theBlock):

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

        if self.mainConf.doReplaceQuote and theOne == "\"":
            qOpen  = self.mainConf.replaceQuotes[0]
            qClose = self.mainConf.replaceQuotes[1]
            nOpen  = theText.count(qOpen)
            nClose = theText.count(qClose)
            if nOpen > nClose:
                self.guiEditor.textCursor().deletePreviousChar()
                self.guiEditor.textCursor().insertText(qClose)
            else:
                self.guiEditor.textCursor().deletePreviousChar()
                self.guiEditor.textCursor().insertText(qOpen)

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

    def _countWords(self, theBlock):
        """Count the number of words in a given block, but only if it's a text block. I.e. we skip
        blocks starting with @ and %, and we also skip the ### in titles. Dashes are replaced with
        spaces before the count to ensure, for instance, 'word1—word2' is counted as two words.
        """

        if not theBlock.isValid():
            return

        theText = theBlock.text()
        theLen  = len(theText)
        self.blockWords[theBlock.blockNumber()] = 0

        if theLen == 0:
            return 0
        if theText[0] == "@" or theText[0] == "%":
            return 0
        if theText[0] == "#":
            nWords = -1
        else:
            nWords = 0

        theBuff = theText.replace("–"," ").replace("—"," ")
        nWords += len(theBuff.split())

        self.blockWords[theBlock.blockNumber()] = nWords

        return nWords

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
