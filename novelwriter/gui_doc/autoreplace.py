"""
novelWriter – GUI AutoReplace
=============================

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

from novelwriter import CONFIG
from novelwriter.constants import nwUnicode
from novelwriter.types import QtKeepAnchor, QtMoveLeft

if TYPE_CHECKING:
    from PyQt6.QtGui import QTextCursor

logger = logging.getLogger(__name__)


class TextAutoReplace:
    """Encapsulates the editor auto replace feature."""

    __slots__ = (
        "_doPadAfter",
        "_doPadBefore",
        "_padAfter",
        "_padBefore",
        "_padChar",
        "_quoteDC",
        "_quoteDO",
        "_quoteSC",
        "_quoteSO",
        "_replaceDQuote",
        "_replaceDash",
        "_replaceDots",
        "_replaceSQuote",
    )

    def __init__(self) -> None:
        self.initSettings()

    def initSettings(self) -> None:
        """Initialise the auto-replace settings from config."""
        self._quoteSO = CONFIG.fmtSQuoteOpen
        self._quoteSC = CONFIG.fmtSQuoteClose
        self._quoteDO = CONFIG.fmtDQuoteOpen
        self._quoteDC = CONFIG.fmtDQuoteClose

        self._replaceSQuote = CONFIG.doReplaceSQuote
        self._replaceDQuote = CONFIG.doReplaceDQuote
        self._replaceDash = CONFIG.doReplaceDash
        self._replaceDots = CONFIG.doReplaceDots

        self._padChar = nwUnicode.U_THNBSP if CONFIG.fmtPadThin else nwUnicode.U_NBSP
        self._padBefore = CONFIG.fmtPadBefore
        self._padAfter = CONFIG.fmtPadAfter
        self._doPadBefore = bool(CONFIG.fmtPadBefore)
        self._doPadAfter = bool(CONFIG.fmtPadAfter)

    def process(self, text: str, cursor: QTextCursor) -> bool:
        """Auto-replace text elements based on main configuration.
        Returns True if anything was changed.
        """
        aPos = cursor.position()
        bPos = cursor.positionInBlock()
        block = cursor.block()
        length = block.length() - 1
        if length < 1 or bPos - 1 > length:
            return False

        cursor.movePosition(QtMoveLeft, QtKeepAnchor, min(4, bPos))
        last = cursor.selectedText()
        delete, insert = self._determine(last, bPos)

        check = insert
        if (
            self._doPadBefore
            and check
            and check in self._padBefore
            and not (check == ":" and length > 1 and text[0] == "@")
        ):
            delete = max(delete, 1)
            chkPos = len(last) - delete - 1
            if chkPos >= 0 and last[chkPos].isspace():
                # Strip existing space before inserting a new (#1061)
                delete += 1
            insert = self._padChar + insert

        if (
            self._doPadAfter
            and check
            and check in self._padAfter
            and not (check == ":" and length > 1 and text[0] == "@")
        ):
            delete = max(delete, 1)
            insert = insert + self._padChar

        if delete > 0:
            cursor.setPosition(aPos)
            cursor.movePosition(QtMoveLeft, QtKeepAnchor, delete)
            cursor.insertText(insert)
            return True

        return False

    def _determine(self, text: str, pos: int) -> tuple[int, str]:
        """Determine what to replace, if anything."""
        t1 = text[-1:]
        t2 = text[-2:]
        t3 = text[-3:]
        t4 = text[-4:]

        if self._replaceDQuote and t1 == '"':
            # Process Double Quote
            if (
                pos == 1
                or (t2[:1].isspace() and t2.endswith('"'))
                or (pos == 2 and t2 == '>"')
                or (pos == 3 and t3 == '>>"')
                or (pos == 2 and t2 == '_"')
                or (t3[:1].isspace() and t3.endswith('_"'))
                or (pos == 3 and t3 in ('**"', '=="', '~~"'))
                or (t4[:1].isspace() and t4.endswith(('**"', '=="', '~~"')))
            ):
                return 1, self._quoteDO
            else:
                return 1, self._quoteDC

        if self._replaceSQuote and t1 == "'":
            # Process Single Quote
            if (
                pos == 1
                or (t2[:1].isspace() and t2.endswith("'"))
                or (pos == 2 and t2 == ">'")
                or (pos == 3 and t3 == ">>'")
                or (pos == 2 and t2 == "_'")
                or (t3[:1].isspace() and t3.endswith("_'"))
                or (pos == 3 and t3 in ("**'", "=='", "~~'"))
                or (t4[:1].isspace() and t4.endswith(("**'", "=='", "~~'")))
            ):
                return 1, self._quoteSO
            else:
                return 1, self._quoteSC

        if self._replaceDash and t1 == "-":
            # Process Dashes
            if t4 == "----":
                return 4, "\u2015"  # Horizontal bar
            elif t3 == "---":
                return 3, "\u2014"  # Long dash
            elif t2 == "--":
                return 2, "\u2013"  # Short dash
            elif t2 == "\u2013-":
                return 2, "\u2014"  # Long dash
            elif t2 == "\u2014-":
                return 2, "\u2015"  # Horizontal bar

        if self._replaceDots and t3 == "...":
            # Process Dots
            return 3, "\u2026"  # Ellipsis

        if t1 == "\u2028":  # Line separator
            # This resolves issue #1150
            return 1, "\u2029"  # Paragraph separator

        return 0, t1
