# -*- coding: utf-8 -*-
"""novelWriter GUI Config Editor

 novelWriter – GUI Config Editor
=================================
 Class holding the config dialog

 File History:
 Created: 2019-06-10 [0.1.5]

"""

import logging
import nw

from os import path

from PyQt5.QtCore    import Qt, QSize
from PyQt5.QtGui     import QIcon, QPixmap, QColor, QBrush, QStandardItemModel, QFont
from PyQt5.QtSvg     import QSvgWidget
from PyQt5.QtWidgets import (
    QDialog, QHBoxLayout, QVBoxLayout, QFormLayout, QLineEdit, QPlainTextEdit, QLabel,
    QWidget, QTabWidget, QDialogButtonBox, QSpinBox, QGroupBox, QComboBox, QMessageBox,
    QCheckBox, QGridLayout, QFontComboBox, QPushButton, QFileDialog
)
from nw.enum      import nwAlert
from nw.constants import nwQuotes

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

        self.gradPath = path.abspath(path.join(self.mainConf.graphPath,"gear.svg"))
        self.svgGradient = QSvgWidget(path.join(self.gradPath))
        self.svgGradient.setFixedSize(QSize(64,64))

        self.theProject.countStatus()
        self.tabMain   = GuiConfigEditGeneral(self.theParent)
        self.tabEditor = GuiConfigEditEditor(self.theParent)

        self.tabWidget = QTabWidget()
        self.tabWidget.addTab(self.tabMain,   "General")
        self.tabWidget.addTab(self.tabEditor, "Editor")

        self.setLayout(self.outerBox)
        self.outerBox.addWidget(self.svgGradient, 0, Qt.AlignTop)
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

        validEntries  = True
        needsRestart  = False

        retA, retB    = self.tabMain.saveValues()
        validEntries &= retA
        needsRestart |= retB

        retA, retB    = self.tabEditor.saveValues()
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

