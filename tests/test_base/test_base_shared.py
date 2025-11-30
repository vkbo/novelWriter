"""
novelWriter – SharedData Class Tester
=====================================

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
"""  # noqa
from __future__ import annotations

import sys

from unittest.mock import MagicMock

import pytest

from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QFileDialog, QWidget

from novelwriter.core.project import NWProject
from novelwriter.shared import SharedData, _GuiAlert

from tests.mocked import MockGuiMain, MockTheme
from tests.tools import buildTestProject


@pytest.mark.base
def testBaseSharedData_Init():
    """Test SharedData class initialisation."""
    shared = SharedData()

    # When not initialised, it should raise exceptions
    with pytest.raises(RuntimeError):
        _ = shared.mainGui
    with pytest.raises(RuntimeError):
        _ = shared.theme
    with pytest.raises(RuntimeError):
        _ = shared.project
    with pytest.raises(RuntimeError):
        _ = shared.spelling

    # Create some mock objects
    mockGui = MockGuiMain()
    mockTheme = MockTheme()
    assert mockGui is not mockTheme

    # Properly initialise the class
    shared.initTheme(mockTheme)  # type: ignore
    shared.initSharedData(mockGui)  # type: ignore

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
    shared.initTheme(mockTheme)  # type: ignore
    shared.initSharedData(mockGui)  # type: ignore
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
def testBaseSharedData_Alerts(qtbot, monkeypatch, caplog, mockGUI):
    """Test SharedData class alert helper functions."""
    monkeypatch.setattr(_GuiAlert, "exec", lambda *a: None)
    monkeypatch.setattr(_GuiAlert, "finalState", True)

    shared = SharedData()

    mockGui = MockGuiMain()
    mockTheme = MockTheme()
    shared.initTheme(mockTheme)  # type: ignore
    shared.initSharedData(mockGui)  # type: ignore

    assert shared.lastAlert == []

    # Info box
    caplog.clear()
    shared.info("Hello World", info="foo", details="bar")
    assert shared.lastAlert == ["Hello World", "foo", "bar"]
    assert caplog.text.strip().startswith("INFO")
    assert caplog.text.strip().endswith("bar")

    # Warning box
    caplog.clear()
    shared.warn("Oops!", info="foo", details="bar")
    assert shared.lastAlert == ["Oops!", "foo", "bar"]
    assert caplog.text.strip().startswith("WARNING")
    assert caplog.text.strip().endswith("bar")

    # Error box
    caplog.clear()
    shared.error("Oh noes!", info="foo", details="bar")
    assert shared.lastAlert == ["Oh noes!", "foo", "bar"]
    assert caplog.text.strip().startswith("ERROR")
    assert caplog.text.strip().endswith("bar")

    # Error box with exception
    caplog.clear()
    shared.error("Oh noes!", info="foo", details="bar", exc=Exception("Boom!"))
    assert shared.lastAlert == ["Oh noes!", "foo", "bar"]
    assert caplog.text.strip().startswith("ERROR")
    assert caplog.text.strip().endswith("bar")

    # Question box
    assert shared.question("Why?") is True
    assert shared.lastAlert == ["Why?"]


@pytest.mark.base
def testBaseSharedData_GuiAlert():
    """Test the _GuiAlert class."""
    alert = _GuiAlert(None, MockTheme())  # type: ignore

    # Default states
    assert alert.logMessage == []
    assert alert.finalState is False

    # Populate message
    text = "one"
    info = "two"
    details = "three"
    alert.setMessage(text, info, details)
    assert alert.logMessage == [text, info, details]
    assert alert.text() == text
    assert alert.informativeText() == info
    assert alert.detailedText() == details

    # Populate exception
    exc = Exception("oops")
    alert.setException(exc)
    assert alert.logMessage == [text, info, details]
    assert alert.informativeText() == f"{info}<br><b>Exception</b>: {exc!s}"

    # Alert: Info
    alert.setAlertType(_GuiAlert.INFO, False)
    assert hasattr(alert, "_btnOk")
    if sys.platform != "darwin":  # Not set on MacOS
        assert alert.windowTitle() == "Information"
    alert._btnOk.click()
    assert alert.finalState is True
    alert._state = False

    # Alert: Warning
    alert.setAlertType(_GuiAlert.WARN, False)
    assert hasattr(alert, "_btnOk")
    if sys.platform != "darwin":  # Not set on MacOS
        assert alert.windowTitle() == "Warning"
    alert._btnOk.click()
    assert alert.finalState is True
    alert._state = False

    # Alert: Error
    alert.setAlertType(_GuiAlert.ERROR, False)
    assert hasattr(alert, "_btnOk")
    if sys.platform != "darwin":  # Not set on MacOS
        assert alert.windowTitle() == "Error"
    alert._btnOk.click()
    assert alert.finalState is True
    alert._state = False

    # Alert: Question
    alert.setAlertType(_GuiAlert.ASK, True)
    assert hasattr(alert, "_btnYes")
    assert hasattr(alert, "_btnNo")
    if sys.platform != "darwin":  # Not set on MacOS
        assert alert.windowTitle() == "Question"
    alert._btnYes.click()
    assert alert.finalState is True
    alert._btnNo.click()
    assert alert.finalState is False
