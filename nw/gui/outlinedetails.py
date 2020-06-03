# -*- coding: utf-8 -*-
"""novelWriter GUI Project Outline

 novelWriter – GUI Project Outline
===================================
 Class holding the project outline view

 File History:
 Created: 2020-06-02 [0.7.0]

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

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QGridLayout, QHBoxLayout, QGroupBox, QLabel, QSizePolicy
)

from nw.constants import nwLabels, nwKeyWords

logger = logging.getLogger(__name__)

class GuiOutlineDetails(QWidget):

    LVL_MAP = {
        "H1" : "Title",
        "H2" : "Chapter",
        "H3" : "Scene",
        "H4" : "Section"
    }

    def __init__(self, theParent):
        QWidget.__init__(self, theParent)

        logger.debug("Initialising GuiOutlineDetails ...")

        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theProject = theParent.theProject
        self.theTheme   = theParent.theTheme
        self.theIndex   = theParent.theIndex
        self.optState   = theParent.theProject.optState

        # Sizes
        minTitle = self.theTheme.getTextWidth("X"*30)
        maxTitle = self.theTheme.getTextWidth("X"*50)
        wCount = self.theTheme.getTextWidth("99,999")
        hSpace = int(0.5*self.theTheme.fontPixelSize)
        vSpace = int(0.3*self.theTheme.fontPixelSize)

        # Details Area
        self.titleLabel = QLabel("<b>Title</b>")
        self.levelLabel = QLabel("<b>Level</b>")
        self.fileLabel  = QLabel("<b>Document</b>")
        self.titleValue = QLabel("")
        self.levelValue = QLabel("")
        self.fileValue  = QLabel("")
        self.titleValue.setMinimumWidth(minTitle)
        self.titleValue.setMaximumWidth(maxTitle)
        self.levelValue.setMinimumWidth(minTitle)
        self.levelValue.setMaximumWidth(maxTitle)
        self.fileValue.setMinimumWidth(minTitle)
        self.fileValue.setMaximumWidth(maxTitle)

        # Stats Area
        self.cCLabel = QLabel("<b>Characters</b>")
        self.wCLabel = QLabel("<b>Words</b>")
        self.pCLabel = QLabel("<b>Paragraphs</b>")
        self.cCValue = QLabel("")
        self.wCValue = QLabel("")
        self.pCValue = QLabel("")
        self.cCValue.setMinimumWidth(wCount)
        self.wCValue.setMinimumWidth(wCount)
        self.pCValue.setMinimumWidth(wCount)
        self.cCValue.setAlignment(Qt.AlignRight)
        self.wCValue.setAlignment(Qt.AlignRight)
        self.pCValue.setAlignment(Qt.AlignRight)

        # Synopsis
        self.synopLabel = QLabel("<b>Synopsis</b>")
        self.synopValue = QLabel("")
        self.synopLWrap = QHBoxLayout()
        self.synopValue.setWordWrap(True)
        self.synopValue.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.synopValue.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred)
        self.synopLWrap.addWidget(self.synopValue, 1)

        # Tags
        self.povKeyLabel = QLabel("<b>%s</b>" % nwLabels.KEY_NAME[nwKeyWords.POV_KEY])
        self.chrKeyLabel = QLabel("<b>%s</b>" % nwLabels.KEY_NAME[nwKeyWords.CHAR_KEY])
        self.pltKeyLabel = QLabel("<b>%s</b>" % nwLabels.KEY_NAME[nwKeyWords.PLOT_KEY])
        self.timKeyLabel = QLabel("<b>%s</b>" % nwLabels.KEY_NAME[nwKeyWords.TIME_KEY])
        self.wldKeyLabel = QLabel("<b>%s</b>" % nwLabels.KEY_NAME[nwKeyWords.WORLD_KEY])
        self.objKeyLabel = QLabel("<b>%s</b>" % nwLabels.KEY_NAME[nwKeyWords.OBJECT_KEY])
        self.entKeyLabel = QLabel("<b>%s</b>" % nwLabels.KEY_NAME[nwKeyWords.ENTITY_KEY])
        self.cstKeyLabel = QLabel("<b>%s</b>" % nwLabels.KEY_NAME[nwKeyWords.CUSTOM_KEY])
        self.povKeyValue = QLabel("")
        self.chrKeyValue = QLabel("")
        self.pltKeyValue = QLabel("")
        self.timKeyValue = QLabel("")
        self.wldKeyValue = QLabel("")
        self.objKeyValue = QLabel("")
        self.entKeyValue = QLabel("")
        self.cstKeyValue = QLabel("")
        self.povKeyValue.linkActivated.connect(self._tagClicked)
        self.chrKeyValue.linkActivated.connect(self._tagClicked)
        self.pltKeyValue.linkActivated.connect(self._tagClicked)
        self.timKeyValue.linkActivated.connect(self._tagClicked)
        self.wldKeyValue.linkActivated.connect(self._tagClicked)
        self.objKeyValue.linkActivated.connect(self._tagClicked)
        self.entKeyValue.linkActivated.connect(self._tagClicked)
        self.cstKeyValue.linkActivated.connect(self._tagClicked)

        # Selected Item Details
        self.mainGroup = QGroupBox("Title Details", self)
        self.mainForm  = QGridLayout()
        self.mainGroup.setLayout(self.mainForm)

        self.mainForm.addWidget(self.titleLabel,  0, 0, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.mainForm.addWidget(self.titleValue,  0, 1, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.mainForm.addWidget(self.cCLabel,     0, 2, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.mainForm.addWidget(self.cCValue,     0, 3, 1, 1, Qt.AlignTop | Qt.AlignRight)
        self.mainForm.addWidget(self.levelLabel,  1, 0, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.mainForm.addWidget(self.levelValue,  1, 1, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.mainForm.addWidget(self.wCLabel,     1, 2, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.mainForm.addWidget(self.wCValue,     1, 3, 1, 1, Qt.AlignTop | Qt.AlignRight)
        self.mainForm.addWidget(self.fileLabel,   2, 0, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.mainForm.addWidget(self.fileValue,   2, 1, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.mainForm.addWidget(self.pCLabel,     2, 2, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.mainForm.addWidget(self.pCValue,     2, 3, 1, 1, Qt.AlignTop | Qt.AlignRight)
        self.mainForm.addWidget(self.synopLabel,  3, 0, 1, 4, Qt.AlignTop | Qt.AlignLeft)
        self.mainForm.addLayout(self.synopLWrap,  4, 0, 1, 4, Qt.AlignTop | Qt.AlignLeft)

        self.mainForm.setColumnStretch(1, 1)
        self.mainForm.setRowStretch(4, 1)
        self.mainForm.setHorizontalSpacing(hSpace)
        self.mainForm.setVerticalSpacing(vSpace)

        # Selected Item Tags
        self.tagsGroup = QGroupBox("Tags", self)
        self.tagsForm  = QGridLayout()
        self.tagsGroup.setLayout(self.tagsForm)

        self.tagsForm.addWidget(self.povKeyLabel, 0, 0, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.tagsForm.addWidget(self.povKeyValue, 0, 1, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.tagsForm.addWidget(self.chrKeyLabel, 1, 0, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.tagsForm.addWidget(self.chrKeyValue, 1, 1, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.tagsForm.addWidget(self.pltKeyLabel, 2, 0, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.tagsForm.addWidget(self.pltKeyValue, 2, 1, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.tagsForm.addWidget(self.timKeyLabel, 3, 0, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.tagsForm.addWidget(self.timKeyValue, 3, 1, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.tagsForm.addWidget(self.wldKeyLabel, 4, 0, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.tagsForm.addWidget(self.wldKeyValue, 4, 1, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.tagsForm.addWidget(self.objKeyLabel, 5, 0, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.tagsForm.addWidget(self.objKeyValue, 5, 1, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.tagsForm.addWidget(self.entKeyLabel, 6, 0, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.tagsForm.addWidget(self.entKeyValue, 6, 1, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.tagsForm.addWidget(self.cstKeyLabel, 7, 0, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.tagsForm.addWidget(self.cstKeyValue, 7, 1, 1, 1, Qt.AlignTop | Qt.AlignLeft)

        self.tagsForm.setColumnStretch(1, 1)
        self.tagsForm.setRowStretch(8, 1)
        self.tagsForm.setHorizontalSpacing(hSpace)
        self.tagsForm.setVerticalSpacing(vSpace)

        # Assemble
        self.outerBox = QHBoxLayout()
        self.outerBox.addWidget(self.mainGroup, 0)
        self.outerBox.addWidget(self.tagsGroup, 1)
        self.outerBox.addStretch(1)

        self.setLayout(self.outerBox)

        logger.debug("GuiOutlineDetails initialisation complete")

        return

    def showItem(self, tHandle, sTitle):
        """Update the content of the tree with the given handle and line
        number pointing to a header.
        """
        try:
            nwItem  = self.theProject.projTree[tHandle]
            novIdx  = self.theIndex.novelIndex[tHandle][sTitle]
            theRefs = self.theIndex.getReferences(tHandle, sTitle)
        except:
            return False

        self.titleValue.setText(novIdx["title"])
        if novIdx["level"] in self.LVL_MAP:
            self.levelValue.setText(self.LVL_MAP[novIdx["level"]])
        else:
            self.levelValue.setText("Unknown")
        self.fileValue.setText(nwItem.itemName)

        self.cCValue.setText("{:n}".format(novIdx["cCount"]))
        self.wCValue.setText("{:n}".format(novIdx["pCount"]))
        self.pCValue.setText("{:n}".format(novIdx["wCount"]))

        self.synopValue.setText(novIdx["synopsis"])
        self.synopValue.adjustSize()
        # print(self.mainForm.sizeHint().width())
        # self.synopValue.setSizePolicy() (self.mainForm.sizeHint().width())

        self.povKeyValue.setText(self._formatTags(theRefs, nwKeyWords.POV_KEY))
        self.chrKeyValue.setText(self._formatTags(theRefs, nwKeyWords.CHAR_KEY))
        self.pltKeyValue.setText(self._formatTags(theRefs, nwKeyWords.PLOT_KEY))
        self.timKeyValue.setText(self._formatTags(theRefs, nwKeyWords.TIME_KEY))
        self.wldKeyValue.setText(self._formatTags(theRefs, nwKeyWords.WORLD_KEY))
        self.objKeyValue.setText(self._formatTags(theRefs, nwKeyWords.OBJECT_KEY))
        self.entKeyValue.setText(self._formatTags(theRefs, nwKeyWords.ENTITY_KEY))
        self.cstKeyValue.setText(self._formatTags(theRefs, nwKeyWords.CUSTOM_KEY))

        return True

    ##
    #  Slots
    ##

    def _tagClicked(self, theLink):
        """Capture the click of a tag in the right-most column.
        """
        logger.verbose("Clicked link: '%s'" % theLink)
        if len(theLink) > 0:
            theBits = theLink.split("=")
            if len(theBits) == 2:
                self.theParent.docViewer.loadFromTag(theBits[1])
                self.theParent.tabWidget.setCurrentWidget(self.theParent.splitView)
        return

    ##
    #  Internal Functions
    ##

    def _formatTags(self, theRefs, theKey):
        """Format the tags as clickable links.
        """
        if theKey not in theKey:
            return ""
        refTags = []
        for tTag in theRefs[theKey]:
            refTags.append("<a href='#%s=%s'>%s</a>" % (
                theKey[1:], tTag, tTag
            ))
        return ", ".join(refTags)

# END Class GuiOutlineDetails
