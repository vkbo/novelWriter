"""
novelWriter – Project Settings Dialog Class Tester
==================================================

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
from __future__ import annotations

import pytest

from tools import C, getGuiItem, buildTestProject

from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QAction, QColorDialog

from novelwriter import CONFIG, SHARED
from novelwriter.enum import nwItemType
from novelwriter.dialogs.editlabel import GuiEditLabel
from novelwriter.dialogs.projsettings import GuiProjectSettings

KEY_DELAY = 1


@pytest.mark.gui
def testDlgProjSettings_Dialog(qtbot, monkeypatch, nwGUI):
    """Test the main dialog class. Saving settings is not tested in this
    test, but are instead tested in the individual tab tests.
    """
    # Block the GUI blocking thread
    monkeypatch.setattr(GuiProjectSettings, "exec_", lambda *a: None)
    monkeypatch.setattr(GuiProjectSettings, "result", lambda *a: QDialog.Accepted)

    # Check that we cannot open when there is no project
    nwGUI.mainMenu.aProjectSettings.activate(QAction.Trigger)
    assert getGuiItem("GuiProjectSettings") is None

    # Pretend we have a project
    SHARED.project._valid = True
    SHARED.project.data.setSpellLang("en")

    # Get the dialog object
    nwGUI.mainMenu.aProjectSettings.activate(QAction.Trigger)
    qtbot.waitUntil(lambda: getGuiItem("GuiProjectSettings") is not None, timeout=1000)

    projSettings = getGuiItem("GuiProjectSettings")
    assert isinstance(projSettings, GuiProjectSettings)
    projSettings.show()
    qtbot.addWidget(projSettings)

    # Switch Tabs
    projSettings._focusTab(GuiProjectSettings.TAB_REPLACE)
    assert projSettings._tabBox.currentWidget() == projSettings.tabReplace

    projSettings._focusTab(GuiProjectSettings.TAB_IMPORT)
    assert projSettings._tabBox.currentWidget() == projSettings.tabImport

    projSettings._focusTab(GuiProjectSettings.TAB_STATUS)
    assert projSettings._tabBox.currentWidget() == projSettings.tabStatus

    projSettings._focusTab(GuiProjectSettings.TAB_MAIN)
    assert projSettings._tabBox.currentWidget() == projSettings.tabMain

    # Clean Up
    projSettings.close()
    # qtbot.stop()

# END Test testDlgProjSettings_Dialog


@pytest.mark.gui
def testDlgProjSettings_Main(qtbot, monkeypatch, nwGUI, fncPath, projPath, mockRnd):
    """Test the main tab of the project settings dialog."""
    monkeypatch.setattr(SHARED._spelling, "listDictionaries", lambda: [("en", "English [en]")])

    # Create new project
    buildTestProject(nwGUI, projPath)
    mockRnd.reset()
    CONFIG.setBackupPath(fncPath)

    # Set some values
    project = SHARED.project
    project.data.setSpellLang("en")
    project.data.setAuthor("Jane Smith")
    project.data.setAutoReplace({"A": "B", "C": "D"})

    # Create Dialog
    projSettings = GuiProjectSettings(nwGUI, GuiProjectSettings.TAB_MAIN)
    projSettings.show()
    qtbot.addWidget(projSettings)

    # Settings Tab
    # ============

    tabMain = projSettings.tabMain

    assert tabMain.editName.text() == "New Project"
    assert tabMain.editTitle.text() == "New Novel"
    assert tabMain.editAuthor.text() == "Jane Smith"
    assert tabMain.spellLang.currentData() == "en"
    assert tabMain.doBackup.isChecked() is False

    tabMain.editName.setText("")
    for c in "Project Name":
        qtbot.keyClick(tabMain.editName, c, delay=KEY_DELAY)
    tabMain.editTitle.setText("")
    for c in "Project Title":
        qtbot.keyClick(tabMain.editTitle, c, delay=KEY_DELAY)

    tabMain.editAuthor.clear()
    for c in "Jane Doe":
        qtbot.keyClick(tabMain.editAuthor, c, delay=KEY_DELAY)

    assert tabMain.editName.text() == "Project Name"
    assert tabMain.editTitle.text() == "Project Title"
    assert tabMain.editAuthor.text() == "Jane Doe"

    projSettings._doSave()
    assert project.data.name == "Project Name"
    assert project.data.title == "Project Title"
    assert project.data.author == "Jane Doe"

    nwGUI._processProjectSettingsChanges()
    assert nwGUI.windowTitle() == "novelWriter - Project Name"

    # qtbot.stop()

# END Test testDlgProjSettings_Main


@pytest.mark.gui
def testDlgProjSettings_StatusImport(qtbot, monkeypatch, nwGUI, fncPath, projPath, mockRnd):
    """Test the status and importance tabs of the project settings
    dialog.
    """
    monkeypatch.setattr(GuiEditLabel, "getLabel", lambda *a, text: (text, True))
    monkeypatch.setattr(SHARED._spelling, "listDictionaries", lambda: [("en", "English [en]")])

    # Create new project
    mockRnd.reset()
    buildTestProject(nwGUI, projPath)
    CONFIG.setBackupPath(fncPath)

    # Set some values
    theProject = SHARED.project
    theProject.tree[C.hTitlePage].setStatus(C.sFinished)  # type: ignore
    theProject.tree[C.hChapterDoc].setStatus(C.sDraft)  # type: ignore
    theProject.tree[C.hSceneDoc].setStatus(C.sDraft)  # type: ignore

    nwGUI.projView.projTree.setSelectedHandle(C.hPlotRoot)
    nwGUI.projView.projTree.newTreeItem(nwItemType.FILE, hLevel=1, isNote=True)
    nwGUI.projView.projTree.setSelectedHandle(C.hCharRoot)
    nwGUI.projView.projTree.newTreeItem(nwItemType.FILE, hLevel=1, isNote=True)
    nwGUI.projView.projTree.setSelectedHandle(C.hWorldRoot)
    nwGUI.projView.projTree.newTreeItem(nwItemType.FILE, hLevel=1, isNote=True)

    hPlotNote = "0000000000010"
    hCharNote = "0000000000011"
    hWorldNote = "0000000000012"

    theProject.tree[hPlotNote].setImport(C.iMajor)  # type: ignore
    theProject.tree[hCharNote].setImport(C.iMajor)  # type: ignore
    theProject.tree[hWorldNote].setImport(C.iMain)  # type: ignore

    # Create Dialog
    projSettings = GuiProjectSettings(nwGUI, GuiProjectSettings.TAB_STATUS)
    projSettings.show()
    qtbot.addWidget(projSettings)

    # Status Tab
    # ==========

    tabStatus = projSettings.tabStatus

    assert tabStatus.colChanged is False
    assert tabStatus.getNewList() == ([], [])
    assert tabStatus.listBox.topLevelItemCount() == 4

    # Can't delete the first item (it's in use)
    tabStatus.listBox.clearSelection()
    tabStatus.listBox.setCurrentItem(tabStatus.listBox.topLevelItem(0))
    qtbot.mouseClick(tabStatus.delButton, Qt.LeftButton)
    assert tabStatus.listBox.topLevelItemCount() == 4

    # Can delete the second item
    tabStatus.listBox.clearSelection()
    tabStatus.listBox.setCurrentItem(tabStatus.listBox.topLevelItem(1))
    qtbot.mouseClick(tabStatus.delButton, Qt.LeftButton)
    assert tabStatus.listBox.topLevelItemCount() == 3

    # Add a new item
    with monkeypatch.context() as mp:
        mp.setattr(QColorDialog, "getColor", lambda *a: QColor(20, 30, 40))
        qtbot.mouseClick(tabStatus.addButton, Qt.LeftButton)
        tabStatus.listBox.setCurrentItem(tabStatus.listBox.topLevelItem(3))
        for _ in range(8):
            qtbot.keyClick(tabStatus.editName, Qt.Key_Backspace, delay=KEY_DELAY)
        for c in "Final":
            qtbot.keyClick(tabStatus.editName, c, delay=KEY_DELAY)
        qtbot.mouseClick(tabStatus.colButton, Qt.LeftButton)
        qtbot.mouseClick(tabStatus.saveButton, Qt.LeftButton)
        assert tabStatus.listBox.topLevelItemCount() == 4

    assert tabStatus.colChanged is True
    assert tabStatus.getNewList() == (
        [
            {
                "key": C.sNew,
                "name": "New",
                "cols": (100, 100, 100)
            }, {
                "key": C.sDraft,
                "name": "Draft",
                "cols": (200, 150, 0)
            }, {
                "key": C.sFinished,
                "name": "Finished",
                "cols": (50, 200, 0)
            }, {
                "key": None,
                "name": "Final",
                "cols": (20, 30, 40)
            }
        ], [
            C.sNote  # Deleted item
        ]
    )

    # Move items, none selected -> no change
    tabStatus.listBox.clearSelection()
    tabStatus._moveItem(1)
    assert [x["key"] for x in tabStatus.getNewList()[0]] == [
        C.sNew, C.sDraft, C.sFinished, None
    ]

    # Move items, first selected, move up -> no change
    tabStatus.listBox.clearSelection()
    tabStatus.listBox.setCurrentItem(tabStatus.listBox.topLevelItem(0))
    tabStatus._moveItem(-1)
    assert [x["key"] for x in tabStatus.getNewList()[0]] == [
        C.sNew, C.sDraft, C.sFinished, None
    ]

    # Move items, last selected, move up -> allowed
    tabStatus.listBox.clearSelection()
    tabStatus.listBox.setCurrentItem(tabStatus.listBox.topLevelItem(3))
    tabStatus._moveItem(-1)
    assert [x["key"] for x in tabStatus.getNewList()[0]] == [
        C.sNew, C.sDraft, None, C.sFinished
    ]

    # Move items, same selected, move down -> allowed
    tabStatus._moveItem(1)
    assert [x["key"] for x in tabStatus.getNewList()[0]] == [
        C.sNew, C.sDraft, C.sFinished, None
    ]

    # Importance Tab
    # ==============

    tabImport = projSettings.tabImport
    projSettings._focusTab(GuiProjectSettings.TAB_IMPORT)

    # Delete unused entry
    tabImport.listBox.clearSelection()
    tabImport.listBox.setCurrentItem(tabImport.listBox.topLevelItem(1))
    qtbot.mouseClick(tabImport.delButton, Qt.LeftButton)
    assert tabImport.listBox.topLevelItemCount() == 3

    # Add a new entry
    with monkeypatch.context() as mp:
        mp.setattr(QColorDialog, "getColor", lambda *a: QColor(20, 30, 40))
        qtbot.mouseClick(tabImport.addButton, Qt.LeftButton)
        tabImport.listBox.clearSelection()
        tabImport.listBox.setCurrentItem(tabImport.listBox.topLevelItem(3))
        for _ in range(8):
            qtbot.keyClick(tabImport.editName, Qt.Key_Backspace, delay=KEY_DELAY)
        for c in "Final":
            qtbot.keyClick(tabImport.editName, c, delay=KEY_DELAY)
        qtbot.mouseClick(tabImport.colButton, Qt.LeftButton)
        qtbot.mouseClick(tabImport.saveButton, Qt.LeftButton)
        assert tabImport.listBox.topLevelItemCount() == 4

    assert tabImport.colChanged is True
    assert tabImport.getNewList() == (
        [
            {
                "key": C.iNew,
                "name": "New",
                "cols": (100, 100, 100)
            }, {
                "key": C.iMajor,
                "name": "Major",
                "cols": (200, 150, 0)
            }, {
                "key": C.iMain,
                "name": "Main",
                "cols": (50, 200, 0)
            }, {
                "key": None,
                "name": "Final",
                "cols": (20, 30, 40)
            }
        ], [
            C.iMinor  # Deleted item
        ]
    )

    # Check Project
    projSettings._doSave()

    statusItems = dict(theProject.data.itemStatus.items())
    assert statusItems[C.sNew]["name"] == "New"
    assert statusItems[C.sDraft]["name"] == "Draft"
    assert statusItems[C.sFinished]["name"] == "Finished"
    assert statusItems["s000013"]["name"] == "Final"

    importItems = dict(theProject.data.itemImport.items())
    assert importItems[C.iNew]["name"] == "New"
    assert importItems[C.iMajor]["name"] == "Major"
    assert importItems[C.iMain]["name"] == "Main"
    assert importItems["i000014"]["name"] == "Final"

    # qtbot.stop()

# END Test testDlgProjSettings_StatusImport


@pytest.mark.gui
def testDlgProjSettings_Replace(qtbot, monkeypatch, nwGUI, fncPath, projPath, mockRnd):
    """Test the auto-replace tab of the project settings dialog."""
    monkeypatch.setattr(GuiEditLabel, "getLabel", lambda *a, text: (text, True))
    monkeypatch.setattr(SHARED._spelling, "listDictionaries", lambda: [("en", "English [en]")])

    # Create new project
    mockRnd.reset()
    buildTestProject(nwGUI, projPath)
    CONFIG.setBackupPath(fncPath)

    # Set some values
    theProject = SHARED.project
    theProject.data.setAutoReplace({
        "A": "B", "C": "D"
    })

    # Create Dialog
    projSettings = GuiProjectSettings(nwGUI, GuiProjectSettings.TAB_REPLACE)
    projSettings.show()
    qtbot.addWidget(projSettings)

    # Auto-Replace Tab
    # ================

    tabReplace = projSettings.tabReplace

    assert tabReplace.listBox.topLevelItem(0).text(0) == "<A>"  # type: ignore
    assert tabReplace.listBox.topLevelItem(0).text(1) == "B"    # type: ignore
    assert tabReplace.listBox.topLevelItem(1).text(0) == "<C>"  # type: ignore
    assert tabReplace.listBox.topLevelItem(1).text(1) == "D"    # type: ignore
    assert tabReplace.listBox.topLevelItemCount() == 2

    # Nothing to save or delete
    tabReplace.listBox.clearSelection()
    tabReplace._saveEntry()
    tabReplace._delEntry()
    assert tabReplace.listBox.topLevelItemCount() == 2

    # Create a new entry
    qtbot.mouseClick(tabReplace.addButton, Qt.LeftButton)
    assert tabReplace.listBox.topLevelItemCount() == 3
    assert tabReplace.listBox.topLevelItem(2).text(0) == "<keyword3>"  # type: ignore
    assert tabReplace.listBox.topLevelItem(2).text(1) == ""  # type: ignore

    # Edit the entry
    tabReplace.listBox.setCurrentItem(tabReplace.listBox.topLevelItem(2))
    tabReplace.editKey.setText("")
    for c in "Th is ":
        qtbot.keyClick(tabReplace.editKey, c, delay=KEY_DELAY)
    tabReplace.editValue.setText("")
    for c in "With This Stuff ":
        qtbot.keyClick(tabReplace.editValue, c, delay=KEY_DELAY)
    qtbot.mouseClick(tabReplace.saveButton, Qt.LeftButton)
    assert tabReplace.listBox.topLevelItem(2).text(0) == "<This>"  # type: ignore
    assert tabReplace.listBox.topLevelItem(2).text(1) == "With This Stuff "  # type: ignore

    # Create a new entry again
    tabReplace.listBox.clearSelection()
    qtbot.mouseClick(tabReplace.addButton, Qt.LeftButton)
    assert tabReplace.listBox.topLevelItemCount() == 4

    # The list is sorted, so we must find it
    newIdx = -1
    for i in range(tabReplace.listBox.topLevelItemCount()):
        if tabReplace.listBox.topLevelItem(i).text(0) == "<keyword4>":  # type: ignore
            newIdx = i
            break
    assert newIdx >= 0

    # Then delete the new item
    tabReplace.listBox.setCurrentItem(tabReplace.listBox.topLevelItem(newIdx))
    qtbot.mouseClick(tabReplace.delButton, Qt.LeftButton)
    assert tabReplace.listBox.topLevelItemCount() == 3

    # Check Project
    projSettings._doSave()
    assert theProject.data.autoReplace == {
        "A": "B", "C": "D", "This": "With This Stuff"
    }

    # qtbot.stop()

# END Test testDlgProjSettings_Replace
