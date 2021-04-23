# -*- coding: utf-8 -*-
"""
novelWriter – GUI New Project Wizard
====================================
GUI classes for the new project wizard dialog

File History:
Created: 2020-07-11 [0.10.1]

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
from PyQt5.QtWidgets import (
    QWizard, QWizardPage, QLabel, QVBoxLayout, QLineEdit, QPlainTextEdit,
    QPushButton, QFileDialog, QHBoxLayout, QRadioButton, QFormLayout,
    QGroupBox, QGridLayout, QSpinBox
)

from nw.enum import nwItemClass
from nw.common import makeFileNameSafe
from nw.constants import trConst, nwLabels
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
        self.setObjectName("GuiProjectWizard")

        self.mainConf  = nw.CONFIG
        self.theParent = theParent
        self.theTheme  = theParent.theTheme

        self.sideImage = self.theTheme.loadDecoration(
            "wiz-back", None, self.mainConf.pxInt(370)
        )
        self.setWizardStyle(QWizard.ModernStyle)
        self.setPixmap(QWizard.WatermarkPixmap, self.sideImage)

        self.introPage = ProjWizardIntroPage(self)
        self.storagePage = ProjWizardFolderPage(self)
        self.popPage = ProjWizardPopulatePage(self)
        self.customPage = ProjWizardCustomPage(self)
        self.finalPage = ProjWizardFinalPage(self)

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

    def __init__(self, theWizard):
        QWizardPage.__init__(self)

        self.mainConf  = nw.CONFIG
        self.theWizard = theWizard
        self.theTheme  = theWizard.theTheme

        self.setTitle(self.tr("Create New Project"))
        self.theText = QLabel(self.tr(
            "Provide at least a working title. The working title should not "
            "be change beyond this point as it is used by the application for "
            "generating file names for for instance backups. The other fields "
            "are optional and can be changed at any time in Project Settings."
        ))
        self.theText.setWordWrap(True)

        self.imgCredit = QLabel(self.tr("Side image by {0}, {1}").format(
            "Peter Mitterhofer", "CC BY-SA 4.0"
        ))
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
        self.projName.setPlaceholderText(self.tr("Required"))

        self.projTitle = QLineEdit()
        self.projTitle.setMaxLength(200)
        self.projTitle.setFixedWidth(xW)
        self.projTitle.setPlaceholderText(self.tr("Optional"))

        self.projAuthors = QPlainTextEdit()
        self.projAuthors.setFixedHeight(xH)
        self.projAuthors.setFixedWidth(xW)
        self.projAuthors.setPlaceholderText(self.tr("Optional. One name per line."))

        self.mainForm = QFormLayout()
        self.mainForm.addRow(self.tr("Working Title"), self.projName)
        self.mainForm.addRow(self.tr("Novel Title"), self.projTitle)
        self.mainForm.addRow(self.tr("Author(s)"), self.projAuthors)
        self.mainForm.setVerticalSpacing(fS)

        self.registerField("projName*", self.projName)
        self.registerField("projTitle", self.projTitle)
        self.registerField("projAuthors", self.projAuthors, "plainText")

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

    def __init__(self, theWizard):
        QWizardPage.__init__(self)

        self.mainConf  = nw.CONFIG
        self.theWizard = theWizard
        self.theTheme  = theWizard.theTheme

        self.setTitle(self.tr("Select Project Folder"))
        self.theText = QLabel(self.tr(
            "Select a location to store the project. A new project folder "
            "will be created in the selected location."
        ))
        self.theText.setWordWrap(True)

        xW = self.mainConf.pxInt(300)
        vS = self.mainConf.pxInt(12)
        fS = self.mainConf.pxInt(8)

        self.projPath = QLineEdit("")
        self.projPath.setFixedWidth(xW)
        self.projPath.setPlaceholderText(self.tr("Required"))

        self.browseButton = QPushButton("...")
        self.browseButton.setMaximumWidth(int(2.5*self.theTheme.getTextWidth("...")))
        self.browseButton.clicked.connect(self._doBrowse)

        self.mainForm = QHBoxLayout()
        self.mainForm.addWidget(QLabel(self.tr("Project Path")), 0)
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
        if not os.path.isdir(lastPath):
            lastPath = ""

        projDir = QFileDialog.getExistingDirectory(
            self, self.tr("Select Project Folder"), lastPath, options=QFileDialog.ShowDirsOnly
        )
        if projDir:
            projName = self.field("projName")
            if projName is not None:
                fullDir = os.path.join(os.path.abspath(projDir), makeFileNameSafe(projName))
                self.projPath.setText(fullDir)
        else:
            self.projPath.setText("")

        return

# END Class ProjWizardFolderPage

class ProjWizardPopulatePage(QWizardPage):

    def __init__(self, theWizard):
        QWizardPage.__init__(self)

        self.mainConf  = nw.CONFIG
        self.theWizard = theWizard

        self.setTitle(self.tr("Populate Project"))
        self.theText = QLabel(self.tr(
            "Choose how to pre-fill the project. Either with a minimal set of "
            "starter items, an example project explaining and showing many of "
            "the features, or show further custom options on the next page."
        ))
        self.theText.setWordWrap(True)

        vS = self.mainConf.pxInt(12)
        fS = self.mainConf.pxInt(4)

        self.popMinimal = QRadioButton(self.tr("Fill the project with a minimal set of items"))
        self.popSample = QRadioButton(self.tr("Fill the project with example files"))
        self.popCustom = QRadioButton(self.tr("Show detailed options for filling the project"))
        self.popMinimal.setChecked(True)

        self.popBox = QVBoxLayout()
        self.popBox.setSpacing(fS)
        self.popBox.addWidget(self.popMinimal)
        self.popBox.addWidget(self.popSample)
        self.popBox.addWidget(self.popCustom)

        self.registerField("popMinimal", self.popMinimal)
        self.registerField("popSample", self.popSample)
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

    def __init__(self, theWizard):
        QWizardPage.__init__(self)

        self.mainConf  = nw.CONFIG
        self.theWizard = theWizard

        self.setTitle(self.tr("Custom Project Options"))
        self.theText = QLabel(self.tr(
            "Select which additional root folders to make, and how to populate "
            "the Novel folder. If you don't want to add chapters or scenes, set "
            "the values to 0. You can add scenes without chapters."
        ))
        self.theText.setWordWrap(True)

        vS = self.mainConf.pxInt(12)

        # Root Folders
        self.rootGroup = QGroupBox(self.tr("Additional Root Folders"))
        self.rootForm  = QGridLayout()
        self.rootGroup.setLayout(self.rootForm)

        self.lblPlot = QLabel(self.tr("{0} folder").format(
            trConst(nwLabels.CLASS_NAME[nwItemClass.PLOT]))
        )
        self.lblChar = QLabel(self.tr("{0} folder").format(
            trConst(nwLabels.CLASS_NAME[nwItemClass.CHARACTER]))
        )
        self.lblWorld = QLabel(self.tr("{0} folder").format(
            trConst(nwLabels.CLASS_NAME[nwItemClass.WORLD]))
        )
        self.lblTime = QLabel(self.tr("{0} folder").format(
            trConst(nwLabels.CLASS_NAME[nwItemClass.TIMELINE]))
        )
        self.lblObject = QLabel(self.tr("{0} folder").format(
            trConst(nwLabels.CLASS_NAME[nwItemClass.OBJECT]))
        )
        self.lblEntity = QLabel(self.tr("{0} folder").format(
            trConst(nwLabels.CLASS_NAME[nwItemClass.ENTITY]))
        )

        self.addPlot   = QSwitch()
        self.addChar   = QSwitch()
        self.addWorld  = QSwitch()
        self.addTime   = QSwitch()
        self.addObject = QSwitch()
        self.addEntity = QSwitch()

        self.addPlot.setChecked(True)
        self.addChar.setChecked(True)
        self.addWorld.setChecked(True)

        self.rootForm.addWidget(self.lblPlot,   0, 0)
        self.rootForm.addWidget(self.lblChar,   1, 0)
        self.rootForm.addWidget(self.lblWorld,  2, 0)
        self.rootForm.addWidget(self.lblTime,   3, 0)
        self.rootForm.addWidget(self.lblObject, 4, 0)
        self.rootForm.addWidget(self.lblEntity, 5, 0)
        self.rootForm.addWidget(self.addPlot,   0, 1, 1, 1, Qt.AlignRight)
        self.rootForm.addWidget(self.addChar,   1, 1, 1, 1, Qt.AlignRight)
        self.rootForm.addWidget(self.addWorld,  2, 1, 1, 1, Qt.AlignRight)
        self.rootForm.addWidget(self.addTime,   3, 1, 1, 1, Qt.AlignRight)
        self.rootForm.addWidget(self.addObject, 4, 1, 1, 1, Qt.AlignRight)
        self.rootForm.addWidget(self.addEntity, 5, 1, 1, 1, Qt.AlignRight)
        self.rootForm.setRowStretch(6, 1)

        # Novel Options
        self.novelGroup = QGroupBox(self.tr("Populate Novel Folder"))
        self.novelForm  = QGridLayout()
        self.novelGroup.setLayout(self.novelForm)

        self.numChapters = QSpinBox()
        self.numChapters.setRange(0, 100)
        self.numChapters.setValue(5)

        self.numScenes = QSpinBox()
        self.numScenes.setRange(0, 200)
        self.numScenes.setValue(5)

        self.chFolders = QSwitch()
        self.chFolders.setChecked(True)

        self.novelForm.addWidget(QLabel(self.tr("Add chapters")),         0, 0)
        self.novelForm.addWidget(QLabel(self.tr("Scenes (per chapter)")), 1, 0)
        self.novelForm.addWidget(QLabel(self.tr("Add chapter folders")),  2, 0)
        self.novelForm.addWidget(self.numChapters, 0, 1, 1, 1, Qt.AlignRight)
        self.novelForm.addWidget(self.numScenes,   1, 1, 1, 1, Qt.AlignRight)
        self.novelForm.addWidget(self.chFolders,   2, 1, 1, 1, Qt.AlignRight)
        self.novelForm.setRowStretch(3, 1)

        # Wizard Fields
        self.registerField("addPlot", self.addPlot)
        self.registerField("addChar", self.addChar)
        self.registerField("addWorld", self.addWorld)
        self.registerField("addTime", self.addTime)
        self.registerField("addObject", self.addObject)
        self.registerField("addEntity", self.addEntity)
        self.registerField("numChapters", self.numChapters)
        self.registerField("numScenes", self.numScenes)
        self.registerField("chFolders", self.chFolders)

        # Assemble
        self.innerBox = QHBoxLayout()
        self.innerBox.addWidget(self.rootGroup)
        self.innerBox.addWidget(self.novelGroup)

        self.outerBox = QVBoxLayout()
        self.outerBox.setSpacing(vS)
        self.outerBox.addWidget(self.theText)
        self.outerBox.addLayout(self.innerBox)
        self.outerBox.addStretch(1)
        self.setLayout(self.outerBox)

        return

# END Class ProjWizardCustomPage

class ProjWizardFinalPage(QWizardPage):

    def __init__(self, theWizard):
        QWizardPage.__init__(self)

        self.mainConf  = nw.CONFIG
        self.theWizard = theWizard

        self.setTitle(self.tr("Finished"))
        self.theText = QLabel(
            "<p>%s</p><p>%s</p>" % (
                self.tr("All done."),
                self.tr("Press '{0}' to create the new project.").format(
                    self.tr("Done") if self.mainConf.osDarwin else self.tr("Finish")
                )
            )
        )
        self.theText.setWordWrap(True)

        # Assemble
        self.outerBox = QVBoxLayout()
        self.outerBox.setSpacing(self.mainConf.pxInt(12))
        self.outerBox.addWidget(self.theText)
        self.outerBox.addStretch(1)
        self.setLayout(self.outerBox)

        return

# END Class ProjWizardFinalPage
