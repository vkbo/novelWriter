# -*- coding: utf-8 -*-
"""novelWriter GUI Build Novel

 novelWriter – GUI Build Novel
===============================
 Class holding the build novel window

 File History:
 Created: 2020-05-09 [0.5]

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

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextOption, QPalette, QColor
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextBrowser
)

from nw.constants import nwConst, nwFiles, nwAlert

logger = logging.getLogger(__name__)

class GuiBuildNovel(QDialog):

    def __init__(self, theParent, theProject):
        QDialog.__init__(self, theParent)

        logger.debug("Initialising GuiBuildNovel ...")

        self.mainConf   = nw.CONFIG
        self.theProject = theProject
        self.theParent  = theParent
        self.optState   = self.theProject.optState

        self.setWindowTitle("Build Project")
        self.setMinimumWidth(400)
        self.setMinimumHeight(400)

        self.outerBox = QVBoxLayout()
        self.innerBox = QHBoxLayout()

        self.docView = GuiBuildNovelDocView(self, self.theProject)

        # Assemble GUI
        self.innerBox.addWidget(self.docView)
        self.outerBox.addLayout(self.innerBox)
        self.setLayout(self.outerBox)

        self.show()

        logger.debug("GuiBuildNovel initialisation complete")

        return

# END Class GuiBuildNovel

class GuiBuildNovelDocView(QTextBrowser):

    def __init__(self, theParent, theProject):
        QTextBrowser.__init__(self, theParent)

        logger.debug("Initialising GuiBuildNovelDocView ...")

        self.mainConf   = nw.CONFIG
        self.theProject = theProject
        self.theParent  = theParent

        self.qDocument = self.document()
        self.setMinimumWidth(300)
        self.setOpenExternalLinks(False)

        theOpt = QTextOption()
        if self.mainConf.doJustify:
            theOpt.setAlignment(Qt.AlignJustify)
        self.qDocument.setDefaultTextOption(theOpt)

        docPalette = self.palette()
        docPalette.setColor(QPalette.Base, QColor(255, 255, 255))
        docPalette.setColor(QPalette.Text, QColor(  0,   0,   0))
        self.setPalette(docPalette)

        self.setHtml("<h1>Hello World</h1><p>Some text ...</p>")

        self.show()

        logger.debug("GuiBuildNovelDocView initialisation complete")

        return

# END Class GuiBuildNovelDocView
