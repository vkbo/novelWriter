# -*- coding: utf-8 -*-
"""novelWriter GUI Project Outline Details

 novelWriter – GUI Project Outline Details
===========================================
 Class holding the project outline details panel

 File History:
 Created: 2020-06-02 [0.7.0]

 This file is a part of novelWriter
 Copyright 2018–2021, Veronica Berglyd Olsen

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

import nw
import logging

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QScrollArea, QWidget, QGridLayout, QHBoxLayout, QGroupBox, QLabel
)

from nw.constants import nwLabels, nwKeyWords
from nw.common import checkInt

logger = logging.getLogger(__name__)

class GuiOutlineDetails(QScrollArea):

    LVL_MAP = {
        "H1" : "Title",
        "H2" : "Chapter",
        "H3" : "Scene",
        "H4" : "Section"
    }

    def __init__(self, theParent):
        QScrollArea.__init__(self, theParent)

        logger.debug("Initialising GuiOutlineDetails ...")

        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theProject = theParent.theProject
        self.theTheme   = theParent.theTheme
        self.theIndex   = theParent.theIndex
        self.optState   = theParent.theProject.optState

        # Sizes
        minTitle = 30*self.theTheme.textNWidth
        maxTitle = 40*self.theTheme.textNWidth
        wCount = self.theTheme.getTextWidth("999,999")
        hSpace = int(self.mainConf.pxInt(10))
        vSpace = int(self.mainConf.pxInt(4))

        # Details Area
        self.titleLabel = QLabel("<b>Title</b>")
        self.fileLabel  = QLabel("<b>Document</b>")
        self.itemLabel  = QLabel("<b>Status</b>")
        self.titleValue = QLabel("")
        self.fileValue  = QLabel("")
        self.itemValue  = QLabel("")

        self.titleValue.setMinimumWidth(minTitle)
        self.titleValue.setMaximumWidth(maxTitle)
        self.fileValue.setMinimumWidth(minTitle)
        self.fileValue.setMaximumWidth(maxTitle)
        self.itemValue.setMinimumWidth(minTitle)
        self.itemValue.setMaximumWidth(maxTitle)

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

        self.povKeyLWrap = QHBoxLayout()
        self.chrKeyLWrap = QHBoxLayout()
        self.pltKeyLWrap = QHBoxLayout()
        self.timKeyLWrap = QHBoxLayout()
        self.wldKeyLWrap = QHBoxLayout()
        self.objKeyLWrap = QHBoxLayout()
        self.entKeyLWrap = QHBoxLayout()
        self.cstKeyLWrap = QHBoxLayout()

        self.povKeyValue = QLabel("")
        self.chrKeyValue = QLabel("")
        self.pltKeyValue = QLabel("")
        self.timKeyValue = QLabel("")
        self.wldKeyValue = QLabel("")
        self.objKeyValue = QLabel("")
        self.entKeyValue = QLabel("")
        self.cstKeyValue = QLabel("")

        self.povKeyValue.setWordWrap(True)
        self.chrKeyValue.setWordWrap(True)
        self.pltKeyValue.setWordWrap(True)
        self.timKeyValue.setWordWrap(True)
        self.wldKeyValue.setWordWrap(True)
        self.objKeyValue.setWordWrap(True)
        self.entKeyValue.setWordWrap(True)
        self.cstKeyValue.setWordWrap(True)

        self.povKeyValue.linkActivated.connect(self._tagClicked)
        self.chrKeyValue.linkActivated.connect(self._tagClicked)
        self.pltKeyValue.linkActivated.connect(self._tagClicked)
        self.timKeyValue.linkActivated.connect(self._tagClicked)
        self.wldKeyValue.linkActivated.connect(self._tagClicked)
        self.objKeyValue.linkActivated.connect(self._tagClicked)
        self.entKeyValue.linkActivated.connect(self._tagClicked)
        self.cstKeyValue.linkActivated.connect(self._tagClicked)

        self.povKeyLWrap.addWidget(self.povKeyValue, 1)
        self.chrKeyLWrap.addWidget(self.chrKeyValue, 1)
        self.pltKeyLWrap.addWidget(self.pltKeyValue, 1)
        self.timKeyLWrap.addWidget(self.timKeyValue, 1)
        self.wldKeyLWrap.addWidget(self.wldKeyValue, 1)
        self.objKeyLWrap.addWidget(self.objKeyValue, 1)
        self.entKeyLWrap.addWidget(self.entKeyValue, 1)
        self.cstKeyLWrap.addWidget(self.cstKeyValue, 1)

        # Selected Item Details
        self.mainGroup = QGroupBox("Title Details", self)
        self.mainForm  = QGridLayout()
        self.mainGroup.setLayout(self.mainForm)

        self.mainForm.addWidget(self.titleLabel,  0, 0, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.mainForm.addWidget(self.titleValue,  0, 1, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.mainForm.addWidget(self.cCLabel,     0, 2, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.mainForm.addWidget(self.cCValue,     0, 3, 1, 1, Qt.AlignTop | Qt.AlignRight)
        self.mainForm.addWidget(self.fileLabel,   1, 0, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.mainForm.addWidget(self.fileValue,   1, 1, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.mainForm.addWidget(self.wCLabel,     1, 2, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.mainForm.addWidget(self.wCValue,     1, 3, 1, 1, Qt.AlignTop | Qt.AlignRight)
        self.mainForm.addWidget(self.itemLabel,   2, 0, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.mainForm.addWidget(self.itemValue,   2, 1, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.mainForm.addWidget(self.pCLabel,     2, 2, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.mainForm.addWidget(self.pCValue,     2, 3, 1, 1, Qt.AlignTop | Qt.AlignRight)
        self.mainForm.addWidget(self.synopLabel,  3, 0, 1, 4, Qt.AlignTop | Qt.AlignLeft)
        self.mainForm.addLayout(self.synopLWrap,  4, 0, 1, 4, Qt.AlignTop | Qt.AlignLeft)

        self.mainForm.setColumnStretch(1, 1)
        self.mainForm.setRowStretch(4, 1)
        self.mainForm.setHorizontalSpacing(hSpace)
        self.mainForm.setVerticalSpacing(vSpace)

        # Selected Item Tags
        self.tagsGroup = QGroupBox("Reference Tags", self)
        self.tagsForm  = QGridLayout()
        self.tagsGroup.setLayout(self.tagsForm)

        self.tagsForm.addWidget(self.povKeyLabel, 0, 0, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.tagsForm.addLayout(self.povKeyLWrap, 0, 1, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.tagsForm.addWidget(self.chrKeyLabel, 1, 0, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.tagsForm.addLayout(self.chrKeyLWrap, 1, 1, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.tagsForm.addWidget(self.pltKeyLabel, 2, 0, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.tagsForm.addLayout(self.pltKeyLWrap, 2, 1, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.tagsForm.addWidget(self.timKeyLabel, 3, 0, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.tagsForm.addLayout(self.timKeyLWrap, 3, 1, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.tagsForm.addWidget(self.wldKeyLabel, 4, 0, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.tagsForm.addLayout(self.wldKeyLWrap, 4, 1, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.tagsForm.addWidget(self.objKeyLabel, 5, 0, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.tagsForm.addLayout(self.objKeyLWrap, 5, 1, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.tagsForm.addWidget(self.entKeyLabel, 6, 0, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.tagsForm.addLayout(self.entKeyLWrap, 6, 1, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.tagsForm.addWidget(self.cstKeyLabel, 7, 0, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.tagsForm.addLayout(self.cstKeyLWrap, 7, 1, 1, 1, Qt.AlignTop | Qt.AlignLeft)

        self.tagsForm.setColumnStretch(1, 1)
        self.tagsForm.setRowStretch(7, 1)
        self.tagsForm.setHorizontalSpacing(hSpace)
        self.tagsForm.setVerticalSpacing(vSpace)

        # Assemble
        self.outerWidget = QWidget()
        self.outerBox = QHBoxLayout()
        self.outerBox.addWidget(self.mainGroup, 0)
        self.outerBox.addWidget(self.tagsGroup, 1)

        self.outerWidget.setLayout(self.outerBox)
        self.setWidget(self.outerWidget)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setWidgetResizable(True)

        self.initDetails()

        logger.debug("GuiOutlineDetails initialisation complete")

        return

    def initDetails(self):
        """Set or update outline settings.
        """
        # Scroll bars
        if self.mainConf.hideVScroll:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        else:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        if self.mainConf.hideHScroll:
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        else:
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        return

    def clearDetails(self):
        """Clear all the data labels.
        """
        self.titleLabel.setText("<b>Title</b>")
        self.titleValue.setText("")
        self.fileValue.setText("")
        self.itemValue.setText("")
        self.cCValue.setText("")
        self.wCValue.setText("")
        self.pCValue.setText("")
        self.synopValue.setText("")
        self.povKeyValue.setText("")
        self.chrKeyValue.setText("")
        self.pltKeyValue.setText("")
        self.timKeyValue.setText("")
        self.wldKeyValue.setText("")
        self.objKeyValue.setText("")
        self.entKeyValue.setText("")
        self.cstKeyValue.setText("")
        return

    def showItem(self, tHandle, sTitle):
        """Update the content of the tree with the given handle and line
        number pointing to a header.
        """
        try:
            nwItem  = self.theProject.projTree[tHandle]
            novIdx  = self.theIndex.novelIndex[tHandle][sTitle]
            theRefs = self.theIndex.getReferences(tHandle, sTitle)
        except Exception:
            return False

        if novIdx["level"] in self.LVL_MAP:
            self.titleLabel.setText("<b>%s</b>" % self.LVL_MAP[novIdx["level"]])
        else:
            self.titleLabel.setText("<b>Title</b>")
        self.titleValue.setText(novIdx["title"])

        self.fileValue.setText(nwItem.itemName)
        self.itemValue.setText(nwItem.itemStatus)

        cC = checkInt(novIdx["cCount"], 0)
        wC = checkInt(novIdx["wCount"], 0)
        pC = checkInt(novIdx["pCount"], 0)

        self.cCValue.setText(f"{cC:n}")
        self.wCValue.setText(f"{wC:n}")
        self.pCValue.setText(f"{pC:n}")

        self.synopValue.setText(novIdx["synopsis"])

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
        return

    ##
    #  Internal Functions
    ##

    def _formatTags(self, theRefs, theKey):
        """Format the tags as clickable links.
        """
        if theKey not in theRefs:
            return ""
        refTags = []
        for tTag in theRefs[theKey]:
            refTags.append("<a href='#%s=%s'>%s</a>" % (
                theKey[1:], tTag, tTag
            ))
        return ", ".join(refTags)

# END Class GuiOutlineDetails
