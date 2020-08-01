# -*- coding: utf-8 -*-
"""novelWriter Help Dialog Class

 novelWriter – Help Dialog Class
=================================
 A dialog to show all the various help files

 File History:
 Created: 2020-07-30 [0.10.2] GuiHelp

 This file is a part of novelWriter
 Copyright 2020, Veronica Berglyd Olsen

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
import nw

from os import path

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QDialogButtonBox, QLabel
)

logger = logging.getLogger(__name__)

class GuiHelp(QDialog):

    def __init__(self, theParent):
        QDialog.__init__(self, theParent)

        logger.debug("Initialising GuiHelp ...")

        self.mainConf  = nw.CONFIG
        self.theParent = theParent
        self.theTheme  = theParent.theTheme

        self.setModal(False)
        self.setWindowTitle("Documentation")

        self.outerBox = QVBoxLayout()
        self.innerBox = QHBoxLayout()

        wW = self.mainConf.pxInt(700)
        wH = self.mainConf.pxInt(750)
        self.setMinimumWidth(self.mainConf.pxInt(600))
        self.setMinimumHeight(self.mainConf.pxInt(600))
        self.resize(*self.mainConf.getHelpWinSize())

        # Nav Buttons
        self.navButtons = QVBoxLayout()

        labelStyle = (
            "QLabel {{padding: {vM}px {hM}px;}}"
            "QLabel:hover {{background: rgba({bR},{bG},{bB},0.2);}}"
        ).format(
            hM = self.mainConf.pxInt(2),
            vM = self.mainConf.pxInt(4),
            bR = self.theTheme.colText[0],
            bG = self.theTheme.colText[1],
            bB = self.theTheme.colText[2],
        )

        self.navHeader = QLabel("<b>Table of Contents</b>")

        navLinks = {
            "quickref.htm"  : "Quick Reference",
            "projects.htm"  : "Project Structure",
            "tagsrefs.htm"  : "Tags & References",
            "tools.htm"     : "Additional Tools",
            "technical.htm" : "Technical Info",
        }

        self.navButtons.addWidget(self.navHeader)
        self.navButtons.addSpacing(self.mainConf.pxInt(4))
        for aTag, aName in navLinks.items():
            navLabel = QLabel("&raquo;&nbsp;<a href='%s'>%s</a>" % (aTag, aName))
            navLabel.setStyleSheet(labelStyle)
            navLabel.linkActivated.connect(self._doLoadDocument)
            self.navButtons.addWidget(navLabel)

        self.navButtons.addStretch(1)
        self.navButtons.setSpacing(0)

        # Central Widget
        self.webPage = QWebEngineView()
        self.webPage.loadFinished.connect(self._pageLoaded)

        # OK Button
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        self.buttonBox.accepted.connect(self._doClose)

        # Assemble
        self.innerBox.addLayout(self.navButtons, 0)
        self.innerBox.addWidget(self.webPage, 1)
        self.innerBox.setSpacing(self.mainConf.pxInt(12))

        self.outerBox.addLayout(self.innerBox, 1)
        self.outerBox.addWidget(self.buttonBox, 0)
        self.setLayout(self.outerBox)

        logger.debug("GuiHelp initialisation complete")

        self.loadDocument("quickref.htm")

        return

    def loadDocument(self, theLink, theAnchor=None):
        """Load a help document based on a link keyword, and optionally
        navigate to a specific heading.
        """
        theFile = path.join(
            self.mainConf.assetPath, "help", self.mainConf.guiLang, theLink
        )
        theUrl = QUrl().fromLocalFile(theFile)
        self.webPage.setUrl(theUrl)
        return True

    ##
    #  Events
    ##

    def closeEvent(self, theEvent):
        """Save the window size before closing it.
        """
        self.mainConf.setHelpWinSize([self.width(), self.height()])
        QDialog.closeEvent(self, theEvent)
        return

    ##
    #  Slots
    ##

    def _pageLoaded(self, isLoaded):
        """Triggered when a page is done loading.
        """
        if isLoaded:
            self.setWindowTitle("Documentation › %s" % self.webPage.title())
        return

    def _doLoadDocument(self, theLink):
        """Slot for connecting the ToC entry to a document.
        """
        self.loadDocument(theLink)
        return

    def _doClose(self):
        """Close the dialog.
        """
        self.close()
        return

# END Class GuiHelp
