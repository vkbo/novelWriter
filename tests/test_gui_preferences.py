# -*- coding: utf-8 -*-
"""novelWriter Dialog Class Tester
"""

import nw
import pytest
import os

from shutil import copyfile
from tools import cmpFiles, getGuiItem

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialogButtonBox, QDialog, QAction, QFileDialog, QFontDialog, QMessageBox
)

from nw.gui import GuiPreferences
from nw.config import Config
from nw.gui.custom import QuotesDialog

keyDelay = 2
typeDelay = 1
stepDelay = 20

@pytest.mark.gui
def testGuiPreferences_Main(qtbot, monkeypatch, fncDir, outDir, refDir):
    """Test the load project wizard.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "question", lambda *args: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "information", lambda *args: QMessageBox.Yes)

    # Must create a clean config and GUI object as the test-wide
    # nw.CONFIG object is created on import an can be tainted by other tests
    confFile = os.path.join(fncDir, "novelwriter.conf")
    if os.path.isfile(confFile):
        os.unlink(confFile)
    theConf = Config()
    theConf.initConfig(fncDir, fncDir)
    theConf.setLastPath("")
    origConf = nw.CONFIG
    nw.CONFIG = theConf

    nwGUI = nw.main(["--testmode", "--config=%s" % fncDir, "--data=%s" % fncDir])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)
    qtbot.wait(20)

    theConf = nwGUI.mainConf
    assert theConf.confPath == fncDir

    monkeypatch.setattr(GuiPreferences, "exec_", lambda *args: None)
    monkeypatch.setattr(GuiPreferences, "result", lambda *args: QDialog.Accepted)
    nwGUI.mainMenu.aPreferences.activate(QAction.Trigger)
    qtbot.waitUntil(lambda: getGuiItem("GuiPreferences") is not None, timeout=1000)

    nwPrefs = getGuiItem("GuiPreferences")
    assert isinstance(nwPrefs, GuiPreferences)
    nwPrefs.show()
    assert nwPrefs.mainConf.confPath == fncDir

    # qtbot.stopForInteraction()
    # General Settings
    qtbot.wait(keyDelay)
    tabGeneral = nwPrefs.tabGeneral
    nwPrefs._tabBox.setCurrentWidget(tabGeneral)

    qtbot.wait(keyDelay)
    assert not tabGeneral.preferDarkIcons.isChecked()
    qtbot.mouseClick(tabGeneral.preferDarkIcons, Qt.LeftButton)
    assert tabGeneral.preferDarkIcons.isChecked()

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

    # Check Browse button
    monkeypatch.setattr(QFileDialog, "getExistingDirectory", lambda *args, **kwargs: "")
    assert not tabProjects._backupFolder()
    monkeypatch.setattr(QFileDialog, "getExistingDirectory", lambda *args, **kwargs: "some/dir")
    qtbot.mouseClick(tabProjects.backupGetPath, Qt.LeftButton)

    qtbot.wait(keyDelay)
    tabProjects.autoSaveDoc.setValue(20)
    tabProjects.autoSaveProj.setValue(40)

    # Text Layout Settings
    qtbot.wait(keyDelay)
    tabLayout = nwPrefs.tabLayout
    nwPrefs._tabBox.setCurrentWidget(tabLayout)

    qtbot.wait(keyDelay)
    qtbot.mouseClick(tabLayout.fontButton, Qt.LeftButton)

    qtbot.wait(keyDelay)
    tabLayout.textStyleSize.setValue(13)
    tabLayout.textFlowMax.setValue(700)
    tabLayout.focusDocWidth.setValue(900)
    tabLayout.textMargin.setValue(45)
    tabLayout.tabWidth.setValue(45)

    qtbot.wait(keyDelay)
    assert not tabLayout.textFlowFixed.isChecked()
    qtbot.mouseClick(tabLayout.textFlowFixed, Qt.LeftButton)
    assert tabLayout.textFlowFixed.isChecked()

    qtbot.wait(keyDelay)
    assert not tabLayout.hideFocusFooter.isChecked()
    qtbot.mouseClick(tabLayout.hideFocusFooter, Qt.LeftButton)
    assert tabLayout.hideFocusFooter.isChecked()

    qtbot.wait(keyDelay)
    assert tabLayout.textJustify.isChecked()
    qtbot.mouseClick(tabLayout.textJustify, Qt.LeftButton)
    assert not tabLayout.textJustify.isChecked()

    qtbot.wait(keyDelay)
    assert tabLayout.scrollPastEnd.isChecked()
    qtbot.mouseClick(tabLayout.scrollPastEnd, Qt.LeftButton)
    assert not tabLayout.scrollPastEnd.isChecked()

    qtbot.wait(keyDelay)
    assert not tabLayout.autoScroll.isChecked()
    qtbot.mouseClick(tabLayout.autoScroll, Qt.LeftButton)
    assert tabLayout.autoScroll.isChecked()

    # Editor Settings
    qtbot.wait(keyDelay)
    tabEditing = nwPrefs.tabEditing
    nwPrefs._tabBox.setCurrentWidget(tabEditing)

    qtbot.wait(keyDelay)
    assert tabEditing.highlightQuotes.isChecked()
    qtbot.mouseClick(tabEditing.highlightQuotes, Qt.LeftButton)
    assert not tabEditing.highlightQuotes.isChecked()

    qtbot.wait(keyDelay)
    assert tabEditing.highlightEmph.isChecked()
    qtbot.mouseClick(tabEditing.highlightEmph, Qt.LeftButton)
    assert not tabEditing.highlightEmph.isChecked()

    qtbot.wait(keyDelay)
    assert not tabEditing.showTabsNSpaces.isChecked()
    qtbot.mouseClick(tabEditing.showTabsNSpaces, Qt.LeftButton)
    assert tabEditing.showTabsNSpaces.isChecked()

    qtbot.wait(keyDelay)
    assert not tabEditing.showLineEndings.isChecked()
    qtbot.mouseClick(tabEditing.showLineEndings, Qt.LeftButton)
    assert tabEditing.showLineEndings.isChecked()

    qtbot.wait(keyDelay)
    tabEditing.bigDocLimit.setValue(500)

    # Auto-Replace Settings
    qtbot.wait(keyDelay)
    tabAutoRep = nwPrefs.tabAutoRep
    nwPrefs._tabBox.setCurrentWidget(tabAutoRep)

    qtbot.wait(keyDelay)
    assert tabAutoRep.autoSelect.isChecked()
    qtbot.mouseClick(tabAutoRep.autoSelect, Qt.LeftButton)
    assert not tabAutoRep.autoSelect.isChecked()

    qtbot.wait(keyDelay)
    assert tabAutoRep.autoReplaceMain.isChecked()
    qtbot.mouseClick(tabAutoRep.autoReplaceMain, Qt.LeftButton)
    assert not tabAutoRep.autoReplaceMain.isChecked()

    qtbot.wait(keyDelay)
    assert not tabAutoRep.autoReplaceSQ.isEnabled()
    assert not tabAutoRep.autoReplaceDQ.isEnabled()
    assert not tabAutoRep.autoReplaceDash.isEnabled()
    assert not tabAutoRep.autoReplaceDots.isEnabled()

    monkeypatch.setattr(QuotesDialog, "selectedQuote", "'")
    monkeypatch.setattr(QuotesDialog, "exec_", lambda *args: QDialog.Accepted)
    qtbot.mouseClick(tabAutoRep.btnDoubleStyleC, Qt.LeftButton)

    # Save and Check Config
    qtbot.mouseClick(nwPrefs.buttonBox.button(QDialogButtonBox.Ok), Qt.LeftButton)

    assert theConf.confChanged
    theConf.lastPath = ""

    assert nwGUI.mainConf.saveConfig()
    projFile = os.path.join(fncDir, "novelwriter.conf")
    testFile = os.path.join(outDir, "guiPreferences_novelwriter.conf")
    compFile = os.path.join(refDir, "guiPreferences_novelwriter.conf")
    copyfile(projFile, testFile)
    ignoreLines = [
        2,                          # Timestamp
        9,                          # Release Notes
        12, 13, 14, 15, 16, 17, 18, # Window sizes
        7, 28,                      # Fonts (depends on system default)
    ]
    assert cmpFiles(testFile, compFile, ignoreLines)

    # Clean up
    nw.CONFIG = origConf
    nwGUI.closeMain()

    # qtbot.stopForInteraction()

# END Test testGuiPreferences_Main
