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

        needsRestart  = False
        needsRestart |= self.tabMain.saveValues()
        needsRestart |= self.tabEditor.saveValues()

        if needsRestart:
            msgBox = QMessageBox()
            msgBox.information(
                self, "Preferences",
                "Some changes will not be applied until<br>%s has been restarted." % nw.__package__
            )

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
        self.outerBox   = QVBoxLayout()

        # User Interface
        self.guiLook     = QGroupBox("User Interface", self)
        self.guiLookForm = QFormLayout(self)
        self.guiLook.setLayout(self.guiLookForm)

        self.theThemes = self.theParent.theTheme.listThemes()
        self.guiLookTheme = QComboBox()
        for themeDir, themeName in self.theThemes:
            self.guiLookTheme.addItem(themeName, themeDir)
        themeIdx = self.guiLookTheme.findData(self.mainConf.guiTheme)
        if themeIdx != -1:
            self.guiLookTheme.setCurrentIndex(themeIdx)
        self.guiLookForm.addRow("Theme", self.guiLookTheme)

        # AutoSave
        self.autoSave     = QGroupBox("Auto-Save", self)
        self.autoSaveForm = QFormLayout(self)
        self.autoSave.setLayout(self.autoSaveForm)

        self.autoSaveDoc = QSpinBox(self)
        self.autoSaveDoc.setMinimum(5)
        self.autoSaveDoc.setMaximum(600)
        self.autoSaveDoc.setSingleStep(1)
        self.autoSaveDoc.setValue(self.mainConf.autoSaveDoc)
        self.autoSaveForm.addRow("Save Document (seconds)", self.autoSaveDoc)

        self.autoSaveProj = QSpinBox(self)
        self.autoSaveProj.setMinimum(5)
        self.autoSaveProj.setMaximum(600)
        self.autoSaveProj.setSingleStep(1)
        self.autoSaveProj.setValue(self.mainConf.autoSaveProj)
        self.autoSaveForm.addRow("Save Project (seconds)", self.autoSaveProj)

        self.outerBox.addWidget(self.guiLook)
        self.outerBox.addWidget(self.autoSave)
        self.outerBox.addStretch(1)
        self.setLayout(self.outerBox)

        return

    def saveValues(self):

        autoSaveDoc  = self.autoSaveDoc.value()
        autoSaveProj = self.autoSaveProj.value()
        guiTheme     = self.guiLookTheme.currentData()

        # Check if restart is needed
        needsRestart = False
        needsRestart |= self.mainConf.guiTheme != guiTheme

        self.mainConf.autoSaveDoc  = autoSaveDoc
        self.mainConf.autoSaveProj = autoSaveProj
        self.mainConf.guiTheme     = guiTheme
        self.mainConf.confChanged  = True

        return needsRestart

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
        self.textStyleFont.setMaximumWidth(300)
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
        self.textFlowForm.addWidget(QLabel("pixles"),           0, 3)
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
        self.textMarginForm.addWidget(QLabel("pixles"),     0, 2)
        self.textMarginForm.addWidget(QLabel("Vertical"),   1, 0)
        self.textMarginForm.addWidget(self.textMarginVer,   1, 1)
        self.textMarginForm.addWidget(QLabel("pixles"),     1, 2)
        self.textMarginForm.addWidget(QLabel("Tab Width"),  2, 0)
        self.textMarginForm.addWidget(self.textMarginTab,   2, 1)
        self.textMarginForm.addWidget(QLabel("pixles"),     2, 2)
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

        self.autoReplaceSStyle = QComboBox()
        for n, qTup in enumerate(nwQuotes.SINGLE):
            qA, qB, qStr = qTup
            self.autoReplaceSStyle.addItem("%s: %stext%s" % (qStr, qA, qB), n)
        singleIdx = self.autoReplaceSStyle.findData(self.mainConf.styleSQuote)
        if singleIdx != -1:
            self.autoReplaceSStyle.setCurrentIndex(singleIdx)

        self.autoReplaceDQ = QCheckBox(self)
        self.autoReplaceDQ.setToolTip("Auto-replace double quotes.")
        if self.mainConf.doReplaceDQuote:
            self.autoReplaceDQ.setCheckState(Qt.Checked)
        else:
            self.autoReplaceDQ.setCheckState(Qt.Unchecked)

        self.autoReplaceDStyle = QComboBox()
        for n, qTup in enumerate(nwQuotes.DOUBLE):
            qA, qB, qStr = qTup
            self.autoReplaceDStyle.addItem("%s: %stext%s" % (qStr, qA, qB), n)
        doubleIdx = self.autoReplaceDStyle.findData(self.mainConf.styleSQuote)
        if doubleIdx != -1:
            self.autoReplaceDStyle.setCurrentIndex(doubleIdx)

        self.autoReplaceForm.addWidget(QLabel("Enable Feature"), 0, 0)
        self.autoReplaceForm.addWidget(self.autoReplaceMain,     0, 1)
        self.autoReplaceForm.addWidget(QLabel("Single Quotes"),  1, 0)
        self.autoReplaceForm.addWidget(self.autoReplaceSQ,       1, 1)
        self.autoReplaceForm.addWidget(QLabel("Style"),          1, 2)
        self.autoReplaceForm.addWidget(self.autoReplaceSStyle,   1, 3)
        self.autoReplaceForm.addWidget(QLabel("Double Quotes"),  2, 0)
        self.autoReplaceForm.addWidget(self.autoReplaceDQ,       2, 1)
        self.autoReplaceForm.addWidget(QLabel("Style"),          2, 2)
        self.autoReplaceForm.addWidget(self.autoReplaceDStyle,   2, 3)
        self.autoReplaceForm.setColumnStretch(4, 1)

        # Assemble
        self.outerBox.addWidget(self.textStyle,   0, 0, 1, 2)
        self.outerBox.addWidget(self.textFlow,    1, 0)
        self.outerBox.addWidget(self.textMargin,  1, 1)
        self.outerBox.addWidget(self.autoReplace, 2, 0, 1, 2)
        self.outerBox.setColumnStretch(2, 1)
        self.setLayout(self.outerBox)

        return

    def saveValues(self):

        textFont = self.textStyleFont.currentFont().family()
        textSize = self.textStyleSize.value()

        self.mainConf.textFont = textFont
        self.mainConf.textSize = textSize

        textWidth  = self.textFlowWidth.value()
        textFixedW = self.textFlowFixed.isChecked()
        doJustify  = self.textFlowJustify.isChecked()
        autoSelect = self.testFlowAutoSelect.isChecked()

        self.mainConf.textWidth   = textWidth
        self.mainConf.textFixedW  = textFixedW
        self.mainConf.doJustify   = doJustify
        self.mainConf.autoSelect  = autoSelect

        textMarginH = self.textMarginHor.value()
        textMarginV = self.textMarginVer.value()
        tabWidth    = self.textMarginTab.value()

        self.mainConf.textMargin[0] = textMarginH
        self.mainConf.textMargin[1] = textMarginV
        self.mainConf.tabWidth      = tabWidth

        doReplace       = self.autoReplaceMain.isChecked()
        doReplaceSQuote = self.autoReplaceSQ.isChecked()
        doReplaceDQuote = self.autoReplaceDQ.isChecked()
        styleSQuote     = self.autoReplaceSStyle.currentData()
        styleDQuote     = self.autoReplaceDStyle.currentData()

        self.mainConf.doReplace       = doReplace
        self.mainConf.doReplaceSQuote = doReplaceSQuote
        self.mainConf.doReplaceDQuote = doReplaceDQuote
        self.mainConf.setSingleQuotes(styleSQuote)
        self.mainConf.setDoubleQuotes(styleDQuote)

        self.mainConf.confChanged = True

        return False

# END Class GuiConfigEditEditor
