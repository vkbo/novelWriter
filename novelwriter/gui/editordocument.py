"""
novelWriter – GUI Text Document
===============================

File History:
Created: 2023-09-07 [2.2b1] GuiTextDocument

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

from collections.abc import Iterable
from time import time

from PyQt5.QtCore import QObject, pyqtSlot
from PyQt5.QtGui import QTextBlock, QTextCursor, QTextDocument
from PyQt5.QtWidgets import QApplication, QPlainTextDocumentLayout

from novelwriter import SHARED
from novelwriter.gui.dochighlight import GuiDocHighlighter, TextBlockData

logger = logging.getLogger(__name__)


class GuiTextDocument(QTextDocument):

    def __init__(self, parent: QObject) -> None:
        super().__init__(parent=parent)

        self._handle = None
        self._syntax = GuiDocHighlighter(self)
        self.setDocumentLayout(QPlainTextDocumentLayout(self))

        logger.debug("Ready: GuiTextDocument")

        return

    def __del__(self) -> None:  # pragma: no cover
        logger.debug("Delete: GuiTextDocument")
        return

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
        count = self.lineCount()

        tMid = time()

        self.setUndoRedoEnabled(True)
        self.blockSignals(False)
        self._syntax.rehighlight()
        QApplication.processEvents()

        tEnd = time()

        logger.debug("Loaded %d text blocks in %.3f ms", count, 1000*(tMid - tStart))
        logger.debug("Highlighted document in %.3f ms", 1000*(tEnd - tMid))

        return

    def metaDataAtPos(self, pos: int) -> tuple[str, str]:
        """Check if there is meta data available at a given position in
        the document, and if so, return it.
        """
        cursor = QTextCursor(self)
        cursor.setPosition(pos)
        block = cursor.block()
        data = block.userData()
        if block.isValid() and isinstance(data, TextBlockData):
            if (check := pos - block.position()) >= 0:
                for cPos, cEnd, cData, cType in data.metaData:
                    if cPos <= check <= cEnd:
                        return cData, cType
        return "", ""

    def spellErrorAtPos(self, pos: int) -> tuple[str, int, int, list[str]]:
        """Check if there is a misspelled word at a given position in
        the document, and if so, return it.
        """
        cursor = QTextCursor(self)
        cursor.setPosition(pos)
        block = cursor.block()
        data = block.userData()
        if block.isValid() and isinstance(data, TextBlockData):
            text = block.text()
            check = pos - block.position()
            if check >= 0:
                for cPos, cEnd in data.spellErrors:
                    cLen = cEnd - cPos
                    if cPos <= check <= cEnd:
                        word = text[cPos:cEnd]
                        return word, cPos, cLen, SHARED.spelling.suggestWords(word)
        return "", -1, -1, []

    def iterBlockByType(self, cType: int, maxCount: int = 1000) -> Iterable[QTextBlock]:
        """Iterate over all text blocks of a given type."""
        count = 0
        for i in range(self.blockCount()):
            block = self.findBlockByNumber(i)
            if count < maxCount and block.isValid() and block.userState() & cType > 0:
                count += 1
                yield block
        return None

    ##
    #  Public Slots
    ##

    @pyqtSlot(bool)
    def setSpellCheckState(self, state: bool) -> None:
        """Set the spell check state of the syntax highlighter."""
        self._syntax.setSpellCheck(state)
        return
