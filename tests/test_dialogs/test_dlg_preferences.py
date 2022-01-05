"""
novelWriter – Preferences Dialog Class Tester
=============================================

This file is a part of novelWriter
Copyright 2018–2022, Veronica Berglyd Olsen

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

import os
import pytest
import novelwriter

from shutil import copyfile
from tools import cmpFiles, getGuiItem

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialogButtonBox, QDialog, QAction, QFileDialog, QFontDialog, QMessageBox
)

from novelwriter.config import Config
from novelwriter.dialogs import GuiPreferences, GuiQuoteSelect

keyDelay = 2
typeDelay = 1
stepDelay = 20


@pytest.mark.gui
def testDlgPreferences_Main(qtbot, monkeypatch, fncDir, outDir, refDir):
    """Test the load project wizard.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "warning", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "information", lambda *a: QMessageBox.Yes)

    # Must create a clean config and GUI object as the test-wide
    # novelwriter.CONFIG object is created on import an can be tainted by other tests
    confFile = os.path.join(fncDir, "novelwriter.conf")
    if os.path.isfile(confFile):
        os.unlink(confFile)
    theConf = Config()
    theConf.initConfig(fncDir, fncDir)
    theConf.setLastPath("")
    origConf = novelwriter.CONFIG
    novelwriter.CONFIG = theConf

    nwGUI = novelwriter.main(["--testmode", "--config=%s" % fncDir, "--data=%s" % fncDir])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.wait(stepDelay)

    theConf = nwGUI.mainConf
    assert theConf.confPath == fncDir

    monkeypatch.setattr(GuiPreferences, "exec_", lambda *a: None)
    monkeypatch.setattr(GuiPreferences, "result", lambda *a: QDialog.Accepted)
    monkeypatch.setattr(nwGUI.docEditor.spEnchant, "listDictionaries", lambda: [("en", "none")])

    nwGUI.mainMenu.aPreferences.activate(QAction.Trigger)
    qtbot.waitUntil(lambda: getGuiItem("GuiPreferences") is not None, timeout=1000)

    nwPrefs = getGuiItem("GuiPreferences")
    assert isinstance(nwPrefs, GuiPreferences)
    nwPrefs.show()
    assert nwPrefs.mainConf.confPath == fncDir

    # General Settings
    qtbot.wait(keyDelay)
    tabGeneral = nwPrefs.tabGeneral
    nwPrefs._tabBox.setCurrentWidget(tabGeneral)

    qtbot.wait(keyDelay)
    assert tabGeneral.showFullPath.isChecked()
    qtbot.mouseClick(tabGeneral.showFullPath, Qt.LeftButton)
    assert not tabGeneral.showFullPath.isChecked()

    qtbot.wait(keyDelay)
    assert not tabGeneral.hideVScroll.isChecked()
    qtbot.mouseClick(tabGeneral.hideVScroll, Qt.LeftButton)
    assert tabGeneral.hideVScroll.isChecked()

    qtbot.wait(keyDelay)
    assert not tabGeneral.hideHScroll.isChecked()
    qtbot.mouseClick(tabGeneral.hideHScroll, Qt.LeftButton)
    assert tabGeneral.hideHScroll.isChecked()

    # Check font button
    monkeypatch.setattr(QFontDialog, "getFont", lambda font, obj: (font, True))
    qtbot.mouseClick(tabGeneral.fontButton, Qt.LeftButton)

    qtbot.wait(keyDelay)
    tabGeneral.guiFontSize.setValue(12)

    # Projects Settings
    qtbot.wait(keyDelay)
    tabProjects = nwPrefs.tabProjects
    nwPrefs._tabBox.setCurrentWidget(tabProjects)
    tabProjects.backupPath = "no/where"

    qtbot.wait(keyDelay)
    assert not tabProjects.backupOnClose.isChecked()
    qtbot.mouseClick(tabProjects.backupOnClose, Qt.LeftButton)
    assert tabProjects.backupOnClose.isChecked()

    # qtbot.stopForInteraction()

    # Check Browse button
    monkeypatch.setattr(QFileDialog, "getExistingDirectory", lambda *a, **k: "")
    assert not tabProjects._backupFolder()
    monkeypatch.setattr(QFileDialog, "getExistingDirectory", lambda *a, **k: "some/dir")
    qtbot.mouseClick(tabProjects.backupGetPath, Qt.LeftButton)

    qtbot.wait(keyDelay)
    tabProjects.autoSaveDoc.setValue(20)
    tabProjects.autoSaveProj.setValue(40)

    # Document Settings
    qtbot.wait(keyDelay)
    tabDocs = nwPrefs.tabDocs
    nwPrefs._tabBox.setCurrentWidget(tabDocs)

    qtbot.wait(keyDelay)
    qtbot.mouseClick(tabDocs.fontButton, Qt.LeftButton)

    qtbot.wait(keyDelay)
    tabDocs.textSize.setValue(13)
    tabDocs.textWidth.setValue(700)
    tabDocs.focusWidth.setValue(900)
    tabDocs.textMargin.setValue(45)
    tabDocs.tabWidth.setValue(45)

    qtbot.wait(keyDelay)
    assert not tabDocs.hideFocusFooter.isChecked()
    qtbot.mouseClick(tabDocs.hideFocusFooter, Qt.LeftButton)
    assert tabDocs.hideFocusFooter.isChecked()

    qtbot.wait(keyDelay)
    assert not tabDocs.doJustify.isChecked()
    qtbot.mouseClick(tabDocs.doJustify, Qt.LeftButton)
    assert tabDocs.doJustify.isChecked()

    # Editor Settings
    qtbot.wait(keyDelay)
    tabEditor = nwPrefs.tabEditor
    nwPrefs._tabBox.setCurrentWidget(tabEditor)

    qtbot.wait(keyDelay)
    assert not tabEditor.showTabsNSpaces.isChecked()
    qtbot.mouseClick(tabEditor.showTabsNSpaces, Qt.LeftButton)
    assert tabEditor.showTabsNSpaces.isChecked()

    qtbot.wait(keyDelay)
    assert not tabEditor.showLineEndings.isChecked()
    qtbot.mouseClick(tabEditor.showLineEndings, Qt.LeftButton)
    assert tabEditor.showLineEndings.isChecked()

    qtbot.wait(keyDelay)
    assert not tabEditor.autoScroll.isChecked()
    qtbot.mouseClick(tabEditor.autoScroll, Qt.LeftButton)
    assert tabEditor.autoScroll.isChecked()

    qtbot.wait(keyDelay)
    tabEditor.scrollPastEnd.setValue(0)

    qtbot.wait(keyDelay)
    tabEditor.bigDocLimit.setValue(500)

    # Syntax Settings
    qtbot.wait(keyDelay)
    tabSyntax = nwPrefs.tabSyntax
    nwPrefs._tabBox.setCurrentWidget(tabSyntax)

    qtbot.wait(keyDelay)
    assert tabSyntax.highlightQuotes.isChecked()
    qtbot.mouseClick(tabSyntax.highlightQuotes, Qt.LeftButton)
    assert not tabSyntax.highlightQuotes.isChecked()

    qtbot.wait(keyDelay)
    assert tabSyntax.highlightEmph.isChecked()
    qtbot.mouseClick(tabSyntax.highlightEmph, Qt.LeftButton)
    assert not tabSyntax.highlightEmph.isChecked()

    # Automation Settings
    qtbot.wait(keyDelay)
    tabAuto = nwPrefs.tabAuto
    nwPrefs._tabBox.setCurrentWidget(tabAuto)

    qtbot.wait(keyDelay)
    assert tabAuto.autoSelect.isChecked()
    qtbot.mouseClick(tabAuto.autoSelect, Qt.LeftButton)
    assert not tabAuto.autoSelect.isChecked()

    qtbot.wait(keyDelay)
    assert tabAuto.doReplace.isChecked()
    qtbot.mouseClick(tabAuto.doReplace, Qt.LeftButton)
    assert not tabAuto.doReplace.isChecked()

    qtbot.wait(keyDelay)
    assert not tabAuto.doReplaceSQuote.isEnabled()
    assert not tabAuto.doReplaceDQuote.isEnabled()
    assert not tabAuto.doReplaceDash.isEnabled()
    assert not tabAuto.doReplaceDots.isEnabled()

    # Quotation Style
    qtbot.wait(keyDelay)
    tabQuote = nwPrefs.tabQuote
    nwPrefs._tabBox.setCurrentWidget(tabQuote)

    monkeypatch.setattr(GuiQuoteSelect, "selectedQuote", "'")
    monkeypatch.setattr(GuiQuoteSelect, "exec_", lambda *args: QDialog.Accepted)
    qtbot.mouseClick(tabQuote.btnDoubleStyleC, Qt.LeftButton)

    # Save and Check Config
    qtbot.mouseClick(nwPrefs.buttonBox.button(QDialogButtonBox.Ok), Qt.LeftButton)
    nwPrefs._doClose()

    assert theConf.confChanged
    theConf.lastPath = ""

    assert nwGUI.mainConf.saveConfig()
    projFile = os.path.join(fncDir, "novelwriter.conf")
    testFile = os.path.join(outDir, "guiPreferences_novelwriter.conf")
    compFile = os.path.join(refDir, "guiPreferences_novelwriter.conf")
    copyfile(projFile, testFile)
    ignTuple = (
        "timestamp", "guifont", "lastnotes", "guilang", "geometry",
        "preferences", "treecols", "novelcols", "projcols", "mainpane",
        "docpane", "viewpane", "outlinepane", "textfont", "textsize"
    )
    assert cmpFiles(testFile, compFile, ignoreStart=ignTuple)

    # Clean up
    novelwriter.CONFIG = origConf
    nwGUI.closeMain()

    # qtbot.stopForInteraction()

# END Test testDlgPreferences_Main
