# -*- coding: utf-8 -*-
"""novelWriter GUI Project Outline

 novelWriter – GUI Project Outline
===================================
 Class holding the project outline view

 File History:
 Created: 2020-06-02 [0.7.0]

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
    QWidget
)

logger = logging.getLogger(__name__)

class GuiOutlineDetails(QWidget):

    def __init__(self, theParent):
        QWidget.__init__(self, theParent)

        logger.debug("Initialising GuiOutlineDetails ...")

        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theProject = theParent.theProject
        self.theTheme   = theParent.theTheme
        self.theIndex   = theParent.theIndex
        self.optState   = theParent.theProject.optState

        logger.debug("GuiOutlineDetails initialisation complete")

        return

# END Class GuiOutlineDetails
