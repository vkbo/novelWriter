# -*- coding: utf-8 -*-
"""novelWriter GUI DocView Details

 novelWriter – GUI DocView Details
===================================
 Class holding the document view details panel

 File History:
 Created: 2019-09-31 [0.3.2]

"""

import logging
import nw

from PyQt5.QtCore    import Qt
from PyQt5.QtGui     import QFont
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QGroupBox, QScrollArea, QFrame

from nw.constants    import nwLabels

logger = logging.getLogger(__name__)

class GuiDocViewDetails(QWidget):

    def __init__(self, theParent, theProject):
        QWidget.__init__(self, theParent)

        logger.debug("Initialising DocViewDetails ...")
        self.mainConf   = nw.CONFIG
        self.debugGUI   = self.mainConf.debugGUI
        self.theParent  = theParent
        self.theProject = theProject

        self.outerBox   = QHBoxLayout(self)
        self.outerBox.setContentsMargins(4,4,4,4)

        self.refTags     = QGroupBox("Referenced From", self)
        self.refTagsForm = QHBoxLayout(self.refTags)
        self.refTags.setLayout(self.refTagsForm)

        self.refList = QLabel("None")
        self.refList.setWordWrap(True)
        self.refList.setAlignment(Qt.AlignTop)
        self.refList.setScaledContents(True)
        self.refList.linkActivated.connect(self._linkClicked)

        self.scrollBox = QScrollArea()
        self.scrollBox.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollBox.setFrameStyle(QFrame.NoFrame)
        self.scrollBox.setWidgetResizable(True)
        self.scrollBox.setMaximumHeight(300)
        self.scrollBox.setWidget(self.refList)

        self.refTagsForm.addWidget(self.scrollBox)
        self.outerBox.addWidget(self.refTags)
        self.setLayout(self.outerBox)
        self.setContentsMargins(0,0,0,0)

        logger.debug("DocViewDetails initialisation complete")

        return

    def refreshReferences(self, tHandle):

        theRefs = self.theParent.theIndex.buildReferenceList(tHandle)
        if theRefs:
            self.setVisible(True)
        else:
            self.setVisible(False)
            return

        theList = []
        for tHandle in theRefs:
            tItem = self.theProject.getItem(tHandle)
            if tItem is not None:
                theList.append("<a href='#tag=%s'>%s</a>" % (tHandle,tItem.itemName))

        self.refList.setText(", ".join(theList))
        self.refList.adjustSize()

        return

    ##
    #  Internal Functions
    ##

    def _linkClicked(self, theLink):
        if len(theLink) == 18:
            tHandle = theLink[-13:]
            self.theParent.viewDocument(tHandle)
        return

# END Class GuiDocViewDetails
