# -*- coding: utf-8 -*-
"""novelWriter GUI Document Viewer

 novelWriter – GUI Document Viewer
===================================
 Class holding the document html viewer

 File History:
 Created: 2019-05-10 [0.0.1]

"""

import logging
import nw

from PyQt5.QtCore    import Qt
from PyQt5.QtWidgets import QTextBrowser
from PyQt5.QtGui     import QTextOption

logger = logging.getLogger(__name__)

class GuiDocViewer(QTextBrowser):

    def __init__(self, theParent):
        QTextBrowser.__init__(self)

        logger.debug("Initialising DocViewer ...")

        # Class Variables
        self.mainConf  = nw.CONFIG
        self.theParent = theParent
        self.theTheme  = theParent.theTheme

        self.theQDoc = self.document()
        self.theQDoc.setDefaultStyleSheet((
            "h1, h2, h3, h4 {{"
            "  color: rgb({0},{1},{2});"
            "}}"
        ).format(
            *self.theTheme.colHead
        ))
        self.theQDoc.setDocumentMargin(self.mainConf.textMargin[0])
        self.setMinimumWidth(300)

        theOpt = QTextOption()
        if self.mainConf.doJustify:
            theOpt.setAlignment(Qt.AlignJustify)
        self.theQDoc.setDefaultTextOption(theOpt)

        logger.debug("DocViewer initialisation complete")

        return

    def clearViewer(self):
        self.clear()
        return True

# END Class GuiDocViewer
