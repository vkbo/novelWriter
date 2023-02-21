"""
novelWriter – Custom Widget: Paged SideBar
==========================================
A custom widget for making a sidebar for flipping through pages

File History:
Created: 2023-02-21 [2.1b1] NPagedSideBar
Created: 2023-02-21 [2.1b1] NToolLabelButton

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

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QActionGroup, QSizePolicy, QToolBar, QToolButton, QWidget


class NPagedSideBar(QToolBar):

    def __init__(self, parent):
        super().__init__(parent=parent)

        self._buttons = []
        self._actions = []
        self._group = QActionGroup(self)
        self._group.setExclusive(True)

        self.setMovable(False)
        self.setOrientation(Qt.Vertical)

        stretch = QWidget(self)
        stretch.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._stretchAction = self.addWidget(stretch)

        return

    def addLabel(self, text, height):
        """Add a new label to the toolbar.
        """
        return

    def addButton(self, text, height):
        """Add a new button to the toolbar.
        """
        button = NToolLabelButton(self)
        button.setFixedHeight(height)
        button.setText(text)

        action = self.insertWidget(self._stretchAction, button)
        self._group.addAction(action)

        self._buttons.append(button)
        self._actions.append(action)

        return action

# END Class NPagedSideBar


class NToolLabelButton(QToolButton):

    def __init__(self, parent):
        super().__init__(parent=parent)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setCheckable(True)

        return

# END Class NToolLabelButton
