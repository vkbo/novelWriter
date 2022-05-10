"""
novelWriter – GUI Main Window Views ToolBar
===========================================
GUI class for the main window "Views" toolbar

File History:
Created: 2022-05-10 [1.7b1]

This file is a part of novelWriter
Copyright 2018–2022, Veronica Berglyd Olsen

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

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QToolBar, QWidget, QSizePolicy, QAction

logger = logging.getLogger(__name__)


class GuiViewsBar(QToolBar):

    def __init__(self, theParent):
        QToolBar.__init__(self, theParent)

        logger.debug("Initialising GuiViewsBar ...")

        self.mainConf  = novelwriter.CONFIG
        self.theParent = theParent
        self.theTheme  = theParent.theTheme

        # Style
        iPx = self.mainConf.pxInt(22)

        lblFont = self.theTheme.guiFont
        lblFont.setPointSizeF(0.65*self.theTheme.fontPointSize)
        self.setFont(lblFont)

        self.setMovable(False)
        self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.setIconSize(QSize(iPx, iPx))
        self.setContentsMargins(0, 0, 0, 0)

        stretch = QWidget(self)
        stretch.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Actions
        self.aProject = QAction(self.tr("Project"))
        self.aProject.setIcon(self.theTheme.getIcon("status_lines"))

        self.aStats = QAction(self.tr("Stats"))
        self.aStats.setIcon(self.theTheme.getIcon("status_stats"))

        self.aSettings = QAction(self.tr("Settings"))
        self.aSettings.setIcon(self.theTheme.getIcon("settings"))

        # Assemble
        self.addWidget(stretch)
        self.addAction(self.aProject)
        self.addAction(self.aStats)
        self.addAction(self.aSettings)

        logger.debug("GuiViewsBar initialisation complete")

        return

# END Class GuiViewsBar
