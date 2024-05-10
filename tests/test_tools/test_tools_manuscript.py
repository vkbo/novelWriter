"""
novelWriter – Manuscript Tool Tester
====================================

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

import sys

import pytest

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtPrintSupport import QPrintPreviewDialog
from PyQt5.QtWidgets import QAction, QListWidgetItem

from novelwriter import CONFIG, SHARED
from novelwriter.constants import nwHeadFmt
from novelwriter.core.buildsettings import BuildSettings
from novelwriter.tools.manusbuild import GuiManuscriptBuild
from novelwriter.tools.manuscript import GuiManuscript
from novelwriter.tools.manussettings import GuiBuildSettings
from novelwriter.types import QtAlignAbsolute, QtAlignJustify, QtDialogApply, QtDialogSave

from tests.mocked import causeOSError
from tests.tools import C, buildTestProject


@pytest.mark.gui
def testManuscript_Init(monkeypatch, qtbot, nwGUI, projPath, mockRnd):
    """Test the init/main functionality of the GuiManuscript dialog."""
    buildTestProject(nwGUI, projPath)
    nwGUI.openProject(projPath)
    SHARED.project.storage.getDocument(C.hChapterDoc).writeDocument("## A Chapter\n\n\t\tHi")
    allText = "New Novel\nBy Jane Doe\nA Chapter\n\t\tHi"

    nwGUI.mainMenu.aBuildManuscript.activate(QAction.Trigger)
    qtbot.waitUntil(lambda: SHARED.findTopLevelWidget(GuiManuscript) is not None, timeout=1000)
    manus = SHARED.findTopLevelWidget(GuiManuscript)
    assert isinstance(manus, GuiManuscript)
    manus.show()
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

    nwGUI.closeProject()  # This should auto-close the manuscript tool
    assert manus.isHidden()

    # qtbot.stop()


@pytest.mark.gui
def testManuscript_Builds(qtbot, nwGUI, projPath):
    """Test the handling of builds in the GuiManuscript dialog."""
    buildTestProject(nwGUI, projPath)
    nwGUI.openProject(projPath)

    manus = GuiManuscript(nwGUI)
    manus.show()
    manus.loadContent()

    # Delete the default build, while it is open
    manus.buildList.clearSelection()
    manus.buildList.setCurrentRow(0)
    with qtbot.waitSignal(manus.tbEdit.clicked, timeout=5000):
        manus.tbEdit.click()

    manus._editSelectedBuild()

    manus.buildList.clearSelection()
    manus.buildList.setCurrentRow(0)
    manus.tbDel.click()
    assert manus.buildList.count() == 0

    # Create a new build
    manus.tbAdd.click()
    bSettings = SHARED.findTopLevelWidget(GuiBuildSettings)
    assert isinstance(bSettings, GuiBuildSettings)
    bSettings.editBuildName.setText("Test Build")
    build = None

    @pyqtSlot(BuildSettings)
    def _testNewSettingsReady(new: BuildSettings):
        nonlocal build
        build = new

    with qtbot.waitSignal(bSettings.newSettingsReady, timeout=5000):
        bSettings.newSettingsReady.connect(_testNewSettingsReady)
        bSettings.buttonBox.button(QtDialogSave).click()

    assert isinstance(build, BuildSettings)
    assert build.name == "Test Build"
    assert manus.buildList.count() == 1

    # Edit the new build
    manus.buildList.clearSelection()
    manus.buildList.setCurrentRow(0)
    with qtbot.waitSignal(manus.tbEdit.clicked, timeout=5000):
        manus.tbEdit.click()

    manus._editSelectedBuild()
    bSettings = SHARED.findTopLevelWidget(GuiBuildSettings)
    assert isinstance(bSettings, GuiBuildSettings)
    build = None

    with qtbot.waitSignal(bSettings.newSettingsReady, timeout=5000):
        bSettings.newSettingsReady.connect(_testNewSettingsReady)
        bSettings.buttonBox.button(QtDialogApply).click()  # Should leave the dialog open

    assert isinstance(build, BuildSettings)
    assert build.name == "Test Build"
    assert manus.buildList.count() == 1

    # Close the dialog should also close the child dialogs
    manus.btnClose.click()
    if isinstance(bSettings, GuiBuildSettings):
        # May have been garbage collected, but if it isn't, it should be hidden
        assert bSettings.isVisible() is False

    # qtbot.stop()


@pytest.mark.gui
def testManuscript_Features(monkeypatch, qtbot, nwGUI, projPath, mockRnd):
    """Test other features of the GuiManuscript dialog."""
    buildTestProject(nwGUI, projPath)
    nwGUI.openProject(projPath)

    nwGUI.openDocument(C.hTitlePage)
    nwGUI.docEditor.setPlainText(
        "#! My Novel\n\n"
        "# Part One\n\n"
        "## Chapter One\n\n"
        "### Scene One\n\n"
        "Text\n\n"
        "### Scene Two\n\n"
        "Text\n\n"
        "## Chapter Two\n\n"
        "### Scene Three\n\n"
        "Text\n\n"
        "###! Scene Four\n\n"
        "Text\n\n"
        "#### Section\n\n"
        "Text\n\n"
    )
    nwGUI.saveDocument()
    # qtbot.stop()

    manus = GuiManuscript(nwGUI)
    manus.show()
    manus.loadContent()

    cacheFile = CONFIG.dataPath("cache") / f"build_{SHARED.project.data.uuid}.json"
    manus.buildList.setCurrentRow(0)
    build = manus._getSelectedBuild()
    assert isinstance(build, BuildSettings)

    # Previews
    # ========

    # No build selected
    manus.buildList.clear()
    manus.btnPreview.click()
    qtbot.wait(200)  # Should be enough to run the build
    assert manus.docPreview.toPlainText().strip() == ""
    assert cacheFile.exists() is False
    manus._updateBuildsList()

    # Preview the first, but fail to save cache
    manus.buildList.setCurrentRow(0)
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", lambda *a, **k: causeOSError)
        with qtbot.waitSignal(manus.docPreview.document().contentsChanged):
            manus.btnPreview.click()
        assert cacheFile.exists() is False

    first = manus.buildList.item(0)
    assert isinstance(first, QListWidgetItem)
    build = manus._builds.getBuild(first.data(GuiManuscript.D_KEY))
    assert isinstance(build, BuildSettings)
    build.setValue("headings.fmtScene", nwHeadFmt.TITLE)
    build.setValue("headings.fmtAltScene", nwHeadFmt.TITLE)
    manus._builds.setBuild(build)

    # Preview again, and allow cache file to be created
    manus.buildList.setCurrentRow(0)
    with qtbot.waitSignal(manus.docPreview.document().contentsChanged):
        manus.btnPreview.click()
    assert manus.docPreview.toPlainText().strip() != ""
    assert cacheFile.exists() is True

    # Check Outline
    assert manus.buildOutline._outline == {
        "000000000000c:T0001": "TT|My Novel",
        "000000000000c:T0002": "PT|Part One",
        "000000000000c:T0003": "CH|Chapter One",
        "000000000000c:T0004": "SC|Scene One",
        "000000000000c:T0005": "SC|Scene Two",
        "000000000000c:T0006": "CH|Chapter Two",
        "000000000000c:T0007": "SC|Scene Three",
        "000000000000c:T0008": "SC|Scene Four",
        "000000000000e:T0001": "CH|New Chapter",
        "000000000000f:T0001": "SC|New Scene",
    }
    listView = manus.buildOutline.listView
    assert listView.topLevelItemCount() == 5
    keyRole = manus.buildOutline.D_LINE

    assert (item := listView.topLevelItem(0)) and item.data(0, keyRole) == "000000000000c:T0001"
    assert (item := listView.topLevelItem(1)) and item.data(0, keyRole) == "000000000000c:T0002"
    assert (item := listView.topLevelItem(2)) and item.data(0, keyRole) == "000000000000c:T0003"
    assert (item := listView.topLevelItem(3)) and item.data(0, keyRole) == "000000000000c:T0006"
    assert (item := listView.topLevelItem(4)) and item.data(0, keyRole) == "000000000000e:T0001"

    # Click Outline
    item = listView.topLevelItem(4)
    assert item is not None
    with qtbot.waitSignal(manus.buildOutline.outlineEntryClicked) as signal:
        manus.buildOutline._onItemClick(item)
        assert signal.args == ["000000000000e:T0001"]

    # Check Preview Stats
    assert manus.docStats.mainStack.currentWidget() == manus.docStats.minWidget
    assert manus.docStats.minWordCount.text() == "25"
    assert manus.docStats.minCharCount.text() == "117"

    manus.docStats.toggleButton.toggle()
    assert manus.docStats.mainStack.currentWidget() == manus.docStats.maxWidget
    assert manus.docStats.maxTotalWords.text() == "25"
    assert manus.docStats.maxTotalChars.text() == "117"

    # Toggle justify
    assert manus.docPreview.document().defaultTextOption().alignment() == QtAlignAbsolute
    manus.docPreview.setJustify(True)
    assert manus.docPreview.document().defaultTextOption().alignment() == QtAlignJustify
    manus.docPreview.setJustify(False)
    assert manus.docPreview.document().defaultTextOption().alignment() == QtAlignAbsolute

    # Tests are too fast to trigger this one, so we trigger it manually to ensure it isn't failing
    manus.docPreview._postUpdate()

    # Builds
    # ======

    build._changed = True
    manus.buildList.clearSelection()
    with monkeypatch.context() as mp:
        mp.setattr("novelwriter.tools.manusbuild.GuiManuscriptBuild.exec", lambda *a: None)

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


@pytest.mark.gui
@pytest.mark.skipif(sys.platform.startswith("darwin"), reason="Not running on Darwin")
def testManuscript_Print(monkeypatch, qtbot, nwGUI, projPath):
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
        mp.setattr(QPrintPreviewDialog, "exec", lambda *a: None)
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
