# -*- coding: utf-8 -*-
"""novelWriter GUI Session Log Viewer

 novelWriter – GUI Session Log Viewer
======================================
 Class holding the session log view window

 File History:
 Created: 2019-10-20 [0.3]

"""

import logging
import nw

from PyQt5.QtCore    import Qt
from PyQt5.QtGui     import QIcon, QColor, QPixmap
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QDialogButtonBox, QLabel, QPushButton, QHeaderView
)

logger = logging.getLogger(__name__)

class GuiSessionLogView(QDialog):

    def __init__(self, theParent, theProject):
        QDialog.__init__(self, theParent)

        logger.debug("Initialising SessionLogView ...")

        self.mainConf   = nw.CONFIG
        self.theProject = theProject
        self.theParent  = theParent

        self.outerBox   = QVBoxLayout()
        self.bottomBox  = QHBoxLayout()

        self.setWindowTitle("Session Log")

        self.setLayout(self.outerBox)

        self.show()

        logger.debug("SessionLogView initialisation complete")

        return

    def _doClose(self):
        self.close()
        return

# END Class GuiSessionLogView
