# -*- coding: utf-8 -*-
"""novelWriter GUI About Box

 novelWriter – GUI About Box
=============================
 The about novelWriter dialog box

 File History:
 Created: 2020-05-21 [0.5.2]

 This file is a part of novelWriter
 Copyright 2018–2020, Veronica Berglyd Olsen

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

import nw
import logging
import os

from datetime import datetime

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog, QHBoxLayout, QVBoxLayout, QDialogButtonBox, QTabWidget,
    QTextBrowser, QLabel
)

logger = logging.getLogger(__name__)

class GuiAbout(QDialog):

    def __init__(self, theParent):
        QDialog.__init__(self, theParent)

        logger.debug("Initialising GuiAbout ...")
        self.setObjectName("GuiAbout")

        self.mainConf  = nw.CONFIG
        self.theParent = theParent
        self.theTheme  = theParent.theTheme

        self.outerBox = QVBoxLayout()
        self.innerBox = QHBoxLayout()
        self.innerBox.setSpacing(self.mainConf.pxInt(16))

        self.setWindowTitle("About %s" % self.mainConf.appName)
        self.setMinimumWidth(self.mainConf.pxInt(650))
        self.setMinimumHeight(self.mainConf.pxInt(600))

        nPx = self.mainConf.pxInt(96)
        self.nwIcon = QLabel()
        self.nwIcon.setPixmap(self.theParent.theTheme.getPixmap("novelwriter", (nPx, nPx)))
        self.lblName = QLabel("<b>%s</b>" % self.mainConf.appName)
        self.lblVers = QLabel("v%s" % nw.__version__)
        self.lblDate = QLabel(datetime.strptime(nw.__date__, "%Y-%m-%d").strftime("%x"))

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

        self.pageLicense = QTextBrowser()
        self.pageLicense.setOpenExternalLinks(True)
        self.pageLicense.document().setDocumentMargin(self.mainConf.pxInt(16))

        # Main Tab Area
        self.tabBox = QTabWidget()
        self.tabBox.addTab(self.pageAbout, "About")
        self.tabBox.addTab(self.pageLicense, "License")
        self.innerBox.addWidget(self.tabBox)

        # OK Button
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        self.buttonBox.accepted.connect(self._doClose)

        self.outerBox.addLayout(self.innerBox)
        self.outerBox.addWidget(self.buttonBox)
        self.setLayout(self.outerBox)

        self._setStyleSheet()
        self._fillAboutPage()
        self._fillLicensePage()

        logger.debug("GuiAbout initialisation complete")

        return

    ##
    #  Internal Functions
    ##

    def _fillAboutPage(self):
        """Generate the content for the About page.
        """
        listPrefix = "&nbsp;&nbsp;&bull;&nbsp;&nbsp;"
        aboutMsg   = (
            "<h2>About {name:s}</h2>"
            "<p>{copyright:s}.</p>"
            "<p>Website: <a href='{website:s}'>{domain:s}</a></p>"
            "<p>{name:s} is a markdown-like text editor designed for "
            "organising and writing novels. It is written in Python 3 with a "
            "Qt5 GUI, using PyQt5.</p>"
            "<p>{name:s} is free software: you can redistribute it and/or "
            "modify it under the terms of the GNU General Public License as "
            "published by the Free Software Foundation, either version 3 of "
            "the License, or (at your option) any later version.</p>"
            "<p>{name:s} is distributed in the hope that it will be useful, "
            "but WITHOUT ANY WARRANTY; without even the implied warranty of "
            "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.</p>"
            "<p>See the License tab for the full text, or visit  the GNU website "
            "at <a href='https://www.gnu.org/licenses/gpl-3.0.html'>GPL v3.0</a> "
            "for more details.</p>"
            "<h3>Credits</h3>"
            "<p>{credits:s}</p>"
        ).format(
            name      = self.mainConf.appName,
            copyright = nw.__copyright__,
            website   = nw.__url__,
            domain    = nw.__domain__,
            credits   = "<br/>".join(["%s%s" % (listPrefix, x) for x in nw.__credits__]),
        )

        theTheme = self.theParent.theTheme
        theIcons = self.theParent.theTheme.theIcons
        if theTheme.themeName:
            aboutMsg += (
                "<h4>Theme: {name:s}</h4>"
                "<p>"
                "<b>Author:</b> {author:s}<br/>"
                "<b>Credit:</b> {credit:s}<br/>"
                "<b>License:</b> <a href='{lic_url:s}'>{license:s}</a>"
                "</p>"
            ).format(
                name    = theTheme.themeName,
                author  = theTheme.themeAuthor,
                credit  = theTheme.themeCredit,
                license = theTheme.themeLicense,
                lic_url = theTheme.themeLicenseUrl,
            )
        if theIcons.themeName:
            aboutMsg += (
                "<h4>Icons: {name:s}</h4>"
                "<p>"
                "<b>Author:</b> {author:s}<br/>"
                "<b>Credit:</b> {credit:s}<br/>"
                "<b>License:</b> <a href='{lic_url:s}'>{license:s}</a>"
                "</p>"
            ).format(
                name    = theIcons.themeName,
                author  = theIcons.themeAuthor,
                credit  = theIcons.themeCredit,
                license = theIcons.themeLicense,
                lic_url = theIcons.themeLicenseUrl,
            )
        if theTheme.syntaxName:
            aboutMsg += (
                "<h4>Syntax: {name:s}</h4>"
                "<p>"
                "<b>Author:</b> {author:s}<br/>"
                "<b>Credit:</b> {credit:s}<br/>"
                "<b>License:</b> <a href='{lic_url:s}'>{license:s}</a>"
                "</p>"
            ).format(
                name    = theTheme.syntaxName,
                author  = theTheme.syntaxAuthor,
                credit  = theTheme.syntaxCredit,
                license = theTheme.syntaxLicense,
                lic_url = theTheme.syntaxLicenseUrl,
            )

        self.pageAbout.setHtml(aboutMsg)

        return

    def _fillLicensePage(self):
        """Load the content for the License page.
        """
        docName = "gplv3_%s.htm" % self.mainConf.guiLang
        docPath = os.path.join(self.mainConf.assetPath, "text", docName)
        if os.path.isfile(docPath):
            with open(docPath, mode="r", encoding="utf8") as inFile:
                helpText = inFile.read()
            self.pageLicense.setHtml(helpText)
        else:
            self.pageLicense.setHtml("Error loading license text ...")
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
        ).format(
            hColR = self.theParent.theTheme.colHead[0],
            hColG = self.theParent.theTheme.colHead[1],
            hColB = self.theParent.theTheme.colHead[2],
        )
        self.pageAbout.document().setDefaultStyleSheet(styleSheet)
        # self.pageCredit.document().setDefaultStyleSheet(styleSheet)
        self.pageLicense.document().setDefaultStyleSheet(styleSheet)

        return

    def _doClose(self):
        self.close()
        return

# END Class GuiAbout
