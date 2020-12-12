# -*- coding: utf-8 -*-
"""novelWriter Dialog Class Tester
"""

import pytest
import os

from tools import getGuiItem

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialogButtonBox, QTreeWidgetItem, QDialog, QAction, QFileDialog,
    QMessageBox
)

from nw.gui import GuiProjectLoad

keyDelay = 2
typeDelay = 1
stepDelay = 20

@pytest.mark.gui
def testGuiLoadProject_Main(qtbot, monkeypatch, nwGUI, nwMinimal):
    """Test the load project wizard.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "question", lambda *args: QMessageBox.Yes)

    assert nwGUI.openProject(nwMinimal)
    assert nwGUI.closeProject()

    qtbot.wait(stepDelay)
    monkeypatch.setattr(GuiProjectLoad, "exec_", lambda *args: None)
    monkeypatch.setattr(GuiProjectLoad, "result", lambda *args: QDialog.Accepted)
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
    nwLoad._keyPressDelete()
    assert nwLoad.listBox.topLevelItemCount() == recentCount - 1

    getFile = os.path.join(nwMinimal, "nwProject.nwx")
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *args, **kwargs: (getFile, None))
    qtbot.mouseClick(nwLoad.browseButton, Qt.LeftButton)
    assert nwLoad.openPath == nwMinimal
    assert nwLoad.openState == nwLoad.OPEN_STATE

    nwLoad.close()
    # qtbot.stopForInteraction()

# END Test testGuiLoadProject_Main
