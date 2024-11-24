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

    # Reference Time
    refTime = time.time()
    nwGUI.mainStatus.setRefTime(refTime)
    assert nwGUI.mainStatus._refTime == refTime

    # Project Status
    nwGUI.mainStatus.setProjectStatus(nwTrinary.NEUTRAL)
    assert nwGUI.mainStatus.projIcon.state == nwTrinary.NEUTRAL
    nwGUI.mainStatus.setProjectStatus(nwTrinary.NEGATIVE)
    assert nwGUI.mainStatus.projIcon.state == nwTrinary.NEGATIVE
    nwGUI.mainStatus.setProjectStatus(nwTrinary.POSITIVE)
    assert nwGUI.mainStatus.projIcon.state == nwTrinary.POSITIVE

    # Document Status
    nwGUI.mainStatus.setDocumentStatus(nwTrinary.NEUTRAL)
    assert nwGUI.mainStatus.docIcon.state == nwTrinary.NEUTRAL
    nwGUI.mainStatus.setDocumentStatus(nwTrinary.NEGATIVE)
    assert nwGUI.mainStatus.docIcon.state == nwTrinary.NEGATIVE
    nwGUI.mainStatus.setDocumentStatus(nwTrinary.POSITIVE)
    assert nwGUI.mainStatus.docIcon.state == nwTrinary.POSITIVE

    # Idle Status
    CONFIG.stopWhenIdle = False
    nwGUI.mainStatus.setUserIdle(True)
    nwGUI.mainStatus.updateTime()
    assert nwGUI.mainStatus._userIdle is False
    assert nwGUI.mainStatus.timeText.text() == "00:00:00"

    CONFIG.stopWhenIdle = True
    nwGUI.mainStatus.setUserIdle(True)
    nwGUI.mainStatus.updateTime(5)
    assert nwGUI.mainStatus._userIdle is True
    assert nwGUI.mainStatus.timeText.text() != "00:00:00"

    nwGUI.mainStatus.setUserIdle(False)
    nwGUI.mainStatus.updateTime(5)
    assert nwGUI.mainStatus._userIdle is False
    assert nwGUI.mainStatus.timeText.text() != "00:00:00"

    # Language
    nwGUI.mainStatus.setLanguage("None", "None")
    assert nwGUI.mainStatus.langText.text() == "None"
    nwGUI.mainStatus.setLanguage("en", "None")
    assert nwGUI.mainStatus.langText.text() == "American English"

    # Project Stats
    CONFIG.incNotesWCount = False
    nwGUI._lastTotalCount = 0
    nwGUI._updateStatusWordCount()
    assert nwGUI.mainStatus.statsText.text() == "Words: 9 (+9)"

    # Update again, but through time tick
    with monkeypatch.context() as mp:
        mp.setattr("novelwriter.guimain.time", lambda *a: 50.0)
        CONFIG.incNotesWCount = True
        nwGUI._lastTotalCount = 0
        nwGUI._timeTick()
        assert nwGUI.mainStatus.statsText.text() == "Words: 11 (+11)"

    # qtbot.stop()
