"""
novelWriter – GUI Editor Runnables
==================================

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

from PyQt6.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot

from novelwriter.editor.textblock import spellCheckText
from novelwriter.text.counting import standardCounter

if TYPE_CHECKING:
    from novelwriter.editor.editor import GuiDocEditor

logger = logging.getLogger(__name__)


class BackgroundWordCounter(QRunnable):
    """The Off-GUI Thread Word Counter.

    A runnable for the word counter to be run in the thread pool off the
    main GUI thread.
    """

    def __init__(self, docEditor: GuiDocEditor, forSelection: bool = False) -> None:
        super().__init__()
        self._docEditor = docEditor
        self._forSelection = forSelection
        self._isRunning = False
        self.signals = BackgroundWordCounterSignals()

    def isRunning(self) -> bool:
        """Return True if the word counter is already running."""
        return self._isRunning

    @pyqtSlot()
    def run(self) -> None:
        """Overloaded run function for the word counter, forwarding the
        call to the function that does the actual counting.
        """
        self._isRunning = True
        if self._forSelection:
            text = self._docEditor.getSelectedText()
        else:
            text = self._docEditor.getText()

        cC, wC, pC = standardCounter(text)
        self.signals.countsReady.emit(cC, wC, pC)
        self._isRunning = False


class BackgroundWordCounterSignals(QObject):
    """The QRunnable cannot emit a signal, so we need a simple QObject
    to hold the word counter signal.
    """

    countsReady = pyqtSignal(int, int, int)


class BackgroundSpellCheck(QRunnable):
    """The Off-GUI Thread Spell Checker.

    A runnable that spell checks a batch of text block snapshots in the
    thread pool off the main GUI thread. It only receives plain text
    snapshots, and never touches the text document itself.
    """

    def __init__(self, jobId: int, payload: list[tuple[int, str, int, list[int] | None]]) -> None:
        super().__init__()
        self._jobId = jobId
        self._payload = payload
        self.signals = BackgroundSpellCheckSignals()

    @pyqtSlot()
    def run(self) -> None:
        """Spell check the text snapshots and emit the results."""
        self.signals.resultsReady.emit(
            self._jobId,
            [(index, spellCheckText(text, offset, utf16Map)) for index, text, offset, utf16Map in self._payload],
        )


class BackgroundSpellCheckSignals(QObject):
    """The QRunnable cannot emit a signal, so we need a simple QObject
    to hold the spell check result signal.
    """

    resultsReady = pyqtSignal(int, object)
