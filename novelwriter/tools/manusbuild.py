"""
novelWriter – GUI Build Manuscript
==================================
GUI classes for the Manuscript Build Tool

File History:
Created: 2023-05-24 [2.1b1]

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

from PyQt5.QtWidgets import QDialog, QWidget

logger = logging.getLogger(__name__)


class GuiManuscriptBuild(QDialog):

    def __init__(self, parent: QWidget):
        super().__init__(parent=parent)

        logger.debug("Create: GuiManuscriptBuild")
        self.setObjectName("GuiManuscriptBuild")

        self._parent = parent

        logger.debug("Ready: GuiManuscriptBuild")

        return

    def __del__(self):
        logger.debug("Delete: GuiManuscriptBuild")
        return

# END Class GuiManuscriptBuild
