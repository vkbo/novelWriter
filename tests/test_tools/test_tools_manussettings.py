"""
novelWriter – Manuscript Build Settings Dialog Tester
=====================================================

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

import pytest

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QFontDialog

from novelwriter import SHARED
from novelwriter.common import describeFont
from novelwriter.constants import nwHeadFmt
from novelwriter.core.buildsettings import BuildSettings, FilterMode
from novelwriter.tools.manussettings import (
    GuiBuildSettings, _FilterTab, _FormattingTab, _HeadingsTab
)
from novelwriter.types import QtDialogApply, QtDialogClose, QtDialogSave

from tests.tools import C, buildTestProject


@pytest.mark.gui
def testToolBuildSettings_Init(qtbot, nwGUI, projPath, mockRnd):
    """Test the initialisation of the GuiBuildSettings dialog."""
    buildTestProject(nwGUI, projPath)
    nwGUI.openProject(projPath)
    build = BuildSettings()

    # Create the dialog and populate it
    bSettings = GuiBuildSettings(nwGUI, build)
    bSettings.show()
    bSettings.loadContent()

    # Flip through pages
    bSettings.sidebar._group.button(bSettings.OPT_FORMATTING + 1).click()
    assert isinstance(bSettings.toolStack.currentWidget(), _FormattingTab)

    bSettings.sidebar._group.button(bSettings.OPT_HEADINGS).click()
    assert isinstance(bSettings.toolStack.currentWidget(), _HeadingsTab)

    bSettings.sidebar._group.button(bSettings.OPT_FILTERS).click()
    assert isinstance(bSettings.toolStack.currentWidget(), _FilterTab)

    # Check dialog buttons
    triggered = False

    @pyqtSlot(BuildSettings)
    def _testNewSettingsReady(new: BuildSettings):
        nonlocal build, triggered
        assert new is build
        triggered = True

    # Capture Apply button
    with qtbot.waitSignal(bSettings.newSettingsReady, timeout=5000):
        bSettings.newSettingsReady.connect(_testNewSettingsReady)
        bSettings._dialogButtonClicked(bSettings.buttonBox.button(QtDialogApply))

    assert triggered

    # Capture Save button
    triggered = False

    with qtbot.waitSignal(bSettings.newSettingsReady, timeout=5000):
        bSettings.newSettingsReady.connect(_testNewSettingsReady)
        bSettings._dialogButtonClicked(bSettings.buttonBox.button(QtDialogSave))

    assert triggered

    # Close manually
    # This pops the ask to save dialog, which is automatically handled
    triggered = False
    build._changed = True
    bSettings.show()

    with qtbot.waitSignal(bSettings.newSettingsReady, timeout=5000):
        bSettings.newSettingsReady.connect(_testNewSettingsReady)
        bSettings.close()

    assert triggered

    # Finish
    bSettings._dialogButtonClicked(bSettings.buttonBox.button(QtDialogClose))
    # qtbot.stop()


@pytest.mark.gui
def testToolBuildSettings_Filter(qtbot, nwGUI, projPath, mockRnd):
    """Test the Filter Tab of the GuiBuildSettings dialog."""
    buildTestProject(nwGUI, projPath)
    nwGUI.openProject(projPath)
    build = BuildSettings()

    switchMap = {
        "incNovel": 1,
        "incNotes": 2,
        "incInactive": 3,
        "novelRoot": 6,
        "plotRoot": 7,
        "charRoot": 8,
        "worldRoot": 9,
    }

    hPlotDoc = SHARED.project.newFile("Main Plot", C.hPlotRoot)
    hCharDoc = SHARED.project.newFile("Jane Doe", C.hCharRoot)
    SHARED.project.tree[hPlotDoc].setActive(False)  # type: ignore

    # Create the dialog and populate it
    bSettings = GuiBuildSettings(nwGUI, build)
    bSettings.show()
    bSettings.loadContent()

    filterTab = bSettings.optTabSelect
    bSettings.sidebar._group.button(bSettings.OPT_FILTERS).click()
    assert bSettings.toolStack.currentWidget() is filterTab

    # Check content
    assert filterTab.optTree.topLevelItemCount() == 4  # The 4 root folders
    assert filterTab.filterOpt._index == 10  # 2 headers, 1 sep, 3 opt and 4 roots

    # Un-toggle note folders
    filterTab.filterOpt._widgets[switchMap["worldRoot"]].setChecked(False)  # World Root
    assert filterTab.optTree.topLevelItemCount() == 3
    assert C.hWorldRoot in build._skipRoot

    filterTab.filterOpt._widgets[switchMap["charRoot"]].setChecked(False)  # Char Root
    assert filterTab.optTree.topLevelItemCount() == 2
    assert C.hCharRoot in build._skipRoot

    filterTab.filterOpt._widgets[switchMap["plotRoot"]].setChecked(False)  # Plot Root
    assert filterTab.optTree.topLevelItemCount() == 1
    assert C.hPlotRoot in build._skipRoot

    # Reset Plot and Char
    filterTab.filterOpt._widgets[switchMap["plotRoot"]].setChecked(True)
    filterTab.filterOpt._widgets[switchMap["charRoot"]].setChecked(True)
    assert filterTab.optTree.topLevelItemCount() == 3

    # Switch off novel docs
    filterTab.filterOpt._widgets[switchMap["incNovel"]].setChecked(False)
    assert build.buildItemFilter(SHARED.project) == {
        C.hNovelRoot:  (False, FilterMode.SKIPPED),
        C.hTitlePage:  (False, FilterMode.FILTERED),
        C.hChapterDir: (False, FilterMode.SKIPPED),
        C.hChapterDoc: (False, FilterMode.FILTERED),
        C.hSceneDoc:   (False, FilterMode.FILTERED),
        C.hPlotRoot:   (False, FilterMode.SKIPPED),
        hPlotDoc:      (False, FilterMode.FILTERED),
        C.hCharRoot:   (False, FilterMode.SKIPPED),
        hCharDoc:      (False, FilterMode.FILTERED),
        C.hWorldRoot:  (False, FilterMode.SKIPPED),
        C.hTrashRoot:  (False, FilterMode.SKIPPED),
    }

    # Switch on note docs
    filterTab.filterOpt._widgets[switchMap["incNotes"]].setChecked(True)
    assert build.buildItemFilter(SHARED.project) == {
        C.hNovelRoot:  (False, FilterMode.SKIPPED),
        C.hTitlePage:  (False, FilterMode.FILTERED),
        C.hChapterDir: (False, FilterMode.SKIPPED),
        C.hChapterDoc: (False, FilterMode.FILTERED),
        C.hSceneDoc:   (False, FilterMode.FILTERED),
        C.hPlotRoot:   (False, FilterMode.SKIPPED),
        hPlotDoc:      (False, FilterMode.FILTERED),  # Set to inactive
        C.hCharRoot:   (False, FilterMode.SKIPPED),
        hCharDoc:      (True,  FilterMode.FILTERED),  # Now enabled
        C.hWorldRoot:  (False, FilterMode.SKIPPED),
        C.hTrashRoot:  (False, FilterMode.SKIPPED),
    }

    # Switch on inactive docs
    filterTab.filterOpt._widgets[switchMap["incInactive"]].setChecked(True)
    assert build.buildItemFilter(SHARED.project) == {
        C.hNovelRoot:  (False, FilterMode.SKIPPED),
        C.hTitlePage:  (False, FilterMode.FILTERED),
        C.hChapterDir: (False, FilterMode.SKIPPED),
        C.hChapterDoc: (False, FilterMode.FILTERED),
        C.hSceneDoc:   (False, FilterMode.FILTERED),
        C.hPlotRoot:   (False, FilterMode.SKIPPED),
        hPlotDoc:      (True,  FilterMode.FILTERED),  # Now enabled
        C.hCharRoot:   (False, FilterMode.SKIPPED),
        hCharDoc:      (True,  FilterMode.FILTERED),
        C.hWorldRoot:  (False, FilterMode.SKIPPED),
        C.hTrashRoot:  (False, FilterMode.SKIPPED),
    }

    # Set chapter and scene docs to included
    filterTab._treeMap[C.hChapterDoc].setSelected(True)
    filterTab._treeMap[C.hSceneDoc].setSelected(True)
    filterTab.includedButton.click()
    assert build.buildItemFilter(SHARED.project) == {
        C.hNovelRoot:  (False, FilterMode.SKIPPED),
        C.hTitlePage:  (False, FilterMode.FILTERED),
        C.hChapterDir: (False, FilterMode.SKIPPED),
        C.hChapterDoc: (True,  FilterMode.INCLUDED),  # Now included
        C.hSceneDoc:   (True,  FilterMode.INCLUDED),  # Now included
        C.hPlotRoot:   (False, FilterMode.SKIPPED),
        hPlotDoc:      (True,  FilterMode.FILTERED),
        C.hCharRoot:   (False, FilterMode.SKIPPED),
        hCharDoc:      (True,  FilterMode.FILTERED),
        C.hWorldRoot:  (False, FilterMode.SKIPPED),
        C.hTrashRoot:  (False, FilterMode.SKIPPED),
    }

    # Set char and plot docs to excluded
    filterTab.optTree.clearSelection()
    filterTab._treeMap[hPlotDoc].setSelected(True)  # type: ignore
    filterTab._treeMap[hCharDoc].setSelected(True)  # type: ignore
    filterTab.excludedButton.click()
    assert build.buildItemFilter(SHARED.project) == {
        C.hNovelRoot:  (False, FilterMode.SKIPPED),
        C.hTitlePage:  (False, FilterMode.FILTERED),
        C.hChapterDir: (False, FilterMode.SKIPPED),
        C.hChapterDoc: (True,  FilterMode.INCLUDED),
        C.hSceneDoc:   (True,  FilterMode.INCLUDED),
        C.hPlotRoot:   (False, FilterMode.SKIPPED),
        hPlotDoc:      (False, FilterMode.EXCLUDED),  # Now excluded
        C.hCharRoot:   (False, FilterMode.SKIPPED),
        hCharDoc:      (False, FilterMode.EXCLUDED),  # Now excluded
        C.hWorldRoot:  (False, FilterMode.SKIPPED),
        C.hTrashRoot:  (False, FilterMode.SKIPPED),
    }

    # Switch on novel docs
    filterTab.filterOpt._widgets[switchMap["incNovel"]].setChecked(True)
    assert build.buildItemFilter(SHARED.project) == {
        C.hNovelRoot:  (False, FilterMode.SKIPPED),
        C.hTitlePage:  (True,  FilterMode.FILTERED),  # Now enabled
        C.hChapterDir: (False, FilterMode.SKIPPED),
        C.hChapterDoc: (True,  FilterMode.INCLUDED),
        C.hSceneDoc:   (True,  FilterMode.INCLUDED),
        C.hPlotRoot:   (False, FilterMode.SKIPPED),
        hPlotDoc:      (False, FilterMode.EXCLUDED),
        C.hCharRoot:   (False, FilterMode.SKIPPED),
        hCharDoc:      (False, FilterMode.EXCLUDED),
        C.hWorldRoot:  (False, FilterMode.SKIPPED),
        C.hTrashRoot:  (False, FilterMode.SKIPPED),
    }

    # Selecting only novel root should iterate through all children
    filterTab.optTree.clearSelection()
    filterTab._treeMap[C.hNovelRoot].setSelected(True)
    filterTab.resetButton.click()
    assert build.buildItemFilter(SHARED.project) == {
        C.hNovelRoot:  (False, FilterMode.SKIPPED),
        C.hTitlePage:  (True,  FilterMode.FILTERED),
        C.hChapterDir: (False, FilterMode.SKIPPED),
        C.hChapterDoc: (True,  FilterMode.FILTERED),
        C.hSceneDoc:   (True,  FilterMode.FILTERED),
        C.hPlotRoot:   (False, FilterMode.SKIPPED),
        hPlotDoc:      (False, FilterMode.EXCLUDED),
        C.hCharRoot:   (False, FilterMode.SKIPPED),
        hCharDoc:      (False, FilterMode.EXCLUDED),
        C.hWorldRoot:  (False, FilterMode.SKIPPED),
        C.hTrashRoot:  (False, FilterMode.SKIPPED),
    }

    # Set everything back to filtered
    filterTab.optTree.clearSelection()
    filterTab._treeMap[C.hNovelRoot].setSelected(True)
    filterTab._treeMap[C.hSceneDoc].setSelected(True)
    filterTab._treeMap[hPlotDoc].setSelected(True)  # type: ignore
    filterTab._treeMap[hCharDoc].setSelected(True)  # type: ignore
    filterTab.resetButton.click()
    assert build.buildItemFilter(SHARED.project) == {
        C.hNovelRoot:  (False, FilterMode.SKIPPED),
        C.hTitlePage:  (True,  FilterMode.FILTERED),
        C.hChapterDir: (False, FilterMode.SKIPPED),
        C.hChapterDoc: (True,  FilterMode.FILTERED),
        C.hSceneDoc:   (True,  FilterMode.FILTERED),
        C.hPlotRoot:   (False, FilterMode.SKIPPED),
        hPlotDoc:      (True,  FilterMode.FILTERED),
        C.hCharRoot:   (False, FilterMode.SKIPPED),
        hCharDoc:      (True,  FilterMode.FILTERED),
        C.hWorldRoot:  (False, FilterMode.SKIPPED),
        C.hTrashRoot:  (False, FilterMode.SKIPPED),
    }

    # Check handling of invalid project items
    assert list(filterTab._treeMap.keys()) == [
        C.hNovelRoot, C.hTitlePage, C.hChapterDir, C.hChapterDoc, C.hSceneDoc,
        C.hPlotRoot, hPlotDoc, C.hCharRoot, hCharDoc,
    ]
    SHARED.project.tree[hCharDoc].setRoot(None)  # type: ignore
    SHARED.project.tree[hPlotDoc].setParent(None)  # type: ignore
    filterTab._populateTree()
    assert list(filterTab._treeMap.keys()) == [
        C.hNovelRoot, C.hTitlePage, C.hChapterDir, C.hChapterDoc, C.hSceneDoc,
        C.hPlotRoot, C.hCharRoot
    ]

    # Finish
    bSettings._dialogButtonClicked(bSettings.buttonBox.button(QtDialogClose))
    # qtbot.stop()


@pytest.mark.gui
def testToolBuildSettings_Headings(qtbot, nwGUI):
    """Test the Headings Tab of the GuiBuildSettings dialog."""
    build = BuildSettings()

    ttTitle = f"Part: {nwHeadFmt.TITLE}"
    chTitle = f"Chapter: {nwHeadFmt.TITLE}"
    unTitle = f"Interlude: {nwHeadFmt.TITLE}"
    scTitle = f"Scene: {nwHeadFmt.TITLE}"
    shTitle = f"Hard Scene: {nwHeadFmt.TITLE}"
    sxTitle = f"Section: {nwHeadFmt.TITLE}"

    build.setValue("headings.fmtPart", ttTitle)
    build.setValue("headings.fmtChapter", chTitle)
    build.setValue("headings.fmtUnnumbered", unTitle)
    build.setValue("headings.fmtScene", scTitle)
    build.setValue("headings.fmtAltScene", shTitle)
    build.setValue("headings.fmtSection", sxTitle)
    build.setValue("headings.hideScene", False)
    build.setValue("headings.hideSection", False)

    # Create the dialog and populate it
    bSettings = GuiBuildSettings(nwGUI, build)
    bSettings.show()
    bSettings.loadContent()

    headTab = bSettings.optTabHeadings
    bSettings.sidebar._group.button(bSettings.OPT_HEADINGS).click()
    assert bSettings.toolStack.currentWidget() is headTab

    # Check initial values
    assert headTab.fmtPart.text() == ttTitle
    assert headTab.fmtChapter.text() == chTitle
    assert headTab.fmtUnnumbered.text() == unTitle
    assert headTab.fmtScene.text() == scTitle
    assert headTab.fmtAScene.text() == shTitle
    assert headTab.fmtSection.text() == sxTitle
    assert headTab.swtScene.isChecked() is False
    assert headTab.swtSection.isChecked() is False

    # Edit in Turn
    # ============

    # Nothing to apply
    assert headTab._editing == 0
    assert headTab.editTextBox.isEnabled() is False
    headTab.btnApply.click()
    assert headTab.editTextBox.isEnabled() is False

    # Title
    headTab.btnPart.click()
    assert headTab._editing == headTab.EDIT_TITLE
    assert headTab.editTextBox.isEnabled() is True
    assert headTab.editTextBox.toPlainText() == ttTitle
    headTab.btnApply.click()
    assert headTab.editTextBox.isEnabled() is False

    # Chapter
    headTab.btnChapter.click()
    assert headTab._editing == headTab.EDIT_CHAPTER
    assert headTab.editTextBox.isEnabled() is True
    assert headTab.editTextBox.toPlainText() == chTitle
    headTab.btnApply.click()
    assert headTab.editTextBox.isEnabled() is False

    # Unnumbered
    headTab.btnUnnumbered.click()
    assert headTab._editing == headTab.EDIT_UNNUM
    assert headTab.editTextBox.isEnabled() is True
    assert headTab.editTextBox.toPlainText() == unTitle
    headTab.btnApply.click()
    assert headTab.editTextBox.isEnabled() is False

    # Scene
    headTab.btnScene.click()
    assert headTab._editing == headTab.EDIT_SCENE
    assert headTab.editTextBox.isEnabled() is True
    assert headTab.editTextBox.toPlainText() == scTitle
    headTab.btnApply.click()
    assert headTab.editTextBox.isEnabled() is False

    # Hard Scene
    headTab.btnAScene.click()
    assert headTab._editing == headTab.EDIT_HSCENE
    assert headTab.editTextBox.isEnabled() is True
    assert headTab.editTextBox.toPlainText() == shTitle
    headTab.btnApply.click()
    assert headTab.editTextBox.isEnabled() is False

    # Section
    headTab.btnSection.click()
    assert headTab._editing == headTab.EDIT_SECTION
    assert headTab.editTextBox.isEnabled() is True
    assert headTab.editTextBox.toPlainText() == sxTitle
    headTab.btnApply.click()
    assert headTab.editTextBox.isEnabled() is False

    # Edit a Heading
    # ==============

    # Create new format of all bits
    headTab.btnChapter.click()
    allFmt = (
        f"{nwHeadFmt.TITLE}{nwHeadFmt.CH_NUM}{nwHeadFmt.CH_WORD}{nwHeadFmt.CH_ROMU}"
        f"{nwHeadFmt.CH_ROML}{nwHeadFmt.SC_NUM}{nwHeadFmt.SC_ABS}"
    )
    headTab.editTextBox.clear()
    assert headTab.editTextBox.toPlainText() == ""
    headTab.aInsTitle.trigger()
    headTab.aInsChNum.trigger()
    headTab.aInsChWord.trigger()
    headTab.aInsChRomU.trigger()
    headTab.aInsChRomL.trigger()
    headTab.aInsScNum.trigger()
    headTab.aInsScAbs.trigger()
    assert headTab.editTextBox.toPlainText() == allFmt
    headTab.btnApply.click()
    assert build.getStr("headings.fmtChapter") == allFmt

    # Check complex format
    headTab.btnChapter.click()
    headTab.editTextBox.setPlainText(f"Chapter {nwHeadFmt.CH_NUM}\n{nwHeadFmt.TITLE}\n")
    headTab.btnApply.click()
    assert build.getStr("headings.fmtChapter") == (
        f"Chapter {nwHeadFmt.CH_NUM}{nwHeadFmt.BR}{nwHeadFmt.TITLE}"
    )

    # Set all to plain title
    headTab.btnPart.click()
    headTab.editTextBox.setPlainText(nwHeadFmt.TITLE)
    headTab.btnApply.click()
    assert build.getStr("headings.fmtPart") == nwHeadFmt.TITLE

    headTab.btnChapter.click()
    headTab.editTextBox.setPlainText(nwHeadFmt.TITLE)
    headTab.btnApply.click()
    assert build.getStr("headings.fmtChapter") == nwHeadFmt.TITLE

    headTab.btnUnnumbered.click()
    headTab.editTextBox.setPlainText(nwHeadFmt.TITLE)
    headTab.btnApply.click()
    assert build.getStr("headings.fmtUnnumbered") == nwHeadFmt.TITLE

    headTab.btnScene.click()
    headTab.editTextBox.setPlainText(nwHeadFmt.TITLE)
    headTab.btnApply.click()
    assert build.getStr("headings.fmtScene") == nwHeadFmt.TITLE

    headTab.btnAScene.click()
    headTab.editTextBox.setPlainText(nwHeadFmt.TITLE)
    headTab.btnApply.click()
    assert build.getStr("headings.fmtAltScene") == nwHeadFmt.TITLE

    headTab.btnSection.click()
    headTab.editTextBox.setPlainText(nwHeadFmt.TITLE)
    headTab.btnApply.click()
    assert build.getStr("headings.fmtSection") == nwHeadFmt.TITLE

    # Check hide switches
    headTab.swtScene.setChecked(True)
    headTab.swtSection.setChecked(True)
    headTab.saveContent()
    assert build.getBool("headings.hideScene") is True
    assert build.getBool("headings.hideSection") is True

    # Finish
    bSettings._dialogButtonClicked(bSettings.buttonBox.button(QtDialogClose))
    # qtbot.stop()


@pytest.mark.gui
def testToolBuildSettings_FormatTextContent(qtbot, nwGUI):
    """Test the Text Content settings."""
    build = BuildSettings()

    build.setValue("text.includeBodyText", False)
    build.setValue("text.includeSynopsis", False)
    build.setValue("text.includeComments", False)
    build.setValue("text.includeKeywords", False)
    build.setValue("text.ignoredKeywords", "")

    build.setValue("text.addNoteHeadings", False)

    # Create the dialog and populate it
    bSettings = GuiBuildSettings(nwGUI, build)
    bSettings.show()
    bSettings.loadContent()

    fmtTab = bSettings.optTabFormatting
    bSettings.sidebar._group.button(bSettings.OPT_FORMATTING + 1).click()
    assert bSettings.toolStack.currentWidget() is fmtTab

    # Check initial values
    assert fmtTab.incBodyText.isChecked() is False
    assert fmtTab.incSynopsis.isChecked() is False
    assert fmtTab.incComments.isChecked() is False
    assert fmtTab.incKeywords.isChecked() is False
    assert fmtTab.ignoredKeywords.text() == ""

    assert fmtTab.addNoteHead.isChecked() is False

    # Toggle switches
    fmtTab.incBodyText.setChecked(True)
    fmtTab.incSynopsis.setChecked(True)
    fmtTab.incComments.setChecked(True)
    fmtTab.incKeywords.setChecked(True)

    fmtTab.addNoteHead.setChecked(True)

    # Test cleanup of ignored keywords
    fmtTab.ignoredKeywords.setText("@stuff, @pizza, @object")  # First two are invalid
    fmtTab._updateIgnoredKeywords("@custom")  # Adding a new should trigger cleanup
    assert fmtTab.ignoredKeywords.text() in ("@custom, @object", "@object, @custom")

    # Save values
    fmtTab.saveContent()

    assert build.getBool("text.includeBodyText") is True
    assert build.getBool("text.includeSynopsis") is True
    assert build.getBool("text.includeComments") is True
    assert build.getBool("text.includeKeywords") is True
    assert build.getStr("text.ignoredKeywords") in ("@custom, @object", "@object, @custom")

    assert build.getBool("text.addNoteHeadings") is True

    # Finish
    bSettings._dialogButtonClicked(bSettings.buttonBox.button(QtDialogClose))
    # qtbot.stop()


@pytest.mark.gui
def testToolBuildSettings_FormatTextFormat(monkeypatch, qtbot, nwGUI):
    """Test the Text Format settings."""
    build = BuildSettings()

    build.setValue("format.buildLang", "en_US")
    build.setValue("format.textFont", "")  # Will fall back to config value
    build.setValue("format.lineHeight", 1.2)

    build.setValue("format.justifyText", False)
    build.setValue("format.stripUnicode", False)
    build.setValue("format.replaceTabs", False)
    build.setValue("format.keepBreaks", True)
    build.setValue("format.showDialogue", False)

    # Create the dialog and populate it
    bSettings = GuiBuildSettings(nwGUI, build)
    bSettings.show()
    bSettings.loadContent()

    fmtTab = bSettings.optTabFormatting
    bSettings.sidebar._group.button(bSettings.OPT_FORMATTING + 2).click()
    assert bSettings.toolStack.currentWidget() is fmtTab

    # Check initial values
    assert fmtTab.lineHeight.value() == 1.2

    assert fmtTab.justifyText.isChecked() is False
    assert fmtTab.stripUnicode.isChecked() is False
    assert fmtTab.replaceTabs.isChecked() is False
    assert fmtTab.keepBreaks.isChecked() is True
    assert fmtTab.showDialogue.isChecked() is False

    # Change values
    testFont = QFont("Arial", 11)
    fmtTab._textFont = testFont
    fmtTab.textFont.setText(describeFont(testFont))
    fmtTab.lineHeight.setValue(1.15)

    fmtTab.justifyText.setChecked(True)
    fmtTab.stripUnicode.setChecked(True)
    fmtTab.replaceTabs.setChecked(True)
    fmtTab.keepBreaks.setChecked(False)
    fmtTab.showDialogue.setChecked(True)

    # Save values
    fmtTab.saveContent()

    assert build.getStr("format.textFont") == testFont.toString()
    assert build.getFloat("format.lineHeight") == 1.15

    assert build.getBool("format.justifyText") is True
    assert build.getBool("format.stripUnicode") is True
    assert build.getBool("format.replaceTabs") is True
    assert build.getBool("format.keepBreaks") is False
    assert build.getBool("format.showDialogue") is True

    # Check that the font dialog doesn't fail
    with monkeypatch.context() as mp:
        font = QFont()
        font.setFamily("Times")
        font.setPointSize(10)
        mp.setattr(QFontDialog, "getFont", lambda *a, **k: (font, True))

        fmtTab.btnTextFont.click()
        assert fmtTab._textFont == font

    # Finish
    bSettings._dialogButtonClicked(bSettings.buttonBox.button(QtDialogClose))
    # qtbot.stop()


@pytest.mark.gui
def testToolBuildSettings_FormatFirstLineIndent(monkeypatch, qtbot, nwGUI):
    """Test the First Line Indent settings."""
    build = BuildSettings()

    build.setValue("format.firstLineIndent", False)
    build.setValue("format.firstIndentWidth", 1.4)
    build.setValue("format.indentFirstPar", False)

    # Create the dialog and populate it
    bSettings = GuiBuildSettings(nwGUI, build)
    bSettings.show()
    bSettings.loadContent()

    fmtTab = bSettings.optTabFormatting
    bSettings.sidebar._group.button(bSettings.OPT_FORMATTING + 3).click()
    assert bSettings.toolStack.currentWidget() is fmtTab

    # Check initial values
    assert fmtTab.firstIndent.isChecked() is False
    assert fmtTab.indentWidth.value() == 1.4
    assert fmtTab.indentFirstPar.isChecked() is False

    # Change values
    fmtTab.firstIndent.setChecked(True)
    fmtTab.indentWidth.setValue(2.0)
    fmtTab.indentFirstPar.setChecked(True)

    # Save values
    fmtTab.saveContent()

    assert build.getBool("format.firstLineIndent") is True
    assert build.getFloat("format.firstIndentWidth") == 2.0
    assert build.getBool("format.indentFirstPar") is True

    # Finish
    bSettings._dialogButtonClicked(bSettings.buttonBox.button(QtDialogClose))
    # qtbot.stop()


@pytest.mark.gui
def testToolBuildSettings_FormatPageLayout(monkeypatch, qtbot, nwGUI):
    """Test the First Line Indent settings."""
    build = BuildSettings()

    build.setValue("format.pageUnit", "mm")
    build.setValue("format.pageSize", "Custom")
    build.setValue("format.pageWidth", 180.0)
    build.setValue("format.pageHeight", 250.0)
    build.setValue("format.topMargin", 25.0)
    build.setValue("format.bottomMargin", 25.0)
    build.setValue("format.leftMargin", 15.0)
    build.setValue("format.rightMargin", 15.0)

    # Create the dialog and populate it
    bSettings = GuiBuildSettings(nwGUI, build)
    bSettings.show()
    bSettings.loadContent()

    fmtTab = bSettings.optTabFormatting
    bSettings.sidebar._group.button(bSettings.OPT_FORMATTING + 4).click()
    assert bSettings.toolStack.currentWidget() is fmtTab

    # Check initial values
    assert fmtTab.pageUnit.currentData() == "mm"
    assert fmtTab.pageSize.currentData() == "Custom"
    assert fmtTab.pageWidth.value() == 180.0
    assert fmtTab.pageHeight.value() == 250.0
    assert fmtTab.topMargin.value() == 25.0
    assert fmtTab.bottomMargin.value() == 25.0
    assert fmtTab.leftMargin.value() == 15.0
    assert fmtTab.rightMargin.value() == 15.0

    # Change values
    fmtTab.pageUnit.setCurrentIndex(fmtTab.pageUnit.findData("cm"))
    fmtTab.pageSize.setCurrentIndex(fmtTab.pageSize.findData("A4"))

    # Save values
    fmtTab.saveContent()

    assert fmtTab.pageUnit.currentData() == "cm"
    assert fmtTab.pageSize.currentData() == "A4"
    assert fmtTab.pageWidth.value() == 21.0
    assert fmtTab.pageHeight.value() == 29.7
    assert fmtTab.topMargin.value() == 2.5
    assert fmtTab.bottomMargin.value() == 2.5
    assert fmtTab.leftMargin.value() == 1.5
    assert fmtTab.rightMargin.value() == 1.5

    # Finish
    bSettings._dialogButtonClicked(bSettings.buttonBox.button(QtDialogClose))
    # qtbot.stop()


@pytest.mark.gui
def testToolBuildSettings_FormatOutput(qtbot, nwGUI):
    """Test the format-specific settings."""
    build = BuildSettings()

    build.setValue("doc.pageHeader", nwHeadFmt.DOC_AUTO)
    build.setValue("doc.pageCountOffset", 0)
    build.setValue("doc.colorHeadings", True)
    build.setValue("doc.scaleHeadings", True)
    build.setValue("doc.boldHeadings", True)

    build.setValue("html.addStyles", False)
    build.setValue("html.preserveTabs", False)

    # Create the dialog and populate it
    bSettings = GuiBuildSettings(nwGUI, build)
    bSettings.show()
    bSettings.loadContent()

    fmtTab = bSettings.optTabFormatting
    bSettings.sidebar._group.button(bSettings.OPT_FORMATTING + 5).click()
    assert bSettings.toolStack.currentWidget() is fmtTab

    # Check initial values
    assert fmtTab.odtPageHeader.text() == nwHeadFmt.DOC_AUTO
    assert fmtTab.odtPageCountOffset.value() == 0
    assert fmtTab.colorHeadings.isChecked() is True
    assert fmtTab.scaleHeadings.isChecked() is True
    assert fmtTab.boldHeadings.isChecked() is True

    assert fmtTab.htmlAddStyles.isChecked() is False
    assert fmtTab.htmlPreserveTabs.isChecked() is False

    # Change Values
    fmtTab.odtPageCountOffset.setValue(1)
    fmtTab.odtPageHeader.setText("Stuff")

    # Toggle all
    fmtTab.colorHeadings.setChecked(False)
    fmtTab.scaleHeadings.setChecked(False)
    fmtTab.boldHeadings.setChecked(False)
    fmtTab.htmlAddStyles.setChecked(True)
    fmtTab.htmlPreserveTabs.setChecked(True)

    # Save values
    fmtTab.saveContent()

    assert build.getStr("doc.pageHeader") == "Stuff"
    assert build.getInt("doc.pageCountOffset") == 1
    assert build.getBool("doc.colorHeadings") is False
    assert build.getBool("doc.scaleHeadings") is False
    assert build.getBool("doc.boldHeadings") is False

    assert build.getBool("html.addStyles") is True
    assert build.getBool("html.preserveTabs") is True

    # Reset header format
    fmtTab.btnPageHeader.click()
    assert fmtTab.odtPageHeader.text() == nwHeadFmt.DOC_AUTO

    # Finish
    bSettings._dialogButtonClicked(bSettings.buttonBox.button(QtDialogClose))
    # qtbot.stop()
