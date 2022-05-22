"""
novelWriter – GUI Main Window Views ToolBar
===========================================
GUI class for the main window "Views" toolbar

File History:
Created: 2022-05-10 [1.7b1]

This file is a part of novelWriter
Copyright 2018–2022, Veronica Berglyd Olsen

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


class GuiViewsBar(QToolBar):

    viewChangeRequested = pyqtSignal(nwView)

    def __init__(self, theParent):
        QToolBar.__init__(self, theParent)

        logger.debug("Initialising GuiViewsBar ...")

        self.mainConf  = novelwriter.CONFIG
        self.theParent = theParent
        self.theTheme  = theParent.theTheme

        # Style
        iPx = self.mainConf.pxInt(22)
        mPx = self.mainConf.pxInt(60)

        lblFont = self.theTheme.guiFont
        lblFont.setPointSizeF(0.65*self.theTheme.fontPointSize)
        self.setFont(lblFont)

        self.setMovable(False)
        self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.setIconSize(QSize(iPx, iPx))
        self.setMaximumWidth(mPx)
        self.setContentsMargins(0, 0, 0, 0)

        stretch = QWidget(self)
        stretch.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Actions
        self.aProject = QAction(self.tr("Project"))
        self.aProject.setIcon(self.theTheme.getIcon("view_editor"))
        self.aProject.triggered.connect(lambda: self.viewChangeRequested.emit(nwView.PROJECT))

        self.aNovel = QAction(self.tr("Novel"))
        self.aNovel.setIcon(self.theTheme.getIcon("view_novel"))
        self.aNovel.triggered.connect(lambda: self.viewChangeRequested.emit(nwView.NOVEL))

        self.aOutline = QAction(self.tr("Outline"))
        self.aOutline.setIcon(self.theTheme.getIcon("view_outline"))
        self.aOutline.triggered.connect(lambda: self.viewChangeRequested.emit(nwView.OUTLINE))

        self.aBuild = QAction(self.tr("Build"))
        self.aBuild.setIcon(self.theTheme.getIcon("view_build"))
        self.aBuild.triggered.connect(lambda: self.theParent.showBuildProjectDialog())

        self.aDetails = QAction(self.tr("Details"))
        self.aDetails.setIcon(self.theTheme.getIcon("proj_details"))
        self.aDetails.triggered.connect(lambda: self.theParent.showProjectDetailsDialog())

        self.aStats = QAction(self.tr("Stats"))
        self.aStats.setIcon(self.theTheme.getIcon("proj_stats"))
        self.aStats.triggered.connect(lambda: self.theParent.showWritingStatsDialog())

        # Settings Menu
        self.mSettings = QMenu()

        self.aPrjSettings = QAction(self.tr("Project Settings"))
        self.aPrjSettings.triggered.connect(lambda: self.theParent.showProjectSettingsDialog())
        self.mSettings.addAction(self.aPrjSettings)

        self.aPreferences = QAction(self.tr("Preferences"))
        self.aPreferences.triggered.connect(lambda: self.theParent.showPreferencesDialog())
        self.mSettings.addAction(self.aPreferences)

        self.tbSettings = QToolButton(self)
        self.tbSettings.setIcon(self.theTheme.getIcon("settings"))
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

        logger.debug("GuiViewsBar initialisation complete")

        return

# END Class GuiViewsBar
