# -*- coding: utf-8 -*
"""novelWriter GUI Main Window

 novelWriter – GUI Main Window
===============================
 Class holding the main window

 File History:
 Created: 2018-0+-22 [0.1.0]

"""

import logging
import nw

from os              import path
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui     import QIcon

logger = logging.getLogger(__name__)

class GuiMain(QWidget):

    def __init__(self):
        QWidget.__init__(self)

        self.mainConf = nw.CONFIG

        self.resize(600,500)
        self.setWindowTitle("%s [%s]" % (nw.__package__, nw.__version__))
        self.setWindowIcon(QIcon(path.join(self.mainConf.appPath,"..","novelWriter.svg")))

        self.show()

        return

# END Class GuiMain
