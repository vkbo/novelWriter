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

from typing import TYPE_CHECKING

from PyQt6.QtCore import QTimer, pyqtSlot
from PyQt6.QtGui import QPalette
from PyQt6.QtWidgets import QApplication, QDialogButtonBox, QHBoxLayout, QTextEdit, QVBoxLayout, QWidget

from novelwriter import CONFIG, SHARED
from novelwriter.common import fontMatcher
from novelwriter.editor.highlighter import GuiDocHighlighter
from novelwriter.enum import nwStandardButton
from novelwriter.extensions.configlayout import NColorLabel
from novelwriter.extensions.modified import NDialog
from novelwriter.extensions.progressbars import NProgressSimple
from novelwriter.formats.fromqdoc import FromQTextDocument
from novelwriter.types import QtAccepted, QtRoleAccept, QtRoleReject

if TYPE_CHECKING:
    from PyQt6.QtGui import QShowEvent

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

        options = SHARED.project.options
        self.resize(
            options.getInt("GuiPasteDialog", "winWidth", 800),
            options.getInt("GuiPasteDialog", "winHeight", 600),
        )

        # Rich Text Preview
        self.richTitle = NColorLabel(
            self.tr("Pasted Text"),
            self,
            color=SHARED.theme.helpText,
            scale=NColorLabel.HEADER_SCALE,
        )

        self.richView = QTextEdit(self)
        self.richView.setReadOnly(True)
        self.richView.setHtml(html)
        self._applyTextTheme(self.richView)

        # Plain Text Result
        self.plainTitle = NColorLabel(
            self.tr("Converted Text"),
            self,
            color=SHARED.theme.helpText,
            scale=NColorLabel.HEADER_SCALE,
        )

        self.plainEdit = QTextEdit(self)
        self.plainEdit.setAcceptRichText(False)
        self.plainEdit.setPlaceholderText(self.tr("Converting ..."))
        self.plainEdit.setEnabled(False)
        self._applyTextTheme(self.plainEdit)

        if plainDoc := self.plainEdit.document():
            self.highlighter = GuiDocHighlighter(plainDoc, withBlockData=False)
            self.highlighter.enableDetached()

        # Conversion Progress
        self.convProgress = NProgressSimple(self)
        self.convProgress.setMinimum(0)
        self.convProgress.setValue(0)
        self.convProgress.setTextVisible(False)
        self.convProgress.setFixedHeight(4)

        # Buttons
        self.btnInsert = SHARED.theme.getStandardButton(nwStandardButton.INSERT, self)
        self.btnInsert.setEnabled(False)
        self.btnInsert.clicked.connect(self.accept)

        self.btnCancel = SHARED.theme.getStandardButton(nwStandardButton.CANCEL, self)
        self.btnCancel.clicked.connect(self.reject)

        self.btnBox = QDialogButtonBox(self)
        self.btnBox.addButton(self.btnInsert, QtRoleAccept)
        self.btnBox.addButton(self.btnCancel, QtRoleReject)

        # Assemble
        self.richBox = QVBoxLayout()
        self.richBox.addWidget(self.richTitle, 0)
        self.richBox.addWidget(self.richView, 1)
        self.richBox.setSpacing(4)
        self.richBox.setContentsMargins(0, 0, 0, 0)

        self.plainBox = QVBoxLayout()
        self.plainBox.addWidget(self.plainTitle, 0)
        self.plainBox.addWidget(self.plainEdit, 1)
        self.plainBox.setSpacing(4)
        self.plainBox.setContentsMargins(8, 0, 0, 0)

        self.splitBox = QHBoxLayout()
        self.splitBox.addLayout(self.richBox, 1)
        self.splitBox.addLayout(self.plainBox, 1)
        self.splitBox.setSpacing(4)
        self.splitBox.setContentsMargins(0, 0, 0, 0)

        self.outerBox = QVBoxLayout()
        self.outerBox.addLayout(self.splitBox, 1)
        self.outerBox.addSpacing(2)
        self.outerBox.addWidget(self.convProgress, 0)
        self.outerBox.addSpacing(8)
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
        dialog._saveSettings()
        text = dialog.text
        accepted = dialog.result() == QtAccepted
        dialog.softDelete()
        return text, accepted

    ##
    #  Events
    ##

    def showEvent(self, event: QShowEvent) -> None:
        """Kick off the conversion once the dialog is visible."""
        super().showEvent(event)
        QTimer.singleShot(0, self._runConversion)

    ##
    #  Private Slots
    ##

    @pyqtSlot()
    def _runConversion(self) -> None:
        """Convert the rich text preview to novelWriter's text format,
        updating the progress bar as it goes.
        """
        if not (document := self.richView.document()):
            return

        converter = FromQTextDocument(document)
        self.convProgress.setMaximum(max(document.blockCount(), 1))
        self.convProgress.setValue(0)
        QApplication.processEvents()

        for count in converter.doConvert():
            self.convProgress.setValue(count)
            QApplication.processEvents()

        self.plainEdit.setPlainText(converter.resultText().strip())
        self.plainEdit.setEnabled(True)
        self.plainEdit.setFocus()
        self.btnInsert.setEnabled(True)

        QTimer.singleShot(3000, self._resetProgress)

    @pyqtSlot()
    def _resetProgress(self) -> None:
        """Set the progress bar back to 0."""
        self.convProgress.setValue(0)

    ##
    #  Internal Functions
    ##

    def _saveSettings(self) -> None:
        """Save the dialog's GUI settings."""
        logger.debug("Saving State: GuiPasteDialog")
        options = SHARED.project.options
        options.setValue("GuiPasteDialog", "winWidth", self.width())
        options.setValue("GuiPasteDialog", "winHeight", self.height())
        options.saveSettings()

    def _applyTextTheme(self, widget: QTextEdit) -> None:
        """Set the text font and syntax background colours on a
        document panel to match the main editor.
        """
        syntax = SHARED.theme.syntaxTheme
        font = fontMatcher(CONFIG.textFont)
        widget.setFont(font)
        if document := widget.document():
            document.setDefaultFont(font)

        palette = widget.palette()
        palette.setColor(QPalette.ColorRole.Window, syntax.back)
        palette.setColor(QPalette.ColorRole.Base, syntax.back)
        palette.setColor(QPalette.ColorRole.Text, syntax.text)
        widget.setPalette(palette)

        if viewport := widget.viewport():
            vPalette = viewport.palette()
            vPalette.setColor(QPalette.ColorRole.Base, syntax.back)
            vPalette.setColor(QPalette.ColorRole.Text, syntax.text)
            viewport.setPalette(vPalette)
