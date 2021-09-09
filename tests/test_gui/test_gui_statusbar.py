"""
novelWriter – Main Status Bar Class Tester
==========================================

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

import time
import pytest

from PyQt5.QtCore import QPoint
from PyQt5.QtWidgets import QMessageBox, QMenu

from novelwriter.core import NWDoc
from novelwriter.enum import nwItemClass, nwState


@pytest.mark.gui
def testGuiStatusBar_Main(qtbot, monkeypatch, nwGUI, fncProj):
    """Test the the various features of the status bar.
    """
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)

    nwGUI.theProject.projTree.setSeed(42)
    assert nwGUI.newProject({"projPath": fncProj}) is True
    cHandle = nwGUI.theProject.newFile("A Note", nwItemClass.CHARACTER, "71ee45a3c0db9")
    newDoc = NWDoc(nwGUI.theProject, cHandle)
    newDoc.writeDocument("# A Note\n\n")
    nwGUI.treeView.revealNewTreeItem(cHandle)
    nwGUI.rebuildIndex(beQuiet=True)

    # Reference Time
    refTime = time.time()
    nwGUI.statusBar.setRefTime(refTime)
    assert nwGUI.statusBar.refTime == refTime

    # Project Status
    nwGUI.statusBar.setProjectStatus(nwState.NONE)
    assert nwGUI.statusBar.projIcon._theCol == nwGUI.statusBar.projIcon._colNone
    nwGUI.statusBar.setProjectStatus(nwState.BAD)
    assert nwGUI.statusBar.projIcon._theCol == nwGUI.statusBar.projIcon._colBad
    nwGUI.statusBar.setProjectStatus(nwState.GOOD)
    assert nwGUI.statusBar.projIcon._theCol == nwGUI.statusBar.projIcon._colGood

    # Document Status
    nwGUI.statusBar.setDocumentStatus(nwState.NONE)
    assert nwGUI.statusBar.docIcon._theCol == nwGUI.statusBar.docIcon._colNone
    nwGUI.statusBar.setDocumentStatus(nwState.BAD)
    assert nwGUI.statusBar.docIcon._theCol == nwGUI.statusBar.docIcon._colBad
    nwGUI.statusBar.setDocumentStatus(nwState.GOOD)
    assert nwGUI.statusBar.docIcon._theCol == nwGUI.statusBar.docIcon._colGood

    # Idle Status
    nwGUI.statusBar.mainConf.stopWhenIdle = False
    nwGUI.statusBar.setUserIdle(True)
    nwGUI.statusBar.updateTime()
    assert nwGUI.statusBar.userIdle is False
    assert nwGUI.statusBar.timeText.text() == "00:00:00"

    nwGUI.statusBar.mainConf.stopWhenIdle = True
    nwGUI.statusBar.setUserIdle(True)
    nwGUI.statusBar.updateTime(5)
    assert nwGUI.statusBar.userIdle is True
    assert nwGUI.statusBar.timeText.text() != "00:00:00"

    nwGUI.statusBar.setUserIdle(False)
    nwGUI.statusBar.updateTime(5)
    assert nwGUI.statusBar.userIdle is False
    assert nwGUI.statusBar.timeText.text() != "00:00:00"

    # Language
    nwGUI.statusBar.setLanguage("None", "None")
    assert nwGUI.statusBar.langText.text() == "None"
    nwGUI.statusBar.setLanguage("en", "None")
    assert nwGUI.statusBar.langText.text() == "American English"

    # Project Stats
    nwGUI.statusBar.mainConf.incNotesWCount = True
    nwGUI.statusBar._doToggleIncludeNotes(None)
    assert nwGUI.statusBar.statsText.text() == "Words: 6 (+6)"
    nwGUI.statusBar._doToggleIncludeNotes(None)
    assert nwGUI.statusBar.statsText.text() == "Words: 8 (+8)"

    # Context Menu
    with monkeypatch.context() as mp:
        # Only checks that nothing crashes
        mp.setattr(QMenu, "exec_", lambda *a: None)
        nwGUI.statusBar._openWordCountMenu(QPoint(1, 1))

    # qtbot.stopForInteraction()

# END Test testGuiStatusBar_Init
