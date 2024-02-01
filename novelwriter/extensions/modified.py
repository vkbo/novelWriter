"""
novelWriter – Custom Widget: Modified Widgets
=============================================

File History:
Created: 2024-02-01 [2.3b1] NComboBox
Created: 2024-02-01 [2.3b1] NSpinBox
Created: 2024-02-01 [2.3b1] NDoubleSpinBox

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

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QWheelEvent
from PyQt5.QtWidgets import QComboBox, QDoubleSpinBox, QSpinBox, QWidget


class NComboBox(QComboBox):

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        return

    def wheelEvent(self, event: QWheelEvent) -> None:
        if self.hasFocus():
            super().wheelEvent(event)
        else:
            event.ignore()
        return

# END Class NComboBox


class NSpinBox(QSpinBox):

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        return

    def wheelEvent(self, event: QWheelEvent) -> None:
        if self.hasFocus():
            super().wheelEvent(event)
        else:
            event.ignore()
        return

# END Class NSpinBox


class NDoubleSpinBox(QDoubleSpinBox):

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        return

    def wheelEvent(self, event: QWheelEvent) -> None:
        if self.hasFocus():
            super().wheelEvent(event)
        else:
            event.ignore()
        return

# END Class NDoubleSpinBox
