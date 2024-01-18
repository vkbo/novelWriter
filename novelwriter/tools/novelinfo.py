"""
novelWriter – GUI Novel Info
============================

File History:
Created: 2024-01-18 [2.3b1] GuiNovelInfo

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
from PyQt5.QtWidgets import QDialog, QWidget

logger = logging.getLogger(__name__)


class GuiNovelInfo(QDialog):

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)

        logger.debug("Create: GuiNovelInfo")
        self.setObjectName("GuiNovelInfo")

        self.setWindowTitle(self.tr("Novel Info"))
        logger.debug("Ready: GuiNovelInfo")

        return

    def __del__(self) -> None:  # pragma: no cover
        logger.debug("Delete: GuiNovelInfo")
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
        logger.debug("Saving State: GuiNovelInfo")
        return

# END Class GuiNovelInfo
