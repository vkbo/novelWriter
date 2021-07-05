"""
novelWriter – GUI Syntax Highlighter
====================================
Class for the main document editor syntax highlighter

File History:
Created: 2019-04-06 [0.0.1]

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

from PyQt5.QtCore import Qt, QRegularExpression
from PyQt5.QtGui import (
    QColor, QTextCharFormat, QFont, QSyntaxHighlighter, QBrush
)

from nw.constants import nwRegEx, nwUnicode

logger = logging.getLogger(__name__)


class GuiDocHighlighter(QSyntaxHighlighter):

    BLOCK_NONE  = 0
    BLOCK_TEXT  = 1
    BLOCK_META  = 2
    BLOCK_TITLE = 4

    def __init__(self, theDoc, theParent):
        QSyntaxHighlighter.__init__(self, theDoc)

        logger.debug("Initialising GuiDocHighlighter ...")
        self.mainConf   = nw.CONFIG
        self.theDoc     = theDoc
        self.theParent  = theParent
        self.theTheme   = theParent.theTheme
        self.theIndex   = theParent.theIndex
        self.theDict    = None
        self.theHandle  = None
        self.spellCheck = False
        self.spellRx    = None
        self.hRules     = []
        self.hStyles    = {}

        self.colHead   = QColor(0, 0, 0)
        self.colHeadH  = QColor(0, 0, 0)
        self.colEmph   = QColor(0, 0, 0)
        self.colDialN  = QColor(0, 0, 0)
        self.colDialD  = QColor(0, 0, 0)
        self.colDialS  = QColor(0, 0, 0)
        self.colHidden = QColor(0, 0, 0)
        self.colKey    = QColor(0, 0, 0)
        self.colVal    = QColor(0, 0, 0)
        self.colSpell  = QColor(0, 0, 0)
        self.colError  = QColor(0, 0, 0)
        self.colRepTag = QColor(0, 0, 0)

        self.initHighlighter()

        logger.debug("GuiDocHighlighter initialisation complete")

        return

    def initHighlighter(self):
        """Initialise the syntax highlighter, setting all the colour
        rules and building the regexes.
        """
        logger.debug("Setting up highlighting rules")

        self.colHead   = QColor(*self.theTheme.colHead)
        self.colHeadH  = QColor(*self.theTheme.colHeadH)
        self.colDialN  = QColor(*self.theTheme.colDialN)
        self.colDialD  = QColor(*self.theTheme.colDialD)
        self.colDialS  = QColor(*self.theTheme.colDialS)
        self.colHidden = QColor(*self.theTheme.colHidden)
        self.colKey    = QColor(*self.theTheme.colKey)
        self.colVal    = QColor(*self.theTheme.colVal)
        self.colSpell  = QColor(*self.theTheme.colSpell)
        self.colError  = QColor(*self.theTheme.colError)
        self.colRepTag = QColor(*self.theTheme.colRepTag)
        self.colMod    = QColor(*self.theTheme.colMod)
        self.colBreak  = QColor(*self.theTheme.colEmph)
        self.colBreak.setAlpha(64)

        self.colEmph = None
        if self.mainConf.highlightEmph:
            self.colEmph = QColor(*self.theTheme.colEmph)

        self.hStyles = {
            "header1":   self._makeFormat(self.colHead, "bold", 1.8),
            "header2":   self._makeFormat(self.colHead, "bold", 1.6),
            "header3":   self._makeFormat(self.colHead, "bold", 1.4),
            "header4":   self._makeFormat(self.colHead, "bold", 1.2),
            "header1h":  self._makeFormat(self.colHeadH, "bold", 1.8),
            "header2h":  self._makeFormat(self.colHeadH, "bold", 1.6),
            "header3h":  self._makeFormat(self.colHeadH, "bold", 1.4),
            "header4h":  self._makeFormat(self.colHeadH, "bold", 1.2),
            "bold":      self._makeFormat(self.colEmph, "bold"),
            "italic":    self._makeFormat(self.colEmph, "italic"),
            "strike":    self._makeFormat(self.colHidden, "strike"),
            "mspaces":   self._makeFormat(self.colError, "errline"),
            "nobreak":   self._makeFormat(self.colBreak, "background"),
            "dialogue1": self._makeFormat(self.colDialN),
            "dialogue2": self._makeFormat(self.colDialD),
            "dialogue3": self._makeFormat(self.colDialS),
            "replace":   self._makeFormat(self.colRepTag),
            "hidden":    self._makeFormat(self.colHidden),
            "keyword":   self._makeFormat(self.colKey),
            "modifier":  self._makeFormat(self.colMod),
            "value":     self._makeFormat(self.colVal, "underline"),
        }

        self.hRules = []

        # Multiple or Trailing Spaces
        if self.mainConf.showMultiSpaces:
            self.hRules.append((
                r"[ ]{2,}|[ ]*$", {
                    0: self.hStyles["mspaces"],
                }
            ))

        # Non-Breaking Spaces
        self.hRules.append((
            "[%s%s]+" % (nwUnicode.U_NBSP, nwUnicode.U_THNBSP), {
                0: self.hStyles["nobreak"],
            }
        ))

        # Quoted Strings
        if self.mainConf.highlightQuotes:
            fmtDbl = self.mainConf.fmtDoubleQuotes
            fmtSng = self.mainConf.fmtSingleQuotes

            # Straight Quotes
            if fmtDbl != ["\"", "\""]:
                self.hRules.append((
                    "(\\B\")(.*?)(\"\\B)", {
                        0: self.hStyles["dialogue1"],
                    }
                ))

            # Double Quotes
            dblEnd = "|$" if self.mainConf.allowOpenDQuote else ""
            self.hRules.append((
                f"(\\B{fmtDbl[0]})(.*?)({fmtDbl[1]}\\B{dblEnd})", {
                    0: self.hStyles["dialogue2"],
                }
            ))

            # Single Quotes
            sngEnd = "|$" if self.mainConf.allowOpenSQuote else ""
            self.hRules.append((
                f"(\\B{fmtSng[0]})(.*?)({fmtSng[1]}\\B{sngEnd})", {
                    0: self.hStyles["dialogue3"],
                }
            ))

        # Markdown Syntax
        self.hRules.append((
            nwRegEx.FMT_EI, {
                1: self.hStyles["hidden"],
                2: self.hStyles["italic"],
                3: self.hStyles["hidden"],
            }
        ))
        self.hRules.append((
            nwRegEx.FMT_EB, {
                1: self.hStyles["hidden"],
                2: self.hStyles["bold"],
                3: self.hStyles["hidden"],
            }
        ))
        self.hRules.append((
            nwRegEx.FMT_ST, {
                1: self.hStyles["hidden"],
                2: self.hStyles["strike"],
                3: self.hStyles["hidden"],
            }
        ))

        # Alignment Tags
        self.hRules.append((
            r"(^>{1,2}|<{1,2}$)", {
                1: self.hStyles["hidden"],
            }
        ))

        # Auto-Replace Tags
        self.hRules.append((
            r"<(\S+?)>", {
                0: self.hStyles["replace"],
            }
        ))

        # Build a QRegExp for each highlight pattern
        self.rxRules = []
        for regEx, regRules in self.hRules:
            hReg = QRegularExpression(regEx)
            hReg.setPatternOptions(QRegularExpression.UseUnicodePropertiesOption)
            self.rxRules.append((hReg, regRules))

        # Build a QRegExp for spell checker
        # Include additional characters that the highlighter should
        # consider to be word separators
        wordSep  = r"\-_\+/"
        wordSep += nwUnicode.U_ENDASH
        wordSep += nwUnicode.U_EMDASH
        self.spellRx = QRegularExpression(r"\b[^\s"+wordSep+r"]+\b")
        self.spellRx.setPatternOptions(QRegularExpression.UseUnicodePropertiesOption)

        return True

    ##
    #  Setters
    ##

    def setDict(self, theDict):
        """Set the dictionary object for spell check underlines lookup.
        """
        self.theDict = theDict
        return True

    def setSpellCheck(self, theMode):
        """Enable/disable the real time spell checker.
        """
        self.spellCheck = theMode
        return True

    def setHandle(self, theHandle):
        """Set the handle of the currently highlighted document. This is
        needed for the index lookup for validating tags and references.
        """
        self.theHandle = theHandle
        return True

    ##
    #  Methods
    ##

    def rehighlightByType(self, theType):
        """Loop through all blocks and rehighlight those of a given
        content type.
        """
        qDoc = self.document()
        nBlocks = qDoc.blockCount()
        bfTime = time()
        for i in range(nBlocks):
            theBlock = qDoc.findBlockByNumber(i)
            if theBlock.userState() & theType > 0:
                self.rehighlightBlock(theBlock)
        afTime = time()
        logger.debug(
            "Document highlighted in %.3f ms" % (1000*(afTime-bfTime))
        )
        return

    ##
    #  Highlight Block
    ##

    def highlightBlock(self, theText):
        """Highlight a single block. Prefer to check first character for
        all formats that are defined by their initial characters. This
        is significantly faster than running the regex checks used for
        text paragraphs.
        """
        self.setCurrentBlockState(self.BLOCK_NONE)
        if self.theHandle is None or not theText:
            return

        if theText.startswith("@"):  # Keywords and commands
            self.setCurrentBlockState(self.BLOCK_META)
            tItem = self.theParent.theProject.projTree[self.theHandle]
            isValid, theBits, thePos = self.theIndex.scanThis(theText)
            isGood = self.theIndex.checkThese(theBits, tItem)
            if isValid:
                for n, theBit in enumerate(theBits):
                    xPos = thePos[n]
                    xLen = len(theBit)
                    if isGood[n]:
                        if n == 0:
                            self.setFormat(xPos, xLen, self.hStyles["keyword"])
                        else:
                            self.setFormat(xPos, xLen, self.hStyles["value"])
                    else:
                        kwFmt = self.format(xPos)
                        kwFmt.setUnderlineColor(self.colError)
                        kwFmt.setUnderlineStyle(QTextCharFormat.SpellCheckUnderline)
                        self.setFormat(xPos, xLen, kwFmt)

            # We never want to run the spell checker on keyword/values,
            # so we force a return here
            return

        elif theText.startswith("# "):  # Header 1
            self.setCurrentBlockState(self.BLOCK_TITLE)
            self.setFormat(0, 1, self.hStyles["header1h"])
            self.setFormat(1, len(theText), self.hStyles["header1"])

        elif theText.startswith("## "):  # Header 2
            self.setCurrentBlockState(self.BLOCK_TITLE)
            self.setFormat(0, 2, self.hStyles["header2h"])
            self.setFormat(2, len(theText), self.hStyles["header2"])

        elif theText.startswith("### "):  # Header 3
            self.setCurrentBlockState(self.BLOCK_TITLE)
            self.setFormat(0, 3, self.hStyles["header3h"])
            self.setFormat(3, len(theText), self.hStyles["header3"])

        elif theText.startswith("#### "):  # Header 4
            self.setCurrentBlockState(self.BLOCK_TITLE)
            self.setFormat(0, 4, self.hStyles["header4h"])
            self.setFormat(4, len(theText), self.hStyles["header4"])

        elif theText.startswith("%"):  # Comments
            self.setCurrentBlockState(self.BLOCK_TEXT)
            toCheck = theText[1:].lstrip()
            synTag  = toCheck[:9].lower()
            tLen = len(theText)
            cLen = len(toCheck)
            cOff = tLen - cLen
            if synTag == "synopsis:":
                self.setFormat(0, cOff+9, self.hStyles["modifier"])
                self.setFormat(cOff+9, tLen, self.hStyles["hidden"])
            else:
                self.setFormat(0, tLen, self.hStyles["hidden"])

        else:  # Text Paragraph
            self.setCurrentBlockState(self.BLOCK_TEXT)
            for rX, xFmt in self.rxRules:
                rxItt = rX.globalMatch(theText, 0)
                while rxItt.hasNext():
                    rxMatch = rxItt.next()
                    for xM in xFmt:
                        xPos = rxMatch.capturedStart(xM)
                        xLen = rxMatch.capturedLength(xM)
                        for x in range(xPos, xPos+xLen):
                            spFmt = self.format(x)
                            if spFmt != self.hStyles["hidden"]:
                                spFmt.merge(xFmt[xM])
                                self.setFormat(x, 1, spFmt)

        if self.theDict is None or not self.spellCheck:
            return

        rxSpell = self.spellRx.globalMatch(theText, 0)
        while rxSpell.hasNext():
            rxMatch = rxSpell.next()
            if not self.theDict.checkWord(rxMatch.captured(0)):
                if rxMatch.captured(0).isupper() or rxMatch.captured(0).isnumeric():
                    continue
                xPos = rxMatch.capturedStart(0)
                xLen = rxMatch.capturedLength(0)
                for x in range(xPos, xPos+xLen):
                    spFmt = self.format(x)
                    spFmt.setUnderlineColor(self.colSpell)
                    spFmt.setUnderlineStyle(QTextCharFormat.SpellCheckUnderline)
                    self.setFormat(x, 1, spFmt)

        return

    ##
    #  Internal Functions
    ##

    def _makeFormat(self, fmtCol=None, fmtStyle=None, fmtSize=None):
        """Generate a valid character format to be applied to the text
        that is to be highlighted.
        """
        theFormat = QTextCharFormat()

        if fmtCol is not None:
            theFormat.setForeground(fmtCol)

        if fmtStyle is not None:
            if "bold" in fmtStyle:
                theFormat.setFontWeight(QFont.Bold)
            if "italic" in fmtStyle:
                theFormat.setFontItalic(True)
            if "strike" in fmtStyle:
                theFormat.setFontStrikeOut(True)
            if "errline" in fmtStyle:
                theFormat.setUnderlineColor(self.colError)
                theFormat.setUnderlineStyle(QTextCharFormat.SpellCheckUnderline)
            if "underline" in fmtStyle:
                theFormat.setFontUnderline(True)
            if "background" in fmtStyle:
                theFormat.setBackground(QBrush(fmtCol, Qt.SolidPattern))

        if fmtSize is not None:
            theFormat.setFontPointSize(int(round(fmtSize*self.mainConf.textSize)))

        return theFormat

# END Class DocHighlighter
