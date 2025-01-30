"""
novelWriter – Welcome Window Tester
===================================

This file is a part of novelWriter
Copyright (C) 2023 Veronica Berglyd Olsen and novelWriter contributors

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

from datetime import datetime
from pathlib import Path

import pytest

from PyQt5.QtCore import QPoint
from PyQt5.QtWidgets import QAction, QFileDialog, QMenu
from pytestqt.qtbot import QtBot

from novelwriter import CONFIG, SHARED
from novelwriter.constants import nwFiles
from novelwriter.core.projectdata import NWProjectData
from novelwriter.enum import nwItemClass
from novelwriter.tools.welcome import GuiWelcome
from novelwriter.types import QtMouseLeft


@pytest.mark.gui
def testToolWelcome_Main(qtbot: QtBot, monkeypatch, nwGUI, fncPath):
    """Test the main Welcome window."""
    welcome = GuiWelcome(nwGUI)
    with qtbot.waitExposed(welcome):
        # This ensures the paint event is executed
        welcome.show()

    # By default, the project list is shown
    assert welcome.mainStack.currentIndex() == 0

    # Show the new project form
    welcome.btnNew.click()
    assert welcome.mainStack.currentIndex() == 1

    # Revert to project lits
    welcome.btnList.click()
    assert welcome.mainStack.currentIndex() == 0

    # Open a project
    with monkeypatch.context() as mp:
        mp.setattr(SHARED, "getProjectPath", lambda *a, **k: fncPath)
        with qtbot.waitSignal(welcome.openProjectRequest) as signal:
            welcome.btnBrowse.click()
        assert signal.args and signal.args[0] == fncPath

    # qtbot.stop()
    welcome.close()


@pytest.mark.gui
def testToolWelcome_Open(qtbot: QtBot, monkeypatch, nwGUI, fncPath):
    """Test the open tab in the Welcome window."""
    monkeypatch.setattr(QMenu, "exec", lambda *a: None)
    monkeypatch.setattr(QMenu, "setParent", lambda *a: None)

    data1 = NWProjectData(SHARED.project)
    data2 = NWProjectData(SHARED.project)

    data1.setUuid(None)
    data2.setUuid(None)
    data1.setName("Project One")
    data2.setName("Project Two")
    data1.setCurrCounts(12345, 0)
    data2.setCurrCounts(54321, 0)

    CONFIG.recentProjects.update("/stuff/project_one", data1, 1690000000)
    CONFIG.recentProjects.update("/stuff/project_two", data2, 1700000000)
    dateOne = CONFIG.localDate(datetime.fromtimestamp(1700000000))
    dateTwo = CONFIG.localDate(datetime.fromtimestamp(1690000000))

    welcome = GuiWelcome(nwGUI)
    with qtbot.waitExposed(welcome):
        welcome.show()

    assert welcome.mainStack.currentIndex() == 0
    tabOpen = welcome.tabOpen
    listModel = tabOpen.listModel
    vPort = tabOpen.listWidget.viewport()

    posOne = tabOpen.listWidget.rectForIndex(listModel.createIndex(0, 0)).center()
    posTwo = tabOpen.listWidget.rectForIndex(listModel.createIndex(1, 0)).center()

    # Check items, which should be in opposite order
    assert listModel.data(listModel.createIndex(0, 0)) == (
        "Project Two", "/stuff/project_two", f"Last Opened: {dateOne}, Word Count: 54.3\u2009k"
    )
    assert listModel.data(listModel.createIndex(1, 0)) == (
        "Project One", "/stuff/project_one", f"Last Opened: {dateTwo}, Word Count: 12.3\u2009k"
    )

    # Single click item
    assert tabOpen.selectedPath.text() == "Path: /stuff/project_two"
    qtbot.mouseClick(vPort, QtMouseLeft, pos=posTwo, delay=10)
    assert tabOpen.selectedPath.text() == "Path: /stuff/project_one"

    # Double click item
    qtbot.mouseClick(vPort, QtMouseLeft, pos=posTwo, delay=10)
    with monkeypatch.context() as mp:
        mp.setattr(welcome, "close", lambda *a: None)
        with qtbot.waitSignal(welcome.openProjectRequest, timeout=5000) as signal:
            qtbot.mouseDClick(vPort, QtMouseLeft, pos=posTwo, delay=10)
        assert signal.args and signal.args[0] == Path("/stuff/project_one")

    # Press open button
    qtbot.mouseClick(vPort, QtMouseLeft, pos=posTwo, delay=10)
    with monkeypatch.context() as mp:
        mp.setattr(welcome, "close", lambda *a: None)
        with qtbot.waitSignal(welcome.openProjectRequest, timeout=5000) as signal:
            welcome.btnOpen.click()
        assert signal.args and signal.args[0] == Path("/stuff/project_one")

    # Context Menu
    def getMenuForPos(pos: QPoint) -> QMenu | None:
        nonlocal tabOpen
        tabOpen._openContextMenu(pos)
        for obj in tabOpen.children():
            if isinstance(obj, QMenu) and obj.objectName() == "ContextMenu":
                return obj
        return None

    qtbot.mouseClick(vPort, QtMouseLeft, pos=posOne, delay=10)
    ctxMenu = getMenuForPos(posOne)
    assert isinstance(ctxMenu, QMenu)
    assert ctxMenu.actions()[0].text() == "Open Project"
    assert ctxMenu.actions()[1].text() == "Remove Project"

    # Open item from context menu
    with monkeypatch.context() as mp:
        mp.setattr(welcome, "close", lambda *a: None)
        with qtbot.waitSignal(welcome.openProjectRequest, timeout=5000) as signal:
            ctxMenu.actions()[0].activate(QAction.ActionEvent.Trigger)
        assert signal.args and signal.args[0] == Path("/stuff/project_two")

    ctxMenu.setObjectName("")
    ctxMenu.deleteLater()

    # Delete item from context menu
    ctxMenu = getMenuForPos(posOne)
    assert isinstance(ctxMenu, QMenu)
    ctxMenu.actions()[1].activate(QAction.ActionEvent.Trigger)
    assert len(CONFIG.recentProjects.listEntries()) == 1

    ctxMenu.setObjectName("")
    ctxMenu.deleteLater()

    # Check removing entry error handling
    assert listModel.data(listModel.createIndex(1, 0)) == ("", "", "")
    assert listModel.removeEntry(listModel.createIndex(1, 0)) is False
    with monkeypatch.context() as mp:
        mp.setattr(listModel, "data", lambda *a: ("a", "b", "c"))
        assert listModel.removeEntry(listModel.createIndex(1, 0)) is False

    # qtbot.stop()
    welcome.close()


@pytest.mark.gui
def testToolWelcome_New(qtbot: QtBot, caplog, monkeypatch, nwGUI, fncPath):
    """Test the new project tab in the Welcome window."""
    welcome = GuiWelcome(nwGUI)
    with qtbot.waitExposed(welcome):
        welcome.show()

    welcome.btnNew.click()
    assert welcome.mainStack.currentIndex() == 1
    tabNew = welcome.tabNew
    newForm = tabNew.projectForm

    # Populate the path
    with monkeypatch.context() as mp:
        mp.setattr(QFileDialog, "getExistingDirectory", lambda *a, **k: fncPath)
        newForm.browsePath.click()
        assert newForm.projPath.text() == str(fncPath)

    # Turning off root folders should disable notes switch
    newForm.addNotes.setChecked(True)
    newForm.addPlot.setChecked(False)
    newForm.addChar.setChecked(False)
    newForm.addWorld.setChecked(False)
    newForm._syncSwitches()
    assert newForm.addNotes.isChecked() is False

    # Change fill info to sample
    newForm.fillSample.trigger()
    assert newForm._fillMode == newForm.FILL_SAMPLE
    assert newForm.projFill.text() == "Example Project"
    assert newForm.extraWidget.isVisible() is False

    # Change fill info to template
    with monkeypatch.context() as mp:
        mp.setattr(SHARED, "getProjectPath", lambda *a, **k: fncPath)
        newForm.fillCopy.trigger()
        assert newForm._fillMode == newForm.FILL_COPY
        assert newForm.projFill.text() == f"Template: {fncPath}"
        assert newForm.extraWidget.isVisible() is False

    # Change back to fill blank using the menu
    newForm.browseFill.click()
    assert newForm.fillMenu.isVisible() is True
    newForm.fillMenu.actions()[0].activate(QAction.ActionEvent.Trigger)
    newForm.fillMenu.close()
    assert newForm._fillMode == newForm.FILL_BLANK
    assert newForm.projFill.text() == "Fresh Project"
    assert newForm.extraWidget.isVisible() is True

    # Creating a project without a name, pops an error
    caplog.clear()
    welcome.btnCreate.click()
    assert "A project name is required." in caplog.text

    # Set some more values, and extract data
    projPath = fncPath / "Test Project"
    newForm.projName.setText("Test Project")
    newForm.projAuthor.setText("Jane Smith")
    newForm.addPlot.setChecked(True)
    newForm.addChar.setChecked(True)
    newForm.addWorld.setChecked(True)
    newForm.addNotes.setChecked(True)
    newForm.numChapters.setValue(10)
    newForm.numScenes.setValue(6)
    assert newForm.getProjectData() == {
        "name": "Test Project",
        "author": "Jane Smith",
        "path": str(projPath),
        "blank": True,
        "sample": False,
        "template": None,
        "chapters": 10,
        "scenes": 6,
        "roots": [nwItemClass.PLOT, nwItemClass.CHARACTER, nwItemClass.WORLD],
        "notes": True,
    }

    # Create a project with these values
    with qtbot.waitSignal(welcome.openProjectRequest, timeout=5000) as signal:
        welcome.btnCreate.click()
    assert signal.args and signal.args[0] == projPath
    assert (projPath / nwFiles.PROJ_FILE).exists()

    # qtbot.stop()
    welcome.close()
