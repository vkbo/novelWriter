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

from PyQt5.QtCore import QRegularExpression, Qt
from PyQt5.QtGui import (
    QBrush, QColor, QFont, QSyntaxHighlighter, QTextBlockUserData,
    QTextCharFormat, QTextDocument
)

from novelwriter import CONFIG, SHARED
from novelwriter.common import checkInt
from novelwriter.constants import nwHeaders, nwRegEx, nwUnicode
from novelwriter.core.index import processComment
from novelwriter.enum import nwComment
from novelwriter.text.patterns import REGEX_PATTERNS
from novelwriter.types import QRegExUnicode

logger = logging.getLogger(__name__)

SPELLRX = QRegularExpression(r"\b[^\s\-\+\/–—\[\]:]+\b")
SPELLRX.setPatternOptions(QRegExUnicode)
SPELLSC = QRegularExpression(nwRegEx.FMT_SC)
SPELLSC.setPatternOptions(QRegExUnicode)
SPELLSV = QRegularExpression(nwRegEx.FMT_SV)
SPELLSV.setPatternOptions(QRegExUnicode)

BLOCK_NONE  = 0
BLOCK_TEXT  = 1
BLOCK_META  = 2
BLOCK_TITLE = 4


class GuiDocHighlighter(QSyntaxHighlighter):

    __slots__ = (
        "_tHandle", "_isNovel", "_isInactive", "_spellCheck", "_spellErr",
        "_hStyles", "_minRules", "_txtRules", "_cmnRules",
    )

    def __init__(self, document: QTextDocument) -> None:
        super().__init__(document)

        logger.debug("Create: GuiDocHighlighter")

        self._tHandle = None
        self._isNovel = False
        self._isInactive = False
        self._spellCheck = False
        self._spellErr = QTextCharFormat()

        self._hStyles: dict[str, QTextCharFormat] = {}
        self._minRules: list[tuple[QRegularExpression, dict[int, QTextCharFormat]]] = []
        self._txtRules: list[tuple[QRegularExpression, dict[int, QTextCharFormat]]] = []
        self._cmnRules: list[tuple[QRegularExpression, dict[int, QTextCharFormat]]] = []

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

        # Create Character Formats
        self._addCharFormat("text",      SHARED.theme.colText)
        self._addCharFormat("header1",   SHARED.theme.colHead, "b", nwHeaders.H_SIZES[1])
        self._addCharFormat("header2",   SHARED.theme.colHead, "b", nwHeaders.H_SIZES[2])
        self._addCharFormat("header3",   SHARED.theme.colHead, "b", nwHeaders.H_SIZES[3])
        self._addCharFormat("header4",   SHARED.theme.colHead, "b", nwHeaders.H_SIZES[4])
        self._addCharFormat("head1h",    SHARED.theme.colHeadH, "b", nwHeaders.H_SIZES[1])
        self._addCharFormat("head2h",    SHARED.theme.colHeadH, "b", nwHeaders.H_SIZES[2])
        self._addCharFormat("head3h",    SHARED.theme.colHeadH, "b", nwHeaders.H_SIZES[3])
        self._addCharFormat("head4h",    SHARED.theme.colHeadH, "b", nwHeaders.H_SIZES[4])
        self._addCharFormat("bold",      colEmph, "b")
        self._addCharFormat("italic",    colEmph, "i")
        self._addCharFormat("strike",    SHARED.theme.colHidden, "s")
        self._addCharFormat("mspaces",   SHARED.theme.colError, "err")
        self._addCharFormat("nobreak",   colBreak, "bg")
        self._addCharFormat("altdialog", SHARED.theme.colDialA)
        self._addCharFormat("dialog",    SHARED.theme.colDialN)
        self._addCharFormat("replace",   SHARED.theme.colRepTag)
        self._addCharFormat("hidden",    SHARED.theme.colHidden)
        self._addCharFormat("markup",    SHARED.theme.colHidden)
        self._addCharFormat("note",      SHARED.theme.colNote)
        self._addCharFormat("code",      SHARED.theme.colCode)
        self._addCharFormat("keyword",   SHARED.theme.colKey)
        self._addCharFormat("tag",       SHARED.theme.colTag)
        self._addCharFormat("modifier",  SHARED.theme.colMod)
        self._addCharFormat("value",     SHARED.theme.colVal)
        self._addCharFormat("optional",  SHARED.theme.colOpt)
        self._addCharFormat("invalid",   None, "err")

        # Cache Spell Error Format
        self._spellErr = QTextCharFormat()
        self._spellErr.setUnderlineColor(SHARED.theme.colSpell)
        self._spellErr.setUnderlineStyle(QTextCharFormat.UnderlineStyle.SpellCheckUnderline)

        self._txtRules.clear()
        self._cmnRules.clear()

        # Multiple or Trailing Spaces
        if CONFIG.showMultiSpaces:
            rxRule = QRegularExpression(r"[ ]{2,}|[ ]*$")
            rxRule.setPatternOptions(QRegExUnicode)
            hlRule = {
                0: self._hStyles["mspaces"],
            }
            self._minRules.append((rxRule, hlRule))
            self._txtRules.append((rxRule, hlRule))
            self._cmnRules.append((rxRule, hlRule))

        # Non-Breaking Spaces
        rxRule = QRegularExpression(f"[{nwUnicode.U_NBSP}{nwUnicode.U_THNBSP}]+")
        rxRule.setPatternOptions(QRegExUnicode)
        hlRule = {
            0: self._hStyles["nobreak"],
        }
        self._minRules.append((rxRule, hlRule))
        self._txtRules.append((rxRule, hlRule))
        self._cmnRules.append((rxRule, hlRule))

        # Dialogue
        if CONFIG.dialogStyle > 0:
            rxRule = REGEX_PATTERNS.dialogStyle
            hlRule = {
                0: self._hStyles["dialog"],
            }
            self._txtRules.append((rxRule, hlRule))

        if CONFIG.dialogLine:
            rxRule = REGEX_PATTERNS.dialogLine
            hlRule = {
                0: self._hStyles["dialog"],
            }
            self._txtRules.append((rxRule, hlRule))

        if CONFIG.narratorBreak:
            rxRule = REGEX_PATTERNS.narratorBreak
            hlRule = {
                0: self._hStyles["text"],
            }
            self._txtRules.append((rxRule, hlRule))

        if CONFIG.altDialogOpen and CONFIG.altDialogClose:
            rxRule = REGEX_PATTERNS.altDialogStyle
            hlRule = {
                0: self._hStyles["altdialog"],
            }
            self._txtRules.append((rxRule, hlRule))

        # Markdown Italic
        rxRule = REGEX_PATTERNS.markdownItalic
        hlRule = {
            1: self._hStyles["markup"],
            2: self._hStyles["italic"],
            3: self._hStyles["markup"],
        }
        self._minRules.append((rxRule, hlRule))
        self._txtRules.append((rxRule, hlRule))
        self._cmnRules.append((rxRule, hlRule))

        # Markdown Bold
        rxRule = REGEX_PATTERNS.markdownBold
        hlRule = {
            1: self._hStyles["markup"],
            2: self._hStyles["bold"],
            3: self._hStyles["markup"],
        }
        self._minRules.append((rxRule, hlRule))
        self._txtRules.append((rxRule, hlRule))
        self._cmnRules.append((rxRule, hlRule))

        # Markdown Strikethrough
        rxRule = REGEX_PATTERNS.markdownStrike
        hlRule = {
            1: self._hStyles["markup"],
            2: self._hStyles["strike"],
            3: self._hStyles["markup"],
        }
        self._minRules.append((rxRule, hlRule))
        self._txtRules.append((rxRule, hlRule))
        self._cmnRules.append((rxRule, hlRule))

        # Shortcodes
        rxRule = REGEX_PATTERNS.shortcodePlain
        hlRule = {
            1: self._hStyles["code"],
        }
        self._minRules.append((rxRule, hlRule))
        self._txtRules.append((rxRule, hlRule))
        self._cmnRules.append((rxRule, hlRule))

        # Shortcodes w/Value
        rxRule = REGEX_PATTERNS.shortcodeValue
        hlRule = {
            1: self._hStyles["code"],
            2: self._hStyles["value"],
            3: self._hStyles["code"],
        }
        self._minRules.append((rxRule, hlRule))
        self._txtRules.append((rxRule, hlRule))
        self._cmnRules.append((rxRule, hlRule))

        # Alignment Tags
        rxRule = QRegularExpression(r"(^>{1,2}|<{1,2}$)")
        rxRule.setPatternOptions(QRegExUnicode)
        hlRule = {
            1: self._hStyles["markup"],
        }
        self._minRules.append((rxRule, hlRule))
        self._txtRules.append((rxRule, hlRule))

        # Auto-Replace Tags
        rxRule = QRegularExpression(r"<(\S+?)>")
        rxRule.setPatternOptions(QRegExUnicode)
        hlRule = {
            0: self._hStyles["replace"],
        }
        self._minRules.append((rxRule, hlRule))
        self._txtRules.append((rxRule, hlRule))
        self._cmnRules.append((rxRule, hlRule))

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
        self._isNovel = False
        self._isInactive = False
        if item := SHARED.project.tree[tHandle]:
            self._isNovel = item.isDocumentLayout()
            self._isInactive = item.isInactiveClass()
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
        self.setCurrentBlockState(BLOCK_NONE)
        if self._tHandle is None or not text:
            return

        xOff = 0
        hRules = None
        if text.startswith("@"):  # Keywords and commands
            self.setCurrentBlockState(BLOCK_META)
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
                        self.setFormat(xPos, len(one), self._hStyles["tag"])
                        if two:
                            yPos = xPos + len(bit) - len(two)
                            self.setFormat(yPos, len(two), self._hStyles["optional"])
                    elif not self._isInactive:
                        self.setFormat(xPos, xLen, self._hStyles["invalid"])

            # We never want to run the spell checker on keyword/values,
            # so we force a return here
            return

        elif text.startswith(("# ", "#! ", "## ", "##! ", "### ", "###! ", "#### ")):
            self.setCurrentBlockState(BLOCK_TITLE)

            if text.startswith("# "):  # Heading 1
                self.setFormat(0, 1, self._hStyles["head1h"])
                self.setFormat(1, len(text), self._hStyles["header1"])

            elif text.startswith("## "):  # Heading 2
                self.setFormat(0, 2, self._hStyles["head2h"])
                self.setFormat(2, len(text), self._hStyles["header2"])

            elif text.startswith("### "):  # Heading 3
                self.setFormat(0, 3, self._hStyles["head3h"])
                self.setFormat(3, len(text), self._hStyles["header3"])

            elif text.startswith("#### "):  # Heading 4
                self.setFormat(0, 4, self._hStyles["head4h"])
                self.setFormat(4, len(text), self._hStyles["header4"])

            elif text.startswith("#! "):  # Title
                self.setFormat(0, 2, self._hStyles["head1h"])
                self.setFormat(2, len(text), self._hStyles["header1"])

            elif text.startswith("##! "):  # Unnumbered
                self.setFormat(0, 3, self._hStyles["head2h"])
                self.setFormat(3, len(text), self._hStyles["header2"])

            elif text.startswith("###! "):  # Alternative Scene
                self.setFormat(0, 4, self._hStyles["head3h"])
                self.setFormat(4, len(text), self._hStyles["header3"])

        elif text.startswith("%"):  # Comments
            self.setCurrentBlockState(BLOCK_TEXT)
            hRules = self._cmnRules

            cStyle, cMod, _, cDot, cPos = processComment(text)
            cLen = len(text) - cPos
            xOff = cPos
            if cStyle == nwComment.PLAIN:
                self.setFormat(0, cLen, self._hStyles["hidden"])
            elif cStyle == nwComment.IGNORE:
                self.setFormat(0, cLen, self._hStyles["strike"])
                return  # No more processing for these
            elif cMod:
                self.setFormat(0, cDot, self._hStyles["modifier"])
                self.setFormat(cDot, cPos - cDot, self._hStyles["value"])
                self.setFormat(cPos, cLen, self._hStyles["note"])
            else:
                self.setFormat(0, cPos, self._hStyles["modifier"])
                self.setFormat(cPos, cLen, self._hStyles["note"])

        elif text.startswith("["):  # Special Command
            self.setCurrentBlockState(BLOCK_TEXT)
            hRules = self._txtRules if self._isNovel else self._minRules

            sText = text.rstrip().lower()
            if sText in ("[newpage]", "[new page]", "[vspace]"):
                self.setFormat(0, len(text), self._hStyles["code"])
                return
            elif sText.startswith("[vspace:") and sText.endswith("]"):
                tLen = len(sText)
                tVal = checkInt(sText[8:-1], 0)
                cVal = "value" if tVal > 0 else "invalid"
                self.setFormat(0, 8, self._hStyles["code"])
                self.setFormat(8, tLen-9, self._hStyles[cVal])
                self.setFormat(tLen-1, tLen, self._hStyles["code"])
                return

        else:  # Text Paragraph
            self.setCurrentBlockState(BLOCK_TEXT)
            hRules = self._txtRules if self._isNovel else self._minRules

        if hRules:
            for rX, hRule in hRules:
                rxItt = rX.globalMatch(text, xOff)
                while rxItt.hasNext():
                    rxMatch = rxItt.next()
                    for xM, hFmt in hRule.items():
                        xPos = rxMatch.capturedStart(xM)
                        xEnd = rxMatch.capturedEnd(xM)
                        for x in range(xPos, xEnd):
                            cFmt = self.format(x)
                            if cFmt.fontStyleName() != "markup":
                                cFmt.merge(hFmt)
                                self.setFormat(x, 1, cFmt)

        data = self.currentBlockUserData()
        if not isinstance(data, TextBlockData):
            data = TextBlockData()
            self.setCurrentBlockUserData(data)

        if self._spellCheck:
            for xPos, xLen in data.spellCheck(text, xOff):
                for x in range(xPos, xPos+xLen):
                    cFmt = self.format(x)
                    cFmt.merge(self._spellErr)
                    self.setFormat(x, 1, cFmt)

        return

    ##
    #  Internal Functions
    ##

    def _addCharFormat(
        self, name: str, color: QColor | None = None,
        style: str | None = None, size: float | None = None
    ) -> None:
        """Generate a highlighter character format."""
        charFormat = QTextCharFormat()
        charFormat.setFontStyleName(name)

        if color:
            charFormat.setForeground(color)

        if style:
            styles = style.split(",")
            if "b" in styles:
                charFormat.setFontWeight(QFont.Weight.Bold)
            if "i" in styles:
                charFormat.setFontItalic(True)
            if "s" in styles:
                charFormat.setFontStrikeOut(True)
            if "err" in styles:
                charFormat.setUnderlineColor(SHARED.theme.colError)
                charFormat.setUnderlineStyle(QTextCharFormat.UnderlineStyle.SpellCheckUnderline)
            if "bg" in styles and color is not None:
                charFormat.setBackground(QBrush(color, Qt.BrushStyle.SolidPattern))

        if size:
            charFormat.setFontPointSize(round(size*CONFIG.textFont.pointSize()))

        self._hStyles[name] = charFormat

        return


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

    def spellCheck(self, text: str, offset: int) -> list[tuple[int, int]]:
        """Run the spell checker and cache the result, and return the
        list of spell check errors.
        """
        if "[" in text:
            # Strip shortcodes
            for rX in [SPELLSC, SPELLSV]:
                rxItt = rX.globalMatch(text, offset)
                while rxItt.hasNext():
                    rxMatch = rxItt.next()
                    xPos = rxMatch.capturedStart(0)
                    xLen = rxMatch.capturedLength(0)
                    xEnd = rxMatch.capturedEnd(0)
                    text = text[:xPos] + " "*xLen + text[xEnd:]

        self._spellErrors = []
        rxSpell = SPELLRX.globalMatch(text.replace("_", " "), offset)
        while rxSpell.hasNext():
            rxMatch = rxSpell.next()
            if not SHARED.spelling.checkWord(rxMatch.captured(0)):
                if not rxMatch.captured(0).isnumeric() and not rxMatch.captured(0).isupper():
                    self._spellErrors.append(
                        (rxMatch.capturedStart(0), rxMatch.capturedLength(0))
                    )
        return self._spellErrors
