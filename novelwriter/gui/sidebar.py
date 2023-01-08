"""
novelWriter – GUI Main Window SideBar
===========================================
GUI class for the main window side bar

File History:
Created: 2022-05-10 [2.0rc1]

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

import logging
import novelwriter

from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtWidgets import (
    QToolBar, QWidget, QSizePolicy, QAction, QMenu, QToolButton
)

from novelwriter.enum import nwView

logger = logging.getLogger(__name__)


class GuiSideBar(QToolBar):

    viewChangeRequested = pyqtSignal(nwView)

    def __init__(self, mainGui):
        super().__init__(parent=mainGui)

        logger.debug("Initialising GuiSideBar ...")

        self.mainConf  = novelwriter.CONFIG
        self.mainGui   = mainGui
        self.mainTheme = mainGui.mainTheme

        # Style
        iPx = self.mainConf.pxInt(22)
        mPx = self.mainConf.pxInt(60)

        lblFont = self.mainTheme.guiFont
        lblFont.setPointSizeF(0.65*self.mainTheme.fontPointSize)

        self.setMovable(False)
        self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.setIconSize(QSize(iPx, iPx))
        self.setMaximumWidth(mPx)
        self.setContentsMargins(0, 0, 0, 0)

        stretch = QWidget(self)
        stretch.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Actions
        self.aProject = QAction(self.tr("Project"), self)
        self.aProject.setFont(lblFont)
        self.aProject.setToolTip(self.tr("Project Tree View"))
        self.aProject.triggered.connect(lambda: self.viewChangeRequested.emit(nwView.PROJECT))

        self.aNovel = QAction(self.tr("Novel"), self)
        self.aNovel.setFont(lblFont)
        self.aNovel.setToolTip(self.tr("Novel Tree View"))
        self.aNovel.triggered.connect(lambda: self.viewChangeRequested.emit(nwView.NOVEL))

        self.aOutline = QAction(self.tr("Outline"), self)
        self.aOutline.setFont(lblFont)
        self.aOutline.setToolTip(self.tr("Novel Outline View"))
        self.aOutline.triggered.connect(lambda: self.viewChangeRequested.emit(nwView.OUTLINE))

        self.aBuild = QAction(self.tr("Build"), self)
        self.aBuild.setFont(lblFont)
        self.aBuild.setToolTip(self.tr("Build Novel Project"))
        self.aBuild.triggered.connect(lambda: self.mainGui.showBuildProjectDialog())

        self.aDetails = QAction(self.tr("Details"), self)
        self.aDetails.setFont(lblFont)
        self.aDetails.setToolTip(self.tr("Project Details"))
        self.aDetails.triggered.connect(lambda: self.mainGui.showProjectDetailsDialog())

        self.aStats = QAction(self.tr("Stats"), self)
        self.aStats.setFont(lblFont)
        self.aStats.setToolTip(self.tr("Writing Statistics"))
        self.aStats.triggered.connect(lambda: self.mainGui.showWritingStatsDialog())

        # Settings Menu
        self.mSettings = QMenu()

        self.mSettings.addAction(self.mainGui.mainMenu.aEditWordList)
        self.mSettings.addAction(self.mainGui.mainMenu.aProjectSettings)
        self.mSettings.addSeparator()
        self.mSettings.addAction(self.mainGui.mainMenu.aPreferences)

        self.tbSettings = QToolButton(self)
        self.tbSettings.setFont(lblFont)
        self.tbSettings.setText(self.tr("Settings"))
        self.tbSettings.setMenu(self.mSettings)
        self.tbSettings.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.tbSettings.setPopupMode(QToolButton.InstantPopup)

        # Assemble
        self.addAction(self.aProject)
        self.addAction(self.aNovel)
        self.addAction(self.aOutline)
        self.addAction(self.aBuild)
        self.addWidget(stretch)
        self.addAction(self.aDetails)
        self.addAction(self.aStats)
        self.addWidget(self.tbSettings)

        self.updateTheme()

        logger.debug("GuiSideBar initialisation complete")

        return

    def updateTheme(self):
        """Initialise GUI elements that depend on specific settings.
        """
        self.setStyleSheet("QToolBar {border: 0px;}")

        self.aProject.setIcon(self.mainTheme.getIcon("view_editor"))
        self.aNovel.setIcon(self.mainTheme.getIcon("view_novel"))
        self.aOutline.setIcon(self.mainTheme.getIcon("view_outline"))
        self.aBuild.setIcon(self.mainTheme.getIcon("view_build"))
        self.aDetails.setIcon(self.mainTheme.getIcon("proj_details"))
        self.aStats.setIcon(self.mainTheme.getIcon("proj_stats"))
        self.tbSettings.setIcon(self.mainTheme.getIcon("settings"))

        return

# END Class GuiSideBar
