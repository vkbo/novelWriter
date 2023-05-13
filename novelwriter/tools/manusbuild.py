"""
novelWriter – GUI Build Manuscript
==================================
GUI classes for the Manuscript Build Tool

File History:
Created: 2023-05-13 [2.1b1]

This file is a part of novelWriter
Copyright 2018–2023, Veronica Berglyd Olsen

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

from PyQt5.QtWidgets import (
    QDialog, QGridLayout, QPushButton, QSplitter, QTextBrowser, QVBoxLayout,
    QWidget, qApp
)

from novelwriter.common import getGuiItem
from novelwriter.tools.manussettings import GuiBuildSettings

logger = logging.getLogger(__name__)


class GuiBuildManuscript(QDialog):

    def __init__(self, mainGui):
        super().__init__(parent=mainGui)

        self.mainConf   = novelwriter.CONFIG
        self.mainGui    = mainGui
        self.mainTheme  = mainGui.mainTheme
        self.theProject = mainGui.theProject

        self.setWindowTitle(self.tr("Build Manuscript"))
        self.setMinimumWidth(self.mainConf.pxInt(600))
        self.setMinimumHeight(self.mainConf.pxInt(500))

        wWin = self.mainConf.pxInt(900)
        hWin = self.mainConf.pxInt(600)

        pOptions = self.theProject.options
        self.resize(
            self.mainConf.pxInt(pOptions.getInt("GuiBuildManuscript", "winWidth", wWin)),
            self.mainConf.pxInt(pOptions.getInt("GuiBuildManuscript", "winHeight", hWin))
        )

        # Controls
        # ========

        self.btnNew = QPushButton(self.tr("New Build"))
        self.btnNew.clicked.connect(self._createNewBuild)

        self.optsGrid = QGridLayout()
        self.optsGrid.addWidget(self.btnNew, 0, 0)

        self.manPreview = GuiManuscriptPreview(self)

        # Assemble GUI
        # ============

        self.optsWidget = QWidget()
        self.optsWidget.setLayout(self.optsGrid)

        self.mainSplit = QSplitter()
        self.mainSplit.addWidget(self.optsWidget)
        self.mainSplit.addWidget(self.manPreview)
        self.mainSplit.setSizes([
            self.mainConf.pxInt(pOptions.getInt("GuiBuildManuscript", "optsWidth", wWin//3)),
            self.mainConf.pxInt(pOptions.getInt("GuiBuildManuscript", "viewWidth", 2*wWin//3)),
        ])

        self.outerBox = QVBoxLayout()
        self.outerBox.addWidget(self.mainSplit)

        self.setLayout(self.outerBox)

        return

    def loadContent(self):
        """
        """
        return

    ##
    #  Events
    ##

    def closeEvent(self, event):
        """Capture the user closing the window so we can save settings.
        """
        self._saveSettings()
        event.accept()
        return

    ##
    #  Private Slots
    ##

    def _createNewBuild(self):
        """Open the build settings dialog for a new build.
        """
        dlgSettings = getGuiItem("GuiBuildSettings")
        if dlgSettings is None:
            dlgSettings = GuiBuildSettings(self)
        assert isinstance(dlgSettings, GuiBuildSettings)

        dlgSettings.setModal(False)
        dlgSettings.show()
        dlgSettings.raise_()
        qApp.processEvents()

        dlgSettings.loadContent({"name": self.tr("My Manuscript")})

        return

    ##
    #  Internal Functions
    ##

    def _saveSettings(self):
        """Save the various user settings.
        """
        logger.debug("Saving GuiBuildManuscript settings")

        winWidth  = self.mainConf.rpxInt(self.width())
        winHeight = self.mainConf.rpxInt(self.height())

        mainSplit = self.mainSplit.sizes()
        optsWidth = mainSplit[0]
        viewWidth = mainSplit[1]

        pOptions = self.theProject.options
        pOptions.setValue("GuiBuildManuscript", "winWidth", winWidth)
        pOptions.setValue("GuiBuildManuscript", "winHeight", winHeight)
        pOptions.setValue("GuiBuildManuscript", "optsWidth", optsWidth)
        pOptions.setValue("GuiBuildManuscript", "viewWidth", viewWidth)
        pOptions.saveSettings()

        return

# END Class GuiBuildManuscript


class GuiManuscriptPreview(QTextBrowser):

    def __init__(self, mainGui):
        super().__init__(parent=mainGui)

        self.mainConf   = novelwriter.CONFIG
        self.mainGui    = mainGui
        self.mainTheme  = mainGui.mainTheme
        self.theProject = mainGui.theProject

        return

# END Class GuiManuscriptPreview
