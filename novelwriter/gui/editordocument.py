"""
novelWriter – GUI Text Document
===============================

This file is a part of novelWriter
Copyright (C) 2023 Veronica Berglyd Olsen and novelWriter contributors

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

from time import time
from typing import TYPE_CHECKING

from PyQt6.QtGui import QTextBlock, QTextBlockFormat, QTextCursor, QTextDocument
from PyQt6.QtWidgets import QApplication

from novelwriter import CONFIG, SHARED
from novelwriter.gui.dochighlight import GuiDocHighlighter
from novelwriter.gui.doctextblock import TextBlockData
from novelwriter.types import QtPropLineHeight

if TYPE_CHECKING:
    from collections.abc import Iterable

    from PyQt6.QtCore import QObject

logger = logging.getLogger(__name__)


class GuiTextDocument(QTextDocument):
    """Custom: Modified QTextDocument.

    A special text document format that incorporates a few additional
    features including spell checking.
    """

    def __init__(self, parent: QObject) -> None:
        super().__init__(parent=parent)

        self._handle = None
        self._syntax = GuiDocHighlighter(self)

        logger.debug("Ready: GuiTextDocument")

    def __del__(self) -> None:  # pragma: no cover
        """Class destructor."""
        logger.debug("Delete: GuiTextDocument")

    ##
    #  Properties
    ##

    @property
    def syntaxHighlighter(self) -> GuiDocHighlighter:
        """Return the document's syntax highlighter object."""
        return self._syntax

    ##
    #  Methods
    ##

    def setTextContent(self, text: str, tHandle: str) -> None:
        """Set the text content of the document."""
        self._syntax.setHandle(tHandle)

        self.blockSignals(True)
        self.setUndoRedoEnabled(False)
        self.clear()

        tStart = time()

        self.setPlainText(text)
        self.setLineHeight(CONFIG.lineHeight)
        count = self.lineCount()

        tMid = time()

        self.setUndoRedoEnabled(True)
        self.blockSignals(False)
        self._syntax.rehighlight()
        QApplication.processEvents()

        tEnd = time()

        logger.debug("Loaded %d text blocks in %.3f ms", count, 1000 * (tMid - tStart))
        logger.debug("Highlighted document in %.3f ms", 1000 * (tEnd - tMid))

    def setLineHeight(self, height: float) -> None:
        """Apply a line height to all blocks in the document.

        The last block is deliberately excluded. Merging a block
        format onto the block a live QTextCursor currently occupies
        corrupts the following Return keypress (it silently fails to
        split the block) for reasons that trace into Qt/PyQt6
        internals rather than anything in this codebase. The excluded
        block keeps its old height until the document is reloaded, or
        until more text is added after it and this is called again.
        """
        end = self.lastBlock().position() - 1
        if end <= 0:
            # Single-block document: there is nothing to select before
            # the last (and only) block, so it can't be touched safely
            return

        blockFormat = QTextBlockFormat()
        blockFormat.setLineHeight(int(height * 100), QtPropLineHeight)
        cursor = QTextCursor(self)
        cursor.setPosition(0)
        cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
        cursor.mergeBlockFormat(blockFormat)

    def metaDataAtPos(self, pos: int) -> tuple[str, str]:
        """Check if there is meta data available at a given position in
        the document, and if so, return it.
        """
        cursor = QTextCursor(self)
        cursor.setPosition(pos)
        block = cursor.block()
        data = block.userData()
        if block.isValid() and isinstance(data, TextBlockData) and (check := pos - block.position()) >= 0:
            for cPos, cEnd, cData, cType in data.metaData:
                if cPos <= check <= cEnd:
                    return cData, cType
        return "", ""

    def spellErrorAtPos(self, pos: int) -> tuple[str, int, int, list[str]]:
        """Check if there is a misspelled word at a given position in
        the document, and if so, return it with its start and end
        positions within the block.
        """
        cursor = QTextCursor(self)
        cursor.setPosition(pos)
        block = cursor.block()
        data = block.userData()
        if block.isValid() and isinstance(data, TextBlockData) and (check := pos - block.position()) >= 0:
            for start, end, word in data.spellErrors:
                if start <= check <= end:
                    return word, start, end, SHARED.spelling.suggestWords(word)
        return "", -1, -1, []

    def iterBlockByType(self, cType: int, maxCount: int = 1000) -> Iterable[QTextBlock]:
        """Iterate over all text blocks of a given type."""
        count = 0
        for i in range(self.blockCount()):
            block = self.findBlockByNumber(i)
            if count < maxCount and block.isValid() and block.userState() & cType > 0:
                count += 1
                yield block
        return
