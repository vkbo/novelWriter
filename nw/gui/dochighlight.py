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

    def __init__(self, theDoc):
        QSyntaxHighlighter.__init__(self, theDoc)

        logger.debug("Initialising DocHighlighter ...")
        self.mainConf = nw.CONFIG
        self.theDoc   = theDoc

        self.colHead = (  0,155,200,255)
        self.colEmph = (200,120,  0,255)
        self.colDial = (184,200,  0,255)
        self.colComm = (120,120,120,255)
        self.colKey  = (200,  0,  0,255)
        self.colVal  = (184,200,  0,255)

        self.hStyles = {
            "header1"   : self._makeFormat(self.colHead,"bold",20),
            "header2"   : self._makeFormat(self.colHead,"bold",18),
            "header3"   : self._makeFormat(self.colHead,"bold",16),
            "header4"   : self._makeFormat(self.colHead,"bold",14),
            "bold"      : self._makeFormat(self.colEmph,"bold"),
            "italic"    : self._makeFormat(self.colEmph,"italic"),
            "strike"    : self._makeFormat(self.colEmph,"strike"),
            "underline" : self._makeFormat(self.colEmph,"underline"),
            "dialogue"  : self._makeFormat(self.colDial),
            "hidden"    : self._makeFormat(self.colComm),
            "keyword"   : self._makeFormat(self.colKey),
            "value"     : self._makeFormat(self.colVal),
        }

        self.hRules = [
            (r"^#{1}[^#].*[^\n]",     0, self.hStyles["header1"]),
            (r"^#{2}[^#].*[^\n]",     0, self.hStyles["header2"]),
            (r"^#{3}[^#].*[^\n]",     0, self.hStyles["header3"]),
            (r"^#{4}[^#].*[^\n]",     0, self.hStyles["header4"]),
            (r"\*{2}(.+?)\*{2}",      0, self.hStyles["bold"]),
            (r"\/{2}(.+?)\/{2}",      0, self.hStyles["italic"]),
            (r"~{2}(.+?)~{2}",        0, self.hStyles["strike"]),
            (r"_{2}(.+?)_{2}",        0, self.hStyles["underline"]),
            (r'"(.+?)"',              0, self.hStyles["dialogue"]),
            (r"«(.+?)»",              0, self.hStyles["dialogue"]),
            (r"“(.+?)”",              0, self.hStyles["dialogue"]),
            (r"^(@.+?)\s*:\s*(.+?)$", 1, self.hStyles["keyword"]),
            (r"^(@.+?)\s*:\s*(.+?)$", 2, self.hStyles["value"]),
            (r"^%.*$",                0, self.hStyles["hidden"]),
        ]

        # Build a QRegExp for each pattern
        self.rules = [(QRegularExpression(a),b,c) for (a,b,c) in self.hRules]

        logger.debug("DocHighlighter initialisation complete")

        return

    def _makeFormat(self, fmtCol=None, fmtStyle=None, fmtSize=None):
        theFormat = QTextCharFormat()

        if fmtCol is not None:
            theCol = QColor()
            if isinstance(fmtCol,str):
                theCol.setNamedColor(fmtCol)
            else:
                theCol.setRgb(*fmtCol)
            theFormat.setForeground(theCol)

        if fmtStyle is not None:
            if "bold" in fmtStyle:
                theFormat.setFontWeight(QFont.Bold)
            if "italic" in fmtStyle:
                theFormat.setFontItalic(True)
            if "strike" in fmtStyle:
                theFormat.setFontStrikeOut(True)
            if "underline" in fmtStyle:
                theFormat.setFontUnderline(True)

        if isinstance(fmtSize,int):
            theFormat.setFontPointSize(fmtSize)

        return theFormat

    def highlightBlock(self, theText):
        for rX, nth, fmt in self.rules:
            rxItt = rX.globalMatch(theText, 0)
            while rxItt.hasNext():
                rxMatch = rxItt.next()
                xPos = rxMatch.capturedStart(nth)
                xLen = rxMatch.capturedLength(nth)
                # logger.verbose("Captured[%d]: '%s'" % (nth,rxMatch.captured(nth)))
                # print(rxMatch.capturedTexts())
                self.setFormat(xPos, xLen, fmt)

        self.setCurrentBlockState(0)

# END Class DocHighlighter
