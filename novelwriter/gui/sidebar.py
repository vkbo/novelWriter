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

from PyQt5.QtGui import QPalette
from PyQt5.QtCore import QEvent, QPoint, Qt, QSize, pyqtSignal
from PyQt5.QtWidgets import QMenu, QToolButton, QVBoxLayout, QWidget

from novelwriter import CONFIG, SHARED
from novelwriter.enum import nwView
from novelwriter.extensions.eventfilters import StatusTipFilter

if TYPE_CHECKING:  # pragma: no cover
    from novelwriter.guimain import GuiMain

logger = logging.getLogger(__name__)


class GuiSideBar(QWidget):

    viewChangeRequested = pyqtSignal(nwView)

    def __init__(self, mainGui: GuiMain) -> None:
        super().__init__(parent=mainGui)

        logger.debug("Create: GuiSideBar")

        self.mainGui = mainGui

        iPx = CONFIG.pxInt(24)
        iconSize = QSize(iPx, iPx)
        self.setContentsMargins(0, 0, 0, 0)
        self.installEventFilter(StatusTipFilter(mainGui))

        # Buttons
        self.tbProject = QToolButton(self)
        self.tbProject.setToolTip("{0} [Ctrl+T]".format(self.tr("Project Tree View")))
        self.tbProject.setIconSize(iconSize)
        self.tbProject.clicked.connect(lambda: self.viewChangeRequested.emit(nwView.PROJECT))

        self.tbNovel = QToolButton(self)
        self.tbNovel.setToolTip("{0} [Ctrl+T]".format(self.tr("Novel Tree View")))
        self.tbNovel.setIconSize(iconSize)
        self.tbNovel.clicked.connect(lambda: self.viewChangeRequested.emit(nwView.NOVEL))

        self.tbOutline = QToolButton(self)
        self.tbOutline.setToolTip("{0} [Ctrl+Shift+T]".format(self.tr("Novel Outline View")))
        self.tbOutline.setIconSize(iconSize)
        self.tbOutline.clicked.connect(lambda: self.viewChangeRequested.emit(nwView.OUTLINE))

        self.tbBuild = QToolButton(self)
        self.tbBuild.setToolTip("{0} [F5]".format(self.tr("Build Manuscript")))
        self.tbBuild.setIconSize(iconSize)
        self.tbBuild.clicked.connect(self.mainGui.showBuildManuscriptDialog)

        self.tbDetails = QToolButton(self)
        self.tbDetails.setToolTip("{0} [Shift+F6]".format(self.tr("Novel Details")))
        self.tbDetails.setIconSize(iconSize)
        self.tbDetails.clicked.connect(self.mainGui.showNovelDetailsDialog)

        self.tbStats = QToolButton(self)
        self.tbStats.setToolTip("{0} [F6]".format(self.tr("Writing Statistics")))
        self.tbStats.setIconSize(iconSize)
        self.tbStats.clicked.connect(self.mainGui.showWritingStatsDialog)

        # Settings Menu
        self.tbSettings = QToolButton(self)
        self.tbSettings.setToolTip(self.tr("Settings"))
        self.tbSettings.setIconSize(iconSize)
        self.tbSettings.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)

        self.mSettings = _PopRightMenu(self.tbSettings)
        self.mSettings.addAction(self.mainGui.mainMenu.aEditWordList)
        self.mSettings.addAction(self.mainGui.mainMenu.aProjectSettings)
        self.mSettings.addSeparator()
        self.mSettings.addAction(self.mainGui.mainMenu.aPreferences)

        self.tbSettings.setMenu(self.mSettings)
        self.tbSettings.setPopupMode(QToolButton.InstantPopup)

        # Assemble
        self.outerBox = QVBoxLayout()
        self.outerBox.addWidget(self.tbProject)
        self.outerBox.addWidget(self.tbNovel)
        self.outerBox.addWidget(self.tbOutline)
        self.outerBox.addWidget(self.tbBuild)
        self.outerBox.addStretch(1)
        self.outerBox.addWidget(self.tbDetails)
        self.outerBox.addWidget(self.tbStats)
        self.outerBox.addWidget(self.tbSettings)
        self.outerBox.setContentsMargins(0, 0, 0, 0)
        self.outerBox.setSpacing(CONFIG.pxInt(4))

        self.setLayout(self.outerBox)
        self.updateTheme()

        logger.debug("Ready: GuiSideBar")

        return

    def updateTheme(self) -> None:
        """Initialise GUI elements that depend on specific settings."""
        qPalette = self.palette()
        qPalette.setBrush(QPalette.Window, qPalette.base())
        self.setPalette(qPalette)

        fadeCol = qPalette.text().color()
        buttonStyle = (
            "QToolButton {{padding: {0}px; border: none; background: transparent;}} "
            "QToolButton:hover {{border: none; background: rgba({1},{2},{3},0.2);}}"
        ).format(CONFIG.pxInt(6), fadeCol.red(), fadeCol.green(), fadeCol.blue())
        buttonStyleMenu = f"{buttonStyle} QToolButton::menu-indicator {{image: none;}}"

        self.tbProject.setIcon(SHARED.theme.getIcon("view_editor"))
        self.tbProject.setStyleSheet(buttonStyle)

        self.tbNovel.setIcon(SHARED.theme.getIcon("view_novel"))
        self.tbNovel.setStyleSheet(buttonStyle)

        self.tbOutline.setIcon(SHARED.theme.getIcon("view_outline"))
        self.tbOutline.setStyleSheet(buttonStyle)

        self.tbBuild.setIcon(SHARED.theme.getIcon("view_build"))
        self.tbBuild.setStyleSheet(buttonStyle)

        self.tbDetails.setIcon(SHARED.theme.getIcon("proj_details"))
        self.tbDetails.setStyleSheet(buttonStyle)

        self.tbStats.setIcon(SHARED.theme.getIcon("proj_stats"))
        self.tbStats.setStyleSheet(buttonStyle)

        self.tbSettings.setIcon(SHARED.theme.getIcon("settings"))
        self.tbSettings.setStyleSheet(buttonStyleMenu)

        return

# END Class GuiSideBar


class _PopRightMenu(QMenu):

    def event(self, event: QEvent) -> bool:
        """Overload the show event and move the menu popup location."""
        if event.type() == QEvent.Show:
            if isinstance(parent := self.parent(), QWidget):
                offset = QPoint(parent.width(), parent.height() - self.height())
                self.move(parent.mapToGlobal(offset))
        return super(_PopRightMenu, self).event(event)

# END Class _PopRightMenu
