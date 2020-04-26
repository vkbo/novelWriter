# -*- coding: utf-8 -*-
"""novelWriter GUI Document Title Bar

 novelWriter – GUI Document Title Bar
======================================
 Class holding the document title bar class

 File History:
 Created: 2020-04-25 [0.4.5]

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
 along with this program. If not, see https://www.gnu.org/licenses/.
"""

import logging
import nw

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QLabel

logger = logging.getLogger(__name__)

class GuiDocTitleBar(QLabel):

    def __init__(self, theParent):
        QLabel.__init__(self, theParent)

        logger.debug("Initialising DocTitleBar ...")

        self.mainConf  = nw.CONFIG
        self.theParent = theParent
        self.theTheme  = theParent.theTheme

        self.setText("A > B > C")
        self.setContentsMargins(8,2,8,2)
        self.setAutoFillBackground(True)
        self.setAlignment(Qt.AlignCenter)
        docPalette = self.palette()
        docPalette.setColor(QPalette.Window, QColor(*self.theTheme.colBack))
        docPalette.setColor(QPalette.Text, QColor(*self.theTheme.colText))
        self.setPalette(docPalette)

        logger.debug("DocTitleBar initialisation complete")

        return

# END Class GuiDocTitleBar
