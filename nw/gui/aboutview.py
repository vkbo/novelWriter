# -*- coding: utf-8 -*
"""novelWriter GUI About View

 novelWriter – GUI About View
==============================
 Class holding the tab viewing the about information

 File History:
 Created: 2018-10-02 [0.1.0]

"""

import logging
import nw

from os              import path
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PyQt5.QtSvg     import QSvgWidget
from PyQt5.QtCore    import Qt, QSize
from PyQt5.QtGui     import QFont

logger = logging.getLogger(__name__)

class GuiAboutView(QWidget):

    def __init__(self):
        QWidget.__init__(self)

        logger.debug("Initialising AboutView ...")
        self.mainConf = nw.CONFIG
        self.innerBox = QHBoxLayout()
        self.outerBox = QVBoxLayout()

        logoPath = path.abspath(path.join(self.mainConf.appPath,"..","novelWriter.svg"))
        logger.verbose("Loading image: %s" % logoPath)
        nwLogo = QSvgWidget(logoPath)
        nwLogo.setFixedSize(QSize(300,300))

        nwName = QLabel()
        nwName.setText(nw.__package__)
        nwName.setAlignment(Qt.AlignCenter)
        fnName = QFont()
        fnName.setPointSize(22)
        fnName.setBold(True)
        nwName.setFont(fnName)

        nwVersion = QLabel()
        nwVersion.setText("Version %s" % nw.__version__)
        nwVersion.setAlignment(Qt.AlignCenter)

        nwCredits = QLabel()
        nwCredits.setText("Created By: %s" % ",".join(nw.__credits__))
        nwCredits.setAlignment(Qt.AlignCenter)

        nwWebsite = QLabel()
        nwWebsite.setText("<a href='%s'>%s</a>" % (nw.__website__,nw.__website__))
        nwWebsite.setOpenExternalLinks(True)
        nwWebsite.setAlignment(Qt.AlignCenter)

        self.outerBox.addStretch(1)
        self.innerBox.addStretch(1)
        self.innerBox.addWidget(nwLogo)
        self.innerBox.addStretch(1)
        self.outerBox.addLayout(self.innerBox)
        self.outerBox.addWidget(nwName)
        self.outerBox.addWidget(nwVersion)
        self.outerBox.addWidget(nwCredits)
        self.outerBox.addWidget(nwWebsite)
        self.outerBox.addStretch(1)

        self.setLayout(self.outerBox)

        logger.debug("AboutView initialisation complete")

        return

# END Class GuiAboutView
