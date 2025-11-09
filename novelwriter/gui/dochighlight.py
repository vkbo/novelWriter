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
"""  # noqa
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
from novelwriter.common import checkInt, utf16CharMap
from novelwriter.constants import nwStyles, nwUnicode
from novelwriter.enum import nwComment
from novelwriter.text.comments import processComment
from novelwriter.text.patterns import REGEX_PATTERNS, DialogParser
from novelwriter.types import QtTextUserProperty

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
    """GUI: Editor Syntax Highlighter."""

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

    def initHighlighter(self) -> None:
        """Initialise the syntax highlighter, setting all the colour
        rules and building the RegExes.
        """
        logger.debug("Setting up highlighting rules")
        syntax = SHARED.theme.syntaxTheme

        colEmph = syntax.emph if CONFIG.highlightEmph else None

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
        self._addCharFormat("mark",      syntax.mark, "bg")
        self._addCharFormat("mspaces",   syntax.error, "err")
        self._addCharFormat("nobreak",   syntax.space, "bg")
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
            rxRule = re.compile(r"[ ]{2,}")
            hlRule = {
                0: self._hStyles["mspaces"],
            }
            self._minRules.append((rxRule, hlRule))
            self._txtRules.append((rxRule, hlRule))
            self._cmnRules.append((rxRule, hlRule))

        # Non-Breaking Spaces
        rxRule = re.compile(f"[{nwUnicode.U_NBSP}{nwUnicode.U_THNBSP}]+")
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

        # Markdown Highlight
        rxRule = REGEX_PATTERNS.markdownMark
        hlRule = {
            1: self._hStyles["markup"],
            2: self._hStyles["mark"],
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
        rxRule = re.compile(r"(^>{1,2}|<{1,2}$)")
        hlRule = {
            1: self._hStyles["markup"],
        }
        self._minRules.append((rxRule, hlRule))
        self._txtRules.append((rxRule, hlRule))

        # Auto-Replace Tags
        rxRule = re.compile(r"<(\S+?)>")
        hlRule = {
            0: self._hStyles["replace"],
        }
        self._minRules.append((rxRule, hlRule))
        self._txtRules.append((rxRule, hlRule))
        self._cmnRules.append((rxRule, hlRule))

    ##
    #  Setters
    ##

    def setSpellCheck(self, state: bool) -> None:
        """Enable/disable the real time spell checker."""
        self._spellCheck = state

    def setHandle(self, tHandle: str) -> None:
        """Set the handle of the currently highlighted document."""
        self._tHandle = tHandle
        self._isNovel = False
        self._isInactive = False
        if item := SHARED.project.tree[tHandle]:
            self._isNovel = item.isDocumentLayout()
            self._isInactive = item.isInactiveClass()
        logger.debug("Syntax highlighter enabled for item '%s'", tHandle)

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

        blockLen = self.currentBlock().length()
        utf16Map = None
        if blockLen > len(text) + 1:
            # If the lengths are different, the line contains 4 byte
            # Unicode characters, and we must use a map between Python
            # string indices and the UTF-16 indices used by Qt, where a
            # 4 byte character occupies two slots. See #2449.
            utf16Map = utf16CharMap(text)

        offset = 0
        rules = None
        if text.startswith("@"):  # Keywords and commands
            self.setCurrentBlockState(BLOCK_META)
            index = SHARED.project.index
            isValid, bits, loc = index.scanThis(text)
            isGood = index.checkThese(bits, self._tHandle)
            if isValid:
                for n, bit in enumerate(bits):
                    pos = utf16Map[loc[n]] if utf16Map else loc[n]
                    length = utf16Map[loc[n] + len(bit)] - pos if utf16Map else len(bit)
                    if n == 0 and isGood[n]:
                        self.setFormat(pos, length, self._hStyles["keyword"])
                    elif isGood[n] and not self._isInactive:
                        a, b = index.parseValue(bit)
                        aLen = utf16Map[loc[n] + len(a)] - pos if utf16Map else len(a)
                        self.setFormat(pos, aLen, self._hStyles["tag"])
                        if b:
                            bLen = utf16Map[loc[n] + len(b)] - pos if utf16Map else len(b)
                            self.setFormat(pos + length - bLen, bLen, self._hStyles["optional"])
                    elif not self._isInactive:
                        self.setFormat(pos, length, self._hStyles["invalid"])

            # We never want to run the spell checker on keyword/values,
            # so we force a return here
            return

        elif text.startswith(("# ", "#! ", "## ", "##! ", "### ", "###! ", "#### ")):
            self.setCurrentBlockState(BLOCK_TITLE)

            if text.startswith("# "):  # Heading 1
                self.setFormat(0, 1, self._hStyles["head1h"])
                self.setFormat(1, blockLen, self._hStyles["header1"])

            elif text.startswith("## "):  # Heading 2
                self.setFormat(0, 2, self._hStyles["head2h"])
                self.setFormat(2, blockLen, self._hStyles["header2"])

            elif text.startswith("### "):  # Heading 3
                self.setFormat(0, 3, self._hStyles["head3h"])
                self.setFormat(3, blockLen, self._hStyles["header3"])

            elif text.startswith("#### "):  # Heading 4
                self.setFormat(0, 4, self._hStyles["head4h"])
                self.setFormat(4, blockLen, self._hStyles["header4"])

            elif text.startswith("#! "):  # Title
                self.setFormat(0, 2, self._hStyles["head1h"])
                self.setFormat(2, blockLen, self._hStyles["header1"])

            elif text.startswith("##! "):  # Unnumbered
                self.setFormat(0, 3, self._hStyles["head2h"])
                self.setFormat(3, blockLen, self._hStyles["header2"])

            elif text.startswith("###! "):  # Alternative Scene
                self.setFormat(0, 4, self._hStyles["head3h"])
                self.setFormat(4, blockLen, self._hStyles["header3"])

        elif text.startswith("%"):  # Comments
            self.setCurrentBlockState(BLOCK_TEXT)
            rules = self._cmnRules

            style, mod, _, dot, pos = processComment(text)
            offset = pos
            if utf16Map:
                dot = utf16Map[dot]
                pos = utf16Map[pos]
            length = blockLen - pos
            if style == nwComment.PLAIN:
                self.setFormat(0, length, self._hStyles["hidden"])
            elif style == nwComment.IGNORE:
                self.setFormat(0, length, self._hStyles["strike"])
                return  # No more processing for these
            elif mod:
                self.setFormat(0, dot, self._hStyles["modifier"])
                self.setFormat(dot, pos - dot, self._hStyles["value"])
                self.setFormat(pos, length, self._hStyles["note"])
            else:
                self.setFormat(0, pos, self._hStyles["modifier"])
                self.setFormat(pos, length, self._hStyles["note"])

        elif text.startswith("["):  # Special Command
            self.setCurrentBlockState(BLOCK_TEXT)
            rules = self._txtRules if self._isNovel else self._minRules

            check = text.rstrip().lower()
            if check in ("[newpage]", "[new page]", "[vspace]"):
                self.setFormat(0, blockLen, self._hStyles["code"])
                return
            elif check.startswith("[vspace:") and check.endswith("]"):
                value = checkInt(check[8:-1], 0)
                style = "value" if value > 0 else "invalid"
                self.setFormat(0, 8, self._hStyles["code"])
                self.setFormat(8, blockLen-10, self._hStyles[style])
                self.setFormat(blockLen-2, blockLen, self._hStyles["code"])
                return

        else:  # Text Paragraph
            self.setCurrentBlockState(BLOCK_TEXT)
            rules = self._txtRules if self._isNovel else self._minRules
            if self._isNovel and self._dialogParser.enabled:
                if utf16Map:
                    for pos, end in self._dialogParser(text):
                        pos = utf16Map[pos]
                        end = utf16Map[end]
                        self.setFormat(pos, end - pos, self._hStyles["dialog"])
                else:
                    for pos, end in self._dialogParser(text):
                        self.setFormat(pos, end - pos, self._hStyles["dialog"])

        if rules:
            if utf16Map:
                for rX, hRule in rules:
                    for res in re.finditer(rX, text[offset:]):
                        for x, hFmt in hRule.items():
                            pos = res.start(x) + offset
                            end = res.end(x) + offset
                            for x in range(pos, end):
                                m = utf16Map[x]
                                cFmt = self.format(m)
                                if not cFmt.property(QtTextUserProperty):
                                    cFmt.merge(hFmt)
                                    self.setFormat(m, utf16Map[x+1] - m, cFmt)
            else:
                for rX, hRule in rules:
                    for res in re.finditer(rX, text[offset:]):
                        for x, hFmt in hRule.items():
                            pos = res.start(x) + offset
                            end = res.end(x) + offset
                            for x in range(pos, end):
                                cFmt = self.format(x)
                                if not cFmt.property(QtTextUserProperty):
                                    cFmt.merge(hFmt)
                                    self.setFormat(x, 1, cFmt)

        data = self.currentBlockUserData()
        if not isinstance(data, TextBlockData):
            data = TextBlockData()
            self.setCurrentBlockUserData(data)

        data.processText(text, offset)
        if self._spellCheck:
            for pos, end, _ in data.spellCheck(utf16Map):
                for x in range(pos, end):
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
        blockMerge = name == "markup"
        charFormat.setProperty(QtTextUserProperty, blockMerge)

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
                color = None

        if color:
            charFormat.setForeground(color)

        if size:
            charFormat.setFontPointSize(round(size*CONFIG.textFont.pointSize()))

        self._hStyles[name] = charFormat


class TextBlockData(QTextBlockUserData):
    """Custom QTextBlock Data.

    Custom data stored in a single text block. The spell check state is
    cached here and used when correcting misspelled text.
    """

    __slots__ = ("_metaData", "_offset", "_spellErrors", "_text")

    def __init__(self) -> None:
        super().__init__()
        self._text = ""
        self._offset = 0
        self._metaData: list[tuple[int, int, str, str]] = []
        self._spellErrors: list[tuple[int, int, str]] = []

    @property
    def metaData(self) -> list[tuple[int, int, str, str]]:
        """Return meta data from last check."""
        return self._metaData

    @property
    def spellErrors(self) -> list[tuple[int, int, str]]:
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

        self._text = text.replace("\u02bc", "'").replace("_", " ")
        self._offset = offset

    def spellCheck(self, utf16Map: list[int] | None) -> list[tuple[int, int, str]]:
        """Run the spell checker and cache the result, and return the
        list of spell check errors.
        """
        spell = SHARED.spelling
        if utf16Map:
            self._spellErrors = [
                (utf16Map[r.start(0)], utf16Map[r.end(0)], w)
                for r in RX_WORDS.finditer(self._text, self._offset)
                if (w := r.group(0)) and not (w.isnumeric() or w.isupper() or spell.checkWord(w))
            ]
        else:
            self._spellErrors = [
                (r.start(0), r.end(0), w)
                for r in RX_WORDS.finditer(self._text, self._offset)
                if (w := r.group(0)) and not (w.isnumeric() or w.isupper() or spell.checkWord(w))
            ]
        return self._spellErrors
