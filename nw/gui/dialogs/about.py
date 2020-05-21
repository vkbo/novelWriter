# -*- coding: utf-8 -*-
"""novelWriter GUI About Box

 novelWriter – GUI About Box
=============================
 The about novelWriter dialog box

 File History:
 Created: 2020-05-21 [0.5.2]

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
from PyQt5.QtWidgets import (
    QDialog, QHBoxLayout, QVBoxLayout, QDialogButtonBox
)

logger = logging.getLogger(__name__)

class GuiAbout(QDialog):

    def __init__(self, theParent):
        QDialog.__init__(self, theParent)

        logger.debug("Initialising GuiAbout ...")

        self.mainConf = nw.CONFIG

        self.outerBox = QVBoxLayout()
        self.innerBox = QHBoxLayout()

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        self.buttonBox.accepted.connect(self._doClose)

        self.outerBox.addLayout(self.innerBox)
        self.outerBox.addWidget(self.buttonBox)
        self.setLayout(self.outerBox)

        logger.debug("GuiAbout initialisation complete")

        return

    ##
    #  Internal Functions
    ##

    def _doClose(self):
        self.close()
        return

# END Class GuiAbout
