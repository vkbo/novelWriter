"""
novelWriter – Preferences Dialog Class Tester
=============================================

This file is a part of novelWriter
Copyright (C) 2020 Veronica Berglyd Olsen and novelWriter contributors

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

from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtGui import QFont, QFontDatabase, QKeyEvent
from PyQt5.QtWidgets import QAction, QFileDialog, QFontDialog

from novelwriter import CONFIG, SHARED
from novelwriter.constants import nwUnicode
from novelwriter.dialogs.preferences import GuiPreferences
from novelwriter.dialogs.quotes import GuiQuoteSelect
from novelwriter.types import QtDialogCancel, QtDialogSave, QtModNone

KEY_DELAY = 1


@pytest.mark.gui
def testDlgPreferences_Main(qtbot, monkeypatch, nwGUI, tstPaths):
    """Test the preferences dialog loading."""
    monkeypatch.setattr(SHARED._spelling, "listDictionaries", lambda: [("en", "English [en]")])
    monkeypatch.setattr(GuiPreferences, "exec", lambda *a: None)

    # Load GUI with standard values
    nwGUI.mainMenu.aPreferences.activate(QAction.ActionEvent.Trigger)
    qtbot.waitUntil(lambda: SHARED.findTopLevelWidget(GuiPreferences) is not None, timeout=1000)
    prefs = SHARED.findTopLevelWidget(GuiPreferences)
    assert isinstance(prefs, GuiPreferences)
    prefs.show()

    # Check Languages
    languages = [prefs.guiLocale.itemData(i) for i in range(prefs.guiLocale.count())]
    assert len(languages) > 0
    assert "en_GB" in languages

    # Check GUI Themes
    themes = [prefs.guiTheme.itemData(i) for i in range(prefs.guiTheme.count())]
    assert len(themes) >= 5
    assert "default" in themes

    # Check GUI Syntax
    syntax = [prefs.guiSyntax.itemData(i) for i in range(prefs.guiSyntax.count())]
    assert len(syntax) >= 10
    assert "default_dark" in syntax
    assert "default_light" in syntax

    # Check Spell Checking
    spelling = [prefs.spellLanguage.itemData(i) for i in range(prefs.spellLanguage.count())]
    assert len(spelling) == 1
    assert spelling == ["en"]

    prefs.close()

    # Check Fallback Values
    with monkeypatch.context() as mp:
        mp.setattr(CONFIG, "hasEnchant", False)
        prefs = GuiPreferences(nwGUI)
        prefs.show()

        # Check Spell Checking
        spelling = [prefs.spellLanguage.itemData(i) for i in range(prefs.spellLanguage.count())]
        assert len(spelling) == 1
        assert spelling == [""]

        prefs.close()

    # qtbot.stop()


@pytest.mark.gui
def testDlgPreferences_Actions(qtbot, monkeypatch, nwGUI):
    """Test the preferences dialog actions."""
    monkeypatch.setattr(SHARED._spelling, "listDictionaries", lambda: [("en", "English [en]")])
    prefs = GuiPreferences(nwGUI)
    with qtbot.waitExposed(prefs):
        prefs.show()

    # Check Navigation
    vBar = prefs.mainForm.verticalScrollBar()
    old = -1
    with qtbot.waitSignal(vBar.valueChanged) as value:
        prefs.sidebar.button(1).click()
        assert value.args[0] > old
        old = value.args[0]
    with qtbot.waitSignal(vBar.valueChanged) as value:
        prefs.sidebar.button(2).click()
        assert value.args[0] > old
        old = value.args[0]
    with qtbot.waitSignal(vBar.valueChanged) as value:
        prefs.sidebar.button(3).click()
        assert value.args[0] > old
        old = value.args[0]

    # Check Search
    prefs.searchText.setText("Display language")
    with qtbot.waitSignal(vBar.valueChanged) as value:
        prefs._gotoSearch()
        assert value.args[0] < old

    # Check Save Button
    prefs.show()
    with qtbot.waitSignal(prefs.newPreferencesReady) as signal:
        prefs.buttonBox.button(QtDialogSave).click()
        assert signal.args == [False, False, False, False]

    # Check Close Button
    prefs.show()
    prefs.buttonBox.button(QtDialogCancel).click()
    assert prefs.isHidden() is True

    # Close Using Escape Key
    prefs.show()
    event = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Escape, QtModNone)
    prefs.keyPressEvent(event)
    assert prefs.isHidden() is True

    # qtbot.stop()


@pytest.mark.gui
def testDlgPreferences_Settings(qtbot, monkeypatch, nwGUI, tstPaths):
    """Test the preferences dialog settings."""
    spelling = [("en", "English [en]"), ("de", "Deutch [de]")]
    languages = [("en_GB", "British English"), ("en_US", "US English")]

    monkeypatch.setattr(SHARED._spelling, "listDictionaries", lambda: spelling)
    monkeypatch.setattr(CONFIG, "listLanguages", lambda *a: languages)

    prefs = GuiPreferences(nwGUI)
    with qtbot.waitExposed(prefs):
        prefs.show()

    # Appearance
    prefs.guiLocale.setCurrentIndex(prefs.guiLocale.findData("en_US"))
    prefs.guiTheme.setCurrentIndex(prefs.guiTheme.findData("default_dark"))
    with monkeypatch.context() as mp:
        mp.setattr(QFontDialog, "getFont", lambda *a, **k: (QFont(), True))
        prefs.nativeFont.setChecked(True)  # Use OS font dialog
        prefs.guiFontButton.click()
    prefs.hideVScroll.setChecked(True)
    prefs.hideHScroll.setChecked(True)

    assert CONFIG.guiLocale != "en_US"
    assert CONFIG.guiTheme != "default_dark"
    assert CONFIG.guiFont.family() != ""
    assert CONFIG.hideVScroll is False
    assert CONFIG.hideHScroll is False

    # Document Style
    prefs.guiSyntax.setCurrentIndex(prefs.guiSyntax.findData("default_dark"))
    with monkeypatch.context() as mp:
        mp.setattr(QFontDialog, "getFont", lambda *a, **k: (QFont(), True))
        prefs.nativeFont.setChecked(False)  # Use Qt font dialog
        prefs.textFontButton.click()
    prefs.emphLabels.setChecked(False)
    prefs.showFullPath.setChecked(False)
    prefs.incNotesWCount.setChecked(False)

    assert CONFIG.guiSyntax != "default_dark"
    assert CONFIG.textFont.family() != ""
    assert CONFIG.emphLabels is True
    assert CONFIG.showFullPath is True
    assert CONFIG.incNotesWCount is True

    # Behaviour
    prefs.autoSaveDoc.stepUp()
    prefs.autoSaveProj.stepUp()
    prefs.askBeforeExit.setChecked(False)

    assert CONFIG.autoSaveDoc == 30
    assert CONFIG.autoSaveProj == 60
    assert CONFIG.askBeforeExit is True

    # Project Backup
    with monkeypatch.context() as mp:
        mp.setattr(QFileDialog, "getExistingDirectory", lambda *a, **k: str(tstPaths.testDir))
        prefs.backupGetPath.click()
        assert prefs.backupPath == str(tstPaths.testDir)
    prefs.backupOnClose.setChecked(True)
    assert prefs.askBeforeBackup.isEnabled() is True
    prefs.askBeforeBackup.setChecked(False)

    assert CONFIG._backupPath != tstPaths.testDir
    assert CONFIG.backupOnClose is False
    assert CONFIG.askBeforeBackup is True

    # Session Timer
    prefs.stopWhenIdle.setChecked(False)
    prefs.userIdleTime.stepUp()

    assert CONFIG.stopWhenIdle is True
    assert CONFIG.userIdleTime == 300

    # Text Flow
    prefs.textWidth.stepDown()
    prefs.focusWidth.stepDown()
    prefs.hideFocusFooter.setChecked(True)
    prefs.doJustify.setChecked(True)
    prefs.textMargin.stepUp()
    prefs.tabWidth.stepUp()

    assert CONFIG.textWidth == 700
    assert CONFIG.focusWidth == 800
    assert CONFIG.hideFocusFooter is False
    assert CONFIG.doJustify is False
    assert CONFIG.textMargin == 40
    assert CONFIG.tabWidth == 40

    # Text Editing
    prefs.spellLanguage.setCurrentIndex(prefs.spellLanguage.findData("de"))
    prefs.autoSelect.setChecked(False)
    prefs.showTabsNSpaces.setChecked(True)
    prefs.showLineEndings.setChecked(True)

    assert CONFIG.spellLanguage != "de"
    assert CONFIG.autoSelect is True
    assert CONFIG.showTabsNSpaces is False
    assert CONFIG.showLineEndings is False

    # Editor Scrolling
    prefs.scrollPastEnd.setChecked(False)
    prefs.autoScroll.setChecked(True)
    prefs.autoScrollPos.stepUp()

    assert CONFIG.scrollPastEnd is True
    assert CONFIG.autoScroll is False
    assert CONFIG.autoScrollPos == 30

    # Text Highlighting
    prefs.dialogStyle.setCurrentData(3, 0)
    prefs.allowOpenDial.setChecked(False)
    prefs.dialogLine.setText("–")
    prefs.narratorBreak.setText("–")
    prefs.narratorDialog.setText("–")
    prefs.altDialogOpen.setText("<")
    prefs.altDialogClose.setText(">")
    prefs.highlightEmph.setChecked(False)
    prefs.showMultiSpaces.setChecked(False)

    assert CONFIG.dialogStyle == 2
    assert CONFIG.allowOpenDial is True
    assert CONFIG.dialogLine == ""
    assert CONFIG.narratorBreak == ""
    assert CONFIG.narratorDialog == ""
    assert CONFIG.altDialogOpen == ""
    assert CONFIG.altDialogClose == ""
    assert CONFIG.highlightEmph is True
    assert CONFIG.showMultiSpaces is True

    # Text Automation
    prefs.doReplaceSQuote.setChecked(False)
    prefs.doReplaceDQuote.setChecked(False)
    prefs.doReplaceDash.setChecked(False)
    prefs.doReplaceDots.setChecked(False)
    prefs.doReplace.setChecked(False)
    prefs.fmtPadBefore.setText("!?:")
    prefs.fmtPadAfter.setText("¡¿")
    prefs.fmtPadThin.setChecked(True)

    assert prefs.doReplaceSQuote.isEnabled() is False
    assert prefs.doReplaceDQuote.isEnabled() is False
    assert prefs.doReplaceDash.isEnabled() is False
    assert prefs.doReplaceDots.isEnabled() is False
    assert prefs.fmtPadThin.isEnabled() is False

    assert CONFIG.doReplace is True
    assert CONFIG.doReplaceSQuote is True
    assert CONFIG.doReplaceDQuote is True
    assert CONFIG.doReplaceDash is True
    assert CONFIG.doReplaceDots is True
    assert CONFIG.fmtPadBefore == ""
    assert CONFIG.fmtPadAfter == ""
    assert CONFIG.fmtPadThin is False

    # Quotation Style
    with monkeypatch.context() as mp:
        mp.setattr(GuiQuoteSelect, "getQuote", lambda *a, **k: (nwUnicode.U_LSAQUO, True))
        prefs.btnSQuoteOpen.click()
    with monkeypatch.context() as mp:
        mp.setattr(GuiQuoteSelect, "getQuote", lambda *a, **k: (nwUnicode.U_RSAQUO, True))
        prefs.btnSQuoteClose.click()
    with monkeypatch.context() as mp:
        mp.setattr(GuiQuoteSelect, "getQuote", lambda *a, **k: (nwUnicode.U_LAQUO, True))
        prefs.btnDQuoteOpen.click()
    with monkeypatch.context() as mp:
        mp.setattr(GuiQuoteSelect, "getQuote", lambda *a, **k: (nwUnicode.U_RAQUO, True))
        prefs.btnDQuoteClose.click()

    assert CONFIG.fmtSQuoteOpen == nwUnicode.U_LSQUO
    assert CONFIG.fmtSQuoteClose == nwUnicode.U_RSQUO
    assert CONFIG.fmtDQuoteOpen == nwUnicode.U_LDQUO
    assert CONFIG.fmtDQuoteClose == nwUnicode.U_RDQUO

    # Save Settings
    with monkeypatch.context() as mp:
        mp.setattr(QFontDatabase, "families", lambda *a: ["TestFont"])
        with qtbot.waitSignal(prefs.newPreferencesReady) as signal:
            prefs.buttonBox.button(QtDialogSave).click()
            assert signal.args == [True, True, True, True]

    # Check Settings
    # ==============

    # Appearance
    assert CONFIG.guiLocale == "en_US"
    assert CONFIG.guiTheme == "default_dark"
    assert CONFIG.guiFont == QFont()
    assert CONFIG.hideVScroll is True
    assert CONFIG.hideHScroll is True

    # Document Style
    assert CONFIG.guiSyntax == "default_dark"
    assert CONFIG.textFont == QFont()
    assert CONFIG.emphLabels is False
    assert CONFIG.showFullPath is False
    assert CONFIG.incNotesWCount is False

    # Behaviour
    assert CONFIG.autoSaveDoc == 31
    assert CONFIG.autoSaveProj == 61
    assert CONFIG.askBeforeExit is False

    # Project Backup
    assert CONFIG._backupPath == tstPaths.testDir
    assert CONFIG.backupOnClose is True
    assert CONFIG.askBeforeBackup is False

    # Session Timer
    assert CONFIG.stopWhenIdle is False
    assert CONFIG.userIdleTime == 330

    # Text Flow
    assert CONFIG.textWidth == 690
    assert CONFIG.focusWidth == 790
    assert CONFIG.hideFocusFooter is True
    assert CONFIG.doJustify is True
    assert CONFIG.textMargin == 41
    assert CONFIG.tabWidth == 41

    # Text Editing
    assert CONFIG.spellLanguage == "de"
    assert CONFIG.autoSelect is False
    assert CONFIG.showTabsNSpaces is True
    assert CONFIG.showLineEndings is True

    # Editor Scrolling
    assert CONFIG.scrollPastEnd is False
    assert CONFIG.autoScroll is True
    assert CONFIG.autoScrollPos == 31

    # Text Highlighting
    assert CONFIG.dialogStyle == 3
    assert CONFIG.allowOpenDial is False
    assert CONFIG.dialogLine == "–"
    assert CONFIG.narratorBreak == "–"
    assert CONFIG.narratorDialog == "–"
    assert CONFIG.altDialogOpen == "<"
    assert CONFIG.altDialogClose == ">"
    assert CONFIG.highlightEmph is False
    assert CONFIG.showMultiSpaces is False

    # Text Automation
    assert CONFIG.doReplace is False
    assert CONFIG.doReplaceSQuote is False
    assert CONFIG.doReplaceDQuote is False
    assert CONFIG.doReplaceDash is False
    assert CONFIG.doReplaceDots is False
    assert CONFIG.fmtPadBefore == "!:?"
    assert CONFIG.fmtPadAfter == "¡¿"
    assert CONFIG.fmtPadThin is True

    # Quotation Style
    assert CONFIG.fmtSQuoteOpen == nwUnicode.U_LSAQUO
    assert CONFIG.fmtSQuoteClose == nwUnicode.U_RSAQUO
    assert CONFIG.fmtDQuoteOpen == nwUnicode.U_LAQUO
    assert CONFIG.fmtDQuoteClose == nwUnicode.U_RAQUO

    # qtbot.stop()
