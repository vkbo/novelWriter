"""
novelWriter – Main Status Bar Class Tester
==========================================

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

import time

import pytest

from novelwriter import CONFIG, SHARED
from novelwriter.enum import nwTrinary

from tests.tools import C, buildTestProject


@pytest.mark.gui
def testGuiStatusBar_Main(qtbot, monkeypatch, nwGUI, projPath, mockRnd):
    """Test the the various features of the status bar."""
    buildTestProject(nwGUI, projPath)
    cHandle = SHARED.project.newFile("A Note", C.hCharRoot)
    newDoc = SHARED.project.storage.getDocument(cHandle)
    newDoc.writeDocument("# A Note\n\n")
    nwGUI.rebuildIndex(beQuiet=True)

    status = nwGUI.mainStatus

    # Reference Time
    refTime = time.time()
    status.setRefTime(refTime)
    assert status._refTime == refTime

    # Project Status
    status.setProjectStatus(nwTrinary.NEUTRAL)
    assert status.projIcon.state == nwTrinary.NEUTRAL
    status.setProjectStatus(nwTrinary.NEGATIVE)
    assert status.projIcon.state == nwTrinary.NEGATIVE
    status.setProjectStatus(nwTrinary.POSITIVE)
    assert status.projIcon.state == nwTrinary.POSITIVE

    # Document Status
    status.setDocumentStatus(nwTrinary.NEUTRAL)
    assert status.docIcon.state == nwTrinary.NEUTRAL
    status.setDocumentStatus(nwTrinary.NEGATIVE)
    assert status.docIcon.state == nwTrinary.NEGATIVE
    status.setDocumentStatus(nwTrinary.POSITIVE)
    assert status.docIcon.state == nwTrinary.POSITIVE

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

    # qtbot.stop()
