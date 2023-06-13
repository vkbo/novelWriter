"""
novelWriter – GUI Preferences
=============================
GUI classes for the user preferences dialog

File History:
Created: 2019-06-10 [0.1.5]

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

import logging

from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QLocale
from PyQt5.QtWidgets import (
    QDialog, QWidget, QComboBox, QSpinBox, QPushButton, QDialogButtonBox,
    QLineEdit, QFileDialog, QFontDialog, QDoubleSpinBox
)

from novelwriter import CONFIG
from novelwriter.dialogs.quotes import GuiQuoteSelect
from novelwriter.extensions.switch import NSwitch
from novelwriter.extensions.pageddialog import NPagedDialog
from novelwriter.extensions.configlayout import NConfigLayout

logger = logging.getLogger(__name__)


class GuiPreferences(NPagedDialog):

    def __init__(self, mainGui):
        super().__init__(parent=mainGui)

        logger.debug("Create: GuiPreferences")
        self.setObjectName("GuiPreferences")

        self.mainGui    = mainGui
        self.theProject = mainGui.theProject

        self.setWindowTitle(self.tr("Preferences"))

        self.tabGeneral  = GuiPreferencesGeneral(self)
        self.tabProjects = GuiPreferencesProjects(self)
        self.tabDocs     = GuiPreferencesDocuments(self)
        self.tabEditor   = GuiPreferencesEditor(self)
        self.tabSyntax   = GuiPreferencesSyntax(self)
        self.tabAuto     = GuiPreferencesAutomation(self)
        self.tabQuote    = GuiPreferencesQuotes(self)

        self.addTab(self.tabGeneral,  self.tr("General"))
        self.addTab(self.tabProjects, self.tr("Projects"))
        self.addTab(self.tabDocs,     self.tr("Documents"))
        self.addTab(self.tabEditor,   self.tr("Editor"))
        self.addTab(self.tabSyntax,   self.tr("Highlighting"))
        self.addTab(self.tabAuto,     self.tr("Automation"))
        self.addTab(self.tabQuote,    self.tr("Quotes"))

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self._doSave)
        self.buttonBox.rejected.connect(self._doClose)
        self.addControls(self.buttonBox)

        self.resize(*CONFIG.preferencesWinSize)

        # Settings
        self._updateTheme = False
        self._updateSyntax = False
        self._needsRestart = False
        self._refreshTree = False

        logger.debug("Ready: GuiPreferences")

        return

    def __del__(self):  # pragma: no cover
        logger.debug("Delete: GuiPreferences")
        return

    ##
    #  Properties
    ##

    @property
    def updateTheme(self):
        return self._updateTheme

    @property
    def updateSyntax(self):
        return self._updateSyntax

    @property
    def needsRestart(self):
        return self._needsRestart

    @property
    def refreshTree(self):
        return self._refreshTree

    ##
    #  Slots
    ##

    def _doSave(self):
        """Trigger all the save functions in the tabs, and collect the
        status of the saves.
        """
        logger.debug("Saving new preferences")

        self.tabGeneral.saveValues()
        self.tabProjects.saveValues()
        self.tabDocs.saveValues()
        self.tabEditor.saveValues()
        self.tabSyntax.saveValues()
        self.tabAuto.saveValues()
        self.tabQuote.saveValues()

        self._saveWindowSize()
        CONFIG.saveConfig()
        self.accept()

        return

    def _doClose(self):
        """Close the preferences without saving the changes.
        """
        self._saveWindowSize()
        self.reject()
        return

    ##
    #  Internal Functions
    ##

    def _saveWindowSize(self):
        """Save the dialog window size.
        """
        CONFIG.setPreferencesWinSize(self.width(), self.height())
        return

# END Class GuiPreferences


class GuiPreferencesGeneral(QWidget):

    def __init__(self, prefsGui):
        super().__init__(parent=prefsGui)

        self.prefsGui  = prefsGui
        self.mainGui   = prefsGui.mainGui
        self.mainTheme = prefsGui.mainGui.mainTheme

        # The Form
        self.mainForm = NConfigLayout()
        self.mainForm.setHelpTextStyle(self.mainTheme.helpText)
        self.setLayout(self.mainForm)

        # Look and Feel
        # =============
        self.mainForm.addGroupLabel(self.tr("Look and Feel"))
        minWidth = CONFIG.pxInt(200)

        # Select Locale
        self.guiLocale = QComboBox()
        self.guiLocale.setMinimumWidth(minWidth)
        theLangs = CONFIG.listLanguages(CONFIG.LANG_NW)
        for lang, langName in theLangs:
            self.guiLocale.addItem(langName, lang)
        langIdx = self.guiLocale.findData(CONFIG.guiLocale)
        if langIdx != -1:
            self.guiLocale.setCurrentIndex(langIdx)

        self.mainForm.addRow(
            self.tr("Main GUI language"),
            self.guiLocale,
            self.tr("Requires restart to take effect.")
        )

        # Select Theme
        self.guiTheme = QComboBox()
        self.guiTheme.setMinimumWidth(minWidth)
        self.theThemes = self.mainTheme.listThemes()
        for themeDir, themeName in self.theThemes:
            self.guiTheme.addItem(themeName, themeDir)
        themeIdx = self.guiTheme.findData(CONFIG.guiTheme)
        if themeIdx != -1:
            self.guiTheme.setCurrentIndex(themeIdx)

        self.mainForm.addRow(
            self.tr("Main GUI theme"),
            self.guiTheme,
            self.tr("General colour theme and icons.")
        )

        # Editor Theme
        self.guiSyntax = QComboBox()
        self.guiSyntax.setMinimumWidth(CONFIG.pxInt(200))
        self.theSyntaxes = self.mainTheme.listSyntax()
        for syntaxFile, syntaxName in self.theSyntaxes:
            self.guiSyntax.addItem(syntaxName, syntaxFile)
        syntaxIdx = self.guiSyntax.findData(CONFIG.guiSyntax)
        if syntaxIdx != -1:
            self.guiSyntax.setCurrentIndex(syntaxIdx)

        self.mainForm.addRow(
            self.tr("Editor theme"),
            self.guiSyntax,
            self.tr("Colour theme for the editor and viewer.")
        )

        # Font Family
        self.guiFont = QLineEdit()
        self.guiFont.setReadOnly(True)
        self.guiFont.setFixedWidth(CONFIG.pxInt(162))
        self.guiFont.setText(CONFIG.guiFont)
        self.fontButton = QPushButton("...")
        self.fontButton.setMaximumWidth(int(2.5*self.mainTheme.getTextWidth("...")))
        self.fontButton.clicked.connect(self._selectFont)
        self.mainForm.addRow(
            self.tr("Font family"),
            self.guiFont,
            self.tr("Requires restart to take effect."),
            button=self.fontButton
        )

        # Font Size
        self.guiFontSize = QSpinBox(self)
        self.guiFontSize.setMinimum(8)
        self.guiFontSize.setMaximum(60)
        self.guiFontSize.setSingleStep(1)
        self.guiFontSize.setValue(CONFIG.guiFontSize)
        self.mainForm.addRow(
            self.tr("Font size"),
            self.guiFontSize,
            self.tr("Requires restart to take effect."),
            unit=self.tr("pt")
        )

        # GUI Settings
        # ============
        self.mainForm.addGroupLabel(self.tr("GUI Settings"))

        self.emphLabels = NSwitch()
        self.emphLabels.setChecked(CONFIG.emphLabels)
        self.mainForm.addRow(
            self.tr("Emphasise partition and chapter labels"),
            self.emphLabels,
            self.tr("Makes them stand out in the project tree."),
        )

        self.showFullPath = NSwitch()
        self.showFullPath.setChecked(CONFIG.showFullPath)
        self.mainForm.addRow(
            self.tr("Show full path in document header"),
            self.showFullPath,
            self.tr("Add the parent folder names to the header.")
        )

        self.hideVScroll = NSwitch()
        self.hideVScroll.setChecked(CONFIG.hideVScroll)
        self.mainForm.addRow(
            self.tr("Hide vertical scroll bars in main windows"),
            self.hideVScroll,
            self.tr("Scrolling available with mouse wheel and keys only.")
        )

        self.hideHScroll = NSwitch()
        self.hideHScroll.setChecked(CONFIG.hideHScroll)
        self.mainForm.addRow(
            self.tr("Hide horizontal scroll bars in main windows"),
            self.hideHScroll,
            self.tr("Scrolling available with mouse wheel and keys only.")
        )

        return

    def saveValues(self):
        """Save the values set for this tab.
        """
        guiLocale   = self.guiLocale.currentData()
        guiTheme    = self.guiTheme.currentData()
        guiSyntax   = self.guiSyntax.currentData()
        guiFont     = self.guiFont.text()
        guiFontSize = self.guiFontSize.value()
        emphLabels  = self.emphLabels.isChecked()

        # Update Flags
        self.prefsGui._updateTheme |= CONFIG.guiTheme != guiTheme
        self.prefsGui._updateSyntax |= CONFIG.guiSyntax != guiSyntax
        self.prefsGui._needsRestart |= CONFIG.guiLocale != guiLocale
        self.prefsGui._needsRestart |= CONFIG.guiFont != guiFont
        self.prefsGui._needsRestart |= CONFIG.guiFontSize != guiFontSize
        self.prefsGui._refreshTree |= CONFIG.emphLabels != emphLabels

        CONFIG.guiLocale    = guiLocale
        CONFIG.guiTheme     = guiTheme
        CONFIG.guiSyntax    = guiSyntax
        CONFIG.guiFont      = guiFont
        CONFIG.guiFontSize  = guiFontSize
        CONFIG.emphLabels   = emphLabels
        CONFIG.showFullPath = self.showFullPath.isChecked()
        CONFIG.hideVScroll  = self.hideVScroll.isChecked()
        CONFIG.hideHScroll  = self.hideHScroll.isChecked()

        return

    ##
    #  Slots
    ##

    def _selectFont(self):
        """Open the QFontDialog and set a font for the font style.
        """
        currFont = QFont()
        currFont.setFamily(CONFIG.guiFont)
        currFont.setPointSize(CONFIG.guiFontSize)
        theFont, theStatus = QFontDialog.getFont(currFont, self)
        if theStatus:
            self.guiFont.setText(theFont.family())
            self.guiFontSize.setValue(theFont.pointSize())
        return

# END Class GuiPreferencesGeneral


class GuiPreferencesProjects(QWidget):

    def __init__(self, prefsGui):
        super().__init__(parent=prefsGui)

        self.mainGui   = prefsGui.mainGui
        self.mainTheme = prefsGui.mainGui.mainTheme

        # The Form
        self.mainForm = NConfigLayout()
        self.mainForm.setHelpTextStyle(self.mainTheme.helpText)
        self.setLayout(self.mainForm)

        # Automatic Save
        # ==============
        self.mainForm.addGroupLabel(self.tr("Automatic Save"))

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
        self.mainForm.addGroupLabel(self.tr("Project Backup"))

        # Backup Path
        self.backupPath = CONFIG.backupPath()
        self.backupGetPath = QPushButton(self.tr("Browse"))
        self.backupGetPath.clicked.connect(self._backupFolder)
        self.backupPathRow = self.mainForm.addRow(
            self.tr("Backup storage location"),
            self.backupGetPath,
            self.tr("Path: {0}").format(self.backupPath)
        )

        # Run when closing
        self.backupOnClose = NSwitch()
        self.backupOnClose.setChecked(CONFIG.backupOnClose)
        self.backupOnClose.toggled.connect(self._toggledBackupOnClose)
        self.mainForm.addRow(
            self.tr("Run backup when the project is closed"),
            self.backupOnClose,
            self.tr("Can be overridden for individual projects in Project Settings.")
        )

        # Ask before backup
        # Only enabled when "Run when closing" is checked
        self.askBeforeBackup = NSwitch()
        self.askBeforeBackup.setChecked(CONFIG.askBeforeBackup)
        self.askBeforeBackup.setEnabled(CONFIG.backupOnClose)
        self.mainForm.addRow(
            self.tr("Ask before running backup"),
            self.askBeforeBackup,
            self.tr("If off, backups will run in the background.")
        )

        # Session Timer
        # =============
        self.mainForm.addGroupLabel(self.tr("Session Timer"))

        # Pause when idle
        self.stopWhenIdle = NSwitch()
        self.stopWhenIdle.setChecked(CONFIG.stopWhenIdle)
        self.mainForm.addRow(
            self.tr("Pause the session timer when not writing"),
            self.stopWhenIdle,
            self.tr("Also pauses when the application window does not have focus.")
        )

        # Inactive time for idle
        self.userIdleTime = QDoubleSpinBox()
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

        return

    def saveValues(self):
        """Save the values set for this tab.
        """
        # Automatic Save
        CONFIG.autoSaveDoc  = self.autoSaveDoc.value()
        CONFIG.autoSaveProj = self.autoSaveProj.value()

        # Project Backup
        CONFIG.setBackupPath(self.backupPath)
        CONFIG.backupOnClose   = self.backupOnClose.isChecked()
        CONFIG.askBeforeBackup = self.askBeforeBackup.isChecked()

        # Session Timer
        CONFIG.stopWhenIdle = self.stopWhenIdle.isChecked()
        CONFIG.userIdleTime = round(self.userIdleTime.value() * 60)

        return

    ##
    #  Slots
    ##

    def _backupFolder(self):
        """Open a dialog to select the backup folder.
        """
        currDir = self.backupPath or ""
        newDir = QFileDialog.getExistingDirectory(
            self, self.tr("Backup Directory"), str(currDir), options=QFileDialog.ShowDirsOnly
        )
        if newDir:
            self.backupPath = newDir
            self.mainForm.setHelpText(
                self.backupPathRow, self.tr("Path: {0}").format(self.backupPath)
            )
            return True

        return False

    def _toggledBackupOnClose(self, theState):
        """Enable or disable switch that depends on the backup on close
        switch.
        """
        self.askBeforeBackup.setEnabled(theState)
        return

# END Class GuiPreferencesProjects


class GuiPreferencesDocuments(QWidget):

    def __init__(self, prefsGui):
        super().__init__(parent=prefsGui)

        self.mainGui   = prefsGui.mainGui
        self.mainTheme = prefsGui.mainGui.mainTheme

        # The Form
        self.mainForm = NConfigLayout()
        self.mainForm.setHelpTextStyle(self.mainTheme.helpText)
        self.setLayout(self.mainForm)

        # Text Style
        # ==========
        self.mainForm.addGroupLabel(self.tr("Text Style"))

        # Font Family
        self.textFont = QLineEdit()
        self.textFont.setReadOnly(True)
        self.textFont.setFixedWidth(CONFIG.pxInt(162))
        self.textFont.setText(CONFIG.textFont)
        self.fontButton = QPushButton("...")
        self.fontButton.setMaximumWidth(int(2.5*self.mainTheme.getTextWidth("...")))
        self.fontButton.clicked.connect(self._selectFont)
        self.mainForm.addRow(
            self.tr("Font family"),
            self.textFont,
            self.tr("Applies to both document editor and viewer."),
            button=self.fontButton
        )

        # Font Size
        self.textSize = QSpinBox(self)
        self.textSize.setMinimum(8)
        self.textSize.setMaximum(60)
        self.textSize.setSingleStep(1)
        self.textSize.setValue(CONFIG.textSize)
        self.mainForm.addRow(
            self.tr("Font size"),
            self.textSize,
            self.tr("Applies to both document editor and viewer."),
            unit=self.tr("pt")
        )

        # Text Flow
        # =========
        self.mainForm.addGroupLabel(self.tr("Text Flow"))

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
        self.hideFocusFooter = NSwitch()
        self.hideFocusFooter.setChecked(CONFIG.hideFocusFooter)
        self.mainForm.addRow(
            self.tr("Hide document footer in \"Focus Mode\""),
            self.hideFocusFooter,
            self.tr("Hide the information bar in the document editor.")
        )

        # Justify Text
        self.doJustify = NSwitch()
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

        return

    def saveValues(self):
        """Save the values set for this tab.
        """
        # Text Style
        CONFIG.setTextFont(self.textFont.text(), self.textSize.value())

        # Text Flow
        CONFIG.textWidth       = self.textWidth.value()
        CONFIG.focusWidth      = self.focusWidth.value()
        CONFIG.hideFocusFooter = self.hideFocusFooter.isChecked()
        CONFIG.doJustify       = self.doJustify.isChecked()
        CONFIG.textMargin      = self.textMargin.value()
        CONFIG.tabWidth        = self.tabWidth.value()

        return

    ##
    #  Slots
    ##

    def _selectFont(self):
        """Open the QFontDialog and set a font for the font style.
        """
        currFont = QFont()
        currFont.setFamily(CONFIG.textFont)
        currFont.setPointSize(CONFIG.textSize)
        theFont, theStatus = QFontDialog.getFont(currFont, self)
        if theStatus:
            self.textFont.setText(theFont.family())
            self.textSize.setValue(theFont.pointSize())

        return

# END Class GuiPreferencesDocuments


class GuiPreferencesEditor(QWidget):

    def __init__(self, prefsGui):
        super().__init__(parent=prefsGui)

        self.mainGui   = prefsGui.mainGui
        self.mainTheme = prefsGui.mainGui.mainTheme

        # The Form
        self.mainForm = NConfigLayout()
        self.mainForm.setHelpTextStyle(self.mainTheme.helpText)
        self.setLayout(self.mainForm)

        mW = CONFIG.pxInt(250)

        # Spell Checking
        # ==============
        self.mainForm.addGroupLabel(self.tr("Spell Checking"))

        # Spell Check Provider and Language
        self.spellLanguage = QComboBox(self)
        self.spellLanguage.setMaximumWidth(mW)

        langAvail = self.mainGui.docEditor.spEnchant.listDictionaries()
        if CONFIG.hasEnchant:
            if langAvail:
                for spTag, spProv in langAvail:
                    qLocal = QLocale(spTag)
                    spLang = qLocal.nativeLanguageName().title()
                    self.spellLanguage.addItem("%s [%s]" % (spLang, spProv), spTag)
            else:
                self.spellLanguage.addItem(self.tr("None"), "")
                self.spellLanguage.setEnabled(False)
        else:
            self.spellLanguage.addItem(self.tr("Not installed"), "")
            self.spellLanguage.setEnabled(False)

        spellIdx = self.spellLanguage.findData(CONFIG.spellLanguage)
        if spellIdx != -1:
            self.spellLanguage.setCurrentIndex(spellIdx)

        self.mainForm.addRow(
            self.tr("Spell check language"),
            self.spellLanguage,
            self.tr("Available languages are determined by your system.")
        )

        # Big Document Size Limit
        self.bigDocLimit = QSpinBox(self)
        self.bigDocLimit.setMinimum(10)
        self.bigDocLimit.setMaximum(10000)
        self.bigDocLimit.setSingleStep(10)
        self.bigDocLimit.setValue(CONFIG.bigDocLimit)
        self.mainForm.addRow(
            self.tr("Big document limit"),
            self.bigDocLimit,
            self.tr("Full spell checking is disabled above this limit."),
            unit=self.tr("kB")
        )

        # Word Count
        # ==========
        self.mainForm.addGroupLabel(self.tr("Word Count"))

        # Word Count Timer
        self.wordCountTimer = QDoubleSpinBox(self)
        self.wordCountTimer.setDecimals(1)
        self.wordCountTimer.setMinimum(2.0)
        self.wordCountTimer.setMaximum(600.0)
        self.wordCountTimer.setSingleStep(0.1)
        self.wordCountTimer.setValue(CONFIG.wordCountTimer)
        self.mainForm.addRow(
            self.tr("Word count interval"),
            self.wordCountTimer,
            unit=self.tr("seconds")
        )

        # Include Notes in Word Count
        self.incNotesWCount = NSwitch()
        self.incNotesWCount.setChecked(CONFIG.incNotesWCount)
        self.mainForm.addRow(
            self.tr("Include project notes in status bar word count"),
            self.incNotesWCount
        )

        # Writing Guides
        # ==============
        self.mainForm.addGroupLabel(self.tr("Writing Guides"))

        # Show Tabs and Spaces
        self.showTabsNSpaces = NSwitch()
        self.showTabsNSpaces.setChecked(CONFIG.showTabsNSpaces)
        self.mainForm.addRow(
            self.tr("Show tabs and spaces"),
            self.showTabsNSpaces
        )

        # Show Line Endings
        self.showLineEndings = NSwitch()
        self.showLineEndings.setChecked(CONFIG.showLineEndings)
        self.mainForm.addRow(
            self.tr("Show line endings"),
            self.showLineEndings
        )

        # Scroll Behaviour
        # ================
        self.mainForm.addGroupLabel(self.tr("Scroll Behaviour"))

        # Scroll Past End
        self.scrollPastEnd = QSpinBox(self)
        self.scrollPastEnd.setMinimum(0)
        self.scrollPastEnd.setMaximum(100)
        self.scrollPastEnd.setSingleStep(1)
        self.scrollPastEnd.setValue(int(CONFIG.scrollPastEnd))
        self.mainForm.addRow(
            self.tr("Scroll past end of the document"),
            self.scrollPastEnd,
            self.tr("Set to 0 to disable this feature."),
            unit=self.tr("lines")
        )

        # Typewriter Scrolling
        self.autoScroll = NSwitch()
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

        return

    def saveValues(self):
        """Save the values set for this tab.
        """
        # Spell Checking
        CONFIG.spellLanguage = self.spellLanguage.currentData()
        CONFIG.bigDocLimit   = self.bigDocLimit.value()

        # Word Count
        CONFIG.wordCountTimer = self.wordCountTimer.value()
        CONFIG.incNotesWCount = self.incNotesWCount.isChecked()

        # Writing Guides
        CONFIG.showTabsNSpaces = self.showTabsNSpaces.isChecked()
        CONFIG.showLineEndings = self.showLineEndings.isChecked()

        # Scroll Behaviour
        CONFIG.scrollPastEnd = self.scrollPastEnd.value()
        CONFIG.autoScroll    = self.autoScroll.isChecked()
        CONFIG.autoScrollPos = self.autoScrollPos.value()

        return

# END Class GuiPreferencesEditor


class GuiPreferencesSyntax(QWidget):

    def __init__(self, prefsGui):
        super().__init__(parent=prefsGui)

        self.prefsGui  = prefsGui
        self.mainGui   = prefsGui.mainGui
        self.mainTheme = prefsGui.mainGui.mainTheme

        # The Form
        self.mainForm = NConfigLayout()
        self.mainForm.setHelpTextStyle(self.mainTheme.helpText)
        self.setLayout(self.mainForm)

        # Quotes & Dialogue
        # =================
        self.mainForm.addGroupLabel(self.tr("Quotes & Dialogue"))

        self.highlightQuotes = NSwitch()
        self.highlightQuotes.setChecked(CONFIG.highlightQuotes)
        self.highlightQuotes.toggled.connect(self._toggleHighlightQuotes)
        self.mainForm.addRow(
            self.tr("Highlight text wrapped in quotes"),
            self.highlightQuotes,
            self.tr("Applies to the document editor only.")
        )

        self.allowOpenSQuote = NSwitch()
        self.allowOpenSQuote.setChecked(CONFIG.allowOpenSQuote)
        self.mainForm.addRow(
            self.tr("Allow open-ended single quotes"),
            self.allowOpenSQuote,
            self.tr("Highlight single-quoted line with no closing quote.")
        )

        self.allowOpenDQuote = NSwitch()
        self.allowOpenDQuote.setChecked(CONFIG.allowOpenDQuote)
        self.mainForm.addRow(
            self.tr("Allow open-ended double quotes"),
            self.allowOpenDQuote,
            self.tr("Highlight double-quoted line with no closing quote.")
        )

        # Text Emphasis
        # =============
        self.mainForm.addGroupLabel(self.tr("Text Emphasis"))

        self.highlightEmph = NSwitch()
        self.highlightEmph.setChecked(CONFIG.highlightEmph)
        self.mainForm.addRow(
            self.tr("Add highlight colour to emphasised text"),
            self.highlightEmph,
            self.tr("Applies to the document editor only.")
        )

        # Text Errors
        # ===========

        self.mainForm.addGroupLabel(self.tr("Text Errors"))

        self.showMultiSpaces = NSwitch()
        self.showMultiSpaces.setChecked(CONFIG.showMultiSpaces)
        self.mainForm.addRow(
            self.tr("Highlight multiple or trailing spaces"),
            self.showMultiSpaces,
            self.tr("Applies to the document editor only.")
        )

        return

    def saveValues(self):
        """Save the values set for this tab.
        """
        highlightQuotes = self.highlightQuotes.isChecked()
        allowOpenSQuote = self.allowOpenSQuote.isChecked()
        allowOpenDQuote = self.allowOpenDQuote.isChecked()
        highlightEmph   = self.highlightEmph.isChecked()
        showMultiSpaces = self.showMultiSpaces.isChecked()

        self.prefsGui._updateSyntax |= CONFIG.highlightQuotes != highlightQuotes
        self.prefsGui._updateSyntax |= CONFIG.highlightEmph != highlightEmph
        self.prefsGui._updateSyntax |= CONFIG.showMultiSpaces != showMultiSpaces

        CONFIG.highlightQuotes = highlightQuotes
        CONFIG.allowOpenSQuote = allowOpenSQuote
        CONFIG.allowOpenDQuote = allowOpenDQuote
        CONFIG.highlightEmph   = highlightEmph
        CONFIG.showMultiSpaces = showMultiSpaces

        return

    ##
    #  Slots
    ##

    def _toggleHighlightQuotes(self, theState):
        """Enables or disables switches controlled by the highlight
        quotes switch.
        """
        self.allowOpenSQuote.setEnabled(theState)
        self.allowOpenDQuote.setEnabled(theState)
        return

# END Class GuiPreferencesSyntax


class GuiPreferencesAutomation(QWidget):

    def __init__(self, prefsGui):
        super().__init__(parent=prefsGui)

        self.mainGui   = prefsGui.mainGui
        self.mainTheme = prefsGui.mainGui.mainTheme

        # The Form
        self.mainForm = NConfigLayout()
        self.mainForm.setHelpTextStyle(self.mainTheme.helpText)
        self.setLayout(self.mainForm)

        # Automatic Features
        # ==================
        self.mainForm.addGroupLabel(self.tr("Automatic Features"))

        # Auto-Select Word Under Cursor
        self.autoSelect = NSwitch()
        self.autoSelect.setChecked(CONFIG.autoSelect)
        self.mainForm.addRow(
            self.tr("Auto-select word under cursor"),
            self.autoSelect,
            self.tr("Apply formatting to word under cursor if no selection is made.")
        )

        # Auto-Replace as You Type Main Switch
        self.doReplace = NSwitch()
        self.doReplace.setChecked(CONFIG.doReplace)
        self.doReplace.toggled.connect(self._toggleAutoReplaceMain)
        self.mainForm.addRow(
            self.tr("Auto-replace text as you type"),
            self.doReplace,
            self.tr("Allow the editor to replace symbols as you type.")
        )

        # Replace as You Type
        # ===================
        self.mainForm.addGroupLabel(self.tr("Replace as You Type"))

        # Auto-Replace Single Quotes
        self.doReplaceSQuote = NSwitch()
        self.doReplaceSQuote.setChecked(CONFIG.doReplaceSQuote)
        self.doReplaceSQuote.setEnabled(CONFIG.doReplace)
        self.mainForm.addRow(
            self.tr("Auto-replace single quotes"),
            self.doReplaceSQuote,
            self.tr("Try to guess which is an opening or a closing quote.")
        )

        # Auto-Replace Double Quotes
        self.doReplaceDQuote = NSwitch()
        self.doReplaceDQuote.setChecked(CONFIG.doReplaceDQuote)
        self.doReplaceDQuote.setEnabled(CONFIG.doReplace)
        self.mainForm.addRow(
            self.tr("Auto-replace double quotes"),
            self.doReplaceDQuote,
            self.tr("Try to guess which is an opening or a closing quote.")
        )

        # Auto-Replace Hyphens
        self.doReplaceDash = NSwitch()
        self.doReplaceDash.setChecked(CONFIG.doReplaceDash)
        self.doReplaceDash.setEnabled(CONFIG.doReplace)
        self.mainForm.addRow(
            self.tr("Auto-replace dashes"),
            self.doReplaceDash,
            self.tr("Double and triple hyphens become short and long dashes.")
        )

        # Auto-Replace Dots
        self.doReplaceDots = NSwitch()
        self.doReplaceDots.setChecked(CONFIG.doReplaceDots)
        self.doReplaceDots.setEnabled(CONFIG.doReplace)
        self.mainForm.addRow(
            self.tr("Auto-replace dots"),
            self.doReplaceDots,
            self.tr("Three consecutive dots become ellipsis.")
        )

        # Automatic Padding
        # =================
        self.mainForm.addGroupLabel(self.tr("Automatic Padding"))

        # Pad Before
        self.fmtPadBefore = QLineEdit()
        self.fmtPadBefore.setMaxLength(32)
        self.fmtPadBefore.setText(CONFIG.fmtPadBefore)
        self.mainForm.addRow(
            self.tr("Insert non-breaking space before"),
            self.fmtPadBefore,
            self.tr("Automatically add space before any of these symbols."),
        )

        # Pad After
        self.fmtPadAfter = QLineEdit()
        self.fmtPadAfter.setMaxLength(32)
        self.fmtPadAfter.setText(CONFIG.fmtPadAfter)
        self.mainForm.addRow(
            self.tr("Insert non-breaking space after"),
            self.fmtPadAfter,
            self.tr("Automatically add space after any of these symbols."),
        )

        # Use Thin Space
        self.fmtPadThin = NSwitch()
        self.fmtPadThin.setChecked(CONFIG.fmtPadThin)
        self.fmtPadThin.setEnabled(CONFIG.doReplace)
        self.mainForm.addRow(
            self.tr("Use thin space instead"),
            self.fmtPadThin,
            self.tr("Inserts a thin space instead of a regular space.")
        )

        return

    def saveValues(self):
        """Save the values set for this tab.
        """
        # Automatic Features
        CONFIG.autoSelect = self.autoSelect.isChecked()
        CONFIG.doReplace  = self.doReplace.isChecked()

        # Replace as You Type
        CONFIG.doReplaceSQuote = self.doReplaceSQuote.isChecked()
        CONFIG.doReplaceDQuote = self.doReplaceDQuote.isChecked()
        CONFIG.doReplaceDash   = self.doReplaceDash.isChecked()
        CONFIG.doReplaceDots   = self.doReplaceDots.isChecked()

        # Automatic Padding
        CONFIG.fmtPadBefore = self.fmtPadBefore.text().strip()
        CONFIG.fmtPadAfter  = self.fmtPadAfter.text().strip()
        CONFIG.fmtPadThin   = self.fmtPadThin.isChecked()

        return

    ##
    #  Slots
    ##

    def _toggleAutoReplaceMain(self, theState):
        """Enables or disables switches controlled by the main auto
        replace switch.
        """
        self.doReplaceSQuote.setEnabled(theState)
        self.doReplaceDQuote.setEnabled(theState)
        self.doReplaceDash.setEnabled(theState)
        self.doReplaceDots.setEnabled(theState)
        self.fmtPadThin.setEnabled(theState)
        return

# END Class GuiPreferencesAutomation


class GuiPreferencesQuotes(QWidget):

    def __init__(self, prefsGui):
        super().__init__(parent=prefsGui)

        self.mainGui   = prefsGui.mainGui
        self.mainTheme = prefsGui.mainGui.mainTheme

        # The Form
        self.mainForm = NConfigLayout()
        self.mainForm.setHelpTextStyle(self.mainTheme.helpText)
        self.setLayout(self.mainForm)

        # Quotation Style
        # ===============
        self.mainForm.addGroupLabel(self.tr("Quotation Style"))

        qWidth = CONFIG.pxInt(40)
        bWidth = int(2.5*self.mainTheme.getTextWidth("..."))
        self.quoteSym = {}

        # Single Quote Style
        self.quoteSym["SO"] = QLineEdit()
        self.quoteSym["SO"].setMaxLength(1)
        self.quoteSym["SO"].setReadOnly(True)
        self.quoteSym["SO"].setFixedWidth(qWidth)
        self.quoteSym["SO"].setAlignment(Qt.AlignCenter)
        self.quoteSym["SO"].setText(CONFIG.fmtSQuoteOpen)
        self.btnSingleStyleO = QPushButton("...")
        self.btnSingleStyleO.setMaximumWidth(bWidth)
        self.btnSingleStyleO.clicked.connect(lambda: self._getQuote("SO"))
        self.mainForm.addRow(
            self.tr("Single quote open style"),
            self.quoteSym["SO"],
            self.tr("The symbol to use for a leading single quote."),
            button=self.btnSingleStyleO
        )

        self.quoteSym["SC"] = QLineEdit()
        self.quoteSym["SC"].setMaxLength(1)
        self.quoteSym["SC"].setReadOnly(True)
        self.quoteSym["SC"].setFixedWidth(qWidth)
        self.quoteSym["SC"].setAlignment(Qt.AlignCenter)
        self.quoteSym["SC"].setText(CONFIG.fmtSQuoteClose)
        self.btnSingleStyleC = QPushButton("...")
        self.btnSingleStyleC.setMaximumWidth(bWidth)
        self.btnSingleStyleC.clicked.connect(lambda: self._getQuote("SC"))
        self.mainForm.addRow(
            self.tr("Single quote close style"),
            self.quoteSym["SC"],
            self.tr("The symbol to use for a trailing single quote."),
            button=self.btnSingleStyleC
        )

        # Double Quote Style
        self.quoteSym["DO"] = QLineEdit()
        self.quoteSym["DO"].setMaxLength(1)
        self.quoteSym["DO"].setReadOnly(True)
        self.quoteSym["DO"].setFixedWidth(qWidth)
        self.quoteSym["DO"].setAlignment(Qt.AlignCenter)
        self.quoteSym["DO"].setText(CONFIG.fmtDQuoteOpen)
        self.btnDoubleStyleO = QPushButton("...")
        self.btnDoubleStyleO.setMaximumWidth(bWidth)
        self.btnDoubleStyleO.clicked.connect(lambda: self._getQuote("DO"))
        self.mainForm.addRow(
            self.tr("Double quote open style"),
            self.quoteSym["DO"],
            self.tr("The symbol to use for a leading double quote."),
            button=self.btnDoubleStyleO
        )

        self.quoteSym["DC"] = QLineEdit()
        self.quoteSym["DC"].setMaxLength(1)
        self.quoteSym["DC"].setReadOnly(True)
        self.quoteSym["DC"].setFixedWidth(qWidth)
        self.quoteSym["DC"].setAlignment(Qt.AlignCenter)
        self.quoteSym["DC"].setText(CONFIG.fmtDQuoteClose)
        self.btnDoubleStyleC = QPushButton("...")
        self.btnDoubleStyleC.setMaximumWidth(bWidth)
        self.btnDoubleStyleC.clicked.connect(lambda: self._getQuote("DC"))
        self.mainForm.addRow(
            self.tr("Double quote close style"),
            self.quoteSym["DC"],
            self.tr("The symbol to use for a trailing double quote."),
            button=self.btnDoubleStyleC
        )

        return

    def saveValues(self):
        """Save the values set for this tab.
        """
        # Quotation Style
        CONFIG.fmtSQuoteOpen = self.quoteSym["SO"].text()
        CONFIG.fmtSQuoteClose = self.quoteSym["SC"].text()
        CONFIG.fmtDQuoteOpen = self.quoteSym["DO"].text()
        CONFIG.fmtDQuoteClose = self.quoteSym["DC"].text()
        return

    ##
    #  Slots
    ##

    def _getQuote(self, qType):
        """Dialog for single quote open.
        """
        qtBox = GuiQuoteSelect(self, currentQuote=self.quoteSym[qType].text())
        if qtBox.exec_() == QDialog.Accepted:
            self.quoteSym[qType].setText(qtBox.selectedQuote)

        return

# END Class GuiPreferencesQuotes
