"""
novelWriter – Project Settings Dialog Class Tester
==================================================

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

from shutil import copyfile
from tools import cmpFiles, getGuiItem

from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog, QAction, QMessageBox, QColorDialog, QTreeWidgetItem
)

from novelwriter.dialogs import GuiProjectSettings

keyDelay = 2
typeDelay = 1
stepDelay = 20


@pytest.mark.gui
def testDlgProjSettings_Dialog(qtbot, monkeypatch, nwGUI, fncDir, fncProj, outDir, refDir):
    """Test the full project settings dialog.
    """
    projFile = os.path.join(fncProj, "nwProject.nwx")
    testFile = os.path.join(outDir, "guiProjSettings_Dialog_nwProject.nwx")
    compFile = os.path.join(refDir, "guiProjSettings_Dialog_nwProject.nwx")

    # Block message box
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "critical", lambda *a: QMessageBox.Yes)

    # Check that we cannot open when there is no project
    nwGUI.mainMenu.aProjectSettings.activate(QAction.Trigger)
    assert getGuiItem("GuiProjectSettings") is None

    # Create new project
    nwGUI.theProject.projTree.setSeed(42)
    assert nwGUI.newProject({"projPath": fncProj})
    nwGUI.mainConf.backupPath = fncDir

    nwGUI.theProject.setSpellLang("en")
    nwGUI.theProject.setBookAuthors("Jane Smith\nJohn Smith")
    nwGUI.theProject.setAutoReplace({"A": "B", "C": "D"})

    # Get the dialog object
    monkeypatch.setattr(GuiProjectSettings, "exec_", lambda *a: None)
    monkeypatch.setattr(GuiProjectSettings, "result", lambda *a: QDialog.Accepted)
    monkeypatch.setattr(nwGUI.docEditor.spEnchant, "listDictionaries", lambda: [("en", "none")])

    nwGUI.mainMenu.aProjectSettings.activate(QAction.Trigger)
    qtbot.waitUntil(lambda: getGuiItem("GuiProjectSettings") is not None, timeout=1000)

    projEdit = getGuiItem("GuiProjectSettings")
    assert isinstance(projEdit, GuiProjectSettings)
    projEdit.show()
    qtbot.addWidget(projEdit)

    # Settings Tab
    # ============

    assert projEdit.tabMain.editName.text() == "New Project"
    assert projEdit.tabMain.editTitle.text() == ""
    assert projEdit.tabMain.editAuthors.toPlainText() == "Jane Smith\nJohn Smith"
    assert projEdit.tabMain.spellLang.currentData() == "en"
    assert projEdit.tabMain.doBackup.isChecked() is False

    qtbot.wait(stepDelay)
    projEdit.tabMain.editName.setText("")
    for c in "Project Name":
        qtbot.keyClick(projEdit.tabMain.editName, c, delay=typeDelay)
    for c in "Project Title":
        qtbot.keyClick(projEdit.tabMain.editTitle, c, delay=typeDelay)

    projEdit.tabMain.editAuthors.clear()
    for c in "Jane Doe":
        qtbot.keyClick(projEdit.tabMain.editAuthors, c, delay=typeDelay)
    qtbot.keyClick(projEdit.tabMain.editAuthors, Qt.Key_Return, delay=keyDelay)
    for c in "John Doh":
        qtbot.keyClick(projEdit.tabMain.editAuthors, c, delay=typeDelay)
    qtbot.keyClick(projEdit.tabMain.editAuthors, Qt.Key_Return, delay=keyDelay)

    qtbot.wait(stepDelay)
    assert projEdit.tabMain.editName.text() == "Project Name"
    assert projEdit.tabMain.editTitle.text() == "Project Title"
    assert projEdit.tabMain.editAuthors.toPlainText() == "Jane Doe\nJohn Doh\n"

    # Status Tab
    # ==========

    projEdit._tabBox.setCurrentWidget(projEdit.tabStatus)

    assert projEdit.tabStatus.colChanged is False
    assert projEdit.tabStatus.getNewList() is None
    assert projEdit.tabStatus.listBox.topLevelItemCount() == 4

    # Fake drag'n'drop should change changed status
    projEdit.tabStatus._rowsMoved()
    assert projEdit.tabStatus.colChanged is True
    projEdit.tabStatus.colChanged = False

    projEdit.tabStatus.listBox.clearSelection()
    assert projEdit.tabStatus._getSelectedItem() is None
    projEdit.tabStatus.listBox.topLevelItem(0).setSelected(True)
    assert isinstance(projEdit.tabStatus._getSelectedItem(), QTreeWidgetItem)

    # Can't delete the first item (it's in use)
    projEdit.tabStatus.listBox.clearSelection()
    projEdit.tabStatus.listBox.topLevelItem(0).setSelected(True)
    qtbot.mouseClick(projEdit.tabStatus.delButton, Qt.LeftButton)
    assert projEdit.tabStatus.listBox.topLevelItemCount() == 4

    # Can delete the third item
    projEdit.tabStatus.listBox.clearSelection()
    projEdit.tabStatus.listBox.topLevelItem(2).setSelected(True)
    qtbot.mouseClick(projEdit.tabStatus.delButton, Qt.LeftButton)
    assert projEdit.tabStatus.listBox.topLevelItemCount() == 3

    # Add a new item
    monkeypatch.setattr(QColorDialog, "getColor", lambda *a: QColor(20, 30, 40))
    qtbot.mouseClick(projEdit.tabStatus.addButton, Qt.LeftButton)
    projEdit.tabStatus.listBox.topLevelItem(3).setSelected(True)
    for n in range(8):
        qtbot.keyClick(projEdit.tabStatus.editName, Qt.Key_Backspace, delay=typeDelay)
    for c in "Final":
        qtbot.keyClick(projEdit.tabStatus.editName, c, delay=typeDelay)
    qtbot.mouseClick(projEdit.tabStatus.colButton, Qt.LeftButton)
    qtbot.mouseClick(projEdit.tabStatus.saveButton, Qt.LeftButton)
    assert projEdit.tabStatus.listBox.topLevelItemCount() == 4
    qtbot.wait(stepDelay)

    assert projEdit.tabStatus.colChanged is True
    assert projEdit.tabStatus.getNewList() == [
        ("New", 100, 100, 100, "New"),
        ("Note", 200, 50, 0, "Note"),
        ("Finished", 50, 200, 0, "Finished"),
        ("Final", 20, 30, 40, None)
    ]

    # Importance Tab
    # ==============

    projEdit._tabBox.setCurrentWidget(projEdit.tabImport)
    projEdit.tabStatus.listBox.clearSelection()
    projEdit.tabImport.listBox.topLevelItem(3).setSelected(True)
    qtbot.mouseClick(projEdit.tabImport.delButton, Qt.LeftButton)
    qtbot.mouseClick(projEdit.tabImport.addButton, Qt.LeftButton)
    projEdit.tabStatus.listBox.clearSelection()
    projEdit.tabImport.listBox.topLevelItem(3).setSelected(True)
    for n in range(8):
        qtbot.keyClick(projEdit.tabImport.editName, Qt.Key_Backspace, delay=typeDelay)
    for c in "Final":
        qtbot.keyClick(projEdit.tabImport.editName, c, delay=typeDelay)
    qtbot.mouseClick(projEdit.tabImport.saveButton, Qt.LeftButton)
    qtbot.wait(stepDelay)

    # Auto-Replace Tab
    # ================

    qtbot.wait(stepDelay)
    projEdit._tabBox.setCurrentWidget(projEdit.tabReplace)

    assert projEdit.tabReplace.listBox.topLevelItem(0).text(0) == "<A>"
    assert projEdit.tabReplace.listBox.topLevelItem(0).text(1) == "B"
    assert projEdit.tabReplace.listBox.topLevelItem(1).text(0) == "<C>"
    assert projEdit.tabReplace.listBox.topLevelItem(1).text(1) == "D"

    qtbot.mouseClick(projEdit.tabReplace.addButton, Qt.LeftButton)
    projEdit.tabReplace.listBox.topLevelItem(2).setSelected(True)
    projEdit.tabReplace.editKey.setText("")
    for c in "Th is ":
        qtbot.keyClick(projEdit.tabReplace.editKey, c, delay=typeDelay)
    projEdit.tabReplace.editValue.setText("")
    for c in "With This Stuff ":
        qtbot.keyClick(projEdit.tabReplace.editValue, c, delay=typeDelay)
    qtbot.mouseClick(projEdit.tabReplace.saveButton, Qt.LeftButton)

    qtbot.wait(stepDelay)
    projEdit.tabReplace.listBox.clearSelection()
    assert not projEdit.tabReplace._saveEntry()
    assert not projEdit.tabReplace._delEntry()
    qtbot.mouseClick(projEdit.tabReplace.addButton, Qt.LeftButton)

    newIdx = -1
    for i in range(projEdit.tabReplace.listBox.topLevelItemCount()):
        if projEdit.tabReplace.listBox.topLevelItem(i).text(0) == "<keyword4>":
            newIdx = i
            break

    assert newIdx >= 0
    newItem = projEdit.tabReplace.listBox.topLevelItem(newIdx)
    projEdit.tabReplace.listBox.setCurrentItem(newItem)
    qtbot.mouseClick(projEdit.tabReplace.delButton, Qt.LeftButton)
    qtbot.wait(stepDelay)

    # Save & Check
    # ============

    projEdit._doSave()

    # Open again, and check project settings
    nwGUI.mainMenu.aProjectSettings.activate(QAction.Trigger)
    qtbot.waitUntil(lambda: getGuiItem("GuiProjectSettings") is not None, timeout=1000)

    projEdit = getGuiItem("GuiProjectSettings")
    assert isinstance(projEdit, GuiProjectSettings)

    qtbot.addWidget(projEdit)
    assert projEdit.tabMain.editName.text()  == "Project Name"
    assert projEdit.tabMain.editTitle.text() == "Project Title"
    theAuth = projEdit.tabMain.editAuthors.toPlainText().strip().splitlines()
    assert len(theAuth) == 2
    assert theAuth[0] == "Jane Doe"
    assert theAuth[1] == "John Doh"

    projEdit._doClose()
    qtbot.wait(stepDelay)

    assert nwGUI.saveProject()
    qtbot.wait(stepDelay)

    # Check the files
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile, [2, 8, 9, 10])

    # qtbot.stopForInteraction()

# END Test testDlgProjSettings_Dialog
