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
from PyQt5.QtGui     import QTextOption, QFont, QPalette, QColor

from nw.convert.tokenizer   import Tokenizer
from nw.convert.text.tohtml import ToHtml
from nw.enum                import nwItemType

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

        self.qDocument = self.document()
        self.setMinimumWidth(300)
        self.initViewer()

        theOpt = QTextOption()
        if self.mainConf.doJustify:
            theOpt.setAlignment(Qt.AlignJustify)
        self.qDocument.setDefaultTextOption(theOpt)

        logger.debug("DocViewer initialisation complete")

        return

    def clearViewer(self):
        self.clear()
        self.setSearchPaths([""])
        return True

    def initViewer(self):
        """Set editor settings from main config.
        """

        self._makeStyleSheet()

        # Set Font
        theFont = QFont()
        if self.mainConf.textFont is None:
            # If none is defined, set the default back to config
            self.mainConf.textFont = self.qDocument.defaultFont().family()
        theFont.setFamily(self.mainConf.textFont)
        theFont.setPointSize(self.mainConf.textSize)
        self.setFont(theFont)

        docPalette = self.palette()
        docPalette.setColor(QPalette.Base, QColor(*self.theTheme.colBack))
        docPalette.setColor(QPalette.Text, QColor(*self.theTheme.colText))
        self.setPalette(docPalette)

        self.qDocument.setDocumentMargin(self.mainConf.textMargin)
        theOpt = QTextOption()
        if self.mainConf.doJustify:
            theOpt.setAlignment(Qt.AlignJustify)
        self.qDocument.setDefaultTextOption(theOpt)

        # If we have a document open, we should reload it in case the font changed
        if self.theHandle is not None:
            tHandle = self.theHandle
            self.clearViewer()
            self.loadText(tHandle)

        return True

    def loadText(self, tHandle):

        tItem = self.theProject.getItem(tHandle)
        if tItem is None:
            logger.warning("Item not found")
            return False

        if tItem.itemType != nwItemType.FILE:
            return False

        logger.debug("Generating preview for item %s" % tHandle)
        sPos = self.verticalScrollBar().value()
        aDoc = ToHtml(self.theProject, self.theParent)
        aDoc.setText(tHandle)
        aDoc.doAutoReplace()
        aDoc.tokenizeText()
        aDoc.doConvert()
        self.setHtml(aDoc.theResult)
        if self.theHandle == tHandle:
            self.verticalScrollBar().setValue(sPos)
        self.theHandle = tHandle
        self.theProject.setLastViewed(tHandle)

        return True

    ##
    #  Internal Functions
    ##

    def _makeStyleSheet(self):

        self.qDocument.setDefaultStyleSheet((
            "body {{"
            "  font-size: {textSize}pt;"
            "  color: rgb({tColR},{tColG},{tColB});"
            "}}\n"
            "h1, h2, h3, h4 {{"
            "  color: rgb({hColR},{hColG},{hColB});"
            "}}\n"
            "a {{"
            "  color: rgb({aColR},{aColG},{aColB});"
            "}}\n"
            "pre {{"
            "  color: rgb({cColR},{cColG},{cColB});"
            "  font-size: {preSize}pt;"
            "}}\n"
            "mark {{"
            "  color: rgb({eColR},{eColG},{eColB});"
            "}}\n"
            "table {{"
            "  margin: 10px 0px;"
            "}}\n"
            "td {{"
            "  padding: 0px 4px;"
            "}}\n"
        ).format(
            textSize = self.mainConf.textSize,
            preSize  = self.mainConf.textSize*0.9,
            tColR    = self.theTheme.colText[0],
            tColG    = self.theTheme.colText[1],
            tColB    = self.theTheme.colText[2],
            hColR    = self.theTheme.colHead[0],
            hColG    = self.theTheme.colHead[1],
            hColB    = self.theTheme.colHead[2],
            cColR    = self.theTheme.colComm[0],
            cColG    = self.theTheme.colComm[1],
            cColB    = self.theTheme.colComm[2],
            eColR    = self.theTheme.colEmph[0],
            eColG    = self.theTheme.colEmph[1],
            eColB    = self.theTheme.colEmph[2],
            aColR    = self.theTheme.colLink[0],
            aColG    = self.theTheme.colLink[1],
            aColB    = self.theTheme.colLink[2],
        ))

        return True

# END Class GuiDocViewer
