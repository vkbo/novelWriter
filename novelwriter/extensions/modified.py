"""
novelWriter – Custom Widget: Modified Widgets
=============================================

File History:
Created: 2024-02-01 [2.3b1] NComboBox
Created: 2024-02-01 [2.3b1] NSpinBox
Created: 2024-02-01 [2.3b1] NDoubleSpinBox
Created: 2024-05-01 [2.5b1] NToolDialog
Created: 2024-05-01 [2.5b1] NNonBlockingDialog

This file is a part of novelWriter
Copyright (C) 2024 Veronica Berglyd Olsen and novelWriter contributors

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

from typing import TYPE_CHECKING

from PyQt6.QtCore import QModelIndex, QSize, Qt, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import (
    QApplication, QComboBox, QDialog, QDoubleSpinBox, QLabel, QPushButton,
    QSpinBox, QToolButton, QTreeView, QWidget
)

from novelwriter import CONFIG, SHARED
from novelwriter.types import QtMouseLeft, QtMouseMiddle

if TYPE_CHECKING:
    from enum import Enum

    from PyQt6.QtGui import QMouseEvent, QWheelEvent

    from novelwriter.guimain import GuiMain


class NDialog(QDialog):
    """Custom: Modified QDialog."""

    def softDelete(self) -> None:
        """Since calling deleteLater is sometimes not safe from Python,
        as the C++ object can be deleted before the Python process is
        done with the object, we instead set the dialog's parent to None
        so that it gets garbage collected when it runs out of scope.
        """
        self.setParent(None)  # type: ignore

    @pyqtSlot()
    def reject(self) -> None:
        """Overload the reject slot and also call close."""
        super().reject()
        self.close()


class NToolDialog(NDialog):
    """Custom: Modified QDialog for Tools."""

    def __init__(self, parent: GuiMain) -> None:
        super().__init__(parent=parent)
        self.setModal(False)
        if CONFIG.osDarwin:
            self.setWindowFlag(Qt.WindowType.Tool)

    def activateDialog(self) -> None:
        """Activate dialog on various operating systems."""
        self.show()
        if CONFIG.osWindows:
            self.activateWindow()
        self.raise_()
        QApplication.processEvents()


class NNonBlockingDialog(NDialog):
    """Custom: Modified Non-Blocking QDialog."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self.setModal(True)

    def activateDialog(self) -> None:
        """Activate dialog on various operating systems."""
        self.show()
        if CONFIG.osWindows:
            self.activateWindow()
        self.raise_()
        QApplication.processEvents()


class NTreeView(QTreeView):
    """Custom: Modified QTreeView.

    The main purpose is to provide the middleClicked signal that matches
    clicked and doubleCLicked.
    """

    middleClicked = pyqtSignal(QModelIndex)

    def mousePressEvent(self, event: QMouseEvent | None) -> None:
        """Emit a signal on mouse middle click."""
        if (
            event and event.button() == QtMouseMiddle
            and (index := self.indexAt(event.pos())).isValid()
        ):
            self.middleClicked.emit(index)
        return super().mousePressEvent(event)


class NComboBox(QComboBox):
    """Custom: Modified QComboBox.

    The main purpose is to provide a combo box that doesn't scroll when
    the mousewheel is active on it while scrolling through a scrollable
    window of many widgets.
    """

    def __init__(self, parent: QWidget | None = None, maxItems: int = 15) -> None:
        super().__init__(parent=parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMaxVisibleItems(maxItems)

        # The style sheet disables Fusion style pop-up mode on some platforms
        # and allows for scrolling of long lists of items
        self.setStyleSheet("QComboBox {combobox-popup: 0;}")

    def wheelEvent(self, event: QWheelEvent) -> None:
        """Only capture the mouse wheel if the widget has focus."""
        if self.hasFocus():
            super().wheelEvent(event)
        else:
            event.ignore()

    def setCurrentData(self, data: str | int | Enum, default: str | int | Enum) -> None:
        """Set the current index from data, with a fallback."""
        idx = self.findData(data)
        self.setCurrentIndex(self.findData(default) if idx < 0 else idx)


class NSpinBox(QSpinBox):
    """Custom: Modified QSpinBox.

    The main purpose is to provide a spin box that doesn't scroll when
    the mousewheel is active on it while scrolling through a scrollable
    window of many widgets.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def wheelEvent(self, event: QWheelEvent) -> None:
        """Only capture the mouse wheel if the widget has focus."""
        if self.hasFocus():
            super().wheelEvent(event)
        else:
            event.ignore()


class NDoubleSpinBox(QDoubleSpinBox):
    """Custom: Modified QDoubleSpinBox.

    The main purpose is to provide a float spin box that doesn't scroll
    when the mousewheel is active on it while scrolling through a
    scrollable window of many widgets.
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        minVal: float = 0.0,
        maxVal: float = 15.0,
        step: float = 0.1,
        prec: int = 2,
    ) -> None:
        super().__init__(parent=parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMinimum(minVal)
        self.setMaximum(maxVal)
        self.setSingleStep(step)
        self.setDecimals(prec)

    def wheelEvent(self, event: QWheelEvent) -> None:
        """Only capture the mouse wheel if the widget has focus."""
        if self.hasFocus():
            super().wheelEvent(event)
        else:
            event.ignore()


class NPushButton(QPushButton):
    """Custom: Modified QPushButton.

    A quicker way to create a push button using the app theme.
    """

    def __init__(
        self, parent: QWidget, text: str, iconSize: QSize,
        icon: str | None = None, color: str | None = None
    ) -> None:
        super().__init__(parent=parent)
        self.setText(text)
        self.setIconSize(iconSize)
        self._icon = icon
        self._color = color
        if icon:
            self.refreshIcon()

    def setThemeIcon(self, icon: str, color: str | None = None) -> None:
        """Set an icon from the current theme."""
        self._icon = icon
        self._color = color
        self.refreshIcon()

    def refreshIcon(self) -> None:
        """Reload the theme icon."""
        if self._icon:
            self.setIcon(SHARED.theme.getIcon(self._icon, self._color))


class NIconToolButton(QToolButton):
    """Custom: Modified QToolButton.

    A quicker way to create a tool button using the app theme.
    """

    def __init__(
        self, parent: QWidget, iconSize: QSize,
        icon: str | None = None, color: str | None = None
    ) -> None:
        super().__init__(parent=parent)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.setIconSize(iconSize)
        self.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        if icon:
            self.setThemeIcon(icon, color)

    def setThemeIcon(self, iconKey: str, color: str | None = None) -> None:
        """Set an icon from the current theme."""
        self.setIcon(SHARED.theme.getIcon(iconKey, color))


class NIconToggleButton(QToolButton):
    """Custom: Modified QToolButton.

    A quicker way to create a toggle button using the app theme.
    """

    def __init__(self, parent: QWidget, iconSize: QSize, icon: str | None = None) -> None:
        super().__init__(parent=parent)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.setIconSize(iconSize)
        self.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.setCheckable(True)
        self.setStyleSheet("border: none; background: transparent;")
        if icon:
            self.setThemeIcon(icon)

    def setThemeIcon(self, iconKey: str) -> None:
        """Set an icon from the current theme."""
        iconSize = self.iconSize()
        self.setIcon(SHARED.theme.getToggleIcon(iconKey, (iconSize.width(), iconSize.height())))


class NClickableLabel(QLabel):
    """Custom: Clickable QLabel."""

    mouseClicked = pyqtSignal()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Capture a left mouse click and emit its signal."""
        if event.button() == QtMouseLeft:
            self.mouseClicked.emit()
        return super().mousePressEvent(event)
