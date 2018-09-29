# -*- coding: utf-8 -*
"""novelWriter GUI Document Tree

 novelWriter – GUI Document Tree
=================================
 Class holding the left side document tree view

 File History:
 Created: 2018-09-29 [0.1.0]

"""

import logging
import nw

from os              import path
from PyQt5.QtCore    import Qt
from PyQt5.QtWidgets import QTreeView
from PyQt5.QtGui     import QStandardItemModel

logger = logging.getLogger(__name__)

class GuiDocTree(QTreeView):

    def __init__(self):
        QTreeView.__init__(self)

        logger.debug("Initialising DocTree ...")
        self.mainConf = nw.CONFIG

        self.treeModel = QStandardItemModel(0, 3, self)
        self.treeModel.setHeaderData(0, Qt.Horizontal, "Name")
        self.treeModel.setHeaderData(1, Qt.Horizontal, "Words")
        self.treeModel.setHeaderData(2, Qt.Horizontal, "Status")

        self.setModel(self.treeModel)

        logger.debug("DocTree initialisation complete")

        return

# END Class GuiDocTree
