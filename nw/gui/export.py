# -*- coding: utf-8 -*-
"""novelWriter GUI Export Tools

 novelWriter – GUI Export Tool
================================
 Tool for exporting project files to other formats

 File History:
 Created: 2019-10-13 [0.2.3]

"""

import logging
import nw

from os import path

from PyQt5.QtCore    import Qt, QSize
from PyQt5.QtSvg     import QSvgWidget
from PyQt5.QtWidgets import (
    QDialog, QHBoxLayout, QVBoxLayout, QWidget, QTabWidget, QDialogButtonBox
)

logger = logging.getLogger(__name__)

class GuiExport(QDialog):

    def __init__(self, theParent, theProject):
        QDialog.__init__(self, theParent)

        logger.debug("Initialising GuiExport ...")

        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theProject = theProject

        self.outerBox   = QHBoxLayout()
        self.innerBox   = QVBoxLayout()
        self.setWindowTitle("Export Project")
        self.setLayout(self.outerBox)

        self.gradPath = path.abspath(path.join(self.mainConf.appPath,"graphics","gear.svg"))
        self.svgGradient = QSvgWidget(self.gradPath)
        self.svgGradient.setFixedSize(QSize(64,64))

        self.theProject.countStatus()
        self.tabMain    = GuiExportMain(self.theParent, self.theProject)

        self.tabWidget = QTabWidget()
        self.tabWidget.addTab(self.tabMain, "Settings")

        self.outerBox.addWidget(self.svgGradient, 0, Qt.AlignTop)
        self.outerBox.addLayout(self.innerBox)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        # self.buttonBox.accepted.connect(self._doSave)
        # self.buttonBox.rejected.connect(self._doClose)

        self.innerBox.addWidget(self.tabWidget)
        self.innerBox.addWidget(self.buttonBox)

        self.show()

        logger.debug("GuiExport initialisation complete")

        return

# END Class GuiExport

class GuiExportMain(QWidget):

    def __init__(self, theParent, theProject):
        QWidget.__init__(self, theParent)

        self.theParent   = theParent
        self.theProject  = theProject

        return

# END Class GuiExportMain
