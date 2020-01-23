# -*- coding: utf-8 -*-
"""novelWriter GUI Doc Merge

 novelWriter – GUI Doc Merge
=============================
 Tool for merging multiple documents to one

 File History:
 Created: 2020-01-23 [0.4.3]

"""

import logging
import nw

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog, QHBoxLayout, QVBoxLayout, QGridLayout, QPushButton, QLabel,
    QProgressBar
)

from nw.tools import OptLastState
from nw.constants import nwFiles

logger = logging.getLogger(__name__)

class GuiDocMerge(QDialog):

    def __init__(self, theParent, theProject):
        QDialog.__init__(self, theParent)

        logger.debug("Initialising GuiDocMerge ...")

        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theProject = theProject
        self.optState   = DocMergeLastState(self.theProject,nwFiles.MERGE_OPT)
        self.optState.loadSettings()

        self.outerBox = QHBoxLayout()
        self.innerBox = QVBoxLayout()
        self.setWindowTitle("Merge Documents")
        self.setLayout(self.outerBox)

        self.guiDeco = self.theParent.theTheme.loadDecoration("merge",(64,64))

        self.outerBox.addWidget(self.guiDeco, 0, Qt.AlignTop)
        self.outerBox.addLayout(self.innerBox)

        self.doMergeForm = QGridLayout()
        self.doMergeForm.setContentsMargins(10,5,0,10)

        self.mergeButton = QPushButton("Merge")
        self.mergeButton.clicked.connect(self._doMerge)

        self.closeButton = QPushButton("Close")
        self.closeButton.clicked.connect(self._doClose)

        self.mergeStatus   = QLabel("Ready ...")
        self.mergeProgress = QProgressBar(self)

        self.doMergeForm.addWidget(self.mergeStatus,   0, 0, 1, 3)
        self.doMergeForm.addWidget(self.mergeProgress, 1, 0)
        self.doMergeForm.addWidget(self.mergeButton,   1, 1)
        self.doMergeForm.addWidget(self.closeButton,   1, 2)

        self.innerBox.addLayout(self.doMergeForm)

        self.rejected.connect(self._doClose)
        self.show()

        logger.debug("GuiDocMerge initialisation complete")

        return

    ##
    #  Buttons
    ##

    def _doMerge(self):

        logger.verbose("GuiDocMerge merge button clicked")

        return

    def _doClose(self):

        logger.verbose("GuiDocMerge close button clicked")

        self.optState.saveSettings()
        self.close()

        return

# END Class GuiDocMerge

class DocMergeLastState(OptLastState):

    def __init__(self, theProject, theFile):
        OptLastState.__init__(self, theProject, theFile)
        self.theState   = {
        }
        self.stringOpt = ()
        self.boolOpt   = ()
        self.intOpt    = ()
        return

# END Class DocMergeLastState
