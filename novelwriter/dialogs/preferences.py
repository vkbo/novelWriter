"""
novelWriter – GUI Preferences
=============================

File History:
Created:   2019-06-10 [0.1.5] GuiPreferences
Rewritten: 2024-01-08 [2.3b1] GuiPreferences

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

import logging

from PyQt5.QtGui import QCloseEvent, QFont
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import (
    QAbstractButton, QDialog, QHBoxLayout, QVBoxLayout, QWidget, QComboBox,
    QSpinBox, QPushButton, QDialogButtonBox, QLineEdit, QFileDialog,
    QFontDialog, QDoubleSpinBox, qApp
)

from novelwriter import CONFIG, SHARED
from novelwriter.dialogs.quotes import GuiQuoteSelect
from novelwriter.extensions.switch import NSwitch
from novelwriter.extensions.configlayout import NScrollableForm
from novelwriter.extensions.pagedsidebar import NPagedSideBar

logger = logging.getLogger(__name__)


class GuiPreferences(QDialog):

    NAV_APPEARANCE = 0

    newPreferencesReady = pyqtSignal(bool, bool, bool, bool)

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)

        logger.debug("Create: GuiPreferences")
        self.setObjectName("GuiPreferences")
        self.setWindowTitle(CONFIG.appName)
        self.setMinimumSize(CONFIG.pxInt(600), CONFIG.pxInt(500))
        self.resize(*CONFIG.preferencesWinSize)

        # SideBar
        self.sidebar = NPagedSideBar(self)
        self.sidebar.setLabelColor(SHARED.theme.helpText)
        self.sidebar.addLabel(self.tr("Preferences"))
        self.sidebar.buttonClicked.connect(self._sidebarClicked)

        # Form
        self.mainForm = NScrollableForm(self)
        self.mainForm.setHelpTextStyle(SHARED.theme.helpText)

        # Buttons
        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.Apply | QDialogButtonBox.Save | QDialogButtonBox.Close
        )
        self.buttonBox.clicked.connect(self._dialogButtonClicked)

        # Assemble
        self.mainBox = QHBoxLayout()
        self.mainBox.addWidget(self.sidebar)
        self.mainBox.addWidget(self.mainForm)
        self.mainBox.setContentsMargins(0, 0, 0, 0)

        self.outerBox = QVBoxLayout()
        self.outerBox.addLayout(self.mainBox)
        self.outerBox.addWidget(self.buttonBox)
        self.outerBox.setSpacing(CONFIG.pxInt(8))

        self.setLayout(self.outerBox)
        self.setSizeGripEnabled(True)
        self.buildForm()

        logger.debug("Ready: GuiPreferences")

        return

    def __del__(self) -> None:  # pragma: no cover
        logger.debug("Delete: GuiPreferences")
        return

    def buildForm(self) -> None:
        """Build the settings form."""
        section = 0
        minWidth = CONFIG.pxInt(200)

        # Appearance
        # ==========

        title = self.tr("Appearance")
        section += 1
        self.sidebar.addButton(title, section)
        self.mainForm.addGroupLabel(title, section)

        # Display Language
        self.guiLocale = QComboBox(self)
        self.guiLocale.setMinimumWidth(minWidth)
        for lang, name in CONFIG.listLanguages(CONFIG.LANG_NW):
            self.guiLocale.addItem(name, lang)
        if (idx := self.guiLocale.findData(CONFIG.guiLocale)) != -1:
            self.guiLocale.setCurrentIndex(idx)

        self.mainForm.addRow(
            self.tr("Display language"),
            self.guiLocale,
            self.tr("Requires restart to take effect.")
        )

        # Colour Theme
        self.guiTheme = QComboBox(self)
        self.guiTheme.setMinimumWidth(minWidth)
        for theme, name in SHARED.theme.listThemes():
            self.guiTheme.addItem(name, theme)
        if (idx := self.guiTheme.findData(CONFIG.guiTheme)) != -1:
            self.guiTheme.setCurrentIndex(idx)

        self.mainForm.addRow(
            self.tr("Colour theme"),
            self.guiTheme,
            self.tr("General colour theme and icons.")
        )

        # Application Font Family
        self.guiFont = QLineEdit(self)
        self.guiFont.setReadOnly(True)
        self.guiFont.setFixedWidth(CONFIG.pxInt(162))
        self.guiFont.setText(CONFIG.guiFont)
        self.guiFontButton = QPushButton("...", self)
        self.guiFontButton.setMaximumWidth(int(2.5*SHARED.theme.getTextWidth("...")))
        self.guiFontButton.clicked.connect(self._selectGuiFont)
        self.mainForm.addRow(
            self.tr("Application font family"),
            self.guiFont,
            self.tr("Requires restart to take effect."),
            button=self.guiFontButton
        )

        # Application Font Size
        self.guiFontSize = QSpinBox(self)
        self.guiFontSize.setMinimum(8)
        self.guiFontSize.setMaximum(60)
        self.guiFontSize.setSingleStep(1)
        self.guiFontSize.setValue(CONFIG.guiFontSize)
        self.mainForm.addRow(
            self.tr("Application font size"),
            self.guiFontSize,
            self.tr("Requires restart to take effect."),
            unit=self.tr("pt")
        )

        # Vertical Scrollbars
        self.hideVScroll = NSwitch(self)
        self.hideVScroll.setChecked(CONFIG.hideVScroll)
        self.mainForm.addRow(
            self.tr("Hide vertical scroll bars in main windows"),
            self.hideVScroll,
            self.tr("Scrolling available with mouse wheel and keys only.")
        )

        # Horizontal Scrollbars
        self.hideHScroll = NSwitch(self)
        self.hideHScroll.setChecked(CONFIG.hideHScroll)
        self.mainForm.addRow(
            self.tr("Hide horizontal scroll bars in main windows"),
            self.hideHScroll,
            self.tr("Scrolling available with mouse wheel and keys only.")
        )

        # Document Style
        # ==============

        title = self.tr("Document Style")
        section += 1
        self.sidebar.addButton(title, section)
        self.mainForm.addGroupLabel(title, section)

        # Document Colour Theme
        self.guiSyntax = QComboBox(self)
        self.guiSyntax.setMinimumWidth(CONFIG.pxInt(200))
        for syntax, name in SHARED.theme.listSyntax():
            self.guiSyntax.addItem(name, syntax)
        if (idx := self.guiSyntax.findData(CONFIG.guiSyntax)) != -1:
            self.guiSyntax.setCurrentIndex(idx)

        self.mainForm.addRow(
            self.tr("Document colour theme"),
            self.guiSyntax,
            self.tr("Colour theme for the editor and viewer.")
        )

        # Document Font Family
        self.textFont = QLineEdit(self)
        self.textFont.setReadOnly(True)
        self.textFont.setFixedWidth(CONFIG.pxInt(162))
        self.textFont.setText(CONFIG.textFont)
        self.textFontButton = QPushButton("...", self)
        self.textFontButton.setMaximumWidth(int(2.5*SHARED.theme.getTextWidth("...")))
        self.textFontButton.clicked.connect(self._selectTextFont)
        self.mainForm.addRow(
            self.tr("Document font family"),
            self.textFont,
            self.tr("Applies to both document editor and viewer."),
            button=self.textFontButton
        )

        # Document Font Size
        self.textSize = QSpinBox(self)
        self.textSize.setMinimum(8)
        self.textSize.setMaximum(60)
        self.textSize.setSingleStep(1)
        self.textSize.setValue(CONFIG.textSize)
        self.mainForm.addRow(
            self.tr("Document font size"),
            self.textSize,
            self.tr("Applies to both document editor and viewer."),
            unit=self.tr("pt")
        )

        # Emphasise Labels
        self.emphLabels = NSwitch(self)
        self.emphLabels.setChecked(CONFIG.emphLabels)
        self.mainForm.addRow(
            self.tr("Emphasise partition and chapter labels"),
            self.emphLabels,
            self.tr("Makes them stand out in the project tree."),
        )

        # Document Path
        self.showFullPath = NSwitch(self)
        self.showFullPath.setChecked(CONFIG.showFullPath)
        self.mainForm.addRow(
            self.tr("Show full path in document header"),
            self.showFullPath,
            self.tr("Add the parent folder names to the header.")
        )

        # Include Notes in Word Count
        self.incNotesWCount = NSwitch(self)
        self.incNotesWCount.setChecked(CONFIG.incNotesWCount)
        self.mainForm.addRow(
            self.tr("Include project notes in status bar word count"),
            self.incNotesWCount
        )

        # Auto Save
        # =========

        title = self.tr("Auto Save")
        section += 1
        self.sidebar.addButton(title, section)
        self.mainForm.addGroupLabel(title, section)

        # Document Save Timer
        self.autoSaveDoc = QSpinBox(self)
        self.autoSaveDoc.setMinimum(5)
        self.autoSaveDoc.setMaximum(600)
        self.autoSaveDoc.setSingleStep(1)
        self.autoSaveDoc.setValue(CONFIG.autoSaveDoc)
        self.mainForm.addRow(
            self.tr("Save document interval"),
            self.autoSaveDoc,
            self.tr("How often the document is automatically saved."),
            unit=self.tr("seconds")
        )

        # Project Save Timer
        self.autoSaveProj = QSpinBox(self)
        self.autoSaveProj.setMinimum(5)
        self.autoSaveProj.setMaximum(600)
        self.autoSaveProj.setSingleStep(1)
        self.autoSaveProj.setValue(CONFIG.autoSaveProj)
        self.mainForm.addRow(
            self.tr("Save project interval"),
            self.autoSaveProj,
            self.tr("How often the project is automatically saved."),
            unit=self.tr("seconds")
        )

        # Project Backup
        # ==============

        title = self.tr("Project Backup")
        section += 1
        self.sidebar.addButton(title, section)
        self.mainForm.addGroupLabel(title, section)

        # Backup Path
        self.backupPath = CONFIG.backupPath()
        self.backupGetPath = QPushButton(SHARED.theme.getIcon("browse"), self.tr("Browse"), self)
        self.backupGetPath.clicked.connect(self._backupFolder)
        self.mainForm.addRow(
            self.tr("Backup storage location"),
            self.backupGetPath,
            self.tr("Path: {0}").format(self.backupPath),
            editable="backupPath"
        )

        # Run When Closing
        self.backupOnClose = NSwitch(self)
        self.backupOnClose.setChecked(CONFIG.backupOnClose)
        self.backupOnClose.toggled.connect(self._toggledBackupOnClose)
        self.mainForm.addRow(
            self.tr("Run backup when the project is closed"),
            self.backupOnClose,
            self.tr("Can be overridden for individual projects in Project Settings.")
        )

        # Ask Before Backup
        # Only enabled when "Run when closing" is checked
        self.askBeforeBackup = NSwitch(self)
        self.askBeforeBackup.setChecked(CONFIG.askBeforeBackup)
        self.askBeforeBackup.setEnabled(CONFIG.backupOnClose)
        self.mainForm.addRow(
            self.tr("Ask before running backup"),
            self.askBeforeBackup,
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
            self.tr("Pause the session timer when not writing"),
            self.stopWhenIdle,
            self.tr("Also pauses when the application window does not have focus.")
        )

        # Inactive Time for Idle
        self.userIdleTime = QDoubleSpinBox(self)
        self.userIdleTime.setMinimum(0.5)
        self.userIdleTime.setMaximum(600.0)
        self.userIdleTime.setSingleStep(0.5)
        self.userIdleTime.setDecimals(1)
        self.userIdleTime.setValue(CONFIG.userIdleTime/60.0)
        self.mainForm.addRow(
            self.tr("Editor inactive time before pausing timer"),
            self.userIdleTime,
            self.tr("User activity includes typing and changing the content."),
            unit=self.tr("minutes")
        )

        # Text Flow
        # =========

        title = self.tr("Text Flow")
        section += 1
        self.sidebar.addButton(title, section)
        self.mainForm.addGroupLabel(title, section)

        # Max Text Width in Normal Mode
        self.textWidth = QSpinBox(self)
        self.textWidth.setMinimum(0)
        self.textWidth.setMaximum(10000)
        self.textWidth.setSingleStep(10)
        self.textWidth.setValue(CONFIG.textWidth)
        self.mainForm.addRow(
            self.tr("Maximum text width in \"Normal Mode\""),
            self.textWidth,
            self.tr("Set to 0 to disable this feature."),
            unit=self.tr("px")
        )

        # Max Text Width in Focus Mode
        self.focusWidth = QSpinBox(self)
        self.focusWidth.setMinimum(200)
        self.focusWidth.setMaximum(10000)
        self.focusWidth.setSingleStep(10)
        self.focusWidth.setValue(CONFIG.focusWidth)
        self.mainForm.addRow(
            self.tr("Maximum text width in \"Focus Mode\""),
            self.focusWidth,
            self.tr("The maximum width cannot be disabled."),
            unit=self.tr("px")
        )

        # Focus Mode Footer
        self.hideFocusFooter = NSwitch(self)
        self.hideFocusFooter.setChecked(CONFIG.hideFocusFooter)
        self.mainForm.addRow(
            self.tr("Hide document footer in \"Focus Mode\""),
            self.hideFocusFooter,
            self.tr("Hide the information bar in the document editor.")
        )

        # Justify Text
        self.doJustify = NSwitch(self)
        self.doJustify.setChecked(CONFIG.doJustify)
        self.mainForm.addRow(
            self.tr("Justify the text margins"),
            self.doJustify,
            self.tr("Applies to both document editor and viewer."),
        )

        # Document Margins
        self.textMargin = QSpinBox(self)
        self.textMargin.setMinimum(0)
        self.textMargin.setMaximum(900)
        self.textMargin.setSingleStep(1)
        self.textMargin.setValue(CONFIG.textMargin)
        self.mainForm.addRow(
            self.tr("Minimum text margin"),
            self.textMargin,
            self.tr("Applies to both document editor and viewer."),
            unit=self.tr("px")
        )

        # Tab Width
        self.tabWidth = QSpinBox(self)
        self.tabWidth.setMinimum(0)
        self.tabWidth.setMaximum(200)
        self.tabWidth.setSingleStep(1)
        self.tabWidth.setValue(CONFIG.tabWidth)
        self.mainForm.addRow(
            self.tr("Tab width"),
            self.tabWidth,
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
        self.spellLanguage = QComboBox(self)
        self.spellLanguage.setMinimumWidth(minWidth)

        if CONFIG.hasEnchant:
            for tag, language in SHARED.spelling.listDictionaries():
                self.spellLanguage.addItem(language, tag)
        else:
            self.spellLanguage.addItem(self.tr("None"), "")
            self.spellLanguage.setEnabled(False)

        if (idx := self.spellLanguage.findData(CONFIG.spellLanguage)) != -1:
            self.spellLanguage.setCurrentIndex(idx)

        self.mainForm.addRow(
            self.tr("Spell check language"),
            self.spellLanguage,
            self.tr("Available languages are determined by your system.")
        )

        # Auto-Select Word Under Cursor
        self.autoSelect = NSwitch(self)
        self.autoSelect.setChecked(CONFIG.autoSelect)
        self.mainForm.addRow(
            self.tr("Auto-select word under cursor"),
            self.autoSelect,
            self.tr("Apply formatting to word under cursor if no selection is made.")
        )

        # Show Tabs and Spaces
        self.showTabsNSpaces = NSwitch(self)
        self.showTabsNSpaces.setChecked(CONFIG.showTabsNSpaces)
        self.mainForm.addRow(
            self.tr("Show tabs and spaces"),
            self.showTabsNSpaces
        )

        # Show Line Endings
        self.showLineEndings = NSwitch(self)
        self.showLineEndings.setChecked(CONFIG.showLineEndings)
        self.mainForm.addRow(
            self.tr("Show line endings"),
            self.showLineEndings
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
            self.tr("Scroll past end of the document"),
            self.scrollPastEnd,
            self.tr("Also centres the cursor when scrolling.")
        )

        # Typewriter Scrolling
        self.autoScroll = NSwitch(self)
        self.autoScroll.setChecked(CONFIG.autoScroll)
        self.mainForm.addRow(
            self.tr("Typewriter style scrolling when you type"),
            self.autoScroll,
            self.tr("Keeps the cursor at a fixed vertical position.")
        )

        # Typewriter Position
        self.autoScrollPos = QSpinBox(self)
        self.autoScrollPos.setMinimum(10)
        self.autoScrollPos.setMaximum(90)
        self.autoScrollPos.setSingleStep(1)
        self.autoScrollPos.setValue(int(CONFIG.autoScrollPos))
        self.mainForm.addRow(
            self.tr("Minimum position for Typewriter scrolling"),
            self.autoScrollPos,
            self.tr("Percentage of the editor height from the top."),
            unit="%"
        )

        # Text Highlighting
        # =================

        title = self.tr("Text Highlighting")
        section += 1
        self.sidebar.addButton(title, section)
        self.mainForm.addGroupLabel(title, section)

        self.highlightQuotes = NSwitch(self)
        self.highlightQuotes.setChecked(CONFIG.highlightQuotes)
        self.highlightQuotes.toggled.connect(self._toggleHighlightQuotes)
        self.mainForm.addRow(
            self.tr("Highlight text wrapped in quotes"),
            self.highlightQuotes,
            self.tr("Applies to the document editor only.")
        )

        self.allowOpenSQuote = NSwitch(self)
        self.allowOpenSQuote.setChecked(CONFIG.allowOpenSQuote)
        self.mainForm.addRow(
            self.tr("Allow open-ended single quotes"),
            self.allowOpenSQuote,
            self.tr("Highlight single-quoted line with no closing quote.")
        )

        self.allowOpenDQuote = NSwitch(self)
        self.allowOpenDQuote.setChecked(CONFIG.allowOpenDQuote)
        self.mainForm.addRow(
            self.tr("Allow open-ended double quotes"),
            self.allowOpenDQuote,
            self.tr("Highlight double-quoted line with no closing quote.")
        )

        self.highlightEmph = NSwitch(self)
        self.highlightEmph.setChecked(CONFIG.highlightEmph)
        self.mainForm.addRow(
            self.tr("Add highlight colour to emphasised text"),
            self.highlightEmph,
            self.tr("Applies to the document editor only.")
        )

        self.showMultiSpaces = NSwitch(self)
        self.showMultiSpaces.setChecked(CONFIG.showMultiSpaces)
        self.mainForm.addRow(
            self.tr("Highlight multiple or trailing spaces"),
            self.showMultiSpaces,
            self.tr("Applies to the document editor only.")
        )

        # Text Automation
        # ===============

        title = self.tr("Text Automation")
        section += 1
        self.sidebar.addButton(title, section)
        self.mainForm.addGroupLabel(title, section)

        boxWidth = CONFIG.pxInt(150)

        # Auto-Replace as You Type Main Switch
        self.doReplace = NSwitch(self)
        self.doReplace.setChecked(CONFIG.doReplace)
        self.doReplace.toggled.connect(self._toggleAutoReplaceMain)
        self.mainForm.addRow(
            self.tr("Auto-replace text as you type"),
            self.doReplace,
            self.tr("Allow the editor to replace symbols as you type.")
        )

        # Auto-Replace Single Quotes
        self.doReplaceSQuote = NSwitch(self)
        self.doReplaceSQuote.setChecked(CONFIG.doReplaceSQuote)
        self.doReplaceSQuote.setEnabled(CONFIG.doReplace)
        self.mainForm.addRow(
            self.tr("Auto-replace single quotes"),
            self.doReplaceSQuote,
            self.tr("Try to guess which is an opening or a closing quote.")
        )

        # Auto-Replace Double Quotes
        self.doReplaceDQuote = NSwitch(self)
        self.doReplaceDQuote.setChecked(CONFIG.doReplaceDQuote)
        self.doReplaceDQuote.setEnabled(CONFIG.doReplace)
        self.mainForm.addRow(
            self.tr("Auto-replace double quotes"),
            self.doReplaceDQuote,
            self.tr("Try to guess which is an opening or a closing quote.")
        )

        # Auto-Replace Hyphens
        self.doReplaceDash = NSwitch(self)
        self.doReplaceDash.setChecked(CONFIG.doReplaceDash)
        self.doReplaceDash.setEnabled(CONFIG.doReplace)
        self.mainForm.addRow(
            self.tr("Auto-replace dashes"),
            self.doReplaceDash,
            self.tr("Double and triple hyphens become short and long dashes.")
        )

        # Auto-Replace Dots
        self.doReplaceDots = NSwitch(self)
        self.doReplaceDots.setChecked(CONFIG.doReplaceDots)
        self.doReplaceDots.setEnabled(CONFIG.doReplace)
        self.mainForm.addRow(
            self.tr("Auto-replace dots"),
            self.doReplaceDots,
            self.tr("Three consecutive dots become ellipsis.")
        )

        # Pad Before
        self.fmtPadBefore = QLineEdit(self)
        self.fmtPadBefore.setMaxLength(32)
        self.fmtPadBefore.setMaximumWidth(boxWidth)
        self.fmtPadBefore.setText(CONFIG.fmtPadBefore)
        self.mainForm.addRow(
            self.tr("Insert non-breaking space before"),
            self.fmtPadBefore,
            self.tr("Automatically add space before any of these symbols."),
        )

        # Pad After
        self.fmtPadAfter = QLineEdit(self)
        self.fmtPadAfter.setMaxLength(32)
        self.fmtPadAfter.setMaximumWidth(boxWidth)
        self.fmtPadAfter.setText(CONFIG.fmtPadAfter)
        self.mainForm.addRow(
            self.tr("Insert non-breaking space after"),
            self.fmtPadAfter,
            self.tr("Automatically add space after any of these symbols."),
        )

        # Use Thin Space
        self.fmtPadThin = NSwitch(self)
        self.fmtPadThin.setChecked(CONFIG.fmtPadThin)
        self.fmtPadThin.setEnabled(CONFIG.doReplace)
        self.mainForm.addRow(
            self.tr("Use thin space instead"),
            self.fmtPadThin,
            self.tr("Inserts a thin space instead of a regular space.")
        )

        # Quotation Style
        # ===============

        title = self.tr("Quotation Style")
        section += 1
        self.sidebar.addButton(title, section)
        self.mainForm.addGroupLabel(title, section)

        qWidth = CONFIG.pxInt(40)
        bWidth = int(2.5*SHARED.theme.getTextWidth("..."))
        self.quoteSym = {}

        # Single Quote Style
        self.quoteSym["SO"] = QLineEdit(self)
        self.quoteSym["SO"].setMaxLength(1)
        self.quoteSym["SO"].setReadOnly(True)
        self.quoteSym["SO"].setFixedWidth(qWidth)
        self.quoteSym["SO"].setAlignment(Qt.AlignCenter)
        self.quoteSym["SO"].setText(CONFIG.fmtSQuoteOpen)
        self.btnSingleStyleO = QPushButton("...", self)
        self.btnSingleStyleO.setMaximumWidth(bWidth)
        self.btnSingleStyleO.clicked.connect(lambda: self._getQuote("SO"))
        self.mainForm.addRow(
            self.tr("Single quote open style"),
            self.quoteSym["SO"],
            self.tr("The symbol to use for a leading single quote."),
            button=self.btnSingleStyleO
        )

        self.quoteSym["SC"] = QLineEdit(self)
        self.quoteSym["SC"].setMaxLength(1)
        self.quoteSym["SC"].setReadOnly(True)
        self.quoteSym["SC"].setFixedWidth(qWidth)
        self.quoteSym["SC"].setAlignment(Qt.AlignCenter)
        self.quoteSym["SC"].setText(CONFIG.fmtSQuoteClose)
        self.btnSingleStyleC = QPushButton("...", self)
        self.btnSingleStyleC.setMaximumWidth(bWidth)
        self.btnSingleStyleC.clicked.connect(lambda: self._getQuote("SC"))
        self.mainForm.addRow(
            self.tr("Single quote close style"),
            self.quoteSym["SC"],
            self.tr("The symbol to use for a trailing single quote."),
            button=self.btnSingleStyleC
        )

        # Double Quote Style
        self.quoteSym["DO"] = QLineEdit(self)
        self.quoteSym["DO"].setMaxLength(1)
        self.quoteSym["DO"].setReadOnly(True)
        self.quoteSym["DO"].setFixedWidth(qWidth)
        self.quoteSym["DO"].setAlignment(Qt.AlignCenter)
        self.quoteSym["DO"].setText(CONFIG.fmtDQuoteOpen)
        self.btnDoubleStyleO = QPushButton("...", self)
        self.btnDoubleStyleO.setMaximumWidth(bWidth)
        self.btnDoubleStyleO.clicked.connect(lambda: self._getQuote("DO"))
        self.mainForm.addRow(
            self.tr("Double quote open style"),
            self.quoteSym["DO"],
            self.tr("The symbol to use for a leading double quote."),
            button=self.btnDoubleStyleO
        )

        self.quoteSym["DC"] = QLineEdit(self)
        self.quoteSym["DC"].setMaxLength(1)
        self.quoteSym["DC"].setReadOnly(True)
        self.quoteSym["DC"].setFixedWidth(qWidth)
        self.quoteSym["DC"].setAlignment(Qt.AlignCenter)
        self.quoteSym["DC"].setText(CONFIG.fmtDQuoteClose)
        self.btnDoubleStyleC = QPushButton("...", self)
        self.btnDoubleStyleC.setMaximumWidth(bWidth)
        self.btnDoubleStyleC.clicked.connect(lambda: self._getQuote("DC"))
        self.mainForm.addRow(
            self.tr("Double quote close style"),
            self.quoteSym["DC"],
            self.tr("The symbol to use for a trailing double quote."),
            button=self.btnDoubleStyleC
        )

        self.mainForm.finalise()
        self.sidebar.setSelected(1)

        return

    ##
    #  Events
    ##

    def closeEvent(self, event: QCloseEvent) -> None:
        """Capture the close event and perform cleanup."""
        logger.debug("Close: GuiPreferences")
        self._saveWindowSize()
        event.accept()
        self.deleteLater()
        return

    ##
    #  Private Slots
    ##

    @pyqtSlot("QAbstractButton*")
    def _dialogButtonClicked(self, button: QAbstractButton) -> None:
        """Handle button clicks from the dialog button box."""
        role = self.buttonBox.buttonRole(button)
        if role == QDialogButtonBox.ApplyRole:
            self._saveValues()
        elif role == QDialogButtonBox.AcceptRole:
            self._saveValues()
            self.close()
        elif role == QDialogButtonBox.RejectRole:
            self.close()
        return

    @pyqtSlot(int)
    def _sidebarClicked(self, section: int) -> None:
        """Process a user request to switch page."""
        self.mainForm.scrollToSection(section)
        return

    @pyqtSlot()
    def _selectGuiFont(self) -> None:
        """Open the QFontDialog and set a font for the font style."""
        current = QFont()
        current.setFamily(CONFIG.guiFont)
        current.setPointSize(CONFIG.guiFontSize)
        font, status = QFontDialog.getFont(current, self)
        if status:
            self.guiFont.setText(font.family())
            self.guiFontSize.setValue(font.pointSize())
        return

    @pyqtSlot()
    def _selectTextFont(self):
        """Open the QFontDialog and set a font for the font style."""
        current = QFont()
        current.setFamily(CONFIG.textFont)
        current.setPointSize(CONFIG.textSize)
        font, status = QFontDialog.getFont(current, self)
        if status:
            self.textFont.setText(font.family())
            self.textSize.setValue(font.pointSize())
        return

    @pyqtSlot()
    def _backupFolder(self) -> None:
        """Open a dialog to select the backup folder."""
        if path := QFileDialog.getExistingDirectory(
            self, self.tr("Backup Directory"), str(self.backupPath or ""),
            options=QFileDialog.ShowDirsOnly
        ):
            self.backupPath = path
            self.mainForm.setHelpText("backupPath", self.tr("Path: {0}").format(path))
        return

    @pyqtSlot(bool)
    def _toggledBackupOnClose(self, state: bool) -> None:
        """Toggle switch that depends on the backup on close switch."""
        self.askBeforeBackup.setEnabled(state)
        return

    @pyqtSlot(bool)
    def _toggleHighlightQuotes(self, state: bool) -> None:
        """Toggle switches controlled by the highlight quotes switch."""
        self.allowOpenSQuote.setEnabled(state)
        self.allowOpenDQuote.setEnabled(state)
        return

    @pyqtSlot(bool)
    def _toggleAutoReplaceMain(self, state: bool) -> None:
        """Toggle switches controlled by the auto replace switch."""
        self.doReplaceSQuote.setEnabled(state)
        self.doReplaceDQuote.setEnabled(state)
        self.doReplaceDash.setEnabled(state)
        self.doReplaceDots.setEnabled(state)
        self.fmtPadThin.setEnabled(state)
        return

    def _getQuote(self, qType: str) -> None:
        """Dialog for single quote open."""
        quote = GuiQuoteSelect(self, currentQuote=self.quoteSym[qType].text())
        if quote.exec_() == QDialog.Accepted:
            self.quoteSym[qType].setText(quote.selectedQuote)
        return

    ##
    #  Internal Functions
    ##

    def _saveWindowSize(self) -> None:
        """Save the dialog window size."""
        CONFIG.setPreferencesWinSize(self.width(), self.height())
        return

    def _saveValues(self) -> None:
        """Save the values set in the form."""
        updateTheme  = False
        needsRestart = False
        updateSyntax = False
        refreshTree  = False

        # Appearance
        guiLocale   = self.guiLocale.currentData()
        guiTheme    = self.guiTheme.currentData()
        guiFont     = self.guiFont.text()
        guiFontSize = self.guiFontSize.value()

        updateTheme  |= CONFIG.guiTheme != guiTheme
        needsRestart |= CONFIG.guiLocale != guiLocale
        needsRestart |= CONFIG.guiFont != guiFont
        needsRestart |= CONFIG.guiFontSize != guiFontSize

        CONFIG.guiLocale   = guiLocale
        CONFIG.guiTheme    = guiTheme
        CONFIG.guiFont     = guiFont
        CONFIG.guiFontSize = guiFontSize
        CONFIG.hideVScroll = self.hideVScroll.isChecked()
        CONFIG.hideHScroll = self.hideHScroll.isChecked()

        # Document Style
        guiSyntax  = self.guiSyntax.currentData()
        emphLabels = self.emphLabels.isChecked()

        updateSyntax |= CONFIG.guiSyntax != guiSyntax
        refreshTree  |= CONFIG.emphLabels != emphLabels

        CONFIG.guiSyntax      = guiSyntax
        CONFIG.emphLabels     = emphLabels
        CONFIG.showFullPath   = self.showFullPath.isChecked()
        CONFIG.incNotesWCount = self.incNotesWCount.isChecked()
        CONFIG.setTextFont(self.textFont.text(), self.textSize.value())

        # Auto Save
        CONFIG.autoSaveDoc  = self.autoSaveDoc.value()
        CONFIG.autoSaveProj = self.autoSaveProj.value()

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
        CONFIG.spellLanguage   = self.spellLanguage.currentData()
        CONFIG.autoSelect      = self.autoSelect.isChecked()
        CONFIG.showTabsNSpaces = self.showTabsNSpaces.isChecked()
        CONFIG.showLineEndings = self.showLineEndings.isChecked()

        # Editor Scrolling
        CONFIG.autoScroll    = self.autoScroll.isChecked()
        CONFIG.autoScrollPos = self.autoScrollPos.value()
        CONFIG.scrollPastEnd = self.scrollPastEnd.isChecked()

        # Text Highlighting
        highlightQuotes = self.highlightQuotes.isChecked()
        highlightEmph   = self.highlightEmph.isChecked()
        showMultiSpaces = self.showMultiSpaces.isChecked()

        updateSyntax |= CONFIG.highlightQuotes != highlightQuotes
        updateSyntax |= CONFIG.highlightEmph != highlightEmph
        updateSyntax |= CONFIG.showMultiSpaces != showMultiSpaces

        CONFIG.highlightQuotes = highlightQuotes
        CONFIG.highlightEmph   = highlightEmph
        CONFIG.showMultiSpaces = showMultiSpaces
        CONFIG.allowOpenSQuote = self.allowOpenSQuote.isChecked()
        CONFIG.allowOpenDQuote = self.allowOpenDQuote.isChecked()

        # Text Automation
        CONFIG.doReplace       = self.doReplace.isChecked()
        CONFIG.doReplaceSQuote = self.doReplaceSQuote.isChecked()
        CONFIG.doReplaceDQuote = self.doReplaceDQuote.isChecked()
        CONFIG.doReplaceDash   = self.doReplaceDash.isChecked()
        CONFIG.doReplaceDots   = self.doReplaceDots.isChecked()
        CONFIG.fmtPadBefore    = self.fmtPadBefore.text().strip()
        CONFIG.fmtPadAfter     = self.fmtPadAfter.text().strip()
        CONFIG.fmtPadThin      = self.fmtPadThin.isChecked()

        # Quotation Style
        CONFIG.fmtSQuoteOpen  = self.quoteSym["SO"].text()
        CONFIG.fmtSQuoteClose = self.quoteSym["SC"].text()
        CONFIG.fmtDQuoteOpen  = self.quoteSym["DO"].text()
        CONFIG.fmtDQuoteClose = self.quoteSym["DC"].text()

        # Finalise
        CONFIG.saveConfig()
        self.newPreferencesReady.emit(needsRestart, refreshTree, updateTheme, updateSyntax)
        qApp.processEvents()

        return

# END Class GuiPreferences
