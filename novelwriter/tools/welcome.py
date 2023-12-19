"""
novelWriter – GUI Welcome Dialog
================================

File History:
Created: 2023-12-14 [2.3b1] GuiWelcome

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
from __future__ import annotations

import logging

from typing import TYPE_CHECKING
from pathlib import Path
from datetime import datetime

from PyQt5.QtGui import QCloseEvent, QPaintEvent, QPainter
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import (
    QComboBox, QDialog, QDialogButtonBox, QFileDialog, QFormLayout,
    QHBoxLayout, QLabel, QLineEdit, QPushButton, QScrollArea, QSpinBox,
    QStackedWidget, QTreeWidget, QVBoxLayout, QWidget
)

from novelwriter import CONFIG, SHARED, __version__, __date__
from novelwriter.common import makeFileNameSafe
from novelwriter.constants import nwUnicode
from novelwriter.extensions.switch import NSwitch

if TYPE_CHECKING:  # pragma: no cover
    from novelwriter.guimain import GuiMain

logger = logging.getLogger(__name__)


class GuiWelcome(QDialog):

    def __init__(self, mainGui: GuiMain) -> None:
        super().__init__(parent=mainGui)

        logger.debug("Create: GuiWelcome")

        self.setWindowTitle(self.tr("Welcome"))
        self.setMinimumWidth(CONFIG.pxInt(700))
        self.setMinimumHeight(CONFIG.pxInt(400))

        hA = CONFIG.pxInt(8)
        hB = CONFIG.pxInt(16)
        hC = CONFIG.pxInt(24)
        hD = CONFIG.pxInt(36)
        hE = CONFIG.pxInt(48)
        hF = CONFIG.pxInt(96)

        self.resize(*CONFIG.welcomeWinSize)

        self.bgImage = SHARED.theme.loadDecoration("welcome")
        self.nwImage = SHARED.theme.loadDecoration("nw-text", h=hD)

        self.nwLogo = QLabel()
        self.nwLogo.setPixmap(SHARED.theme.getPixmap("novelwriter", (hF, hF)))

        self.nwLabel = QLabel("novelWriter")
        self.nwLabel.setPixmap(self.nwImage)

        self.nwInfo = QLabel(self.tr("Version {0} {1} Released on {2}").format(
            __version__, nwUnicode.U_ENDASH, datetime.strptime(__date__, "%Y-%m-%d").strftime("%x")
        ))

        self.tabOpen = _OpenProjectPage(self)
        self.tabNew = _NewProjectPage(self)
        self.tabNew.cancelNewProject.connect(self._showOpenProjectPage)

        self.mainStack = QStackedWidget()
        self.mainStack.addWidget(self.tabOpen)
        self.mainStack.addWidget(self.tabNew)

        # Buttons
        # =======
        self.btnBox = QDialogButtonBox(QDialogButtonBox.Open | QDialogButtonBox.Cancel, self)
        self.btnBox.accepted.connect(self.accept)
        self.btnBox.rejected.connect(self.close)

        self.newButton = self.btnBox.addButton(self.tr("New Project"), QDialogButtonBox.ActionRole)
        self.newButton.setIcon(SHARED.theme.getIcon("add"))
        self.newButton.clicked.connect(self._showNewProjectPage)

        self.browseButton = self.btnBox.addButton(self.tr("Browse"), QDialogButtonBox.ActionRole)
        self.browseButton.setIcon(SHARED.theme.getIcon("browse"))

        # Assemble
        # ========
        self.innerBox = QVBoxLayout()
        self.innerBox.addSpacing(hB)
        self.innerBox.addWidget(self.nwLabel)
        self.innerBox.addWidget(self.nwInfo)
        self.innerBox.addSpacing(hA)
        self.innerBox.addWidget(self.mainStack)
        self.innerBox.addSpacing(hA)
        self.innerBox.addWidget(self.btnBox)

        topRight = Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight

        self.outerBox = QHBoxLayout()
        self.outerBox.addWidget(self.nwLogo, 3, topRight)
        self.outerBox.addLayout(self.innerBox, 7)
        self.outerBox.setContentsMargins(hF, hE, hC, hE)

        self.setLayout(self.outerBox)

        logger.debug("Ready: GuiWelcome")

        return

    def __del__(self) -> None:  # pragma: no cover
        logger.debug("Delete: GuiWelcome")
        return

    ##
    #  Events
    ##

    def paintEvent(self, event: QPaintEvent) -> None:
        """Overload the paint event to draw the background image."""
        hWin = self.height()
        hPix = min(hWin, 700)
        tMode = Qt.TransformationMode.SmoothTransformation
        qPaint = QPainter(self)
        qPaint.drawPixmap(0, hWin - hPix, self.bgImage.scaledToHeight(hPix, tMode))
        super().paintEvent(event)
        return

    def closeEvent(self, event: QCloseEvent) -> None:
        """Capture the user closing the window and save settings."""
        self._saveSettings()
        event.accept()
        self.deleteLater()
        return

    ##
    #  Private Slots
    ##

    @pyqtSlot()
    def _showNewProjectPage(self) -> None:
        """Show the create new project page."""
        self.mainStack.setCurrentWidget(self.tabNew)
        return

    @pyqtSlot()
    def _showOpenProjectPage(self) -> None:
        """Show the open exiting project page."""
        self.mainStack.setCurrentWidget(self.tabOpen)
        return

    ##
    #  Internal Functions
    ##

    def _saveSettings(self) -> None:
        """Save the user GUI settings."""
        logger.debug("Saving State: GuiWelcome")
        CONFIG.setWelcomeWinSize(self.width(), self.height())
        return

# END Class GuiWelcome


class _OpenProjectPage(QWidget):

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)

        self.listWidget = QTreeWidget(self)
        self.listWidget.setHeaderHidden(True)

        self.outerBox = QVBoxLayout()
        self.outerBox.addWidget(self.listWidget)
        self.outerBox.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.outerBox)

        baseCol = self.palette().base().color()
        self.setStyleSheet((
            "QTreeWidget {{border: none; background: rgba({r},{g},{b},0.5);}}"
        ).format(r=baseCol.red(), g=baseCol.green(), b=baseCol.blue()))

        return

# END Class _OpenProjectPage


class _NewProjectPage(QWidget):

    cancelNewProject = pyqtSignal()

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)

        # Main Form
        # =========

        self.projectForm = _NewProjectForm(self)

        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidget(self.projectForm)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Controls
        # ========

        self.createButton = QPushButton(self.tr("Create Project"), self)
        self.createButton.setIcon(SHARED.theme.getIcon("star"))

        self.cancelButton = QPushButton(self.tr("Go Back"), self)
        self.cancelButton.setIcon(SHARED.theme.getIcon("backward"))
        self.cancelButton.clicked.connect(lambda: self.cancelNewProject.emit())

        self.buttonBox = QHBoxLayout()
        self.buttonBox.addStretch(1)
        self.buttonBox.addWidget(self.cancelButton, 0)
        self.buttonBox.addWidget(self.createButton, 0)

        # Assemble
        # ========

        self.outerBox = QVBoxLayout()
        self.outerBox.addWidget(self.scrollArea)
        self.outerBox.addLayout(self.buttonBox)
        self.outerBox.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.outerBox)

        # Styles
        # ======

        baseCol = self.palette().base().color()
        self.setStyleSheet((
            "QScrollArea {{border: none; background: rgba({r},{g},{b},0.5);}} "
            "_NewProjectForm {{border: none; background: rgba({r},{g},{b},0.5);}} "
        ).format(r=baseCol.red(), g=baseCol.green(), b=baseCol.blue()))

        return

# END Class _NewProjectPage


class _NewProjectForm(QWidget):

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)

        self._basePath = CONFIG.lastPath()

        # Project Settings
        # ================

        self.projName = QLineEdit()
        self.projName.setMaxLength(200)
        self.projName.setPlaceholderText(self.tr("Required"))
        self.projName.textChanged.connect(self._updateProjPath)

        self.projAuthor = QLineEdit()
        self.projAuthor.setMaxLength(200)
        self.projAuthor.setPlaceholderText(self.tr("Optional"))

        self.projLang = QComboBox(self)
        for tag, language in CONFIG.listLanguages(CONFIG.LANG_PROJ):
            self.projLang.addItem(language, tag)

        langIdx = self.projLang.findData(CONFIG.guiLocale)
        if langIdx == -1:
            langIdx = self.projLang.findData("en_GB")
        if langIdx != -1:
            self.projLang.setCurrentIndex(langIdx)

        self.projPath = QLineEdit("", self)
        self.projPath.setReadOnly(True)
        self.projPath.setPlaceholderText(self.tr("Required"))

        self.browsePath = QPushButton(self)
        self.browsePath.setIcon(SHARED.theme.getIcon("browse"))
        self.browsePath.clicked.connect(self._doBrowse)

        self.pathBox = QHBoxLayout()
        self.pathBox.addWidget(self.projPath)
        self.pathBox.addWidget(self.browsePath)

        self.projectForm = QFormLayout()
        self.projectForm.addRow(self.tr("Project Name"), self.projName)
        self.projectForm.addRow(self.tr("Author(s)"), self.projAuthor)
        self.projectForm.addRow(self.tr("Language"), self.projLang)
        self.projectForm.addRow(self.tr("Project Path"), self.pathBox)

        # Chapters and Scenes
        # ===================

        self.numChapters = QSpinBox()
        self.numChapters.setRange(0, 200)
        self.numChapters.setValue(5)
        self.numChapters.setToolTip(self.tr("Set to 0 to only add scenes"))

        self.chapterBox = QHBoxLayout()
        self.chapterBox.addWidget(QLabel(self.tr("Add")))
        self.chapterBox.addWidget(self.numChapters)
        self.chapterBox.addWidget(QLabel(self.tr("chapter documents")))
        self.chapterBox.addStretch(1)

        self.numScenes = QSpinBox()
        self.numScenes.setRange(0, 200)
        self.numScenes.setValue(5)

        self.sceneBox = QHBoxLayout()
        self.sceneBox.addWidget(QLabel(self.tr("Add")))
        self.sceneBox.addWidget(self.numScenes)
        self.sceneBox.addWidget(QLabel(self.tr("scene documents (to each chapter)")))
        self.sceneBox.addStretch(1)

        self.novelForm = QVBoxLayout()
        self.novelForm.addLayout(self.chapterBox)
        self.novelForm.addLayout(self.sceneBox)

        # Project Notes
        # =============

        self.addPlot = NSwitch(self)
        self.addPlot.setChecked(True)
        self.addPlot.clicked.connect(self._syncSwitches)

        self.addChar = NSwitch(self)
        self.addChar.setChecked(True)
        self.addChar.clicked.connect(self._syncSwitches)

        self.addWorld = NSwitch(self)
        self.addWorld.setChecked(False)
        self.addWorld.clicked.connect(self._syncSwitches)

        self.addNotes = NSwitch()
        self.addNotes.setChecked(False)

        self.notesForm = QFormLayout()
        self.notesForm.addRow(self.tr("Add a folder for plot notes"), self.addPlot)
        self.notesForm.addRow(self.tr("Add a folder for character notes"), self.addChar)
        self.notesForm.addRow(self.tr("Add a folder for location notes"), self.addWorld)
        self.notesForm.addRow(self.tr("Add example notes to the above"), self.addNotes)

        # Assemble
        # ========

        self.formBox = QVBoxLayout()
        self.formBox.addLayout(self.projectForm)
        self.formBox.addSpacing(16)
        self.formBox.addWidget(QLabel("<b>{0}</b>".format(self.tr("Chapters and Scenes"))))
        self.formBox.addLayout(self.novelForm)
        self.formBox.addSpacing(16)
        self.formBox.addWidget(QLabel("<b>{0}</b>".format(self.tr("Project Notes"))))
        self.formBox.addLayout(self.notesForm)
        self.formBox.addStretch(1)

        self.setLayout(self.formBox)

        self._updateProjPath()

        return

    ##
    #  Private Slots
    ##

    @pyqtSlot()
    def _doBrowse(self) -> None:
        """Select a project folder."""
        if projDir := QFileDialog.getExistingDirectory(
            self, self.tr("Select Project Folder"),
            str(self._basePath), options=QFileDialog.ShowDirsOnly
        ):
            self._basePath = Path(projDir)
            self._updateProjPath()
            CONFIG.setLastPath(self._basePath)
        return

    @pyqtSlot()
    def _updateProjPath(self) -> None:
        """Update the path box to show the full project path."""
        projName = makeFileNameSafe(self.projName.text().strip())
        self.projPath.setText(str(self._basePath / projName))
        return

    @pyqtSlot()
    def _syncSwitches(self):
        """Check if the add notes option should also be switched off."""
        addPlot = self.addPlot.isChecked()
        addChar = self.addChar.isChecked()
        addWorld = self.addWorld.isChecked()
        if not (addPlot or addChar or addWorld):
            self.addNotes.setChecked(False)
        return

# END Class _NewProjectForm
