"""
novelWriter – Main Status Bar Class Tester
==========================================

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

import time
import pytest

from tools import C, buildTestProject

from PyQt5.QtWidgets import QMessageBox

from novelwriter.enum import nwState
from novelwriter.core.document import NWDoc


@pytest.mark.gui
def testGuiStatusBar_Main(qtbot, monkeypatch, nwGUI, fncProj, mockRnd):
    """Test the the various features of the status bar.
    """
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)

    buildTestProject(nwGUI, fncProj)
    cHandle = nwGUI.theProject.newFile("A Note", C.hCharRoot)
    newDoc = NWDoc(nwGUI.theProject, cHandle)
    newDoc.writeDocument("# A Note\n\n")
    nwGUI.projView.projTree.revealNewTreeItem(cHandle)
    nwGUI.rebuildIndex(beQuiet=True)

    # Reference Time
    refTime = time.time()
    nwGUI.mainStatus.setRefTime(refTime)
    assert nwGUI.mainStatus.refTime == refTime

    # Project Status
    nwGUI.mainStatus.setProjectStatus(nwState.NONE)
    assert nwGUI.mainStatus.projIcon._theCol == nwGUI.mainStatus.projIcon._colNone
    nwGUI.mainStatus.setProjectStatus(nwState.BAD)
    assert nwGUI.mainStatus.projIcon._theCol == nwGUI.mainStatus.projIcon._colBad
    nwGUI.mainStatus.setProjectStatus(nwState.GOOD)
    assert nwGUI.mainStatus.projIcon._theCol == nwGUI.mainStatus.projIcon._colGood

    # Document Status
    nwGUI.mainStatus.setDocumentStatus(nwState.NONE)
    assert nwGUI.mainStatus.docIcon._theCol == nwGUI.mainStatus.docIcon._colNone
    nwGUI.mainStatus.setDocumentStatus(nwState.BAD)
    assert nwGUI.mainStatus.docIcon._theCol == nwGUI.mainStatus.docIcon._colBad
    nwGUI.mainStatus.setDocumentStatus(nwState.GOOD)
    assert nwGUI.mainStatus.docIcon._theCol == nwGUI.mainStatus.docIcon._colGood

    # Idle Status
    nwGUI.mainStatus.mainConf.stopWhenIdle = False
    nwGUI.mainStatus.setUserIdle(True)
    nwGUI.mainStatus.updateTime()
    assert nwGUI.mainStatus.userIdle is False
    assert nwGUI.mainStatus.timeText.text() == "00:00:00"

    nwGUI.mainStatus.mainConf.stopWhenIdle = True
    nwGUI.mainStatus.setUserIdle(True)
    nwGUI.mainStatus.updateTime(5)
    assert nwGUI.mainStatus.userIdle is True
    assert nwGUI.mainStatus.timeText.text() != "00:00:00"

    nwGUI.mainStatus.setUserIdle(False)
    nwGUI.mainStatus.updateTime(5)
    assert nwGUI.mainStatus.userIdle is False
    assert nwGUI.mainStatus.timeText.text() != "00:00:00"

    # Language
    nwGUI.mainStatus.setLanguage("None", "None")
    assert nwGUI.mainStatus.langText.text() == "None"
    nwGUI.mainStatus.setLanguage("en", "None")
    assert nwGUI.mainStatus.langText.text() == "American English"

    # Project Stats
    nwGUI.mainStatus.mainConf.incNotesWCount = False
    nwGUI._updateStatusWordCount()
    assert nwGUI.mainStatus.statsText.text() == "Words: 9 (+9)"
    nwGUI.mainStatus.mainConf.incNotesWCount = True
    nwGUI._updateStatusWordCount()
    assert nwGUI.mainStatus.statsText.text() == "Words: 11 (+11)"

    # qtbot.stop()

# END Test testGuiStatusBar_Init
