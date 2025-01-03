"""
novelWriter – SharedData Class Tester
=====================================

This file is a part of novelWriter
Copyright (C) 2023 Veronica Berglyd Olsen

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

from unittest.mock import MagicMock

import pytest

from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QWidget

from novelwriter.core.project import NWProject
from novelwriter.shared import SharedData

from tests.mocked import MockGuiMain, MockTheme
from tests.tools import buildTestProject


@pytest.mark.base
def testBaseSharedData_Init():
    """Test SharedData class initialisation."""
    shared = SharedData()

    # When not initialised, it should raise exceptions
    with pytest.raises(Exception):
        shared.mainGui
    with pytest.raises(Exception):
        shared.theme
    with pytest.raises(Exception):
        shared.project
    with pytest.raises(Exception):
        shared.spelling

    # Create some mock objects
    mockGui = MockGuiMain()
    mockTheme = MockTheme()
    assert mockGui is not mockTheme

    # Properly initialise the class
    shared.initSharedData(mockGui, mockTheme)  # type: ignore

    assert shared.mainGui is mockGui
    assert shared.theme is mockTheme

    assert isinstance(shared.project, NWProject)
    assert shared.hasProject is False
    assert shared.projectIdleTime == 0.0
    assert shared.projectLock is None


@pytest.mark.base
def testBaseSharedData_Functions(monkeypatch):
    """Test SharedData class functions."""
    shared = SharedData()

    # Open URL
    with monkeypatch.context() as mp:
        openUrl = MagicMock()
        mp.setattr(QDesktopServices, "openUrl", openUrl)
        shared.openWebsite("http://www.example.com")
        assert openUrl.called is True
        assert openUrl.call_args[0][0] == QUrl("http://www.example.com")


@pytest.mark.base
def testBaseSharedData_Projects(monkeypatch, caplog, fncPath):
    """Test SharedData handling of projects."""
    project = NWProject()
    buildTestProject(project, fncPath)
    project.closeProject(0.0)  # Clears the lockfile

    shared = SharedData()
    assert shared._project is None

    # Initialise the instance, should create an empty project
    mockGui = MockGuiMain()
    mockTheme = MockTheme()
    shared.initSharedData(mockGui, mockTheme)  # type: ignore
    assert isinstance(shared.project, NWProject)
    assert shared.hasProject is False

    # Load the test project
    assert shared.openProject(fncPath) is True
    assert shared.hasProject is True

    # We cannot open two projects
    caplog.clear()
    assert shared.openProject(fncPath) is False
    assert caplog.messages[-1] == "A project is already open"
    assert shared._idleTime == 0.0

    # Update idle time
    refTime = shared._idleRefTime
    shared.updateIdleTime(refTime + 1.0, False)
    shared.updateIdleTime(refTime + 2.0, True)
    shared.updateIdleTime(refTime + 3.0, False)
    shared.updateIdleTime(refTime + 4.0, True)
    assert round(shared.projectIdleTime) == 2

    # Save project
    assert shared.saveProject() is True

    # Close project
    shared.closeProject()
    assert shared.hasProject is False

    # Cannot save a project after it's been closed
    assert shared.saveProject() is False

    # Check locked project info
    project.openProject(fncPath)  # First open with our independent project instance
    assert shared.hasProject is False
    assert shared.projectLock is None
    assert shared.openProject(fncPath) is False  # Then with our shared instance
    assert shared.hasProject is False
    assert isinstance(shared.projectLock, list)

    # Test browsing for projects
    with monkeypatch.context() as mp:
        mp.setattr(QFileDialog, "getOpenFileName", lambda *a, **k: (a[2], ""))
        assert shared.getProjectPath(QWidget(), fncPath, allowZip=True) == fncPath


@pytest.mark.base
def testBaseSharedData_Alerts(qtbot, monkeypatch, caplog):
    """Test SharedData class alert helper functions."""
    monkeypatch.setattr(QMessageBox, "exec", lambda *a: None)
    monkeypatch.setattr(QMessageBox, "result", lambda *a: QMessageBox.StandardButton.Yes)

    shared = SharedData()

    mockGui = MockGuiMain()
    mockTheme = MockTheme()
    shared.initSharedData(mockGui, mockTheme)  # type: ignore

    assert shared.lastAlert == ""

    # Info box
    caplog.clear()
    shared.info("Hello World", info="foo", details="bar")
    assert shared.lastAlert == "Hello World foo bar"
    assert caplog.text.strip().startswith("INFO")
    assert caplog.text.strip().endswith("Hello World foo bar")

    # Warning box
    caplog.clear()
    shared.warn("Oops!", info="foo", details="bar")
    assert shared.lastAlert == "Oops! foo bar"
    assert caplog.text.strip().startswith("WARNING")
    assert caplog.text.strip().endswith("Oops! foo bar")

    # Error box
    caplog.clear()
    shared.error("Oh noes!", info="foo", details="bar")
    assert shared.lastAlert == "Oh noes! foo bar"
    assert caplog.text.strip().startswith("ERROR")
    assert caplog.text.strip().endswith("Oh noes! foo bar")

    # Error box with exception
    caplog.clear()
    shared.error("Oh noes!", info="foo", details="bar", exc=Exception("Boom!"))
    assert shared.lastAlert == "Oh noes! foo bar"
    assert caplog.text.strip().startswith("ERROR")
    assert caplog.text.strip().endswith("Oh noes! foo bar")

    # Question box
    assert shared.question("Why?") is True
    assert shared.lastAlert == "Why?"
