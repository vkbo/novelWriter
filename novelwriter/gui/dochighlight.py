"""
novelWriter – GUI Syntax Highlighter
====================================

File History:
Created: 2019-04-06 [0.0.1] GuiDocHighlighter
Created: 2023-09-10 [2.2b1] TextBlockData

This file is a part of novelWriter
Copyright (C) 2019 Veronica Berglyd Olsen and novelWriter contributors

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
import re

from time import time

from PyQt6.QtCore import Qt
from PyQt6.QtGui import (
    QBrush, QColor, QFont, QSyntaxHighlighter, QTextBlockUserData,
    QTextCharFormat, QTextDocument
)

from novelwriter import CONFIG, SHARED
from novelwriter.common import checkInt
from novelwriter.constants import nwStyles, nwUnicode
from novelwriter.enum import nwComment
from novelwriter.text.comments import processComment
from novelwriter.text.patterns import REGEX_PATTERNS, DialogParser

logger = logging.getLogger(__name__)

RX_URL = REGEX_PATTERNS.url
RX_WORDS = REGEX_PATTERNS.wordSplit
RX_FMT_SC = REGEX_PATTERNS.shortcodePlain
RX_FMT_SV = REGEX_PATTERNS.shortcodeValue

BLOCK_NONE  = 0
BLOCK_TEXT  = 1
BLOCK_META  = 2
BLOCK_TITLE = 4


class GuiDocHighlighter(QSyntaxHighlighter):

    __slots__ = (
        "_cmnRules", "_dialogParser", "_hStyles", "_isInactive", "_isNovel",
        "_minRules", "_spellCheck", "_spellErr", "_tHandle", "_txtRules",
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
        self._minRules: list[tuple[re.Pattern, dict[int, QTextCharFormat]]] = []
        self._txtRules: list[tuple[re.Pattern, dict[int, QTextCharFormat]]] = []
        self._cmnRules: list[tuple[re.Pattern, dict[int, QTextCharFormat]]] = []

        self._dialogParser = DialogParser()

        self.initHighlighter()

        logger.debug("Ready: GuiDocHighlighter")

        return

    def initHighlighter(self) -> None:
        """Initialise the syntax highlighter, setting all the colour
        rules and building the RegExes.
        """
        logger.debug("Setting up highlighting rules")
        syntax = SHARED.theme.syntaxTheme

        colEmph = syntax.emph if CONFIG.highlightEmph else None
        colBreak = QColor(syntax.emph)
        colBreak.setAlpha(64)

        # Create Character Formats
        self._addCharFormat("text",      syntax.text)
        self._addCharFormat("header1",   syntax.head, "b", nwStyles.H_SIZES[1])
        self._addCharFormat("header2",   syntax.head, "b", nwStyles.H_SIZES[2])
        self._addCharFormat("header3",   syntax.head, "b", nwStyles.H_SIZES[3])
        self._addCharFormat("header4",   syntax.head, "b", nwStyles.H_SIZES[4])
        self._addCharFormat("head1h",    syntax.headH, "b", nwStyles.H_SIZES[1])
        self._addCharFormat("head2h",    syntax.headH, "b", nwStyles.H_SIZES[2])
        self._addCharFormat("head3h",    syntax.headH, "b", nwStyles.H_SIZES[3])
        self._addCharFormat("head4h",    syntax.headH, "b", nwStyles.H_SIZES[4])
        self._addCharFormat("bold",      colEmph, "b")
        self._addCharFormat("italic",    colEmph, "i")
        self._addCharFormat("strike",    syntax.hidden, "s")
        self._addCharFormat("mspaces",   syntax.error, "err")
        self._addCharFormat("nobreak",   colBreak, "bg")
        self._addCharFormat("altdialog", syntax.dialA)
        self._addCharFormat("dialog",    syntax.dialN)
        self._addCharFormat("replace",   syntax.repTag)
        self._addCharFormat("hidden",    syntax.hidden)
        self._addCharFormat("markup",    syntax.hidden)
        self._addCharFormat("link",      syntax.link, "u")
        self._addCharFormat("note",      syntax.note)
        self._addCharFormat("code",      syntax.code)
        self._addCharFormat("keyword",   syntax.key)
        self._addCharFormat("tag",       syntax.tag, "u")
        self._addCharFormat("modifier",  syntax.mod)
        self._addCharFormat("value",     syntax.val)
        self._addCharFormat("optional",  syntax.opt)
        self._addCharFormat("invalid",   None, "err")

        # Cache Spell Error Format
        self._spellErr = QTextCharFormat()
        self._spellErr.setUnderlineColor(syntax.spell)
        self._spellErr.setUnderlineStyle(QTextCharFormat.UnderlineStyle.SpellCheckUnderline)

        self._txtRules.clear()
        self._cmnRules.clear()

        self._dialogParser.initParser()

        # Multiple or Trailing Spaces
        if CONFIG.showMultiSpaces:
            rxRule = re.compile(r"[ ]{2,}|[ ]*$", re.UNICODE)
            hlRule = {
                0: self._hStyles["mspaces"],
            }
            self._minRules.append((rxRule, hlRule))
            self._txtRules.append((rxRule, hlRule))
            self._cmnRules.append((rxRule, hlRule))

        # Non-Breaking Spaces
        rxRule = re.compile(f"[{nwUnicode.U_NBSP}{nwUnicode.U_THNBSP}]+", re.UNICODE)
        hlRule = {
            0: self._hStyles["nobreak"],
        }
        self._minRules.append((rxRule, hlRule))
        self._txtRules.append((rxRule, hlRule))
        self._cmnRules.append((rxRule, hlRule))

        # Alt Dialogue
        if rxRule := REGEX_PATTERNS.altDialogStyle:
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

        # URLs
        rxRule = REGEX_PATTERNS.url
        hlRule = {
            0: self._hStyles["link"],
        }
        self._minRules.append((rxRule, hlRule))
        self._txtRules.append((rxRule, hlRule))
        self._cmnRules.append((rxRule, hlRule))

        # Alignment Tags
        rxRule = re.compile(r"(^>{1,2}|<{1,2}$)", re.UNICODE)
        hlRule = {
            1: self._hStyles["markup"],
        }
        self._minRules.append((rxRule, hlRule))
        self._txtRules.append((rxRule, hlRule))

        # Auto-Replace Tags
        rxRule = re.compile(r"<(\S+?)>", re.UNICODE)
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
        if document := self.document():
            nBlocks = document.blockCount()
            tStart = time()
            for i in range(nBlocks):
                block = document.findBlockByNumber(i)
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
            if self._isNovel and self._dialogParser.enabled:
                for pos, end in self._dialogParser(text):
                    length = end - pos
                    self.setFormat(pos, length, self._hStyles["dialog"])

        if hRules:
            for rX, hRule in hRules:
                for res in re.finditer(rX, text[xOff:]):
                    for xM, hFmt in hRule.items():
                        xPos = res.start(xM) + xOff
                        xEnd = res.end(xM) + xOff
                        for x in range(xPos, xEnd):
                            cFmt = self.format(x)
                            if cFmt.fontStyleName() != "markup":
                                cFmt.merge(hFmt)
                                self.setFormat(x, 1, cFmt)

        data = self.currentBlockUserData()
        if not isinstance(data, TextBlockData):
            data = TextBlockData()
            self.setCurrentBlockUserData(data)

        data.processText(text, xOff)
        if self._spellCheck:
            for xPos, xEnd in data.spellCheck():
                for x in range(xPos, xEnd):
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
            if "u" in styles:
                charFormat.setFontUnderline(True)
            if "s" in styles:
                charFormat.setFontStrikeOut(True)
            if "err" in styles:
                charFormat.setUnderlineColor(SHARED.theme.syntaxTheme.error)
                charFormat.setUnderlineStyle(QTextCharFormat.UnderlineStyle.SpellCheckUnderline)
            if "bg" in styles and color is not None:
                charFormat.setBackground(QBrush(color, Qt.BrushStyle.SolidPattern))

        if size:
            charFormat.setFontPointSize(round(size*CONFIG.textFont.pointSize()))

        self._hStyles[name] = charFormat

        return


class TextBlockData(QTextBlockUserData):

    __slots__ = ("_metaData", "_offset", "_spellErrors", "_text")

    def __init__(self) -> None:
        super().__init__()
        self._text = ""
        self._offset = 0
        self._metaData: list[tuple[int, int, str, str]] = []
        self._spellErrors: list[tuple[int, int]] = []
        return

    @property
    def metaData(self) -> list[tuple[int, int, str, str]]:
        """Return meta data from last check."""
        return self._metaData

    @property
    def spellErrors(self) -> list[tuple[int, int]]:
        """Return spell error data from last check."""
        return self._spellErrors

    def processText(self, text: str, offset: int) -> None:
        """Extract meta data from the text."""
        self._metaData = []
        if "[" in text:
            # Strip shortcodes
            for regEx in [RX_FMT_SC, RX_FMT_SV]:
                for res in regEx.finditer(text, offset):
                    if (s := res.start(0)) >= 0 and (e := res.end(0)) >= 0:
                        pad = " "*(e - s)
                        text = f"{text[:s]}{pad}{text[e:]}"

        if "http" in text:
            # Strip URLs
            for res in RX_URL.finditer(text, offset):
                if (s := res.start(0)) >= 0 and (e := res.end(0)) >= 0:
                    pad = " "*(e - s)
                    text = f"{text[:s]}{pad}{text[e:]}"
                    self._metaData.append((s, e, res.group(0), "url"))

        self._text = text.replace("\u02bc", "'")
        self._offset = offset

        return

    def spellCheck(self) -> list[tuple[int, int]]:
        """Run the spell checker and cache the result, and return the
        list of spell check errors.
        """
        self._spellErrors = []
        checker = SHARED.spelling
        for res in RX_WORDS.finditer(self._text.replace("_", " "), self._offset):
            if (
                (word := res.group(0))
                and not (word.isnumeric() or word.isupper() or checker.checkWord(word))
            ):
                self._spellErrors.append((res.start(0), res.end(0)))

        return self._spellErrors
