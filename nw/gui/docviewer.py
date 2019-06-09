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

from PyQt5.QtCore    import Qt, QUrl
from PyQt5.QtWidgets import QTextBrowser
from PyQt5.QtGui     import QTextOption

from nw.convert.tokenizer import Tokenizer
from nw.convert.tohtml    import ToHtml
from nw.enum              import nwItemType

logger = logging.getLogger(__name__)

class GuiDocViewer(QTextBrowser):

    def __init__(self, theParent, theProject):
        QTextBrowser.__init__(self)

        logger.debug("Initialising DocViewer ...")

        # Class Variables
        self.mainConf   = nw.CONFIG
        self.theProject = theProject
        self.theParent  = theParent
        self.theTheme   = theParent.theTheme
        self.theHandle  = None

        self.theQDoc = self.document()
        self.theQDoc.setDefaultStyleSheet((
            "h1, h2, h3, h4 {{"
            "  color: rgb({0},{1},{2});"
            "}}"
        ).format(
            *self.theTheme.colHead
        ))
        self.setMinimumWidth(300)
        self.initEditor()

        theOpt = QTextOption()
        if self.mainConf.doJustify:
            theOpt.setAlignment(Qt.AlignJustify)
        self.theQDoc.setDefaultTextOption(theOpt)

        logger.debug("DocViewer initialisation complete")

        return

    def clearViewer(self):
        self.clear()
        self.setSearchPaths([""])
        return True

    def initEditor(self):
        """Set editor settings from mani config.
        """
        self.theQDoc.setDocumentMargin(self.mainConf.textMargin[0])
        theOpt = QTextOption()
        if self.mainConf.doJustify:
            theOpt.setAlignment(Qt.AlignJustify)
        self.theQDoc.setDefaultTextOption(theOpt)

        return True

    def loadText(self, tHandle):

        if tHandle == "Help":
            self.loadHelp()
            return True

        tItem = self.theProject.getItem(tHandle)
        if tItem is None:
            logger.warning("Item not found")
            return False

        if tItem.itemType != nwItemType.FILE:
            return False

        logger.debug("Generating preview for item %s" % tHandle)
        aDoc = ToHtml(self.theProject, self.theParent)
        aDoc.setText(tHandle)
        aDoc.doAutoReplace()
        aDoc.tokenizeText()
        aDoc.doConvert()
        self.setHtml(aDoc.theResult)
        self.theHandle = tHandle
        self.theProject.setLastViewed(tHandle)

        return True

    def loadHelp(self):

        self.clearViewer()
        self.setSearchPaths([self.mainConf.helpPath])
        self.setSource(QUrl("index.html"))

        return True

# END Class GuiDocViewer