class GuiConfigEditGeneral(QWidget):

    def __init__(self, theParent):
        QWidget.__init__(self, theParent)

        self.mainConf  = nw.CONFIG
        self.theParent = theParent
        self.theTheme  = theParent.theTheme
        self.outerBox  = QGridLayout()

        # User Interface
        self.guiLook     = QGroupBox("User Interface", self)
        self.guiLookForm = QGridLayout(self)
        self.guiLook.setLayout(self.guiLookForm)

        self.guiLookTheme = QComboBox()
        self.guiLookTheme.setMinimumWidth(200)
        self.theThemes = self.theTheme.listThemes()
        for themeDir, themeName in self.theThemes:
            self.guiLookTheme.addItem(themeName, themeDir)
        themeIdx = self.guiLookTheme.findData(self.mainConf.guiTheme)
        if themeIdx != -1:
            self.guiLookTheme.setCurrentIndex(themeIdx)

        self.guiLookSyntax = QComboBox()
        self.guiLookSyntax.setMinimumWidth(200)
        self.theSyntaxes = self.theTheme.listSyntax()
        for syntaxFile, syntaxName in self.theSyntaxes:
            self.guiLookSyntax.addItem(syntaxName, syntaxFile)
        syntaxIdx = self.guiLookSyntax.findData(self.mainConf.guiSyntax)
        if syntaxIdx != -1:
            self.guiLookSyntax.setCurrentIndex(syntaxIdx)

        self.guiLookForm.addWidget(QLabel("Theme"),    0, 0)
        self.guiLookForm.addWidget(self.guiLookTheme,  0, 1)
        self.guiLookForm.addWidget(QLabel("Syntax"),   1, 0)
        self.guiLookForm.addWidget(self.guiLookSyntax, 1, 1)
        self.guiLookForm.setColumnStretch(2, 1)

        # Spell Checking
        self.spellLang     = QGroupBox("Spell Checker", self)
        self.spellLangForm = QGridLayout(self)
        self.spellLang.setLayout(self.spellLangForm)

        self.spellLangList = QComboBox(self)
        for spTag, spName in self.theParent.docEditor.theDict.listDictionaries():
            self.spellLangList.addItem(spName, spTag)
        spellIdx = self.spellLangList.findData(self.mainConf.spellLanguage)
        if spellIdx != -1:
            self.spellLangList.setCurrentIndex(spellIdx)

        self.spellLangForm.addWidget(QLabel("Language"), 0, 0)
        self.spellLangForm.addWidget(self.spellLangList, 0, 1)
        self.spellLangForm.setColumnStretch(2, 1)

        # AutoSave
        self.autoSave     = QGroupBox("Automatic Save", self)
        self.autoSaveForm = QGridLayout(self)
        self.autoSave.setLayout(self.autoSaveForm)

        self.autoSaveDoc = QSpinBox(self)
        self.autoSaveDoc.setMinimum(5)
        self.autoSaveDoc.setMaximum(600)
        self.autoSaveDoc.setSingleStep(1)
        self.autoSaveDoc.setValue(self.mainConf.autoSaveDoc)

        self.autoSaveProj = QSpinBox(self)
        self.autoSaveProj.setMinimum(5)
        self.autoSaveProj.setMaximum(600)
        self.autoSaveProj.setSingleStep(1)
        self.autoSaveProj.setValue(self.mainConf.autoSaveProj)

        self.autoSaveForm.addWidget(QLabel("Document"), 0, 0)
        self.autoSaveForm.addWidget(self.autoSaveDoc,   0, 1)
        self.autoSaveForm.addWidget(QLabel("seconds"),  0, 2)
        self.autoSaveForm.addWidget(QLabel("Project"),  1, 0)
        self.autoSaveForm.addWidget(self.autoSaveProj,  1, 1)
        self.autoSaveForm.addWidget(QLabel("seconds"),  1, 2)
        self.autoSaveForm.setColumnStretch(3, 1)

        # Backup
        self.projBackup     = QGroupBox("Backup Folder", self)
        self.projBackupForm = QGridLayout(self)
        self.projBackup.setLayout(self.projBackupForm)

        self.projBackupPath = QLineEdit()
        if path.isdir(self.mainConf.backupPath):
            self.projBackupPath.setText(self.mainConf.backupPath)

        self.projBackupGetPath = QPushButton(self.theTheme.getIcon("folder"),"")
        self.projBackupGetPath.clicked.connect(self._backupFolder)

        self.projBackupClose = QCheckBox("Run on close",self)
        self.projBackupClose.setToolTip("Backup automatically on project close.")
        if self.mainConf.backupOnClose:
            self.projBackupClose.setCheckState(Qt.Checked)
        else:
            self.projBackupClose.setCheckState(Qt.Unchecked)

        self.projBackupAsk = QCheckBox("Ask before backup",self)
        self.projBackupAsk.setToolTip("Ask before backup.")
        if self.mainConf.askBeforeBackup:
            self.projBackupAsk.setCheckState(Qt.Checked)
        else:
            self.projBackupAsk.setCheckState(Qt.Unchecked)

        self.projBackupForm.addWidget(self.projBackupPath,    0, 0, 1, 2)
        self.projBackupForm.addWidget(self.projBackupGetPath, 0, 2)
        self.projBackupForm.addWidget(self.projBackupClose,   1, 0)
        self.projBackupForm.addWidget(self.projBackupAsk,     1, 1, 1, 2)
        self.projBackupForm.setColumnStretch(1, 1)

        # Assemble
        self.outerBox.addWidget(self.guiLook,    0, 0)
        self.outerBox.addWidget(self.spellLang,  1, 0)
        self.outerBox.addWidget(self.autoSave,   2, 0)
        self.outerBox.addWidget(self.projBackup, 3, 0)
        self.outerBox.setColumnStretch(2, 1)
        self.outerBox.setRowStretch(4, 1)
        self.setLayout(self.outerBox)

        return

    def saveValues(self):

        validEntries = True
        needsRestart = False

        guiTheme        = self.guiLookTheme.currentData()
        guiSyntax       = self.guiLookSyntax.currentData()
        spellLanguage   = self.spellLangList.currentData()
        autoSaveDoc     = self.autoSaveDoc.value()
        autoSaveProj    = self.autoSaveProj.value()
        backupPath      = self.projBackupPath.text()
        backupOnClose   = self.projBackupClose.isChecked()
        askBeforeBackup = self.projBackupAsk.isChecked()

        # Check if restart is needed
        needsRestart |= self.mainConf.guiTheme != guiTheme

        self.mainConf.guiTheme        = guiTheme
        self.mainConf.guiSyntax       = guiSyntax
        self.mainConf.spellLanguage   = spellLanguage
        self.mainConf.autoSaveDoc     = autoSaveDoc
        self.mainConf.autoSaveProj    = autoSaveProj
        self.mainConf.backupPath      = backupPath
        self.mainConf.backupOnClose   = backupOnClose
        self.mainConf.askBeforeBackup = askBeforeBackup

        self.mainConf.confChanged = True

        return validEntries, needsRestart

    ##
    #  Internal Functions
    ##

    def _backupFolder(self):

        currDir = self.projBackupPath.text()
        if not path.isdir(currDir):
            currDir = ""

        dlgOpt  = QFileDialog.Options()
        dlgOpt |= QFileDialog.ShowDirsOnly
        dlgOpt |= QFileDialog.DontUseNativeDialog
        newDir = QFileDialog.getExistingDirectory(
            self,"Backup Directory",currDir,options=dlgOpt
        )
        if newDir:
            self.projBackupPath.setText(newDir)
            return True

        return False

