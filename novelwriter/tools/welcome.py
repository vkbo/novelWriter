"""
novelWriter – GUI Welcome Dialog
================================

File History:
Created: 2023-12-14 [2.3b1] GuiWelcome

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
from datetime import datetime

from PyQt5.QtGui import QPaintEvent, QPainter, QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog, QDialogButtonBox, QHBoxLayout, QLabel, QStackedWidget,
    QTreeWidget, QVBoxLayout, QWidget
)

from novelwriter import CONFIG, SHARED, __version__, __date__

if TYPE_CHECKING:  # pragma: no cover
    from novelwriter.guimain import GuiMain

logger = logging.getLogger(__name__)


class GuiWelcome(QDialog):

    def __init__(self, mainGui: GuiMain) -> None:
        super().__init__(parent=mainGui)

        logger.debug("Create: GuiWelcome")

        self.bgImage = QPixmap(str(CONFIG.assetPath("images") / "welcome.jpg"))

        self.nwLogo = QLabel()
        self.nwLogo.setPixmap(SHARED.theme.getPixmap("novelwriter", (96, 96)))

        font = self.font()
        font.setPointSize(48)

        self.nwLabel = QLabel("novelWriter")
        self.nwLabel.setFont(font)

        self.nwInfo = QLabel(self.tr("Version {0}, Released on {1}").format(
            __version__, datetime.strptime(__date__, "%Y-%m-%d").strftime("%x")
        ))

        self.mainStack = QStackedWidget()
        self.mainStack.addWidget(_ProjectsPage(self))

        # Buttons
        # =======
        self.btnBox = QDialogButtonBox(QDialogButtonBox.Open | QDialogButtonBox.Cancel, self)

        self.newButton = self.btnBox.addButton(self.tr("New Project"), QDialogButtonBox.ActionRole)
        self.newButton.setIcon(SHARED.theme.getIcon("add"))

        self.browseButton = self.btnBox.addButton(self.tr("Browse"), QDialogButtonBox.ActionRole)
        self.browseButton.setIcon(SHARED.theme.getIcon("browse"))

        # Assemble
        # ========
        self.innerBox = QVBoxLayout()
        self.innerBox.addWidget(self.nwLabel)
        self.innerBox.addWidget(self.nwInfo)
        self.innerBox.addWidget(self.mainStack)
        self.innerBox.addWidget(self.btnBox)

        topRight = Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight

        self.outerBox = QHBoxLayout()
        self.outerBox.addWidget(self.nwLogo, 3, topRight)
        self.outerBox.addLayout(self.innerBox, 7)
        self.outerBox.setContentsMargins(24, 24, 24, 96)

        self.setLayout(self.outerBox)

        self.setMinimumSize(900, 500)

        logger.debug("Ready: GuiWelcome")

        return

    def __del__(self) -> None:  # pragma: no cover
        logger.debug("Delete: GuiWelcome")
        return

    ##
    #  Events
    ##

    def paintEvent(self, event: QPaintEvent) -> None:
        """Overload the paint event to draw the background image."""
        hWin = self.height()
        hPix = min(hWin, 700)
        tMode = Qt.TransformationMode.SmoothTransformation
        qPaint = QPainter(self)
        qPaint.drawPixmap(0, hWin - hPix, self.bgImage.scaledToHeight(hPix, tMode))
        super().paintEvent(event)
        return

# END Class GuiWelcome


class _ProjectsPage(QWidget):

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)

        self.listWidget = QTreeWidget(self)
        self.listWidget.setHeaderHidden(True)

        self.outerBox = QVBoxLayout()
        self.outerBox.addWidget(self.listWidget)
        self.outerBox.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.outerBox)

        self.updateTheme()

        return

    def updateTheme(self) -> None:
        """"""
        baseCol = self.palette().base().color()
        listStyle = (
            "QTreeWidget {{border: none; background: rgba({0},{1},{2},0.5);}}"
        ).format(baseCol.red(), baseCol.green(), baseCol.blue())
        self.listWidget.setStyleSheet(listStyle)
        return

# END Class _ProjectsPage
