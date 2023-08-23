"""
novelWriter – Main Status Bar Class Tester
==========================================

This file is a part of novelWriter
Copyright 2018–2023, Veronica Berglyd Olsen

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

from novelwriter import CONFIG, SHARED
from novelwriter.extensions.statusled import StatusLED


@pytest.mark.gui
def testGuiStatusBar_Main(qtbot, nwGUI, projPath, mockRnd):
    """Test the the various features of the status bar."""
    buildTestProject(nwGUI, projPath)
    cHandle = SHARED.project.newFile("A Note", C.hCharRoot)
    newDoc = SHARED.project.storage.getDocument(cHandle)
    newDoc.writeDocument("# A Note\n\n")
    nwGUI.projView.projTree.revealNewTreeItem(cHandle)
    nwGUI.rebuildIndex(beQuiet=True)

    # Reference Time
    refTime = time.time()
    nwGUI.mainStatus.setRefTime(refTime)
    assert nwGUI.mainStatus._refTime == refTime

    # Project Status
    nwGUI.mainStatus.setProjectStatus(StatusLED.S_NONE)
    assert nwGUI.mainStatus.projIcon._theCol == nwGUI.mainStatus.projIcon._colNone
    nwGUI.mainStatus.setProjectStatus(StatusLED.S_BAD)
    assert nwGUI.mainStatus.projIcon._theCol == nwGUI.mainStatus.projIcon._colBad
    nwGUI.mainStatus.setProjectStatus(StatusLED.S_GOOD)
    assert nwGUI.mainStatus.projIcon._theCol == nwGUI.mainStatus.projIcon._colGood

    # Document Status
    nwGUI.mainStatus.setDocumentStatus(StatusLED.S_NONE)
    assert nwGUI.mainStatus.docIcon._theCol == nwGUI.mainStatus.docIcon._colNone
    nwGUI.mainStatus.setDocumentStatus(StatusLED.S_BAD)
    assert nwGUI.mainStatus.docIcon._theCol == nwGUI.mainStatus.docIcon._colBad
    nwGUI.mainStatus.setDocumentStatus(StatusLED.S_GOOD)
    assert nwGUI.mainStatus.docIcon._theCol == nwGUI.mainStatus.docIcon._colGood

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
    nwGUI._updateStatusWordCount()
    assert nwGUI.mainStatus.statsText.text() == "Words: 9 (+9)"
    CONFIG.incNotesWCount = True
    nwGUI._updateStatusWordCount()
    assert nwGUI.mainStatus.statsText.text() == "Words: 11 (+11)"

    # qtbot.stop()

# END Test testGuiStatusBar_Init
