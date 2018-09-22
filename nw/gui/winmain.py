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
from PyQt5.QtWidgets import QWidget, QMainWindow, QHBoxLayout, QVBoxLayout, QFrame, QSplitter, QTreeView
from PyQt5.QtCore    import Qt
from PyQt5.QtGui     import QIcon, QStandardItemModel

logger = logging.getLogger(__name__)

class GuiMain(QMainWindow):

    def __init__(self):
        QWidget.__init__(self)

        self.mainConf = nw.CONFIG

        self.resize(900,600)
        self.setWindowTitle("%s [%s]" % (nw.__package__, nw.__version__))
        self.setWindowIcon(QIcon(path.join(self.mainConf.appPath,"..","novelWriter.svg")))

        self.statBar = self.statusBar()
        self.statBar.showMessage("Hello Kitty!")

        self.treePane = QFrame()
        self.treePane.setFrameShape(QFrame.StyledPanel)
        self.textPane = QFrame()
        self.textPane.setFrameShape(QFrame.StyledPanel)
        self.splitMain = QSplitter(Qt.Horizontal)
        self.splitMain.addWidget(self.treePane)
        self.splitMain.addWidget(self.textPane)

        self.treeModel = QStandardItemModel(0, 3, self)
        self.treeModel.setHeaderData(0, Qt.Horizontal, "Name")
        self.treeModel.setHeaderData(1, Qt.Horizontal, "Words")
        self.treeModel.setHeaderData(2, Qt.Horizontal, "Status")

        self.treeBox = QVBoxLayout()
        # self.treeBox.addStretch(1)
        self.treeView = QTreeView()
        self.treeView.setModel(self.treeModel)
        self.treeBox.addWidget(self.treeView)
        self.treePane.setLayout(self.treeBox)

        self.setCentralWidget(self.splitMain)

        self._buildMenu()

        self.show()

        return

    def _buildMenu(self):
        menuBar = self.menuBar()
        menuBar.addMenu("File")
        return

# END Class GuiMain
