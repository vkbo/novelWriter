# -*- coding: utf-8 -*-
"""novelWriter GUI Export Tools

 novelWriter – GUI Export Tools
================================
 Tool for exporting project files to other formats

 File History:
 Created: 2019-10-13 [0.2.3]

"""

import logging
import nw

from os import path

from PyQt5.QtCore    import Qt, QSize
from PyQt5.QtSvg     import QSvgWidget
from PyQt5.QtWidgets import (
    QDialog, QHBoxLayout, QVBoxLayout, QWidget, QTabWidget, QDialogButtonBox, QGridLayout,
    QGroupBox, QCheckBox, QLabel, QComboBox, QLineEdit
)

from nw.tools.translate import numberToWord

logger = logging.getLogger(__name__)

class GuiExport(QDialog):

    def __init__(self, theParent, theProject):
        QDialog.__init__(self, theParent)

        logger.debug("Initialising GuiExport ...")

        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theProject = theProject

        self.outerBox   = QHBoxLayout()
        self.innerBox   = QVBoxLayout()
        self.setWindowTitle("Export Project")
        self.setLayout(self.outerBox)

        self.gradPath = path.abspath(path.join(self.mainConf.appPath,"graphics","gear.svg"))
        self.svgGradient = QSvgWidget(self.gradPath)
        self.svgGradient.setFixedSize(QSize(64,64))

        self.theProject.countStatus()
        self.tabMain    = GuiExportMain(self.theParent, self.theProject)

        self.tabWidget = QTabWidget()
        self.tabWidget.addTab(self.tabMain, "Settings")

        self.outerBox.addWidget(self.svgGradient, 0, Qt.AlignTop)
        self.outerBox.addLayout(self.innerBox)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        # self.buttonBox.accepted.connect(self._doSave)
        # self.buttonBox.rejected.connect(self._doClose)

        self.innerBox.addWidget(self.tabWidget)
        self.innerBox.addWidget(self.buttonBox)

        self.show()

        for n in range(1000):
            numberToWord(n,"EN")

        logger.debug("GuiExport initialisation complete")

        return

# END Class GuiExport

class GuiExportMain(QWidget):

    CHFMT_NUM      = 1
    CHFMT_NUMWORD  = 2
    CHFMT_TITLE    = 3
    CHFMT_LABEL    = 4
    CHFMT_NUMTITLE = 5
    CHFMT_NUMLABEL = 6
    CHFMT_CUSTOM   = 7

    def __init__(self, theParent, theProject):
        QWidget.__init__(self, theParent)

        self.theParent  = theParent
        self.theProject = theProject
        self.outerBox   = QGridLayout()

        # Select Files
        self.guiFiles     = QGroupBox("Export Files", self)
        self.guiFilesForm = QGridLayout(self)
        self.guiFiles.setLayout(self.guiFilesForm)

        self.expNovel = QCheckBox(self)
        self.expNovel.setToolTip("Include all novel files in the exported document")
        self.expNotes = QCheckBox(self)
        self.expNotes.setToolTip("Include all note files in the exported document")

        self.guiFilesForm.addWidget(QLabel("Novel files"), 0, 0)
        self.guiFilesForm.addWidget(self.expNovel,         0, 1)
        self.guiFilesForm.addWidget(QLabel("Note files"),  1, 0)
        self.guiFilesForm.addWidget(self.expNotes,         1, 1)

        # Chapter Settings
        self.guiChapters     = QGroupBox("Chapters", self)
        self.guiChaptersForm = QGridLayout(self)
        self.guiChapters.setLayout(self.guiChaptersForm)

        self.chapterFormat = QComboBox(self)
        self.chapterFormat.addItem("Chapter 1",   self.CHFMT_NUM)
        self.chapterFormat.addItem("Chapter One", self.CHFMT_NUMWORD)
        self.chapterFormat.addItem("[Title]",     self.CHFMT_TITLE)
        self.chapterFormat.addItem("[Label]",     self.CHFMT_LABEL)
        self.chapterFormat.addItem("1. [Title]",  self.CHFMT_NUMTITLE)
        self.chapterFormat.addItem("1. [Label]",  self.CHFMT_NUMLABEL)
        self.chapterFormat.addItem("Custom",      self.CHFMT_CUSTOM)

        self.chapterCustom = QLineEdit()
        self.chapterCustom.setText("%num%. %title%")
        self.chapterCustom.setToolTip("Available options: %num%, %numword%, %title%, %label%")
        self.chapterCustom.setMinimumWidth(200)

        self.guiChaptersForm.addWidget(QLabel("Name format"),   0, 0)
        self.guiChaptersForm.addWidget(self.chapterFormat,      0, 1)
        self.guiChaptersForm.addWidget(QLabel("Custom format"), 1, 0)
        self.guiChaptersForm.addWidget(self.chapterCustom,      1, 1)

        # Assemble
        self.outerBox.addWidget(self.guiFiles,    0, 0)
        self.outerBox.addWidget(self.guiChapters, 1, 0)
        self.outerBox.setColumnStretch(2, 1)
        self.outerBox.setRowStretch(4, 1)
        self.setLayout(self.outerBox)

        return

# END Class GuiExportMain
