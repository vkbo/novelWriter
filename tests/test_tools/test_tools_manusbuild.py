"""
novelWriter – Manuscript Build Dialog Tester
============================================

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

from pathlib import Path

import pytest

from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QFileDialog, QListWidgetItem
from pytestqt.qtbot import QtBot

from novelwriter.constants import nwLabels
from novelwriter.core.buildsettings import BuildSettings
from novelwriter.enum import nwBuildFmt
from novelwriter.guimain import GuiMain
from novelwriter.shared import _GuiAlert
from novelwriter.tools.manusbuild import GuiManuscriptBuild
from novelwriter.types import QtDialogClose

from tests.tools import buildTestProject


@pytest.mark.gui
def testToolManuscriptBuild_Main(
    monkeypatch, qtbot: QtBot, nwGUI: GuiMain, fncPath: Path, projPath: Path, mockRnd
):
    """Test the GuiManuscriptBuild dialog."""
    buildTestProject(nwGUI, projPath)
    nwGUI.openProject(projPath)
    build = BuildSettings()
    build.setLastBuildPath(fncPath)

    manus = GuiManuscriptBuild(nwGUI, build)
    manus.show()

    # Check initial values
    assert manus.buildPath.text() == str(fncPath)
    assert manus.buildName.text() == "New Project - "
    assert manus.listContent.count() == 3  # All novel docs

    # Reset build name to default
    build.setName("Test Build")
    manus.btnReset.click()
    assert manus.buildName.text() == "New Project - Test Build"

    # Change path
    with monkeypatch.context() as mp:
        mp.setattr(QFileDialog, "getExistingDirectory", lambda *a: str(projPath))
        manus.btnBrowse.click()
        assert manus.buildPath.text() == str(projPath)

    # Builds
    # ======

    # Reset values
    manus.buildPath.setText(str(fncPath))
    manus.buildName.setText("TestBuild")

    # Helper function
    def selectFormat(fmt):
        for i in range(manus.listFormats.count()):
            item = manus.listFormats.item(i)
            assert isinstance(item, QListWidgetItem)
            if item.data(manus.D_KEY) == fmt:
                manus.listFormats.setCurrentItem(item)
                return
        raise ValueError("No such key in format list")

    # Build documents
    lastFmt = None
    for fmt in nwBuildFmt:
        selectFormat(fmt)
        assert manus._getSelectedFormat() == fmt
        manus.btnBuild.click()
        assert (fncPath / "TestBuild").with_suffix(nwLabels.BUILD_EXT[fmt]).exists()
        lastFmt = fmt

    button = manus.buttonBox.button(QtDialogClose)
    assert button is not None
    manus._dialogButtonClicked(button)
    manus.deleteLater()

    assert build.lastBuildName == "TestBuild"
    assert build.lastFormat == lastFmt
    assert build.lastBuildPath == fncPath

    # Error Handling
    # ==============

    manus = GuiManuscriptBuild(nwGUI, build)
    manus.show()

    # Name, path and format should be remembered
    assert manus.buildPath.text() == str(fncPath)
    assert manus.buildName.text() == "TestBuild"
    assert manus._getSelectedFormat() == lastFmt

    # Check handling of no selected build
    manus.listFormats.clearSelection()
    assert manus._getSelectedFormat() is None
    assert manus._runBuild() is False

    # Check ODT build with no name set, which should just reset it
    selectFormat(nwBuildFmt.ODT)
    manus.buildName.clear()
    assert manus._runBuild() is True
    assert manus.buildName.text() == "New Project - Test Build"
    assert (fncPath / "New Project - Test Build.odt").exists()

    # But invalid path should fail
    manus.buildPath.setText(str(fncPath / "blabla"))
    assert manus._runBuild() is False

    # Blocking overwrite should also fail
    manus.buildPath.setText(str(fncPath))
    manus.buildName.setText("TestBuild")
    with monkeypatch.context() as mp:
        mp.setattr(_GuiAlert, "finalState", False)
        assert manus._runBuild() is False

    # Test that the open button works
    lastUrl = ""

    def mockOpenUrl(url: QUrl) -> None:
        nonlocal lastUrl
        lastUrl = url.toString()

    with monkeypatch.context() as mp:
        mp.setattr(QDesktopServices, "openUrl", mockOpenUrl)
        manus.btnOpen.click()
        assert lastUrl.startswith("file://")

    # Finish
    button = manus.buttonBox.button(QtDialogClose)
    assert button is not None
    manus._dialogButtonClicked(button)
    # qtbot.stop()
