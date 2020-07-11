# -*- coding: utf-8 -*-
"""novelWriter GUI New Project Wizard

 novelWriter – GUI New project Wizard
======================================
 Class holding the new project wizard dialog

 File History:
 Created: 2020-07-11 [0.10.1]

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

from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtWidgets import (
    QWizard, QWizardPage, QLabel, QVBoxLayout, QLineEdit, QPlainTextEdit,
    QPushButton, QFileDialog, QHBoxLayout
)

from nw.common import makeFileNameSafe
from nw.gui.custom import QSwitch, QConfigLayout

logger = logging.getLogger(__name__)

class GuiProjectWizard(QWizard):

    def __init__(self, theParent):
        QWizard.__init__(self, theParent)

        logger.debug("Initialising GuiProjectWizard ...")

        self.mainConf  = nw.CONFIG
        self.theParent = theParent
        self.theTheme  = theParent.theTheme

        nPx = self.mainConf.pxInt(96)
        wmW = self.mainConf.pxInt(100)
        wmH = self.mainConf.pxInt(340)

        self.sideImage = QPixmap(wmW, wmH)
        self.sideImage.fill(self.palette().dark().color())

        # self.setWizardStyle(QWizard.ModernStyle)
        self.setPixmap(QWizard.WatermarkPixmap, self.sideImage)

        self.introPage = ProjWizardIntroPage(self.theParent)
        self.storagePage = ProjWizardFolderPage(self.theParent)

        self.addPage(self.introPage)
        self.addPage(self.storagePage)

        self.setOption(QWizard.NoBackButtonOnStartPage, True)
        # self.setOption(QWizard.ExtendedWatermarkPixmap, True)

        logger.debug("GuiProjectWizard initialisation complete")

        return

# END Class GuiProjectWizard

class ProjWizardIntroPage(QWizardPage):

    def __init__(self, theParent):
        QWizardPage.__init__(self)

        self.mainConf  = nw.CONFIG
        self.theParent = theParent
        self.theTheme  = theParent.theTheme

        self.setTitle("Create New Project")
        self.theText = QLabel(
            "Provide at least a working title. The working title should not "
            "be change beyond this point as it is used by the application for "
            "generating file names for for instance backups. The other fields "
            "are optional and can be changed at any time in Project Settings."
        )
        self.theText.setWordWrap(True)

        xW = self.mainConf.pxInt(300)
        xH = self.mainConf.pxInt(100)
        vS = self.mainConf.pxInt(12)
        fS = self.mainConf.pxInt(4)

        # The Page Form
        self.projName = QLineEdit()
        self.projName.setMaxLength(200)
        self.projName.setFixedWidth(xW)
        self.projName.setPlaceholderText("Required")

        self.projTitle = QLineEdit()
        self.projTitle.setMaxLength(200)
        self.projTitle.setFixedWidth(xW)
        self.projTitle.setPlaceholderText("Optional")

        self.projAuthors = QPlainTextEdit()
        self.projAuthors.setFixedHeight(xH)
        self.projAuthors.setFixedWidth(xW)
        self.projAuthors.setPlaceholderText("Optional. One name per line.")

        self.mainForm = QConfigLayout()
        self.mainForm.addRow("Working Title", self.projName)
        self.mainForm.addRow("Novel Title", self.projTitle)
        self.mainForm.addRow("Author(s)", self.projAuthors)
        self.mainForm.setVerticalSpacing(fS)

        self.registerField("projName*", self.projName)
        self.registerField("projTitle", self.projTitle)
        self.registerField("projAuthors", self.projAuthors)

        # Assemble
        self.outerBox = QVBoxLayout()
        self.outerBox.setSpacing(vS)
        self.outerBox.addWidget(self.theText)
        self.outerBox.addLayout(self.mainForm)
        self.outerBox.addStretch(1)
        self.setLayout(self.outerBox)

        return

# END Class ProjWizardIntroPage

class ProjWizardFolderPage(QWizardPage):

    def __init__(self, theParent):
        QWizardPage.__init__(self)

        self.mainConf  = nw.CONFIG
        self.theParent = theParent
        self.theTheme  = theParent.theTheme

        self.setTitle("Select Project Folder")
        self.theText = QLabel(
            "Select a location to store the project. A new project folder "
            "will be created in the selected location."
        )
        self.theText.setWordWrap(True)

        xW = self.mainConf.pxInt(300)
        # xH = self.mainConf.pxInt(100)
        vS = self.mainConf.pxInt(12)
        fS = self.mainConf.pxInt(4)

        self.projPath = QLineEdit("")
        self.projPath.setFixedWidth(xW)
        self.projPath.setPlaceholderText("Required")

        self.browseButton = QPushButton("...")
        self.browseButton.setMaximumWidth(int(2.5*self.theTheme.getTextWidth("...")))
        self.browseButton.clicked.connect(self._doBrowse)

        self.mainForm = QConfigLayout()
        self.mainForm.addRow("Project Path", self.projPath, theButton=self.browseButton)
        self.mainForm.setVerticalSpacing(fS)

        self.registerField("projPath*", self.projPath)

        # Assemble
        self.outerBox = QVBoxLayout()
        self.outerBox.setSpacing(vS)
        self.outerBox.addWidget(self.theText)
        self.outerBox.addLayout(self.mainForm)
        self.outerBox.addStretch(1)
        self.setLayout(self.outerBox)

        return

    ##
    #  Slots
    ##

    def _doBrowse(self):
        """Select a project folder.
        """
        lastPath = self.mainConf.lastPath
        if not path.isdir(lastPath):
            lastPath = ""

        dlgOpt  = QFileDialog.Options()
        dlgOpt |= QFileDialog.ShowDirsOnly
        dlgOpt |= QFileDialog.DontUseNativeDialog
        projDir = QFileDialog.getExistingDirectory(
            self,"Select Project Folder", lastPath, options=dlgOpt
        )
        if projDir:
            projName = self.field("projName")
            if projName is not None:
                fullDir = path.join(path.abspath(projDir), makeFileNameSafe(projName))
                self.projPath.setText(fullDir)
        else:
            self.projPath.setText("")

        return

# END Class ProjWizardFolderPage
