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
from PyQt5.QtGui     import QIcon, QPixmap, QColor, QBrush, QStandardItemModel
from PyQt5.QtSvg     import QSvgWidget
from PyQt5.QtWidgets import (
    QDialog, QHBoxLayout, QVBoxLayout, QFormLayout, QLineEdit, QPlainTextEdit, QLabel,
    QWidget, QTabWidget, QDialogButtonBox, QSpinBox, QGroupBox, QComboBox, QMessageBox
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
        self.tabMain = GuiConfigEditGeneral(self.theParent, self.theProject)

        self.tabWidget = QTabWidget()
        self.tabWidget.addTab(self.tabMain, "General")

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

    def __init__(self, theParent, theProject):
        QWidget.__init__(self, theParent)

        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theProject = theProject
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
