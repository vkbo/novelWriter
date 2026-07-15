"""
novelWriter – GUI Viewer Header
===============================

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

import logging

from typing import TYPE_CHECKING

from PyQt6.QtCore import pyqtSlot
from PyQt6.QtGui import QAction, QPalette
from PyQt6.QtWidgets import QHBoxLayout, QMenu, QWidget

from novelwriter import CONFIG, SHARED
from novelwriter.common import elide, qtAddAction
from novelwriter.enum import nwDocMode, nwState
from novelwriter.extensions.configlayout import NPathColorLabel
from novelwriter.extensions.modified import NIconToolButton
from novelwriter.gui.theme import STYLES_MIN_TOOLBUTTON
from novelwriter.types import QtAlignCenterTop, QtAlignMiddle

if TYPE_CHECKING:
    from novelwriter.viewer.viewer import GuiDocViewer

logger = logging.getLogger(__name__)


class GuiDocViewHeader(QWidget):
    """The Embedded Document Header.

    Only used by DocViewer, and is at a fixed position in the
    QTextBrowser's viewport.
    """

    def __init__(self, docViewer: GuiDocViewer) -> None:
        super().__init__(parent=docViewer)

        logger.debug("Create: GuiDocViewHeader")

        self.docViewer = docViewer

        # Internal Variables
        self._docHandle = None
        self._docOutline: dict[str, tuple[str, int]] = {}

        iSz = SHARED.theme.baseIconSize
        fPx = SHARED.theme.fontPixelSize

        # Main Widget Settings
        self.setAutoFillBackground(True)

        # Title Label
        self.itemTitle = NPathColorLabel("", self, faded=SHARED.theme.fadedText)
        self.itemTitle.setMargin(0)
        self.itemTitle.setContentsMargins(0, 0, 0, 0)
        self.itemTitle.setAutoFillBackground(True)
        self.itemTitle.setAlignment(QtAlignCenterTop)
        self.itemTitle.setFixedHeight(fPx)
        self.itemTitle.linkActivated.connect(self._processLabelLink)

        # Other Widgets
        self.outlineMenu = QMenu(self)
        self.outlineMenu.triggered.connect(self._gotoHeader)

        # Buttons
        self.outlineButton = NIconToolButton(self, iSz, "list:action")
        self.outlineButton.setVisible(False)
        self.outlineButton.setToolTip(self.tr("Outline"))
        self.outlineButton.setMenu(self.outlineMenu)

        self.backButton = NIconToolButton(self, iSz, "chevron_left:action")
        self.backButton.setVisible(False)
        self.backButton.setToolTip(self.tr("Go Backward"))
        self.backButton.clicked.connect(self.docViewer.navBackward)

        self.forwardButton = NIconToolButton(self, iSz, "chevron_right:action")
        self.forwardButton.setVisible(False)
        self.forwardButton.setToolTip(self.tr("Go Forward"))
        self.forwardButton.clicked.connect(self.docViewer.navForward)

        self.editButton = NIconToolButton(self, iSz, "edit:change")
        self.editButton.setVisible(False)
        self.editButton.setToolTip(self.tr("Open in Editor"))
        self.editButton.clicked.connect(self._editDocument)

        self.refreshButton = NIconToolButton(self, iSz, "refresh:change")
        self.refreshButton.setVisible(False)
        self.refreshButton.setToolTip(self.tr("Reload"))
        self.refreshButton.clicked.connect(self._refreshDocument)

        self.closeButton = NIconToolButton(self, iSz, "close:reject")
        self.closeButton.setVisible(False)
        self.closeButton.setToolTip(self.tr("Close"))
        self.closeButton.clicked.connect(self._closeDocument)

        # Assemble Layout
        self.outerBox = QHBoxLayout()
        self.outerBox.addWidget(self.outlineButton, 0, QtAlignMiddle)
        self.outerBox.addWidget(self.backButton, 0, QtAlignMiddle)
        self.outerBox.addWidget(self.forwardButton, 0, QtAlignMiddle)
        self.outerBox.addSpacing(4)
        self.outerBox.addWidget(self.itemTitle, 1, QtAlignMiddle)
        self.outerBox.addSpacing(4)
        self.outerBox.addWidget(self.editButton, 0, QtAlignMiddle)
        self.outerBox.addWidget(self.refreshButton, 0, QtAlignMiddle)
        self.outerBox.addWidget(self.closeButton, 0, QtAlignMiddle)
        self.outerBox.setSpacing(0)

        self.setLayout(self.outerBox)

        # Fix Margins and Size
        # This is needed for high DPI systems. See issue #499.
        self.setContentsMargins(0, 0, 0, 0)
        self.outerBox.setContentsMargins(4, 4, 4, 4)
        self.setMinimumHeight(fPx + 4)

        self.updateFont()
        self.updateTheme(init=True)

        logger.debug("Ready: GuiDocViewHeader")

    ##
    #  Methods
    ##

    def clearHeader(self) -> None:
        """Clear the header."""
        self._docHandle = None
        self._docOutline = {}

        self.itemTitle.setText("")
        self.outlineMenu.clear()
        self.outlineButton.setVisible(False)
        self.backButton.setVisible(False)
        self.forwardButton.setVisible(False)
        self.editButton.setVisible(False)
        self.refreshButton.setVisible(False)
        self.closeButton.setVisible(False)

    def setOutline(self, data: dict[str, tuple[str, int]]) -> None:
        """Set the document outline dataset."""
        tHandle = self._docHandle
        if data != self._docOutline and tHandle:
            self.outlineMenu.clear()
            entries = []
            minLevel = 5
            for title, (text, level) in data.items():
                if title != "T0000":
                    entries.append((title, text, level))
                    minLevel = min(minLevel, level)
            for title, text, level in entries[:30]:
                indent = "    " * (level - minLevel)
                qtAddAction(self.outlineMenu, f"{indent}{elide(text, 50)}", data=f"#{tHandle}:{title}")
            self._docOutline = data

    def updateFont(self) -> None:
        """Update the font settings."""
        self.setFont(SHARED.theme.guiFont)
        self.itemTitle.setFont(SHARED.theme.guiFontSmall)

    def updateTheme(self, *, init: bool = False) -> None:
        """Update theme elements."""
        logger.debug("Theme Update: GuiDocViewHeader")

        if not init:
            self.outlineButton.refreshTheme()
            self.backButton.refreshTheme()
            self.forwardButton.refreshTheme()
            self.editButton.refreshTheme()
            self.refreshButton.refreshTheme()
            self.closeButton.refreshTheme()

        buttonStyle = SHARED.theme.getStyleSheet(STYLES_MIN_TOOLBUTTON)
        self.outlineButton.setStyleSheet(buttonStyle)
        self.backButton.setStyleSheet(buttonStyle)
        self.forwardButton.setStyleSheet(buttonStyle)
        self.editButton.setStyleSheet(buttonStyle)
        self.refreshButton.setStyleSheet(buttonStyle)
        self.closeButton.setStyleSheet(buttonStyle)

        self.matchColors()

    def matchColors(self) -> None:
        """Update the colours of the widget to match those of the syntax
        theme rather than the main GUI.
        """
        syntax = SHARED.theme.syntaxTheme
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, syntax.back)
        palette.setColor(QPalette.ColorRole.WindowText, syntax.text)
        palette.setColor(QPalette.ColorRole.Text, syntax.text)
        self.setPalette(palette)
        self.itemTitle.setTextColors(
            color=palette.windowText().color(),
            faded=SHARED.theme.fadedText,
        )

    def changeFocusState(self, state: bool) -> None:
        """Toggle focus state."""
        self.itemTitle.setColorState(nwState.NORMAL if state else nwState.INACTIVE)

    def setHandle(self, tHandle: str) -> None:
        """Set the document title from the handle, or alternatively, set
        the whole document path within the project.
        """
        self._docHandle = tHandle
        if CONFIG.showFullPath:
            self.itemTitle.setText(SHARED.project.tree.itemPath(tHandle, withName=True))
        elif item := SHARED.project.tree[tHandle]:
            self.itemTitle.setText([(item.itemHandle, item.itemName)])

        self.backButton.setVisible(True)
        self.forwardButton.setVisible(True)
        self.outlineButton.setVisible(True)
        self.editButton.setVisible(True)
        self.refreshButton.setVisible(True)
        self.closeButton.setVisible(True)

    def updateNavButtons(self, firstIdx: int, lastIdx: int, currIdx: int) -> None:
        """Enable and disable nav buttons based on index in history."""
        self.backButton.setEnabled(currIdx > firstIdx)
        self.forwardButton.setEnabled(currIdx < lastIdx)

    ##
    #  Private Slots
    ##

    @pyqtSlot()
    def _closeDocument(self) -> None:
        """Trigger the close editor/viewer on the main window."""
        self.clearHeader()
        self.docViewer.closeDocumentRequest.emit()

    @pyqtSlot()
    def _refreshDocument(self) -> None:
        """Reload the content of the document."""
        self.docViewer.reloadDocumentRequest.emit()

    @pyqtSlot()
    def _editDocument(self) -> None:
        """Open the document in the editor."""
        if tHandle := self._docHandle:
            self.docViewer.openDocumentRequest.emit(tHandle, nwDocMode.EDIT, "", True)

    @pyqtSlot(str)
    def _processLabelLink(self, link: str) -> None:
        """Process an activated link in the label."""
        if link.startswith("#"):
            self.docViewer.requestProjectItemSelected.emit(link.lstrip("#"), True)

    @pyqtSlot(QAction)
    def _gotoHeader(self, action: QAction) -> None:
        """Move cursor to a specific heading."""
        if isinstance(data := action.data(), str):
            self.docViewer.navigateTo(data)
