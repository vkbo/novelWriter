# -*- coding: utf-8 -*-
"""novelWriter GUI DocView Details

 novelWriter – GUI DocView Details
===================================
 Class holding the document view details panel

 File History:
 Created: 2019-10-31 [0.3.2]

 This file is a part of novelWriter
 Copyright 2020, Veronica Berglyd Olsen

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful, but
 WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

import logging
import nw

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import (
    QWidget, QLabel, QScrollArea, QFrame, QToolButton, QCheckBox, QGridLayout
)

logger = logging.getLogger(__name__)

class GuiDocViewDetails(QWidget):

    def __init__(self, theParent, theProject):
        QWidget.__init__(self, theParent)

        logger.debug("Initialising DocViewDetails ...")
        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theProject = theProject
        self.currHandle = None

        self.outerBox = QGridLayout(self)
        self.outerBox.setContentsMargins(0,0,0,0)
        self.outerBox.setHorizontalSpacing(0)
        self.outerBox.setVerticalSpacing(4)

        self.refLabel = QLabel("Referenced By", self)

        self.showHide = QToolButton()
        self.showHide.setStyleSheet("QToolButton { border: none; }")
        self.showHide.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.showHide.setArrowType(Qt.DownArrow)
        self.showHide.setCheckable(True)
        self.showHide.setIconSize(QSize(16,16))
        self.showHide.toggled.connect(self._doShowHide)

        self.isSticky = QCheckBox("Sticky")
        self.isSticky.setChecked(False)
        self.isSticky.toggled.connect(self._doSticky)

        self.refList = QLabel("None")
        self.refList.setWordWrap(True)
        self.refList.setAlignment(Qt.AlignTop)
        self.refList.setScaledContents(True)
        self.refList.linkActivated.connect(self._linkClicked)

        self.scrollBox = QScrollArea()
        self.scrollBox.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollBox.setFrameStyle(QFrame.NoFrame)
        self.scrollBox.setWidgetResizable(True)
        self.scrollBox.setFixedHeight(80)
        self.scrollBox.setWidget(self.refList)

        self.outerBox.addWidget(self.showHide,  0, 0)
        self.outerBox.addWidget(self.refLabel,  0, 1)
        self.outerBox.addWidget(self.isSticky,  0, 2)
        self.outerBox.addWidget(self.scrollBox, 1, 1, 1, 2)
        self.outerBox.setColumnStretch(1, 1)

        self.setLayout(self.outerBox)
        self.setContentsMargins(0,0,0,0)

        self._doShowHide(self.mainConf.showRefPanel)

        logger.debug("DocViewDetails initialisation complete")

        return

    def refreshReferences(self, tHandle):
        """Update the current list of document references from the
        project index.
        """
        self.currHandle = tHandle

        if self.isSticky.isChecked():
            return

        theRefs = self.theParent.theIndex.getBackReferenceList(tHandle)
        theList = []
        for tHandle in theRefs:
            tItem = self.theProject.projTree[tHandle]
            if tItem is not None:
                theList.append("<a href='#head_%s:%s'>%s</a>" % (
                    tHandle, theRefs[tHandle], tItem.itemName
                ))

        self.refList.setText(", ".join(theList))
        self.refList.adjustSize()

        return

    ##
    #  Internal Functions
    ##

    def _linkClicked(self, theLink):
        """Capture the link-click and forward it to the document viewer
        class for handling.
        """
        logger.verbose("Clicked link: '%s'" % theLink)
        if len(theLink) == 27:
            tHandle = theLink[6:19]
            self.theParent.viewDocument(tHandle, theLink)
        return

    def _doShowHide(self, chState):
        """Toggle the expand/collapse of the panel.
        """
        self.scrollBox.setVisible(chState)
        self.mainConf.setShowRefPanel(chState)
        if chState:
            self.showHide.setArrowType(Qt.DownArrow)
        else:
            self.showHide.setArrowType(Qt.RightArrow)
        return

    def _doSticky(self, chState):
        """Toggle the sticky feature of the references.
        """
        if not chState and self.currHandle is not None:
            self.refreshReferences(self.currHandle)
        return

# END Class GuiDocViewDetails
