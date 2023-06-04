"""
novelWriter – GUI Build Manuscript
==================================

File History:
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
    QAbstractButton, QDialog, QDialogButtonBox, QFrame, QGridLayout,
    QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem, QProgressBar,
    QPushButton, QSplitter, QVBoxLayout, QWidget
)

from novelwriter import CONFIG
from novelwriter.common import makeFileNameSafe
from novelwriter.constants import nwLabels
from novelwriter.core.buildsettings import BuildSettings
from novelwriter.extensions.switchbox import NSwitchBox

if TYPE_CHECKING:
    from novelwriter.guimain import GuiMain

logger = logging.getLogger(__name__)


class GuiManuscriptBuild(QDialog):
    """GUI Tools: Manucript Builder Dialog

    This is the tool for running the build itself. It can be accessed
    independently of the Manuscript Build Tool.
    """

    def __init__(self, parent: QWidget, mainGui: GuiMain, build: BuildSettings):
        super().__init__(parent=parent)

        logger.debug("Create: GuiManuscriptBuild")
        self.setObjectName("GuiManuscriptBuild")

        self.mainGui    = mainGui
        self.mainTheme  = mainGui.mainTheme
        self.theProject = mainGui.theProject

        self._parent = parent
        self._build = build

        self.setWindowTitle(self.tr("Build Manuscript"))
        self.setMinimumWidth(CONFIG.pxInt(500))
        self.setMinimumHeight(CONFIG.pxInt(250))

        wWin = CONFIG.pxInt(660)
        hWin = CONFIG.pxInt(350)

        pOptions = self.theProject.options
        self.resize(
            CONFIG.pxInt(pOptions.getInt("GuiManuscriptBuild", "winWidth", wWin)),
            CONFIG.pxInt(pOptions.getInt("GuiManuscriptBuild", "winHeight", hWin))
        )

        # Formats
        # =======

        self.lblFormat = QLabel("<b>{0}</b>".format(self.tr("Build Format")))
        self.listFormats = QListWidget()
        current = None
        for key, (_, label) in nwLabels.BUILD_FORMATS.items():
            item = QListWidgetItem()
            item.setText(label)
            item.setData(Qt.UserRole, key)
            self.listFormats.addItem(item)
            if key == self._build.lastFormat:
                current = item
        if current:
            self.listFormats.setCurrentItem(current)

        self.formatBox = QVBoxLayout()
        self.formatBox.addWidget(self.lblFormat, 0)
        self.formatBox.addWidget(self.listFormats, 1)
        self.formatBox.setContentsMargins(0, 0, 0, 0)

        self.formatWidget = QWidget()
        self.formatWidget.setLayout(self.formatBox)
        self.formatWidget.setContentsMargins(0, 0, 0, 0)

        # Build Controls
        # ==============

        # Build Options
        self.swtOptions = NSwitchBox(self, self.mainTheme.baseIconSize)
        self.swtOptions.switchToggled.connect(self._applyBuildOptions)
        self.swtOptions.setFrameStyle(QFrame.NoFrame)
        self.swtOptions.setInnerContentsMargins(0, 0, 0, 0)

        self.swtOptions.addLabel(self._build.getLabel("build"))
        self.swtOptions.addItem(
            self.mainTheme.getIcon("cls_novel"), self._build.getLabel("build.splitNovel"),
            "build.splitNovel", default=self._build.getBool("build.splitNovel")
        )
        self.swtOptions.addItem(
            self.mainTheme.getIcon("cls_custom"), self._build.getLabel("build.splitNotes"),
            "build.splitNotes", default=self._build.getBool("build.splitNotes")
        )
        self.swtOptions.addItem(
            self.mainTheme.getIcon("proj_chapter"), self._build.getLabel("build.splitChapters"),
            "build.splitChapters", default=self._build.getBool("build.splitChapters")
        )

        # Dialog Controls
        # ===============

        # Build Path
        self.lblPath = QLabel(self.tr("Build Folder"))
        self.buildPath = QLineEdit()
        self.buildPath.setText(str(self._build.lastPath))
        self.btnBrowse = QPushButton(self.mainTheme.getIcon("browse"), "")

        self.pathBox = QHBoxLayout()
        self.pathBox.addWidget(self.buildPath)
        self.pathBox.addWidget(self.btnBrowse)

        # Build Name
        self.lblName = QLabel(self.tr("Build Name"))
        self.buildName = QLineEdit()
        self.btnReset = QPushButton(self.mainTheme.getIcon("revert"), "")
        self.btnReset.setToolTip(self.tr("Reset Build Name to default"))
        self.btnReset.clicked.connect(self._doResetBuildName)

        self.nameBox = QHBoxLayout()
        self.nameBox.addWidget(self.buildName)
        self.nameBox.addWidget(self.btnReset)

        # Build Progress
        self.lblProgress = QLabel(self.tr("Build Progress"))
        self.buildProgress = QProgressBar()

        # Dialog Buttons
        self.dlgButtons = QDialogButtonBox(QDialogButtonBox.Close)
        self.dlgButtons.addButton(
            QPushButton(self.mainTheme.getIcon("export"), self.tr("&Build")),
            QDialogButtonBox.ActionRole
        )
        self.dlgButtons.clicked.connect(self._dialogButtonClicked)

        # Assemble GUI
        # ============

        self.mainSplit = QSplitter()
        self.mainSplit.addWidget(self.formatWidget)
        self.mainSplit.addWidget(self.swtOptions)
        self.mainSplit.setHandleWidth(CONFIG.pxInt(16))
        self.mainSplit.setCollapsible(0, False)
        self.mainSplit.setCollapsible(1, False)
        self.mainSplit.setSizes([
            CONFIG.pxInt(pOptions.getInt("GuiManuscriptBuild", "fmtWidth", int(0.45*wWin))),
            CONFIG.pxInt(pOptions.getInt("GuiManuscriptBuild", "optsWidth", int(0.55*wWin))),
        ])

        self.outerBox = QGridLayout()
        self.outerBox.addWidget(self.mainSplit,     0, 0, 1, 2)
        self.outerBox.addWidget(self.lblPath,       1, 0, 1, 1)
        self.outerBox.addLayout(self.pathBox,       1, 1, 1, 1)
        self.outerBox.addWidget(self.lblName,       2, 0, 1, 1)
        self.outerBox.addLayout(self.nameBox,       2, 1, 1, 1)
        self.outerBox.addWidget(self.lblProgress,   3, 0, 1, 1)
        self.outerBox.addWidget(self.buildProgress, 3, 1, 1, 1)
        self.outerBox.addWidget(self.dlgButtons,    4, 0, 1, 2)

        self.setLayout(self.outerBox)

        if self._build.lastBuildName:
            self.buildName.setText(makeFileNameSafe(self._build.lastBuildName))
        else:
            self._doResetBuildName()

        logger.debug("Ready: GuiManuscriptBuild")

        return

    def __del__(self):
        """For debug use only."""
        logger.debug("Delete: GuiManuscriptBuild")
        return

    ##
    #  Events
    ##

    def closeEvent(self, event):
        """Capture the user closing the window so we can save GUI
        settings.
        """
        self._saveSettings()
        event.accept()
        self.deleteLater()
        return

    ##
    #  Private Slots
    ##

    @pyqtSlot(str, bool)
    def _applyBuildOptions(self, key: str, state: bool):
        """Set the build options for the build."""
        self._build.setValue(key, state)
        return

    @pyqtSlot("QAbstractButton*")
    def _dialogButtonClicked(self, button: QAbstractButton):
        """Handle button clicks from the dialog button box."""
        role = self.dlgButtons.buttonRole(button)
        if role == QDialogButtonBox.ActionRole:
            self._runBuild()
        elif role == QDialogButtonBox.RejectRole:
            self.close()
        return

    @pyqtSlot()
    def _doResetBuildName(self):
        """Generate a default build name."""
        bName = makeFileNameSafe(f"{self.theProject.data.name} - {self._build.name}")
        self.buildName.setText(bName)
        self._build.setLastBuildName(bName)
        return

    ##
    #  Internal Functions
    ##

    def _runBuild(self) -> bool:
        """Run the currently selected build."""
        bFormat = self._getSelectedFormat()
        if not bFormat:
            return False

        bPath = self.buildPath.text()
        bName = self.buildName.text()

        self._build.setLastFormat(bFormat)
        self._build.setLastPath(bPath)
        self._build.setLastBuildName(bName)

        return True

    def _getSelectedFormat(self) -> str | None:
        """Get the currently selected format."""
        items = self.listFormats.selectedItems()
        if items and isinstance(items[0], QListWidgetItem):
            return str(items[0].data(Qt.UserRole))
        return None

    def _saveSettings(self):
        """Save the user GUI settings."""
        logger.debug("Saving GuiManuscriptBuild settings")

        winWidth  = CONFIG.rpxInt(self.width())
        winHeight = CONFIG.rpxInt(self.height())

        mainSplit = self.mainSplit.sizes()
        fmtWidth  = CONFIG.rpxInt(mainSplit[0])
        optsWidth = CONFIG.rpxInt(mainSplit[1])

        pOptions = self.theProject.options
        pOptions.setValue("GuiManuscriptBuild", "winWidth", winWidth)
        pOptions.setValue("GuiManuscriptBuild", "winHeight", winHeight)
        pOptions.setValue("GuiManuscriptBuild", "fmtWidth", fmtWidth)
        pOptions.setValue("GuiManuscriptBuild", "optsWidth", optsWidth)
        pOptions.saveSettings()

        return

# END Class GuiManuscriptBuild
