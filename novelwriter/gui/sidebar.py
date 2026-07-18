"""
novelWriter – GUI Main Window Side Bar
======================================

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
from novelwriter.common import qtWeakLambda
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
        self.tbProject = NIconToolButton(self, iSz, "sb_project:sidebar")
        self.tbProject.setToolTip("{0} [Ctrl+T]".format(self.tr("Project Tree View")))
        self.tbProject.clicked.connect(qtWeakLambda(self._emitViewChange, nwView.PROJECT))

        self.tbNovel = NIconToolButton(self, iSz, "sb_novel:sidebar")
        self.tbNovel.setToolTip("{0} [Ctrl+T]".format(self.tr("Novel Tree View")))
        self.tbNovel.clicked.connect(qtWeakLambda(self._emitViewChange, nwView.NOVEL))

        self.tbSearch = NIconToolButton(self, iSz, "sb_search:sidebar")
        self.tbSearch.setToolTip("{0} [Ctrl+Shift+F]".format(self.tr("Project Search")))
        self.tbSearch.clicked.connect(qtWeakLambda(self._emitViewChange, nwView.SEARCH))

        self.tbOutline = NIconToolButton(self, iSz, "sb_outline:sidebar")
        self.tbOutline.setToolTip("{0} [Ctrl+Shift+T]".format(self.tr("Novel Outline View")))
        self.tbOutline.clicked.connect(qtWeakLambda(self._emitViewChange, nwView.OUTLINE))

        self.tbTheme = NIconToolButton(self, iSz)
        self.tbTheme.setToolTip(self.tr("Switch Colour Theme"))
        self.tbTheme.clicked.connect(self._cycleColorTheme)

        self.tbDetails = NIconToolButton(self, iSz, "sb_details:sidebar")
        self.tbDetails.setToolTip("{0} [Shift+F6]".format(self.tr("Novel Details")))
        self.tbDetails.clicked.connect(self.mainGui.showNovelDetailsDialog)

        self.tbStats = NIconToolButton(self, iSz, "sb_stats:sidebar")
        self.tbStats.setToolTip("{0} [F6]".format(self.tr("Writing Statistics")))
        self.tbStats.clicked.connect(self.mainGui.showWritingStatsDialog)

        self.tbBuild = NIconToolButton(self, iSz, "sb_build:sidebar")
        self.tbBuild.setToolTip("{0} [F5]".format(self.tr("Manuscript Build")))
        self.tbBuild.clicked.connect(self.mainGui.showBuildManuscriptDialog)

        # Settings Menu
        self.tbSettings = NIconToolButton(self, iSz, "settings:sidebar")
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
        self.updateTheme(init=True)

        logger.debug("Ready: GuiSideBar")

    def updateTheme(self, *, init: bool = False) -> None:
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

        if not init:
            self.tbProject.refreshTheme()
            self.tbNovel.refreshTheme()
            self.tbSearch.refreshTheme()
            self.tbOutline.refreshTheme()
            self.tbBuild.refreshTheme()
            self.tbDetails.refreshTheme()
            self.tbStats.refreshTheme()
            self.tbTheme.refreshTheme()
            self.tbSettings.refreshTheme()

        self._setThemeModeIcon()

    ##
    #  Private Slots
    ##

    @pyqtSlot()
    def _cycleColorTheme(self) -> None:
        """Go to next colour theme."""
        match CONFIG.themeMode:
            case nwTheme.AUTO:
                CONFIG.themeMode = nwTheme.LIGHT
            case nwTheme.LIGHT:
                CONFIG.themeMode = nwTheme.DARK
            case nwTheme.DARK:
                CONFIG.themeMode = nwTheme.AUTO
            case _:  # pragma: no cover
                pass
        self.mainGui.refreshColorTheme()
        self._setThemeModeIcon()

    @pyqtSlot(nwView)
    def _emitViewChange(self, view: nwView) -> None:
        """Forward a view change request."""
        self.requestViewChange.emit(view)

    ##
    #  Internal Functions
    ##

    def _setThemeModeIcon(self) -> None:
        """Set the theme button icon."""
        self.tbTheme.setThemeIcon(nwLabels.THEME_MODE_ICON[CONFIG.themeMode])
        self.tbTheme.setToolTip(trConst(nwLabels.THEME_MODE_LABEL[CONFIG.themeMode]))


class _PopRightMenu(QMenu):
    def event(self, event: QEvent) -> bool:
        """Overload the show event and move the menu popup location."""
        if event.type() == QEvent.Type.Show and isinstance(parent := self.parent(), QWidget):
            offset = QPoint(parent.width(), parent.height() - self.height())
            self.move(parent.mapToGlobal(offset))
        return super().event(event)
