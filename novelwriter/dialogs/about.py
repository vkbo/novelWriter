"""
novelWriter – GUI About Box
===========================
The about novelWriter dialog box

File History:
Created: 2020-05-21 [0.5.2]

This file is a part of novelWriter
Copyright 2018–2023, Veronica Berglyd Olsen

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

import logging
import novelwriter

from datetime import datetime

from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    qApp, QDialog, QHBoxLayout, QVBoxLayout, QDialogButtonBox, QTabWidget,
    QTextBrowser, QLabel
)

from novelwriter.common import readTextFile

logger = logging.getLogger(__name__)


class GuiAbout(QDialog):

    def __init__(self, mainGui):
        super().__init__(parent=mainGui)

        logger.debug("Initialising GuiAbout ...")
        self.setObjectName("GuiAbout")

        self.mainConf  = novelwriter.CONFIG
        self.mainGui   = mainGui
        self.mainTheme = mainGui.mainTheme

        self.outerBox = QVBoxLayout()
        self.innerBox = QHBoxLayout()
        self.innerBox.setSpacing(self.mainConf.pxInt(16))

        self.setWindowTitle(self.tr("About novelWriter"))
        self.setMinimumWidth(self.mainConf.pxInt(650))
        self.setMinimumHeight(self.mainConf.pxInt(600))

        nPx = self.mainConf.pxInt(96)
        self.nwIcon = QLabel()
        self.nwIcon.setPixmap(self.mainGui.mainTheme.getPixmap("novelwriter", (nPx, nPx)))
        self.lblName = QLabel("<b>novelWriter</b>")
        self.lblVers = QLabel(f"v{novelwriter.__version__}")
        self.lblDate = QLabel(datetime.strptime(novelwriter.__date__, "%Y-%m-%d").strftime("%x"))

        self.leftBox = QVBoxLayout()
        self.leftBox.setSpacing(self.mainConf.pxInt(4))
        self.leftBox.addWidget(self.nwIcon,  0, Qt.AlignCenter)
        self.leftBox.addWidget(self.lblName, 0, Qt.AlignCenter)
        self.leftBox.addWidget(self.lblVers, 0, Qt.AlignCenter)
        self.leftBox.addWidget(self.lblDate, 0, Qt.AlignCenter)
        self.leftBox.addStretch(1)
        self.innerBox.addLayout(self.leftBox)

        # Pages
        self.pageAbout = QTextBrowser()
        self.pageAbout.setOpenExternalLinks(True)
        self.pageAbout.document().setDocumentMargin(self.mainConf.pxInt(16))

        self.pageNotes = QTextBrowser()
        self.pageNotes.setOpenExternalLinks(True)
        self.pageNotes.document().setDocumentMargin(self.mainConf.pxInt(16))

        self.pageCredits = QTextBrowser()
        self.pageCredits.setOpenExternalLinks(True)
        self.pageCredits.document().setDocumentMargin(self.mainConf.pxInt(16))

        self.pageLicense = QTextBrowser()
        self.pageLicense.setOpenExternalLinks(True)
        self.pageLicense.document().setDocumentMargin(self.mainConf.pxInt(16))

        # Main Tab Area
        self.tabBox = QTabWidget()
        self.tabBox.addTab(self.pageAbout, self.tr("About"))
        self.tabBox.addTab(self.pageNotes, self.tr("Release"))
        self.tabBox.addTab(self.pageCredits, self.tr("Credits"))
        self.tabBox.addTab(self.pageLicense, self.tr("Licence"))
        self.innerBox.addWidget(self.tabBox)

        # OK Button
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        self.buttonBox.accepted.connect(self._doClose)

        self.outerBox.addLayout(self.innerBox)
        self.outerBox.addWidget(self.buttonBox)
        self.setLayout(self.outerBox)

        logger.debug("GuiAbout initialisation complete")

        return

    def populateGUI(self):
        """Populate tabs with text.
        """
        qApp.setOverrideCursor(QCursor(Qt.WaitCursor))
        self._setStyleSheet()
        self._fillAboutPage()
        self._fillNotesPage()
        self._fillCreditsPage()
        self._fillLicensePage()
        qApp.restoreOverrideCursor()
        return

    def showReleaseNotes(self):
        """Show the release notes.
        """
        self.tabBox.setCurrentWidget(self.pageNotes)
        return

    ##
    #  Internal Functions
    ##

    def _fillAboutPage(self):
        """Generate the content for the About page.
        """
        aboutMsg = (
            "<h2>{title1}</h2>"
            "<p>{copy}</p>"
            "<p>{link}</p>"
            "<p>{intro}</p>"
            "<p>{license1}</p>"
            "<p>{license2}</p>"
            "<p>{license3}</p>"
        ).format(
            title1=self.tr("About novelWriter"),
            copy=novelwriter.__copyright__,
            link=self.tr("Website: {0}").format(
                f"<a href='{novelwriter.__url__}'>{novelwriter.__domain__}</a>"
            ),
            intro=self.tr(
                "novelWriter is a markdown-like text editor designed for organising and "
                "writing novels. It is written in Python 3 with a Qt5 GUI, using PyQt5."
            ),
            license1=self.tr(
                "novelWriter is free software: you can redistribute it and/or modify it "
                "under the terms of the GNU General Public License as published by the "
                "Free Software Foundation, either version 3 of the License, or (at your "
                "option) any later version."
            ),
            license2=self.tr(
                "novelWriter is distributed in the hope that it will be useful, but "
                "WITHOUT ANY WARRANTY; without even the implied warranty of "
                "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE."
            ),
            license3=self.tr(
                "See the Licence tab for the full licence text, or visit the "
                "GNU website at {0} for more details."
            ).format(
                "<a href='https://www.gnu.org/licenses/gpl-3.0.html'>GPL v3.0</a>"
            ),
        )

        self.pageAbout.setHtml(aboutMsg)

        return

    def _fillNotesPage(self):
        """Load the content for the Release Notes page.
        """
        docPath = self.mainConf.assetPath("text") / "release_notes.htm"
        docText = readTextFile(docPath)
        if docText:
            self.pageNotes.setHtml(docText)
        else:
            self.pageNotes.setHtml("Error loading release notes text ...")
        return

    def _fillCreditsPage(self):
        """Load the content for the Credits page.
        """
        docPath = self.mainConf.assetPath("text") / "credits_en.htm"
        docText = readTextFile(docPath)
        if docText:
            self.pageCredits.setHtml(docText)
        else:
            self.pageCredits.setHtml("Error loading credits text ...")
        return

    def _fillLicensePage(self):
        """Load the content for the Licence page.
        """
        docPath = self.mainConf.assetPath("text") / "gplv3_en.htm"
        docText = readTextFile(docPath)
        if docText:
            self.pageLicense.setHtml(docText)
        else:
            self.pageLicense.setHtml("Error loading licence text ...")
        return

    def _setStyleSheet(self):
        """Set stylesheet for all browser tabs
        """
        styleSheet = (
            "h1, h2, h3, h4 {{"
            "  color: rgb({hColR},{hColG},{hColB});"
            "}}\n"
            "a {{"
            "  color: rgb({hColR},{hColG},{hColB});"
            "}}\n"
            ".alt {{"
            "  color: rgb({kColR},{kColG},{kColB});"
            "}}\n"
        ).format(
            hColR=self.mainGui.mainTheme.colHead[0],
            hColG=self.mainGui.mainTheme.colHead[1],
            hColB=self.mainGui.mainTheme.colHead[2],
            kColR=self.mainTheme.colKey[0],
            kColG=self.mainTheme.colKey[1],
            kColB=self.mainTheme.colKey[2],
        )
        self.pageAbout.document().setDefaultStyleSheet(styleSheet)
        self.pageNotes.document().setDefaultStyleSheet(styleSheet)
        self.pageCredits.document().setDefaultStyleSheet(styleSheet)
        self.pageLicense.document().setDefaultStyleSheet(styleSheet)

        return

    def _doClose(self):
        self.close()
        return

# END Class GuiAbout
