"""
novelWriter – GUI About Box
===========================

File History:
Created: 2020-05-21 [0.5.2] GuiAbout

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

import logging

from PyQt5.QtGui import QCloseEvent, QColor
from PyQt5.QtWidgets import (
    QDialogButtonBox, QHBoxLayout, QLabel, QTextBrowser, QVBoxLayout, QWidget
)

from novelwriter import CONFIG, SHARED
from novelwriter.common import cssCol, readTextFile
from novelwriter.extensions.configlayout import NColourLabel
from novelwriter.extensions.modified import NDialog
from novelwriter.extensions.versioninfo import VersionInfoWidget
from novelwriter.types import QtAlignRightTop, QtDialogClose

logger = logging.getLogger(__name__)


class GuiAbout(NDialog):

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)

        logger.debug("Create: GuiAbout")
        self.setObjectName("GuiAbout")

        self.setWindowTitle(self.tr("About novelWriter"))
        self.resize(CONFIG.pxInt(700), CONFIG.pxInt(500))

        hA = CONFIG.pxInt(8)
        hB = CONFIG.pxInt(16)
        nwH = CONFIG.pxInt(36)
        nwPx = CONFIG.pxInt(128)

        # Logo and Banner
        self.nwImage = SHARED.theme.loadDecoration("nw-text", h=nwH)
        self.bgColor = QColor(255, 255, 255) if SHARED.theme.isLightTheme else QColor(54, 54, 54)

        self.nwLogo = QLabel(self)
        self.nwLogo.setPixmap(SHARED.theme.getPixmap("novelwriter", (nwPx, nwPx)))

        self.nwLabel = QLabel(self)
        self.nwLabel.setPixmap(self.nwImage)

        self.nwInfo = VersionInfoWidget(self)

        self.nwLicence = QLabel(self.tr("This application is licenced under {0}").format(
            "<a href='https://www.gnu.org/licenses/gpl-3.0.html'>GPL v3.0</a>"
        ), self)
        self.nwLicence.setOpenExternalLinks(True)

        # Credits
        self.lblCredits = NColourLabel(
            self.tr("Credits"), self, scale=1.6, bold=True
        )

        self.txtCredits = QTextBrowser(self)
        self.txtCredits.setOpenExternalLinks(True)
        self.txtCredits.document().setDocumentMargin(0)
        self.txtCredits.setViewportMargins(0, hA, hA, 0)

        # Buttons
        self.btnBox = QDialogButtonBox(QtDialogClose, self)
        self.btnBox.rejected.connect(self.reject)

        # Assemble
        self.innerBox = QVBoxLayout()
        self.innerBox.addSpacing(hB)
        self.innerBox.addWidget(self.nwLabel)
        self.innerBox.addWidget(self.nwInfo)
        self.innerBox.addSpacing(hA)
        self.innerBox.addWidget(self.nwLicence)
        self.innerBox.addSpacing(hA)
        self.innerBox.addWidget(self.lblCredits)
        self.innerBox.addWidget(self.txtCredits)
        self.innerBox.addSpacing(hB)
        self.innerBox.addWidget(self.btnBox)

        self.outerBox = QHBoxLayout()
        self.outerBox.addWidget(self.nwLogo, 0, QtAlignRightTop)
        self.outerBox.addLayout(self.innerBox, 1)

        self.setLayout(self.outerBox)
        self.setSizeGripEnabled(True)

        self._setStyleSheet()
        self._fillCreditsPage()

        logger.debug("Ready: GuiAbout")

        return

    def __del__(self) -> None:  # pragma: no cover
        logger.debug("Delete: GuiAbout")
        return

    ##
    #  Events
    ##

    def closeEvent(self, event: QCloseEvent) -> None:
        """Capture the close event and perform cleanup."""
        event.accept()
        self.softDelete()
        return

    ##
    #  Internal Functions
    ##

    def _fillCreditsPage(self) -> None:
        """Load the content for the Credits page."""
        if html := readTextFile(CONFIG.assetPath("text") / "credits_en.htm"):
            self.txtCredits.setHtml(html)
        else:
            self.txtCredits.setHtml("Error loading credits text ...")
        return

    def _setStyleSheet(self) -> None:
        """Set stylesheet text document."""
        baseCol = cssCol(self.palette().window().color())
        self.txtCredits.setStyleSheet(
            f"QTextBrowser {{border: none; background: {baseCol};}} "
        )
        return
