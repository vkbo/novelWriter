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

from datetime import datetime

from PyQt5.QtGui import QCloseEvent, QColor
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog, QDialogButtonBox, QHBoxLayout, QLabel, QTextBrowser, QVBoxLayout,
    QWidget
)

from novelwriter import CONFIG, SHARED, __version__, __date__
from novelwriter.common import formatVersion, readTextFile
from novelwriter.constants import nwConst, nwUnicode
from novelwriter.extensions.configlayout import NColourLabel

logger = logging.getLogger(__name__)


class GuiAbout(QDialog):

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

        self.nwInfo = QLabel(self.tr("Version {0} {1} Released on {2} {1} {3}").format(
            formatVersion(__version__), nwUnicode.U_ENDASH,
            datetime.strptime(__date__, "%Y-%m-%d").strftime("%x"),
            "<a href='{0}'>{1}</a>".format(nwConst.URL_RELEASES, self.tr("Release Notes"))
        ))
        self.nwInfo.setOpenExternalLinks(True)

        self.nwLicence = QLabel(self.tr("This application is licenced under {0}".format(
            "<a href='https://www.gnu.org/licenses/gpl-3.0.html'>GPL v3.0</a>"
        )))
        self.nwLicence.setOpenExternalLinks(True)

        # Credits
        self.lblCredits = NColourLabel(
            self.tr("Credits"), SHARED.theme.helpText,
            scale=NColourLabel.HEADER_SCALE, parent=self
        )

        self.txtCredits = QTextBrowser(self)
        self.txtCredits.setOpenExternalLinks(True)
        self.txtCredits.document().setDocumentMargin(0)
        self.txtCredits.setViewportMargins(0, hA, hA, 0)

        # Buttons
        self.btnBox = QDialogButtonBox(QDialogButtonBox.Close, self)
        self.btnBox.rejected.connect(self.close)

        # Assemble
        self.innerBox = QVBoxLayout()
        self.innerBox.addSpacing(hB)
        self.innerBox.addWidget(self.nwLabel)
        self.innerBox.addWidget(self.nwInfo)
        self.innerBox.addWidget(self.nwLicence)
        self.innerBox.addSpacing(hA)
        self.innerBox.addWidget(self.lblCredits)
        self.innerBox.addWidget(self.txtCredits)
        self.innerBox.addSpacing(hB)
        self.innerBox.addWidget(self.btnBox)

        topRight = Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight

        self.outerBox = QHBoxLayout()
        self.outerBox.addWidget(self.nwLogo, 0, topRight)
        self.outerBox.addLayout(self.innerBox, 1)

        self.setLayout(self.outerBox)
        self.setSizeGripEnabled(True)
        self._setStyleSheet()

        logger.debug("Ready: GuiAbout")

        return

    def __del__(self) -> None:  # pragma: no cover
        logger.debug("Delete: GuiAbout")
        return

    def populateGUI(self) -> None:
        """Populate tabs with text."""
        self._fillCreditsPage()
        return

    ##
    #  Events
    ##

    def closeEvent(self, event: QCloseEvent) -> None:
        """Capture the close event and perform cleanup."""
        event.accept()
        self.deleteLater()
        return

    ##
    #  Internal Functions
    ##

    def _fillCreditsPage(self) -> None:
        """Load the content for the Credits page."""
        docPath = CONFIG.assetPath("text") / "credits_en.htm"
        docText = readTextFile(docPath)
        if docText:
            self.txtCredits.setHtml(docText)
        else:
            self.txtCredits.setHtml("Error loading credits text ...")
        return

    def _setStyleSheet(self) -> None:
        """Set stylesheet for all browser tabs."""
        colHead = SHARED.theme.colHead
        colKey = SHARED.theme.colKey
        styleSheet = (
            "h1, h2, h3, h4 {{"
            "  color: rgb({hColR}, {hColG}, {hColB});"
            "}}\n"
            "a {{"
            "  color: rgb({hColR}, {hColG}, {hColB});"
            "}}\n"
            ".alt {{"
            "  color: rgb({kColR}, {kColG}, {kColB});"
            "}}\n"
        ).format(
            hColR=colHead.red(),
            hColG=colHead.green(),
            hColB=colHead.blue(),
            kColR=colKey.red(),
            kColG=colKey.green(),
            kColB=colKey.blue(),
        )
        self.txtCredits.document().setDefaultStyleSheet(styleSheet)

        baseCol = self.palette().window().color()
        self.txtCredits.setStyleSheet((
            "QTextBrowser {{border: none; background: rgb({r},{g},{b});}} "
        ).format(r=baseCol.red(), g=baseCol.green(), b=baseCol.blue()))

        return

# END Class GuiAbout
