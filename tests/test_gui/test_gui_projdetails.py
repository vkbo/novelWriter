# -*- coding: utf-8 -*-
"""
novelWriter – Project Details Dialog Class Tester
=================================================

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

from tools import getGuiItem

from PyQt5.QtWidgets import QAction, QMessageBox

from nw.gui import GuiProjectDetails
from nw.constants import nwUnicode

keyDelay = 2
typeDelay = 1
stepDelay = 20

@pytest.mark.gui
def testGuiProjDetails_Dialog(qtbot, monkeypatch, nwGUI, nwLipsum):
    """Test the project details dialog.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "question", lambda *args: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "information", lambda *args: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "warning", lambda *args: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "critical", lambda *args: QMessageBox.Yes)

    # Create a project to work on
    assert nwGUI.openProject(nwLipsum)
    assert nwGUI.rebuildIndex(beQuiet=True)
    qtbot.wait(100)

    # Open the Writing Stats dialog
    nwGUI.mainConf.lastPath = ""
    nwGUI.mainMenu.aProjectDetails.activate(QAction.Trigger)
    qtbot.waitUntil(lambda: getGuiItem("GuiProjectDetails") is not None, timeout=1000)

    projDet = getGuiItem("GuiProjectDetails")
    assert isinstance(projDet, GuiProjectDetails)
    qtbot.wait(stepDelay)

    # Overview Page
    # =============

    assert projDet.tabMain.bookTitle.text() == "Lorem Ipsum"
    assert projDet.tabMain.projName.text()[-11:] == "Lorem Ipsum"
    assert projDet.tabMain.bookAuthors.text()[-10:] == "lipsum.com"

    assert projDet.tabMain.wordCountVal.text() == f"{3000:n}"
    assert projDet.tabMain.chapCountVal.text() == f"{3:n}"
    assert projDet.tabMain.sceneCountVal.text() == f"{5:n}"
    assert projDet.tabMain.revCountVal.text() == f"{nwGUI.theProject.saveCount:n}"

    assert projDet.tabMain.projPathVal.text() == nwLipsum

    # Contents Page
    # =============

    tocTab = projDet.tabContents
    tocTree = tocTab.tocTree
    assert tocTree.topLevelItemCount() == 7
    assert tocTree.topLevelItem(0).text(tocTab.C_TITLE) == "Lorem Ipsum"
    assert tocTree.topLevelItem(2).text(tocTab.C_TITLE) == nwUnicode.U_ENSP+"Prologue"
    assert tocTree.topLevelItem(3).text(tocTab.C_TITLE) == "Act One"
    assert tocTree.topLevelItem(4).text(tocTab.C_TITLE) == nwUnicode.U_ENSP+"Chapter One"
    assert tocTree.topLevelItem(5).text(tocTab.C_TITLE) == nwUnicode.U_ENSP+"Chapter Two"
    assert tocTree.topLevelItem(6).text(tocTab.C_TITLE) == "END"

    # Count Pages
    tocTab.wpValue.setValue(100)
    tocTab.dblValue.setChecked(False)
    tocTab._populateTree()

    thePages = [1, 2, 1, 1, 11, 17, 0]
    thePage = [1, 2, 4, 5, 6, 17, 34]
    for i in range(7):
        assert tocTree.topLevelItem(i).text(tocTab.C_PAGES) == f"{thePages[i]:n}"
        assert tocTree.topLevelItem(i).text(tocTab.C_PAGE) == f"{thePage[i]:n}"

    tocTab.dblValue.setChecked(True)
    tocTab._populateTree()

    thePages = [2, 2, 2, 2, 12, 18, 0]
    thePage = [1, 3, 5, 7, 9, 21, 39]
    for i in range(7):
        assert tocTree.topLevelItem(i).text(tocTab.C_PAGES) == f"{thePages[i]:n}"
        assert tocTree.topLevelItem(i).text(tocTab.C_PAGE) == f"{thePage[i]:n}"

    # qtbot.stopForInteraction()

    # Clean Up
    projDet._doClose()
    nwGUI.closeMain()
    monkeypatch.undo()

# END Test testGuiProjDetails_Dialog
