# -*- coding: utf-8 -*-
"""novelWriter GUI Document Highlighter

 novelWriter – GUI Document Highlighter
========================================
 Syntax highlighting for MarkDown

 File History:
 Created: 2019-04-06 [0.0.1]

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

from PyQt5.QtCore import Qt, QRegularExpression
from PyQt5.QtGui import (
    QColor, QTextCharFormat, QFont, QSyntaxHighlighter, QBrush
)

from nw.constants import nwUnicode

logger = logging.getLogger(__name__)

class GuiDocHighlighter(QSyntaxHighlighter):

    def __init__(self, theDoc, theParent):
        QSyntaxHighlighter.__init__(self, theDoc)

        logger.debug("Initialising DocHighlighter ...")
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

        self.colHead   = QColor(0,0,0)
        self.colHeadH  = QColor(0,0,0)
        self.colEmph   = QColor(0,0,0)
        self.colDialN  = QColor(0,0,0)
        self.colDialD  = QColor(0,0,0)
        self.colDialS  = QColor(0,0,0)
        self.colComm   = QColor(0,0,0)
        self.colKey    = QColor(0,0,0)
        self.colVal    = QColor(0,0,0)
        self.colSpell  = QColor(0,0,0)
        self.colTagErr = QColor(0,0,0)
        self.colRepTag = QColor(0,0,0)

        self.initHighlighter()

        logger.debug("DocHighlighter initialisation complete")

        return

    def initHighlighter(self):
        """Initialise the syntax highlighter, setting all the colour
        rules and building the regexes.
        """

        logger.debug("Setting up highlighting rules")

        self.colHead   = QColor(*self.theTheme.colHead)
        self.colHeadH  = QColor(*self.theTheme.colHeadH)
        self.colEmph   = QColor(*self.theTheme.colEmph)
        self.colDialN  = QColor(*self.theTheme.colDialN)
        self.colDialD  = QColor(*self.theTheme.colDialD)
        self.colDialS  = QColor(*self.theTheme.colDialS)
        self.colComm   = QColor(*self.theTheme.colComm)
        self.colKey    = QColor(*self.theTheme.colKey)
        self.colVal    = QColor(*self.theTheme.colVal)
        self.colSpell  = QColor(*self.theTheme.colSpell)
        self.colTagErr = QColor(*self.theTheme.colTagErr)
        self.colRepTag = QColor(*self.theTheme.colRepTag)
        self.colMod    = QColor(*self.theTheme.colMod)
        self.colTrail  = QColor(*self.theTheme.colEmph)
        self.colTrail.setAlpha(64)

        self.hStyles = {
            "header1"   : self._makeFormat(self.colHead, "bold",1.8),
            "header2"   : self._makeFormat(self.colHead, "bold",1.6),
            "header3"   : self._makeFormat(self.colHead, "bold",1.4),
            "header4"   : self._makeFormat(self.colHead, "bold",1.2),
            "header1h"  : self._makeFormat(self.colHeadH,"bold",1.8),
            "header2h"  : self._makeFormat(self.colHeadH,"bold",1.6),
            "header3h"  : self._makeFormat(self.colHeadH,"bold",1.4),
            "header4h"  : self._makeFormat(self.colHeadH,"bold",1.2),
            "bold"      : self._makeFormat(self.colEmph, "bold"),
            "italic"    : self._makeFormat(self.colEmph, "italic"),
            "strike"    : self._makeFormat(self.colEmph, "strike"),
            "underline" : self._makeFormat(self.colEmph, "underline"),
            "trailing"  : self._makeFormat(self.colTrail,"background"),
            "nobreak"   : self._makeFormat(self.colTrail,"background"),
            "dialogue1" : self._makeFormat(self.colDialN),
            "dialogue2" : self._makeFormat(self.colDialD),
            "dialogue3" : self._makeFormat(self.colDialS),
            "replace"   : self._makeFormat(self.colRepTag),
            "hidden"    : self._makeFormat(self.colComm),
            "keyword"   : self._makeFormat(self.colKey),
            "modifier"  : self._makeFormat(self.colMod),
            "value"     : self._makeFormat(self.colVal),
        }

        self.hRules = []

        # Trailing Spaces, 2+
        self.hRules.append((
            r"[ ]{2,}$", {
                0 : self.hStyles["trailing"],
            }
        ))

        # Non-breaking Space
        self.hRules.append((
            "[%s]+" % nwUnicode.U_NBSP, {
                0 : self.hStyles["nobreak"],
            }
        ))

        # Markdown
        self.hRules.append((
            r"(?<![\w|\\])([\*]{2})(?!\s)(?m:(.+?))(?<![\s|\\])(\1)(?!\w)", {
                1 : self.hStyles["hidden"],
                2 : self.hStyles["bold"],
                3 : self.hStyles["hidden"],
            }
        ))
        self.hRules.append((
            r"(?<![\w|_|\\])([_])(?!\s|\1)(?m:(.+?))(?<![\s|\\])(\1)(?!\w)", {
                1 : self.hStyles["hidden"],
                2 : self.hStyles["italic"],
                3 : self.hStyles["hidden"],
            }
        ))
        self.hRules.append((
            r"(?<![\w|\\])([_]{2})(?!\s)(?m:(.+?))(?<![\s|\\])(\1)(?!\w)", {
                1 : self.hStyles["hidden"],
                2 : self.hStyles["underline"],
                3 : self.hStyles["hidden"],
            }
        ))

        # Quoted Strings
        if self.mainConf.highlightQuotes:
            self.hRules.append((
                "{:s}(.+?){:s}".format('"','"'), {
                    0 : self.hStyles["dialogue1"],
                }
            ))
            self.hRules.append((
                "{:s}(.+?){:s}".format(*self.mainConf.fmtDoubleQuotes), {
                    0 : self.hStyles["dialogue2"],
                }
            ))
            self.hRules.append((
                "{:s}(.+?){:s}".format(*self.mainConf.fmtSingleQuotes), {
                    0 : self.hStyles["dialogue3"],
                }
            ))

        # Auto-Replace Tags
        self.hRules.append((
            r"<(\S+?)>", {
                0 : self.hStyles["replace"],
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
        wordSep  = "_+"
        wordSep += nwUnicode.U_EMDASH
        self.spellRx = QRegularExpression("\\b[^\\s%s]+\\b" % wordSep)
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
    #  Highlight Block
    ##

    def highlightBlock(self, theText):
        """Highlight a single block. Prefer to check first character for
        all formats that are defined by their initial characters. This
        is significantly faster than running the regex checks we use for
        text paragraphs.
        """
        if self.theHandle is None or not theText:
            return

        if theText.startswith("@"): # Keywords and commands
            tItem = self.theParent.theProject.projTree[self.theHandle]
            isValid, theBits, thePos = self.theIndex.scanThis(theText)
            isGood = self.theIndex.checkThese(theBits, tItem)
            if isValid:
                for n in range(len(theBits)):
                    xPos = thePos[n]
                    xLen = len(theBits[n])
                    if isGood[n]:
                        if n == 0:
                            self.setFormat(xPos, xLen, self.hStyles["keyword"])
                        else:
                            self.setFormat(xPos, xLen, self.hStyles["value"])
                    else:
                        kwFmt = self.format(xPos)
                        kwFmt.setUnderlineColor(self.colTagErr)
                        kwFmt.setUnderlineStyle(QTextCharFormat.SpellCheckUnderline)
                        self.setFormat(xPos, xLen, kwFmt)

            # We never want to run the spell checker on keyword/values,
            # so we force a return here
            return

        elif theText.startswith("# "): # Header 1
            self.setFormat(0, 1, self.hStyles["header1h"])
            self.setFormat(1, len(theText), self.hStyles["header1"])

        elif theText.startswith("## "): # Header 2
            self.setFormat(0, 2, self.hStyles["header2h"])
            self.setFormat(2, len(theText), self.hStyles["header2"])

        elif theText.startswith("### "): # Header 3
            self.setFormat(0, 3, self.hStyles["header3h"])
            self.setFormat(3, len(theText), self.hStyles["header3"])

        elif theText.startswith("#### "): # Header 4
            self.setFormat(0, 4, self.hStyles["header4h"])
            self.setFormat(4, len(theText), self.hStyles["header4"])

        elif theText.startswith("%"): # Comments
            toCheck = theText[1:].lstrip().lower()
            tLen = len(theText)
            cLen = len(toCheck)
            cOff = tLen - cLen
            if toCheck.startswith("synopsis:"):
                self.setFormat(0, cOff+9, self.hStyles["modifier"])
                self.setFormat(cOff+9, tLen, self.hStyles["hidden"])
            else:
                self.setFormat(0, tLen, self.hStyles["hidden"])

        else: # Text Paragraph
            for rX, xFmt in self.rxRules:
                rxItt = rX.globalMatch(theText, 0)
                while rxItt.hasNext():
                    rxMatch = rxItt.next()
                    for xM in xFmt.keys():
                        xPos = rxMatch.capturedStart(xM)
                        xLen = rxMatch.capturedLength(xM)
                        self.setFormat(xPos, xLen, xFmt[xM])

        if self.theDict is None or not self.spellCheck:
            return

        rxSpell = self.spellRx.globalMatch(theText, 0)
        while rxSpell.hasNext():
            rxMatch = rxSpell.next()
            if not self.theDict.checkWord(rxMatch.captured(0)):
                if rxMatch.captured(0) == rxMatch.captured(0).upper():
                    continue
                xPos = rxMatch.capturedStart(0)
                xLen = rxMatch.capturedLength(0)
                for x in range(xLen):
                    spFmt = self.format(xPos+x)
                    spFmt.setUnderlineColor(self.colSpell)
                    spFmt.setUnderlineStyle(QTextCharFormat.SpellCheckUnderline)
                    self.setFormat(xPos+x, 1, spFmt)

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
            if "underline" in fmtStyle:
                theFormat.setFontUnderline(True)
            if "background" in fmtStyle:
                theFormat.setBackground(QBrush(fmtCol,Qt.SolidPattern))

        if fmtSize is not None:
            theFormat.setFontPointSize(round(fmtSize*self.mainConf.textSize))

        return theFormat

# END Class DocHighlighter
