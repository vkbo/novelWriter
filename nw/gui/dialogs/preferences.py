# -*- coding: utf-8 -*-
"""novelWriter GUI Config Editor

 novelWriter – GUI Config Editor
=================================
 Class holding the config dialog

 File History:
 Created: 2019-06-10 [0.1.5]

 This file is a part of novelWriter
 Copyright 2020, Veronica Berglyd Olsen

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
import nw

from os import path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QDialog, QWidget, QComboBox, QSpinBox, QPushButton, QLineEdit, QMessageBox,
    QDialogButtonBox, QFileDialog, QFontDialog
)

from nw.gui.additions import QSwitch, QConfigLayout, PagedDialog
from nw.core import NWSpellCheck, NWSpellSimple, NWSpellEnchant
from nw.constants import nwAlert, nwQuotes

logger = logging.getLogger(__name__)

class GuiPreferences(PagedDialog):

    def __init__(self, theParent, theProject):
        PagedDialog.__init__(self, theParent)

        logger.debug("Initialising GuiPreferences ...")

        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theProject = theProject

        self.setWindowTitle("Preferences")

        self.tabGeneral = GuiConfigEditGeneralTab(self.theParent)
        self.tabLayout  = GuiConfigEditLayoutTab(self.theParent)
        self.tabEditing = GuiConfigEditEditingTab(self.theParent)
        self.tabAutoRep = GuiConfigEditAutoReplaceTab(self.theParent)

        self.addTab(self.tabGeneral, "General")
        self.addTab(self.tabLayout,  "Layout")
        self.addTab(self.tabEditing, "Editor")
        self.addTab(self.tabAutoRep, "Auto-Replace")

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self._doSave)
        self.buttonBox.rejected.connect(self._doClose)
        self.addControls(self.buttonBox)

        self.show()

        logger.debug("GuiPreferences initialisation complete")

        return

    ##
    #  Buttons
    ##

    def _doSave(self):

        logger.verbose("ConfigEditor save button clicked")

        validEntries = True
        needsRestart = False

        retA, retB = self.tabGeneral.saveValues()
        validEntries &= retA
        needsRestart |= retB

        retA, retB = self.tabLayout.saveValues()
        validEntries &= retA
        needsRestart |= retB

        retA, retB = self.tabEditing.saveValues()
        validEntries &= retA
        needsRestart |= retB

        retA, retB = self.tabAutoRep.saveValues()
        validEntries &= retA
        needsRestart |= retB

        if needsRestart:
            msgBox = QMessageBox()
            msgBox.information(
                self, "Preferences",
                "Some changes will not be applied until %s has been restarted." % nw.__package__
            )

        if validEntries:
            self.accept()

        return

    def _doClose(self):
        logger.verbose("ConfigEditor close button clicked")
        self.close()
        return

# END Class GuiPreferences

class GuiConfigEditGeneralTab(QWidget):

    def __init__(self, theParent):
        QWidget.__init__(self, theParent)

        self.mainConf  = nw.CONFIG
        self.theParent = theParent
        self.theTheme  = theParent.theTheme

        # The Form
        self.mainForm = QConfigLayout()
        self.mainForm.setHelpTextStyle(self.theTheme.helpText)
        self.setLayout(self.mainForm)

        # Look and Feel
        # =============
        self.mainForm.addGroupLabel("Look and Feel")

        ## Select Theme
        self.selectTheme = QComboBox()
        self.selectTheme.setMinimumWidth(200)
        self.theThemes = self.theTheme.listThemes()
        for themeDir, themeName in self.theThemes:
            self.selectTheme.addItem(themeName, themeDir)
        themeIdx = self.selectTheme.findData(self.mainConf.guiTheme)
        if themeIdx != -1:
            self.selectTheme.setCurrentIndex(themeIdx)

        self.mainForm.addRow(
            "Main GUI theme",
            self.selectTheme,
            "Changing this requires restarting %s." % nw.__package__
        )

        ## Select Icon Theme
        self.selectIcons = QComboBox()
        self.selectIcons.setMinimumWidth(200)
        self.theIcons = self.theTheme.theIcons.listThemes()
        for iconDir, iconName in self.theIcons:
            self.selectIcons.addItem(iconName, iconDir)
        iconIdx = self.selectIcons.findData(self.mainConf.guiIcons)
        if iconIdx != -1:
            self.selectIcons.setCurrentIndex(iconIdx)

        self.mainForm.addRow(
            "Main icon theme",
            self.selectIcons,
            "Changing this requires restarting %s." % nw.__package__
        )

        ## Dark Icons
        self.preferDarkIcons = QSwitch()
        self.preferDarkIcons.setChecked(self.mainConf.guiDark)
        self.mainForm.addRow(
            "Prefer icons for dark backgrounds",
            self.preferDarkIcons,
            "This may improve the look of icons on dark themes."
        )

        ## Font Family
        self.guiFont = QLineEdit()
        self.guiFont.setReadOnly(True)
        self.guiFont.setFixedWidth(162)
        self.guiFont.setText(self.mainConf.guiFont)
        self.fontButton = QPushButton("...")
        self.fontButton.setMaximumWidth(int(2.5*self.theTheme.getTextWidth("...")))
        self.fontButton.clicked.connect(self._selectFont)
        self.mainForm.addRow(
            "Font family",
            self.guiFont,
            "Changing this requires restarting %s." % nw.__package__,
            theButton = self.fontButton
        )

        ## Font Size
        self.guiFontSize = QSpinBox(self)
        self.guiFontSize.setMinimum(8)
        self.guiFontSize.setMaximum(60)
        self.guiFontSize.setSingleStep(1)
        self.guiFontSize.setValue(self.mainConf.guiFontSize)
        self.mainForm.addRow(
            "Font size",
            self.guiFontSize,
            "Changing this requires restarting %s." % nw.__package__,
            theUnit = "pt"
        )

        # GUI Settings
        # ============
        self.mainForm.addGroupLabel("GUI Settings")

        self.showFullPath = QSwitch()
        self.showFullPath.setChecked(self.mainConf.showFullPath)
        self.mainForm.addRow(
            "Show full path in document header",
            self.showFullPath
        )

        # AutoSave Settings
        # =================
        self.mainForm.addGroupLabel("Automatic Save")

        ## Document Save Timer
        self.autoSaveDoc = QSpinBox(self)
        self.autoSaveDoc.setMinimum(5)
        self.autoSaveDoc.setMaximum(600)
        self.autoSaveDoc.setSingleStep(1)
        self.autoSaveDoc.setValue(self.mainConf.autoSaveDoc)
        self.backupPathRow = self.mainForm.addRow(
            "Save interval for the currently open document",
            self.autoSaveDoc,
            theUnit="seconds"
        )

        ## Project Save Timer
        self.autoSaveProj = QSpinBox(self)
        self.autoSaveProj.setMinimum(5)
        self.autoSaveProj.setMaximum(600)
        self.autoSaveProj.setSingleStep(1)
        self.autoSaveProj.setValue(self.mainConf.autoSaveProj)
        self.backupPathRow = self.mainForm.addRow(
            "Save interval for the currently open project",
            self.autoSaveProj,
            theUnit="seconds"
        )

        # Backup Settings
        # ===============
        self.mainForm.addGroupLabel("Project Backup")

        ## Backup Path
        self.backupPath = self.mainConf.backupPath
        self.backupGetPath = QPushButton("Browse")
        self.backupGetPath.clicked.connect(self._backupFolder)
        self.backupPathRow = self.mainForm.addRow(
            "Backup storage location",
            self.backupGetPath,
            "Path: %s" % self.backupPath
        )

        ## Run when closing
        self.backupOnClose = QSwitch()
        self.backupOnClose.setChecked(self.mainConf.backupOnClose)
        self.backupOnClose.toggled.connect(self._toggledBackupOnClose)
        self.mainForm.addRow(
            "Run backup when closing project",
            self.backupOnClose,
            "This option can be overridden in project settings."
        )

        ## Ask before backup
        ## Only enabled when "Run when closing" is checked
        self.askBeforeBackup = QSwitch()
        self.askBeforeBackup.setChecked(self.mainConf.askBeforeBackup)
        self.askBeforeBackup.setEnabled(self.mainConf.backupOnClose)
        self.mainForm.addRow(
            "Ask before running backup",
            self.askBeforeBackup
        )

        return

    def saveValues(self):

        validEntries = True
        needsRestart = False

        guiTheme        = self.selectTheme.currentData()
        guiIcons        = self.selectIcons.currentData()
        guiDark         = self.preferDarkIcons.isChecked()
        guiFont         = self.guiFont.text()
        guiFontSize     = self.guiFontSize.value()
        showFullPath    = self.showFullPath.isChecked()
        autoSaveDoc     = self.autoSaveDoc.value()
        autoSaveProj    = self.autoSaveProj.value()
        backupPath      = self.backupPath
        backupOnClose   = self.backupOnClose.isChecked()
        askBeforeBackup = self.askBeforeBackup.isChecked()

        # Check if restart is needed
        needsRestart |= self.mainConf.guiTheme != guiTheme
        needsRestart |= self.mainConf.guiIcons != guiIcons
        needsRestart |= self.mainConf.guiFont != guiFont
        needsRestart |= self.mainConf.guiFontSize != guiFontSize

        self.mainConf.guiTheme        = guiTheme
        self.mainConf.guiIcons        = guiIcons
        self.mainConf.guiDark         = guiDark
        self.mainConf.guiFont         = guiFont
        self.mainConf.guiFontSize     = guiFontSize
        self.mainConf.showFullPath    = showFullPath
        self.mainConf.autoSaveDoc     = autoSaveDoc
        self.mainConf.autoSaveProj    = autoSaveProj
        self.mainConf.backupPath      = backupPath
        self.mainConf.backupOnClose   = backupOnClose
        self.mainConf.askBeforeBackup = askBeforeBackup

        self.mainConf.confChanged = True

        return validEntries, needsRestart

    ##
    #  Slots
    ##

    def _backupFolder(self):

        currDir = self.backupPath
        if not path.isdir(currDir):
            currDir = ""

        dlgOpt  = QFileDialog.Options()
        dlgOpt |= QFileDialog.ShowDirsOnly
        dlgOpt |= QFileDialog.DontUseNativeDialog
        newDir = QFileDialog.getExistingDirectory(
            self,"Backup Directory",currDir,options=dlgOpt
        )
        if newDir:
            self.backupPath = newDir
            self.mainForm.setHelpText(self.backupPathRow, "Path: %s" % self.backupPath)
            return True

        return False

    def _toggledBackupOnClose(self, theState):
        """Enable or disable switch that depends on the backup on close
        switch,
        """
        self.askBeforeBackup.setEnabled(theState)
        return

    def _selectFont(self):
        """Open the QFontDialog and set a font for the font style.
        """
        currFont = QFont()
        currFont.setFamily(self.mainConf.guiFont)
        currFont.setPointSize(self.mainConf.guiFontSize)
        theFont, theStatus = QFontDialog.getFont(currFont, self)
        if theStatus:
            self.guiFont.setText(theFont.family())
            self.guiFontSize.setValue(theFont.pointSize())
        return

# END Class GuiConfigEditGeneralTab

class GuiConfigEditLayoutTab(QWidget):

    def __init__(self, theParent):
        QWidget.__init__(self, theParent)

        self.mainConf  = nw.CONFIG
        self.theParent = theParent
        self.theTheme  = theParent.theTheme

        # The Form
        self.mainForm = QConfigLayout()
        self.mainForm.setHelpTextStyle(self.theTheme.helpText)
        self.setLayout(self.mainForm)

        # Text Style
        # ==========
        self.mainForm.addGroupLabel("Text Style")


        ## Font Family
        self.textStyleFont = QLineEdit()
        self.textStyleFont.setReadOnly(True)
        self.textStyleFont.setFixedWidth(162)
        self.textStyleFont.setText(self.mainConf.textFont)
        self.fontButton = QPushButton("...")
        self.fontButton.setMaximumWidth(int(2.5*self.theTheme.getTextWidth("...")))
        self.fontButton.clicked.connect(self._selectFont)
        self.mainForm.addRow(
            "Font family",
            self.textStyleFont,
            "Font for the document editor and viewer.",
            theButton = self.fontButton
        )

        ## Font Size
        self.textStyleSize = QSpinBox(self)
        self.textStyleSize.setMinimum(8)
        self.textStyleSize.setMaximum(60)
        self.textStyleSize.setSingleStep(1)
        self.textStyleSize.setValue(self.mainConf.textSize)
        self.mainForm.addRow(
            "Font size",
            self.textStyleSize,
            theUnit = "pt"
        )

        # Text Flow
        # =========
        self.mainForm.addGroupLabel("Text Flow")

        ## Max Text Width in Normal Mode
        self.textFlowMax = QSpinBox(self)
        self.textFlowMax.setMinimum(300)
        self.textFlowMax.setMaximum(10000)
        self.textFlowMax.setSingleStep(10)
        self.textFlowMax.setValue(self.mainConf.textWidth)
        self.mainForm.addRow(
            "Maximum text width in \"Normal Mode\"",
            self.textFlowMax,
            theUnit="px"
        )

        ## Max Text Width in Zen Mode
        self.zenDocWidth = QSpinBox(self)
        self.zenDocWidth.setMinimum(300)
        self.zenDocWidth.setMaximum(10000)
        self.zenDocWidth.setSingleStep(10)
        self.zenDocWidth.setValue(self.mainConf.zenWidth)
        self.mainForm.addRow(
            "Maximum text width in \"Zen Mode\"",
            self.zenDocWidth,
            theUnit="px"
        )

        ## Document Fixed Width
        self.textFlowFixed = QSwitch()
        self.textFlowFixed.setChecked(not self.mainConf.textFixedW)
        self.mainForm.addRow(
            "Disable maximum text width in \"Normal Mode\"",
            self.textFlowFixed,
            "If disabled, minimum text width is defined by the margin setting."
        )

        ## Justify Text
        self.textJustify = QSwitch()
        self.textJustify.setChecked(self.mainConf.textFixedW)
        self.mainForm.addRow(
            "Justify the text margins in editor and viewer",
            self.textJustify
        )

        ## Document Margins
        self.textMargin = QSpinBox(self)
        self.textMargin.setMinimum(0)
        self.textMargin.setMaximum(900)
        self.textMargin.setSingleStep(1)
        self.textMargin.setValue(self.mainConf.textMargin)
        self.mainForm.addRow(
            "Document text margin",
            self.textMargin,
            "If max width is enabled, this is the minimum margin.",
            theUnit="px"
        )

        ## Tab Width
        self.tabWidth = QSpinBox(self)
        self.tabWidth.setMinimum(0)
        self.tabWidth.setMaximum(200)
        self.tabWidth.setSingleStep(1)
        self.tabWidth.setValue(self.mainConf.tabWidth)
        self.mainForm.addRow(
            "Editor tab width",
            self.tabWidth,
            "This feature requires Qt 5.9 or later.",
            theUnit="px"
        )

        # Writing Guides
        # ==============
        self.mainForm.addGroupLabel("Writing Guides")

        ## Show Tabs and Spaces
        self.showTabsNSpaces = QSwitch()
        self.showTabsNSpaces.setChecked(self.mainConf.showTabsNSpaces)
        self.mainForm.addRow(
            "Show tabs and spaces",
            self.showTabsNSpaces
        )

        ## Show Line Endings
        self.showLineEndings = QSwitch()
        self.showLineEndings.setChecked(self.mainConf.showLineEndings)
        self.mainForm.addRow(
            "Show line endings",
            self.showLineEndings
        )

        return

    def saveValues(self):

        validEntries = True
        needsRestart = False

        textFont        = self.textStyleFont.text()
        textSize        = self.textStyleSize.value()
        textWidth       = self.textFlowMax.value()
        zenWidth        = self.zenDocWidth.value()
        textFixedW      = not self.textFlowFixed.isChecked()
        doJustify       = self.textJustify.isChecked()
        textMargin      = self.textMargin.value()
        tabWidth        = self.tabWidth.value()
        showTabsNSpaces = self.showTabsNSpaces.isChecked()
        showLineEndings = self.showLineEndings.isChecked()

        self.mainConf.textFont        = textFont
        self.mainConf.textSize        = textSize
        self.mainConf.textWidth       = textWidth
        self.mainConf.zenWidth        = zenWidth
        self.mainConf.textFixedW      = textFixedW
        self.mainConf.doJustify       = doJustify
        self.mainConf.textMargin      = textMargin
        self.mainConf.tabWidth        = tabWidth
        self.mainConf.showTabsNSpaces = showTabsNSpaces
        self.mainConf.showLineEndings = showLineEndings

        self.mainConf.confChanged = True

        return validEntries, needsRestart

    ##
    #  Slots
    ##

    def _selectFont(self):
        """Open the QFontDialog and set a font for the font style.
        """
        currFont = QFont()
        currFont.setFamily(self.mainConf.textFont)
        currFont.setPointSize(self.mainConf.textSize)
        theFont, theStatus = QFontDialog.getFont(currFont, self)
        if theStatus:
            self.textStyleFont.setText(theFont.family())
            self.textStyleSize.setValue(theFont.pointSize())
        return

# END Class GuiConfigEditLayoutTab

class GuiConfigEditEditingTab(QWidget):

    def __init__(self, theParent):
        QWidget.__init__(self, theParent)

        self.mainConf  = nw.CONFIG
        self.theParent = theParent
        self.theTheme  = theParent.theTheme

        # The Form
        self.mainForm = QConfigLayout()
        self.mainForm.setHelpTextStyle(self.theTheme.helpText)
        self.setLayout(self.mainForm)

        # Spell Checking
        # ==============
        self.mainForm.addGroupLabel("Syntax Highlighting")

        ## Syntax Highlighting
        self.selectSyntax = QComboBox()
        self.selectSyntax.setMinimumWidth(200)
        self.theSyntaxes = self.theTheme.listSyntax()
        for syntaxFile, syntaxName in self.theSyntaxes:
            self.selectSyntax.addItem(syntaxName, syntaxFile)
        syntaxIdx = self.selectSyntax.findData(self.mainConf.guiSyntax)
        if syntaxIdx != -1:
            self.selectSyntax.setCurrentIndex(syntaxIdx)

        self.mainForm.addRow(
            "Highlight theme",
            self.selectSyntax,
            ""
        )

        self.highlightQuotes = QSwitch()
        self.highlightQuotes.setChecked(self.mainConf.highlightQuotes)
        self.mainForm.addRow(
            "Highlight text wrapped in quotes",
            self.highlightQuotes
        )

        # Spell Checking
        # ==============
        self.mainForm.addGroupLabel("Spell Checking")

        ## Spell Check Provider and Language
        self.spellLangList = QComboBox(self)
        self.spellToolList = QComboBox(self)
        self.spellToolList.addItem("Internal (difflib)",        NWSpellCheck.SP_INTERNAL)
        self.spellToolList.addItem("Spell Enchant (pyenchant)", NWSpellCheck.SP_ENCHANT)
        # self.spellToolList.addItem("SymSpell (symspellpy)",     NWSpellCheck.SP_SYMSPELL)

        theModel   = self.spellToolList.model()
        idEnchant  = self.spellToolList.findData(NWSpellCheck.SP_ENCHANT)
        # idSymSpell = self.spellToolList.findData(NWSpellCheck.SP_SYMSPELL)
        theModel.item(idEnchant).setEnabled(self.mainConf.hasEnchant)
        # theModel.item(idSymSpell).setEnabled(self.mainConf.hasSymSpell)

        self.spellToolList.currentIndexChanged.connect(self._doUpdateSpellTool)
        toolIdx = self.spellToolList.findData(self.mainConf.spellTool)
        if toolIdx != -1:
            self.spellToolList.setCurrentIndex(toolIdx)
        self._doUpdateSpellTool(0)

        self.mainForm.addRow(
            "Spell check provider",
            self.spellToolList,
            "Note that the internal spell check tool is quite slow."
        )
        self.mainForm.addRow(
            "Spell check language",
            self.spellLangList
        )

        ## Big Document Size Limit
        self.bigDocLimit = QSpinBox(self)
        self.bigDocLimit.setMinimum(10)
        self.bigDocLimit.setMaximum(10000)
        self.bigDocLimit.setSingleStep(10)
        self.bigDocLimit.setValue(self.mainConf.bigDocLimit)
        self.mainForm.addRow(
            "Big document limit",
            self.bigDocLimit,
            "Disables full spell checking over the size limit.",
            theUnit="kB"
        )

        return

    def saveValues(self):

        validEntries = True
        needsRestart = False

        guiSyntax       = self.selectSyntax.currentData()
        highlightQuotes = self.highlightQuotes.isChecked()
        spellTool       = self.spellToolList.currentData()
        spellLanguage   = self.spellLangList.currentData()
        bigDocLimit     = self.bigDocLimit.value()

        self.mainConf.guiSyntax       = guiSyntax
        self.mainConf.highlightQuotes = highlightQuotes
        self.mainConf.spellTool       = spellTool
        self.mainConf.spellLanguage   = spellLanguage
        self.mainConf.bigDocLimit     = bigDocLimit

        self.mainConf.confChanged = True

        return validEntries, needsRestart

    ##
    #  Internal Functions
    ##

    def _disableComboItem(self, theList, theValue):
        theIdx = theList.findData(theValue)
        theModel = theList.model()
        anItem = theModel.item(1)
        anItem.setFlags(anItem.flags() ^ Qt.ItemIsEnabled)
        return theModel

    def _doUpdateSpellTool(self, currIdx):
        spellTool = self.spellToolList.currentData()
        self._updateLanguageList(spellTool)
        return

    def _updateLanguageList(self, spellTool):
        """Updates the list of available spell checking dictionaries
        available for the selected spell check tool. It will try to
        preserve the language choice, if the language exists in the
        updated list.
        """
        if spellTool == NWSpellCheck.SP_ENCHANT:
            theDict = NWSpellEnchant()
        else:
            theDict = NWSpellSimple()

        self.spellLangList.clear()
        for spTag, spName in theDict.listDictionaries():
            self.spellLangList.addItem(spName, spTag)

        spellIdx = self.spellLangList.findData(self.mainConf.spellLanguage)
        if spellIdx != -1:
            self.spellLangList.setCurrentIndex(spellIdx)

        return

# END Class GuiConfigEditEditingTab

class GuiConfigEditAutoReplaceTab(QWidget):

    def __init__(self, theParent):
        QWidget.__init__(self, theParent)

        self.mainConf  = nw.CONFIG
        self.theParent = theParent
        self.theTheme  = theParent.theTheme

        # The Form
        self.mainForm = QConfigLayout()
        self.mainForm.setHelpTextStyle(self.theTheme.helpText)
        self.setLayout(self.mainForm)

        # Automatic Features
        # ==================
        self.mainForm.addGroupLabel("Automatic Features")

        ## Auto-Select Word Under Cursor
        self.autoSelect = QSwitch()
        self.autoSelect.setChecked(self.mainConf.autoSelect)
        self.mainForm.addRow(
            "Auto-select word under cursor",
            self.autoSelect,
            "Apply formatting to word under cursor if no selection is made."
        )

        ## Auto-Replace as You Type Main Switch
        self.autoReplaceMain = QSwitch()
        self.autoReplaceMain.setChecked(self.mainConf.doReplace)
        self.autoReplaceMain.toggled.connect(self._toggleAutoReplaceMain)
        self.mainForm.addRow(
            "Auto-replace text as you type",
            self.autoReplaceMain,
            "Apply formatting to word under cursor if no selection is made."
        )

        # Auto-Replace
        # ============
        self.mainForm.addGroupLabel("Replace as You Type")

        ## Auto-Replace Single Quotes
        self.autoReplaceSQ = QSwitch()
        self.autoReplaceSQ.setChecked(self.mainConf.doReplaceSQuote)
        self.autoReplaceSQ.setEnabled(self.mainConf.doReplace)
        self.mainForm.addRow(
            "Auto-replace single quotes",
            self.autoReplaceSQ,
            "The feature will try to guess opening or closing single quote."
        )

        ## Auto-Replace Double Quotes
        self.autoReplaceDQ = QSwitch()
        self.autoReplaceDQ.setChecked(self.mainConf.doReplaceDQuote)
        self.autoReplaceDQ.setEnabled(self.mainConf.doReplace)
        self.mainForm.addRow(
            "Auto-replace double quotes",
            self.autoReplaceDQ,
            "The feature will try to guess opening or closing quote quote."
        )

        ## Auto-Replace Hyphens
        self.autoReplaceDash = QSwitch()
        self.autoReplaceDash.setChecked(self.mainConf.doReplaceDash)
        self.autoReplaceDash.setEnabled(self.mainConf.doReplace)
        self.mainForm.addRow(
            "Auto-replace dashes",
            self.autoReplaceDash,
            "Auto-replace double and triple hyphens with short and long dash."
        )

        ## Auto-Replace Dots
        self.autoReplaceDots = QSwitch()
        self.autoReplaceDots.setChecked(self.mainConf.doReplaceDots)
        self.autoReplaceDots.setEnabled(self.mainConf.doReplace)
        self.mainForm.addRow(
            "Auto-replace dots",
            self.autoReplaceDots,
            "Auto-replace three dots with ellipsis."
        )

        # Quotation Style
        # ===============
        self.mainForm.addGroupLabel("Quotation Style")

        ## Single Quote Style
        self.quoteSingleStyleO = QLineEdit()
        self.quoteSingleStyleO.setMaxLength(1)
        self.quoteSingleStyleO.setFixedWidth(40)
        self.quoteSingleStyleO.setAlignment(Qt.AlignCenter)
        self.quoteSingleStyleO.setText(self.mainConf.fmtSingleQuotes[0])
        self.mainForm.addRow(
            "Single quote open style",
            self.quoteSingleStyleO,
            "Auto-replaces apostrophe before words."
        )

        self.quoteSingleStyleC = QLineEdit()
        self.quoteSingleStyleC.setMaxLength(1)
        self.quoteSingleStyleC.setFixedWidth(40)
        self.quoteSingleStyleC.setAlignment(Qt.AlignCenter)
        self.quoteSingleStyleC.setText(self.mainConf.fmtSingleQuotes[1])
        self.mainForm.addRow(
            "Single quote close style",
            self.quoteSingleStyleC,
            "Auto-replaces apostrophe after words."
        )

        ## Double Quote Style
        self.quoteDoubleStyleO = QLineEdit()
        self.quoteDoubleStyleO.setMaxLength(1)
        self.quoteDoubleStyleO.setFixedWidth(40)
        self.quoteDoubleStyleO.setAlignment(Qt.AlignCenter)
        self.quoteDoubleStyleO.setText(self.mainConf.fmtDoubleQuotes[0])
        self.mainForm.addRow(
            "Double quote open style",
            self.quoteDoubleStyleO,
            "Auto-replaces straight quotes before words."
        )

        self.quoteDoubleStyleC = QLineEdit()
        self.quoteDoubleStyleC.setMaxLength(1)
        self.quoteDoubleStyleC.setFixedWidth(40)
        self.quoteDoubleStyleC.setAlignment(Qt.AlignCenter)
        self.quoteDoubleStyleC.setText(self.mainConf.fmtDoubleQuotes[1])
        self.mainForm.addRow(
            "Double quote close style",
            self.quoteDoubleStyleC,
            "Auto-replaces straight quotes after words."
        )

        return

    def saveValues(self):

        validEntries = True
        needsRestart = False

        autoSelect      = self.autoSelect.isChecked()
        doReplace       = self.autoReplaceMain.isChecked()
        doReplaceSQuote = self.autoReplaceSQ.isChecked()
        doReplaceDQuote = self.autoReplaceDQ.isChecked()
        doReplaceDash   = self.autoReplaceDash.isChecked()
        doReplaceDots   = self.autoReplaceDots.isChecked()

        self.mainConf.autoSelect      = autoSelect
        self.mainConf.doReplace       = doReplace
        self.mainConf.doReplaceSQuote = doReplaceSQuote
        self.mainConf.doReplaceDQuote = doReplaceDQuote
        self.mainConf.doReplaceDash   = doReplaceDash
        self.mainConf.doReplaceDots   = doReplaceDots

        fmtSingleQuotesO = self.quoteSingleStyleO.text()
        fmtSingleQuotesC = self.quoteSingleStyleC.text()
        fmtDoubleQuotesO = self.quoteDoubleStyleO.text()
        fmtDoubleQuotesC = self.quoteDoubleStyleC.text()

        if self._checkQuoteSymbol(fmtSingleQuotesO):
            self.mainConf.fmtSingleQuotes[0] = fmtSingleQuotesO
        else:
            self.theParent.makeAlert(
                "Invalid quote symbol: %s" % fmtSingleQuotesO, nwAlert.ERROR
            )
            validEntries = False

        if self._checkQuoteSymbol(fmtSingleQuotesC):
            self.mainConf.fmtSingleQuotes[1] = fmtSingleQuotesC
        else:
            self.theParent.makeAlert(
                "Invalid quote symbol: %s" % fmtSingleQuotesC, nwAlert.ERROR
            )
            validEntries = False

        if self._checkQuoteSymbol(fmtDoubleQuotesO):
            self.mainConf.fmtDoubleQuotes[0] = fmtDoubleQuotesO
        else:
            self.theParent.makeAlert(
                "Invalid quote symbol: %s" % fmtDoubleQuotesO, nwAlert.ERROR
            )
            validEntries = False

        if self._checkQuoteSymbol(fmtDoubleQuotesC):
            self.mainConf.fmtDoubleQuotes[1] = fmtDoubleQuotesC
        else:
            self.theParent.makeAlert(
                "Invalid quote symbol: %s" % fmtDoubleQuotesC, nwAlert.ERROR
            )
            validEntries = False

        self.mainConf.confChanged = True

        return validEntries, needsRestart

    ##
    #  Slots
    ##

    def _toggleAutoReplaceMain(self, theState):
        """Enables or disables switches controlled by the main auto
        replace switch.
        """
        self.autoReplaceSQ.setEnabled(theState)
        self.autoReplaceDQ.setEnabled(theState)
        self.autoReplaceDash.setEnabled(theState)
        self.autoReplaceDots.setEnabled(theState)
        return

    ##
    #  Internal Functions
    ##

    def _checkQuoteSymbol(self, toCheck):
        """Check that the quote symbols entered are in nwQuotes and is
        therefore a valid quote symbol for this app.
        """
        if len(toCheck) != 1:
            return False
        if toCheck in nwQuotes.SYMBOLS:
            return True
        return False

# END Class GuiConfigEditAutoReplaceTab
