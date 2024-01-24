"""
novelWriter – GUI Novel Info
============================

File History:
Created: 2024-01-18 [2.3b1] GuiNovelDetails

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

from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import (
    QDialog, QDialogButtonBox, QHBoxLayout, QStackedWidget, QVBoxLayout,
    QWidget
)

from novelwriter import CONFIG, SHARED
from novelwriter.extensions.configlayout import NColourLabel
from novelwriter.extensions.novelselector import NovelSelector
from novelwriter.extensions.pagedsidebar import NPagedSideBar

logger = logging.getLogger(__name__)


class GuiNovelDetails(QDialog):

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)

        logger.debug("Create: GuiNovelDetails")
        self.setObjectName("GuiNovelDetails")
        self.setWindowTitle(self.tr("Novel Details"))
        self.setMinimumSize(CONFIG.pxInt(600), CONFIG.pxInt(500))

        # Title
        self.titleLabel = NColourLabel(
            self.tr("Novel Details"), SHARED.theme.helpText, parent=self, scale=1.25
        )
        self.titleLabel.setIndent(CONFIG.pxInt(4))

        # Novel Selector
        self.novelSelector = NovelSelector(self)
        self.novelSelector.refreshNovelList()

        # SideBar
        self.sidebar = NPagedSideBar(self)
        self.sidebar.setLabelColor(SHARED.theme.helpText)
        # self.sidebar.buttonClicked.connect(self._sidebarClicked)

        # Content
        self.mainStack = QStackedWidget(self)

        # Buttons
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        self.buttonBox.rejected.connect(self.close)

        # Assemble
        self.topBox = QHBoxLayout()
        self.topBox.addWidget(self.titleLabel)
        self.topBox.addStretch(1)
        self.topBox.addWidget(self.novelSelector, 1)

        self.mainBox = QHBoxLayout()
        self.mainBox.addWidget(self.sidebar)
        self.mainBox.addWidget(self.mainStack)
        self.mainBox.setContentsMargins(0, 0, 0, 0)

        self.outerBox = QVBoxLayout()
        self.outerBox.addLayout(self.topBox)
        self.outerBox.addLayout(self.mainBox)
        self.outerBox.addWidget(self.buttonBox)
        self.outerBox.setSpacing(CONFIG.pxInt(8))

        self.setLayout(self.outerBox)
        self.setSizeGripEnabled(True)

        logger.debug("Ready: GuiNovelDetails")

        return

    def __del__(self) -> None:  # pragma: no cover
        logger.debug("Delete: GuiNovelDetails")
        return

    ##
    #  Events
    ##

    def closeEvent(self, event: QCloseEvent) -> None:
        """Capture the user closing the window and save settings."""
        self._saveSettings()
        event.accept()
        self.deleteLater()
        return

    ##
    #  Internal Functions
    ##

    def _saveSettings(self) -> None:
        """Save the user GUI settings."""
        logger.debug("Saving State: GuiNovelDetails")
        return

# END Class GuiNovelDetails
