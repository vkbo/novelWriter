"""
novelWriter – GUI Text Document
===============================

File History:
Created: 2023-09-07 [2.2b1]

This file is a part of novelWriter
Copyright 2018–2023, Veronica Berglyd Olsen

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
from PyQt5.QtCore import QObject

from PyQt5.QtGui import QTextDocument
from PyQt5.QtWidgets import QPlainTextDocumentLayout

from novelwriter.gui.dochighlight import GuiDocHighlighter

logger = logging.getLogger(__name__)


class GuiTextDocument(QTextDocument):

    def __init__(self, parent: QObject) -> None:
        super().__init__(parent=parent)

        self._handle = None
        self._syntax = GuiDocHighlighter(self)
        self.setDocumentLayout(QPlainTextDocumentLayout(self))

        logger.debug("Ready: GuiTextDocument")

        return

    def __del__(self):  # pragma: no cover
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
    #  Metods
    ##

    def setTextContent(self, text: str, tHandle: str) -> None:
        """Set the text content of the document."""
        self._syntax.setHandle(tHandle)
        self.setPlainText(text)
        return

# END Class GuiTextDocument
