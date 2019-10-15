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
    QGroupBox, QCheckBox, QLabel, QComboBox, QLineEdit, QPushButton
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

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self._doSave)
        self.buttonBox.rejected.connect(self._doClose)

        self.innerBox.addWidget(self.tabWidget)
        self.innerBox.addWidget(self.buttonBox)

        self.show()

        logger.debug("GuiExport initialisation complete")

        return

    ##
    #  Buttons
    ##

    def _doSave(self):
        logger.verbose("GuiExport save button clicked")
        self.close()
        return

    def _doClose(self):
        logger.verbose("GuiExport close button clicked")
        self.close()
        return

# END Class GuiExport

class GuiExportMain(QWidget):

    FMT_MD    = 1
    FMT_HTML  = 2
    FMT_EBOOK = 3
    FMT_FODT  = 4
    FMT_PDF   = 5

    def __init__(self, theParent, theProject):
        QWidget.__init__(self, theParent)

        self.theParent  = theParent
        self.theProject = theProject
        self.theTheme   = theParent.theTheme
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

        self.chapterFormat = QLineEdit()
        self.chapterFormat.setText("Chapter %numword%")
        self.chapterFormat.setToolTip("Available formats: %num%, %numword%, %title%, %label%")
        self.chapterFormat.setMinimumWidth(250)

        self.guiChaptersForm.addWidget(QLabel("Format"),   0, 0)
        self.guiChaptersForm.addWidget(self.chapterFormat, 0, 1)

        # Output Format
        self.guiOutput     = QGroupBox("Output", self)
        self.guiOutputForm = QGridLayout(self)
        self.guiOutput.setLayout(self.guiOutputForm)

        self.outputFormat = QComboBox(self)
        self.outputFormat.addItem("Markdown",       self.FMT_MD)
        self.outputFormat.addItem("HTML (Plain)",   self.FMT_HTML)
        self.outputFormat.addItem("HTML (eBook)",   self.FMT_EBOOK)
        self.outputFormat.addItem("Open Document",  self.FMT_FODT)
        self.outputFormat.addItem("PDF (PDFLaTeX)", self.FMT_PDF)

        self.outputComments = QCheckBox("include comments", self)

        self.guiOutputForm.addWidget(QLabel("Export format"), 0, 0)
        self.guiOutputForm.addWidget(self.outputFormat,       0, 1)
        self.guiOutputForm.addWidget(self.outputComments,     0, 2)
        self.guiOutputForm.setColumnStretch(2, 1)

        # Scene Settings
        self.guiScenes     = QGroupBox("Scenes", self)
        self.guiScenesForm = QGridLayout(self)
        self.guiScenes.setLayout(self.guiScenesForm)

        self.sceneFormat = QLineEdit()
        self.sceneFormat.setText("* * *")
        self.sceneFormat.setToolTip("Available formats: %title%")
        self.sceneFormat.setMinimumWidth(100)

        self.guiScenesForm.addWidget(QLabel("Format"), 0, 0)
        self.guiScenesForm.addWidget(self.sceneFormat, 0, 1)

        # Output Path
        self.exportTo     = QGroupBox("Backup", self)
        self.exportToForm = QGridLayout(self)
        self.exportTo.setLayout(self.exportToForm)

        self.exportPath = QLineEdit()

        self.exportGetPath = QPushButton(self.theTheme.getIcon("folder"),"")
        # self.exportGetPath.clicked.connect(self._backupFolder)

        self.exportToForm.addWidget(QLabel("Save to"),  0, 0)
        self.exportToForm.addWidget(self.exportPath,    0, 1)
        self.exportToForm.addWidget(self.exportGetPath, 0, 2)

        # Assemble
        self.outerBox.addWidget(self.guiFiles,    0, 0)
        self.outerBox.addWidget(self.guiOutput,   0, 1, 1, 2)
        self.outerBox.addWidget(self.guiChapters, 1, 0, 1, 2)
        self.outerBox.addWidget(self.guiScenes,   1, 2)
        self.outerBox.addWidget(self.exportTo,    2, 0, 1, 3)
        self.outerBox.setColumnStretch(0, 1)
        self.outerBox.setColumnStretch(1, 1)
        self.outerBox.setColumnStretch(2, 1)
        # self.outerBox.setRowStretch(4, 1)
        self.setLayout(self.outerBox)

        return

# END Class GuiExportMain
