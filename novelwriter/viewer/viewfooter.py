"""
novelWriter – GUI Viewer Footer
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

from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QPalette
from PyQt6.QtWidgets import QHBoxLayout, QToolButton, QWidget

from novelwriter import CONFIG, SHARED
from novelwriter.extensions.modified import NIconToolButton
from novelwriter.gui.theme import STYLES_MIN_TOOLBUTTON

if TYPE_CHECKING:
    from novelwriter.viewer.viewer import GuiDocViewer

logger = logging.getLogger(__name__)


class GuiDocViewFooter(QWidget):
    """The Embedded Document Footer.

    Only used by DocViewer, and is at a fixed position in the
    QTextBrowser's viewport.
    """

    def __init__(self, docViewer: GuiDocViewer) -> None:
        super().__init__(parent=docViewer)

        logger.debug("Create: GuiDocViewFooter")

        self.docViewer = docViewer

        # Internal Variables
        self._docHandle = None

        iPx = SHARED.theme.baseIconHeight
        iSz = SHARED.theme.baseIconSize

        # Main Widget Settings
        self.setContentsMargins(0, 0, 0, 0)
        self.setAutoFillBackground(True)

        # Show/Hide Details
        self.showHide = NIconToolButton(self, iSz)
        self.showHide.setToolTip(self.tr("Show/Hide Viewer Panel"))
        self.showHide.clicked.connect(lambda: self.docViewer.togglePanelVisibility.emit())

        # Show Comments
        self.showComments = QToolButton(self)
        self.showComments.setText(self.tr("Comments"))
        self.showComments.setToolTip(self.tr("Show Comments"))
        self.showComments.setCheckable(True)
        self.showComments.setChecked(CONFIG.viewComments)
        self.showComments.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.showComments.setIconSize(iSz)
        self.showComments.toggled.connect(self._doToggleComments)

        # Show Synopsis
        self.showSynopsis = QToolButton(self)
        self.showSynopsis.setText(self.tr("Synopsis"))
        self.showSynopsis.setToolTip(self.tr("Show Synopsis Comments"))
        self.showSynopsis.setCheckable(True)
        self.showSynopsis.setChecked(CONFIG.viewSynopsis)
        self.showSynopsis.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.showSynopsis.setIconSize(iSz)
        self.showSynopsis.toggled.connect(self._doToggleSynopsis)

        # Show Notes
        self.showNotes = QToolButton(self)
        self.showNotes.setText(self.tr("Notes"))
        self.showNotes.setToolTip(self.tr("Show Notes"))
        self.showNotes.setCheckable(True)
        self.showNotes.setChecked(CONFIG.viewNotes)
        self.showNotes.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.showNotes.setIconSize(iSz)
        self.showNotes.toggled.connect(self._doToggleNotes)

        # Assemble Layout
        self.outerBox = QHBoxLayout()
        self.outerBox.addWidget(self.showHide, 0)
        self.outerBox.addStretch(1)
        self.outerBox.addWidget(self.showComments, 0)
        self.outerBox.addWidget(self.showSynopsis, 0)
        self.outerBox.addWidget(self.showNotes, 0)
        self.outerBox.setSpacing(4)
        self.setLayout(self.outerBox)

        # Fix Margins and Size
        # This is needed for high DPI systems. See issue #499.
        self.setContentsMargins(0, 0, 0, 0)
        self.outerBox.setContentsMargins(4, 4, 4, 4)
        self.setMinimumHeight(iPx + 8)

        self.updateFont()
        self.updateTheme()

        logger.debug("Ready: GuiDocViewFooter")

    ##
    #  Methods
    ##

    def updateFont(self) -> None:
        """Update the font settings."""
        self.setFont(SHARED.theme.guiFont)
        self.showComments.setFont(SHARED.theme.guiFontSmall)
        self.showSynopsis.setFont(SHARED.theme.guiFontSmall)
        self.showNotes.setFont(SHARED.theme.guiFontSmall)

    def updateTheme(self) -> None:
        """Update theme elements."""
        logger.debug("Theme Update: GuiDocViewFooter")

        fPx = int(0.9 * SHARED.theme.fontPixelSize)
        bulletIcon = SHARED.theme.getToggleIcon("bullet", (fPx, fPx), "action")

        self.showHide.setThemeIcon("panel", "default")
        self.showComments.setIcon(bulletIcon)
        self.showSynopsis.setIcon(bulletIcon)
        self.showNotes.setIcon(bulletIcon)

        buttonStyle = SHARED.theme.getStyleSheet(STYLES_MIN_TOOLBUTTON)
        self.showHide.setStyleSheet(buttonStyle)
        self.showComments.setStyleSheet(buttonStyle)
        self.showSynopsis.setStyleSheet(buttonStyle)
        self.showNotes.setStyleSheet(buttonStyle)

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

    ##
    #  Private Slots
    ##

    @pyqtSlot(bool)
    def _doToggleComments(self, state: bool) -> None:
        """Toggle the view comment button and reload the document."""
        CONFIG.viewComments = state
        self.docViewer.reloadText()

    @pyqtSlot(bool)
    def _doToggleSynopsis(self, state: bool) -> None:
        """Toggle the view synopsis button and reload the document."""
        CONFIG.viewSynopsis = state
        self.docViewer.reloadText()

    @pyqtSlot(bool)
    def _doToggleNotes(self, state: bool) -> None:
        """Toggle the view notes button and reload the document."""
        CONFIG.viewNotes = state
        self.docViewer.reloadText()