# END Class GuiConfigEditGeneral

class GuiConfigEditEditor(QWidget):

    def __init__(self, theParent):
        QWidget.__init__(self, theParent)

        self.mainConf  = nw.CONFIG
        self.theParent = theParent
        self.outerBox  = QGridLayout()

        # Text Style
        self.textStyle     = QGroupBox("Text Style", self)
        self.textStyleForm = QGridLayout(self)
        self.textStyle.setLayout(self.textStyleForm)

        self.textStyleFont = QFontComboBox()
        self.textStyleFont.setMaximumWidth(250)
        self.textStyleFont.setCurrentFont(QFont(self.mainConf.textFont))

        self.textStyleSize = QSpinBox(self)
        self.textStyleSize.setMinimum(5)
        self.textStyleSize.setMaximum(120)
        self.textStyleSize.setSingleStep(1)
        self.textStyleSize.setValue(self.mainConf.textSize)

        self.textStyleForm.addWidget(QLabel("Font family"), 0, 0)
        self.textStyleForm.addWidget(self.textStyleFont,    0, 1)
        self.textStyleForm.addWidget(QLabel("Size"),        0, 2)
        self.textStyleForm.addWidget(self.textStyleSize,    0, 3)
        self.textStyleForm.setColumnStretch(4, 1)

        # Text Flow
        self.textFlow     = QGroupBox("Text Flow", self)
        self.textFlowForm = QGridLayout(self)
        self.textFlow.setLayout(self.textFlowForm)

        self.textFlowFixed = QCheckBox("Max text width",self)
        self.textFlowFixed.setToolTip("Maximum width of the text.")
        if self.mainConf.textFixedW:
            self.textFlowFixed.setCheckState(Qt.Checked)
        else:
            self.textFlowFixed.setCheckState(Qt.Unchecked)
        self.textFlowMax = QSpinBox(self)
        self.textFlowMax.setMinimum(300)
        self.textFlowMax.setMaximum(10000)
        self.textFlowMax.setSingleStep(10)
        self.textFlowMax.setValue(self.mainConf.textWidth)

        self.textFlowJustify = QCheckBox("Justify text",self)
        self.textFlowJustify.setToolTip("Justify text in main document editor.")
        if self.mainConf.doJustify:
            self.textFlowJustify.setCheckState(Qt.Checked)
        else:
            self.textFlowJustify.setCheckState(Qt.Unchecked)

        self.textFlowForm.addWidget(self.textFlowFixed,   0, 0)
        self.textFlowForm.addWidget(self.textFlowMax,     0, 1)
        self.textFlowForm.addWidget(QLabel("px"),         0, 2)
        self.textFlowForm.addWidget(self.textFlowJustify, 1, 0)
        self.textFlowForm.setColumnStretch(4, 1)

        # Text Margins
        self.textMargin     = QGroupBox("Margins", self)
        self.textMarginForm = QGridLayout(self)
        self.textMargin.setLayout(self.textMarginForm)

        self.textMarginDoc = QSpinBox(self)
        self.textMarginDoc.setMinimum(0)
        self.textMarginDoc.setMaximum(2000)
        self.textMarginDoc.setSingleStep(1)
        self.textMarginDoc.setValue(self.mainConf.textMargin)

        self.textMarginTab = QSpinBox(self)
        self.textMarginTab.setMinimum(0)
        self.textMarginTab.setMaximum(200)
        self.textMarginTab.setSingleStep(1)
        self.textMarginTab.setValue(self.mainConf.tabWidth)
        self.textMarginTab.setToolTip("Requires Qt 5.9 or later.")

        self.textMarginForm.addWidget(QLabel("Document"),   0, 0)
        self.textMarginForm.addWidget(self.textMarginDoc,   0, 1)
        self.textMarginForm.addWidget(QLabel("px"),         0, 2)
        self.textMarginForm.addWidget(QLabel("Tab width"),  2, 0)
        self.textMarginForm.addWidget(self.textMarginTab,   2, 1)
        self.textMarginForm.addWidget(QLabel("px"),         2, 2)
        self.textMarginForm.setColumnStretch(4, 1)

        # Automatic Features
        self.autoReplace     = QGroupBox("Automatic Features", self)
        self.autoReplaceForm = QGridLayout(self)
        self.autoReplace.setLayout(self.autoReplaceForm)

        self.autoSelect = QCheckBox(self)
        self.autoSelect.setToolTip("Auto-select word under cursor when applying formatting.")
        if self.mainConf.autoSelect:
            self.autoSelect.setCheckState(Qt.Checked)
        else:
            self.autoSelect.setCheckState(Qt.Unchecked)

        self.autoReplaceMain = QCheckBox(self)
        self.autoReplaceMain.setToolTip("Auto-replace text as you type.")
        if self.mainConf.doReplace:
            self.autoReplaceMain.setCheckState(Qt.Checked)
        else:
            self.autoReplaceMain.setCheckState(Qt.Unchecked)

        self.autoReplaceSQ = QCheckBox(self)
        self.autoReplaceSQ.setToolTip("Auto-replace single quotes.")
        if self.mainConf.doReplaceSQuote:
            self.autoReplaceSQ.setCheckState(Qt.Checked)
        else:
            self.autoReplaceSQ.setCheckState(Qt.Unchecked)

        self.autoReplaceDQ = QCheckBox(self)
        self.autoReplaceDQ.setToolTip("Auto-replace double quotes.")
        if self.mainConf.doReplaceDQuote:
            self.autoReplaceDQ.setCheckState(Qt.Checked)
        else:
            self.autoReplaceDQ.setCheckState(Qt.Unchecked)

        self.autoReplaceDash = QCheckBox(self)
        self.autoReplaceDash.setToolTip("Auto-replace double and triple hyphens with short and long dash.")
        if self.mainConf.doReplaceDash:
            self.autoReplaceDash.setCheckState(Qt.Checked)
        else:
            self.autoReplaceDash.setCheckState(Qt.Unchecked)

        self.autoReplaceDots = QCheckBox(self)
        self.autoReplaceDots.setToolTip("Auto-replace three dots with ellipsis.")
        if self.mainConf.doReplaceDots:
            self.autoReplaceDots.setCheckState(Qt.Checked)
        else:
            self.autoReplaceDots.setCheckState(Qt.Unchecked)

        self.autoReplaceForm.addWidget(QLabel("Auto-select text"),          0, 0)
        self.autoReplaceForm.addWidget(self.autoSelect,                     0, 1)
        self.autoReplaceForm.addWidget(QLabel("Auto-replace:"),             1, 0)
        self.autoReplaceForm.addWidget(self.autoReplaceMain,                1, 1)
        self.autoReplaceForm.addWidget(QLabel("\u2192 Single quotes"),      2, 0)
        self.autoReplaceForm.addWidget(self.autoReplaceSQ,                  2, 1)
        self.autoReplaceForm.addWidget(QLabel("\u2192 Double quotes"),      3, 0)
        self.autoReplaceForm.addWidget(self.autoReplaceDQ,                  3, 1)
        self.autoReplaceForm.addWidget(QLabel("\u2192 Hyphens with dash"),  4, 0)
        self.autoReplaceForm.addWidget(self.autoReplaceDash,                4, 1)
        self.autoReplaceForm.addWidget(QLabel("\u2192 Dots with ellipsis"), 5, 0)
        self.autoReplaceForm.addWidget(self.autoReplaceDots,                5, 1)
        self.autoReplaceForm.setColumnStretch(2, 1)
        self.autoReplaceForm.setRowStretch(6, 1)

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

        # Writing Guides
        self.showGuides     = QGroupBox("Writing Guides", self)
        self.showGuidesForm = QGridLayout(self)
        self.showGuides.setLayout(self.showGuidesForm)

        self.showTabsNSpaces = QCheckBox("Show tabs and spaces",self)
        if self.mainConf.showTabsNSpaces:
            self.showTabsNSpaces.setCheckState(Qt.Checked)
        else:
            self.showTabsNSpaces.setCheckState(Qt.Unchecked)

        self.showLineEndings = QCheckBox("Show line endings",self)
        if self.mainConf.showTabsNSpaces:
            self.showLineEndings.setCheckState(Qt.Checked)
        else:
            self.showLineEndings.setCheckState(Qt.Unchecked)

        self.showGuidesForm.addWidget(self.showTabsNSpaces, 0, 0)
        self.showGuidesForm.addWidget(self.showLineEndings, 1, 0)

        # Assemble
        self.outerBox.addWidget(self.textStyle,   0, 0, 1, 2)
        self.outerBox.addWidget(self.textFlow,    1, 0)
        self.outerBox.addWidget(self.textMargin,  1, 1)
        self.outerBox.addWidget(self.quoteStyle,  2, 0)
        self.outerBox.addWidget(self.autoReplace, 2, 1, 2, 1)
        self.outerBox.addWidget(self.showGuides,  3, 0)
        self.outerBox.setColumnStretch(2, 1)
        self.setLayout(self.outerBox)

        return

    def saveValues(self):

        validEntries = True

        textFont = self.textStyleFont.currentFont().family()
        textSize = self.textStyleSize.value()

        self.mainConf.textFont = textFont
        self.mainConf.textSize = textSize

        textWidth  = self.textFlowMax.value()
        textFixedW = self.textFlowFixed.isChecked()
        doJustify  = self.textFlowJustify.isChecked()

        self.mainConf.textWidth  = textWidth
        self.mainConf.textFixedW = textFixedW
        self.mainConf.doJustify  = doJustify

        textMargin = self.textMarginDoc.value()
        tabWidth   = self.textMarginTab.value()

        self.mainConf.textMargin = textMargin
        self.mainConf.tabWidth   = tabWidth

        autoSelect       = self.autoSelect.isChecked()
        doReplace        = self.autoReplaceMain.isChecked()
        doReplaceSQuote  = self.autoReplaceSQ.isChecked()
        doReplaceDQuote  = self.autoReplaceDQ.isChecked()
        doReplaceDash    = self.autoReplaceDash.isChecked()
        doReplaceDots    = self.autoReplaceDash.isChecked()

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
            self.theParent.makeAlert("Invalid quote symbol: %s" % fmtSingleQuotesO, nwAlert.ERROR)
            validEntries = False

        if self._checkQuoteSymbol(fmtSingleQuotesC):
            self.mainConf.fmtSingleQuotes[1] = fmtSingleQuotesC
        else:
            self.theParent.makeAlert("Invalid quote symbol: %s" % fmtSingleQuotesC, nwAlert.ERROR)
            validEntries = False

        if self._checkQuoteSymbol(fmtDoubleQuotesO):
            self.mainConf.fmtDoubleQuotes[0] = fmtDoubleQuotesO
        else:
            self.theParent.makeAlert("Invalid quote symbol: %s" % fmtDoubleQuotesO, nwAlert.ERROR)
            validEntries = False

        if self._checkQuoteSymbol(fmtDoubleQuotesC):
            self.mainConf.fmtDoubleQuotes[1] = fmtDoubleQuotesC
        else:
            self.theParent.makeAlert("Invalid quote symbol: %s" % fmtDoubleQuotesC, nwAlert.ERROR)
            validEntries = False

        showTabsNSpaces = self.showTabsNSpaces.isChecked()
        showLineEndings = self.showLineEndings.isChecked()

        self.mainConf.showTabsNSpaces = showTabsNSpaces
        self.mainConf.showLineEndings = showLineEndings

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
