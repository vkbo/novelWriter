"""
novelWriter – GUI Editor Toolbar
================================

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

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QPalette
from PyQt6.QtWidgets import QVBoxLayout, QWidget

from novelwriter import SHARED
from novelwriter.common import qtLambda
from novelwriter.enum import nwDocAction
from novelwriter.extensions.modified import NIconToolButton

if TYPE_CHECKING:
    from novelwriter.gui_doc.editor import GuiDocEditor

logger = logging.getLogger(__name__)


class GuiDocToolBar(QWidget):
    """The Formatting and Options Fold Out Menu.

    Only used by DocEditor, and is opened by the first button in the
    header.
    """

    requestDocAction = pyqtSignal(nwDocAction)

    def __init__(self, docEditor: GuiDocEditor) -> None:
        super().__init__(parent=docEditor)

        logger.debug("Create: GuiDocToolBar")

        iSz = SHARED.theme.baseIconSize
        self.setContentsMargins(0, 0, 0, 0)

        # General Buttons
        # ===============

        self.tbBoldMD = NIconToolButton(self, iSz)
        self.tbBoldMD.setToolTip(self.tr("Markdown Bold"))
        self.tbBoldMD.clicked.connect(qtLambda(self.requestDocAction.emit, nwDocAction.MD_BOLD))

        self.tbItalicMD = NIconToolButton(self, iSz)
        self.tbItalicMD.setToolTip(self.tr("Markdown Italic"))
        self.tbItalicMD.clicked.connect(qtLambda(self.requestDocAction.emit, nwDocAction.MD_ITALIC))

        self.tbStrikeMD = NIconToolButton(self, iSz)
        self.tbStrikeMD.setToolTip(self.tr("Markdown Strikethrough"))
        self.tbStrikeMD.clicked.connect(qtLambda(self.requestDocAction.emit, nwDocAction.MD_STRIKE))

        self.tbMarkMD = NIconToolButton(self, iSz)
        self.tbMarkMD.setToolTip(self.tr("Markdown Highlight"))
        self.tbMarkMD.clicked.connect(qtLambda(self.requestDocAction.emit, nwDocAction.MD_MARK))

        self.tbBold = NIconToolButton(self, iSz)
        self.tbBold.setToolTip(self.tr("Shortcode Bold"))
        self.tbBold.clicked.connect(qtLambda(self.requestDocAction.emit, nwDocAction.SC_BOLD))

        self.tbItalic = NIconToolButton(self, iSz)
        self.tbItalic.setToolTip(self.tr("Shortcode Italic"))
        self.tbItalic.clicked.connect(qtLambda(self.requestDocAction.emit, nwDocAction.SC_ITALIC))

        self.tbStrike = NIconToolButton(self, iSz)
        self.tbStrike.setToolTip(self.tr("Shortcode Strikethrough"))
        self.tbStrike.clicked.connect(qtLambda(self.requestDocAction.emit, nwDocAction.SC_STRIKE))

        self.tbUnderline = NIconToolButton(self, iSz)
        self.tbUnderline.setToolTip(self.tr("Shortcode Underline"))
        self.tbUnderline.clicked.connect(qtLambda(self.requestDocAction.emit, nwDocAction.SC_ULINE))

        self.tbMark = NIconToolButton(self, iSz)
        self.tbMark.setToolTip(self.tr("Shortcode Highlight"))
        self.tbMark.clicked.connect(qtLambda(self.requestDocAction.emit, nwDocAction.SC_MARK))

        self.tbSuperscript = NIconToolButton(self, iSz)
        self.tbSuperscript.setToolTip(self.tr("Shortcode Superscript"))
        self.tbSuperscript.clicked.connect(qtLambda(self.requestDocAction.emit, nwDocAction.SC_SUP))

        self.tbSubscript = NIconToolButton(self, iSz)
        self.tbSubscript.setToolTip(self.tr("Shortcode Subscript"))
        self.tbSubscript.clicked.connect(qtLambda(self.requestDocAction.emit, nwDocAction.SC_SUB))

        # Assemble
        # ========

        self.outerBox = QVBoxLayout()
        self.outerBox.addWidget(self.tbBoldMD)
        self.outerBox.addWidget(self.tbItalicMD)
        self.outerBox.addWidget(self.tbStrikeMD)
        self.outerBox.addWidget(self.tbMarkMD)
        self.outerBox.addSpacing(4)
        self.outerBox.addWidget(self.tbBold)
        self.outerBox.addWidget(self.tbItalic)
        self.outerBox.addWidget(self.tbStrike)
        self.outerBox.addWidget(self.tbUnderline)
        self.outerBox.addWidget(self.tbMark)
        self.outerBox.addWidget(self.tbSuperscript)
        self.outerBox.addWidget(self.tbSubscript)
        self.outerBox.setContentsMargins(4, 4, 4, 4)
        self.outerBox.setSpacing(4)

        self.setLayout(self.outerBox)
        self.updateTheme()

        # Starts as Invisible
        self.setVisible(False)

        logger.debug("Ready: GuiDocToolBar")

    def updateTheme(self) -> None:
        """Initialise GUI elements that depend on specific settings."""
        logger.debug("Theme Update: GuiDocToolBar")

        syntax = SHARED.theme.syntaxTheme
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, syntax.back)
        palette.setColor(QPalette.ColorRole.WindowText, syntax.text)
        palette.setColor(QPalette.ColorRole.Text, syntax.text)
        self.setPalette(palette)

        self.tbBoldMD.setThemeIcon("fmt_bold", "markdown")
        self.tbItalicMD.setThemeIcon("fmt_italic", "markdown")
        self.tbStrikeMD.setThemeIcon("fmt_strike", "markdown")
        self.tbMarkMD.setThemeIcon("fmt_mark", "markdown")
        self.tbBold.setThemeIcon("fmt_bold", "shortcode")
        self.tbItalic.setThemeIcon("fmt_italic", "shortcode")
        self.tbStrike.setThemeIcon("fmt_strike", "shortcode")
        self.tbUnderline.setThemeIcon("fmt_underline", "shortcode")
        self.tbMark.setThemeIcon("fmt_mark", "shortcode")
        self.tbSuperscript.setThemeIcon("fmt_superscript", "shortcode")
        self.tbSubscript.setThemeIcon("fmt_subscript", "shortcode")
