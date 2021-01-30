# -*- coding: utf-8 -*-
"""novelWriter GUI Preferences

 novelWriter – GUI Preferences
===============================
 Class holding the preferences dialog

 File History:
 Created: 2019-06-10 [0.1.5]

 This file is a part of novelWriter
 Copyright 2018–2021, Veronica Berglyd Olsen

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

import nw
import logging
import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QDialog, QWidget, QComboBox, QSpinBox, QPushButton, QLineEdit, QMessageBox,
    QDialogButtonBox, QFileDialog, QFontDialog
)

from nw.gui.custom import QSwitch, QConfigLayout, PagedDialog, QuotesDialog
from nw.core import NWSpellSimple, NWSpellEnchant
from nw.constants import nwConst

logger = logging.getLogger(__name__)

class GuiPreferences(PagedDialog):

    def __init__(self, theParent, theProject):
        PagedDialog.__init__(self, theParent)

        logger.debug("Initialising GuiPreferences ...")
        self.setObjectName("GuiPreferences")

        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theProject = theProject

        self.setWindowTitle("Preferences")

        self.tabGeneral  = GuiConfigEditGeneralTab(self.theParent)
        self.tabProjects = GuiConfigEditProjectsTab(self.theParent)
        self.tabLayout   = GuiConfigEditLayoutTab(self.theParent)
        self.tabEditing  = GuiConfigEditEditingTab(self.theParent)
        self.tabAutoRep  = GuiConfigEditAutoReplaceTab(self.theParent)

        self.addTab(self.tabGeneral,  "General")
        self.addTab(self.tabProjects, "Projects")
        self.addTab(self.tabLayout,   "Text Layout")
        self.addTab(self.tabEditing,  "Editor")
        self.addTab(self.tabAutoRep,  "Auto-Replace")

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self._doSave)
        self.buttonBox.rejected.connect(self._doClose)
        self.addControls(self.buttonBox)

        logger.debug("GuiPreferences initialisation complete")

        return

    ##
    #  Buttons
    ##

    def _doSave(self):
        """Trigger all the save functions in the tabs, and collect the
        status of the saves.
        """
        logger.verbose("ConfigEditor save button clicked")

        validEntries = True
        needsRestart = False

        retA, retB = self.tabGeneral.saveValues()
        validEntries &= retA
        needsRestart |= retB

        retA, retB = self.tabProjects.saveValues()
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
                "Some changes will not be applied until novelWriter has been restarted."
            )

        if validEntries:
            self.accept()

        return

    def _doClose(self):
        """Close the preferences without saving the changes.
        """
        logger.verbose("ConfigEditor close button clicked")
        self.reject()
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
        self.selectTheme.setMinimumWidth(self.mainConf.pxInt(200))
        self.theThemes = self.theTheme.listThemes()
        for themeDir, themeName in self.theThemes:
            self.selectTheme.addItem(themeName, themeDir)
        themeIdx = self.selectTheme.findData(self.mainConf.guiTheme)
        if themeIdx != -1:
            self.selectTheme.setCurrentIndex(themeIdx)

        self.mainForm.addRow(
            "Main GUI theme",
            self.selectTheme,
            "Changing this requires restarting novelWriter."
        )

        ## Select Icon Theme
        self.selectIcons = QComboBox()
        self.selectIcons.setMinimumWidth(self.mainConf.pxInt(200))
        self.theIcons = self.theTheme.theIcons.listThemes()
        for iconDir, iconName in self.theIcons:
            self.selectIcons.addItem(iconName, iconDir)
        iconIdx = self.selectIcons.findData(self.mainConf.guiIcons)
        if iconIdx != -1:
            self.selectIcons.setCurrentIndex(iconIdx)

        self.mainForm.addRow(
            "Main icon theme",
            self.selectIcons,
            "Changing this requires restarting novelWriter."
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
        self.guiFont.setFixedWidth(self.mainConf.pxInt(162))
        self.guiFont.setText(self.mainConf.guiFont)
        self.fontButton = QPushButton("...")
        self.fontButton.setMaximumWidth(int(2.5*self.theTheme.getTextWidth("...")))
        self.fontButton.clicked.connect(self._selectFont)
        self.mainForm.addRow(
            "Font family",
            self.guiFont,
            "Changing this requires restarting novelWriter.",
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
            "Changing this requires restarting novelWriter.",
            theUnit = "pt"
        )

        # GUI Settings
        # ============
        self.mainForm.addGroupLabel("GUI Settings")

        self.showFullPath = QSwitch()
        self.showFullPath.setChecked(self.mainConf.showFullPath)
        self.mainForm.addRow(
            "Show full path in document header",
            self.showFullPath,
            "Add the parent folder names to the header."
        )

        self.hideVScroll = QSwitch()
        self.hideVScroll.setChecked(self.mainConf.hideVScroll)
        self.mainForm.addRow(
            "Hide vertical scroll bars in main windows",
            self.hideVScroll,
            "Scrolling available with mouse wheel and keys only."
        )

        self.hideHScroll = QSwitch()
        self.hideHScroll.setChecked(self.mainConf.hideHScroll)
        self.mainForm.addRow(
            "Hide horizontal scroll bars in main windows",
            self.hideHScroll,
            "Scrolling available with mouse wheel and keys only."
        )

        return

    def saveValues(self):
        """Save the values set for this tab.
        """
        validEntries = True
        needsRestart = False

        guiTheme     = self.selectTheme.currentData()
        guiIcons     = self.selectIcons.currentData()
        guiDark      = self.preferDarkIcons.isChecked()
        guiFont      = self.guiFont.text()
        guiFontSize  = self.guiFontSize.value()
        showFullPath = self.showFullPath.isChecked()
        hideVScroll  = self.hideVScroll.isChecked()
        hideHScroll  = self.hideHScroll.isChecked()

        # Check if restart is needed
        needsRestart |= self.mainConf.guiTheme != guiTheme
        needsRestart |= self.mainConf.guiIcons != guiIcons
        needsRestart |= self.mainConf.guiFont != guiFont
        needsRestart |= self.mainConf.guiFontSize != guiFontSize

        self.mainConf.guiTheme     = guiTheme
        self.mainConf.guiIcons     = guiIcons
        self.mainConf.guiDark      = guiDark
        self.mainConf.guiFont      = guiFont
        self.mainConf.guiFontSize  = guiFontSize
        self.mainConf.showFullPath = showFullPath
        self.mainConf.hideVScroll  = hideVScroll
        self.mainConf.hideHScroll  = hideHScroll

        self.mainConf.confChanged = True

        return validEntries, needsRestart

    ##
    #  Slots
    ##

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

class GuiConfigEditProjectsTab(QWidget):

    def __init__(self, theParent):
        QWidget.__init__(self, theParent)

        self.mainConf  = nw.CONFIG
        self.theParent = theParent
        self.theTheme  = theParent.theTheme

        # The Form
        self.mainForm = QConfigLayout()
        self.mainForm.setHelpTextStyle(self.theTheme.helpText)
        self.setLayout(self.mainForm)

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
            "Save document interval",
            self.autoSaveDoc,
            "How often the open document is automatically saved.",
            theUnit="seconds"
        )

        ## Project Save Timer
        self.autoSaveProj = QSpinBox(self)
        self.autoSaveProj.setMinimum(5)
        self.autoSaveProj.setMaximum(600)
        self.autoSaveProj.setSingleStep(1)
        self.autoSaveProj.setValue(self.mainConf.autoSaveProj)
        self.backupPathRow = self.mainForm.addRow(
            "Save project interval",
            self.autoSaveProj,
            "How often the open project is automatically saved.",
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
            "Run backup when the project is closed",
            self.backupOnClose,
            "Can be overridden for individual projects in project settings."
        )

        ## Ask before backup
        ## Only enabled when "Run when closing" is checked
        self.askBeforeBackup = QSwitch()
        self.askBeforeBackup.setChecked(self.mainConf.askBeforeBackup)
        self.askBeforeBackup.setEnabled(self.mainConf.backupOnClose)
        self.mainForm.addRow(
            "Ask before running backup",
            self.askBeforeBackup,
            "Disabling this will cause backups to run in the background."
        )

        return

    def saveValues(self):
        """Save the values set for this tab.
        """
        validEntries = True
        needsRestart = False

        autoSaveDoc     = self.autoSaveDoc.value()
        autoSaveProj    = self.autoSaveProj.value()
        backupPath      = self.backupPath
        backupOnClose   = self.backupOnClose.isChecked()
        askBeforeBackup = self.askBeforeBackup.isChecked()

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
        """Open a dialog to select the backup folder.
        """
        currDir = self.backupPath
        if not os.path.isdir(currDir):
            currDir = ""

        dlgOpt  = QFileDialog.Options()
        dlgOpt |= QFileDialog.ShowDirsOnly
        dlgOpt |= QFileDialog.DontUseNativeDialog
        newDir  = QFileDialog.getExistingDirectory(
            self, "Backup Directory", currDir, options=dlgOpt
        )
        if newDir:
            self.backupPath = newDir
            self.mainForm.setHelpText(self.backupPathRow, "Path: %s" % self.backupPath)
            return True

        return False

    def _toggledBackupOnClose(self, theState):
        """Enable or disable switch that depends on the backup on close
        switch.
        """
        self.askBeforeBackup.setEnabled(theState)
        return

# END Class GuiConfigEditProjectsTab

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
        self.mainForm.addGroupLabel("Document Text Style")

        ## Font Family
        self.textStyleFont = QLineEdit()
        self.textStyleFont.setReadOnly(True)
        self.textStyleFont.setFixedWidth(self.mainConf.pxInt(162))
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
            "Font size for the document editor and viewer.",
            theUnit = "pt"
        )

        # Text Flow
        # =========
        self.mainForm.addGroupLabel("Document Text Flow")

        ## Max Text Width in Normal Mode
        self.textFlowMax = QSpinBox(self)
        self.textFlowMax.setMinimum(300)
        self.textFlowMax.setMaximum(10000)
        self.textFlowMax.setSingleStep(10)
        self.textFlowMax.setValue(self.mainConf.textWidth)
        self.mainForm.addRow(
            "Maximum text width in \"Normal Mode\"",
            self.textFlowMax,
            "Horizontal margins are scaled automatically.",
            theUnit="px"
        )

        ## Max Text Width in Focus Mode
        self.focusDocWidth = QSpinBox(self)
        self.focusDocWidth.setMinimum(300)
        self.focusDocWidth.setMaximum(10000)
        self.focusDocWidth.setSingleStep(10)
        self.focusDocWidth.setValue(self.mainConf.focusWidth)
        self.mainForm.addRow(
            "Maximum text width in \"Focus Mode\"",
            self.focusDocWidth,
            "Horizontal margins are scaled automatically.",
            theUnit="px"
        )

        ## Document Fixed Width
        self.textFlowFixed = QSwitch()
        self.textFlowFixed.setChecked(not self.mainConf.textFixedW)
        self.mainForm.addRow(
            "Disable maximum text width in \"Normal Mode\"",
            self.textFlowFixed,
            "If disabled, minimum text width is defined by the margin."
        )

        ## Focus Mode Footer
        self.hideFocusFooter = QSwitch()
        self.hideFocusFooter.setChecked(self.mainConf.hideFocusFooter)
        self.mainForm.addRow(
            "Hide document footer in \"Focus Mode\"",
            self.hideFocusFooter,
            "Hide the information bar at the bottom of the document."
        )

        ## Justify Text
        self.textJustify = QSwitch()
        self.textJustify.setChecked(self.mainConf.doJustify)
        self.mainForm.addRow(
            "Justify the text margins in editor and viewer",
            self.textJustify,
            "Lay out text with straight edges in the editor and viewer."
        )

        ## Document Margins
        self.textMargin = QSpinBox(self)
        self.textMargin.setMinimum(0)
        self.textMargin.setMaximum(900)
        self.textMargin.setSingleStep(1)
        self.textMargin.setValue(self.mainConf.textMargin)
        self.mainForm.addRow(
            "Text margin",
            self.textMargin,
            "If maximum width is set, this becomes the minimum margin.",
            theUnit="px"
        )

        ## Tab Width
        self.tabWidth = QSpinBox(self)
        self.tabWidth.setMinimum(0)
        self.tabWidth.setMaximum(200)
        self.tabWidth.setSingleStep(1)
        self.tabWidth.setValue(self.mainConf.tabWidth)
        self.mainForm.addRow(
            "Tab width",
            self.tabWidth,
            "The width of a tab key press in the editor and viewer.",
            theUnit="px"
        )

        # Scroll Behaviour
        # ================
        self.mainForm.addGroupLabel("Scroll Behaviour")

        ## Scroll Past End
        self.scrollPastEnd = QSwitch()
        self.scrollPastEnd.setChecked(self.mainConf.scrollPastEnd)
        self.mainForm.addRow(
            "Scroll past end of the document",
            self.scrollPastEnd,
            "Allow scrolling until the last line is centred in the editor."
        )

        ## Typewriter Scrolling
        self.autoScroll = QSwitch()
        self.autoScroll.setChecked(self.mainConf.autoScroll)
        self.mainForm.addRow(
            "Typewriter style scrolling when you type",
            self.autoScroll,
            "Try to keep the cursor at a fixed vertical position."
        )

        ## Font Size
        self.autoScrollPos = QSpinBox(self)
        self.autoScrollPos.setMinimum(10)
        self.autoScrollPos.setMaximum(90)
        self.autoScrollPos.setSingleStep(1)
        self.autoScrollPos.setValue(int(self.mainConf.autoScrollPos))
        self.mainForm.addRow(
            "Minimum position for Typewriter scrolling",
            self.autoScrollPos,
            "In units of percentage of the editor height.",
            theUnit = "%"
        )

        return

    def saveValues(self):
        """Save the values set for this tab.
        """
        validEntries = True
        needsRestart = False

        textFont        = self.textStyleFont.text()
        textSize        = self.textStyleSize.value()
        textWidth       = self.textFlowMax.value()
        focusWidth      = self.focusDocWidth.value()
        textFixedW      = not self.textFlowFixed.isChecked()
        hideFocusFooter = self.hideFocusFooter.isChecked()
        doJustify       = self.textJustify.isChecked()
        textMargin      = self.textMargin.value()
        tabWidth        = self.tabWidth.value()
        scrollPastEnd   = self.scrollPastEnd.isChecked()
        autoScroll      = self.autoScroll.isChecked()
        autoScrollPos   = self.autoScrollPos.value()

        self.mainConf.textFont        = textFont
        self.mainConf.textSize        = textSize
        self.mainConf.textWidth       = textWidth
        self.mainConf.focusWidth      = focusWidth
        self.mainConf.textFixedW      = textFixedW
        self.mainConf.hideFocusFooter = hideFocusFooter
        self.mainConf.doJustify       = doJustify
        self.mainConf.textMargin      = textMargin
        self.mainConf.tabWidth        = tabWidth
        self.mainConf.scrollPastEnd   = scrollPastEnd
        self.mainConf.autoScroll      = autoScroll
        self.mainConf.autoScrollPos   = autoScrollPos

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
        self.selectSyntax.setMinimumWidth(self.mainConf.pxInt(200))
        self.theSyntaxes = self.theTheme.listSyntax()
        for syntaxFile, syntaxName in self.theSyntaxes:
            self.selectSyntax.addItem(syntaxName, syntaxFile)
        syntaxIdx = self.selectSyntax.findData(self.mainConf.guiSyntax)
        if syntaxIdx != -1:
            self.selectSyntax.setCurrentIndex(syntaxIdx)

        self.mainForm.addRow(
            "Highlight theme",
            self.selectSyntax,
            "Colour theme to apply to the editor and viewer."
        )

        self.highlightQuotes = QSwitch()
        self.highlightQuotes.setChecked(self.mainConf.highlightQuotes)
        self.mainForm.addRow(
            "Highlight text wrapped in quotes",
            self.highlightQuotes,
            "Applies to single, double and straight quotes."
        )

        self.highlightEmph = QSwitch()
        self.highlightEmph.setChecked(self.mainConf.highlightEmph)
        self.mainForm.addRow(
            "Add highlight colour to emphasised text",
            self.highlightEmph,
            "Applies to emphasis, strong and strikethrough."
        )

        # Spell Checking
        # ==============
        self.mainForm.addGroupLabel("Spell Checking")

        ## Spell Check Provider and Language
        self.spellLangList = QComboBox(self)
        self.spellToolList = QComboBox(self)
        self.spellToolList.addItem("Internal (difflib)",        nwConst.SP_INTERNAL)
        self.spellToolList.addItem("Spell Enchant (pyenchant)", nwConst.SP_ENCHANT)

        theModel  = self.spellToolList.model()
        idEnchant = self.spellToolList.findData(nwConst.SP_ENCHANT)
        theModel.item(idEnchant).setEnabled(self.mainConf.hasEnchant)

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
            self.spellLangList,
            "Available languages are determined by your system."
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
            "Full spell checking is disabled above this limit.",
            theUnit="kB"
        )

        # Writing Guides
        # ==============
        self.mainForm.addGroupLabel("Writing Guides")

        ## Show Tabs and Spaces
        self.showTabsNSpaces = QSwitch()
        self.showTabsNSpaces.setChecked(self.mainConf.showTabsNSpaces)
        self.mainForm.addRow(
            "Show tabs and spaces",
            self.showTabsNSpaces,
            "Add symbols to indicate tabs and spaces in the editor."
        )

        ## Show Line Endings
        self.showLineEndings = QSwitch()
        self.showLineEndings.setChecked(self.mainConf.showLineEndings)
        self.mainForm.addRow(
            "Show line endings",
            self.showLineEndings,
            "Add a symbol to indicate line endings in the editor."
        )

        return

    def saveValues(self):
        """Save the values set for this tab.
        """
        validEntries = True
        needsRestart = False

        guiSyntax       = self.selectSyntax.currentData()
        highlightQuotes = self.highlightQuotes.isChecked()
        highlightEmph   = self.highlightEmph.isChecked()
        spellTool       = self.spellToolList.currentData()
        spellLanguage   = self.spellLangList.currentData()
        bigDocLimit     = self.bigDocLimit.value()
        showTabsNSpaces = self.showTabsNSpaces.isChecked()
        showLineEndings = self.showLineEndings.isChecked()

        self.mainConf.guiSyntax       = guiSyntax
        self.mainConf.highlightQuotes = highlightQuotes
        self.mainConf.highlightEmph   = highlightEmph
        self.mainConf.spellTool       = spellTool
        self.mainConf.spellLanguage   = spellLanguage
        self.mainConf.bigDocLimit     = bigDocLimit
        self.mainConf.showTabsNSpaces = showTabsNSpaces
        self.mainConf.showLineEndings = showLineEndings

        self.mainConf.confChanged = True

        return validEntries, needsRestart

    ##
    #  Internal Functions
    ##

    def _doUpdateSpellTool(self, currIdx):
        """Update the list of dictionaries based on spell tool selected.
        """
        spellTool = self.spellToolList.currentData()
        self._updateLanguageList(spellTool)
        return

    def _updateLanguageList(self, spellTool):
        """Updates the list of available spell checking dictionaries
        available for the selected spell check tool. It will try to
        preserve the language choice, if the language exists in the
        updated list.
        """
        if spellTool == nwConst.SP_ENCHANT:
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
            "Allow the editor to replace symbols as you type."
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
            "Try to guess which is an opening or a closing single quote."
        )

        ## Auto-Replace Double Quotes
        self.autoReplaceDQ = QSwitch()
        self.autoReplaceDQ.setChecked(self.mainConf.doReplaceDQuote)
        self.autoReplaceDQ.setEnabled(self.mainConf.doReplace)
        self.mainForm.addRow(
            "Auto-replace double quotes",
            self.autoReplaceDQ,
            "Try to guess which is an opening or a closing double quote."
        )

        ## Auto-Replace Hyphens
        self.autoReplaceDash = QSwitch()
        self.autoReplaceDash.setChecked(self.mainConf.doReplaceDash)
        self.autoReplaceDash.setEnabled(self.mainConf.doReplace)
        self.mainForm.addRow(
            "Auto-replace dashes",
            self.autoReplaceDash,
            "Double and triple hyphens become short and long dashes."
        )

        ## Auto-Replace Dots
        self.autoReplaceDots = QSwitch()
        self.autoReplaceDots.setChecked(self.mainConf.doReplaceDots)
        self.autoReplaceDots.setEnabled(self.mainConf.doReplace)
        self.mainForm.addRow(
            "Auto-replace dots",
            self.autoReplaceDots,
            "Three consecutive dots becomes ellipsis."
        )

        # Quotation Style
        # ===============
        self.mainForm.addGroupLabel("Quotation Style")

        qWidth = self.mainConf.pxInt(40)
        bWidth = int(2.5*self.theTheme.getTextWidth("..."))
        self.quoteSym = {}

        ## Single Quote Style
        self.quoteSym["SO"] = QLineEdit()
        self.quoteSym["SO"].setMaxLength(1)
        self.quoteSym["SO"].setReadOnly(True)
        self.quoteSym["SO"].setFixedWidth(qWidth)
        self.quoteSym["SO"].setAlignment(Qt.AlignCenter)
        self.quoteSym["SO"].setText(self.mainConf.fmtSingleQuotes[0])
        self.btnSingleStyleO = QPushButton("...")
        self.btnSingleStyleO.setMaximumWidth(bWidth)
        self.btnSingleStyleO.clicked.connect(lambda: self._getQuote("SO"))
        self.mainForm.addRow(
            "Single quote open style",
            self.quoteSym["SO"],
            "The symbol to use for a leading single quote.",
            theButton=self.btnSingleStyleO
        )

        self.quoteSym["SC"] = QLineEdit()
        self.quoteSym["SC"].setMaxLength(1)
        self.quoteSym["SC"].setReadOnly(True)
        self.quoteSym["SC"].setFixedWidth(qWidth)
        self.quoteSym["SC"].setAlignment(Qt.AlignCenter)
        self.quoteSym["SC"].setText(self.mainConf.fmtSingleQuotes[1])
        self.btnSingleStyleC = QPushButton("...")
        self.btnSingleStyleC.setMaximumWidth(bWidth)
        self.btnSingleStyleC.clicked.connect(lambda: self._getQuote("SC"))
        self.mainForm.addRow(
            "Single quote close style",
            self.quoteSym["SC"],
            "The symbol to use for a trailing single quote.",
            theButton=self.btnSingleStyleC
        )

        ## Double Quote Style
        self.quoteSym["DO"] = QLineEdit()
        self.quoteSym["DO"].setMaxLength(1)
        self.quoteSym["DO"].setReadOnly(True)
        self.quoteSym["DO"].setFixedWidth(qWidth)
        self.quoteSym["DO"].setAlignment(Qt.AlignCenter)
        self.quoteSym["DO"].setText(self.mainConf.fmtDoubleQuotes[0])
        self.btnDoubleStyleO = QPushButton("...")
        self.btnDoubleStyleO.setMaximumWidth(bWidth)
        self.btnDoubleStyleO.clicked.connect(lambda: self._getQuote("DO"))
        self.mainForm.addRow(
            "Double quote open style",
            self.quoteSym["DO"],
            "The symbol to use for a leading double quote.",
            theButton=self.btnDoubleStyleO
        )

        self.quoteSym["DC"] = QLineEdit()
        self.quoteSym["DC"].setMaxLength(1)
        self.quoteSym["DC"].setReadOnly(True)
        self.quoteSym["DC"].setFixedWidth(qWidth)
        self.quoteSym["DC"].setAlignment(Qt.AlignCenter)
        self.quoteSym["DC"].setText(self.mainConf.fmtDoubleQuotes[1])
        self.btnDoubleStyleC = QPushButton("...")
        self.btnDoubleStyleC.setMaximumWidth(bWidth)
        self.btnDoubleStyleC.clicked.connect(lambda: self._getQuote("DC"))
        self.mainForm.addRow(
            "Double quote close style",
            self.quoteSym["DC"],
            "The symbol to use for a trailing double quote.",
            theButton=self.btnDoubleStyleC
        )

        return

    def saveValues(self):
        """Save the values set for this tab.
        """
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

        fmtSingleQuotesO = self.quoteSym["SO"].text()
        fmtSingleQuotesC = self.quoteSym["SC"].text()
        fmtDoubleQuotesO = self.quoteSym["DO"].text()
        fmtDoubleQuotesC = self.quoteSym["DC"].text()

        self.mainConf.fmtSingleQuotes[0] = fmtSingleQuotesO
        self.mainConf.fmtSingleQuotes[1] = fmtSingleQuotesC
        self.mainConf.fmtDoubleQuotes[0] = fmtDoubleQuotesO
        self.mainConf.fmtDoubleQuotes[1] = fmtDoubleQuotesC

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

    def _getQuote(self, qType):
        """Dialog for single quote open.
        """
        qtBox = QuotesDialog(self, currentQuote=self.quoteSym[qType].text())
        if qtBox.exec_() == QDialog.Accepted:
            self.quoteSym[qType].setText(qtBox.selectedQuote)
        return

# END Class GuiConfigEditAutoReplaceTab
