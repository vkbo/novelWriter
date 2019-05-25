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

from PyQt5.QtCore import QRegularExpression
from PyQt5.QtGui  import QColor, QTextCharFormat, QFont, QSyntaxHighlighter

logger = logging.getLogger(__name__)

class GuiDocHighlighter(QSyntaxHighlighter):

    def __init__(self, theDoc, theTheme):
        QSyntaxHighlighter.__init__(self, theDoc)

        logger.debug("Initialising DocHighlighter ...")
        self.mainConf   = nw.CONFIG
        self.theDoc     = theDoc
        self.theTheme   = theTheme
        self.theDict    = None
        self.spellCheck = False
        self.hRules     = []

        self.colHead    = QColor(*self.theTheme.colHead)
        self.colHeadH   = QColor(*self.theTheme.colHeadH)
        self.colEmph    = QColor(*self.theTheme.colEmph)
        self.colDialN   = QColor(*self.theTheme.colDialN)
        self.colDialD   = QColor(*self.theTheme.colDialD)
        self.colDialS   = QColor(*self.theTheme.colDialS)
        self.colComm    = QColor(*self.theTheme.colComm)
        self.colKey     = QColor(*self.theTheme.colKey)
        self.colVal     = QColor(*self.theTheme.colVal)
        self.colSpell   = QColor(*self.theTheme.colSpell)

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
            "dialogue1" : self._makeFormat(self.colDialN),
            "dialogue2" : self._makeFormat(self.colDialD),
            "dialogue3" : self._makeFormat(self.colDialS),
            "hidden"    : self._makeFormat(self.colComm),
            "keyword"   : self._makeFormat(self.colKey),
            "value"     : self._makeFormat(self.colVal),
        }

        # Headers
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
        self.hRules.append((
            r"^(@.+?)\s*:\s*(.+?)$", {
                1 : self.hStyles["keyword"],
                2 : self.hStyles["value"],
            }
        ))

        # Comments
        self.hRules.append((
            r"^%.*$", {
                0 : self.hStyles["hidden"],
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

        # Build a QRegExp for each pattern and for the spell checker
        self.rules   = [(QRegularExpression(a),b) for (a,b) in self.hRules]
        self.spellRx = QRegularExpression(r"\b[^\s]+\b")

        logger.debug("DocHighlighter initialisation complete")

        return

    def setDict(self, theDict):
        self.theDict = theDict
        return True

    def setSpellCheck(self, theMode):
        self.spellCheck = theMode
        return True

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

        if fmtSize is not None:
            theFormat.setFontPointSize(round(fmtSize*self.mainConf.textSize))

        return theFormat

    def highlightBlock(self, theText):

        for rX, xFmt in self.rules:
            rxItt = rX.globalMatch(theText, 0)
            while rxItt.hasNext():
                rxMatch = rxItt.next()
                for xM in xFmt.keys():
                    xPos = rxMatch.capturedStart(xM)
                    xLen = rxMatch.capturedLength(xM)
                    self.setFormat(xPos, xLen, xFmt[xM])

        self.setCurrentBlockState(0)

        if self.theDict is None or not self.spellCheck or theText.startswith("@"):
            return

        rxSpell = self.spellRx.globalMatch(theText.replace("_"," "), 0)
        while rxSpell.hasNext():
            rxMatch = rxSpell.next()
            if not self.theDict.check(rxMatch.captured(0)):
                if rxMatch.captured(0) == rxMatch.captured(0).upper(): continue
                xPos = rxMatch.capturedStart(0)
                xLen = rxMatch.capturedLength(0)
                spFmt = self.format(xPos)
                spFmt.setUnderlineColor(self.colSpell)
                spFmt.setUnderlineStyle(QTextCharFormat.SpellCheckUnderline)
                self.setFormat(xPos, xLen, spFmt)

        return

# END Class DocHighlighter
