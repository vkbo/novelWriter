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
 along with this program. If not, see https://www.gnu.org/licenses/.
"""

import logging
import nw

from os import path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QDialog, QHBoxLayout, QVBoxLayout, QLineEdit, QLabel, QWidget, QTabWidget,
    QDialogButtonBox, QSpinBox, QGroupBox, QComboBox, QMessageBox, QCheckBox,
    QGridLayout, QFontComboBox, QPushButton, QFileDialog, QFormLayout
)

from nw.additions import QSwitch, QConfigLayout
from nw.tools import NWSpellCheck, NWSpellSimple, NWSpellEnchant
from nw.constants import nwAlert, nwQuotes

logger = logging.getLogger(__name__)

class GuiConfigEditor(QDialog):

    def __init__(self, theParent, theProject):
        QDialog.__init__(self, theParent)

        logger.debug("Initialising ConfigEditor ...")

        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theProject = theProject
        self.outerBox   = QHBoxLayout()
        self.innerBox   = QVBoxLayout()

        self.setWindowTitle("Preferences")
        self.guiDeco = self.theParent.theTheme.loadDecoration("settings",(64,64))

        self.tabGeneral = GuiConfigEditGeneralTab(self.theParent)
        self.tabLayout  = GuiConfigEditLayoutTab(self.theParent)
        self.tabEditing = GuiConfigEditEditingTab(self.theParent)
        self.tabEditor  = GuiConfigEditEditor(self.theParent)

        self.tabWidget = QTabWidget()
        self.tabWidget.setMinimumWidth(600)
        self.tabWidget.addTab(self.tabGeneral, "General")
        self.tabWidget.addTab(self.tabLayout,  "Layout")
        self.tabWidget.addTab(self.tabEditing, "Editing")
        self.tabWidget.addTab(self.tabEditor, "Editor")

        self.setLayout(self.outerBox)
        self.outerBox.addWidget(self.guiDeco, 0, Qt.AlignTop)
        self.outerBox.addLayout(self.innerBox)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self._doSave)
        self.buttonBox.rejected.connect(self._doClose)

        self.innerBox.addWidget(self.tabWidget)
        self.innerBox.addWidget(self.buttonBox)

        self.show()

        logger.debug("ConfigEditor initialisation complete")

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

        retA, retB = self.tabEditor.saveValues()
        validEntries &= retA
        needsRestart |= retB

        if needsRestart:
            msgBox = QMessageBox()
            msgBox.information(
                self, "Preferences",
                "Some changes will not be applied until<br>%s has been restarted." % nw.__package__
            )

        if validEntries:
            self.accept()

        return

    def _doClose(self):
        logger.verbose("ConfigEditor close button clicked")
        self.close()
        return

# END Class GuiConfigEditor

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

        # GUI Settings
        # ============
        self.mainForm.addGroupLabel("GUI")

        ## Select Theme
        self.selectTheme = QComboBox()
        self.selectTheme.setMinimumWidth(200)
        self.theThemes = self.theTheme.listThemes()
        for themeDir, themeName in self.theThemes:
            self.selectTheme.addItem(themeName, themeDir)
        themeIdx = self.selectTheme.findData(self.mainConf.guiTheme)
        if themeIdx != -1:
            self.selectTheme.setCurrentIndex(themeIdx)

        self.mainForm.addRow("Colour theme", self.selectTheme)

        ## Syntax Highlighting
        self.selectSyntax = QComboBox()
        self.selectSyntax.setMinimumWidth(200)
        self.theSyntaxes = self.theTheme.listSyntax()
        for syntaxFile, syntaxName in self.theSyntaxes:
            self.selectSyntax.addItem(syntaxName, syntaxFile)
        syntaxIdx = self.selectSyntax.findData(self.mainConf.guiSyntax)
        if syntaxIdx != -1:
            self.selectSyntax.setCurrentIndex(syntaxIdx)

        self.mainForm.addRow("Syntax highlight theme", self.selectSyntax)

        ## Dark Icons
        self.preferDarkIcons = QSwitch()
        self.preferDarkIcons.setChecked(self.mainConf.guiDark)
        self.mainForm.addRow(
            "Prefer icons for dark backgrounds",
            self.preferDarkIcons,
            "May improve the look of icons on dark themes."
        )

        # AutoSave Settings
        # =================
        self.mainForm.addGroupLabel("Automatic Save")

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
        self.backupGetPath = QPushButton(self.theTheme.getIcon("folder"),"Select Folder")
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
        self.askBeforeBackup = QSwitch()
        self.askBeforeBackup.setChecked(self.mainConf.askBeforeBackup)
        self.mainForm.addRow(
            "Ask before running backup",
            self.askBeforeBackup
        )

        return

    def saveValues(self):

        validEntries = True
        needsRestart = False

        guiTheme        = self.selectTheme.currentData()
        guiSyntax       = self.selectSyntax.currentData()
        guiDark         = self.preferDarkIcons.isChecked()
        autoSaveDoc     = self.autoSaveDoc.value()
        autoSaveProj    = self.autoSaveProj.value()
        backupPath      = self.backupPath
        backupOnClose   = self.backupOnClose.isChecked()
        askBeforeBackup = self.askBeforeBackup.isChecked()

        # Check if restart is needed
        needsRestart |= self.mainConf.guiTheme != guiTheme

        self.mainConf.guiTheme        = guiTheme
        self.mainConf.guiSyntax       = guiSyntax
        self.mainConf.guiDark         = guiDark
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

        self.textStyleFont = QFontComboBox()
        self.textStyleFont.setMaximumWidth(200)
        self.textStyleFont.setCurrentFont(QFont(self.mainConf.textFont))
        self.mainForm.addRow(
            "Font family",
            self.textStyleFont,
            "For the document editor and viewer."
        )

        self.textStyleSize = QSpinBox(self)
        self.textStyleSize.setMinimum(5)
        self.textStyleSize.setMaximum(120)
        self.textStyleSize.setSingleStep(1)
        self.textStyleSize.setValue(self.mainConf.textSize)
        self.mainForm.addRow(
            "Font size",
            self.textStyleSize,
            theUnit="pt"
        )

        # Text Flow
        # =========
        self.mainForm.addGroupLabel("Text Flow")

        self.textFlowMax = QSpinBox(self)
        self.textFlowMax.setMinimum(300)
        self.textFlowMax.setMaximum(10000)
        self.textFlowMax.setSingleStep(10)
        self.textFlowMax.setValue(self.mainConf.textWidth)
        self.mainForm.addRow(
            "Maximum text width in Normal mode",
            self.textFlowMax,
            theUnit="px"
        )

        self.zenDocWidth = QSpinBox(self)
        self.zenDocWidth.setMinimum(300)
        self.zenDocWidth.setMaximum(10000)
        self.zenDocWidth.setSingleStep(10)
        self.zenDocWidth.setValue(self.mainConf.zenWidth)
        self.mainForm.addRow(
            "Maximum text width in Zen mode",
            self.zenDocWidth,
            theUnit="px"
        )

        self.textFlowFixed = QSwitch()
        self.textFlowFixed.setChecked(not self.mainConf.textFixedW)
        self.mainForm.addRow(
            "Disable maximum text width in Normal mode",
            self.textFlowFixed,
            "Only fixed margins are applied to the document."
        )

        self.textJustify = QSwitch()
        self.textJustify.setChecked(self.mainConf.textFixedW)
        self.mainForm.addRow(
            "Justify the text margins in editor and viewer",
            self.textJustify
        )

        self.textMargin = QSpinBox(self)
        self.textMargin.setMinimum(0)
        self.textMargin.setMaximum(900)
        self.textMargin.setSingleStep(1)
        self.textMargin.setValue(self.mainConf.textMargin)
        self.mainForm.addRow(
            "Document text margin",
            self.textMargin,
            "The minimum horizontal text margin if max with is enabled.",
            theUnit="px"
        )

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

        self.showTabsNSpaces = QSwitch()
        self.showTabsNSpaces.setChecked(self.mainConf.showTabsNSpaces)
        self.mainForm.addRow(
            "Show tabs and spaces",
            self.showTabsNSpaces
        )

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

        textFont        = self.textStyleFont.currentFont().family()
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
        self.mainForm.addGroupLabel("Spell Checking")

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

        self.bigDocLimit = QSpinBox(self)
        self.bigDocLimit.setMinimum(10)
        self.bigDocLimit.setMaximum(10000)
        self.bigDocLimit.setSingleStep(10)
        self.bigDocLimit.setValue(self.mainConf.bigDocLimit)
        self.mainForm.addRow(
            "Big document limit",
            self.bigDocLimit,
            "Disables full spell checking over the size limit.",
            theUnit="kb"
        )

        # Automatic Features
        # ==================
        self.mainForm.addGroupLabel("Automatic Features")

        self.autoSelect = QSwitch()
        self.autoSelect.setChecked(self.mainConf.autoSelect)
        self.mainForm.addRow(
            "Auto-select word under cursor",
            self.autoSelect,
            "Apply formatting to word under cursor if no selection is made."
        )

        self.autoReplaceMain = QSwitch()
        self.autoReplaceMain.setChecked(self.mainConf.doReplace)
        self.autoReplaceMain.toggled.connect(self._toggleAutoReplaceMain)
        self.mainForm.addRow(
            "Auto-replace text as you type",
            self.autoReplaceMain,
            "Apply formatting to word under cursor if no selection is made."
        )

        self.autoReplaceSQ = QSwitch()
        self.autoReplaceSQ.setChecked(self.mainConf.doReplaceSQuote)
        self.mainForm.addRow(
            "Auto-replace single quotes",
            self.autoReplaceSQ,
            "The feature will try to guess opening or closing symbol."
        )

        self.autoReplaceDQ = QSwitch()
        self.autoReplaceDQ.setChecked(self.mainConf.doReplaceDQuote)
        self.mainForm.addRow(
            "Auto-replace double quotes",
            self.autoReplaceDQ,
            "The feature will try to guess opening or closing symbol."
        )

        self.autoReplaceDash = QSwitch()
        self.autoReplaceDash.setChecked(self.mainConf.doReplaceDash)
        self.mainForm.addRow(
            "Auto-replace dashes",
            self.autoReplaceDash,
            "Auto-replace double and triple hyphens with short and long dash."
        )

        self.autoReplaceDots = QSwitch()
        self.autoReplaceDots.setChecked(self.mainConf.doReplaceDots)
        self.mainForm.addRow(
            "Auto-replace dots",
            self.autoReplaceDots,
            "Auto-replace three dots with ellipsis."
        )

        return

    def saveValues(self):

        validEntries = True
        needsRestart = False

        spellTool       = self.spellToolList.currentData()
        spellLanguage   = self.spellLangList.currentData()
        bigDocLimit     = self.bigDocLimit.value()
        autoSelect      = self.autoSelect.isChecked()
        doReplace       = self.autoReplaceMain.isChecked()
        doReplaceSQuote = self.autoReplaceSQ.isChecked()
        doReplaceDQuote = self.autoReplaceDQ.isChecked()
        doReplaceDash   = self.autoReplaceDash.isChecked()
        doReplaceDots   = self.autoReplaceDots.isChecked()

        self.mainConf.spellTool       = spellTool
        self.mainConf.spellLanguage   = spellLanguage
        self.mainConf.bigDocLimit     = bigDocLimit
        self.mainConf.autoSelect      = autoSelect
        self.mainConf.doReplace       = doReplace
        self.mainConf.doReplaceSQuote = doReplaceSQuote
        self.mainConf.doReplaceDQuote = doReplaceDQuote
        self.mainConf.doReplaceDash   = doReplaceDash
        self.mainConf.doReplaceDots   = doReplaceDots

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

class GuiConfigEditEditor(QWidget):

    def __init__(self, theParent):
        QWidget.__init__(self, theParent)

        self.mainConf  = nw.CONFIG
        self.theParent = theParent
        self.outerBox  = QGridLayout()

        # Quote Style
        self.quoteStyle     = QGroupBox("Quotation Style", self)
        self.quoteStyleForm = QGridLayout(self)
        self.quoteStyle.setLayout(self.quoteStyleForm)

        self.quoteSingleStyleO = QLineEdit()
        self.quoteSingleStyleO.setMaxLength(1)
        self.quoteSingleStyleO.setFixedWidth(30)
        self.quoteSingleStyleO.setAlignment(Qt.AlignCenter)
        self.quoteSingleStyleO.setText(self.mainConf.fmtSingleQuotes[0])

        self.quoteSingleStyleC = QLineEdit()
        self.quoteSingleStyleC.setMaxLength(1)
        self.quoteSingleStyleC.setFixedWidth(30)
        self.quoteSingleStyleC.setAlignment(Qt.AlignCenter)
        self.quoteSingleStyleC.setText(self.mainConf.fmtSingleQuotes[1])

        self.quoteDoubleStyleO = QLineEdit()
        self.quoteDoubleStyleO.setMaxLength(1)
        self.quoteDoubleStyleO.setFixedWidth(30)
        self.quoteDoubleStyleO.setAlignment(Qt.AlignCenter)
        self.quoteDoubleStyleO.setText(self.mainConf.fmtDoubleQuotes[0])

        self.quoteDoubleStyleC = QLineEdit()
        self.quoteDoubleStyleC.setMaxLength(1)
        self.quoteDoubleStyleC.setFixedWidth(30)
        self.quoteDoubleStyleC.setAlignment(Qt.AlignCenter)
        self.quoteDoubleStyleC.setText(self.mainConf.fmtDoubleQuotes[1])

        self.quoteStyleForm.addWidget(QLabel("Single Quotes"), 0, 0, 1, 3)
        self.quoteStyleForm.addWidget(QLabel("Open"),          1, 0)
        self.quoteStyleForm.addWidget(self.quoteSingleStyleO,  1, 1)
        self.quoteStyleForm.addWidget(QLabel("Close"),         1, 2)
        self.quoteStyleForm.addWidget(self.quoteSingleStyleC,  1, 3)
        self.quoteStyleForm.addWidget(QLabel("Double Quotes"), 2, 0, 1, 3)
        self.quoteStyleForm.addWidget(QLabel("Open"),          3, 0)
        self.quoteStyleForm.addWidget(self.quoteDoubleStyleO,  3, 1)
        self.quoteStyleForm.addWidget(QLabel("Close"),         3, 2)
        self.quoteStyleForm.addWidget(self.quoteDoubleStyleC,  3, 3)
        self.quoteStyleForm.setColumnStretch(4, 1)
        self.quoteStyleForm.setRowStretch(4, 1)

        # Assemble
        self.outerBox.addWidget(self.quoteStyle,  2, 1, 2, 1)
        self.outerBox.setColumnStretch(2, 1)
        self.outerBox.setRowStretch(5, 1)
        self.setLayout(self.outerBox)

        return

    def saveValues(self):

        validEntries = True

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

        return validEntries, False

    ##
    #  Internal Functions
    ##

    def _checkQuoteSymbol(self, toCheck):
        if len(toCheck) != 1:
            return False
        if toCheck in nwQuotes.SYMBOLS:
            return True
        return False

# END Class GuiConfigEditEditor
