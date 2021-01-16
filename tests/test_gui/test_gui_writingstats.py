# -*- coding: utf-8 -*-
"""
novelWriter – Writing Stats Dialog Class Tester
===============================================

This file is a part of novelWriter
Copyright 2018–2021, Veronica Berglyd Olsen

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
from dummy import causeOSError

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAction, QFileDialog, QMessageBox

from nw.gui import GuiWritingStats
from nw.constants import nwFiles

keyDelay = 2
typeDelay = 1
stepDelay = 20

@pytest.mark.gui
def testGuiWritingStats_Dialog(qtbot, monkeypatch, nwGUI, fncDir, fncProj):
    """Test the full writing stats tool.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "question", lambda *args: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "information", lambda *args: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "warning", lambda *args: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "critical", lambda *args: QMessageBox.Yes)

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
        "# Start Time         End Time                Novel     Notes\n"
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
        "# Start Time         End Time                Novel     Notes\n"
        "2020-01-01 21:00:00  2020-01-01 21:00:05         6         0\n"
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
        "# Start Time         End Time                Novel     Notes\n"
        "2020-01-01 21:00:00  2020-01-01 21:00:05         6         0\n"
        "2020-01-03 21:00:00  2020-01-03 21:00:15       125         0\n"
        "2020-01-03 21:30:00  2020-01-03 21:30:15       125         5\n"
        "2020-01-06 21:00:00  2020-01-06 21:00:10       125         5\n"
        "2020-01-08 21:00:00  2020-01-08 21:00:10       120         5\n"
    ))
    sessLog.populateGUI()

    # Make the saving fail
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *args, **kwargs: ("", ""))
    assert not sessLog._saveData(sessLog.FMT_CSV)
    assert not sessLog._saveData(sessLog.FMT_JSON)
    assert not sessLog._saveData(None)

    # Make the save succeed
    monkeypatch.setattr("os.path.expanduser", lambda *args: fncDir)
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda ss, tt, pp, options: (pp, ""))

    assert sessLog._saveData(sessLog.FMT_CSV)
    qtbot.wait(100)

    assert sessLog._saveData(sessLog.FMT_JSON)
    qtbot.wait(100)

    assert nwGUI.mainConf.lastPath == fncDir

    # Check the exported files
    jsonStats = os.path.join(fncDir, "sessionStats.json")
    with open(jsonStats, mode="r", encoding="utf-8") as inFile:
        jsonData = json.load(inFile)

    assert len(jsonData) == 4
    assert jsonData[1]["length"] >= 14.0
    assert jsonData[1]["newWords"] == 119
    assert jsonData[1]["novelWords"] == 125
    assert jsonData[1]["noteWords"] == 0

    # Test Filters
    # ============

    # No Novel Files
    qtbot.mouseClick(sessLog.incNovel, Qt.LeftButton)
    qtbot.wait(stepDelay)
    assert sessLog._saveData(sessLog.FMT_JSON)
    qtbot.wait(stepDelay)

    assert sessLog.novelWords.text() == "{:n}".format(120)
    assert sessLog.notesWords.text() == "{:n}".format(5)
    assert sessLog.totalWords.text() == "{:n}".format(125)

    jsonStats = os.path.join(fncDir, "sessionStats.json")
    with open(jsonStats, mode="r", encoding="utf-8") as inFile:
        jsonData = json.loads(inFile.read())

    assert len(jsonData) == 1
    assert jsonData[0]["length"] >= 14.0
    assert jsonData[0]["newWords"] == 5
    assert jsonData[0]["novelWords"] == 125
    assert jsonData[0]["noteWords"] == 5

    # No Note Files
    qtbot.mouseClick(sessLog.incNovel, Qt.LeftButton)
    qtbot.mouseClick(sessLog.incNotes, Qt.LeftButton)
    qtbot.wait(stepDelay)
    assert sessLog._saveData(sessLog.FMT_JSON)
    qtbot.wait(stepDelay)

    jsonStats = os.path.join(fncDir, "sessionStats.json")
    with open(jsonStats, mode="r", encoding="utf-8") as inFile:
        jsonData = json.load(inFile)

    assert len(jsonData) == 3
    assert jsonData[1]["length"] >= 14.0
    assert jsonData[1]["newWords"] == 119
    assert jsonData[1]["novelWords"] == 125
    assert jsonData[1]["noteWords"] == 0

    # No Negative Entries
    qtbot.mouseClick(sessLog.incNotes, Qt.LeftButton)
    qtbot.mouseClick(sessLog.hideNegative, Qt.LeftButton)
    qtbot.wait(stepDelay)
    assert sessLog._saveData(sessLog.FMT_JSON)
    qtbot.wait(stepDelay)

    jsonStats = os.path.join(fncDir, "sessionStats.json")
    with open(jsonStats, mode="r", encoding="utf-8") as inFile:
        jsonData = json.load(inFile)

    assert len(jsonData) == 3

    # Un-hide Zero Entries
    qtbot.mouseClick(sessLog.hideNegative, Qt.LeftButton)
    qtbot.mouseClick(sessLog.hideZeros, Qt.LeftButton)
    qtbot.wait(stepDelay)
    assert sessLog._saveData(sessLog.FMT_JSON)
    qtbot.wait(stepDelay)

    jsonStats = os.path.join(fncDir, "sessionStats.json")
    with open(jsonStats, mode="r", encoding="utf-8") as inFile:
        jsonData = json.load(inFile)

    assert len(jsonData) == 5

    # Group by Day
    qtbot.mouseClick(sessLog.groupByDay, Qt.LeftButton)
    qtbot.wait(stepDelay)
    assert sessLog._saveData(sessLog.FMT_JSON)
    qtbot.wait(stepDelay)

    jsonStats = os.path.join(fncDir, "sessionStats.json")
    with open(jsonStats, mode="r", encoding="utf-8") as inFile:
        jsonData = json.load(inFile)

    # Check against both 1 and 2 as this can be 2 if test was started just before midnight.
    # A failed test should in any case produce a 4
    assert len(jsonData) == 4

    # IOError
    # =======
    monkeypatch.setattr("builtins.open", causeOSError)
    assert not sessLog._loadLogFile()
    assert not sessLog._saveData(sessLog.FMT_CSV)

    # qtbot.stopForInteraction()

    sessLog._doClose()
    assert nwGUI.closeProject()
    qtbot.wait(stepDelay)

    monkeypatch.undo()

# END Test testGuiWritingStats_Dialog
