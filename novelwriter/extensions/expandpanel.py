"""
novelWriter – Custom Widget: Expandable Panel
=============================================

This file is a part of novelWriter
Copyright (C) 2026 Veronica Berglyd Olsen and novelWriter contributors

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

from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QHBoxLayout, QLayout, QVBoxLayout, QWidget

from novelwriter import SHARED
from novelwriter.extensions.modified import NClickableLabel, NIconToggleButton


class NExpandablePanel(QWidget):
    """Custom Widget: Expandable Panel.

    A panel that can be expanded or collapsed by clicking on its header.
    The header contains a title and an optional icon, and the content
    area can contain any widget.
    """

    expandedStateChanged = pyqtSignal(bool)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._ep_expanded = True
        self._ep_widget = QWidget(self)

        self._ep_toggle = NIconToggleButton(self, SHARED.theme.baseIconSize, "unfold", "default")
        self._ep_toggle.setChecked(self._ep_expanded)
        self._ep_toggle.toggled.connect(self._toggleExpanded)

        self._ep_label = NClickableLabel("Unnamed", self)
        self._ep_label.setFont(SHARED.theme.guiFontB)
        self._ep_label.mouseClicked.connect(self._ep_toggle.click)

        self._ep_header = QHBoxLayout()
        self._ep_header.setContentsMargins(0, 0, 0, 0)
        self._ep_header.addWidget(self._ep_toggle)
        self._ep_header.addWidget(self._ep_label)
        self._ep_header.setSpacing(2)

        self._ep_layout = QVBoxLayout()
        self._ep_layout.setContentsMargins(0, 0, 0, 0)
        self._ep_layout.addLayout(self._ep_header)
        self._ep_layout.addWidget(self._ep_widget)

        self.setLayout(self._ep_layout)

    ##
    #  Setters
    ##

    def setTitle(self, title: str) -> None:
        """Set the title of the panel."""
        self._ep_label.setText(title)

    def setExpanded(self, expanded: bool) -> None:
        """Set the expanded state of the panel."""
        self._ep_toggle.setChecked(expanded)

    def setContentLayout(self, layout: QLayout) -> None:
        """Set the content layout of the panel."""
        self._ep_widget.setLayout(layout)

    ##
    #  Methods
    ##

    def isExpanded(self) -> bool:
        """Return the expanded state of the panel."""
        return self._ep_expanded

    def updateTheme(self) -> None:
        """Update the theme of the panel."""
        self._ep_toggle.refreshTheme()

    ##
    #  Private Slots
    ##

    @pyqtSlot(bool)
    def _toggleExpanded(self, state: bool) -> None:
        """Toggle the expanded state of the panel."""
        if self._ep_expanded != state:
            self._ep_expanded = state
            self._ep_widget.setVisible(state)
            self.expandedStateChanged.emit(state)
