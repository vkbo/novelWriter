"""
novelWriter – Writing Stats Dialog Class Tester
===============================================

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

import json

from pathlib import Path

import pytest

from PyQt5.QtWidgets import QAction, QFileDialog

from novelwriter import SHARED
from novelwriter.constants import nwFiles
from novelwriter.tools.writingstats import GuiWritingStats
from novelwriter.types import QtMouseLeft

from tests.mocked import causeOSError
from tests.tools import buildTestProject


@pytest.mark.gui
def testToolWritingStats_Main(qtbot, monkeypatch, nwGUI, projPath, tstPaths):
    """Test the full writing stats tool."""
    # Create a project to work on
    buildTestProject(nwGUI, projPath)
    project = SHARED.project

    qtbot.wait(100)
    assert nwGUI.saveProject()
    sessFile: Path = projPath / "meta" / nwFiles.SESS_FILE

    # Open the Writing Stats dialog
    nwGUI.mainMenu.aWritingStats.activate(QAction.Trigger)
    qtbot.waitUntil(lambda: SHARED.findTopLevelWidget(GuiWritingStats) is not None, timeout=1000)

    sessLog = SHARED.findTopLevelWidget(GuiWritingStats)
    assert isinstance(sessLog, GuiWritingStats)

    # Test Loading
    # ============

    # No initial logfile
    assert not sessFile.is_file()
    assert list(project.session.iterRecords()) == []

    # Make a test log file
    data = [
        project.session.createInitial(123),
        project.session.createRecord("2020-01-01 21:00:00", "2020-01-01 21:00:05", 6, 0, 0),
        project.session.createRecord("2020-01-03 21:00:00", "2020-01-03 21:00:15", 125, 0, 0),
        project.session.createRecord("2020-01-03 21:30:00", "2020-01-03 21:30:15", 125, 5, 0),
        project.session.createRecord("2020-01-06 21:00:00", "2020-01-06 21:00:10", 125, 5, 0),
    ]
    sessFile.write_text("".join(data), encoding="utf-8")
    sessLog._loadLogFile()
    assert sessLog.wordOffset == 123
    assert len(sessLog.logData) == 4

    # Test Exporting
    # ==============

    data = [
        project.session.createInitial(1075),
        project.session.createRecord("2021-01-31 19:00:00", "2021-01-31 19:30:00", 700, 375, 0),
        project.session.createRecord("2021-02-01 19:00:00", "2021-02-01 19:30:00", 700, 375, 10),
        project.session.createRecord("2021-02-01 20:00:00", "2021-02-01 20:30:00", 600, 275, 20),
        project.session.createRecord("2021-02-02 19:00:00", "2021-02-02 19:30:00", 750, 425, 30),
        project.session.createRecord("2021-02-02 20:00:00", "2021-02-02 20:30:00", 690, 365, 40),
        project.session.createRecord("2021-02-03 19:00:00", "2021-02-03 19:30:00", 680, 355, 50),
        project.session.createRecord("2021-02-04 19:00:00", "2021-02-04 19:30:00", 700, 375, 60),
        project.session.createRecord("2021-02-05 19:00:00", "2021-02-05 19:30:00", 500, 175, 70),
        project.session.createRecord("2021-02-06 19:00:00", "2021-02-06 19:30:00", 600, 275, 80),
        project.session.createRecord("2021-02-07 19:00:00", "2021-02-07 19:30:00", 600, 275, 90),
    ]
    sessFile.write_text("".join(data), encoding="utf-8")
    sessLog.populateGUI()

    # Make the saving fail
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *a, **k: ("", ""))
    assert not sessLog._saveData(sessLog.FMT_CSV)
    assert not sessLog._saveData(sessLog.FMT_JSON)
    assert not sessLog._saveData(None)  # type: ignore

    # Make the save succeed
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda ss, tt, pp, options: (pp, ""))
    sessLog.listBox.sortByColumn(sessLog.C_TIME, 0)  # type: ignore

    assert sessLog.novelWords.text() == "{:n}".format(600)
    assert sessLog.notesWords.text() == "{:n}".format(275)
    assert sessLog.totalWords.text() == "{:n}".format(875)

    assert sessLog.listBox.topLevelItem(0).text(sessLog.C_COUNT) == "{:n}".format(1)
    assert sessLog.listBox.topLevelItem(1).text(sessLog.C_COUNT) == "{:n}".format(-200)
    assert sessLog.listBox.topLevelItem(2).text(sessLog.C_COUNT) == "{:n}".format(300)
    assert sessLog.listBox.topLevelItem(3).text(sessLog.C_COUNT) == "{:n}".format(-120)
    assert sessLog.listBox.topLevelItem(4).text(sessLog.C_COUNT) == "{:n}".format(-20)
    assert sessLog.listBox.topLevelItem(5).text(sessLog.C_COUNT) == "{:n}".format(40)
    assert sessLog.listBox.topLevelItem(6).text(sessLog.C_COUNT) == "{:n}".format(-400)
    assert sessLog.listBox.topLevelItem(7).text(sessLog.C_COUNT) == "{:n}".format(200)

    assert sessLog._saveData(sessLog.FMT_CSV)
    assert sessLog._saveData(sessLog.FMT_JSON)

    # Check the exported files
    jsonStats = tstPaths.tmpDir / "sessionStats.json"
    with open(jsonStats, mode="r", encoding="utf-8") as inFile:
        jsonData = json.load(inFile)

    assert jsonData == [
        {
            "date": "2021-01-31 19:00:00", "length": 1800.0,
            "newWords": 1, "novelWords": 700, "noteWords": 375, "idleTime": 0
        }, {
            "date": "2021-02-01 20:00:00", "length": 1800.0,
            "newWords": -200, "novelWords": 600, "noteWords": 275, "idleTime": 20
        }, {
            "date": "2021-02-02 19:00:00", "length": 1800.0,
            "newWords": 300, "novelWords": 750, "noteWords": 425, "idleTime": 30
        }, {
            "date": "2021-02-02 20:00:00", "length": 1800.0,
            "newWords": -120, "novelWords": 690, "noteWords": 365, "idleTime": 40
        }, {
            "date": "2021-02-03 19:00:00", "length": 1800.0,
            "newWords": -20, "novelWords": 680, "noteWords": 355, "idleTime": 50
        }, {
            "date": "2021-02-04 19:00:00", "length": 1800.0,
            "newWords": 40, "novelWords": 700, "noteWords": 375, "idleTime": 60
        }, {
            "date": "2021-02-05 19:00:00", "length": 1800.0,
            "newWords": -400, "novelWords": 500, "noteWords": 175, "idleTime": 70
        }, {
            "date": "2021-02-06 19:00:00", "length": 1800.0,
            "newWords": 200, "novelWords": 600, "noteWords": 275, "idleTime": 80
        }
    ]

    # Test Filters
    # ============

    # No Novel Files
    qtbot.mouseClick(sessLog.incNovel, QtMouseLeft)
    assert sessLog._saveData(sessLog.FMT_JSON)

    jsonStats = tstPaths.tmpDir / "sessionStats.json"
    with open(jsonStats, mode="r", encoding="utf-8") as inFile:
        jsonData = json.loads(inFile.read())

    assert sessLog.listBox.topLevelItem(0).text(sessLog.C_COUNT) == "{:n}".format(1)
    assert sessLog.listBox.topLevelItem(1).text(sessLog.C_COUNT) == "{:n}".format(-100)
    assert sessLog.listBox.topLevelItem(2).text(sessLog.C_COUNT) == "{:n}".format(150)
    assert sessLog.listBox.topLevelItem(3).text(sessLog.C_COUNT) == "{:n}".format(-60)
    assert sessLog.listBox.topLevelItem(4).text(sessLog.C_COUNT) == "{:n}".format(-10)
    assert sessLog.listBox.topLevelItem(5).text(sessLog.C_COUNT) == "{:n}".format(20)
    assert sessLog.listBox.topLevelItem(6).text(sessLog.C_COUNT) == "{:n}".format(-200)
    assert sessLog.listBox.topLevelItem(7).text(sessLog.C_COUNT) == "{:n}".format(100)

    assert jsonData == [
        {
            "date": "2021-01-31 19:00:00", "length": 1800.0,
            "newWords": 1, "novelWords": 700, "noteWords": 375, "idleTime": 0
        }, {
            "date": "2021-02-01 20:00:00", "length": 1800.0,
            "newWords": -100, "novelWords": 600, "noteWords": 275, "idleTime": 20
        }, {
            "date": "2021-02-02 19:00:00", "length": 1800.0,
            "newWords": 150, "novelWords": 750, "noteWords": 425, "idleTime": 30
        }, {
            "date": "2021-02-02 20:00:00", "length": 1800.0,
            "newWords": -60, "novelWords": 690, "noteWords": 365, "idleTime": 40
        }, {
            "date": "2021-02-03 19:00:00", "length": 1800.0,
            "newWords": -10, "novelWords": 680, "noteWords": 355, "idleTime": 50
        }, {
            "date": "2021-02-04 19:00:00", "length": 1800.0,
            "newWords": 20, "novelWords": 700, "noteWords": 375, "idleTime": 60
        }, {
            "date": "2021-02-05 19:00:00", "length": 1800.0,
            "newWords": -200, "novelWords": 500, "noteWords": 175, "idleTime": 70
        }, {
            "date": "2021-02-06 19:00:00", "length": 1800.0,
            "newWords": 100, "novelWords": 600, "noteWords": 275, "idleTime": 80
        }
    ]

    # No Note Files
    qtbot.mouseClick(sessLog.incNovel, QtMouseLeft)
    qtbot.mouseClick(sessLog.incNotes, QtMouseLeft)
    assert sessLog._saveData(sessLog.FMT_JSON)

    jsonStats = tstPaths.tmpDir / "sessionStats.json"
    with open(jsonStats, mode="r", encoding="utf-8") as inFile:
        jsonData = json.load(inFile)

    assert sessLog.listBox.topLevelItem(0).text(sessLog.C_COUNT) == "{:n}".format(1)
    assert sessLog.listBox.topLevelItem(1).text(sessLog.C_COUNT) == "{:n}".format(-100)
    assert sessLog.listBox.topLevelItem(2).text(sessLog.C_COUNT) == "{:n}".format(150)
    assert sessLog.listBox.topLevelItem(3).text(sessLog.C_COUNT) == "{:n}".format(-60)
    assert sessLog.listBox.topLevelItem(4).text(sessLog.C_COUNT) == "{:n}".format(-10)
    assert sessLog.listBox.topLevelItem(5).text(sessLog.C_COUNT) == "{:n}".format(20)
    assert sessLog.listBox.topLevelItem(6).text(sessLog.C_COUNT) == "{:n}".format(-200)
    assert sessLog.listBox.topLevelItem(7).text(sessLog.C_COUNT) == "{:n}".format(100)

    assert jsonData == [
        {
            "date": "2021-01-31 19:00:00", "length": 1800.0,
            "newWords": 1, "novelWords": 700, "noteWords": 375, "idleTime": 0
        }, {
            "date": "2021-02-01 20:00:00", "length": 1800.0,
            "newWords": -100, "novelWords": 600, "noteWords": 275, "idleTime": 20
        }, {
            "date": "2021-02-02 19:00:00", "length": 1800.0,
            "newWords": 150, "novelWords": 750, "noteWords": 425, "idleTime": 30
        }, {
            "date": "2021-02-02 20:00:00", "length": 1800.0,
            "newWords": -60, "novelWords": 690, "noteWords": 365, "idleTime": 40
        }, {
            "date": "2021-02-03 19:00:00", "length": 1800.0,
            "newWords": -10, "novelWords": 680, "noteWords": 355, "idleTime": 50
        }, {
            "date": "2021-02-04 19:00:00", "length": 1800.0,
            "newWords": 20, "novelWords": 700, "noteWords": 375, "idleTime": 60
        }, {
            "date": "2021-02-05 19:00:00", "length": 1800.0,
            "newWords": -200, "novelWords": 500, "noteWords": 175, "idleTime": 70
        }, {
            "date": "2021-02-06 19:00:00", "length": 1800.0,
            "newWords": 100, "novelWords": 600, "noteWords": 275, "idleTime": 80
        }
    ]

    # No Negative Entries
    qtbot.mouseClick(sessLog.incNotes, QtMouseLeft)
    qtbot.mouseClick(sessLog.hideNegative, QtMouseLeft)
    assert sessLog._saveData(sessLog.FMT_JSON)

    # qtbot.stop()

    jsonStats = tstPaths.tmpDir / "sessionStats.json"
    with open(jsonStats, mode="r", encoding="utf-8") as inFile:
        jsonData = json.load(inFile)

    assert sessLog.listBox.topLevelItem(0).text(sessLog.C_COUNT) == "{:n}".format(1)
    assert sessLog.listBox.topLevelItem(1).text(sessLog.C_COUNT) == "{:n}".format(300)
    assert sessLog.listBox.topLevelItem(2).text(sessLog.C_COUNT) == "{:n}".format(40)
    assert sessLog.listBox.topLevelItem(3).text(sessLog.C_COUNT) == "{:n}".format(200)

    assert jsonData == [
        {
            "date": "2021-01-31 19:00:00", "length": 1800.0,
            "newWords": 1, "novelWords": 700, "noteWords": 375, "idleTime": 0
        }, {
            "date": "2021-02-02 19:00:00", "length": 1800.0,
            "newWords": 300, "novelWords": 750, "noteWords": 425, "idleTime": 30
        }, {
            "date": "2021-02-04 19:00:00", "length": 1800.0,
            "newWords": 40, "novelWords": 700, "noteWords": 375, "idleTime": 60
        }, {
            "date": "2021-02-06 19:00:00", "length": 1800.0,
            "newWords": 200, "novelWords": 600, "noteWords": 275, "idleTime": 80
        }
    ]

    # Un-hide Zero Entries
    qtbot.mouseClick(sessLog.hideNegative, QtMouseLeft)
    qtbot.mouseClick(sessLog.hideZeros, QtMouseLeft)
    assert sessLog._saveData(sessLog.FMT_JSON)

    jsonStats = tstPaths.tmpDir / "sessionStats.json"
    with open(jsonStats, mode="r", encoding="utf-8") as inFile:
        jsonData = json.load(inFile)

    assert sessLog.listBox.topLevelItem(0).text(sessLog.C_COUNT) == "{:n}".format(1)
    assert sessLog.listBox.topLevelItem(1).text(sessLog.C_COUNT) == "{:n}".format(0)
    assert sessLog.listBox.topLevelItem(2).text(sessLog.C_COUNT) == "{:n}".format(-200)
    assert sessLog.listBox.topLevelItem(3).text(sessLog.C_COUNT) == "{:n}".format(300)
    assert sessLog.listBox.topLevelItem(4).text(sessLog.C_COUNT) == "{:n}".format(-120)
    assert sessLog.listBox.topLevelItem(5).text(sessLog.C_COUNT) == "{:n}".format(-20)
    assert sessLog.listBox.topLevelItem(6).text(sessLog.C_COUNT) == "{:n}".format(40)
    assert sessLog.listBox.topLevelItem(7).text(sessLog.C_COUNT) == "{:n}".format(-400)
    assert sessLog.listBox.topLevelItem(8).text(sessLog.C_COUNT) == "{:n}".format(200)
    assert sessLog.listBox.topLevelItem(9).text(sessLog.C_COUNT) == "{:n}".format(0)

    assert jsonData == [
        {
            "date": "2021-01-31 19:00:00", "length": 1800.0,
            "newWords": 1, "novelWords": 700, "noteWords": 375, "idleTime": 0
        }, {
            "date": "2021-02-01 19:00:00", "length": 1800.0,
            "newWords": 0, "novelWords": 700, "noteWords": 375, "idleTime": 10
        }, {
            "date": "2021-02-01 20:00:00", "length": 1800.0,
            "newWords": -200, "novelWords": 600, "noteWords": 275, "idleTime": 20
        }, {
            "date": "2021-02-02 19:00:00", "length": 1800.0,
            "newWords": 300, "novelWords": 750, "noteWords": 425, "idleTime": 30
        }, {
            "date": "2021-02-02 20:00:00", "length": 1800.0,
            "newWords": -120, "novelWords": 690, "noteWords": 365, "idleTime": 40
        }, {
            "date": "2021-02-03 19:00:00", "length": 1800.0,
            "newWords": -20, "novelWords": 680, "noteWords": 355, "idleTime": 50
        }, {
            "date": "2021-02-04 19:00:00", "length": 1800.0,
            "newWords": 40, "novelWords": 700, "noteWords": 375, "idleTime": 60
        }, {
            "date": "2021-02-05 19:00:00", "length": 1800.0,
            "newWords": -400, "novelWords": 500, "noteWords": 175, "idleTime": 70
        }, {
            "date": "2021-02-06 19:00:00", "length": 1800.0,
            "newWords": 200, "novelWords": 600, "noteWords": 275, "idleTime": 80
        }, {
            "date": "2021-02-07 19:00:00", "length": 1800.0,
            "newWords": 0, "novelWords": 600, "noteWords": 275, "idleTime": 90
        }
    ]

    # Group by Day
    qtbot.mouseClick(sessLog.groupByDay, QtMouseLeft)
    assert sessLog._saveData(sessLog.FMT_JSON)

    jsonStats = tstPaths.tmpDir / "sessionStats.json"
    with open(jsonStats, mode="r", encoding="utf-8") as inFile:
        jsonData = json.load(inFile)

    assert sessLog.listBox.topLevelItem(0).text(sessLog.C_COUNT) == "{:n}".format(1)
    assert sessLog.listBox.topLevelItem(1).text(sessLog.C_COUNT) == "{:n}".format(-200)
    assert sessLog.listBox.topLevelItem(2).text(sessLog.C_COUNT) == "{:n}".format(180)
    assert sessLog.listBox.topLevelItem(3).text(sessLog.C_COUNT) == "{:n}".format(-20)
    assert sessLog.listBox.topLevelItem(4).text(sessLog.C_COUNT) == "{:n}".format(40)
    assert sessLog.listBox.topLevelItem(5).text(sessLog.C_COUNT) == "{:n}".format(-400)
    assert sessLog.listBox.topLevelItem(6).text(sessLog.C_COUNT) == "{:n}".format(200)
    assert sessLog.listBox.topLevelItem(7).text(sessLog.C_COUNT) == "{:n}".format(0)

    assert jsonData == [
        {
            "date": "2021-01-31", "length": 1800.0,
            "newWords": 1, "novelWords": 700, "noteWords": 375, "idleTime": 0
        }, {
            "date": "2021-02-01", "length": 3600.0,
            "newWords": -200, "novelWords": 600, "noteWords": 275, "idleTime": 30
        }, {
            "date": "2021-02-02", "length": 3600.0,
            "newWords": 180, "novelWords": 690, "noteWords": 365, "idleTime": 70
        }, {
            "date": "2021-02-03", "length": 1800.0,
            "newWords": -20, "novelWords": 680, "noteWords": 355, "idleTime": 50
        }, {
            "date": "2021-02-04", "length": 1800.0,
            "newWords": 40, "novelWords": 700, "noteWords": 375, "idleTime": 60
        }, {
            "date": "2021-02-05", "length": 1800.0,
            "newWords": -400, "novelWords": 500, "noteWords": 175, "idleTime": 70
        }, {
            "date": "2021-02-06", "length": 1800.0,
            "newWords": 200, "novelWords": 600, "noteWords": 275, "idleTime": 80
        }, {
            "date": "2021-02-07", "length": 1800.0,
            "newWords": 0, "novelWords": 600, "noteWords": 275, "idleTime": 90
        }
    ]

    # IOError
    # =======
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        assert not sessLog._loadLogFile()
        assert not sessLog._saveData(sessLog.FMT_CSV)

    # qtbot.stop()

    sessLog._doClose()
    assert nwGUI.closeProject() is True
