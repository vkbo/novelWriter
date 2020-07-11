# -*- coding: utf-8 -*-
"""novelWriter GUI New Project Wizard

 novelWriter – GUI New project Wizard
======================================
 Class holding the new project wizard dialog

 File History:
 Created: 2020-07-11 [0.10.1]

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

from PyQt5.QtWidgets import QWizard

logger = logging.getLogger(__name__)

class GuiProjectWizard(QWizard):

    def __init__(self, theParent):
        QWizard.__init__(self, theParent)

        logger.debug("Initialising GuiProjectWizard ...")

        self.mainConf  = nw.CONFIG
        self.theParent = theParent

        logger.debug("GuiProjectWizard initialisation complete")

        return

# END Class GuiProjectWizard
