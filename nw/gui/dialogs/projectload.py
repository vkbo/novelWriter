# -*- coding: utf-8 -*-
"""novelWriter GUI Open Project

 novelWriter – GUI Open Project
================================
 New and open project dialog

 File History:
 Created: 2020-02-26 [0.4.5]

"""

import logging
import nw

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog, QHBoxLayout, QVBoxLayout, QGridLayout, QPushButton, QListWidget,
    QAbstractItemView
)

logger = logging.getLogger(__name__)

class GuiProjectLoad(QDialog):

    def __init__(self, theParent):
        QDialog.__init__(self, theParent)

        logger.debug("Initialising GuiProjectLoad ...")

        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.sourceItem = None

        self.outerBox = QHBoxLayout()
        self.innerBox = QVBoxLayout()
        self.setWindowTitle("Manage Projects")
        self.setLayout(self.outerBox)

        self.guiDeco = self.theParent.theTheme.loadDecoration("nwicon", (128, 128))

        self.outerBox.addWidget(self.guiDeco, 0, Qt.AlignTop)
        self.outerBox.addLayout(self.innerBox)

        self.projectForm = QGridLayout()
        self.projectForm.setContentsMargins(0, 0, 0, 0)

        self.listBox = QListWidget()
        self.listBox.setDragDropMode(QAbstractItemView.NoDragDrop)

        self.closeButton = QPushButton("Close")
        self.closeButton.clicked.connect(self._doClose)

        self.projectForm.addWidget(self.listBox,     0, 0, 1, 3)
        self.projectForm.addWidget(self.closeButton, 1, 2)

        self.innerBox.addLayout(self.projectForm)

        self.rejected.connect(self._doClose)
        self.setModal(True)
        self.show()

        self._populateList()

        logger.debug("GuiProjectLoad initialisation complete")

        return

    ##
    #  Buttons
    ##

    def _doClose(self):
        """Close the dialog window without doing anything.
        """
        logger.verbose("GuiProjectLoad close button clicked")
        self.close()
        return

    ##
    #  Internal Functions
    ##

    def _populateList(self):
        return

# END Class GuiProjectLoad
