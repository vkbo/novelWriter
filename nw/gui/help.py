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

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog
)

logger = logging.getLogger(__name__)

class GuiHelp(QDialog):

    def __init__(self, theParent):
        QDialog.__init__(self, theParent)

        logger.debug("Initialising GuiHelp ...")

        self.mainConf  = nw.CONFIG
        self.theParent = theParent
        self.theTheme  = theParent.theTheme

        logger.debug("GuiHelp initialisation complete")

        return

# END Class GuiHelp
