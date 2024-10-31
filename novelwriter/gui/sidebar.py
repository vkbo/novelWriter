"""
novelWriter – GUI Main Window SideBar
=====================================

File History:
Created: 2022-05-10 [2.0rc1] GuiSideBar

This file is a part of novelWriter
Copyright 2018–2024, Veronica Berglyd Olsen

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

from PyQt5.QtCore import QEvent, QPoint, QSize, pyqtSignal
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QMenu, QVBoxLayout, QWidget

from novelwriter import CONFIG, SHARED
from novelwriter.common import qtLambda
from novelwriter.enum import nwView
from novelwriter.extensions.eventfilters import StatusTipFilter
from novelwriter.extensions.modified import NIconToolButton
from novelwriter.gui.theme import STYLES_BIG_TOOLBUTTON

if TYPE_CHECKING:  # pragma: no cover
    from novelwriter.guimain import GuiMain

logger = logging.getLogger(__name__)


class GuiSideBar(QWidget):

    requestViewChange = pyqtSignal(nwView)

    def __init__(self, mainGui: GuiMain) -> None:
        super().__init__(parent=mainGui)

        logger.debug("Create: GuiSideBar")

        self.mainGui = mainGui

        iPx = int(1.25*SHARED.theme.baseButtonHeight)
        iSz = QSize(iPx, iPx)

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

        self.tbBuild = NIconToolButton(self, iSz)
        self.tbBuild.setToolTip("{0} [F5]".format(self.tr("Build Manuscript")))
        self.tbBuild.clicked.connect(self.mainGui.showBuildManuscriptDialog)

        self.tbDetails = NIconToolButton(self, iSz)
        self.tbDetails.setToolTip("{0} [Shift+F6]".format(self.tr("Novel Details")))
        self.tbDetails.clicked.connect(self.mainGui.showNovelDetailsDialog)

        self.tbStats = NIconToolButton(self, iSz)
        self.tbStats.setToolTip("{0} [F6]".format(self.tr("Writing Statistics")))
        self.tbStats.clicked.connect(self.mainGui.showWritingStatsDialog)

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
        self.outerBox.addWidget(self.tbSettings)
        self.outerBox.setContentsMargins(0, 0, 0, 0)
        self.outerBox.setSpacing(CONFIG.pxInt(6))

        self.setLayout(self.outerBox)
        self.updateTheme()

        logger.debug("Ready: GuiSideBar")

        return

    def updateTheme(self) -> None:
        """Initialise GUI elements that depend on specific settings."""
        qPalette = self.palette()
        qPalette.setBrush(QPalette.ColorRole.Window, qPalette.base())
        self.setPalette(qPalette)

        buttonStyle = SHARED.theme.getStyleSheet(STYLES_BIG_TOOLBUTTON)

        self.tbProject.setStyleSheet(buttonStyle)
        self.tbNovel.setStyleSheet(buttonStyle)
        self.tbSearch.setStyleSheet(buttonStyle)
        self.tbOutline.setStyleSheet(buttonStyle)
        self.tbBuild.setStyleSheet(buttonStyle)
        self.tbDetails.setStyleSheet(buttonStyle)
        self.tbStats.setStyleSheet(buttonStyle)
        self.tbSettings.setStyleSheet(buttonStyle)

        self.tbProject.setThemeIcon("view_editor")
        self.tbNovel.setThemeIcon("view_novel")
        self.tbSearch.setThemeIcon("view_search")
        self.tbOutline.setThemeIcon("view_outline")
        self.tbBuild.setThemeIcon("view_build")
        self.tbDetails.setThemeIcon("proj_details")
        self.tbStats.setThemeIcon("proj_stats")
        self.tbSettings.setThemeIcon("settings")

        return


class _PopRightMenu(QMenu):

    def event(self, event: QEvent) -> bool:
        """Overload the show event and move the menu popup location."""
        if event.type() == QEvent.Type.Show:
            if isinstance(parent := self.parent(), QWidget):
                offset = QPoint(parent.width(), parent.height() - self.height())
                self.move(parent.mapToGlobal(offset))
        return super(_PopRightMenu, self).event(event)
