"""
novelWriter – Custom Widget: Modified Widgets
=============================================

File History:
Created: 2024-02-01 [2.3b1]  NComboBox
Created: 2024-02-01 [2.3b1]  NSpinBox
Created: 2024-02-01 [2.3b1]  NDoubleSpinBox
Created: 2024-03-20 [2.4b1]  NIconToolButton
Created: 2024-04-01 [2.4rc1] NIconToggleButton
Created: 2024-05-01 [2.5b1]  NToolDialog
Created: 2024-05-01 [2.5b1]  NNonBlockingDialog
Created: 2024-05-27 [2.5rc1] NDialog
Created: 2024-12-29 [2.6rc1] NClickableLabel
Created: 2025-02-22 [2.7b1]  NTreeView
Created: 2025-10-25 [2.8b1]  NPushButton
Created: 2025-11-08 [2.8rc1] NFontDialog

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

import logging

from typing import TYPE_CHECKING

from PyQt6.QtCore import QModelIndex, QSize, Qt, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import (
    QApplication, QComboBox, QDialog, QDialogButtonBox, QDoubleSpinBox,
    QFontDialog, QLabel, QPushButton, QSpinBox, QToolButton, QTreeView, QWidget
)

from novelwriter import CONFIG, SHARED
from novelwriter.enum import nwStandardButton
from novelwriter.types import QtMouseLeft, QtMouseMiddle, QtRoleAccept, QtRoleReject

if TYPE_CHECKING:
    from enum import Enum

    from PyQt6.QtGui import QFont, QMouseEvent, QWheelEvent

    from novelwriter.guimain import GuiMain

logger = logging.getLogger(__name__)


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
    def closeDialog(self) -> None:
        """Close the dialog."""
        self.setResult(0)
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


class NFontDialog(QFontDialog):
    """Custom: Modified Font Dialog.

    An overload of the Qt font dialog that remembers its previous size.
    """

    def __init__(self, initial: QFont, parent: QWidget) -> None:
        super().__init__(initial, parent)

        # Look for the button box and replace the buttons
        if dlgBox := self.findChild(QDialogButtonBox):
            self.btnOk = SHARED.theme.getStandardButton(nwStandardButton.OK, self)
            self.btnOk.clicked.connect(self.accept)

            self.btnCancel = SHARED.theme.getStandardButton(nwStandardButton.CANCEL, self)
            self.btnCancel.clicked.connect(self.reject)

            dlgBox.clear()
            dlgBox.addButton(self.btnOk, QtRoleAccept)
            dlgBox.addButton(self.btnCancel, QtRoleReject)

        logger.debug("Ready: NFontDialog")

    def __del__(self) -> None:  # pragma: no cover
        logger.debug("Delete: NFontDialog")

    @staticmethod
    def selectFont(font: QFont, parent: QWidget, title: str, native: bool) -> tuple[QFont, bool]:
        """Open the dialog and select a font."""
        if native:
            # If we're using the native dialog, let Qt handle it
            font, result = QFontDialog.getFont(font, parent, title)
            return font, bool(result)

        # Execute the custom dialog
        dialog = NFontDialog(font, parent)
        dialog.setOption(QFontDialog.FontDialogOption.DontUseNativeDialog, True)
        dialog.setWindowTitle(title)
        dialog.resize(*CONFIG.fontWinSize)

        dialog.exec()
        CONFIG.setFontWinSize(dialog.geometry())

        return dialog.selectedFont(), dialog.result() == 1


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
        self.updateStyle()

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

    def updateStyle(self) -> None:
        """Update the style sheet."""
        # The style sheet disables Fusion style pop-up mode on some
        # platforms and allows for scrolling of long lists of items
        self.setStyleSheet("QComboBox {combobox-popup: 0;}")


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
        self._icon = icon
        self._color = color
        self.setText(text)
        self.setIconSize(iconSize)
        self.updateIcon()

    def updateIcon(self) -> None:
        """Update the theme icon."""
        if self._icon and self._color:
            self.setIcon(SHARED.theme.getIcon(self._icon, self._color))

    def setText(self, text: str) -> None:
        """Overload the text setter to add padding."""
        return super().setText(f" {text}")


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
        if icon and color:
            self.setThemeIcon(icon, color)

    def setThemeIcon(self, icon: str, color: str) -> None:
        """Set an icon from the current theme."""
        self.setIcon(SHARED.theme.getIcon(icon, color))


class NIconToggleButton(QToolButton):
    """Custom: Modified QToolButton.

    A quicker way to create a toggle button using the app theme.
    """

    def __init__(
        self, parent: QWidget, iconSize: QSize,
        icon: str | None = None, color: str | None = None
    ) -> None:
        super().__init__(parent=parent)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.setIconSize(iconSize)
        self.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.setCheckable(True)
        self.setStyleSheet("border: none; background: transparent;")
        if icon and color:
            self.setThemeIcon(icon, color)

    def setThemeIcon(self, icon: str, color: str) -> None:
        """Set an icon from the current theme."""
        size = self.iconSize()
        self.setIcon(SHARED.theme.getToggleIcon(icon, (size.width(), size.height()), color))


class NClickableLabel(QLabel):
    """Custom: Clickable QLabel."""

    mouseClicked = pyqtSignal()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Capture a left mouse click and emit its signal."""
        if event.button() == QtMouseLeft:
            self.mouseClicked.emit()
        return super().mousePressEvent(event)
