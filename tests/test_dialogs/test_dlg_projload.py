"""
novelWriter – Project Load Dialog Class Tester
==============================================

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
import os

from tools import getGuiItem

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialogButtonBox, QTreeWidgetItem, QDialog, QAction, QFileDialog,
    QMessageBox
)

from novelwriter.dialogs import GuiProjectLoad

keyDelay = 2
typeDelay = 1
stepDelay = 20


@pytest.mark.gui
def testDlgLoadProject_Main(qtbot, monkeypatch, nwGUI, nwMinimal):
    """Test the load project wizard.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "question", lambda *args: QMessageBox.Yes)

    assert nwGUI.openProject(nwMinimal)
    assert nwGUI.closeProject()

    qtbot.wait(stepDelay)
    monkeypatch.setattr(GuiProjectLoad, "exec_", lambda *a: None)
    monkeypatch.setattr(GuiProjectLoad, "result", lambda *a: QDialog.Accepted)
    nwGUI.mainMenu.aOpenProject.activate(QAction.Trigger)
    qtbot.waitUntil(lambda: getGuiItem("GuiProjectLoad") is not None, timeout=1000)

    nwLoad = getGuiItem("GuiProjectLoad")
    assert isinstance(nwLoad, GuiProjectLoad)
    nwLoad.show()

    qtbot.wait(stepDelay)
    recentCount = nwLoad.listBox.topLevelItemCount()
    assert recentCount > 0

    qtbot.wait(stepDelay)
    selItem = nwLoad.listBox.topLevelItem(0)
    selPath = selItem.data(nwLoad.C_NAME, Qt.UserRole)
    assert isinstance(selItem, QTreeWidgetItem)

    qtbot.wait(stepDelay)
    nwLoad.selPath.setText("")
    nwLoad.listBox.setCurrentItem(selItem)
    nwLoad._doSelectRecent()
    assert nwLoad.selPath.text() == selPath

    qtbot.wait(stepDelay)
    qtbot.mouseClick(nwLoad.buttonBox.button(QDialogButtonBox.Open), Qt.LeftButton)
    assert nwLoad.openPath == selPath
    assert nwLoad.openState == nwLoad.OPEN_STATE

    # Just create a new project load from scratch for the rest of the test
    del nwLoad

    qtbot.wait(stepDelay)
    nwGUI.mainMenu.aOpenProject.activate(QAction.Trigger)
    qtbot.waitUntil(lambda: getGuiItem("GuiProjectLoad") is not None, timeout=1000)

    qtbot.wait(stepDelay)
    nwLoad = getGuiItem("GuiProjectLoad")
    assert isinstance(nwLoad, GuiProjectLoad)
    nwLoad.show()

    qtbot.wait(stepDelay)
    qtbot.mouseClick(nwLoad.buttonBox.button(QDialogButtonBox.Cancel), Qt.LeftButton)
    assert nwLoad.openPath is None
    assert nwLoad.openState == nwLoad.NONE_STATE

    qtbot.wait(stepDelay)
    nwLoad.show()
    qtbot.mouseClick(nwLoad.newButton, Qt.LeftButton)
    assert nwLoad.openPath is None
    assert nwLoad.openState == nwLoad.NEW_STATE

    qtbot.wait(stepDelay)
    nwLoad.show()
    nwLoad._doDeleteRecent()
    assert nwLoad.listBox.topLevelItemCount() == recentCount - 1

    getFile = os.path.join(nwMinimal, "nwProject.nwx")
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *a, **k: (getFile, None))
    qtbot.mouseClick(nwLoad.browseButton, Qt.LeftButton)
    assert nwLoad.openPath == nwMinimal
    assert nwLoad.openState == nwLoad.OPEN_STATE

    nwLoad.close()
    # qtbot.stopForInteraction()

# END Test testDlgLoadProject_Main
