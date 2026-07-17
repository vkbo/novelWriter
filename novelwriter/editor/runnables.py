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

from novelwriter.editor.textblock import T_TextCheckList, formatCheckText, spellCheckText
from novelwriter.text.counting import standardCounter

if TYPE_CHECKING:
    from novelwriter.editor.editor import GuiDocEditor

logger = logging.getLogger(__name__)

T_TextCheckPayload = list[tuple[int, str, str, int, list[int] | None]]


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


class BackgroundTextCheck(QRunnable):
    """The Off-GUI Thread Text Checker.

    A runnable that spell and/or format checks a batch of text block
    snapshots in the thread pool off the main GUI thread. It only
    receives plain text snapshots, and never touches the text document
    itself.
    """

    def __init__(
        self,
        jobId: int,
        payload: T_TextCheckPayload,
        checkSpell: bool,
        checkFormat: bool,
    ) -> None:
        super().__init__()
        self._jobId = jobId
        self._payload = payload
        self._checkSpell = checkSpell
        self._checkFormat = checkFormat
        self.signals = BackgroundTextCheckSignals()

    @pyqtSlot()
    def run(self) -> None:
        """Spell and format check the text snapshots and emit the results."""
        results: list[tuple[int, T_TextCheckList, T_TextCheckList]] = []
        for index, spellText, formatText, offset, utf16Map in self._payload:
            spellErrors = spellCheckText(spellText, offset, utf16Map) if self._checkSpell else []
            formatErrors = formatCheckText(formatText, offset, utf16Map) if self._checkFormat else []
            results.append((index, spellErrors, formatErrors))
        self.signals.resultsReady.emit(self._jobId, results)


class BackgroundTextCheckSignals(QObject):
    """The QRunnable cannot emit a signal, so we need a simple QObject
    to hold the text check result signal.
    """

    resultsReady = pyqtSignal(int, list)
