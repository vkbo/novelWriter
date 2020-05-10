# -*- coding: utf-8 -*-
"""novelWriter GUI Build Novel

 novelWriter – GUI Build Novel
===============================
 Class holding the build novel window

 File History:
 Created: 2020-05-09 [0.5]

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
from PyQt5.QtGui import QTextOption, QPalette, QColor
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextBrowser, QPushButton,
    QLabel, QLineEdit, QGroupBox, QGridLayout, QComboBox, QProgressBar,
    QMenu, QAction
)

from nw.gui.additions import QSwitch
from nw.core import ToHtml
from nw.constants import nwConst, nwFiles, nwAlert, nwItemType

logger = logging.getLogger(__name__)

class GuiBuildNovel(QDialog):

    FMT_ODT = 1
    FMT_PDF = 2
    FMT_HTM = 3
    FMT_MD  = 4

    def __init__(self, theParent, theProject):
        QDialog.__init__(self, theParent)

        logger.debug("Initialising GuiBuildNovel ...")

        self.mainConf   = nw.CONFIG
        self.theProject = theProject
        self.theParent  = theParent
        self.theTheme   = theParent.theTheme
        self.optState   = self.theProject.optState

        self.setWindowTitle("Build Project")
        self.setMinimumWidth(800)
        self.setMinimumHeight(700)

        self.resize(
            self.optState.getInt("GuiBuildNovel", "winWidth", 800),
            self.optState.getInt("GuiBuildNovel", "winHeight", 700)
        )

        self.outerBox = QVBoxLayout()
        self.innerBox = QHBoxLayout()
        self.toolsBox = QVBoxLayout()

        self.docView = GuiBuildNovelDocView(self, self.theProject)

        # Title Formats
        # =============
        self.titleGroup = QGroupBox("Novel Title Formats", self)
        self.titleForm  = QGridLayout(self)
        self.titleGroup.setLayout(self.titleForm)

        self.fmtTitle = QLineEdit()
        self.fmtTitle.setMaxLength(200)
        self.fmtTitle.setFixedWidth(200)
        self.fmtTitle.setText(self.theProject.titleFormat["title"])

        self.fmtChapter = QLineEdit()
        self.fmtChapter.setMaxLength(200)
        self.fmtChapter.setFixedWidth(200)
        self.fmtChapter.setText(self.theProject.titleFormat["chapter"])

        self.fmtUnnumbered = QLineEdit()
        self.fmtUnnumbered.setMaxLength(200)
        self.fmtUnnumbered.setFixedWidth(200)
        self.fmtUnnumbered.setText(self.theProject.titleFormat["unnumbered"])

        self.fmtScene = QLineEdit()
        self.fmtScene.setMaxLength(200)
        self.fmtScene.setFixedWidth(200)
        self.fmtScene.setText(self.theProject.titleFormat["scene"])

        self.fmtSection = QLineEdit()
        self.fmtSection.setMaxLength(200)
        self.fmtSection.setFixedWidth(200)
        self.fmtSection.setText(self.theProject.titleFormat["section"])

        self.titleForm.addWidget(QLabel("Title"),      0, 0)
        self.titleForm.addWidget(self.fmtTitle,        0, 1)
        self.titleForm.addWidget(QLabel("Chapter"),    1, 0)
        self.titleForm.addWidget(self.fmtChapter,      1, 1)
        self.titleForm.addWidget(QLabel("Unnumbered"), 2, 0)
        self.titleForm.addWidget(self.fmtUnnumbered,   2, 1)
        self.titleForm.addWidget(QLabel("Scene"),      3, 0)
        self.titleForm.addWidget(self.fmtScene,        3, 1)
        self.titleForm.addWidget(QLabel("Section"),    4, 0)
        self.titleForm.addWidget(self.fmtSection,      4, 1)

        self.titleForm.setColumnStretch(0, 1)
        self.titleForm.setColumnStretch(1, 0)

        # Build Settings
        # ==============
        self.buildGroup = QGroupBox("Build Overrides", self)
        self.buildForm  = QGridLayout(self)
        self.buildGroup.setLayout(self.buildForm)

        self.outlineMode = QSwitch()
        self.outlineMode.setChecked(self.optState.getBool("GuiBuildNovel", "outlineMode", False))

        self.buildForm.addWidget(QLabel("Novel Outline Mode"), 0, 0)
        self.buildForm.addWidget(self.outlineMode,             0, 1)

        self.buildForm.setColumnStretch(0, 1)
        self.buildForm.setColumnStretch(1, 0)

        # Include Switches
        # ================
        self.includeGroup = QGroupBox("Include Non-Text Elements", self)
        self.includeForm  = QGridLayout(self)
        self.includeGroup.setLayout(self.includeForm)

        self.includeSynopsis = QSwitch()
        self.includeSynopsis.setChecked(self.theProject.titleFormat["withSynopsis"])
        self.includeComments = QSwitch()
        self.includeComments.setChecked(self.theProject.titleFormat["withComments"])
        self.includeKeywords = QSwitch()
        self.includeKeywords.setChecked(self.theProject.titleFormat["withKeywords"])

        self.includeForm.addWidget(QLabel("Include Synopsis"), 0, 0)
        self.includeForm.addWidget(self.includeSynopsis,       0, 1)
        self.includeForm.addWidget(QLabel("Include Comments"), 1, 0)
        self.includeForm.addWidget(self.includeComments,       1, 1)
        self.includeForm.addWidget(QLabel("Include Keywords"), 2, 0)
        self.includeForm.addWidget(self.includeKeywords,       2, 1)

        self.includeForm.setColumnStretch(0, 1)
        self.includeForm.setColumnStretch(1, 0)

        # Additional Options
        # ==================
        self.addsGroup = QGroupBox("Additional Options", self)
        self.addsForm  = QGridLayout(self)
        self.addsGroup.setLayout(self.addsForm)

        self.novelFiles = QSwitch()
        self.novelFiles.setChecked(self.optState.getBool("GuiBuildNovel", "addNovel", True))
        self.noteFiles = QSwitch()
        self.noteFiles.setChecked(self.optState.getBool("GuiBuildNovel", "addNotes", False))
        self.ignoreFlag = QSwitch()
        self.ignoreFlag.setChecked(self.optState.getBool("GuiBuildNovel", "ignoreFlag", False))

        self.addsForm.addWidget(QLabel("Include Novel Files"), 0, 0)
        self.addsForm.addWidget(self.novelFiles,               0, 1)
        self.addsForm.addWidget(QLabel("Include Note Files"),  1, 0)
        self.addsForm.addWidget(self.noteFiles,                1, 1)
        self.addsForm.addWidget(QLabel("Ignore Export Flag"),  2, 0)
        self.addsForm.addWidget(self.ignoreFlag,               2, 1)

        self.addsForm.setColumnStretch(0, 1)
        self.addsForm.setColumnStretch(1, 0)

        # Build Button
        # ============
        self.buildProgress = QProgressBar()

        self.genPreview = QPushButton("Generate Preview")
        self.genPreview.clicked.connect(self._buildPreview)

        # Action Buttons
        # ==============
        self.buttonForm = QGridLayout()

        self.btnHelp = QPushButton("Help")
        self.btnHelp.clicked.connect(self._showHelp)

        self.btnPrint = QPushButton("Print")
        self.btnPrint.clicked.connect(self._printDocument)

        self.btnSave = QPushButton("Save As")
        self.saveMenu = QMenu(self)
        self.saveODT = QAction("Open Document (.odt)")
        self.savePDF = QAction("Portable Document (.pdf)")
        self.saveHTM = QAction("HTML5 (.htm)")
        self.saveMD  = QAction("Markdown (.md)")
        self.saveODT.triggered.connect(lambda: self._saveDocument(self.FMT_ODT))
        self.savePDF.triggered.connect(lambda: self._saveDocument(self.FMT_PDF))
        self.saveHTM.triggered.connect(lambda: self._saveDocument(self.FMT_HTM))
        self.saveMD.triggered.connect(lambda: self._saveDocument(self.FMT_MD))
        self.saveMenu.addAction(self.saveODT)
        self.saveMenu.addAction(self.savePDF)
        self.saveMenu.addAction(self.saveHTM)
        self.saveMenu.addAction(self.saveMD)
        self.btnSave.setMenu(self.saveMenu)

        self.btnClose = QPushButton("Close")
        self.btnClose.clicked.connect(self._doClose)

        self.buttonForm.addWidget(self.btnHelp,  0, 0)
        self.buttonForm.addWidget(self.btnPrint, 0, 1)
        self.buttonForm.addWidget(self.btnSave,  1, 0)
        self.buttonForm.addWidget(self.btnClose, 1, 1)

        # Assemble GUI
        # ============
        self.toolsBox.addWidget(self.titleGroup)
        self.toolsBox.addWidget(self.buildGroup)
        self.toolsBox.addWidget(self.includeGroup)
        self.toolsBox.addWidget(self.addsGroup)
        self.toolsBox.addStretch(1)
        self.toolsBox.addWidget(self.buildProgress)
        self.toolsBox.addWidget(self.genPreview)
        self.toolsBox.addSpacing(8)
        self.toolsBox.addLayout(self.buttonForm)

        self.innerBox.addLayout(self.toolsBox)
        self.innerBox.addWidget(self.docView)

        self.outerBox.addLayout(self.innerBox)
        self.setLayout(self.outerBox)

        self.innerBox.setStretch(0, 0)
        self.innerBox.setStretch(1, 1)

        self.outlineMode.toggled.connect(self._toggelOutlineMode)
        self._toggelOutlineMode(self.outlineMode.isChecked())

        self.show()

        logger.debug("GuiBuildNovel initialisation complete")

        return

    ##
    #  Slots
    ##

    def _buildPreview(self):
        """Build a preview of the project in the document viewer.
        """

        makeHtml = ToHtml(self.theProject, self.theParent)
        theText = ""

        for tItem in self.theProject.projTree:
            if tItem is not None and tItem.itemType == nwItemType.FILE:
                makeHtml.setText(tItem.itemHandle)
                makeHtml.doAutoReplace()
                makeHtml.tokenizeText()
                makeHtml.doHeaders()
                makeHtml.doConvert()
                makeHtml.doPostProcessing()
                theText += makeHtml.getResult()

        self.docView.setHtml(theText)

        return

    def _saveDocument(self, theFormat):
        return

    def _printDocument(self):
        return

    def _toggelOutlineMode(self, theState):
        """Enables or disables the options that are overridden in#
        outline mode.
        """
        self.fmtTitle.setEnabled(not theState)
        self.fmtChapter.setEnabled(not theState)
        self.fmtUnnumbered.setEnabled(not theState)
        self.fmtScene.setEnabled(not theState)
        self.fmtSection.setEnabled(not theState)
        self.includeSynopsis.setEnabled(not theState)
        self.novelFiles.setEnabled(not theState)
        self.noteFiles.setEnabled(not theState)
        return

    def _doClose(self):
        """Close button was clicked.
        """
        self.close()
        return

    ##
    #  Events
    ##

    def closeEvent(self, theEvent):
        """Capture the user closing the window so we can save settings.
        """
        self._saveSettings()
        QDialog.closeEvent(self, theEvent)
        return

    ##
    #  Internal Functions
    ##

    def _saveSettings(self):
        """Save the various user settings.
        """
        logger.debug("Saving GuiBuildNovel settings")

        # Formatting
        self.theProject.setTitleFormat({
            "title"        : self.fmtTitle.text().strip(),
            "chapter"      : self.fmtChapter.text().strip(),
            "unnumbered"   : self.fmtUnnumbered.text().strip(),
            "scene"        : self.fmtScene.text().strip(),
            "section"      : self.fmtSection.text().strip(),
            "withSynopsis" : self.includeSynopsis.isChecked(),
            "withComments" : self.includeComments.isChecked(),
            "withKeywords" : self.includeKeywords.isChecked(),
        })

        # GUI Settings
        self.optState.setValue("GuiBuildNovel", "winWidth",    self.width())
        self.optState.setValue("GuiBuildNovel", "winHeight",   self.height())
        self.optState.setValue("GuiBuildNovel", "outlineMode", self.outlineMode.isChecked())
        self.optState.setValue("GuiBuildNovel", "addNovel",    self.novelFiles.isChecked())
        self.optState.setValue("GuiBuildNovel", "addNotes",    self.noteFiles.isChecked())
        self.optState.setValue("GuiBuildNovel", "ignoreFlag",  self.ignoreFlag.isChecked())
        self.optState.saveSettings()

        return

    def _showHelp(self):
        """Generate a help text and show it in the document window.
        """
        docName = "exportHelp_%s.htm" % self.mainConf.guiLang
        docPath = path.join(self.mainConf.assetPath, "text", docName)
        if path.isfile(docPath):
            with open(docPath, mode="r", encoding="utf8") as inFile:
                helpText = inFile.read()
            self.docView.setText(helpText)
        else:
            self.theParent.makeAlert(
                "Could not open help text file for Build Project.", nwAlert.ERROR
            )
        return

# END Class GuiBuildNovel

class GuiBuildNovelDocView(QTextBrowser):

    def __init__(self, theParent, theProject):
        QTextBrowser.__init__(self, theParent)

        logger.debug("Initialising GuiBuildNovelDocView ...")

        self.mainConf   = nw.CONFIG
        self.theProject = theProject
        self.theParent  = theParent

        self.setMinimumWidth(400)
        self.setOpenExternalLinks(False)

        self.qDocument = self.document()
        self.qDocument.setDocumentMargin(self.mainConf.textMargin)

        theOpt = QTextOption()
        if self.mainConf.doJustify:
            theOpt.setAlignment(Qt.AlignJustify)
        self.qDocument.setDefaultTextOption(theOpt)

        docPalette = self.palette()
        docPalette.setColor(QPalette.Base, QColor(255, 255, 255))
        docPalette.setColor(QPalette.Text, QColor(  0,   0,   0))
        self.setPalette(docPalette)

        self._makeStyleSheet()

        self.show()

        logger.debug("GuiBuildNovelDocView initialisation complete")

        return

    def setText(self, theText):
        self.setHtml(theText)
        return

    ##
    #  Internal Functions
    ##

    def _makeStyleSheet(self):

        styleSheet = (
            "h1, h2 {"
            "  color: rgb(66, 113, 174);"
            "}\n"
            "h3, h4 {"
            "  color: rgb(50, 50, 50);"
            "}\n"
            "a {"
            "  color: rgb(137, 89, 168);"
            "}\n"
            "mark {"
            "  background-color: rgb(240, 198, 116);"
            "}\n"
        )
        self.qDocument.setDefaultStyleSheet(styleSheet)

        return

# END Class GuiBuildNovelDocView
