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
from pathlib import Path

from PyQt5.QtCore import QSize, QTimer, Qt, pyqtSlot
from PyQt5.QtWidgets import (
    QAbstractButton, QAbstractItemView, QDialog, QDialogButtonBox, QFileDialog,
    QGridLayout, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QPushButton, QSplitter, QVBoxLayout, QWidget
)

from novelwriter import CONFIG
from novelwriter.enum import nwAlert, nwBuildFmt
from novelwriter.common import makeFileNameSafe
from novelwriter.constants import nwLabels
from novelwriter.core.item import NWItem
from novelwriter.core.docbuild import NWBuildDocument
from novelwriter.core.buildsettings import BuildSettings
from novelwriter.extensions.simpleprogress import NProgressSimple

if TYPE_CHECKING:  # pragma: no cover
    from novelwriter.guimain import GuiMain

logger = logging.getLogger(__name__)


class GuiManuscriptBuild(QDialog):
    """GUI Tools: Manuscript Build Dialog

    This is the tool for running the build itself. It can be accessed
    independently of the Manuscript Build Tool.
    """

    D_KEY = Qt.ItemDataRole.UserRole

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
        self.setMinimumHeight(CONFIG.pxInt(300))

        iPx = self.mainTheme.baseIconSize
        sp4 = CONFIG.pxInt(4)
        sp8 = CONFIG.pxInt(8)
        sp16 = CONFIG.pxInt(16)
        wWin = CONFIG.pxInt(620)
        hWin = CONFIG.pxInt(360)

        pOptions = self.theProject.options
        self.resize(
            CONFIG.pxInt(pOptions.getInt("GuiManuscriptBuild", "winWidth", wWin)),
            CONFIG.pxInt(pOptions.getInt("GuiManuscriptBuild", "winHeight", hWin))
        )

        # Output Format
        # =============

        self.lblFormat = QLabel(self.tr("Output Format"))
        self.listFormats = QListWidget()
        self.listFormats.setIconSize(QSize(iPx, iPx))
        current = None
        for key in nwBuildFmt:
            item = QListWidgetItem()
            item.setText(nwLabels.BUILD_FMT[key])
            item.setData(self.D_KEY, key)
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

        # Table of Contents
        # =================

        self.lblContent = QLabel(self.tr("Table of Contents"))

        self.listContent = QListWidget(self)
        self.listContent.setIconSize(QSize(iPx, iPx))
        self.listContent.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)

        self.contentBox = QVBoxLayout()
        self.contentBox.addWidget(self.lblContent, 0)
        self.contentBox.addWidget(self.listContent, 0)
        self.contentBox.setContentsMargins(0, 0, 0, 0)

        self.contentWidget = QWidget()
        self.contentWidget.setLayout(self.contentBox)
        self.contentWidget.setContentsMargins(0, 0, 0, 0)

        # Dialog Controls
        # ===============

        font = self.font()
        font.setBold(True)
        font.setUnderline(True)
        font.setPointSizeF(1.5*font.pointSizeF())

        self.lblMain = QLabel(self._build.name)
        self.lblMain.setWordWrap(True)
        self.lblMain.setFont(font)

        # Build Path
        self.lblPath = QLabel(self.tr("Path"))
        self.buildPath = QLineEdit(self)
        self.btnBrowse = QPushButton(self.mainTheme.getIcon("browse"), "")

        self.pathBox = QHBoxLayout()
        self.pathBox.addWidget(self.buildPath)
        self.pathBox.addWidget(self.btnBrowse)
        self.pathBox.setSpacing(sp8)

        # Build Name
        self.lblName = QLabel(self.tr("File Name"))
        self.buildName = QLineEdit(self)
        self.btnReset = QPushButton(self.mainTheme.getIcon("revert"), "")
        self.btnReset.setToolTip(self.tr("Reset file name to default"))

        self.nameBox = QHBoxLayout()
        self.nameBox.addWidget(self.buildName)
        self.nameBox.addWidget(self.btnReset)
        self.nameBox.setSpacing(sp8)

        # Build Progress
        self.buildProgress = NProgressSimple(self)
        self.buildProgress.setMinimum(0)
        self.buildProgress.setValue(0)
        self.buildProgress.setTextVisible(False)
        self.buildProgress.setFixedHeight(sp8)

        # Build Box
        self.buildBox = QGridLayout()
        self.buildBox.addWidget(self.lblPath, 0, 0)
        self.buildBox.addLayout(self.pathBox, 0, 1)
        self.buildBox.addWidget(self.lblName, 1, 0)
        self.buildBox.addLayout(self.nameBox, 1, 1)
        self.buildBox.setHorizontalSpacing(sp8)
        self.buildBox.setVerticalSpacing(sp4)

        # Dialog Buttons
        self.btnBuild = QPushButton(self.mainTheme.getIcon("export"), self.tr("&Build"))
        self.dlgButtons = QDialogButtonBox(QDialogButtonBox.Close)
        self.dlgButtons.addButton(self.btnBuild, QDialogButtonBox.ActionRole)

        # Assemble GUI
        # ============

        self.mainSplit = QSplitter()
        self.mainSplit.addWidget(self.formatWidget)
        self.mainSplit.addWidget(self.contentWidget)
        self.mainSplit.setHandleWidth(sp16)
        self.mainSplit.setCollapsible(0, False)
        self.mainSplit.setCollapsible(1, False)
        self.mainSplit.setStretchFactor(0, 0)
        self.mainSplit.setStretchFactor(1, 1)
        self.mainSplit.setSizes([
            CONFIG.pxInt(pOptions.getInt("GuiManuscriptBuild", "fmtWidth", wWin//2)),
            CONFIG.pxInt(pOptions.getInt("GuiManuscriptBuild", "sumWidth", wWin//2)),
        ])

        self.outerBox = QVBoxLayout()
        self.outerBox.addWidget(self.lblMain, 0, Qt.AlignCenter)
        self.outerBox.addSpacing(sp16)
        self.outerBox.addWidget(self.mainSplit, 1)
        self.outerBox.addSpacing(sp4)
        self.outerBox.addWidget(self.buildProgress, 0)
        self.outerBox.addSpacing(sp4)
        self.outerBox.addLayout(self.buildBox, 0)
        self.outerBox.addSpacing(sp16)
        self.outerBox.addWidget(self.dlgButtons, 0)
        self.outerBox.setSpacing(0)

        self.setLayout(self.outerBox)

        self.btnBuild.setFocus()
        self._populateContentList()
        self.buildPath.setText(str(self._build.lastPath))
        if self._build.lastBuildName:
            self.buildName.setText(self._build.lastBuildName)
        else:
            self._doResetBuildName()

        # Signals
        self.btnReset.clicked.connect(self._doResetBuildName)
        self.btnBrowse.clicked.connect(self._doSelectPath)
        self.dlgButtons.clicked.connect(self._dialogButtonClicked)
        self.listFormats.itemSelectionChanged.connect(self._resetProgress)

        logger.debug("Ready: GuiManuscriptBuild")

        return

    def __del__(self):  # pragma: no cover
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
    def _doSelectPath(self):
        """Select a folder for output."""
        bPath = Path(self.buildPath.text())
        bPath = bPath if bPath.is_dir() else self._build.lastPath
        savePath = QFileDialog.getExistingDirectory(
            self, self.tr("Select Folder"), str(bPath)
        )
        if savePath:
            self.buildPath.setText(savePath)
        return

    @pyqtSlot()
    def _doResetBuildName(self):
        """Generate a default build name."""
        bName = f"{self.theProject.data.name} - {self._build.name}"
        self.buildName.setText(bName)
        self._build.setLastBuildName(bName)
        return

    @pyqtSlot()
    def _resetProgress(self):
        """Set the progress bar back to 0."""
        self.buildProgress.setValue(0)
        return

    ##
    #  Internal Functions
    ##

    def _runBuild(self) -> bool:
        """Run the currently selected build."""
        bFormat = self._getSelectedFormat()
        if not isinstance(bFormat, nwBuildFmt):
            return False

        bName = self.buildName.text().strip()
        if not bName:
            self._doResetBuildName()
            bName = self.buildName.text().strip()

        self.buildProgress.setValue(0)
        bPath = Path(self.buildPath.text())
        if not bPath.is_dir():
            self.mainGui.makeAlert(self.tr("Output folder does not exist."), nwAlert.ERROR)
            return False

        bExt = nwLabels.BUILD_EXT[bFormat]
        buildPath = (bPath / makeFileNameSafe(bName)).with_suffix(bExt)

        if buildPath.exists():
            if not self.mainGui.askQuestion(
                self.tr("File Exists"),
                self.tr("The file already exists. Do you want to overwrite it?")
            ):
                return False

        docBuild = NWBuildDocument(self.theProject, self._build)
        docBuild.queueAll()

        self.buildProgress.setMaximum(len(docBuild))
        for i, _ in docBuild.iterBuild(buildPath, bFormat):
            self.buildProgress.setValue(i+1)

        self._build.setLastPath(bPath)
        self._build.setLastBuildName(bName)
        self._build.setLastFormat(bFormat)

        QTimer.singleShot(1000, self._resetProgress)

        return True

    def _getSelectedFormat(self) -> nwBuildFmt | None:
        """Get the currently selected format."""
        items = self.listFormats.selectedItems()
        if items and isinstance(items[0], QListWidgetItem):
            return items[0].data(self.D_KEY)
        return None

    def _saveSettings(self):
        """Save the user GUI settings."""
        logger.debug("Saving GuiManuscriptBuild settings")

        winWidth  = CONFIG.rpxInt(self.width())
        winHeight = CONFIG.rpxInt(self.height())

        mainSplit = self.mainSplit.sizes()
        fmtWidth = CONFIG.rpxInt(mainSplit[0])
        sumWidth = CONFIG.rpxInt(mainSplit[1])

        pOptions = self.theProject.options
        pOptions.setValue("GuiManuscriptBuild", "winWidth", winWidth)
        pOptions.setValue("GuiManuscriptBuild", "winHeight", winHeight)
        pOptions.setValue("GuiManuscriptBuild", "fmtWidth", fmtWidth)
        pOptions.setValue("GuiManuscriptBuild", "sumWidth", sumWidth)
        pOptions.saveSettings()

        return

    def _populateContentList(self):
        """Build the content list."""
        rootMap = {}
        filtered = self._build.buildItemFilter(self.theProject)
        self.listContent.clear()
        for nwItem in self.theProject.tree:
            tHandle = nwItem.itemHandle
            rHandle = nwItem.itemRoot

            if tHandle is None or rHandle is None or not nwItem.isFileType():
                continue

            if filtered.get(tHandle, (False, 0))[0]:
                if rHandle not in rootMap:
                    rItem = self.theProject.tree[rHandle]
                    if isinstance(rItem, NWItem):
                        rootMap[rHandle] = rItem.itemName

                itemIcon = self.mainTheme.getItemIcon(
                    nwItem.itemType, nwItem.itemClass,
                    nwItem.itemLayout, nwItem.mainHeading
                )
                rootName = rootMap.get(rHandle, "??????")
                item = QListWidgetItem(f"{rootName}: {nwItem.itemName}")
                item.setIcon(itemIcon)
                self.listContent.addItem(item)

        return

# END Class GuiManuscriptBuild
