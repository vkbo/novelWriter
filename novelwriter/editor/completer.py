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

from PyQt6.QtCore import QModelIndex, Qt, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import QCompleter, QWidget

from novelwriter import SHARED
from novelwriter.constants import nwKeyWords

logger = logging.getLogger(__name__)


class CompleterAction(NamedTuple):
    """Values needed to complete a completer action."""

    pos: int
    length: int
    value: str


class CommandCompleter(QCompleter):
    """GuiWidget: Command Completer Popup.

    This is a completion popup populated from the user's defined tags
    and keys. It also helps to type the meta data keyword on a new
    line starting with @ or %. The update functions should be called
    on every keystroke on a line starting with @ or %.

    Unlike a QMenu, a QCompleter popup never takes keyboard focus, so
    the editor keeps receiving key events directly while it is open.
    The editor's keyPressEvent is responsible for letting Return,
    Enter, Tab and Escape fall through to this popup instead of
    processing them itself while it is visible.
    """

    __slots__ = ("_model",)

    insertText = pyqtSignal(int, int, str)

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)
        self._model = QStandardItemModel(self)
        self.setModel(self._model)
        self.setWidget(parent)
        self.setCompletionMode(QCompleter.CompletionMode.UnfilteredPopupCompletion)
        self.setMaxVisibleItems(15)
        self.activated[QModelIndex].connect(self._emitComplete)  # type: ignore[index]

    def updateMetaText(self, text: str, pos: int) -> bool:
        """Update the popup options based on the line of meta text."""
        self._model.clear()
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
            self._addOption(value, CompleterAction(pos=offset, length=length, value=value + suffix))

        return True

    def updateCommentText(self, text: str, pos: int) -> bool:
        """Update the popup options based on the line of comment text."""
        self._model.clear()
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
                    self._addOption(rep.rstrip(":. "), CompleterAction(pos=offset, length=length, value=rep))
                return True

        return False

    ##
    #  Internal Functions
    ##

    def _addOption(self, label: str, data: CompleterAction) -> None:
        """Add a single entry to the popup's model."""
        item = QStandardItem(label)
        item.setEditable(False)
        item.setData(data, Qt.ItemDataRole.UserRole)
        self._model.appendRow(item)

    ##
    #  Internal Slots
    ##

    @pyqtSlot(QModelIndex)
    def _emitComplete(self, index: QModelIndex) -> None:
        """Emit the signal to indicate a selection has been made."""
        if isinstance(data := index.data(Qt.ItemDataRole.UserRole), CompleterAction):
            self.insertText.emit(data.pos, data.length, data.value)
