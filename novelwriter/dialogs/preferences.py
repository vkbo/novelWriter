"""
novelWriter – GUI Preferences
=============================

File History:
Created:   2019-06-10 [0.1.5] GuiPreferences
Rewritten: 2024-01-08 [2.3b1] GuiPreferences

This file is a part of novelWriter
Copyright (C) 2019 Veronica Berglyd Olsen and novelWriter contributors

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

import logging

from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QAction, QCloseEvent, QKeyEvent, QKeySequence
from PyQt6.QtWidgets import (
    QCompleter, QDialogButtonBox, QFileDialog, QHBoxLayout, QLineEdit, QMenu,
    QPushButton, QVBoxLayout, QWidget
)

from novelwriter import CONFIG, SHARED
from novelwriter.common import compact, describeFont, processDialogSymbols, uniqueCompact
from novelwriter.config import DEF_GUI_DARK, DEF_GUI_LIGHT, DEF_ICONS, DEF_TREECOL
from novelwriter.constants import nwLabels, nwQuotes, nwUnicode, trConst
from novelwriter.dialogs.quotes import GuiQuoteSelect
from novelwriter.enum import nwStandardButton
from novelwriter.extensions.configlayout import NColorLabel, NScrollableForm
from novelwriter.extensions.modified import (
    NComboBox, NDialog, NDoubleSpinBox, NIconToolButton, NSpinBox
)
from novelwriter.extensions.pagedsidebar import NPagedSideBar
from novelwriter.extensions.switch import NSwitch
from novelwriter.types import QtAlignCenter, QtRoleAccept, QtRoleReject

logger = logging.getLogger(__name__)


class GuiPreferences(NDialog):
    """GUI: Preferences Dialog."""

    newPreferencesReady = pyqtSignal(bool, bool, bool, bool)

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)

        logger.debug("Create: GuiPreferences")
        self.setObjectName("GuiPreferences")
        self.setWindowTitle(self.tr("Preferences"))
        self.setMinimumSize(600, 500)
        self.resize(*CONFIG.prefsWinSize)

        # Title
        self.titleLabel = NColorLabel(
            self.tr("Preferences"), self, color=SHARED.theme.helpText,
            scale=NColorLabel.HEADER_SCALE, indent=4,
        )

        # Search Box
        self.searchAction = QAction(SHARED.theme.getIcon("search", "apply"), "")
        self.searchAction.triggered.connect(self._gotoSearch)

        self.searchText = QLineEdit(self)
        self.searchText.setPlaceholderText(self.tr("Search"))
        self.searchText.setMinimumWidth(200)
        self.searchText.addAction(self.searchAction, QLineEdit.ActionPosition.TrailingPosition)

        # SideBar
        self.sidebar = NPagedSideBar(self)
        self.sidebar.setLabelColor(SHARED.theme.helpText)
        self.sidebar.setAccessibleName(self.titleLabel.text())
        self.sidebar.buttonClicked.connect(self._sidebarClicked)

        # Form
        self.mainForm = NScrollableForm(self)
        self.mainForm.setHelpTextStyle(SHARED.theme.helpText)

        # Buttons
        self.btnSave = SHARED.theme.getStandardButton(nwStandardButton.SAVE, self)
        self.btnSave.clicked.connect(self._doSave)

        self.btnCancel = SHARED.theme.getStandardButton(nwStandardButton.CANCEL, self)
        self.btnCancel.clicked.connect(self.reject)

        self.btnBox = QDialogButtonBox(self)
        self.btnBox.addButton(self.btnSave, QtRoleAccept)
        self.btnBox.addButton(self.btnCancel, QtRoleReject)

        # Assemble
        self.searchBox = QHBoxLayout()
        self.searchBox.addWidget(self.titleLabel)
        self.searchBox.addStretch(1)
        self.searchBox.addWidget(self.searchText, 1)

        self.mainBox = QHBoxLayout()
        self.mainBox.addWidget(self.sidebar)
        self.mainBox.addWidget(self.mainForm)
        self.mainBox.setContentsMargins(0, 0, 0, 0)

        self.outerBox = QVBoxLayout()
        self.outerBox.addLayout(self.searchBox)
        self.outerBox.addLayout(self.mainBox)
        self.outerBox.addWidget(self.btnBox)
        self.outerBox.setSpacing(8)

        self.setLayout(self.outerBox)
        self.setSizeGripEnabled(True)

        # Build Form
        self.buildForm()

        # Populate Search
        self.searchCompleter = QCompleter(self.mainForm.labels, self)
        self.searchCompleter.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.searchCompleter.setFilterMode(Qt.MatchFlag.MatchContains)
        self.searchCompleter.activated.connect(self._gotoSearch)

        self.searchText.setCompleter(self.searchCompleter)

        logger.debug("Ready: GuiPreferences")

    def __del__(self) -> None:  # pragma: no cover
        logger.debug("Delete: GuiPreferences")

    def buildForm(self) -> None:
        """Build the settings form."""
        section = 0
        iSz = SHARED.theme.baseIconSize
        boxFixed = 6*SHARED.theme.textNWidth

        # Temporary Variables
        self._guiFont = CONFIG.guiFont
        self._textFont = CONFIG.textFont

        # Label
        self.sidebar.addLabel(self.tr("General"))

        # Appearance
        # ==========

        title = self.tr("Appearance")
        section += 1
        self.sidebar.addButton(title, section)
        self.mainForm.addGroupLabel(title, section)

        # Display Language
        self.guiLocale = NComboBox(self, scrollable=True)
        self.guiLocale.setMinimumWidth(200)
        for lang, name in CONFIG.listLanguages(CONFIG.LANG_NW):
            self.guiLocale.addItem(name, lang)
        self.guiLocale.setCurrentData(CONFIG.guiLocale, "en_GB")

        self.mainForm.addRow(
            self.tr("Display language"), self.guiLocale,
            self.tr("Requires restart to take effect."), stretch=(3, 2)
        )

        # Colour Theme
        self.lightTheme = NComboBox(self, scrollable=True)
        self.lightTheme.setMinimumWidth(200)
        self.darkTheme = NComboBox(self, scrollable=True)
        self.darkTheme.setMinimumWidth(200)
        for key, theme in SHARED.theme.colourThemes.items():
            if theme.dark:
                self.darkTheme.addItem(theme.name, key)
            else:
                self.lightTheme.addItem(theme.name, key)

        self.lightTheme.setCurrentData(CONFIG.lightTheme, DEF_GUI_LIGHT)
        self.darkTheme.setCurrentData(CONFIG.darkTheme, DEF_GUI_DARK)

        self.mainForm.addRow(
            self.tr("Light colour theme"), self.lightTheme,
            self.tr("You can change theme mode from the sidebar."), stretch=(3, 2)
        )
        self.mainForm.addRow(
            self.tr("Dark colour theme"), self.darkTheme,
            self.tr("You can change theme mode from the sidebar."), stretch=(3, 2)
        )

        # Icon Theme
        self.iconTheme = NComboBox(self, scrollable=True)
        self.iconTheme.setMinimumWidth(200)
        for key, theme in SHARED.theme.iconCache.iconThemes.items():
            self.iconTheme.addItem(theme.name, key)

        self.iconTheme.setCurrentData(CONFIG.iconTheme, DEF_ICONS)

        self.mainForm.addRow(
            self.tr("Icon theme"), self.iconTheme,
            self.tr("User interface icon theme."), stretch=(3, 2)
        )

        # Application Font Family
        self.guiFont = QLineEdit(self)
        self.guiFont.setReadOnly(True)
        self.guiFont.setMinimumWidth(162)
        self.guiFont.setText(describeFont(self._guiFont))
        self.guiFont.setCursorPosition(0)
        self.guiFontButton = NIconToolButton(self, iSz, "font", "tool")
        self.guiFontButton.clicked.connect(self._selectGuiFont)
        self.mainForm.addRow(
            self.tr("Application font"), self.guiFont,
            self.tr("Requires restart to take effect."), stretch=(3, 2),
            button=self.guiFontButton
        )

        # Vertical Scrollbars
        self.hideVScroll = NSwitch(self)
        self.hideVScroll.setChecked(CONFIG.hideVScroll)
        self.mainForm.addRow(
            self.tr("Hide vertical scroll bars in main windows"), self.hideVScroll,
            self.tr("Scrolling available with mouse wheel and keys only.")
        )

        # Horizontal Scrollbars
        self.hideHScroll = NSwitch(self)
        self.hideHScroll.setChecked(CONFIG.hideHScroll)
        self.mainForm.addRow(
            self.tr("Hide horizontal scroll bars in main windows"), self.hideHScroll,
            self.tr("Scrolling available with mouse wheel and keys only.")
        )

        # Native Font Dialog
        self.nativeFont = NSwitch(self)
        self.nativeFont.setChecked(CONFIG.nativeFont)
        self.mainForm.addRow(
            self.tr("Use the system's font selection dialog"), self.nativeFont,
            self.tr("Turn off to use the Qt font dialog, which may have more options.")
        )

        # Use Character Count
        self.useCharCount = NSwitch(self)
        self.useCharCount.setChecked(CONFIG.useCharCount)
        self.mainForm.addRow(
            self.tr("Prefer character count over word count"), self.useCharCount,
            self.tr("Display character count instead where available.")
        )

        # Document Style
        # ==============

        title = self.tr("Document Style")
        section += 1
        self.sidebar.addButton(title, section)
        self.mainForm.addGroupLabel(title, section)

        # Document Font Family
        self.textFont = QLineEdit(self)
        self.textFont.setReadOnly(True)
        self.textFont.setMinimumWidth(162)
        self.textFont.setText(describeFont(CONFIG.textFont))
        self.textFont.setCursorPosition(0)
        self.textFontButton = NIconToolButton(self, iSz, "font", "tool")
        self.textFontButton.clicked.connect(self._selectTextFont)
        self.mainForm.addRow(
            self.tr("Document font"), self.textFont,
            self.tr("Applies to both document editor and viewer."), stretch=(3, 2),
            button=self.textFontButton
        )

        # Document Path
        self.showFullPath = NSwitch(self)
        self.showFullPath.setChecked(CONFIG.showFullPath)
        self.mainForm.addRow(
            self.tr("Show full path in document header"), self.showFullPath,
            self.tr("Add the parent folder names to the header.")
        )

        # Include Notes in Word Count
        self.incNotesWCount = NSwitch(self)
        self.incNotesWCount.setChecked(CONFIG.incNotesWCount)
        self.mainForm.addRow(
            self.tr("Include project notes in status bar word count"), self.incNotesWCount
        )

        # Project View
        # ============

        title = self.tr("Project View")
        section += 1
        self.sidebar.addButton(title, section)
        self.mainForm.addGroupLabel(title, section)

        # Tree Icon Colours
        self.iconColTree = NComboBox(self)
        self.iconColTree.setMinimumWidth(200)
        self.iconColTree.addItem(self.tr("Theme Colours"), DEF_TREECOL)
        for key, label in nwLabels.THEME_COLORS.items():
            self.iconColTree.addItem(trConst(label), key)
        self.iconColTree.setCurrentData(CONFIG.iconColTree, DEF_TREECOL)

        self.mainForm.addRow(
            self.tr("Project tree icon colours"), self.iconColTree,
            self.tr("Override colours for project icons."), stretch=(3, 2)
        )

        # Keep Theme Colours on Documents
        self.iconColDocs = NSwitch(self)
        self.iconColDocs.setChecked(CONFIG.iconColDocs)
        self.mainForm.addRow(
            self.tr("Keep theme colours on documents"), self.iconColDocs,
            self.tr("Only override icon colours for folders.")
        )

        # Emphasise Labels
        self.emphLabels = NSwitch(self)
        self.emphLabels.setChecked(CONFIG.emphLabels)
        self.mainForm.addRow(
            self.tr("Emphasise partition and chapter labels"), self.emphLabels,
            self.tr("Makes them stand out in the project tree."),
        )

        # Behaviour
        # =========

        title = self.tr("Behaviour")
        section += 1
        self.sidebar.addButton(title, section)
        self.mainForm.addGroupLabel(title, section)

        # Document Save Timer
        self.autoSaveDoc = NSpinBox(self)
        self.autoSaveDoc.setMinimum(5)
        self.autoSaveDoc.setMaximum(600)
        self.autoSaveDoc.setSingleStep(1)
        self.autoSaveDoc.setValue(CONFIG.autoSaveDoc)
        self.mainForm.addRow(
            self.tr("Save document interval"), self.autoSaveDoc,
            self.tr("How often the document is automatically saved."), unit=self.tr("seconds")
        )

        # Project Save Timer
        self.autoSaveProj = NSpinBox(self)
        self.autoSaveProj.setMinimum(5)
        self.autoSaveProj.setMaximum(600)
        self.autoSaveProj.setSingleStep(1)
        self.autoSaveProj.setValue(CONFIG.autoSaveProj)
        self.mainForm.addRow(
            self.tr("Save project interval"), self.autoSaveProj,
            self.tr("How often the project is automatically saved."), unit=self.tr("seconds")
        )

        # Ask before exiting novelWriter
        self.askBeforeExit = NSwitch(self)
        self.askBeforeExit.setChecked(CONFIG.askBeforeExit)
        self.mainForm.addRow(
            self.tr("Ask before exiting novelWriter"), self.askBeforeExit,
            self.tr("Only applies when a project is open.")
        )

        # Project Backup
        # ==============

        title = self.tr("Project Backup")
        section += 1
        self.sidebar.addButton(title, section)
        self.mainForm.addGroupLabel(title, section)

        # Backup Path
        self.backupPath = CONFIG.backupPath()
        self.backupGetPath = QPushButton(
            SHARED.theme.getIcon("browse", "systemio"), self.tr("Browse"), self
        )
        self.backupGetPath.setIconSize(iSz)
        self.backupGetPath.clicked.connect(self._backupFolder)
        self.mainForm.addRow(
            self.tr("Backup storage location"), self.backupGetPath,
            self.tr("Path: {0}").format(self.backupPath), editable="backupPath"
        )

        # Run When Closing
        self.backupOnClose = NSwitch(self)
        self.backupOnClose.setChecked(CONFIG.backupOnClose)
        self.backupOnClose.toggled.connect(self._toggledBackupOnClose)
        self.mainForm.addRow(
            self.tr("Run backup when the project is closed"), self.backupOnClose,
            self.tr("Can be overridden for individual projects in Project Settings.")
        )

        # Ask Before Backup
        # Only enabled when "Run when closing" is checked
        self.askBeforeBackup = NSwitch(self)
        self.askBeforeBackup.setChecked(CONFIG.askBeforeBackup)
        self.askBeforeBackup.setEnabled(CONFIG.backupOnClose)
        self.mainForm.addRow(
            self.tr("Ask before running backup"), self.askBeforeBackup,
            self.tr("If off, backups will run in the background.")
        )

        # Session Timer
        # =============

        title = self.tr("Session Timer")
        section += 1
        self.sidebar.addButton(title, section)
        self.mainForm.addGroupLabel(title, section)

        # Pause When Idle
        self.stopWhenIdle = NSwitch(self)
        self.stopWhenIdle.setChecked(CONFIG.stopWhenIdle)
        self.mainForm.addRow(
            self.tr("Pause the session timer when not writing"), self.stopWhenIdle,
            self.tr("Also pauses when the application window does not have focus.")
        )

        # Inactive Time for Idle
        self.userIdleTime = NDoubleSpinBox(self)
        self.userIdleTime.setMinimum(0.5)
        self.userIdleTime.setMaximum(600.0)
        self.userIdleTime.setSingleStep(0.5)
        self.userIdleTime.setDecimals(1)
        self.userIdleTime.setValue(CONFIG.userIdleTime/60.0)
        self.mainForm.addRow(
            self.tr("Editor inactive time before pausing timer"), self.userIdleTime,
            self.tr("User activity includes typing and changing the content."),
            unit=self.tr("minutes")
        )

        # Label
        self.sidebar.addLabel(self.tr("Writing"))

        # Text Flow
        # =========

        title = self.tr("Text Flow")
        section += 1
        self.sidebar.addButton(title, section)
        self.mainForm.addGroupLabel(title, section)

        # Max Text Width in Normal Mode
        self.textWidth = NSpinBox(self)
        self.textWidth.setMinimum(0)
        self.textWidth.setMaximum(10000)
        self.textWidth.setSingleStep(10)
        self.textWidth.setValue(CONFIG.textWidth)
        self.mainForm.addRow(
            self.tr('Maximum text width in "Normal Mode"'), self.textWidth,
            self.tr("Set to 0 to disable this feature."), unit=self.tr("px")
        )

        # Max Text Width in Focus Mode
        self.focusWidth = NSpinBox(self)
        self.focusWidth.setMinimum(200)
        self.focusWidth.setMaximum(10000)
        self.focusWidth.setSingleStep(10)
        self.focusWidth.setValue(CONFIG.focusWidth)
        self.mainForm.addRow(
            self.tr('Maximum text width in "Focus Mode"'), self.focusWidth,
            self.tr("The maximum width cannot be disabled."), unit=self.tr("px")
        )

        # Focus Mode Footer
        self.hideFocusFooter = NSwitch(self)
        self.hideFocusFooter.setChecked(CONFIG.hideFocusFooter)
        self.mainForm.addRow(
            self.tr('Hide document footer in "Focus Mode"'), self.hideFocusFooter,
            self.tr("Hide the information bar in the document editor.")
        )

        # Justify Text
        self.doJustify = NSwitch(self)
        self.doJustify.setChecked(CONFIG.doJustify)
        self.mainForm.addRow(
            self.tr("Justify the text margins"), self.doJustify,
            self.tr("Applies to both document editor and viewer."),
        )

        # Document Margins
        self.textMargin = NSpinBox(self)
        self.textMargin.setMinimum(0)
        self.textMargin.setMaximum(900)
        self.textMargin.setSingleStep(1)
        self.textMargin.setValue(CONFIG.textMargin)
        self.mainForm.addRow(
            self.tr("Minimum text margin"), self.textMargin,
            self.tr("Applies to both document editor and viewer."),
            unit=self.tr("px")
        )

        # Tab Width
        self.tabWidth = NSpinBox(self)
        self.tabWidth.setMinimum(0)
        self.tabWidth.setMaximum(200)
        self.tabWidth.setSingleStep(1)
        self.tabWidth.setValue(CONFIG.tabWidth)
        self.mainForm.addRow(
            self.tr("Tab width"), self.tabWidth,
            self.tr("The width of a tab key press in the editor and viewer."),
            unit=self.tr("px")
        )

        # Text Editing
        # ============

        title = self.tr("Text Editing")
        section += 1
        self.sidebar.addButton(title, section)
        self.mainForm.addGroupLabel(title, section)

        # Spell Checking
        self.spellLanguage = NComboBox(self, scrollable=True)
        self.spellLanguage.setMinimumWidth(200)

        if CONFIG.hasEnchant:
            for tag, language in SHARED.spelling.listDictionaries():
                self.spellLanguage.addItem(language, tag)
        else:
            self.spellLanguage.addItem(nwUnicode.U_EMDASH, "")
            self.spellLanguage.setEnabled(False)

        if (idx := self.spellLanguage.findData(CONFIG.spellLanguage)) != -1:
            self.spellLanguage.setCurrentIndex(idx)

        self.mainForm.addRow(
            self.tr("Spell check language"), self.spellLanguage,
            self.tr("Available languages are determined by your system."), stretch=(3, 2)
        )

        # Auto-Select Word Under Cursor
        self.autoSelect = NSwitch(self)
        self.autoSelect.setChecked(CONFIG.autoSelect)
        self.mainForm.addRow(
            self.tr("Auto-select word under cursor"), self.autoSelect,
            self.tr("Apply formatting to word under cursor if no selection is made.")
        )

        # Cursor Width
        self.cursorWidth = NSpinBox(self)
        self.cursorWidth.setMinimum(1)
        self.cursorWidth.setMaximum(20)
        self.cursorWidth.setSingleStep(1)
        self.cursorWidth.setValue(CONFIG.cursorWidth)
        self.mainForm.addRow(
            self.tr("Cursor width"), self.cursorWidth,
            self.tr("The width of the text cursor of the editor."),
            unit=self.tr("px")
        )

        # Highlight Current Line
        self.lineHighlight = NSwitch(self)
        self.lineHighlight.setChecked(CONFIG.lineHighlight)
        self.mainForm.addRow(
            self.tr("Highlight current line"), self.lineHighlight
        )

        # Show Tabs and Spaces
        self.showTabsNSpaces = NSwitch(self)
        self.showTabsNSpaces.setChecked(CONFIG.showTabsNSpaces)
        self.mainForm.addRow(
            self.tr("Show tabs and spaces"), self.showTabsNSpaces
        )

        # Show Line Endings
        self.showLineEndings = NSwitch(self)
        self.showLineEndings.setChecked(CONFIG.showLineEndings)
        self.mainForm.addRow(
            self.tr("Show line endings"), self.showLineEndings
        )

        # Editor Scrolling
        # ================

        title = self.tr("Editor Scrolling")
        section += 1
        self.sidebar.addButton(title, section)
        self.mainForm.addGroupLabel(title, section)

        # Scroll Past End
        self.scrollPastEnd = NSwitch(self)
        self.scrollPastEnd.setChecked(CONFIG.scrollPastEnd)
        self.mainForm.addRow(
            self.tr("Scroll past the end of the document"), self.scrollPastEnd,
            self.tr("Also centres the cursor when scrolling.")
        )

        # Typewriter Scrolling
        self.autoScroll = NSwitch(self)
        self.autoScroll.setChecked(CONFIG.autoScroll)
        self.mainForm.addRow(
            self.tr("Typewriter style scrolling when you type"), self.autoScroll,
            self.tr("Keeps the cursor at a fixed vertical position.")
        )

        # Typewriter Position
        self.autoScrollPos = NSpinBox(self)
        self.autoScrollPos.setMinimum(10)
        self.autoScrollPos.setMaximum(90)
        self.autoScrollPos.setSingleStep(1)
        self.autoScrollPos.setValue(int(CONFIG.autoScrollPos))
        self.mainForm.addRow(
            self.tr("Minimum position for Typewriter scrolling"), self.autoScrollPos,
            self.tr("Percentage of the editor height from the top."), unit="%"
        )

        # Text Highlighting
        # =================

        title = self.tr("Text Highlighting")
        section += 1
        self.sidebar.addButton(title, section)
        self.mainForm.addGroupLabel(title, section)

        # Dialogue Quotes
        self.dialogStyle = NComboBox(self)
        self.dialogStyle.addItem(self.tr("None"), 0)
        self.dialogStyle.addItem(self.tr("Single Quotes"), 1)
        self.dialogStyle.addItem(self.tr("Double Quotes"), 2)
        self.dialogStyle.addItem(self.tr("Both"), 3)
        self.dialogStyle.setCurrentData(CONFIG.dialogStyle, 2)
        self.mainForm.addRow(
            self.tr("Highlight dialogue"), self.dialogStyle,
            self.tr("Applies to the selected quote styles.")
        )

        # Open-Ended Dialogue
        self.allowOpenDial = NSwitch(self)
        self.allowOpenDial.setChecked(CONFIG.allowOpenDial)
        self.mainForm.addRow(
            self.tr("Allow open-ended dialogue"), self.allowOpenDial,
            self.tr("Highlight dialogue line with no closing quote.")
        )

        # Alternative Dialogue
        self.altDialogOpen = QLineEdit(self)
        self.altDialogOpen.setMaxLength(4)
        self.altDialogOpen.setFixedWidth(boxFixed)
        self.altDialogOpen.setAlignment(QtAlignCenter)
        self.altDialogOpen.setText(CONFIG.altDialogOpen)

        self.altDialogClose = QLineEdit(self)
        self.altDialogClose.setMaxLength(4)
        self.altDialogClose.setFixedWidth(boxFixed)
        self.altDialogClose.setAlignment(QtAlignCenter)
        self.altDialogClose.setText(CONFIG.altDialogClose)

        self.mainForm.addRow(
            self.tr("Alternative dialogue symbols"), [self.altDialogOpen, self.altDialogClose],
            self.tr("Custom highlighting of dialogue text.")
        )

        # Dialogue Line
        self.mnLineSymbols = QMenu(self)
        for symbol in nwQuotes.ALLOWED:
            label = trConst(nwQuotes.SYMBOLS.get(symbol, nwQuotes.DASHES.get(symbol, "None")))
            self.mnLineSymbols.addAction(
                f"[ {symbol } ] {label}",
                lambda symbol=symbol: self._insertDialogLineSymbol(symbol)
            )

        self.dialogLine = QLineEdit(self)
        self.dialogLine.setMinimumWidth(100)
        self.dialogLine.setAlignment(QtAlignCenter)
        self.dialogLine.setText(" ".join(CONFIG.dialogLine))

        self.dialogLineButton = NIconToolButton(self, iSz, "add", "add")
        self.dialogLineButton.setMenu(self.mnLineSymbols)

        self.mainForm.addRow(
            self.tr("Dialogue line symbols"), self.dialogLine,
            self.tr("Lines starting with any of these symbols are dialogue."),
            button=self.dialogLineButton
        )

        # Narrator Break
        self.narratorBreak = NComboBox(self)
        self.narratorDialog = NComboBox(self)
        for key, value in nwQuotes.DASHES.items():
            label = trConst(value)
            self.narratorBreak.addItem(label, key)
            self.narratorDialog.addItem(label, key)

        self.narratorBreak.setCurrentData(CONFIG.narratorBreak, "")
        self.narratorDialog.setCurrentData(CONFIG.narratorDialog, "")

        self.mainForm.addRow(
            self.tr("Narrator break symbol"), self.narratorBreak,
            self.tr("Symbol to indicate a narrator break in dialogue.")
        )
        self.mainForm.addRow(
            self.tr("Alternating dialogue/narration symbol"), self.narratorDialog,
            self.tr("Alternates dialogue highlighting within any paragraph.")
        )

        # Emphasis
        self.highlightEmph = NSwitch(self)
        self.highlightEmph.setChecked(CONFIG.highlightEmph)
        self.mainForm.addRow(
            self.tr("Add highlight colour to emphasised text"), self.highlightEmph,
            self.tr("Applies to the document editor only.")
        )

        # Additional Spaces
        self.showMultiSpaces = NSwitch(self)
        self.showMultiSpaces.setChecked(CONFIG.showMultiSpaces)
        self.mainForm.addRow(
            self.tr("Highlight multiple spaces between words"), self.showMultiSpaces,
            self.tr("Applies to the document editor only.")
        )

        # Text Automation
        # ===============

        title = self.tr("Text Automation")
        section += 1
        self.sidebar.addButton(title, section)
        self.mainForm.addGroupLabel(title, section)

        # Auto-Replace as You Type Main Switch
        self.doReplace = NSwitch(self)
        self.doReplace.setChecked(CONFIG.doReplace)
        self.doReplace.toggled.connect(self._toggleAutoReplaceMain)
        self.mainForm.addRow(
            self.tr("Auto-replace text as you type"), self.doReplace,
            self.tr("Allow the editor to replace symbols as you type.")
        )

        # Auto-Replace Single Quotes
        self.doReplaceSQuote = NSwitch(self)
        self.doReplaceSQuote.setChecked(CONFIG.doReplaceSQuote)
        self.doReplaceSQuote.setEnabled(CONFIG.doReplace)
        self.mainForm.addRow(
            self.tr("Auto-replace single quotes"), self.doReplaceSQuote,
            self.tr("Try to guess which is an opening or a closing quote.")
        )

        # Auto-Replace Double Quotes
        self.doReplaceDQuote = NSwitch(self)
        self.doReplaceDQuote.setChecked(CONFIG.doReplaceDQuote)
        self.doReplaceDQuote.setEnabled(CONFIG.doReplace)
        self.mainForm.addRow(
            self.tr("Auto-replace double quotes"), self.doReplaceDQuote,
            self.tr("Try to guess which is an opening or a closing quote.")
        )

        # Auto-Replace Hyphens
        self.doReplaceDash = NSwitch(self)
        self.doReplaceDash.setChecked(CONFIG.doReplaceDash)
        self.doReplaceDash.setEnabled(CONFIG.doReplace)
        self.mainForm.addRow(
            self.tr("Auto-replace dashes"), self.doReplaceDash,
            self.tr("Double and triple hyphens become short and long dashes.")
        )

        # Auto-Replace Dots
        self.doReplaceDots = NSwitch(self)
        self.doReplaceDots.setChecked(CONFIG.doReplaceDots)
        self.doReplaceDots.setEnabled(CONFIG.doReplace)
        self.mainForm.addRow(
            self.tr("Auto-replace dots"), self.doReplaceDots,
            self.tr("Three consecutive dots become ellipsis.")
        )

        # Pad Before
        self.fmtPadBefore = QLineEdit(self)
        self.fmtPadBefore.setMaxLength(32)
        self.fmtPadBefore.setMinimumWidth(150)
        self.fmtPadBefore.setText(CONFIG.fmtPadBefore)
        self.mainForm.addRow(
            self.tr("Insert non-breaking space before"), self.fmtPadBefore,
            self.tr("Automatically add space before any of these symbols."), stretch=(2, 1)
        )

        # Pad After
        self.fmtPadAfter = QLineEdit(self)
        self.fmtPadAfter.setMaxLength(32)
        self.fmtPadAfter.setMinimumWidth(150)
        self.fmtPadAfter.setText(CONFIG.fmtPadAfter)
        self.mainForm.addRow(
            self.tr("Insert non-breaking space after"), self.fmtPadAfter,
            self.tr("Automatically add space after any of these symbols."), stretch=(2, 1)
        )

        # Use Thin Space
        self.fmtPadThin = NSwitch(self)
        self.fmtPadThin.setChecked(CONFIG.fmtPadThin)
        self.fmtPadThin.setEnabled(CONFIG.doReplace)
        self.mainForm.addRow(
            self.tr("Use thin space instead"), self.fmtPadThin,
            self.tr("Inserts a thin space instead of a regular space.")
        )

        # Quotation Style
        # ===============

        title = self.tr("Quotation Style")
        section += 1
        self.sidebar.addButton(title, section)
        self.mainForm.addGroupLabel(title, section)

        # Single Quote Style
        self.fmtSQuoteOpen = QLineEdit(self)
        self.fmtSQuoteOpen.setMaxLength(1)
        self.fmtSQuoteOpen.setReadOnly(True)
        self.fmtSQuoteOpen.setFixedWidth(boxFixed)
        self.fmtSQuoteOpen.setAlignment(QtAlignCenter)
        self.fmtSQuoteOpen.setText(CONFIG.fmtSQuoteOpen)
        self.btnSQuoteOpen = NIconToolButton(self, iSz, "quote", "tool")
        self.btnSQuoteOpen.clicked.connect(self._changeSingleQuoteOpen)
        self.mainForm.addRow(
            self.tr("Single quote open style"), self.fmtSQuoteOpen,
            self.tr("The symbol to use for a leading single quote."),
            button=self.btnSQuoteOpen
        )

        self.fmtSQuoteClose = QLineEdit(self)
        self.fmtSQuoteClose.setMaxLength(1)
        self.fmtSQuoteClose.setReadOnly(True)
        self.fmtSQuoteClose.setFixedWidth(boxFixed)
        self.fmtSQuoteClose.setAlignment(QtAlignCenter)
        self.fmtSQuoteClose.setText(CONFIG.fmtSQuoteClose)
        self.btnSQuoteClose = NIconToolButton(self, iSz, "quote", "tool")
        self.btnSQuoteClose.clicked.connect(self._changeSingleQuoteClose)
        self.mainForm.addRow(
            self.tr("Single quote close style"), self.fmtSQuoteClose,
            self.tr("The symbol to use for a trailing single quote."),
            button=self.btnSQuoteClose
        )

        # Double Quote Style
        self.fmtDQuoteOpen = QLineEdit(self)
        self.fmtDQuoteOpen.setMaxLength(1)
        self.fmtDQuoteOpen.setReadOnly(True)
        self.fmtDQuoteOpen.setFixedWidth(boxFixed)
        self.fmtDQuoteOpen.setAlignment(QtAlignCenter)
        self.fmtDQuoteOpen.setText(CONFIG.fmtDQuoteOpen)
        self.btnDQuoteOpen = NIconToolButton(self, iSz, "quote", "tool")
        self.btnDQuoteOpen.clicked.connect(self._changeDoubleQuoteOpen)
        self.mainForm.addRow(
            self.tr("Double quote open style"), self.fmtDQuoteOpen,
            self.tr("The symbol to use for a leading double quote."),
            button=self.btnDQuoteOpen
        )

        self.fmtDQuoteClose = QLineEdit(self)
        self.fmtDQuoteClose.setMaxLength(1)
        self.fmtDQuoteClose.setReadOnly(True)
        self.fmtDQuoteClose.setFixedWidth(boxFixed)
        self.fmtDQuoteClose.setAlignment(QtAlignCenter)
        self.fmtDQuoteClose.setText(CONFIG.fmtDQuoteClose)
        self.btnDQuoteClose = NIconToolButton(self, iSz, "quote", "tool")
        self.btnDQuoteClose.clicked.connect(self._changeDoubleQuoteClose)
        self.mainForm.addRow(
            self.tr("Double quote close style"), self.fmtDQuoteClose,
            self.tr("The symbol to use for a trailing double quote."),
            button=self.btnDQuoteClose
        )

        self.mainForm.finalise()
        self.sidebar.setSelected(1)

    ##
    #  Events
    ##

    def closeEvent(self, event: QCloseEvent) -> None:
        """Capture the close event and perform cleanup."""
        logger.debug("Close: GuiPreferences")
        self._saveWindowSize()
        event.accept()
        self.softDelete()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Overload keyPressEvent and only accept escape. The main
        purpose here is to prevent Enter/Return from closing the dialog
        as it is used for the search box.
        """
        if event.matches(QKeySequence.StandardKey.Cancel):
            self.close()
        event.ignore()

    ##
    #  Private Slots
    ##

    @pyqtSlot(int)
    def _sidebarClicked(self, section: int) -> None:
        """Process a user request to switch page."""
        self.mainForm.scrollToSection(section)

    @pyqtSlot()
    def _gotoSearch(self) -> None:
        """Go to the setting indicated by the search text."""
        self.mainForm.scrollToLabel(self.searchText.text().strip())

    @pyqtSlot()
    def _selectGuiFont(self) -> None:
        """Open the QFontDialog and set a font for the font style."""
        font, status = SHARED.getFont(self._guiFont, self.nativeFont.isChecked())
        if status:
            self.guiFont.setText(describeFont(font))
            self.guiFont.setCursorPosition(0)
            self._guiFont = font

    @pyqtSlot()
    def _selectTextFont(self) -> None:
        """Open the QFontDialog and set a font for the font style."""
        font, status = SHARED.getFont(self._textFont, self.nativeFont.isChecked())
        if status:
            self.textFont.setText(describeFont(font))
            self.textFont.setCursorPosition(0)
            self._textFont = font

    @pyqtSlot()
    def _backupFolder(self) -> None:
        """Open a dialog to select the backup folder."""
        if path := QFileDialog.getExistingDirectory(
            self, self.tr("Backup Directory"), str(self.backupPath) or "",
            options=QFileDialog.Option.ShowDirsOnly
        ):
            self.backupPath = path
            self.mainForm.setHelpText("backupPath", self.tr("Path: {0}").format(path))

    @pyqtSlot(bool)
    def _toggledBackupOnClose(self, state: bool) -> None:
        """Toggle switch that depends on the backup on close switch."""
        self.askBeforeBackup.setEnabled(state)

    @pyqtSlot(str)
    def _insertDialogLineSymbol(self, symbol: str) -> None:
        """Insert a symbol in the dialogue line box."""
        current = self.dialogLine.text()
        values = processDialogSymbols(f"{current} {symbol}")
        self.dialogLine.setText(" ".join(values))

    @pyqtSlot(bool)
    def _toggleAutoReplaceMain(self, state: bool) -> None:
        """Toggle switches controlled by the auto replace switch."""
        self.doReplaceSQuote.setEnabled(state)
        self.doReplaceDQuote.setEnabled(state)
        self.doReplaceDash.setEnabled(state)
        self.doReplaceDots.setEnabled(state)
        self.fmtPadThin.setEnabled(state)

    @pyqtSlot()
    def _changeSingleQuoteOpen(self) -> None:
        """Change single quote open style."""
        quote, status = GuiQuoteSelect.getQuote(self, current=self.fmtSQuoteOpen.text())
        if status:
            self.fmtSQuoteOpen.setText(quote)

    @pyqtSlot()
    def _changeSingleQuoteClose(self) -> None:
        """Change single quote close style."""
        quote, status = GuiQuoteSelect.getQuote(self, current=self.fmtSQuoteClose.text())
        if status:
            self.fmtSQuoteClose.setText(quote)

    @pyqtSlot()
    def _changeDoubleQuoteOpen(self) -> None:
        """Change double quote open style."""
        quote, status = GuiQuoteSelect.getQuote(self, current=self.fmtDQuoteOpen.text())
        if status:
            self.fmtDQuoteOpen.setText(quote)

    @pyqtSlot()
    def _changeDoubleQuoteClose(self) -> None:
        """Change double quote close style."""
        quote, status = GuiQuoteSelect.getQuote(self, current=self.fmtDQuoteClose.text())
        if status:
            self.fmtDQuoteClose.setText(quote)

    ##
    #  Internal Functions
    ##

    def _saveWindowSize(self) -> None:
        """Save the dialog window size."""
        CONFIG.setPreferencesWinSize(self.width(), self.height())

    def _doSave(self) -> None:
        """Save the values set in the form."""
        updateTheme  = False
        needsRestart = False
        updateSyntax = False
        refreshTree  = False

        # Appearance
        guiLocale    = self.guiLocale.currentData()
        lightTheme   = self.lightTheme.currentData()
        darkTheme    = self.darkTheme.currentData()
        iconTheme    = self.iconTheme.currentData()
        useCharCount = self.useCharCount.isChecked()

        updateTheme  |= CONFIG.lightTheme != lightTheme
        updateTheme  |= CONFIG.darkTheme != darkTheme
        updateTheme  |= CONFIG.iconTheme != iconTheme
        needsRestart |= CONFIG.guiLocale != guiLocale
        needsRestart |= CONFIG.guiFont != self._guiFont
        refreshTree  |= CONFIG.useCharCount != useCharCount
        updateSyntax |= CONFIG.lightTheme != lightTheme
        updateSyntax |= CONFIG.darkTheme != darkTheme

        CONFIG.guiLocale    = guiLocale
        CONFIG.lightTheme   = lightTheme
        CONFIG.darkTheme    = darkTheme
        CONFIG.iconTheme    = iconTheme
        CONFIG.hideVScroll  = self.hideVScroll.isChecked()
        CONFIG.hideHScroll  = self.hideHScroll.isChecked()
        CONFIG.nativeFont   = self.nativeFont.isChecked()
        CONFIG.useCharCount = useCharCount
        CONFIG.setGuiFont(self._guiFont)

        # Document Style
        CONFIG.showFullPath   = self.showFullPath.isChecked()
        CONFIG.incNotesWCount = self.incNotesWCount.isChecked()
        CONFIG.setTextFont(self._textFont)

        # Project View
        iconColTree = self.iconColTree.currentData()
        iconColDocs = self.iconColDocs.isChecked()
        emphLabels = self.emphLabels.isChecked()

        updateTheme |= CONFIG.iconColTree != iconColTree
        updateTheme |= CONFIG.iconColDocs != iconColDocs
        refreshTree |= CONFIG.emphLabels != emphLabels

        CONFIG.iconColTree = iconColTree
        CONFIG.iconColDocs = iconColDocs
        CONFIG.emphLabels     = emphLabels

        # Behaviour
        CONFIG.autoSaveDoc   = self.autoSaveDoc.value()
        CONFIG.autoSaveProj  = self.autoSaveProj.value()
        CONFIG.askBeforeExit = self.askBeforeExit.isChecked()

        # Project Backup
        CONFIG.setBackupPath(self.backupPath)
        CONFIG.backupOnClose   = self.backupOnClose.isChecked()
        CONFIG.askBeforeBackup = self.askBeforeBackup.isChecked()

        # Session Timer
        CONFIG.stopWhenIdle = self.stopWhenIdle.isChecked()
        CONFIG.userIdleTime = round(self.userIdleTime.value() * 60)

        # Text Flow
        CONFIG.textWidth       = self.textWidth.value()
        CONFIG.focusWidth      = self.focusWidth.value()
        CONFIG.hideFocusFooter = self.hideFocusFooter.isChecked()
        CONFIG.doJustify       = self.doJustify.isChecked()
        CONFIG.textMargin      = self.textMargin.value()
        CONFIG.tabWidth        = self.tabWidth.value()

        # Text Editing
        lineHighlight = self.lineHighlight.isChecked()

        updateSyntax |= CONFIG.lineHighlight != lineHighlight

        CONFIG.spellLanguage   = self.spellLanguage.currentData()
        CONFIG.autoSelect      = self.autoSelect.isChecked()
        CONFIG.cursorWidth     = self.cursorWidth.value()
        CONFIG.lineHighlight   = lineHighlight
        CONFIG.showTabsNSpaces = self.showTabsNSpaces.isChecked()
        CONFIG.showLineEndings = self.showLineEndings.isChecked()

        # Editor Scrolling
        CONFIG.autoScroll    = self.autoScroll.isChecked()
        CONFIG.autoScrollPos = self.autoScrollPos.value()
        CONFIG.scrollPastEnd = self.scrollPastEnd.isChecked()

        # Text Highlighting
        dialogueStyle   = self.dialogStyle.currentData()
        allowOpenDial   = self.allowOpenDial.isChecked()
        dialogueLine    = processDialogSymbols(self.dialogLine.text())
        narratorBreak   = self.narratorBreak.currentData()
        narratorDialog  = self.narratorDialog.currentData()
        altDialogOpen   = compact(self.altDialogOpen.text())
        altDialogClose  = compact(self.altDialogClose.text())
        highlightEmph   = self.highlightEmph.isChecked()
        showMultiSpaces = self.showMultiSpaces.isChecked()

        updateSyntax |= CONFIG.dialogStyle != dialogueStyle
        updateSyntax |= CONFIG.allowOpenDial != allowOpenDial
        updateSyntax |= CONFIG.dialogLine != dialogueLine
        updateSyntax |= CONFIG.narratorBreak != narratorBreak
        updateSyntax |= CONFIG.narratorDialog != narratorDialog
        updateSyntax |= CONFIG.altDialogOpen != altDialogOpen
        updateSyntax |= CONFIG.altDialogClose != altDialogClose
        updateSyntax |= CONFIG.highlightEmph != highlightEmph
        updateSyntax |= CONFIG.showMultiSpaces != showMultiSpaces

        CONFIG.dialogStyle     = dialogueStyle
        CONFIG.allowOpenDial   = allowOpenDial
        CONFIG.dialogLine      = dialogueLine
        CONFIG.narratorBreak   = narratorBreak
        CONFIG.narratorDialog  = narratorDialog
        CONFIG.altDialogOpen   = altDialogOpen
        CONFIG.altDialogClose  = altDialogClose
        CONFIG.highlightEmph   = highlightEmph
        CONFIG.showMultiSpaces = showMultiSpaces

        # Text Automation
        CONFIG.doReplace       = self.doReplace.isChecked()
        CONFIG.doReplaceSQuote = self.doReplaceSQuote.isChecked()
        CONFIG.doReplaceDQuote = self.doReplaceDQuote.isChecked()
        CONFIG.doReplaceDash   = self.doReplaceDash.isChecked()
        CONFIG.doReplaceDots   = self.doReplaceDots.isChecked()
        CONFIG.fmtPadBefore    = uniqueCompact(self.fmtPadBefore.text())
        CONFIG.fmtPadAfter     = uniqueCompact(self.fmtPadAfter.text())
        CONFIG.fmtPadThin      = self.fmtPadThin.isChecked()

        # Quotation Style
        CONFIG.fmtSQuoteOpen  = self.fmtSQuoteOpen.text()
        CONFIG.fmtSQuoteClose = self.fmtSQuoteClose.text()
        CONFIG.fmtDQuoteOpen  = self.fmtDQuoteOpen.text()
        CONFIG.fmtDQuoteClose = self.fmtDQuoteClose.text()

        # Finalise
        CONFIG.saveConfig()
        self.newPreferencesReady.emit(needsRestart, refreshTree, updateTheme, updateSyntax)

        self.close()
