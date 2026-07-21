"""
novelWriter – GUI Paste Dialog
==============================

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

from PyQt6.QtGui import QTextDocument
from PyQt6.QtWidgets import QDialogButtonBox, QHBoxLayout, QTextEdit, QVBoxLayout, QWidget

from novelwriter import SHARED
from novelwriter.enum import nwStandardButton
from novelwriter.extensions.modified import NDialog
from novelwriter.types import QtAccepted, QtRoleAccept, QtRoleReject

logger = logging.getLogger(__name__)


class GuiPasteDialog(NDialog):
    """GUI: Paste Rich Text Dialog."""

    def __init__(self, parent: QWidget, html: str) -> None:
        super().__init__(parent=parent)

        logger.debug("Create: GuiPasteDialog")
        self.setObjectName("GuiPasteDialog")
        self.setWindowTitle(self.tr("Paste Formatted Text"))

        self.setMinimumWidth(600)
        self.setMinimumHeight(400)

        # Rich Text Preview
        self.richView = QTextEdit(self)
        self.richView.setReadOnly(True)
        self.richView.setHtml(html)

        # Plain Text Result
        self.plainEdit = QTextEdit(self)
        self.plainEdit.setAcceptRichText(False)
        self.plainEdit.setPlainText(self._toMarkdown(html))

        self.splitBox = QHBoxLayout()
        self.splitBox.addWidget(self.richView, 1)
        self.splitBox.addWidget(self.plainEdit, 1)

        # Buttons
        self.btnInsert = SHARED.theme.getStandardButton(nwStandardButton.INSERT, self)
        self.btnInsert.clicked.connect(self.accept)

        self.btnCancel = SHARED.theme.getStandardButton(nwStandardButton.CANCEL, self)
        self.btnCancel.clicked.connect(self.reject)

        self.btnBox = QDialogButtonBox(self)
        self.btnBox.addButton(self.btnInsert, QtRoleAccept)
        self.btnBox.addButton(self.btnCancel, QtRoleReject)

        # Assemble
        self.outerBox = QVBoxLayout()
        self.outerBox.setSpacing(12)
        self.outerBox.addLayout(self.splitBox, 1)
        self.outerBox.addWidget(self.btnBox, 0)

        self.setLayout(self.outerBox)

        logger.debug("Ready: GuiPasteDialog")

    def __del__(self) -> None:  # pragma: no cover
        """Class destructor."""
        logger.debug("Delete: GuiPasteDialog")

    @property
    def text(self) -> str:
        """Return the content of the plain text panel."""
        return self.plainEdit.toPlainText()

    @classmethod
    def getText(cls, parent: QWidget, html: str) -> tuple[str, bool]:
        """Pop the dialog and return the result."""
        dialog = cls(parent, html)
        dialog.exec()
        text = dialog.text
        accepted = dialog.result() == QtAccepted
        dialog.softDelete()
        return text, accepted

    ##
    #  Internal Functions
    ##

    def _toMarkdown(self, html: str) -> str:
        """Convert a HTML fragment to Markdown text.

        This is a simple first pass using Qt's built-in converter. A
        more advanced Markdown converter may replace this later.
        """
        document = QTextDocument()
        document.setHtml(html)
        return document.toMarkdown().strip()
