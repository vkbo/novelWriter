"""
novelWriter – GUI Build Manuscript
==================================
GUI classes for the Manuscript Build Tool

File History:
Created: 2023-05-13 [2.1b1] GuiManuscript
Created: 2023-05-13 [2.1b1] GuiManuscriptPreview
Created: 2023-05-24 [2.1b1] GuiManuscriptBuild

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

from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import (
    QDialog, QHBoxLayout, QListWidget, QListWidgetItem, QMenu, QProgressBar,
    QPushButton, QSplitter, QTextBrowser, QVBoxLayout, QWidget, qApp
)

from novelwriter import CONFIG
from novelwriter.core.buildsettings import BuildCollection, BuildSettings
from novelwriter.tools.manussettings import GuiBuildSettings

if TYPE_CHECKING:
    from novelwriter.guimain import GuiMain

logger = logging.getLogger(__name__)


class GuiManuscript(QDialog):

    def __init__(self, mainGui: GuiMain):
        super().__init__(parent=mainGui)

        logger.debug("Initialising GuiManuscript ...")
        self.setObjectName("GuiManuscript")

        self.mainGui    = mainGui
        self.mainTheme  = mainGui.mainTheme
        self.theProject = mainGui.theProject

        self._builds = BuildCollection(self.theProject)
        self._buildMap = {}

        self.setWindowTitle(self.tr("Build Manuscript"))
        self.setMinimumWidth(CONFIG.pxInt(600))
        self.setMinimumHeight(CONFIG.pxInt(500))

        wWin = CONFIG.pxInt(900)
        hWin = CONFIG.pxInt(600)

        pOptions = self.theProject.options
        self.resize(
            CONFIG.pxInt(pOptions.getInt("GuiManuscript", "winWidth", wWin)),
            CONFIG.pxInt(pOptions.getInt("GuiManuscript", "winHeight", hWin))
        )

        # Build Controls
        # ==============

        self.buildList = QListWidget()

        self.btnNew = QPushButton(self.tr("New"))
        self.btnNew.clicked.connect(self._createNewBuild)

        self.btnEdit = QPushButton(self.tr("Edit"))
        self.btnEdit.clicked.connect(self._editSelectedBuild)

        self.btnDelete = QPushButton(self.tr("Delete"))

        # Process Controls
        # ================

        self.buildProgress = QProgressBar()
        self.btnPreview = QPushButton(self.tr("Build Preview"))
        self.manPreview = GuiManuscriptPreview(self)

        self.menuPrint = QMenu(self)
        self.aPrintSend = self.menuPrint.addAction(self.tr("Print Preview"))
        self.aPrintFile = self.menuPrint.addAction(self.tr("Print to PDF"))

        self.menuSave = QMenu(self)
        self.aSaveODT = self.menuSave.addAction(self.tr("Open Document (.odt)"))
        self.aSaveFODT = self.menuSave.addAction(self.tr("Flat Open Document (.fodt)"))
        self.aSaveHTM = self.menuSave.addAction(self.tr("novelWriter HTML (.htm)"))
        self.aSaveNWD = self.menuSave.addAction(self.tr("novelWriter Markdown (.nwd)"))
        self.aSaveMD = self.menuSave.addAction(self.tr("Standard Markdown (.md)"))
        self.aSaveGH = self.menuSave.addAction(self.tr("GitHub Markdown (.md)"))
        self.aSaveJsonH = self.menuSave.addAction(self.tr("JSON + novelWriter HTML (.json)"))
        self.aSaveJsonM = self.menuSave.addAction(self.tr("JSON + novelWriter Markdown (.json)"))

        self.btnPrint = QPushButton(self.tr("Print"))
        self.btnPrint.setMenu(self.menuPrint)

        self.btnSave = QPushButton(self.tr("Save As"))
        self.btnSave.setMenu(self.menuSave)

        self.btnClose = QPushButton(self.tr("Close"))
        self.btnClose.clicked.connect(self._doClose)

        # Assemble GUI
        # ============

        self.buildBox = QHBoxLayout()
        self.buildBox.addWidget(self.btnNew)
        self.buildBox.addWidget(self.btnEdit)
        self.buildBox.addWidget(self.btnDelete)

        self.processBox = QHBoxLayout()
        self.processBox.addWidget(self.btnSave)
        self.processBox.addWidget(self.btnPrint)
        self.processBox.addWidget(self.btnClose)

        self.controlBox = QVBoxLayout()
        self.controlBox.addWidget(self.buildList)
        self.controlBox.addLayout(self.buildBox)
        self.controlBox.addWidget(self.buildProgress)
        self.controlBox.addWidget(self.btnPreview)
        self.controlBox.addLayout(self.processBox)
        self.controlBox.setContentsMargins(0, 0, 0, 0)

        self.optsWidget = QWidget()
        self.optsWidget.setLayout(self.controlBox)

        self.mainSplit = QSplitter()
        self.mainSplit.addWidget(self.optsWidget)
        self.mainSplit.addWidget(self.manPreview)
        self.mainSplit.setSizes([
            CONFIG.pxInt(pOptions.getInt("GuiManuscript", "optsWidth", wWin//3)),
            CONFIG.pxInt(pOptions.getInt("GuiManuscript", "viewWidth", 2*wWin//3)),
        ])

        self.outerBox = QVBoxLayout()
        self.outerBox.addWidget(self.mainSplit)

        self.setLayout(self.outerBox)

        logger.debug("GuiManuscript initialisation complete")

        return

    def loadContent(self):
        """Load dialog content from project data.
        """
        self._builds.loadCollection()
        self._updateBuildsList()
        return

    ##
    #  Events
    ##

    def closeEvent(self, event):
        """Capture the user closing the window so we can save settings.
        """
        self._beforeClose()
        event.accept()
        return

    ##
    #  Private Slots
    ##

    @pyqtSlot()
    def _createNewBuild(self):
        """Open the build settings dialog for a new build.
        """
        build = BuildSettings()
        build.setName(self.tr("My Manuscript"))
        self._openSettingsDialog(build)
        return

    @pyqtSlot()
    def _editSelectedBuild(self):
        """Edit the currently selected build settings entry.
        """
        bItems = self.buildList.selectedItems()
        if bItems:
            build = self._builds.getBuild(bItems[0].data(Qt.UserRole))
            if isinstance(build, BuildSettings):
                self._openSettingsDialog(build)
        return

    @pyqtSlot(BuildSettings)
    def _processNewSettings(self, build: BuildSettings):
        """Process new build settings from the settings dialog.
        """
        self._builds.setBuild(build)
        self._builds.saveCollection()
        self._updateBuildItem(build)
        return

    @pyqtSlot()
    def _doClose(self):
        """The close button has been clicked.
        """
        self._beforeClose()
        self.close()
        return

    ##
    #  Internal Functions
    ##

    def _saveManuscript(self, outFormat: int):
        """Save the manuscript file or files.
        """
        return

    def _beforeClose(self):
        """List of things to do before closing.
        """
        self._saveSettings()
        for qWidget in qApp.topLevelWidgets():
            if qWidget.objectName() == "GuiBuildSettings":
                qWidget.close()
        return

    def _saveSettings(self):
        """Save the various user settings.
        """
        logger.debug("Saving GuiManuscript settings")

        winWidth  = CONFIG.rpxInt(self.width())
        winHeight = CONFIG.rpxInt(self.height())

        mainSplit = self.mainSplit.sizes()
        optsWidth = mainSplit[0]
        viewWidth = mainSplit[1]

        pOptions = self.theProject.options
        pOptions.setValue("GuiManuscript", "winWidth", winWidth)
        pOptions.setValue("GuiManuscript", "winHeight", winHeight)
        pOptions.setValue("GuiManuscript", "optsWidth", optsWidth)
        pOptions.setValue("GuiManuscript", "viewWidth", viewWidth)
        pOptions.saveSettings()

        return

    def _openSettingsDialog(self, build: BuildSettings):
        """Open a new build settings dialog.
        """
        dlgSettings = GuiBuildSettings(self.mainGui, build)
        dlgSettings.setModal(False)
        dlgSettings.show()
        dlgSettings.raise_()
        qApp.processEvents()
        dlgSettings.loadContent()
        dlgSettings.newSettingsReady.connect(self._processNewSettings)
        return

    def _updateBuildsList(self):
        """Update the list of available builds.
        """
        self.buildList.clear()
        for key, name in self._builds.builds():
            bItem = QListWidgetItem()
            bItem.setText(name)
            bItem.setData(Qt.UserRole, key)
            self.buildList.addItem(bItem)
            self._buildMap[key] = bItem
        return

    def _updateBuildItem(self, build: BuildSettings):
        """Update the entry of a specific build item.
        """
        bItem = self._buildMap.get(build.buildID, None)
        if isinstance(bItem, QListWidgetItem):
            bItem.setText(build.name)
        else:  # Propbably a new item
            self._updateBuildsList()
        return

# END Class GuiManuscript


class GuiManuscriptPreview(QTextBrowser):

    def __init__(self, mainGui):
        super().__init__(parent=mainGui)

        self.mainGui    = mainGui
        self.mainTheme  = mainGui.mainTheme
        self.theProject = mainGui.theProject

        return

# END Class GuiManuscriptPreview


class GuiManuscriptBuild(QDialog):

    def __init__(self, parent):
        super().__init__(parent=parent)
        self._manusGui = parent

        return

# END Class GuiManuscriptBuild
