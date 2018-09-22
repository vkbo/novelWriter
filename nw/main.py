# -*- coding: utf-8 -*
"""novelWriter Main Class

 novelWriter – Main Class
==========================
 Sets up the main GUI and holds action and event functions

 File History:
 Created: 2018-09-22 [0.1.0]

"""

import logging
import nw

from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui     import QIcon

logger = logging.getLogger(__name__)

class NovelWriter(QWidget):

    def __init__(self):
        super().__init__()

        self.initGUI()

    def initGUI(self):

        # self.setGeometry(300, 300, 300, 220)
        self.resize(600,500)
        self.setWindowTitle("novelWriter")
        self.setWindowIcon(QIcon("novelWriter.svg"))

        self.show()

# END Class NovelWriter
