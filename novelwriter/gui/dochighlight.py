"""
novelWriter – GUI Syntax Highlighter
====================================

File History:
Created: 2019-04-06 [0.0.1] GuiDocHighlighter
Created: 2023-09-10 [2.2b1] TextBlockData

This file is a part of novelWriter
Copyright 2018–2024, Veronica Berglyd Olsen

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
from __future__ import annotations

import logging

from time import time

from PyQt5.QtCore import Qt, QRegularExpression
from PyQt5.QtGui import (
    QBrush, QColor, QFont, QSyntaxHighlighter, QTextBlockUserData,
    QTextCharFormat, QTextDocument
)

from novelwriter import CONFIG, SHARED
from novelwriter.enum import nwComment
from novelwriter.common import checkInt
from novelwriter.constants import nwRegEx, nwUnicode
from novelwriter.core.index import processComment

logger = logging.getLogger(__name__)

SPELLRX = QRegularExpression(r"\b[^\s\-\+\/–—\[\]:]+\b")
SPELLRX.setPatternOptions(QRegularExpression.UseUnicodePropertiesOption)


class GuiDocHighlighter(QSyntaxHighlighter):

    __slots__ = ("_tItem", "_tHandle", "_spellCheck", "_spellErr", "_hRules", "_hStyles")

    BLOCK_NONE  = 0
    BLOCK_TEXT  = 1
    BLOCK_META  = 2
    BLOCK_TITLE = 4

    def __init__(self, document: QTextDocument) -> None:
        super().__init__(document)

        logger.debug("Create: GuiDocHighlighter")

        self._tHandle = None
        self._isInactive = False
        self._spellCheck = False
        self._spellErr = QTextCharFormat()

        self._hRules: list[tuple[str, dict]] = []
        self._hStyles: dict[str, QTextCharFormat] = {}

        self.initHighlighter()

        logger.debug("Ready: GuiDocHighlighter")

        return

    def initHighlighter(self) -> None:
        """Initialise the syntax highlighter, setting all the colour
        rules and building the RegExes.
        """
        logger.debug("Setting up highlighting rules")

        colEmph = SHARED.theme.colEmph if CONFIG.highlightEmph else None
        colBreak = QColor(SHARED.theme.colEmph)
        colBreak.setAlpha(64)

        self._hRules = []
        self._hStyles = {
            "header1":   self._makeFormat(SHARED.theme.colHead, "bold", 1.8),
            "header2":   self._makeFormat(SHARED.theme.colHead, "bold", 1.6),
            "header3":   self._makeFormat(SHARED.theme.colHead, "bold", 1.4),
            "header4":   self._makeFormat(SHARED.theme.colHead, "bold", 1.2),
            "header1h":  self._makeFormat(SHARED.theme.colHeadH, "bold", 1.8),
            "header2h":  self._makeFormat(SHARED.theme.colHeadH, "bold", 1.6),
            "header3h":  self._makeFormat(SHARED.theme.colHeadH, "bold", 1.4),
            "header4h":  self._makeFormat(SHARED.theme.colHeadH, "bold", 1.2),
            "bold":      self._makeFormat(colEmph, "bold"),
            "italic":    self._makeFormat(colEmph, "italic"),
            "strike":    self._makeFormat(SHARED.theme.colHidden, "strike"),
            "mspaces":   self._makeFormat(SHARED.theme.colError, "errline"),
            "nobreak":   self._makeFormat(colBreak, "background"),
            "dialogue1": self._makeFormat(SHARED.theme.colDialN),
            "dialogue2": self._makeFormat(SHARED.theme.colDialD),
            "dialogue3": self._makeFormat(SHARED.theme.colDialS),
            "replace":   self._makeFormat(SHARED.theme.colRepTag),
            "hidden":    self._makeFormat(SHARED.theme.colHidden),
            "code":      self._makeFormat(SHARED.theme.colCode),
            "keyword":   self._makeFormat(SHARED.theme.colKey),
            "modifier":  self._makeFormat(SHARED.theme.colMod),
            "value":     self._makeFormat(SHARED.theme.colVal),
            "optional":  self._makeFormat(SHARED.theme.colOpt),
            "codevalue": self._makeFormat(SHARED.theme.colVal),
            "codeinval": self._makeFormat(None, "errline"),
        }

        # Cache Spell Error Format
        self._spellErr = QTextCharFormat()
        self._spellErr.setUnderlineColor(SHARED.theme.colSpell)
        self._spellErr.setUnderlineStyle(QTextCharFormat.SpellCheckUnderline)

        # Multiple or Trailing Spaces
        if CONFIG.showMultiSpaces:
            self._hRules.append((
                r"[ ]{2,}|[ ]*$", {
                    0: self._hStyles["mspaces"],
                }
            ))

        # Non-Breaking Spaces
        self._hRules.append((
            f"[{nwUnicode.U_NBSP}{nwUnicode.U_THNBSP}]+", {
                0: self._hStyles["nobreak"],
            }
        ))

        # Quoted Strings
        if CONFIG.highlightQuotes:
            fmtDblO = CONFIG.fmtDQuoteOpen
            fmtDblC = CONFIG.fmtDQuoteClose
            fmtSngO = CONFIG.fmtSQuoteOpen
            fmtSngC = CONFIG.fmtSQuoteClose

            # Straight Quotes
            if not (fmtDblO == fmtDblC == "\""):
                self._hRules.append((
                    "(\\B\")(.*?)(\"\\B)", {
                        0: self._hStyles["dialogue1"],
                    }
                ))

            # Double Quotes
            dblEnd = "|$" if CONFIG.allowOpenDQuote else ""
            self._hRules.append((
                f"(\\B{fmtDblO})(.*?)({fmtDblC}\\B{dblEnd})", {
                    0: self._hStyles["dialogue2"],
                }
            ))

            # Single Quotes
            sngEnd = "|$" if CONFIG.allowOpenSQuote else ""
            self._hRules.append((
                f"(\\B{fmtSngO})(.*?)({fmtSngC}\\B{sngEnd})", {
                    0: self._hStyles["dialogue3"],
                }
            ))

        # Markdown Syntax
        self._hRules.append((
            nwRegEx.FMT_EI, {
                1: self._hStyles["hidden"],
                2: self._hStyles["italic"],
                3: self._hStyles["hidden"],
            }
        ))
        self._hRules.append((
            nwRegEx.FMT_EB, {
                1: self._hStyles["hidden"],
                2: self._hStyles["bold"],
                3: self._hStyles["hidden"],
            }
        ))
        self._hRules.append((
            nwRegEx.FMT_ST, {
                1: self._hStyles["hidden"],
                2: self._hStyles["strike"],
                3: self._hStyles["hidden"],
            }
        ))

        # Shortcodes
        self._hRules.append((
            nwRegEx.FMT_SC, {
                1: self._hStyles["code"],
            }
        ))

        # Shortcodes w/Value
        self._hRules.append((
            nwRegEx.FMT_SV, {
                1: self._hStyles["code"],
                2: self._hStyles["codevalue"],
                3: self._hStyles["code"],
            }
        ))

        # Alignment Tags
        self._hRules.append((
            r"(^>{1,2}|<{1,2}$)", {
                1: self._hStyles["hidden"],
            }
        ))

        # Auto-Replace Tags
        self._hRules.append((
            r"<(\S+?)>", {
                0: self._hStyles["replace"],
            }
        ))

        # Build a QRegExp for each highlight pattern
        self.rxRules = []
        for regEx, regRules in self._hRules:
            hReg = QRegularExpression(regEx)
            hReg.setPatternOptions(QRegularExpression.UseUnicodePropertiesOption)
            self.rxRules.append((hReg, regRules))

        return

    ##
    #  Setters
    ##

    def setSpellCheck(self, state: bool) -> None:
        """Enable/disable the real time spell checker."""
        self._spellCheck = state
        return

    def setHandle(self, tHandle: str) -> None:
        """Set the handle of the currently highlighted document."""
        self._tHandle = tHandle
        self._isInactive = (
            item.isInactiveClass() if (item := SHARED.project.tree[tHandle]) else False
        )
        logger.debug("Syntax highlighter enabled for item '%s'", tHandle)
        return

    ##
    #  Methods
    ##

    def rehighlightByType(self, cType: int) -> None:
        """Loop through all blocks and re-highlight those of a given
        content type.
        """
        qDoc = self.document()
        nBlocks = qDoc.blockCount()
        tStart = time()
        for i in range(nBlocks):
            block = qDoc.findBlockByNumber(i)
            if block.userState() & cType > 0:
                self.rehighlightBlock(block)
        logger.debug("Document highlighted in %.3f ms" % (1000*(time() - tStart)))
        return

    ##
    #  Highlight Block
    ##

    def highlightBlock(self, text: str) -> None:
        """Highlight a single block. Prefer to check first character for
        all formats that are defined by their initial characters. This
        is significantly faster than running the regex checks used for
        text paragraphs.
        """
        self.setCurrentBlockState(self.BLOCK_NONE)
        if self._tHandle is None or not text:
            return

        if text.startswith("@"):  # Keywords and commands
            self.setCurrentBlockState(self.BLOCK_META)
            index = SHARED.project.index
            isValid, bits, pos = index.scanThis(text)
            isGood = index.checkThese(bits, self._tHandle)
            if isValid:
                for n, bit in enumerate(bits):
                    xPos = pos[n]
                    xLen = len(bit)
                    if n == 0 and isGood[n]:
                        self.setFormat(xPos, xLen, self._hStyles["keyword"])
                    elif isGood[n] and not self._isInactive:
                        one, two = index.parseValue(bit)
                        self.setFormat(xPos, len(one), self._hStyles["value"])
                        if two:
                            yPos = xPos + len(bit) - len(two)
                            self.setFormat(yPos, len(two), self._hStyles["optional"])
                    elif not self._isInactive:
                        self.setFormat(xPos, xLen, self._hStyles["codeinval"])

            # We never want to run the spell checker on keyword/values,
            # so we force a return here
            return

        elif text.startswith(("# ", "#! ", "## ", "##! ", "### ", "#### ")):
            self.setCurrentBlockState(self.BLOCK_TITLE)

            if text.startswith("# "):  # Header 1
                self.setFormat(0, 1, self._hStyles["header1h"])
                self.setFormat(1, len(text), self._hStyles["header1"])

            elif text.startswith("## "):  # Header 2
                self.setFormat(0, 2, self._hStyles["header2h"])
                self.setFormat(2, len(text), self._hStyles["header2"])

            elif text.startswith("### "):  # Header 3
                self.setFormat(0, 3, self._hStyles["header3h"])
                self.setFormat(3, len(text), self._hStyles["header3"])

            elif text.startswith("#### "):  # Header 4
                self.setFormat(0, 4, self._hStyles["header4h"])
                self.setFormat(4, len(text), self._hStyles["header4"])

            elif text.startswith("#! "):  # Title
                self.setFormat(0, 2, self._hStyles["header1h"])
                self.setFormat(2, len(text), self._hStyles["header1"])

            elif text.startswith("##! "):  # Unnumbered
                self.setFormat(0, 3, self._hStyles["header2h"])
                self.setFormat(3, len(text), self._hStyles["header2"])

        elif text.startswith("%"):  # Comments
            self.setCurrentBlockState(self.BLOCK_TEXT)
            cStyle, _, cPos = processComment(text)
            if cStyle == nwComment.PLAIN:
                self.setFormat(0, len(text), self._hStyles["hidden"])
            else:
                self.setFormat(0, cPos, self._hStyles["modifier"])
                self.setFormat(cPos, len(text), self._hStyles["hidden"])

        else:  # Text Paragraph

            if text.startswith("["):  # Special Command
                sText = text.rstrip().lower()
                if sText in ("[newpage]", "[new page]", "[vspace]"):
                    self.setFormat(0, len(text), self._hStyles["code"])
                    return
                elif sText.startswith("[vspace:") and sText.endswith("]"):
                    tLen = len(sText)
                    tVal = checkInt(sText[8:-1], 0)
                    cVal = "codevalue" if tVal > 0 else "codeinval"
                    self.setFormat(0, 8, self._hStyles["code"])
                    self.setFormat(8, tLen-9, self._hStyles[cVal])
                    self.setFormat(tLen-1, tLen, self._hStyles["code"])
                    return

            # Regular Text
            self.setCurrentBlockState(self.BLOCK_TEXT)
            for rX, xFmt in self.rxRules:
                rxItt = rX.globalMatch(text, 0)
                while rxItt.hasNext():
                    rxMatch = rxItt.next()
                    for xM in xFmt:
                        xPos = rxMatch.capturedStart(xM)
                        xLen = rxMatch.capturedLength(xM)
                        for x in range(xPos, xPos+xLen):
                            spFmt = self.format(x)
                            if spFmt != self._hStyles["hidden"]:
                                spFmt.merge(xFmt[xM])
                                self.setFormat(x, 1, spFmt)

        data = self.currentBlockUserData()
        if not isinstance(data, TextBlockData):
            data = TextBlockData()
            self.setCurrentBlockUserData(data)

        if self._spellCheck:
            for xPos, xLen in data.spellCheck(text):
                for x in range(xPos, xPos+xLen):
                    spFmt = self.format(x)
                    spFmt.merge(self._spellErr)
                    self.setFormat(x, 1, spFmt)

        return

    ##
    #  Internal Functions
    ##

    def _makeFormat(self, color: QColor | None = None, style: str | None = None,
                    size: float | None = None) -> QTextCharFormat:
        """Generate a valid character format to be applied to the text
        that is to be highlighted.
        """
        charFormat = QTextCharFormat()

        if color is not None:
            charFormat.setForeground(color)

        if style is not None:
            styles = style.split(",")
            if "bold" in styles:
                charFormat.setFontWeight(QFont.Bold)
            if "italic" in styles:
                charFormat.setFontItalic(True)
            if "strike" in styles:
                charFormat.setFontStrikeOut(True)
            if "errline" in styles:
                charFormat.setUnderlineColor(SHARED.theme.colError)
                charFormat.setUnderlineStyle(QTextCharFormat.SpellCheckUnderline)
            if "background" in styles and color is not None:
                charFormat.setBackground(QBrush(color, Qt.SolidPattern))

        if size is not None:
            charFormat.setFontPointSize(int(round(size*CONFIG.textSize)))

        return charFormat

# END Class GuiDocHighlighter


class TextBlockData(QTextBlockUserData):

    __slots__ = ("_spellErrors")

    def __init__(self) -> None:
        super().__init__()
        self._spellErrors: list[tuple[int, int]] = []
        return

    @property
    def spellErrors(self) -> list[tuple[int, int]]:
        """Return spell error data from last check."""
        return self._spellErrors

    def spellCheck(self, text: str) -> list[tuple[int, int]]:
        """Run the spell checker and cache the result, and return the
        list of spell check errors.
        """
        self._spellErrors = []
        rxSpell = SPELLRX.globalMatch(text.replace("_", " "), 0)
        while rxSpell.hasNext():
            rxMatch = rxSpell.next()
            if not SHARED.spelling.checkWord(rxMatch.captured(0)):
                if not rxMatch.captured(0).isnumeric() and not rxMatch.captured(0).isupper():
                    self._spellErrors.append((rxMatch.capturedStart(0), rxMatch.capturedLength(0)))
        return self._spellErrors

# END Class TextBlockData
