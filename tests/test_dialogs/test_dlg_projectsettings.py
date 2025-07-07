"""
novelWriter – Project Settings Dialog Class Tester
==================================================

This file is a part of novelWriter
Copyright (C) 2020 Veronica Berglyd Olsen and novelWriter contributors

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

from PyQt6.QtGui import QAction, QColor
from PyQt6.QtWidgets import QColorDialog, QFileDialog

from novelwriter import CONFIG, SHARED
from novelwriter.dialogs.editlabel import GuiEditLabel
from novelwriter.dialogs.projectsettings import GuiProjectSettings
from novelwriter.enum import nwItemType, nwStatusShape
from novelwriter.types import QtAccepted, QtMouseLeft

from tests.mocked import causeOSError
from tests.tools import C, buildTestProject

KEY_DELAY = 1


@pytest.mark.gui
def testDlgProjSettings_Dialog(qtbot, monkeypatch, nwGUI):
    """Test the main dialog class. Saving settings is not tested in this
    test, but are instead tested in the individual tab tests.
    """
    # Block the GUI blocking thread
    monkeypatch.setattr(GuiProjectSettings, "exec", lambda *a: None)
    monkeypatch.setattr(GuiProjectSettings, "result", lambda *a: QtAccepted)

    # Check that we cannot open when there is no project
    nwGUI.mainMenu.aProjectSettings.activate(QAction.ActionEvent.Trigger)
    assert SHARED.findTopLevelWidget(GuiProjectSettings) is None

    # Pretend we have a project
    SHARED.project._valid = True
    SHARED.project.data.setSpellLang("en")

    # Get the dialog object
    nwGUI.mainMenu.aProjectSettings.activate(QAction.ActionEvent.Trigger)
    qtbot.waitUntil(
        lambda: SHARED.findTopLevelWidget(GuiProjectSettings) is not None, timeout=1000
    )

    projSettings = SHARED.findTopLevelWidget(GuiProjectSettings)
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


@pytest.mark.gui
def testDlgProjSettings_SettingsPage(qtbot, monkeypatch, nwGUI, fncPath, projPath, mockRnd):
    """Test the settings page of the dialog."""
    languages = [("en", "English"), ("de", "German")]
    monkeypatch.setattr(SHARED._spelling, "listDictionaries", lambda *a: languages)

    (fncPath / "nw_en.qm").touch()
    (fncPath / "nw_de.qm").touch()
    (fncPath / "project_en.json").touch()
    (fncPath / "project_de.json").touch()
    CONFIG._nwLangPath = fncPath

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
    assert settings.noBackup.isChecked() is False

    settings.projName.setText("Project Name")
    settings.projAuthor.setText("Jane Doe")
    settings.projLang.setCurrentIndex(settings.projLang.findData("de"))
    settings.spellLang.setCurrentIndex(settings.spellLang.findData("de"))
    settings.noBackup.setChecked(True)

    projSettings._doSave()
    assert project.data.name == "Project Name"
    assert project.data.author == "Jane Doe"
    assert project.data.language == "de"
    assert project.data.spellLang == "de"
    assert project.data.doBackup is False

    nwGUI._processProjectSettingsChanges()
    assert nwGUI.windowTitle() == "Project Name - novelWriter"

    # qtbot.stop()


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

    project.tree.refreshAllItems()
    project.countStatus()

    assert [e.count for _, e in project.data.itemStatus.iterItems()] == [2, 0, 2, 1]
    assert [e.count for _, e in project.data.itemImport.iterItems()] == [3, 0, 2, 1]

    # Create Dialog
    projSettings = GuiProjectSettings(nwGUI, GuiProjectSettings.PAGE_STATUS)
    projSettings.show()
    qtbot.addWidget(projSettings)

    # Status Tab
    # ==========

    status = projSettings.statusPage

    assert status.changed is False
    assert status.getNewList() == []
    assert status.listBox.topLevelItemCount() == 4

    # Can't delete the first item (it's in use)
    status.listBox.clearSelection()
    status.listBox.setCurrentItem(status.listBox.topLevelItem(0))
    status.delButton.click()
    assert status.listBox.topLevelItemCount() == 4

    # Can delete the second item
    status.listBox.clearSelection()
    status.listBox.setCurrentItem(status.listBox.topLevelItem(1))
    status.delButton.click()
    assert status.listBox.topLevelItemCount() == 3

    # Add a new item
    with monkeypatch.context() as mp:
        mp.setattr(QColorDialog, "getColor", lambda *a: QColor(20, 30, 40))
        status.addButton.click()
        status.listBox.setCurrentItem(status.listBox.topLevelItem(3))
        status._onNameEdit("Final")
        status.colorButton.click()
        status._selectShape(nwStatusShape.CIRCLE)
        assert status.listBox.topLevelItemCount() == 4

    assert status.changed is True
    update = status.getNewList()

    assert update[0][0] == C.sNew
    assert update[0][1].name == "New"
    assert update[0][1].color.getRgb() == (108, 108, 108, 255)
    assert update[0][1].shape == nwStatusShape.STAR

    assert update[1][0] == C.sDraft
    assert update[1][1].name == "Draft"
    assert update[1][1].color.getRgb() == (163, 156, 52, 255)
    assert update[1][1].shape == nwStatusShape.CIRCLE_T

    assert update[2][0] == C.sFinished
    assert update[2][1].name == "Finished"
    assert update[2][1].color.getRgb() == (41, 102, 41, 255)
    assert update[2][1].shape == nwStatusShape.STAR

    assert update[3][0] is None
    assert update[3][1].name == "Final"
    assert update[3][1].color.getRgb() == (20, 30, 40, 255)
    assert update[3][1].shape == nwStatusShape.CIRCLE

    # Move items, none selected -> no change
    status.listBox.clearSelection()
    status._moveItem(1)
    assert [x[0] for x in status.getNewList()] == [
        C.sNew, C.sDraft, C.sFinished, None
    ]

    # Move items, first selected, move up -> no change
    status.listBox.clearSelection()
    status.listBox.setCurrentItem(status.listBox.topLevelItem(0))
    status._moveItem(-1)
    assert [x[0] for x in status.getNewList()] == [
        C.sNew, C.sDraft, C.sFinished, None
    ]

    # Move items, last selected, move up -> allowed
    status.listBox.clearSelection()
    status.listBox.setCurrentItem(status.listBox.topLevelItem(3))
    status._moveItem(-1)
    assert [x[0] for x in status.getNewList()] == [
        C.sNew, C.sDraft, None, C.sFinished
    ]

    # Move items, same selected, move down -> allowed
    status._moveItem(1)
    assert [x[0] for x in status.getNewList()] == [
        C.sNew, C.sDraft, C.sFinished, None
    ]

    # Importance Tab
    # ==============

    importance = projSettings.importPage
    projSettings._sidebarClicked(GuiProjectSettings.PAGE_IMPORT)

    # Delete unused entry
    importance.listBox.clearSelection()
    importance.listBox.setCurrentItem(importance.listBox.topLevelItem(1))
    importance.delButton.click()
    assert importance.listBox.topLevelItemCount() == 3

    # Add a new entry
    with monkeypatch.context() as mp:
        mp.setattr(QColorDialog, "getColor", lambda *a: QColor(20, 30, 40))
        importance.addButton.click()
        importance.listBox.clearSelection()
        importance.listBox.setCurrentItem(importance.listBox.topLevelItem(3))
        importance._onNameEdit("Final")
        importance.colorButton.click()
        importance._selectShape(nwStatusShape.TRIANGLE)
        assert importance.listBox.topLevelItemCount() == 4

    assert importance.changed is True
    update = importance.getNewList()

    assert update[0][0] == C.iNew
    assert update[0][1].name == "New"
    assert update[0][1].color.getRgb() == (179, 90, 179, 255)
    assert update[0][1].shape == nwStatusShape.SQUARE

    assert update[1][0] == C.iMajor
    assert update[1][1].name == "Major"
    assert update[1][1].color.getRgb() == (179, 90, 179, 255)
    assert update[1][1].shape == nwStatusShape.BLOCK_3

    assert update[2][0] == C.iMain
    assert update[2][1].name == "Main"
    assert update[2][1].color.getRgb() == (179, 90, 179, 255)
    assert update[2][1].shape == nwStatusShape.BLOCK_4

    assert update[3][0] is None
    assert update[3][1].name == "Final"
    assert update[3][1].color.getRgb() == (20, 30, 40, 255)
    assert update[3][1].shape == nwStatusShape.TRIANGLE

    # Check Project
    projSettings._doSave()

    statusItems = dict(project.data.itemStatus.iterItems())
    assert statusItems[C.sNew].name == "New"
    assert statusItems[C.sDraft].name == "Draft"
    assert statusItems[C.sFinished].name == "Finished"
    assert statusItems["s000013"].name == "Final"

    importItems = dict(project.data.itemImport.iterItems())
    assert importItems[C.iNew].name == "New"
    assert importItems[C.iMajor].name == "Major"
    assert importItems[C.iMain].name == "Main"
    assert importItems["i000014"].name == "Final"

    # qtbot.stop()


@pytest.mark.gui
def testDlgProjSettings_StatusImportExport(qtbot, monkeypatch, nwGUI, projPath, mockRnd):
    """Test the status and importance import/export."""
    buildTestProject(nwGUI, projPath)

    # Create Dialog
    projSettings = GuiProjectSettings(nwGUI, GuiProjectSettings.PAGE_STATUS)
    projSettings.show()
    qtbot.addWidget(projSettings)

    status = projSettings.statusPage
    assert status.listBox.topLevelItemCount() == 4
    expFile = projPath / "status.csv"

    # Export Error
    with monkeypatch.context() as mp:
        mp.setattr(QFileDialog, "getSaveFileName", lambda *a, **k: (str(expFile), ""))
        mp.setattr("builtins.open", causeOSError)
        status._exportLabels()

    assert expFile.is_file() is False

    # Export File
    with monkeypatch.context() as mp:
        mp.setattr(QFileDialog, "getSaveFileName", lambda *a, **k: (str(expFile), ""))
        status._exportLabels()

    assert expFile.is_file() is True
    assert expFile.read_text().split() == [
        "STAR,#6c6c6c,New",
        "TRIANGLE,#a62a2d,Note",
        "CIRCLE_T,#a39c34,Draft",
        "STAR,#296629,Finished",
    ]

    # Import Error
    with monkeypatch.context() as mp:
        mp.setattr(QFileDialog, "getOpenFileName", lambda *a, **k: (str(expFile), ""))
        mp.setattr("builtins.open", causeOSError)
        status._importLabels()

    assert status.listBox.topLevelItemCount() == 4
    assert status.changed is False

    # Import File
    with monkeypatch.context() as mp:
        mp.setattr(QFileDialog, "getOpenFileName", lambda *a, **k: (str(expFile), ""))
        status._importLabels()

    assert status.listBox.topLevelItemCount() == 8
    assert status.changed is True

    item4 = status.listBox.topLevelItem(4)
    assert item4 is not None
    assert item4.text(0) == "New"

    item5 = status.listBox.topLevelItem(5)
    assert item5 is not None
    assert item5.text(0) == "Note"

    item6 = status.listBox.topLevelItem(6)
    assert item6 is not None
    assert item6.text(0) == "Draft"

    item7 = status.listBox.topLevelItem(7)
    assert item7 is not None
    assert item7.text(0) == "Finished"


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
    replace._onEntryDeleted()
    assert replace.listBox.topLevelItemCount() == 2

    # Create a new entry
    qtbot.mouseClick(replace.addButton, QtMouseLeft)
    assert replace.listBox.topLevelItemCount() == 3
    assert replace.listBox.topLevelItem(2).text(0) == "<keyword3>"  # type: ignore
    assert replace.listBox.topLevelItem(2).text(1) == ""  # type: ignore

    # Edit the entry
    replace.listBox.setCurrentItem(replace.listBox.topLevelItem(2))
    replace._onKeyEdit("Th is ")
    replace._onValueEdit("With This Stuff ")
    assert replace.listBox.topLevelItem(2).text(0) == "<This>"  # type: ignore
    assert replace.listBox.topLevelItem(2).text(1) == "With This Stuff "  # type: ignore

    # Create a new entry again
    replace.listBox.clearSelection()
    qtbot.mouseClick(replace.addButton, QtMouseLeft)
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
    qtbot.mouseClick(replace.delButton, QtMouseLeft)
    assert replace.listBox.topLevelItemCount() == 3

    # Check Project
    projSettings._doSave()
    assert project.data.autoReplace == {
        "A": "B", "C": "D", "This": "With This Stuff"
    }

    # qtbot.stop()
