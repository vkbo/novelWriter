"""
novelWriter – Preferences Dialog Class Tester
=============================================

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

import pytest

from PyQt5.QtGui import QFontDatabase, QKeyEvent
from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtWidgets import QDialogButtonBox, QFileDialog, QFontDialog

from novelwriter import CONFIG, SHARED
from novelwriter.constants import nwConst, nwUnicode
from novelwriter.dialogs.preferences import GuiPreferences
from novelwriter.dialogs.quotes import GuiQuoteSelect

KEY_DELAY = 1


@pytest.mark.gui
def testDlgPreferences_Main(qtbot, monkeypatch, nwGUI, tstPaths):
    """Test the preferences dialog loading."""
    monkeypatch.setattr(SHARED._spelling, "listDictionaries", lambda: [("en", "English [en]")])

    # Load GUI with standard values
    prefs = GuiPreferences(nwGUI)
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

# END Test testDlgPreferences_Main


@pytest.mark.gui
def testDlgPreferences_Actions(qtbot, monkeypatch, nwGUI):
    """Test the preferences dialog actions."""
    monkeypatch.setattr(SHARED._spelling, "listDictionaries", lambda: [("en", "English [en]")])
    monkeypatch.setattr(GuiPreferences, "deleteLater", lambda *a: None)
    prefs = GuiPreferences(nwGUI)
    prefs.show()

    # Check Navigation
    vBar = prefs.mainForm.verticalScrollBar()
    old = -1
    with qtbot.waitSignal(vBar.valueChanged) as value:
        prefs.sidebar.button(0).click()
        assert value.args[0] > old
        old = value.args[0]
    with qtbot.waitSignal(vBar.valueChanged) as value:
        prefs.sidebar.button(1).click()
        assert value.args[0] > old
        old = value.args[0]
    with qtbot.waitSignal(vBar.valueChanged) as value:
        prefs.sidebar.button(2).click()
        assert value.args[0] > old
        old = value.args[0]

    # Check Search
    prefs.searchText.setText("Display language")
    with qtbot.waitSignal(vBar.valueChanged) as value:
        prefs._gotoSearch()
        assert value.args[0] < old

    # Check Apply Button
    prefs.show()
    with qtbot.waitSignal(prefs.newPreferencesReady) as signal:
        prefs.buttonBox.button(QDialogButtonBox.StandardButton.Apply).click()
        assert signal.args == [False, False, False, False]

    # Check Save Button
    prefs.show()
    with qtbot.waitSignal(prefs.newPreferencesReady) as signal:
        with qtbot.waitSignal(prefs.finished) as status:
            prefs.buttonBox.button(QDialogButtonBox.StandardButton.Save).click()
            assert signal.args == [False, False, False, False]
            assert status.args == [nwConst.DLG_FINISHED]

    # Check Close Button
    prefs.show()
    with qtbot.waitSignal(prefs.finished) as status:
        prefs.buttonBox.button(QDialogButtonBox.StandardButton.Close).click()
        assert status.args == [nwConst.DLG_FINISHED]

    # Close Using Escape Key
    prefs.show()
    with qtbot.waitSignal(prefs.finished) as status:
        event = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Escape, Qt.KeyboardModifier.NoModifier)
        prefs.keyPressEvent(event)
        assert status.args == [nwConst.DLG_FINISHED]

    # qtbot.stop()

# END Test testDlgPreferences_Actions


@pytest.mark.gui
def testDlgPreferences_Settings(qtbot, monkeypatch, nwGUI, tstPaths):
    """Test the preferences dialog settings."""
    spelling = [("en", "English [en]"), ("de", "Deutch [de]")]

    monkeypatch.setattr(SHARED._spelling, "listDictionaries", lambda: spelling)
    monkeypatch.setattr(GuiPreferences, "deleteLater", lambda *a: None)

    prefs = GuiPreferences(nwGUI)
    prefs.show()

    # Mock Font
    class MockFont:

        def family(self):
            return "TestFont"

        def pointSize(self):
            return 42

    # Appearance
    prefs.guiLocale.setCurrentIndex(prefs.guiLocale.findData("en_US"))
    prefs.guiTheme.setCurrentIndex(prefs.guiTheme.findData("default_dark"))
    with monkeypatch.context() as mp:
        mp.setattr(QFontDialog, "getFont", lambda *a: (MockFont(), True))
        prefs.guiFontButton.click()
    prefs.guiFontSize.stepDown()  # Should change it to 41
    prefs.hideVScroll.setChecked(True)
    prefs.hideHScroll.setChecked(True)

    assert CONFIG.guiLocale != "en_US"
    assert CONFIG.guiTheme != "default_dark"
    assert CONFIG.guiFont != "TestFont"
    assert CONFIG.guiFontSize < 42
    assert CONFIG.hideVScroll is False
    assert CONFIG.hideHScroll is False

    # Document Style
    prefs.guiSyntax.setCurrentIndex(prefs.guiSyntax.findData("default_dark"))
    with monkeypatch.context() as mp:
        mp.setattr(QFontDialog, "getFont", lambda *a: (MockFont(), True))
        prefs.textFontButton.click()
    prefs.textSize.stepDown()  # Should change it to 41
    prefs.emphLabels.setChecked(False)
    prefs.showFullPath.setChecked(False)
    prefs.incNotesWCount.setChecked(False)

    assert CONFIG.guiSyntax != "default_dark"
    assert CONFIG.textFont != "testFont"
    assert CONFIG.textSize < 42
    assert CONFIG.emphLabels is True
    assert CONFIG.showFullPath is True
    assert CONFIG.incNotesWCount is True

    # Auto Save
    prefs.autoSaveDoc.stepUp()
    prefs.autoSaveProj.stepUp()

    assert CONFIG.autoSaveDoc == 30
    assert CONFIG.autoSaveProj == 60

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
    prefs.allowOpenSQuote.setChecked(True)
    prefs.allowOpenDQuote.setChecked(False)
    prefs.highlightQuotes.setChecked(False)
    prefs.highlightEmph.setChecked(False)
    prefs.showMultiSpaces.setChecked(False)

    assert prefs.allowOpenSQuote.isEnabled() is False
    assert prefs.allowOpenDQuote.isEnabled() is False

    assert CONFIG.highlightQuotes is True
    assert CONFIG.allowOpenSQuote is False
    assert CONFIG.allowOpenDQuote is True
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
        prefs.btnSingleStyleO.click()
    with monkeypatch.context() as mp:
        mp.setattr(GuiQuoteSelect, "getQuote", lambda *a, **k: (nwUnicode.U_RSAQUO, True))
        prefs.btnSingleStyleC.click()
    with monkeypatch.context() as mp:
        mp.setattr(GuiQuoteSelect, "getQuote", lambda *a, **k: (nwUnicode.U_LAQUO, True))
        prefs.btnDoubleStyleO.click()
    with monkeypatch.context() as mp:
        mp.setattr(GuiQuoteSelect, "getQuote", lambda *a, **k: (nwUnicode.U_RAQUO, True))
        prefs.btnDoubleStyleC.click()

    assert CONFIG.fmtSQuoteOpen == nwUnicode.U_LSQUO
    assert CONFIG.fmtSQuoteClose == nwUnicode.U_RSQUO
    assert CONFIG.fmtDQuoteOpen == nwUnicode.U_LDQUO
    assert CONFIG.fmtDQuoteClose == nwUnicode.U_RDQUO

    # Save Settings
    with monkeypatch.context() as mp:
        mp.setattr(QFontDatabase, "families", lambda *a: ["TestFont"])
        with qtbot.waitSignal(prefs.newPreferencesReady) as signal:
            prefs.buttonBox.button(QDialogButtonBox.StandardButton.Apply).click()
            assert signal.args == [True, True, True, True]

    # Check Settings
    # ==============

    # Appearance
    assert CONFIG.guiLocale == "en_US"
    assert CONFIG.guiTheme == "default_dark"
    assert CONFIG.guiFont == "TestFont"
    assert CONFIG.guiFontSize == 41
    assert CONFIG.hideVScroll is True
    assert CONFIG.hideHScroll is True

    # Document Style
    assert CONFIG.guiSyntax == "default_dark"
    assert CONFIG.textFont == "TestFont"
    assert CONFIG.textSize == 41
    assert CONFIG.emphLabels is False
    assert CONFIG.showFullPath is False
    assert CONFIG.incNotesWCount is False

    # Auto Save
    assert CONFIG.autoSaveDoc == 31
    assert CONFIG.autoSaveProj == 61

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
    assert CONFIG.highlightQuotes is False
    assert CONFIG.allowOpenSQuote is True
    assert CONFIG.allowOpenDQuote is False
    assert CONFIG.highlightEmph is False
    assert CONFIG.showMultiSpaces is False

    # Text Automation
    assert CONFIG.doReplace is False
    assert CONFIG.doReplaceSQuote is False
    assert CONFIG.doReplaceDQuote is False
    assert CONFIG.doReplaceDash is False
    assert CONFIG.doReplaceDots is False
    assert CONFIG.fmtPadBefore == "!?:"
    assert CONFIG.fmtPadAfter == "¡¿"
    assert CONFIG.fmtPadThin is True

    # Quotation Style
    assert CONFIG.fmtSQuoteOpen == nwUnicode.U_LSAQUO
    assert CONFIG.fmtSQuoteClose == nwUnicode.U_RSAQUO
    assert CONFIG.fmtDQuoteOpen == nwUnicode.U_LAQUO
    assert CONFIG.fmtDQuoteClose == nwUnicode.U_RAQUO

    # qtbot.stop()

# END Test testDlgPreferences_Settings
