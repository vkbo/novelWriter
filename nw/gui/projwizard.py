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
    QPushButton, QFileDialog, QHBoxLayout, QRadioButton, QFormLayout
)

from nw.common import makeFileNameSafe
from nw.gui.custom import QSwitch

logger = logging.getLogger(__name__)

PAGE_INTRO  = 0
PAGE_STORE  = 1
PAGE_POP    = 2
PAGE_CUSTOM = 3
PAGE_FINAL  = 4

class GuiProjectWizard(QWizard):

    def __init__(self, theParent):
        QWizard.__init__(self, theParent)

        logger.debug("Initialising GuiProjectWizard ...")

        self.mainConf  = nw.CONFIG
        self.theParent = theParent
        self.theTheme  = theParent.theTheme

        self.sideImage = self.theTheme.loadDecoration(
            "wiz-back", None, self.mainConf.pxInt(370)
        )
        self.setWizardStyle(QWizard.ModernStyle)
        self.setPixmap(QWizard.WatermarkPixmap, self.sideImage)

        self.introPage = ProjWizardIntroPage(self.theParent)
        self.storagePage = ProjWizardFolderPage(self.theParent)
        self.popPage = ProjWizardPopulatePage(self.theParent)
        self.customPage = ProjWizardCustomPage(self.theParent)
        self.finalPage = ProjWizardFinalPage(self.theParent)

        self.setPage(PAGE_INTRO, self.introPage)
        self.setPage(PAGE_STORE, self.storagePage)
        self.setPage(PAGE_POP, self.popPage)
        self.setPage(PAGE_CUSTOM, self.customPage)
        self.setPage(PAGE_FINAL, self.finalPage)

        self.setOption(QWizard.NoBackButtonOnStartPage, True)

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

        self.imgCredit = QLabel("Side image by Peter Mitterhofer, CC BY-SA 4.0")
        lblFont = self.imgCredit.font()
        lblFont.setPointSizeF(0.6*self.theTheme.fontPointSize)
        self.imgCredit.setFont(lblFont)

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

        self.mainForm = QFormLayout()
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
        self.outerBox.addWidget(self.imgCredit)
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
        vS = self.mainConf.pxInt(12)
        fS = self.mainConf.pxInt(8)

        self.projPath = QLineEdit("")
        self.projPath.setFixedWidth(xW)
        self.projPath.setPlaceholderText("Required")

        self.browseButton = QPushButton("...")
        self.browseButton.setMaximumWidth(int(2.5*self.theTheme.getTextWidth("...")))
        self.browseButton.clicked.connect(self._doBrowse)

        self.mainForm = QHBoxLayout()
        self.mainForm.addWidget(QLabel("Project Path"), 0)
        self.mainForm.addWidget(self.projPath, 1)
        self.mainForm.addWidget(self.browseButton, 0)
        self.mainForm.setSpacing(fS)

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

class ProjWizardPopulatePage(QWizardPage):

    def __init__(self, theParent):
        QWizardPage.__init__(self)

        self.mainConf  = nw.CONFIG
        self.theParent = theParent
        self.theTheme  = theParent.theTheme

        self.setTitle("Populate Project")
        self.theText = QLabel(
            "Choose how to pre-fill the project. Either with a minimal set of "
            "starter items, a sample project explaining and showing many of "
            "the features, or show further custom options on the next page."
        )
        self.theText.setWordWrap(True)

        vS = self.mainConf.pxInt(12)
        fS = self.mainConf.pxInt(4)

        self.popSample = QRadioButton("Fill the project with sample files")
        self.popMinimal = QRadioButton("Fill the project with a minimal set of items")
        self.popCustom = QRadioButton("Show detailed options for filling the project")
        self.popMinimal.setChecked(True)

        self.popBox = QVBoxLayout()
        self.popBox.setSpacing(fS)
        self.popBox.addWidget(self.popMinimal)
        self.popBox.addWidget(self.popSample)
        self.popBox.addWidget(self.popCustom)

        self.registerField("popSample", self.popSample)
        self.registerField("popMinimal", self.popMinimal)
        self.registerField("popCustom", self.popCustom)

        # Assemble
        self.outerBox = QVBoxLayout()
        self.outerBox.setSpacing(vS)
        self.outerBox.addWidget(self.theText)
        self.outerBox.addLayout(self.popBox)
        self.outerBox.addStretch(1)
        self.setLayout(self.outerBox)

        return

    def nextId(self):
        """Overload the nextID function to skip further pages if custom
        is not selected.
        """
        if self.popCustom.isChecked():
            return PAGE_CUSTOM
        else:
            return PAGE_FINAL

# END Class ProjWizardPopulatePage

class ProjWizardCustomPage(QWizardPage):

    def __init__(self, theParent):
        QWizardPage.__init__(self)

        self.mainConf  = nw.CONFIG
        self.theParent = theParent
        self.theTheme  = theParent.theTheme

        self.setTitle("Custom Project Options")
        self.theText = QLabel(
            "Text"
        )
        self.theText.setWordWrap(True)

        vS = self.mainConf.pxInt(12)
        fS = self.mainConf.pxInt(4)

        # Assemble
        self.outerBox = QVBoxLayout()
        self.outerBox.setSpacing(vS)
        self.outerBox.addWidget(self.theText)
        # self.outerBox.addLayout(self.popBox)
        self.outerBox.addStretch(1)
        self.setLayout(self.outerBox)

        return

# END Class ProjWizardCustomPage

class ProjWizardFinalPage(QWizardPage):

    def __init__(self, theParent):
        QWizardPage.__init__(self)

        self.mainConf  = nw.CONFIG
        self.theParent = theParent
        self.theTheme  = theParent.theTheme

        self.setTitle("Overview")
        self.theText = QLabel(
            "Text"
        )
        self.theText.setWordWrap(True)

        vS = self.mainConf.pxInt(12)
        fS = self.mainConf.pxInt(4)

        # Assemble
        self.outerBox = QVBoxLayout()
        self.outerBox.setSpacing(vS)
        self.outerBox.addWidget(self.theText)
        # self.outerBox.addLayout(self.popBox)
        self.outerBox.addStretch(1)
        self.setLayout(self.outerBox)

        return

# END Class ProjWizardFinalPage
