"""
novelWriter – Manuscript Build Dialog Tester
============================================

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

from pathlib import Path
from pytestqt.qtbot import QtBot

from tools import buildTestProject

from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QDialogButtonBox, QFileDialog, QListWidgetItem, QMessageBox

from novelwriter.enum import nwBuildFmt
from novelwriter.guimain import GuiMain
from novelwriter.constants import nwLabels
from novelwriter.tools.manusbuild import GuiManuscriptBuild
from novelwriter.core.buildsettings import BuildSettings


@pytest.mark.gui
def testManuscriptBuild_Main(
    monkeypatch, qtbot: QtBot, nwGUI: GuiMain, fncPath: Path, projPath: Path, mockRnd
):
    """Test the GuiManuscriptBuild dialog."""
    buildTestProject(nwGUI, projPath)
    nwGUI.openProject(projPath)
    build = BuildSettings()
    build.setLastPath(fncPath)

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
        else:
            raise ValueError("No such key in format list")

    # Build documents
    lastFmt = None
    for fmt in nwBuildFmt:
        selectFormat(fmt)
        assert manus._getSelectedFormat() == fmt
        manus.btnBuild.click()
        assert (fncPath / "TestBuild").with_suffix(nwLabels.BUILD_EXT[fmt]).exists()
        lastFmt = fmt

    manus._dialogButtonClicked(manus.dlgButtons.button(QDialogButtonBox.Close))
    manus.deleteLater()

    assert build.lastBuildName == "TestBuild"
    assert build.lastFormat == lastFmt
    assert build.lastPath == fncPath

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
        mp.setattr(QMessageBox, "result", lambda *a: QMessageBox.No)
        assert manus._runBuild() is False

    # Test that the open button works
    lastUrl = ""

    def mockOpenUrl(url: QUrl) -> None:
        nonlocal lastUrl
        lastUrl = url.toString()
        return

    with monkeypatch.context() as mp:
        mp.setattr(QDesktopServices, "openUrl", mockOpenUrl)
        manus.btnOpen.click()
        assert lastUrl.startswith("file://")

    # Finish
    manus._dialogButtonClicked(manus.dlgButtons.button(QDialogButtonBox.Close))
    # qtbot.stop()

# END Test testManuscriptBuild_Main
