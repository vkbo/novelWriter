"""
novelWriter – QTextDocument to Text Converter
==============================================

This file is a part of novelWriter
Copyright (C) 2026 Veronica Berglyd Olsen and novelWriter contributors

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

from typing import TYPE_CHECKING

from PyQt6.QtGui import QFont, QTextCharFormat, QTextDocument

from novelwriter import CONFIG
from novelwriter.constants import nwShortcode, nwUnicode

if TYPE_CHECKING:
    from collections.abc import Iterator

    from PyQt6.QtGui import QTextBlock

logger = logging.getLogger(__name__)

SHORTCODES = {
    "bold": (nwShortcode.BOLD_O, nwShortcode.BOLD_C),
    "italic": (nwShortcode.ITALIC_O, nwShortcode.ITALIC_C),
    "strike": (nwShortcode.STRIKE_O, nwShortcode.STRIKE_C),
    "underline": (nwShortcode.ULINE_O, nwShortcode.ULINE_C),
    "sup": (nwShortcode.SUP_O, nwShortcode.SUP_C),
    "sub": (nwShortcode.SUB_O, nwShortcode.SUB_C),
}

MARKDOWN_FMTS = ("underline", "sub", "sup", "strike", "italic", "bold")


class FromQTextDocument:
    """Core: Convert a QTextDocument to novelWriter's Text Format."""

    __slots__ = ("_document", "_preserveSoftBreak", "_result")

    def __init__(self, document: QTextDocument) -> None:
        self._document = document
        self._result: list[str] = []
        self._preserveSoftBreak = False

    def setPreserveSoftBreak(self, state: bool) -> None:
        """Set whether soft line breaks should be preserved as hard
        line breaks, or collapsed into a single space.
        """
        self._preserveSoftBreak = state

    def convert(self) -> Iterator[int]:
        """Convert the document one block at a time. Yields the number
        of blocks processed so far as a progress counter.
        """
        self._result = []
        count = 0
        block = self._document.begin()
        while block.isValid():
            if (level := block.blockFormat().headingLevel()) > 0:
                self._addHeading(block, level)
            else:
                self._addParagraph(block)
            count += 1
            yield count
            block = block.next()

    def result(self) -> str:
        """Return the converted text as a single string."""
        return "\n".join(self._result)

    ##
    #  Internal Functions
    ##

    def _addHeading(self, block: QTextBlock, level: int) -> None:
        """Add a heading block to the result."""
        text = self._resolveSoftBreaks(block.text())
        if level <= 4:
            self._result.append(f"{'#' * level} {text}")
        else:
            bold = "*" if CONFIG.singleStarBold else "**"
            self._result.append(f"{bold}{text}{bold}")
        self._result.append("")

    def _addParagraph(self, block: QTextBlock) -> None:
        """Add a regular text block to the result."""
        text = self._formatBlock(block)
        if text.strip():
            self._result.append(text)
        self._result.append("")

    def _resolveSoftBreaks(self, text: str) -> str:
        """Convert soft line break characters to either a Markdown
        hard line break, or a single space.
        """
        if self._preserveSoftBreak:
            return text.replace(nwUnicode.U_LSEP, "  \n")
        return text.replace(nwUnicode.U_LSEP, " ")

    def _formatBlock(self, block: QTextBlock) -> str:
        """Format the text of a block, applying inline formatting to
        each of its fragments.
        """
        blockText = block.text()
        parts = []
        offset = 0
        it = block.begin()
        while not it.atEnd():
            if (frag := it.fragment()).isValid():
                text = frag.text()
                parts.append(self._formatFragment(text, offset, blockText, frag.charFormat()))
                offset += len(text)
            it += 1
        return self._resolveSoftBreaks("".join(parts))

    def _formatFragment(self, text: str, start: int, blockText: str, cFormat: QTextCharFormat) -> str:
        """Wrap a single formatted text fragment in the appropriate
        Markdown syntax or novelWriter shortcode.
        """
        core = text.strip()
        if not core:
            return text

        lead = text[: len(text) - len(text.lstrip())]
        trail = text[len(lead) + len(core) :]

        coreStart = start + len(lead)
        coreEnd = coreStart + len(core)
        cleanEdges = (coreStart == 0 or not self._isWordChar(blockText[coreStart - 1])) and (
            coreEnd >= len(blockText) or not self._isWordChar(blockText[coreEnd])
        )

        align = cFormat.verticalAlignment()
        active = {
            "underline": cFormat.fontUnderline(),
            "sub": align == QTextCharFormat.VerticalAlignment.AlignSubScript,
            "sup": align == QTextCharFormat.VerticalAlignment.AlignSuperScript,
            "strike": cFormat.fontStrikeOut(),
            "italic": cFormat.fontItalic(),
            "bold": cFormat.fontWeight() >= QFont.Weight.Bold,
        }

        for name in MARKDOWN_FMTS:
            if not active[name]:
                continue
            if name in ("bold", "italic", "strike") and cleanEdges:
                tag = self._markdownTag(name)
                core = f"{tag}{core}{tag}"
            else:
                cOpen, cClose = SHORTCODES[name]
                core = f"{cOpen}{core}{cClose}"

        return f"{lead}{core}{trail}"

    @staticmethod
    def _markdownTag(name: str) -> str:
        """Return the Markdown tag for a given format name."""
        if name == "bold":
            return "*" if CONFIG.singleStarBold else "**"
        elif name == "italic":
            return "_"
        return "~~"

    @staticmethod
    def _isWordChar(char: str) -> bool:
        """Check if a character counts as a word character."""
        return char.isalnum() or char == "_"
