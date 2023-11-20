"""
novelWriter – GUI Dictionary Downloader
=======================================

File History:
Created: 2023-11-19 [2.2rc1]

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

from pathlib import Path

from PyQt5.QtGui import QCloseEvent
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import (
    QDialog, QDialogButtonBox, QVBoxLayout, QWidget
)

from novelwriter import CONFIG

logger = logging.getLogger(__name__)


class GuiDictionaries(QDialog):

    C_CODE  = 0
    C_NAME  = 1
    C_STATE = 2

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)

        logger.debug("Create: GuiDictionaries")
        self.setObjectName("GuiDictionaries")
        self.setWindowTitle(self.tr("Add Dictionaries"))

        sPx = CONFIG.pxInt(16)

        self.setMinimumWidth(CONFIG.pxInt(500))
        self.setMinimumHeight(CONFIG.pxInt(200))

        # Buttons
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Close)
        self.buttonBox.rejected.connect(self._doClose)

        # Assemble
        self.outerBox = QVBoxLayout()
        self.outerBox.addWidget(self.buttonBox)
        self.outerBox.setSpacing(sPx)

        self.setLayout(self.outerBox)

        logger.debug("Ready: GuiDictionaries")

        return

    def __del__(self) -> None:  # pragma: no cover
        logger.debug("Delete: GuiDictionaries")
        return

    def initDialog(self) -> bool:
        """Prepare and check that we can proceed."""
        try:
            import enchant
            path = Path(enchant.get_user_config_dir())
        except Exception:
            logger.error("Could not get enchant path")
            return False

        if path.is_dir():
            pass

        return True

    ##
    #  Events
    ##

    def closeEvent(self, event: QCloseEvent) -> None:
        """Capture the user closing the window."""
        event.accept()
        self.deleteLater()
        return

    ##
    #  Private Slots
    ##

    @pyqtSlot()
    def _doClose(self) -> None:
        """Close the dialog."""
        self.close()
        return

# END Class GuiDictionaries
