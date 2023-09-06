"""
novelWriter – Preferences Dialog Class Tester
=============================================

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

import pytest

from shutil import copyfile

from tools import cmpFiles, getGuiItem

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialogButtonBox, QDialog, QAction, QFileDialog, QFontDialog
)

from novelwriter import CONFIG, SHARED
from novelwriter.dialogs.quotes import GuiQuoteSelect
from novelwriter.dialogs.preferences import GuiPreferences

KEY_DELAY = 1


@pytest.mark.gui
def testDlgPreferences_Main(qtbot, monkeypatch, nwGUI, tstPaths):
    """Test the preferences dialog."""
    monkeypatch.setattr(GuiPreferences, "exec_", lambda *a: None)
    monkeypatch.setattr(GuiPreferences, "result", lambda *a: QDialog.Accepted)
    monkeypatch.setattr(SHARED._spelling, "listDictionaries", lambda: [("en", "English [en]")])

    with monkeypatch.context() as mp:
        mp.setattr(GuiPreferences, "updateTheme", lambda *a: True)
        mp.setattr(GuiPreferences, "updateSyntax", lambda *a: True)
        mp.setattr(GuiPreferences, "needsRestart", lambda *a: True)
        mp.setattr(GuiPreferences, "refreshTree", lambda *a: True)
        nwGUI.mainMenu.aPreferences.activate(QAction.Trigger)
        qtbot.waitUntil(lambda: getGuiItem("GuiPreferences") is not None, timeout=1000)

    nwPrefs = getGuiItem("GuiPreferences")
    assert isinstance(nwPrefs, GuiPreferences)
    nwPrefs.show()

    assert nwPrefs.updateTheme is False
    assert nwPrefs.updateSyntax is False
    assert nwPrefs.needsRestart is False
    assert nwPrefs.refreshTree is False

    # General Settings
    qtbot.wait(KEY_DELAY)
    tabGeneral = nwPrefs.tabGeneral
    nwPrefs._tabBox.setCurrentWidget(tabGeneral)

    qtbot.wait(KEY_DELAY)
    assert tabGeneral.showFullPath.isChecked()
    qtbot.mouseClick(tabGeneral.showFullPath, Qt.LeftButton)
    assert not tabGeneral.showFullPath.isChecked()

    qtbot.wait(KEY_DELAY)
    assert not tabGeneral.hideVScroll.isChecked()
    qtbot.mouseClick(tabGeneral.hideVScroll, Qt.LeftButton)
    assert tabGeneral.hideVScroll.isChecked()

    qtbot.wait(KEY_DELAY)
    assert not tabGeneral.hideHScroll.isChecked()
    qtbot.mouseClick(tabGeneral.hideHScroll, Qt.LeftButton)
    assert tabGeneral.hideHScroll.isChecked()

    # Check font button
    monkeypatch.setattr(QFontDialog, "getFont", lambda font, obj: (font, True))
    qtbot.mouseClick(tabGeneral.fontButton, Qt.LeftButton)

    qtbot.wait(KEY_DELAY)
    tabGeneral.guiFontSize.setValue(12)

    # Projects Settings
    qtbot.wait(KEY_DELAY)
    tabProjects = nwPrefs.tabProjects
    nwPrefs._tabBox.setCurrentWidget(tabProjects)
    tabProjects.backupPath = "no/where"

    qtbot.wait(KEY_DELAY)
    assert not tabProjects.backupOnClose.isChecked()
    qtbot.mouseClick(tabProjects.backupOnClose, Qt.LeftButton)
    assert tabProjects.backupOnClose.isChecked()

    # qtbot.stop()

    # Check Browse button
    monkeypatch.setattr(QFileDialog, "getExistingDirectory", lambda *a, **k: "")
    assert not tabProjects._backupFolder()
    monkeypatch.setattr(QFileDialog, "getExistingDirectory", lambda *a, **k: "some/dir")
    qtbot.mouseClick(tabProjects.backupGetPath, Qt.LeftButton)

    qtbot.wait(KEY_DELAY)
    tabProjects.autoSaveDoc.setValue(20)
    tabProjects.autoSaveProj.setValue(40)

    # Document Settings
    qtbot.wait(KEY_DELAY)
    tabDocs = nwPrefs.tabDocs
    nwPrefs._tabBox.setCurrentWidget(tabDocs)

    qtbot.wait(KEY_DELAY)
    qtbot.mouseClick(tabDocs.fontButton, Qt.LeftButton)

    qtbot.wait(KEY_DELAY)
    tabDocs.textSize.setValue(13)
    tabDocs.textWidth.setValue(700)
    tabDocs.focusWidth.setValue(900)
    tabDocs.textMargin.setValue(45)
    tabDocs.tabWidth.setValue(45)

    qtbot.wait(KEY_DELAY)
    assert not tabDocs.hideFocusFooter.isChecked()
    qtbot.mouseClick(tabDocs.hideFocusFooter, Qt.LeftButton)
    assert tabDocs.hideFocusFooter.isChecked()

    qtbot.wait(KEY_DELAY)
    assert not tabDocs.doJustify.isChecked()
    qtbot.mouseClick(tabDocs.doJustify, Qt.LeftButton)
    assert tabDocs.doJustify.isChecked()

    # Editor Settings
    qtbot.wait(KEY_DELAY)
    tabEditor = nwPrefs.tabEditor
    nwPrefs._tabBox.setCurrentWidget(tabEditor)

    qtbot.wait(KEY_DELAY)
    assert not tabEditor.showTabsNSpaces.isChecked()
    qtbot.mouseClick(tabEditor.showTabsNSpaces, Qt.LeftButton)
    assert tabEditor.showTabsNSpaces.isChecked()

    qtbot.wait(KEY_DELAY)
    assert not tabEditor.showLineEndings.isChecked()
    qtbot.mouseClick(tabEditor.showLineEndings, Qt.LeftButton)
    assert tabEditor.showLineEndings.isChecked()

    qtbot.wait(KEY_DELAY)
    assert not tabEditor.autoScroll.isChecked()
    qtbot.mouseClick(tabEditor.autoScroll, Qt.LeftButton)
    assert tabEditor.autoScroll.isChecked()

    # Syntax Settings
    qtbot.wait(KEY_DELAY)
    tabSyntax = nwPrefs.tabSyntax
    nwPrefs._tabBox.setCurrentWidget(tabSyntax)

    qtbot.wait(KEY_DELAY)
    assert tabSyntax.highlightQuotes.isChecked()
    qtbot.mouseClick(tabSyntax.highlightQuotes, Qt.LeftButton)
    assert not tabSyntax.highlightQuotes.isChecked()

    qtbot.wait(KEY_DELAY)
    assert tabSyntax.highlightEmph.isChecked()
    qtbot.mouseClick(tabSyntax.highlightEmph, Qt.LeftButton)
    assert not tabSyntax.highlightEmph.isChecked()

    # Automation Settings
    qtbot.wait(KEY_DELAY)
    tabAuto = nwPrefs.tabAuto
    nwPrefs._tabBox.setCurrentWidget(tabAuto)

    qtbot.wait(KEY_DELAY)
    assert tabAuto.autoSelect.isChecked()
    qtbot.mouseClick(tabAuto.autoSelect, Qt.LeftButton)
    assert not tabAuto.autoSelect.isChecked()

    qtbot.wait(KEY_DELAY)
    assert tabAuto.doReplace.isChecked()
    qtbot.mouseClick(tabAuto.doReplace, Qt.LeftButton)
    assert not tabAuto.doReplace.isChecked()

    qtbot.wait(KEY_DELAY)
    assert not tabAuto.doReplaceSQuote.isEnabled()
    assert not tabAuto.doReplaceDQuote.isEnabled()
    assert not tabAuto.doReplaceDash.isEnabled()
    assert not tabAuto.doReplaceDots.isEnabled()

    # Quotation Style
    qtbot.wait(KEY_DELAY)
    tabQuote = nwPrefs.tabQuote
    nwPrefs._tabBox.setCurrentWidget(tabQuote)

    monkeypatch.setattr(GuiQuoteSelect, "selectedQuote", "'")
    monkeypatch.setattr(GuiQuoteSelect, "exec_", lambda *a: QDialog.Accepted)
    qtbot.mouseClick(tabQuote.btnDoubleStyleC, Qt.LeftButton)

    # Save and Check Config
    qtbot.mouseClick(nwPrefs.buttonBox.button(QDialogButtonBox.Ok), Qt.LeftButton)
    nwPrefs._doClose()

    assert CONFIG.saveConfig()
    projFile = tstPaths.cnfDir / "novelwriter.conf"
    testFile = tstPaths.outDir / "guiPreferences_novelwriter.conf"
    compFile = tstPaths.refDir / "guiPreferences_novelwriter.conf"
    copyfile(projFile, testFile)
    ignTuple = (
        "timestamp", "font", "lastnotes", "localisation", "geometry",
        "preferences", "projcols", "mainpane", "docpane", "viewpane",
        "outlinepane", "textfont", "textsize", "lastpath", "backuppath"
    )
    assert cmpFiles(testFile, compFile, ignoreStart=ignTuple)

    # Clean up
    nwGUI.closeMain()

    # qtbot.stop()

# END Test testDlgPreferences_Main
