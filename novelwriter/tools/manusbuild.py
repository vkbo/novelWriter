"""
novelWriter – GUI Build Manuscript
==================================
GUI classes for the Manuscript Build Tool

File History:
Created: 2023-05-13 [2.1b1]

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
    QDialog, QHBoxLayout, QListWidget, QListWidgetItem, QPushButton, QSplitter,
    QTextBrowser, QVBoxLayout, QWidget, qApp
)

from novelwriter import CONFIG
from novelwriter.core.buildsettings import BuildCollection, BuildSettings
from novelwriter.tools.manussettings import GuiBuildSettings

if TYPE_CHECKING:
    from novelwriter.guimain import GuiMain

logger = logging.getLogger(__name__)


class GuiBuildManuscript(QDialog):

    def __init__(self, mainGui: GuiMain):
        super().__init__(parent=mainGui)

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
            CONFIG.pxInt(pOptions.getInt("GuiBuildManuscript", "winWidth", wWin)),
            CONFIG.pxInt(pOptions.getInt("GuiBuildManuscript", "winHeight", hWin))
        )

        # Controls
        # ========

        self.buildList = QListWidget()

        self.btnNew = QPushButton(self.tr("New"))
        self.btnNew.clicked.connect(self._createNewBuild)

        self.btnEdit = QPushButton(self.tr("Edit"))
        self.btnEdit.clicked.connect(self._editSelectedBuild)

        self.btnDel = QPushButton(self.tr("Delete"))

        self.buttonBox = QHBoxLayout()
        self.buttonBox.addWidget(self.btnNew)
        self.buttonBox.addWidget(self.btnEdit)
        self.buttonBox.addWidget(self.btnDel)

        self.manPreview = GuiManuscriptPreview(self)

        # Assemble GUI
        # ============

        self.controlBox = QVBoxLayout()
        self.controlBox.addWidget(self.buildList)
        self.controlBox.addLayout(self.buttonBox)

        self.optsWidget = QWidget()
        self.optsWidget.setLayout(self.controlBox)

        self.mainSplit = QSplitter()
        self.mainSplit.addWidget(self.optsWidget)
        self.mainSplit.addWidget(self.manPreview)
        self.mainSplit.setSizes([
            CONFIG.pxInt(pOptions.getInt("GuiBuildManuscript", "optsWidth", wWin//3)),
            CONFIG.pxInt(pOptions.getInt("GuiBuildManuscript", "viewWidth", 2*wWin//3)),
        ])

        self.outerBox = QVBoxLayout()
        self.outerBox.addWidget(self.mainSplit)

        self.setLayout(self.outerBox)

        return

    def loadContent(self):
        """
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
        self._saveSettings()
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

    ##
    #  Internal Functions
    ##

    def _saveSettings(self):
        """Save the various user settings.
        """
        logger.debug("Saving GuiBuildManuscript settings")

        winWidth  = CONFIG.rpxInt(self.width())
        winHeight = CONFIG.rpxInt(self.height())

        mainSplit = self.mainSplit.sizes()
        optsWidth = mainSplit[0]
        viewWidth = mainSplit[1]

        pOptions = self.theProject.options
        pOptions.setValue("GuiBuildManuscript", "winWidth", winWidth)
        pOptions.setValue("GuiBuildManuscript", "winHeight", winHeight)
        pOptions.setValue("GuiBuildManuscript", "optsWidth", optsWidth)
        pOptions.setValue("GuiBuildManuscript", "viewWidth", viewWidth)
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

# END Class GuiBuildManuscript


class GuiManuscriptPreview(QTextBrowser):

    def __init__(self, mainGui):
        super().__init__(parent=mainGui)

        self.mainGui    = mainGui
        self.mainTheme  = mainGui.mainTheme
        self.theProject = mainGui.theProject

        return

# END Class GuiManuscriptPreview
