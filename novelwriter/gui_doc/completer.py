"""
novelWriter – GUI Command Completer
===================================

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

import bisect
import logging

from typing import NamedTuple

from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtGui import QAction, QKeyEvent
from PyQt6.QtWidgets import QMenu, QWidget

from novelwriter import SHARED
from novelwriter.common import qtAddAction
from novelwriter.constants import nwKeyWords
from novelwriter.types import QtKeyDown, QtKeyEnter, QtKeyEscape, QtKeyLeft, QtKeyReturn, QtKeyRight, QtKeyTab, QtKeyUp

logger = logging.getLogger(__name__)


class CompleterAction(NamedTuple):
    """Values needed to complete a completer action."""

    pos: int
    length: int
    value: str


class CommandCompleter(QMenu):
    """GuiWidget: Command Completer Menu.

    This is a context menu with options populated from the user's
    defined tags and keys. It also helps to type the meta data keyword
    on a new line starting with @ or %. The update functions should be
    called on every keystroke on a line starting with @ or %.
    """

    __slots__ = ("_parent",)

    insertText = pyqtSignal(int, int, str)

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)
        self._parent = parent
        self.triggered.connect(self._emitComplete)

    def updateMetaText(self, text: str, pos: int) -> bool:
        """Update the menu options based on the line of meta text."""
        self.clear()
        kw, sep, _ = text.partition(":")
        if pos <= len(kw):
            offset = 0
            length = len(kw.rstrip())
            suffix = "" if sep else ":"
            options = sorted(filter(lambda x: x.startswith(kw.rstrip()), nwKeyWords.VALID_KEYS))
        else:
            status, tBits, tPos = SHARED.project.index.scanThis(text)
            if not status:
                return False
            index = bisect.bisect_right(tPos, pos) - 1
            lookup = tBits[index].lower() if index > 0 else ""
            offset = tPos[index] if lookup else pos
            length = len(lookup)
            suffix = ""
            options = sorted(filter(lambda x: lookup in x.lower(), SHARED.project.index.getKeyWordTags(kw.strip())))[
                :15
            ]

        if not options:
            return False

        for value in options:
            rep = value + suffix
            action = qtAddAction(self, value)
            action.setData(CompleterAction(pos=offset, length=length, value=rep))

        return True

    def updateCommentText(self, text: str, pos: int) -> bool:
        """Update the menu options based on the line of comment text."""
        self.clear()
        cmd, sep, _ = text.partition(":")
        if pos <= len(cmd):
            clean = text[1:].lstrip()[:6].lower()
            if clean[:6] == "story.":
                pre, _, key = cmd.partition(".")
                offset = len(pre) + 1
                length = len(key)
                suffix = "" if sep else ": "
                options = sorted(
                    filter(
                        lambda x: x.startswith(key.rstrip()),
                        SHARED.project.index.getStoryKeys(),
                    )
                )
            elif clean[:5] == "note.":
                pre, _, key = cmd.partition(".")
                offset = len(pre) + 1
                length = len(key)
                suffix = "" if sep else ": "
                options = sorted(
                    filter(
                        lambda x: x.startswith(key.rstrip()),
                        SHARED.project.index.getNoteKeys(),
                    )
                )
            elif pos < 12:
                offset = 0
                length = len(cmd.rstrip())
                suffix = ""
                options = list(
                    filter(
                        lambda x: x.startswith(cmd.rstrip()),
                        ["%Synopsis: ", "%Short: ", "%Story", "%Note"],
                    )
                )
            else:
                return False

            if options:
                for value in options:
                    rep = value + suffix
                    action = qtAddAction(self, rep.rstrip(":. "))
                    action.setData(CompleterAction(pos=offset, length=length, value=rep))
                return True

        return False

    ##
    #  Events
    ##

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Capture keypresses and forward most of them to the editor."""
        key = event.key()
        if key in (QtKeyUp, QtKeyDown):
            # Let the menu handle navigation
            super().keyPressEvent(event)
        elif key in (QtKeyRight, QtKeyReturn, QtKeyEnter, QtKeyTab):
            # Activate the selection if there is one, otherwise close the completer
            if action := self.activeAction():
                action.trigger()
            else:
                self.clear()
                self.close()
        elif key in (QtKeyLeft, QtKeyEscape):
            # Cancel the completer
            self.clear()
            self.close()
        else:
            # Any other keys, send back to the editor
            # Also close to release the event lock before forwarding key press (#2510)
            self.clear()
            self.close()
            self._parent.keyPressEvent(event)

    ##
    #  Internal Slots
    ##

    @pyqtSlot(QAction)
    def _emitComplete(self, action: QAction) -> None:
        """Emit the signal to indicate a selection has been made."""
        if isinstance(data := action.data(), CompleterAction):
            self.insertText.emit(data.pos, data.length, data.value)
