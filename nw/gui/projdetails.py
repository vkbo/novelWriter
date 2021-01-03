# -*- coding: utf-8 -*-
"""novelWriter GUI Project Details

 novelWriter – GUI Project Details
===================================
 Class holding the project details dialog

 File History:
 Created: 2021-01-03 [1.0a0]

 This file is a part of novelWriter
 Copyright 2018–2021, Veronica Berglyd Olsen

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

from PyQt5.QtWidgets import QDialogButtonBox

from nw.gui.custom import PagedDialog

logger = logging.getLogger(__name__)

class GuiProjectDetails(PagedDialog):

    def __init__(self, theParent, theProject):
        PagedDialog.__init__(self, theParent)

        logger.debug("Initialising GuiProjectDetails ...")
        self.setObjectName("GuiProjectDetails")

        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theProject = theProject
        self.optState   = theProject.optState

        self.setWindowTitle("Project Details")

        wW = self.mainConf.pxInt(570)
        wH = self.mainConf.pxInt(375)

        self.setMinimumWidth(wW)
        self.setMinimumHeight(wH)
        self.resize(
            self.mainConf.pxInt(self.optState.getInt("GuiProjectDetails", "winWidth",  wW)),
            self.mainConf.pxInt(self.optState.getInt("GuiProjectDetails", "winHeight", wH))
        )

        # self.tabMain    = GuiProjectEditMain(self.theParent, self.theProject)

        # self.addTab(self.tabMain,    "Settings")

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Close)
        self.buttonBox.rejected.connect(self._doClose)
        self.addControls(self.buttonBox)

        logger.debug("GuiProjectDetails initialisation complete")

        return

    ##
    #  Slots
    ##

    def _doClose(self):
        """Save settings and close the dialog.
        """
        self._saveGuiSettings()
        self.close()
        return

    ##
    #  Internal Functions
    ##

    def _saveGuiSettings(self):
        """Save GUI settings.
        """
        winWidth  = self.mainConf.rpxInt(self.width())
        winHeight = self.mainConf.rpxInt(self.height())

        self.optState.setValue("GuiProjectDetails", "winWidth",  winWidth)
        self.optState.setValue("GuiProjectDetails", "winHeight", winHeight)

        return

# END Class GuiProjectDetails
