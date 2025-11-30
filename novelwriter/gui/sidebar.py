"""
novelWriter – GUI Main Window SideBar
=====================================

File History:
Created: 2022-05-10 [2.0rc1] GuiSideBar

This file is a part of novelWriter
Copyright (C) 2022 Veronica Berglyd Olsen and novelWriter contributors

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
"""  # noqa
from __future__ import annotations

import logging

from typing import TYPE_CHECKING

from PyQt6.QtCore import QEvent, QPoint, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QMenu, QVBoxLayout, QWidget

from novelwriter import CONFIG, SHARED
from novelwriter.common import qtLambda
from novelwriter.constants import nwLabels, trConst
from novelwriter.enum import nwTheme, nwView
from novelwriter.extensions.eventfilters import StatusTipFilter
from novelwriter.extensions.modified import NIconToolButton
from novelwriter.gui.theme import STYLES_BIG_TOOLBUTTON

if TYPE_CHECKING:
    from novelwriter.guimain import GuiMain

logger = logging.getLogger(__name__)


class GuiSideBar(QWidget):
    """GUI: Main Window SideBar."""

    requestViewChange = pyqtSignal(nwView)

    def __init__(self, mainGui: GuiMain) -> None:
        super().__init__(parent=mainGui)

        logger.debug("Create: GuiSideBar")

        self.mainGui = mainGui

        iSz = SHARED.theme.sidebarIconSize

        self.setContentsMargins(0, 0, 0, 0)
        self.installEventFilter(StatusTipFilter(self.mainGui))

        # Buttons
        self.tbProject = NIconToolButton(self, iSz)
        self.tbProject.setToolTip("{0} [Ctrl+T]".format(self.tr("Project Tree View")))
        self.tbProject.clicked.connect(qtLambda(self.requestViewChange.emit, nwView.PROJECT))

        self.tbNovel = NIconToolButton(self, iSz)
        self.tbNovel.setToolTip("{0} [Ctrl+T]".format(self.tr("Novel Tree View")))
        self.tbNovel.clicked.connect(qtLambda(self.requestViewChange.emit, nwView.NOVEL))

        self.tbSearch = NIconToolButton(self, iSz)
        self.tbSearch.setToolTip("{0} [Ctrl+Shift+F]".format(self.tr("Project Search")))
        self.tbSearch.clicked.connect(qtLambda(self.requestViewChange.emit, nwView.SEARCH))

        self.tbOutline = NIconToolButton(self, iSz)
        self.tbOutline.setToolTip("{0} [Ctrl+Shift+T]".format(self.tr("Novel Outline View")))
        self.tbOutline.clicked.connect(qtLambda(self.requestViewChange.emit, nwView.OUTLINE))

        self.tbTheme = NIconToolButton(self, iSz)
        self.tbTheme.setToolTip(self.tr("Switch Colour Theme"))
        self.tbTheme.clicked.connect(self._cycleColurTheme)

        self.tbDetails = NIconToolButton(self, iSz)
        self.tbDetails.setToolTip("{0} [Shift+F6]".format(self.tr("Novel Details")))
        self.tbDetails.clicked.connect(self.mainGui.showNovelDetailsDialog)

        self.tbStats = NIconToolButton(self, iSz)
        self.tbStats.setToolTip("{0} [F6]".format(self.tr("Writing Statistics")))
        self.tbStats.clicked.connect(self.mainGui.showWritingStatsDialog)

        self.tbBuild = NIconToolButton(self, iSz)
        self.tbBuild.setToolTip("{0} [F5]".format(self.tr("Build Manuscript")))
        self.tbBuild.clicked.connect(self.mainGui.showBuildManuscriptDialog)

        # Settings Menu
        self.tbSettings = NIconToolButton(self, iSz)
        self.tbSettings.setToolTip(self.tr("Settings"))

        self.mSettings = _PopRightMenu(self.tbSettings)
        self.mSettings.addAction(self.mainGui.mainMenu.aEditWordList)
        self.mSettings.addAction(self.mainGui.mainMenu.aProjectSettings)
        self.mSettings.addSeparator()
        self.mSettings.addAction(self.mainGui.mainMenu.aPreferences)

        self.tbSettings.setMenu(self.mSettings)

        # Assemble
        self.outerBox = QVBoxLayout()
        self.outerBox.addWidget(self.tbProject)
        self.outerBox.addWidget(self.tbNovel)
        self.outerBox.addWidget(self.tbSearch)
        self.outerBox.addWidget(self.tbOutline)
        self.outerBox.addWidget(self.tbBuild)
        self.outerBox.addStretch(1)
        self.outerBox.addWidget(self.tbDetails)
        self.outerBox.addWidget(self.tbStats)
        self.outerBox.addWidget(self.tbTheme)
        self.outerBox.addWidget(self.tbSettings)
        self.outerBox.setContentsMargins(0, 0, 0, 0)
        self.outerBox.setSpacing(6)

        self.setLayout(self.outerBox)
        self.updateTheme()

        logger.debug("Ready: GuiSideBar")

    def updateTheme(self) -> None:
        """Initialise GUI elements that depend on specific settings."""
        logger.debug("Theme Update: GuiSideBar")

        buttonStyle = SHARED.theme.getStyleSheet(STYLES_BIG_TOOLBUTTON)
        self.tbProject.setStyleSheet(buttonStyle)
        self.tbNovel.setStyleSheet(buttonStyle)
        self.tbSearch.setStyleSheet(buttonStyle)
        self.tbOutline.setStyleSheet(buttonStyle)
        self.tbBuild.setStyleSheet(buttonStyle)
        self.tbDetails.setStyleSheet(buttonStyle)
        self.tbStats.setStyleSheet(buttonStyle)
        self.tbTheme.setStyleSheet(buttonStyle)
        self.tbSettings.setStyleSheet(buttonStyle)

        self.tbProject.setThemeIcon("sb_project", "sidebar")
        self.tbNovel.setThemeIcon("sb_novel", "sidebar")
        self.tbSearch.setThemeIcon("sb_search", "sidebar")
        self.tbOutline.setThemeIcon("sb_outline", "sidebar")
        self.tbBuild.setThemeIcon("sb_build", "sidebar")
        self.tbDetails.setThemeIcon("sb_details", "sidebar")
        self.tbStats.setThemeIcon("sb_stats", "sidebar")
        self.tbSettings.setThemeIcon("settings", "sidebar")

        self._setThemeModeIcon()

    ##
    #  Private Slots
    ##

    @pyqtSlot()
    def _cycleColurTheme(self) -> None:
        """Go to nex colour theme."""
        match CONFIG.themeMode:
            case nwTheme.AUTO:
                CONFIG.themeMode = nwTheme.LIGHT
            case nwTheme.LIGHT:
                CONFIG.themeMode = nwTheme.DARK
            case nwTheme.DARK:
                CONFIG.themeMode = nwTheme.AUTO
        self.mainGui.checkThemeUpdate()
        self._setThemeModeIcon()

    ##
    #  Internal Functions
    ##

    def _setThemeModeIcon(self) -> None:
        """Set the theme button icon."""
        self.tbTheme.setThemeIcon(nwLabels.THEME_MODE_ICON[CONFIG.themeMode], "sidebar")
        self.tbTheme.setToolTip(trConst(nwLabels.THEME_MODE_LABEL[CONFIG.themeMode]))


class _PopRightMenu(QMenu):

    def event(self, event: QEvent) -> bool:
        """Overload the show event and move the menu popup location."""
        if event.type() == QEvent.Type.Show:
            if isinstance(parent := self.parent(), QWidget):
                offset = QPoint(parent.width(), parent.height() - self.height())
                self.move(parent.mapToGlobal(offset))
        return super().event(event)
