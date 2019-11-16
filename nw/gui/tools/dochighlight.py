# -*- coding: utf-8 -*-
"""novelWriter GUI Document Highlighter

 novelWriter – GUI Document Highlighter
========================================
 Syntax highlighting for MarkDown

 File History:
 Created: 2019-04-06 [0.0.1]

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
        self.colTrail  = QColor(*self.theTheme.colEmph,64)

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
            "value"     : self._makeFormat(self.colVal),
        }

        # Headers
        self.hRules = []
        self.hRules.append((
            r"^(#{1}) (.*)[^\n]", {
                0 : self.hStyles["header1"],
                1 : self.hStyles["header1h"],
            }
        ))
        self.hRules.append((
            r"^(#{2}) (.*)[^\n]", {
                0 : self.hStyles["header2"],
                1 : self.hStyles["header2h"],
            }
        ))
        self.hRules.append((
            r"^(#{3}) (.*)[^\n]", {
                0 : self.hStyles["header3"],
                1 : self.hStyles["header3h"],
            }
        ))
        self.hRules.append((
            r"^(#{4}) (.*)[^\n]", {
                0 : self.hStyles["header4"],
                1 : self.hStyles["header4h"],
            }
        ))

        # Keyword/Value
        # self.hRules.append((
        #     r"^(@.+?)\s*:\s*(.+?)$", {
        #         1 : self.hStyles["keyword"],
        #         2 : self.hStyles["value"],
        #     }
        # ))

        # Comments
        self.hRules.append((
            r"^%.*$", {
                0 : self.hStyles["hidden"],
            }
        ))

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
        self.theDict = theDict
        return True

    def setSpellCheck(self, theMode):
        self.spellCheck = theMode
        return True

    def setHandle(self, theHandle):
        self.theHandle = theHandle
        return True

    ##
    #  Highlight Block
    ##

    def highlightBlock(self, theText):

        if self.theHandle is None:
            return

        if theText.startswith("@"):
            # Highlighting of keywords and commands
            tItem = self.theParent.theProject.getItem(self.theHandle)
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

            # We're done, no need to continue
            return

        else:
            # For other text, just use our regex rules
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
