"""
novelWriter – Writing Stats Dialog Class Tester
===============================================

This file is a part of novelWriter
Copyright 2018–2022, Veronica Berglyd Olsen

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

import pytest
import json
import os

from tools import getGuiItem, writeFile
from mock import causeOSError

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAction, QFileDialog, QMessageBox

from novelwriter.tools import GuiWritingStats
from novelwriter.constants import nwFiles

keyDelay = 2
typeDelay = 1
stepDelay = 20


@pytest.mark.gui
def testToolWritingStats_Main(qtbot, monkeypatch, nwGUI, fncDir, fncProj):
    """Test the full writing stats tool.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "information", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "warning", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "critical", lambda *a: QMessageBox.Yes)

    # Create a project to work on
    assert nwGUI.newProject({"projPath": fncProj})
    qtbot.wait(100)
    assert nwGUI.saveProject()
    sessFile = os.path.join(fncProj, "meta", nwFiles.SESS_STATS)

    # Open the Writing Stats dialog
    nwGUI.mainConf.lastPath = ""
    nwGUI.mainMenu.aWritingStats.activate(QAction.Trigger)
    qtbot.waitUntil(lambda: getGuiItem("GuiWritingStats") is not None, timeout=1000)

    sessLog = getGuiItem("GuiWritingStats")
    assert isinstance(sessLog, GuiWritingStats)
    qtbot.wait(stepDelay)

    # Test Loading
    # ============

    # No initial logfile
    assert not os.path.isfile(sessFile)
    assert not sessLog._loadLogFile()

    # Make a test log file
    writeFile(sessFile, (
        "# Offset 123\n"
        "# Start Time         End Time                Novel     Notes      Idle\n"
        "2020-01-01 21:00:00  2020-01-01 21:00:05         6         0\n"
        "2020-01-03 21:00:00  2020-01-03 21:00:15       125         0\n"
        "2020-01-03 21:30:00  2020-01-03 21:30:15       125         5\n"
        "2020-01-06 21:00:00  2020-01-06 21:00:10       125         5\n"
    ))
    assert os.path.isfile(sessFile)
    assert sessLog._loadLogFile()
    assert sessLog.wordOffset == 123
    assert len(sessLog.logData) == 4

    # Make sure a faulty file can still be read
    writeFile(sessFile, (
        "# Offset abc123\n"
        "# Start Time         End Time                Novel     Notes      Idle\n"
        "2020-01-01 21:00:00  2020-01-01 21:00:05         6         0        50\n"
        "2020-01-03 21:00:00  2020-01-03 21:00:15       125         0\n"
        "2020-01-03 21:30:00  2020-01-03 21:30:15       125         5\n"
        "2020-01-06 21:00:00  2020-01-06 21:00:10       125\n"
    ))
    assert sessLog._loadLogFile()
    assert sessLog.wordOffset == 0
    assert len(sessLog.logData) == 3

    # Test Exporting
    # ==============

    writeFile(sessFile, (
        "# Offset 1075\n"
        "# Start Time         End Time                Novel     Notes      Idle\n"
        "2021-01-31 19:00:00  2021-01-31 19:30:00       700       375         0\n"
        "2021-02-01 19:00:00  2021-02-01 19:30:00       700       375        10\n"
        "2021-02-01 20:00:00  2021-02-01 20:30:00       600       275        20\n"
        "2021-02-02 19:00:00  2021-02-02 19:30:00       750       425        30\n"
        "2021-02-02 20:00:00  2021-02-02 20:30:00       690       365        40\n"
        "2021-02-03 19:00:00  2021-02-03 19:30:00       680       355        50\n"
        "2021-02-04 19:00:00  2021-02-04 19:30:00       700       375        60\n"
        "2021-02-05 19:00:00  2021-02-05 19:30:00       500       175        70\n"
        "2021-02-06 19:00:00  2021-02-06 19:30:00       600       275        80\n"
        "2021-02-07 19:00:00  2021-02-07 19:30:00       600       275        90\n"
    ))
    sessLog.populateGUI()

    # Make the saving fail
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *a, **k: ("", ""))
    assert not sessLog._saveData(sessLog.FMT_CSV)
    assert not sessLog._saveData(sessLog.FMT_JSON)
    assert not sessLog._saveData(None)

    # Make the save succeed
    monkeypatch.setattr("os.path.expanduser", lambda *a: fncDir)
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda ss, tt, pp, options: (pp, ""))

    sessLog.listBox.sortByColumn(sessLog.C_TIME, 0)

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
    qtbot.wait(100)

    assert sessLog._saveData(sessLog.FMT_JSON)
    qtbot.wait(100)

    assert nwGUI.mainConf.lastPath == fncDir

    # Check the exported files
    jsonStats = os.path.join(fncDir, "sessionStats.json")
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
    qtbot.mouseClick(sessLog.incNovel, Qt.LeftButton)
    qtbot.wait(stepDelay)
    assert sessLog._saveData(sessLog.FMT_JSON)
    qtbot.wait(stepDelay)

    jsonStats = os.path.join(fncDir, "sessionStats.json")
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
    qtbot.mouseClick(sessLog.incNovel, Qt.LeftButton)
    qtbot.mouseClick(sessLog.incNotes, Qt.LeftButton)
    qtbot.wait(stepDelay)
    assert sessLog._saveData(sessLog.FMT_JSON)
    qtbot.wait(stepDelay)

    jsonStats = os.path.join(fncDir, "sessionStats.json")
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
    qtbot.mouseClick(sessLog.incNotes, Qt.LeftButton)
    qtbot.mouseClick(sessLog.hideNegative, Qt.LeftButton)
    qtbot.wait(stepDelay)
    assert sessLog._saveData(sessLog.FMT_JSON)
    qtbot.wait(stepDelay)

    # qtbot.stopForInteraction()

    jsonStats = os.path.join(fncDir, "sessionStats.json")
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
    qtbot.mouseClick(sessLog.hideNegative, Qt.LeftButton)
    qtbot.mouseClick(sessLog.hideZeros, Qt.LeftButton)
    qtbot.wait(stepDelay)
    assert sessLog._saveData(sessLog.FMT_JSON)
    qtbot.wait(stepDelay)

    jsonStats = os.path.join(fncDir, "sessionStats.json")
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
    qtbot.mouseClick(sessLog.groupByDay, Qt.LeftButton)
    qtbot.wait(stepDelay)
    assert sessLog._saveData(sessLog.FMT_JSON)
    qtbot.wait(stepDelay)

    jsonStats = os.path.join(fncDir, "sessionStats.json")
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
    monkeypatch.setattr("builtins.open", causeOSError)
    assert not sessLog._loadLogFile()
    assert not sessLog._saveData(sessLog.FMT_CSV)

    # qtbot.stopForInteraction()

    sessLog._doClose()
    assert nwGUI.closeProject()
    qtbot.wait(stepDelay)

# END Test testToolWritingStats_Main
