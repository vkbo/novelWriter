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

from PyQt5.QtWidgets import QTextBrowser

logger = logging.getLogger(__name__)

class GuiDocViewer(QTextBrowser):

    def __init__(self, theParent):
        QTextBrowser.__init__(self)

        logger.debug("Initialising DocViewer ...")

        # Class Variables
        self.mainConf  = nw.CONFIG
        self.theParent = theParent
        self.theTheme  = theParent.theTheme

        self.theDoc = self.document()
        self.theDoc.setDefaultStyleSheet((
            "h1, h2, h3, h4 {{"
            "  color: rgb({0},{1},{2});"
            "}}"
        ).format(
            *self.theTheme.colHead
        ))
        self.theDoc.setDocumentMargin(self.mainConf.textMargin[0])
        self.setMinimumWidth(300)

        logger.debug("DocViewer initialisation complete")

        return

    def clearViewer(self):
        self.clear()
        return True

# END Class GuiDocViewer
