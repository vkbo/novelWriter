"""
novelWriter – GUI New Project Wizard
====================================
GUI classes for the new project wizard dialog

File History:
Created: 2020-07-11 [0.10.1]

This file is a part of novelWriter
Copyright 2018–2023, Veronica Berglyd Olsen

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

import os
import logging
import novelwriter

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QFileDialog, QFormLayout, QGridLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QRadioButton, QSpinBox, QVBoxLayout, QWizard, QWizardPage
)

from novelwriter.common import makeFileNameSafe
from novelwriter.custom import QSwitch

logger = logging.getLogger(__name__)

PAGE_INTRO  = 0
PAGE_STORE  = 1
PAGE_POP    = 2
PAGE_CUSTOM = 3
PAGE_FINAL  = 4


class GuiProjectWizard(QWizard):

    def __init__(self, mainGui):
        super().__init__(parent=mainGui)

        logger.debug("Initialising GuiProjectWizard ...")
        self.setObjectName("GuiProjectWizard")

        self.mainConf  = novelwriter.CONFIG
        self.mainGui   = mainGui
        self.mainTheme = mainGui.mainTheme

        self.sideImage = self.mainTheme.loadDecoration(
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
        super().__init__()

        self.mainConf  = novelwriter.CONFIG
        self.theWizard = theWizard
        self.mainTheme = theWizard.mainTheme

        self.setTitle(self.tr("Create New Project"))
        self.theText = QLabel(self.tr(
            "Provide at least a project name. The project name should not "
            "be changed beyond this point as it is used for generating file "
            "names for for instance backups. The other fields are optional "
            "and can be changed at any time in Project Settings."
        ))
        self.theText.setWordWrap(True)

        self.imgCredit = QLabel(self.tr("Side image by {0}, {1}").format(
            "Peter Mitterhofer", "CC BY-SA 4.0"
        ))
        lblFont = self.imgCredit.font()
        lblFont.setPointSizeF(0.6*self.mainTheme.fontPointSize)
        self.imgCredit.setFont(lblFont)

        xW = self.mainConf.pxInt(300)
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

        self.projAuthor = QLineEdit()
        self.projAuthor.setMaxLength(200)
        self.projAuthor.setFixedWidth(xW)
        self.projAuthor.setPlaceholderText(self.tr("Optional"))

        self.mainForm = QFormLayout()
        self.mainForm.addRow(self.tr("Project Name"), self.projName)
        self.mainForm.addRow(self.tr("Novel Title"), self.projTitle)
        self.mainForm.addRow(self.tr("Author(s)"), self.projAuthor)
        self.mainForm.setVerticalSpacing(fS)

        self.registerField("projName*", self.projName)
        self.registerField("projTitle", self.projTitle)
        self.registerField("projAuthor", self.projAuthor)

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
        super().__init__()

        self.mainConf  = novelwriter.CONFIG
        self.theWizard = theWizard
        self.mainTheme = theWizard.mainTheme

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
        self.browseButton.setMaximumWidth(int(2.5*self.mainTheme.getTextWidth("...")))
        self.browseButton.clicked.connect(self._doBrowse)

        self.errLabel = QLabel("")
        self.errLabel.setWordWrap(True)

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
        self.outerBox.addWidget(self.errLabel)
        self.outerBox.addStretch(1)
        self.setLayout(self.outerBox)

        return

    def isComplete(self):
        """Check that the selected path isn't already being used.
        """
        self.errLabel.setText("")
        if not super().isComplete():
            return False

        setPath = os.path.abspath(os.path.expanduser(self.projPath.text()))
        parPath = os.path.dirname(setPath)
        logger.debug("Path is: %s", setPath)
        if parPath and not os.path.isdir(parPath):
            self.errLabel.setText(self.tr(
                "Error: A project folder cannot be created using this path."
            ))
            return False

        if os.path.exists(setPath):
            self.errLabel.setText(self.tr(
                "Error: The selected path already exists."
            ))
            return False

        return True

    ##
    #  Slots
    ##

    def _doBrowse(self):
        """Select a project folder.
        """
        lastPath = self.mainConf.lastPath()
        projDir = QFileDialog.getExistingDirectory(
            self, self.tr("Select Project Folder"), str(lastPath), options=QFileDialog.ShowDirsOnly
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
        super().__init__()

        self.mainConf  = novelwriter.CONFIG
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
        super().__init__()

        self.mainConf  = novelwriter.CONFIG
        self.theWizard = theWizard

        self.setTitle(self.tr("Custom Project Options"))
        self.theText = QLabel(self.tr(
            "Select which additional elements to populate the project with. "
            "You can skip making chapters and add only scenes by setting the "
            "number of chapters to 0."
        ))
        self.theText.setWordWrap(True)

        cM = self.mainConf.pxInt(12)
        mH = self.mainConf.pxInt(26)
        fS = self.mainConf.pxInt(4)

        # Root Folders
        self.addPlot = QSwitch()
        self.addPlot.setChecked(True)
        self.addPlot.clicked.connect(self._syncSwitches)

        self.addChar = QSwitch()
        self.addChar.setChecked(True)
        self.addChar.clicked.connect(self._syncSwitches)

        self.addWorld = QSwitch()
        self.addWorld.setChecked(False)
        self.addWorld.clicked.connect(self._syncSwitches)

        self.addNotes = QSwitch()
        self.addNotes.setChecked(False)

        # Generate Content
        self.numChapters = QSpinBox()
        self.numChapters.setRange(0, 100)
        self.numChapters.setValue(5)

        self.numScenes = QSpinBox()
        self.numScenes.setRange(0, 200)
        self.numScenes.setValue(5)

        # Grid Form
        self.addBox = QGridLayout()
        self.addBox.addWidget(QLabel(self.tr("Add a folder for plot notes")),      0, 0)
        self.addBox.addWidget(QLabel(self.tr("Add a folder for character notes")), 1, 0)
        self.addBox.addWidget(QLabel(self.tr("Add a folder for location notes")),  2, 0)
        self.addBox.addWidget(QLabel(self.tr("Add example notes to the above")),   3, 0)
        self.addBox.addWidget(QLabel(self.tr("Add chapters to the novel folder")), 4, 0)
        self.addBox.addWidget(QLabel(self.tr("Add scenes to each chapter")),       5, 0)
        self.addBox.addWidget(self.addPlot,     0, 1, 1, 1, Qt.AlignRight)
        self.addBox.addWidget(self.addChar,     1, 1, 1, 1, Qt.AlignRight)
        self.addBox.addWidget(self.addWorld,    2, 1, 1, 1, Qt.AlignRight)
        self.addBox.addWidget(self.addNotes,    3, 1, 1, 1, Qt.AlignRight)
        self.addBox.addWidget(self.numChapters, 4, 1, 1, 1, Qt.AlignRight)
        self.addBox.addWidget(self.numScenes,   5, 1, 1, 1, Qt.AlignRight)
        self.addBox.setVerticalSpacing(fS)
        self.addBox.setHorizontalSpacing(cM)
        self.addBox.setContentsMargins(cM, 0, cM, 0)
        self.addBox.setColumnStretch(2, 1)
        for i in range(6):
            self.addBox.setRowMinimumHeight(i, mH)

        # Wizard Fields
        self.registerField("addPlot", self.addPlot)
        self.registerField("addChar", self.addChar)
        self.registerField("addWorld", self.addWorld)
        self.registerField("addNotes", self.addNotes)
        self.registerField("numChapters", self.numChapters)
        self.registerField("numScenes", self.numScenes)

        # Assemble
        self.outerBox = QVBoxLayout()
        self.outerBox.setSpacing(cM)
        self.outerBox.addWidget(self.theText)
        self.outerBox.addLayout(self.addBox)
        self.outerBox.addStretch(1)
        self.setLayout(self.outerBox)

        return

    ##
    #  Internal Functions
    ##

    def _syncSwitches(self):
        """Check if the add notes option should also be switched off.
        """
        addPlot = self.addPlot.isChecked()
        addChar = self.addChar.isChecked()
        addWorld = self.addWorld.isChecked()
        if not (addPlot or addChar or addWorld):
            self.addNotes.setChecked(False)
        return

# END Class ProjWizardCustomPage


class ProjWizardFinalPage(QWizardPage):

    def __init__(self, theWizard):
        super().__init__()

        self.mainConf  = novelwriter.CONFIG
        self.theWizard = theWizard

        self.setTitle(self.tr("Summary"))
        self.theText = QLabel("")
        self.theText.setWordWrap(True)

        # Assemble
        self.outerBox = QVBoxLayout()
        self.outerBox.setSpacing(self.mainConf.pxInt(12))
        self.outerBox.addWidget(self.theText)
        self.outerBox.addStretch(1)
        self.setLayout(self.outerBox)

        return

    def initializePage(self):
        """Update the summary information on the final page.
        """
        super().initializePage()

        sumList = []
        sumList.append(self.tr("Project Name: {0}").format(self.field("projName")))
        sumList.append(self.tr("Project Path: {0}").format(self.field("projPath")))

        if self.field("popMinimal"):
            sumList.append(self.tr("Fill the project with a minimal set of items"))
        elif self.field("popSample"):
            sumList.append(self.tr("Fill the project with example files"))
        elif self.field("popCustom"):
            if self.field("addPlot"):
                sumList.append(self.tr("Add a folder for plot notes"))
            if self.field("addChar"):
                sumList.append(self.tr("Add a folder for character notes"))
            if self.field("addWorld"):
                sumList.append(self.tr("Add a folder for location notes"))
            if self.field("addNotes"):
                sumList.append(self.tr("Add example notes to the above"))
            if self.field("numChapters") > 0:
                sumList.append(self.tr("Add {0} chapters to the novel folder").format(
                    self.field("numChapters")
                ))
                if self.field("numScenes") > 0:
                    sumList.append(self.tr("Add {0} scenes to each chapter").format(
                        self.field("numScenes")
                    ))
            else:
                if self.field("numScenes") > 0:
                    sumList.append(self.tr("Add {0} scenes").format(
                        self.field("numScenes")
                    ))

        self.theText.setText(
            "<p>%s</p><p>&nbsp;&bull;&nbsp;%s</p><p>%s</p>" % (
                self.tr("You have selected the following:"),
                "<br>&nbsp;&bull;&nbsp;".join(sumList),
                self.tr("Press '{0}' to create the new project.").format(
                    self.tr("Done") if self.mainConf.osDarwin else self.tr("Finish")
                )
            )
        )
        return

# END Class ProjWizardFinalPage
