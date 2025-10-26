"""
novelWriter – Main Status Bar Class Tester
==========================================

This file is a part of novelWriter
Copyright (C) 2021 Veronica Berglyd Olsen and novelWriter contributors

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

import time

import pytest

from novelwriter import CONFIG, SHARED

from tests.tools import C, buildTestProject


@pytest.mark.gui
def testGuiStatusBar_Main(qtbot, monkeypatch, nwGUI, projPath, mockRnd):
    """Test the various features of the status bar."""
    buildTestProject(nwGUI, projPath)
    cHandle = SHARED.project.newFile("A Note", C.hCharRoot)
    newDoc = SHARED.project.storage.getDocument(cHandle)
    newDoc.writeDocument("# A Note\n\n")
    nwGUI.rebuildIndex()

    status = nwGUI.mainStatus

    # Reference Time
    refTime = time.time()
    status.setRefTime(refTime)
    assert status._refTime == refTime

    # Project Status
    status.setProjectStatus(None)
    assert status.projIcon.state is None
    status.setProjectStatus(False)
    assert status.projIcon.state is False
    status.setProjectStatus(True)
    assert status.projIcon.state is True

    # Document Status
    status.setDocumentStatus(None)
    assert status.docIcon.state is None
    status.setDocumentStatus(False)
    assert status.docIcon.state is False
    status.setDocumentStatus(True)
    assert status.docIcon.state is True

    # Idle Status
    CONFIG.stopWhenIdle = False
    status.setUserIdle(True)
    status.updateTime()
    assert status._userIdle is False
    assert status.timeText.text() == "00:00:00"

    CONFIG.stopWhenIdle = True
    status.setUserIdle(True)
    status.updateTime(5)
    assert status._userIdle is True
    assert status.timeText.text() != "00:00:00"

    status.setUserIdle(False)
    status.updateTime(5)
    assert status._userIdle is False
    assert status.timeText.text() != "00:00:00"

    # Show/Hide Timer
    assert status.timeText.isVisible() is True
    assert CONFIG.showSessionTime is True
    status._onClickTimerLabel()
    assert status.timeText.isVisible() is False
    assert CONFIG.showSessionTime is False
    status._onClickTimerLabel()
    assert status.timeText.isVisible() is True
    assert CONFIG.showSessionTime is True

    # Language
    status.setLanguage("None", "None")
    assert status.langText.text() == "None"
    status.setLanguage("en", "None")
    assert status.langText.text() == "American English"

    # Project Stats
    CONFIG.incNotesWCount = False
    nwGUI._lastTotalCount = 0
    nwGUI._updateStatusWordCount()
    assert status.statsText.text() == "Words: 9 (+9)"

    # Update again, but through time tick
    with monkeypatch.context() as mp:
        mp.setattr("novelwriter.guimain.time", lambda *a: 50.0)
        CONFIG.incNotesWCount = True
        nwGUI._lastTotalCount = 0
        nwGUI._timeTick()
        assert status.statsText.text() == "Words: 11 (+11)"

    # Switch to character count
    CONFIG.useCharCount = True
    status.initSettings()
    with monkeypatch.context() as mp:
        mp.setattr("novelwriter.guimain.time", lambda *a: 50.0)
        CONFIG.incNotesWCount = True
        nwGUI._lastTotalCount = 0
        nwGUI._timeTick()
        assert status.statsText.text() == "Characters: 46 (+46)"
        CONFIG.incNotesWCount = False
        nwGUI._lastTotalCount = 0
        nwGUI._timeTick()
        assert status.statsText.text() == "Characters: 40 (+40)"

    # qtbot.stop()
