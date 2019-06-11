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

from PyQt5.QtCore    import Qt
from PyQt5.QtGui     import QIcon, QPixmap, QColor, QBrush, QStandardItemModel, QFont
from PyQt5.QtSvg     import QSvgWidget
from PyQt5.QtWidgets import (
    QDialog, QHBoxLayout, QVBoxLayout, QFormLayout, QLineEdit, QPlainTextEdit, QLabel,
    QWidget, QTabWidget, QDialogButtonBox, QSpinBox, QGroupBox, QComboBox, QMessageBox,
    QCheckBox, QGridLayout, QFontComboBox
)
from nw.enum import nwAlert

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

        self.gradPath = path.abspath(path.join(self.mainConf.appPath,"graphics","block.svg"))
        self.svgGradient = QSvgWidget(self.gradPath)
        self.svgGradient.setFixedWidth(80)

        self.theProject.countStatus()
        self.tabMain   = GuiConfigEditGeneral(self.theParent)
        self.tabEditor = GuiConfigEditEditor(self.theParent)

        self.tabWidget = QTabWidget()
        self.tabWidget.addTab(self.tabMain, "General")
        self.tabWidget.addTab(self.tabEditor, "Editor")

        self.setLayout(self.outerBox)
        self.outerBox.addWidget(self.svgGradient)
        self.outerBox.addLayout(self.innerBox)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self._doSave)
        self.buttonBox.rejected.connect(self._doClose)

        self.innerBox.addWidget(self.tabWidget)
        self.innerBox.addWidget(self.buttonBox)

        self.show()

        logger.debug("ProjectEditor ConfigEditor complete")

        return

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

        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.outerBox   = QGridLayout()

        # User Interface
        self.guiLook     = QGroupBox("User Interface", self)
        self.guiLookForm = QGridLayout(self)
        self.guiLook.setLayout(self.guiLookForm)

        self.guiLookTheme = QComboBox()
        self.guiLookTheme.setMinimumWidth(200)
        self.theThemes = self.theParent.theTheme.listThemes()
        for themeDir, themeName in self.theThemes:
            self.guiLookTheme.addItem(themeName, themeDir)
        themeIdx = self.guiLookTheme.findData(self.mainConf.guiTheme)
        if themeIdx != -1:
            self.guiLookTheme.setCurrentIndex(themeIdx)

        self.guiLookForm.addWidget(QLabel("Theme"),   0, 0)
        self.guiLookForm.addWidget(self.guiLookTheme, 0, 1)

        # AutoSave
        self.autoSave     = QGroupBox("Auto-Save", self)
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

        self.outerBox.addWidget(self.guiLook,  0, 0)
        self.outerBox.addWidget(self.autoSave, 1, 0)
        self.outerBox.setColumnStretch(2, 1)
        self.outerBox.setRowStretch(2, 1)
        self.setLayout(self.outerBox)

        return

    def saveValues(self):

        validEntries = True
        needsRestart = False

        autoSaveDoc  = self.autoSaveDoc.value()
        autoSaveProj = self.autoSaveProj.value()
        guiTheme     = self.guiLookTheme.currentData()

        # Check if restart is needed
        needsRestart |= self.mainConf.guiTheme != guiTheme

        self.mainConf.autoSaveDoc  = autoSaveDoc
        self.mainConf.autoSaveProj = autoSaveProj
        self.mainConf.guiTheme     = guiTheme
        self.mainConf.confChanged  = True

        return validEntries, needsRestart

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

        self.textStyleForm.addWidget(QLabel("Font Family"), 0, 0)
        self.textStyleForm.addWidget(self.textStyleFont,    0, 1)
        self.textStyleForm.addWidget(QLabel("Size"),        0, 2)
        self.textStyleForm.addWidget(self.textStyleSize,    0, 3)
        self.textStyleForm.setColumnStretch(4, 1)

        # Text Flow
        self.textFlow     = QGroupBox("Text Flow", self)
        self.textFlowForm = QGridLayout(self)
        self.textFlow.setLayout(self.textFlowForm)

        self.textFlowFixed = QCheckBox(self)
        self.textFlowFixed.setToolTip("Make text in editor fixed width and scale margins instead.")
        if self.mainConf.textFixedW:
            self.textFlowFixed.setCheckState(Qt.Checked)
        else:
            self.textFlowFixed.setCheckState(Qt.Unchecked)
        self.textFlowWidth = QSpinBox(self)
        self.textFlowWidth.setMinimum(300)
        self.textFlowWidth.setMaximum(10000)
        self.textFlowWidth.setSingleStep(10)
        self.textFlowWidth.setValue(self.mainConf.textWidth)

        self.textFlowJustify = QCheckBox(self)
        self.textFlowJustify.setToolTip("Justify text in main document editor.")
        if self.mainConf.doJustify:
            self.textFlowJustify.setCheckState(Qt.Checked)
        else:
            self.textFlowJustify.setCheckState(Qt.Unchecked)

        self.testFlowAutoSelect = QCheckBox(self)
        self.testFlowAutoSelect.setToolTip("Auto-select word under cursor when applying formatting.")
        if self.mainConf.autoSelect:
            self.testFlowAutoSelect.setCheckState(Qt.Checked)
        else:
            self.testFlowAutoSelect.setCheckState(Qt.Unchecked)

        self.textFlowForm.addWidget(QLabel("Fixed Width"),      0, 0)
        self.textFlowForm.addWidget(self.textFlowFixed,         0, 1)
        self.textFlowForm.addWidget(self.textFlowWidth,         0, 2)
        self.textFlowForm.addWidget(QLabel("px"),               0, 3)
        self.textFlowForm.addWidget(QLabel("Justify Text"),     1, 0)
        self.textFlowForm.addWidget(self.textFlowJustify,       1, 1)
        self.textFlowForm.addWidget(QLabel("Auto-Select Text"), 2, 0)
        self.textFlowForm.addWidget(self.testFlowAutoSelect,    2, 1)
        self.textFlowForm.setColumnStretch(4, 1)

        # Text Margins
        self.textMargin     = QGroupBox("Margins", self)
        self.textMarginForm = QGridLayout(self)
        self.textMargin.setLayout(self.textMarginForm)

        self.textMarginHor = QSpinBox(self)
        self.textMarginHor.setMinimum(0)
        self.textMarginHor.setMaximum(2000)
        self.textMarginHor.setSingleStep(1)
        self.textMarginHor.setValue(self.mainConf.textMargin[0])

        self.textMarginVer = QSpinBox(self)
        self.textMarginVer.setMinimum(0)
        self.textMarginVer.setMaximum(2000)
        self.textMarginVer.setSingleStep(1)
        self.textMarginVer.setValue(self.mainConf.textMargin[1])

        self.textMarginTab = QSpinBox(self)
        self.textMarginTab.setMinimum(0)
        self.textMarginTab.setMaximum(200)
        self.textMarginTab.setSingleStep(1)
        self.textMarginTab.setValue(self.mainConf.tabWidth)

        self.textMarginForm.addWidget(QLabel("Horizontal"), 0, 0)
        self.textMarginForm.addWidget(self.textMarginHor,   0, 1)
        self.textMarginForm.addWidget(QLabel("px"),         0, 2)
        self.textMarginForm.addWidget(QLabel("Vertical"),   1, 0)
        self.textMarginForm.addWidget(self.textMarginVer,   1, 1)
        self.textMarginForm.addWidget(QLabel("px"),         1, 2)
        self.textMarginForm.addWidget(QLabel("Tab Width"),  2, 0)
        self.textMarginForm.addWidget(self.textMarginTab,   2, 1)
        self.textMarginForm.addWidget(QLabel("px"),         2, 2)
        self.textMarginForm.setColumnStretch(4, 1)

        # Auto-Replace
        self.autoReplace     = QGroupBox("Auto-Replace", self)
        self.autoReplaceForm = QGridLayout(self)
        self.autoReplace.setLayout(self.autoReplaceForm)

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

        self.autoReplaceSStyleO = QLineEdit()
        self.autoReplaceSStyleO.setMaxLength(1)
        self.autoReplaceSStyleO.setFixedWidth(30)
        self.autoReplaceSStyleO.setAlignment(Qt.AlignCenter)
        self.autoReplaceSStyleO.setText(self.mainConf.fmtSingleQuotes[0])

        self.autoReplaceSStyleC = QLineEdit()
        self.autoReplaceSStyleC.setMaxLength(1)
        self.autoReplaceSStyleC.setFixedWidth(30)
        self.autoReplaceSStyleC.setAlignment(Qt.AlignCenter)
        self.autoReplaceSStyleC.setText(self.mainConf.fmtSingleQuotes[1])

        self.autoReplaceDQ = QCheckBox(self)
        self.autoReplaceDQ.setToolTip("Auto-replace double quotes.")
        if self.mainConf.doReplaceDQuote:
            self.autoReplaceDQ.setCheckState(Qt.Checked)
        else:
            self.autoReplaceDQ.setCheckState(Qt.Unchecked)

        self.autoReplaceDStyleO = QLineEdit()
        self.autoReplaceDStyleO.setMaxLength(1)
        self.autoReplaceDStyleO.setFixedWidth(30)
        self.autoReplaceDStyleO.setAlignment(Qt.AlignCenter)
        self.autoReplaceDStyleO.setText(self.mainConf.fmtDoubleQuotes[0])

        self.autoReplaceDStyleC = QLineEdit()
        self.autoReplaceDStyleC.setMaxLength(1)
        self.autoReplaceDStyleC.setFixedWidth(30)
        self.autoReplaceDStyleC.setAlignment(Qt.AlignCenter)
        self.autoReplaceDStyleC.setText(self.mainConf.fmtDoubleQuotes[1])

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

        self.autoReplaceForm.addWidget(QLabel("Enable Feature"),     0, 0)
        self.autoReplaceForm.addWidget(self.autoReplaceMain,         0, 1)
        self.autoReplaceForm.addWidget(QLabel("Single Quotes"),      1, 0)
        self.autoReplaceForm.addWidget(self.autoReplaceSQ,           1, 1)
        self.autoReplaceForm.addWidget(QLabel("Open"),               1, 2)
        self.autoReplaceForm.addWidget(self.autoReplaceSStyleO,      1, 3)
        self.autoReplaceForm.addWidget(QLabel("Close"),              1, 4)
        self.autoReplaceForm.addWidget(self.autoReplaceSStyleC,      1, 5)
        self.autoReplaceForm.addWidget(QLabel("Double Quotes"),      2, 0)
        self.autoReplaceForm.addWidget(self.autoReplaceDQ,           2, 1)
        self.autoReplaceForm.addWidget(QLabel("Open"),               2, 2)
        self.autoReplaceForm.addWidget(self.autoReplaceDStyleO,      2, 3)
        self.autoReplaceForm.addWidget(QLabel("Close"),              2, 4)
        self.autoReplaceForm.addWidget(self.autoReplaceDStyleC,      2, 5)
        self.autoReplaceForm.addWidget(QLabel("Hyphens with Dash"),  3, 0)
        self.autoReplaceForm.addWidget(self.autoReplaceDash,         3, 1)
        self.autoReplaceForm.addWidget(QLabel("Dots with Ellipsis"), 4, 0)
        self.autoReplaceForm.addWidget(self.autoReplaceDots,         4, 1)
        self.autoReplaceForm.setColumnStretch(6, 1)

        # Assemble
        self.outerBox.addWidget(self.textStyle,   0, 0, 1, 2)
        self.outerBox.addWidget(self.textFlow,    1, 0)
        self.outerBox.addWidget(self.textMargin,  1, 1)
        self.outerBox.addWidget(self.autoReplace, 2, 0, 1, 2)
        self.outerBox.setColumnStretch(2, 1)
        self.setLayout(self.outerBox)

        return

    def saveValues(self):

        validEntries = True

        textFont = self.textStyleFont.currentFont().family()
        textSize = self.textStyleSize.value()

        self.mainConf.textFont = textFont
        self.mainConf.textSize = textSize

        textWidth  = self.textFlowWidth.value()
        textFixedW = self.textFlowFixed.isChecked()
        doJustify  = self.textFlowJustify.isChecked()
        autoSelect = self.testFlowAutoSelect.isChecked()

        self.mainConf.textWidth  = textWidth
        self.mainConf.textFixedW = textFixedW
        self.mainConf.doJustify  = doJustify
        self.mainConf.autoSelect = autoSelect

        textMarginH = self.textMarginHor.value()
        textMarginV = self.textMarginVer.value()
        tabWidth    = self.textMarginTab.value()

        self.mainConf.textMargin[0] = textMarginH
        self.mainConf.textMargin[1] = textMarginV
        self.mainConf.tabWidth      = tabWidth

        doReplace        = self.autoReplaceMain.isChecked()
        doReplaceSQuote  = self.autoReplaceSQ.isChecked()
        doReplaceDQuote  = self.autoReplaceDQ.isChecked()
        doReplaceDash    = self.autoReplaceDash.isChecked()
        doReplaceDots    = self.autoReplaceDash.isChecked()
        fmtSingleQuotesO = self.autoReplaceSStyleO.text()
        fmtSingleQuotesC = self.autoReplaceSStyleC.text()
        fmtDoubleQuotesO = self.autoReplaceDStyleO.text()
        fmtDoubleQuotesC = self.autoReplaceDStyleC.text()

        self.mainConf.doReplace       = doReplace
        self.mainConf.doReplaceSQuote = doReplaceSQuote
        self.mainConf.doReplaceDQuote = doReplaceDQuote
        self.mainConf.doReplaceDash   = doReplaceDash
        self.mainConf.doReplaceDots   = doReplaceDots

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

        self.mainConf.confChanged = True

        return validEntries, False

    ##
    #  Internal Functions
    ##

    def _checkQuoteSymbol(self, toCheck):
        validOnes = [
            "\"","'",
            "“","”","„",
            "‘","’","‚",
            "«","»","‹","›",
            "『","』","「","」",
            "《","》","〈","〉"
        ]
        if len(toCheck) != 1:
            return False
        if toCheck in validOnes:
            return True
        return False

# END Class GuiConfigEditEditor
