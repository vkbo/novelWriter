"""
novelWriter – Custom Widget: Config Layout
==========================================

File History:
Created: 2020-05-03 [0.4.5] NColourLabel
Created: 2024-01-08 [2.3b1] NScrollableForm
Created: 2024-01-26 [2.3b1] NScrollablePage
Created: 2024-01-26 [2.3b1] NFixedPage
Created: 2024-03-12 [2.4b1] NWrappedWidgetBox

This file is a part of novelWriter
Copyright (C) 2023 Veronica Berglyd Olsen and novelWriter contributors

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

from PyQt6.QtGui import QColor, QFont, QPalette, QPixmap
from PyQt6.QtWidgets import (
    QAbstractButton, QFrame, QHBoxLayout, QLabel, QLayout, QScrollArea,
    QVBoxLayout, QWidget
)

from novelwriter.types import QtScrollAsNeeded

DEFAULT_SCALE = 0.9


class NFixedPage(QFrame):
    """Extension: Fixed Page Widget

    A custom widget that holds a layout. This is just a wrapper around a
    QFrame that sets the same frame style as the other Page widgets.
    """

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)
        self.setFrameShadow(QFrame.Shadow.Sunken)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        return

    def setCentralLayout(self, layout: QLayout) -> None:
        """Set a layout as the central object."""
        self.setLayout(layout)
        return

    def setCentralWidget(self, widget: QWidget) -> None:
        """Set a layout as the central object."""
        layout = QHBoxLayout()
        layout.addWidget(widget)
        self.setLayout(layout)
        return


class NScrollablePage(QScrollArea):
    """Extension: Scrollable Page Widget

    A custom widget that holds a layout within a scrollable area.
    """

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)
        self._widget = QWidget(self)
        self.setWidget(self._widget)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(QtScrollAsNeeded)
        self.setVerticalScrollBarPolicy(QtScrollAsNeeded)
        self.setFrameShadow(QFrame.Shadow.Sunken)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        return

    def setCentralLayout(self, layout: QLayout) -> None:
        """Set the central layout of the scroll page."""
        self._widget.setLayout(layout)
        return


class NScrollableForm(QScrollArea):
    """Extension: Scrollable Form Widget

    A custom widget that creates a form within a scrollable area.
    """

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)
        self._helpCol = QColor(0, 0, 0)
        self._fontScale = DEFAULT_SCALE
        self._first = True
        self._indent = 12

        self._sections: dict[int, QLabel] = {}
        self._editable: dict[str, NColorLabel] = {}
        self._index: dict[str, QWidget] = {}

        self._layout = QVBoxLayout()
        self._layout.setSpacing(12)

        self._widget = QWidget(self)
        self._widget.setLayout(self._layout)

        self.setWidget(self._widget)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(QtScrollAsNeeded)
        self.setVerticalScrollBarPolicy(QtScrollAsNeeded)
        self.setFrameShadow(QFrame.Shadow.Sunken)
        self.setFrameShape(QFrame.Shape.StyledPanel)

        return

    ##
    #  Properties
    ##

    @property
    def labels(self) -> list[str]:
        return list(self._index.keys())

    ##
    #  Setters
    ##

    def setHelpTextStyle(self, color: QColor, scale: float = DEFAULT_SCALE) -> None:
        """Set the text color for the help text."""
        self._helpCol = color
        self._fontScale = scale
        return

    def setHelpText(self, key: str, text: str) -> None:
        """Set the text for the help label."""
        if qHelp := self._editable.get(key):
            qHelp.setText(text)
        return

    def setRowIndent(self, indent: int) -> None:
        """Set the indentation of each row."""
        self._indent = max(indent, 0)
        return

    ##
    #  Methods
    ##

    def scrollToSection(self, identifier: int) -> None:
        """Scroll to the requested section identifier."""
        if identifier in self._sections:
            yPos = self._sections[identifier].pos().y() - 8
            if vBar := self.verticalScrollBar():
                vBar.setValue(yPos)
        return

    def scrollToLabel(self, label: str) -> None:
        """Scroll to the requested label."""
        if label in self._index:
            yPos = self._index[label].pos().y() - 8
            if vBar := self.verticalScrollBar():
                vBar.setValue(yPos)
        return

    def addGroupLabel(self, label: str, identifier: int | None = None) -> None:
        """Add a text label to separate groups of settings."""
        qLabel = QLabel(f"<b>{label}</b>", self)
        qLabel.setContentsMargins(0, 4, 0, 4)
        if not self._first:
            self._layout.addSpacing(20)
        self._layout.addWidget(qLabel)
        self._first = False
        if identifier is not None:
            self._sections[identifier] = qLabel
        return

    def addRow(
        self,
        label: str | None,
        widget: QWidget | list[QWidget | QPixmap | int],
        helpText: str = "",
        unit: str | None = None,
        button: QWidget | None = None,
        editable: str | None = None,
        stretch: tuple[int, int] = (1, 0),
    ) -> None:
        """Add a label and a widget as a new row of the form."""
        row = QHBoxLayout()
        row.setSpacing(12)

        if isinstance(widget, list):
            wBox = QHBoxLayout()
            wBox.setContentsMargins(0, 0, 0, 0)
            for item in widget:
                if isinstance(item, QWidget):
                    wBox.addWidget(item)
                elif isinstance(item, QPixmap):
                    icon = QLabel(self)
                    icon.setPixmap(item)
                    wBox.addWidget(icon)
                elif isinstance(item, int):
                    wBox.addSpacing(item)
            qWidget = QWidget(self)
            qWidget.setLayout(wBox)
        else:
            qWidget = widget

        text = label or ""
        qLabel = QLabel(text, self)
        qLabel.setIndent(self._indent)
        qLabel.setBuddy(qWidget)

        if helpText:
            qHelp = NColorLabel(
                str(helpText), self, color=self._helpCol,
                scale=self._fontScale, wrap=True, indent=self._indent
            )
            labelBox = QVBoxLayout()
            labelBox.addWidget(qLabel, 0)
            labelBox.addWidget(qHelp, 1)
            labelBox.setSpacing(0)
            row.addLayout(labelBox, stretch[0])
            if editable:
                self._editable[editable] = qHelp
            text = f"{text}: {helpText}"
        else:
            row.addWidget(qLabel, stretch[0])

        if isinstance(unit, str):
            box = QHBoxLayout()
            box.addWidget(qWidget, 1)
            box.addWidget(QLabel(unit, self), 0)
            row.addLayout(box, stretch[1])
            text = f"{text} Unit: {unit}"
        elif isinstance(button, QAbstractButton):
            box = QHBoxLayout()
            box.addWidget(qWidget, 1)
            box.addWidget(button, 0)
            row.addLayout(box, stretch[1])
        else:
            row.addWidget(qWidget, stretch[1])

        self._first = False
        self._layout.addLayout(row)
        if label:
            self._index[label.strip()] = qWidget
        qLabel.setAccessibleName(text)

        return

    def finalise(self) -> None:
        """Finalise the layout when the form is built."""
        self._layout.addSpacing(20)
        self._layout.addStretch(1)
        return


class NColorLabel(QLabel):
    """Extension: A Coloured Label

    A custom widget that draws a label in a specific colour, and
    optionally at a specific size, and word wrapped.
    """

    HELP_SCALE = DEFAULT_SCALE
    HEADER_SCALE = 1.25

    _state = None

    def __init__(
        self, text: str, parent: QWidget, *,
        color: QColor | None = None, faded: QColor | None = None,
        scale: float = HELP_SCALE, wrap: bool = False, indent: int = 0,
        bold: bool = False
    ) -> None:
        super().__init__(text, parent=parent)

        default = self.palette().windowText().color()
        self._color = color or default
        self._faded = faded or default

        font = self.font()
        font.setPointSizeF(scale*font.pointSizeF())
        font.setWeight(QFont.Weight.Bold if bold else QFont.Weight.Normal)
        if color:
            colour = self.palette()
            colour.setColor(QPalette.ColorRole.WindowText, color)
            self.setPalette(colour)

        self.setFont(font)
        self.setIndent(indent)
        self.setWordWrap(wrap)
        self.setColorState(True)

        return

    def setTextColors(self, *, color: QColor | None = None, faded: QColor | None = None) -> None:
        """Set or update the text colours."""
        self._color = color or self._color
        self._faded = faded or self._faded
        self._refeshTextColor()
        return

    def setColorState(self, state: bool) -> None:
        """Change the colour state."""
        if self._state is not state:
            self._state = state
            self._refeshTextColor()
        return

    def _refeshTextColor(self) -> None:
        """Refresh the colour of the text on the label."""
        palette = self.palette()
        palette.setColor(
            QPalette.ColorRole.WindowText,
            self._color if self._state else self._faded,
        )
        self.setPalette(palette)
        return


class NWrappedWidgetBox(QHBoxLayout):
    """Extension: A Text-Wrapped Widget Box

    A custom layout box where a widget is wrapped in text labels on
    either side within a layout box. The widget is inserted at the {0}
    position so that it can be used for translation strings.
    """

    def __init__(self, text: str, widget: QWidget) -> None:
        super().__init__()
        before, _, after  = text.partition(r"{0}")
        if before:
            self.addWidget(QLabel(before.rstrip()))
        self.addWidget(widget)
        if after:
            self.addWidget(QLabel(after.lstrip()))
        return
