"""
novelWriter – GUI Document Viewer Panel
=======================================

File History:
Created: 2023-11-09 [2.2a1] GuiDocViewerPanel

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

from PyQt5.QtWidgets import QVBoxLayout, QWidget

from novelwriter.gui.docviewer import GuiDocViewer

logger = logging.getLogger(__name__)


class GuiDocViewerPanel(QWidget):

    def __init__(self, docViewer: GuiDocViewer) -> None:
        super().__init__(parent=docViewer)

        logger.debug("Create: GuiDocViewerPanel")

        self.panelHeader = GuiDocViewerPanelHeader(self)

        # Assemble
        self.outerBox = QVBoxLayout()
        self.outerBox.addWidget(self.panelHeader)
        self.outerBox.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.outerBox)

        logger.debug("Ready: GuiDocViewerPanel")

        return

# END Class GuiDocViewerPanel


class GuiDocViewerPanelHeader(QWidget):

    def __init__(self, docViewerPanel: GuiDocViewerPanel) -> None:
        super().__init__(parent=docViewerPanel)
        return

# END Class GuiDocViewerPanelHeader
