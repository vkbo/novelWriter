# -*- coding: utf-8 -*
"""novelWriter GUI Document Editor

 novelWriter – GUI Document Editor
===================================
 Class holding the document editor

 File History:
 Created: 2018-09-29 [0.1.0]

"""

import logging
import nw

from os              import path
from PyQt5.QtCore    import Qt
from PyQt5.QtWidgets import QTextEdit
# from PyQt5.QtWidgets import QTabWidget, QWidget
# from PyQt5.QtGui     import QStandardItemModel

logger = logging.getLogger(__name__)

class GuiDocEditor(QTextEdit):

    def __init__(self):
        QTextEdit.__init__(self)

        logger.debug("Initialising DocEditor ...")
        self.mainConf = nw.CONFIG
        self.setPlainText("Hello Kitty!")

        logger.debug("DocEditor initialisation complete")

        return


# END Class GuiDocEditor
