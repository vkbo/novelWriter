"""
novelWriter – Project Settings Dialog Class Tester
==================================================

This file is a part of novelWriter
Copyright 2018–2024, Veronica Berglyd Olsen

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
from novelwriter.dialogs.projectsettings import GuiProjectSettings

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
    projSettings.sidebar.button(GuiProjectSettings.PAGE_SETTINGS).click()
    assert projSettings.mainStack.currentWidget() == projSettings.settingsPage

    projSettings.sidebar.button(GuiProjectSettings.PAGE_STATUS).click()
    assert projSettings.mainStack.currentWidget() == projSettings.statusPage

    projSettings.sidebar.button(GuiProjectSettings.PAGE_IMPORT).click()
    assert projSettings.mainStack.currentWidget() == projSettings.importPage

    projSettings.sidebar.button(GuiProjectSettings.PAGE_REPLACE).click()
    assert projSettings.mainStack.currentWidget() == projSettings.replacePage

    # Clean Up
    projSettings.close()
    # qtbot.stop()

# END Test testDlgProjSettings_Dialog


@pytest.mark.gui
def testDlgProjSettings_SettingsPage(qtbot, monkeypatch, nwGUI, fncPath, projPath, mockRnd):
    """Test the settings page of the dialog."""
    languages = [("en", "English"), ("de", "German")]
    monkeypatch.setattr(SHARED._spelling, "listDictionaries", lambda *a: languages)
    monkeypatch.setattr(CONFIG, "listLanguages", lambda *a: languages)

    # Create new project
    buildTestProject(nwGUI, projPath)
    mockRnd.reset()
    CONFIG.setBackupPath(fncPath)

    # Set some values
    project = SHARED.project
    project.data.setLanguage("en")
    project.data.setSpellLang("en")
    project.data.setAuthor("Jane Smith")
    project.data.setAutoReplace({"A": "B", "C": "D"})

    # Create Dialog
    projSettings = GuiProjectSettings(nwGUI, GuiProjectSettings.PAGE_SETTINGS)
    projSettings.show()
    qtbot.addWidget(projSettings)

    # Settings Tab
    settings = projSettings.settingsPage

    assert settings.projName.text() == "New Project"
    assert settings.projAuthor.text() == "Jane Smith"
    assert settings.projLang.currentData() == "en"
    assert settings.spellLang.currentData() == "en"
    assert settings.doBackup.isChecked() is False

    settings.projName.setText("Project Name")
    settings.projAuthor.setText("Jane Doe")
    settings.projLang.setCurrentIndex(settings.projLang.findData("de"))
    settings.spellLang.setCurrentIndex(settings.spellLang.findData("de"))
    settings.doBackup.setChecked(True)

    projSettings._doSave()
    assert project.data.name == "Project Name"
    assert project.data.author == "Jane Doe"
    assert project.data.language == "de"
    assert project.data.spellLang == "de"
    assert project.data.doBackup is False

    nwGUI._processProjectSettingsChanges(False)
    assert nwGUI.windowTitle() == "novelWriter - Project Name"

    # qtbot.stop()

# END Test testDlgProjSettings_SettingsPage


@pytest.mark.gui
def testDlgProjSettings_StatusImport(qtbot, monkeypatch, nwGUI, projPath, mockRnd):
    """Test the status and importance pages of the dialog."""
    monkeypatch.setattr(GuiEditLabel, "getLabel", lambda *a, text: (text, True))
    buildTestProject(nwGUI, projPath)

    # Set some values
    project = SHARED.project
    project.tree[C.hTitlePage].setStatus(C.sFinished)  # type: ignore
    project.tree[C.hChapterDoc].setStatus(C.sDraft)  # type: ignore
    project.tree[C.hSceneDoc].setStatus(C.sDraft)  # type: ignore

    nwGUI.projView.projTree.setSelectedHandle(C.hPlotRoot)
    nwGUI.projView.projTree.newTreeItem(nwItemType.FILE, hLevel=1, isNote=True)
    nwGUI.projView.projTree.setSelectedHandle(C.hCharRoot)
    nwGUI.projView.projTree.newTreeItem(nwItemType.FILE, hLevel=1, isNote=True)
    nwGUI.projView.projTree.setSelectedHandle(C.hWorldRoot)
    nwGUI.projView.projTree.newTreeItem(nwItemType.FILE, hLevel=1, isNote=True)

    hPlotNote = "0000000000010"
    hCharNote = "0000000000011"
    hWorldNote = "0000000000012"

    project.tree[hPlotNote].setImport(C.iMajor)  # type: ignore
    project.tree[hCharNote].setImport(C.iMajor)  # type: ignore
    project.tree[hWorldNote].setImport(C.iMain)  # type: ignore

    nwGUI.rebuildTrees()
    project.countStatus()

    assert [e["count"] for _, e in project.data.itemStatus.items()] == [2, 0, 2, 1]
    assert [e["count"] for _, e in project.data.itemImport.items()] == [3, 0, 2, 1]

    # Create Dialog
    projSettings = GuiProjectSettings(nwGUI, GuiProjectSettings.PAGE_STATUS)
    projSettings.show()
    qtbot.addWidget(projSettings)

    # Status Tab
    # ==========

    status = projSettings.statusPage

    assert status.wasChanged is False
    assert status.getNewList() == ([], [])
    assert status.listBox.topLevelItemCount() == 4

    # Can't delete the first item (it's in use)
    status.listBox.clearSelection()
    status.listBox.setCurrentItem(status.listBox.topLevelItem(0))
    qtbot.mouseClick(status.delButton, Qt.LeftButton)
    assert status.listBox.topLevelItemCount() == 4

    # Can delete the second item
    status.listBox.clearSelection()
    status.listBox.setCurrentItem(status.listBox.topLevelItem(1))
    qtbot.mouseClick(status.delButton, Qt.LeftButton)
    assert status.listBox.topLevelItemCount() == 3

    # Add a new item
    with monkeypatch.context() as mp:
        mp.setattr(QColorDialog, "getColor", lambda *a: QColor(20, 30, 40))
        status.addButton.click()
        status.listBox.setCurrentItem(status.listBox.topLevelItem(3))
        status.editName.setText("Final")
        status.colButton.click()
        status.saveButton.click()
        assert status.listBox.topLevelItemCount() == 4

    assert status.wasChanged is True
    assert status.getNewList() == (
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
    status.listBox.clearSelection()
    status._moveItem(1)
    assert [x["key"] for x in status.getNewList()[0]] == [
        C.sNew, C.sDraft, C.sFinished, None
    ]

    # Move items, first selected, move up -> no change
    status.listBox.clearSelection()
    status.listBox.setCurrentItem(status.listBox.topLevelItem(0))
    status._moveItem(-1)
    assert [x["key"] for x in status.getNewList()[0]] == [
        C.sNew, C.sDraft, C.sFinished, None
    ]

    # Move items, last selected, move up -> allowed
    status.listBox.clearSelection()
    status.listBox.setCurrentItem(status.listBox.topLevelItem(3))
    status._moveItem(-1)
    assert [x["key"] for x in status.getNewList()[0]] == [
        C.sNew, C.sDraft, None, C.sFinished
    ]

    # Move items, same selected, move down -> allowed
    status._moveItem(1)
    assert [x["key"] for x in status.getNewList()[0]] == [
        C.sNew, C.sDraft, C.sFinished, None
    ]

    # Importance Tab
    # ==============

    importance = projSettings.importPage
    projSettings._sidebarClicked(GuiProjectSettings.PAGE_IMPORT)

    # Delete unused entry
    importance.listBox.clearSelection()
    importance.listBox.setCurrentItem(importance.listBox.topLevelItem(1))
    qtbot.mouseClick(importance.delButton, Qt.LeftButton)
    assert importance.listBox.topLevelItemCount() == 3

    # Add a new entry
    with monkeypatch.context() as mp:
        mp.setattr(QColorDialog, "getColor", lambda *a: QColor(20, 30, 40))
        qtbot.mouseClick(importance.addButton, Qt.LeftButton)
        importance.listBox.clearSelection()
        importance.listBox.setCurrentItem(importance.listBox.topLevelItem(3))
        for _ in range(8):
            qtbot.keyClick(importance.editName, Qt.Key_Backspace, delay=KEY_DELAY)
        for c in "Final":
            qtbot.keyClick(importance.editName, c, delay=KEY_DELAY)
        qtbot.mouseClick(importance.colButton, Qt.LeftButton)
        qtbot.mouseClick(importance.saveButton, Qt.LeftButton)
        assert importance.listBox.topLevelItemCount() == 4

    assert importance.wasChanged is True
    assert importance.getNewList() == (
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

    statusItems = dict(project.data.itemStatus.items())
    assert statusItems[C.sNew]["name"] == "New"
    assert statusItems[C.sDraft]["name"] == "Draft"
    assert statusItems[C.sFinished]["name"] == "Finished"
    assert statusItems["s000013"]["name"] == "Final"

    importItems = dict(project.data.itemImport.items())
    assert importItems[C.iNew]["name"] == "New"
    assert importItems[C.iMajor]["name"] == "Major"
    assert importItems[C.iMain]["name"] == "Main"
    assert importItems["i000014"]["name"] == "Final"

    # qtbot.stop()

# END Test testDlgProjSettings_StatusImport


@pytest.mark.gui
def testDlgProjSettings_Replace(qtbot, monkeypatch, nwGUI, projPath, mockRnd):
    """Test the auto-replace page of the dialog."""
    monkeypatch.setattr(GuiEditLabel, "getLabel", lambda *a, text: (text, True))
    buildTestProject(nwGUI, projPath)

    # Set some values
    project = SHARED.project
    project.data.setAutoReplace({
        "A": "B", "C": "D"
    })

    # Create Dialog
    projSettings = GuiProjectSettings(nwGUI, GuiProjectSettings.PAGE_REPLACE)
    projSettings.show()
    qtbot.addWidget(projSettings)

    # Auto-Replace Tab
    # ================

    replace = projSettings.replacePage

    assert replace.listBox.topLevelItem(0).text(0) == "<A>"  # type: ignore
    assert replace.listBox.topLevelItem(0).text(1) == "B"    # type: ignore
    assert replace.listBox.topLevelItem(1).text(0) == "<C>"  # type: ignore
    assert replace.listBox.topLevelItem(1).text(1) == "D"    # type: ignore
    assert replace.listBox.topLevelItemCount() == 2

    # Nothing to save or delete
    replace.listBox.clearSelection()
    replace._saveEntry()
    replace._delEntry()
    assert replace.listBox.topLevelItemCount() == 2

    # Create a new entry
    qtbot.mouseClick(replace.addButton, Qt.LeftButton)
    assert replace.listBox.topLevelItemCount() == 3
    assert replace.listBox.topLevelItem(2).text(0) == "<keyword3>"  # type: ignore
    assert replace.listBox.topLevelItem(2).text(1) == ""  # type: ignore

    # Edit the entry
    replace.listBox.setCurrentItem(replace.listBox.topLevelItem(2))
    replace.editKey.setText("")
    for c in "Th is ":
        qtbot.keyClick(replace.editKey, c, delay=KEY_DELAY)
    replace.editValue.setText("")
    for c in "With This Stuff ":
        qtbot.keyClick(replace.editValue, c, delay=KEY_DELAY)
    qtbot.mouseClick(replace.saveButton, Qt.LeftButton)
    assert replace.listBox.topLevelItem(2).text(0) == "<This>"  # type: ignore
    assert replace.listBox.topLevelItem(2).text(1) == "With This Stuff "  # type: ignore

    # Create a new entry again
    replace.listBox.clearSelection()
    qtbot.mouseClick(replace.addButton, Qt.LeftButton)
    assert replace.listBox.topLevelItemCount() == 4

    # The list is sorted, so we must find it
    newIdx = -1
    for i in range(replace.listBox.topLevelItemCount()):
        if replace.listBox.topLevelItem(i).text(0) == "<keyword4>":  # type: ignore
            newIdx = i
            break
    assert newIdx >= 0

    # Then delete the new item
    replace.listBox.setCurrentItem(replace.listBox.topLevelItem(newIdx))
    qtbot.mouseClick(replace.delButton, Qt.LeftButton)
    assert replace.listBox.topLevelItemCount() == 3

    # Check Project
    projSettings._doSave()
    assert project.data.autoReplace == {
        "A": "B", "C": "D", "This": "With This Stuff"
    }

    # qtbot.stop()

# END Test testDlgProjSettings_Replace
