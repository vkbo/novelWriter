"""
novelWriter – Manuscript Tool Tester
====================================

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

import sys
import pytest

from pathlib import Path
from pytestqt.qtbot import QtBot

from tools import C, buildTestProject, getGuiItem
from mocked import causeOSError

from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QDialogButtonBox
from PyQt5.QtPrintSupport import QPrintPreviewDialog

from novelwriter import CONFIG
from novelwriter.guimain import GuiMain
from novelwriter.core.buildsettings import BuildSettings
from novelwriter.tools.manuscript import GuiManuscript
from novelwriter.tools.manusbuild import GuiManuscriptBuild
from novelwriter.tools.manussettings import GuiBuildSettings


@pytest.mark.gui
def testManuscript_Init(monkeypatch, qtbot: QtBot, nwGUI: GuiMain, projPath: Path, mockRnd):
    """Test the init/main functionality of the GuiManuscript dialog."""
    buildTestProject(nwGUI, projPath)
    nwGUI.openProject(projPath)
    nwGUI.theProject.storage.getDocument(C.hChapterDoc).writeDocument("## A Chapter\n\n\t\tHi")
    allText = "New Novel\nBy Jane Doe\nA Chapter\n\t\tHi\n* * *"

    manus = GuiManuscript(nwGUI)
    manus.show()
    manus.loadContent()
    assert manus.docPreview.toPlainText().strip() == ""

    # Run the default build
    manus.buildList.clearSelection()
    manus.buildList.setCurrentRow(0)
    with qtbot.waitSignal(manus.docPreview.document().contentsChanged):
        manus.btnPreview.click()
    assert manus.docPreview.toPlainText().strip() == allText

    manus.close()

    # A new dialog should load the old build
    manus = GuiManuscript(nwGUI)
    manus.show()
    manus.loadContent()
    assert manus.docPreview.toPlainText().strip() == allText
    manus.close()

    # But blocking the reload should leave it empty
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", lambda *a, **k: causeOSError)
        manus = GuiManuscript(nwGUI)
        manus.show()
        manus.loadContent()
        assert manus.docPreview.toPlainText().strip() == ""
        manus.close()

    # Finish
    # qtbot.stop()

# END Test testManuscript_Init


@pytest.mark.gui
def testManuscript_Builds(qtbot: QtBot, nwGUI: GuiMain, projPath: Path):
    """Test the handling of builds in the GuiManuscript dialog."""
    buildTestProject(nwGUI, projPath)
    nwGUI.openProject(projPath)

    manus = GuiManuscript(nwGUI)
    manus.show()
    manus.loadContent()

    # Delete the default build
    manus.buildList.clearSelection()
    manus.buildList.setCurrentRow(0)
    manus.tbDel.click()
    assert manus.buildList.count() == 0

    # Create a new build
    manus.tbAdd.click()
    bSettings = getGuiItem("GuiBuildSettings")
    assert isinstance(bSettings, GuiBuildSettings)
    bSettings.editBuildName.setText("Test Build")
    build = None

    @pyqtSlot(BuildSettings)
    def _testNewSettingsReady(new: BuildSettings):
        nonlocal build
        build = new

    with qtbot.waitSignal(bSettings.newSettingsReady, timeout=5000):
        bSettings.newSettingsReady.connect(_testNewSettingsReady)
        bSettings.dlgButtons.button(QDialogButtonBox.Save).click()

    assert isinstance(build, BuildSettings)
    assert build.name == "Test Build"
    assert manus.buildList.count() == 1

    # Edit the new build
    manus.buildList.clearSelection()
    manus.buildList.setCurrentRow(0)
    manus.tbEdit.click()

    bSettings = getGuiItem("GuiBuildSettings")
    assert isinstance(bSettings, GuiBuildSettings)
    build = None

    with qtbot.waitSignal(bSettings.newSettingsReady, timeout=5000):
        bSettings.newSettingsReady.connect(_testNewSettingsReady)
        bSettings.dlgButtons.button(QDialogButtonBox.Apply).click()  # Should leave the dialog open

    assert isinstance(build, BuildSettings)
    assert build.name == "Test Build"
    assert manus.buildList.count() == 1

    # Close the dialog should also close the child dialogs
    manus.btnClose.click()
    if isinstance(bSettings, GuiBuildSettings):
        # May have been garbage collected, but if it isn't, it should be hidden
        assert bSettings.isVisible() is False

    # Finish
    # qtbot.stop()

# END Test testManuscript_Builds


@pytest.mark.gui
def testManuscript_Features(monkeypatch, qtbot: QtBot, nwGUI: GuiMain, projPath: Path):
    """Test other features of the GuiManuscript dialog."""
    buildTestProject(nwGUI, projPath)
    nwGUI.openProject(projPath)

    manus = GuiManuscript(nwGUI)
    manus.show()
    manus.loadContent()

    cacheFile = CONFIG.dataPath("cache") / f"build_{nwGUI.theProject.data.uuid}.json"
    manus.buildList.setCurrentRow(0)
    build = manus._getSelectedBuild()
    assert isinstance(build, BuildSettings)

    # Previews
    # ========

    # No build selected
    manus.buildList.clearSelection()
    manus.btnPreview.click()
    qtbot.wait(200)  # Should be enough to run the build
    assert manus.docPreview.toPlainText().strip() == ""
    assert cacheFile.exists() is False

    # Preview the first, but fail to save cache
    manus.buildList.setCurrentRow(0)
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", lambda *a, **k: causeOSError)
        with qtbot.waitSignal(manus.docPreview.document().contentsChanged):
            manus.btnPreview.click()
        assert cacheFile.exists() is False

    # Preview again, and allow cache file to be created
    manus.buildList.setCurrentRow(0)
    with qtbot.waitSignal(manus.docPreview.document().contentsChanged):
        manus.btnPreview.click()
    assert manus.docPreview.toPlainText().strip() != ""
    assert cacheFile.exists() is True

    # Toggle justify
    assert manus.docPreview.document().defaultTextOption().alignment() == Qt.AlignAbsolute
    manus.docPreview.setJustify(True)
    assert manus.docPreview.document().defaultTextOption().alignment() == Qt.AlignJustify
    manus.docPreview.setJustify(False)
    assert manus.docPreview.document().defaultTextOption().alignment() == Qt.AlignAbsolute

    # Tests are too fast to trigger this one, so we trigger it manually to ensure it isn't failing
    manus.docPreview._hideProgress()

    # Builds
    # ======

    build._changed = True
    manus.buildList.clearSelection()
    with monkeypatch.context() as mp:
        mp.setattr("novelwriter.tools.manusbuild.GuiManuscriptBuild.exec_", lambda *a: None)

        # With no selection, no dialog should be created
        manus.btnBuild.click()
        for obj in manus.children():
            assert not isinstance(obj, GuiManuscriptBuild)

        # With a selection, there should be one
        manus.buildList.setCurrentRow(0)
        manus.btnBuild.click()
        for obj in manus.children():
            if isinstance(obj, GuiManuscriptBuild):
                obj.close()
                break
        else:
            assert False

    # Finish
    manus.close()
    # qtbot.stop()

# END Test testManuscript_Features


@pytest.mark.gui
@pytest.mark.skipif(sys.platform.startswith("darwin"), reason="Not running on Darwin")
def testManuscript_Print(monkeypatch, qtbot: QtBot, nwGUI: GuiMain, projPath: Path):
    """Test the print feature of the GuiManuscript dialog."""
    buildTestProject(nwGUI, projPath)
    nwGUI.openProject(projPath)

    manus = GuiManuscript(nwGUI)
    manus.show()
    manus.loadContent()

    manus.buildList.setCurrentRow(0)
    with qtbot.waitSignal(manus.docPreview.document().contentsChanged):
        manus.btnPreview.click()
    assert manus.docPreview.toPlainText().strip() != ""

    with monkeypatch.context() as mp:
        mp.setattr(QPrintPreviewDialog, "exec_", lambda *a: None)
        manus.btnPrint.click()
        for obj in manus.children():
            if isinstance(obj, QPrintPreviewDialog):
                obj.show()
                obj.close()
                break
        else:
            assert False

    # Finish
    manus.close()
    # qtbot.stop()

# END Test testManuscript_Print
