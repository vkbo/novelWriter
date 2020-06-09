# -*- coding: utf-8 -*-
"""novelWriter GUI Main Window SearchBar

 novelWriter – GUI Main Window SearchBar
=========================================
 Class holding the main window search bar

 File History:
 Created: 2019-09-29 [0.2.1] GuiSearchBar
 Created: 2019-10-31 [0.3.2] GuiDocViewDetails
 Created: 2020-04-25 [0.4.5] GuiDocTitleBar
 Created: 2020-06-09 [0.8.0] GuiDocViewFooter

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
from PyQt5.QtGui import QPalette, QColor, QIcon
from PyQt5.QtWidgets import (
    qApp, QWidget, QFrame, QGridLayout, QLabel, QLineEdit, QPushButton,
    QHBoxLayout, QToolButton, QScrollArea
)

from nw.constants import nwDocAction, nwUnicode

logger = logging.getLogger(__name__)

class GuiSearchBar(QWidget):

    def __init__(self, theParent):
        QWidget.__init__(self, theParent)

        logger.debug("Initialising GuiSearchBar ...")

        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theTheme   = theParent.theTheme
        self.repVisible = False

        self.setContentsMargins(0, 0, 0, 0)

        self.mainBox = QGridLayout(self)
        self.setLayout(self.mainBox)

        self.searchBox     = QLineEdit()
        self.replaceBox    = QLineEdit()
        self.searchLabel   = QLabel("Search")
        self.replaceLabel  = QLabel("Replace")
        self.closeButton   = QPushButton(self.theTheme.getIcon("close"),"")
        self.searchButton  = QPushButton(self.theTheme.getIcon("search"),"")
        self.replaceButton = QPushButton(self.theTheme.getIcon("search-replace"),"")

        self.closeButton.clicked.connect(self._doClose)
        self.searchButton.clicked.connect(self._doSearch)
        self.replaceButton.clicked.connect(self._doReplace)
        self.searchBox.returnPressed.connect(self._doSearch)
        self.replaceBox.returnPressed.connect(self._doSearch)

        self.mainBox.addWidget(QLabel(""),         0, 0)
        self.mainBox.addWidget(self.searchLabel,   0, 1)
        self.mainBox.addWidget(self.searchBox,     0, 2)
        self.mainBox.addWidget(self.searchButton,  0, 3)
        self.mainBox.addWidget(self.closeButton,   0, 4)
        self.mainBox.addWidget(self.replaceLabel,  1, 1)
        self.mainBox.addWidget(self.replaceBox,    1, 2)
        self.mainBox.addWidget(self.replaceButton, 1, 3)

        self.mainBox.setColumnStretch(0, 1)
        self.mainBox.setColumnStretch(1, 0)
        self.mainBox.setColumnStretch(2, 0)
        self.mainBox.setColumnStretch(3, 0)
        self.mainBox.setColumnStretch(4, 0)
        self.mainBox.setContentsMargins(0, 0, 0, 0)

        boxWidth = 16*self.theTheme.textNWidth
        self.searchBox.setMinimumWidth(boxWidth)
        self.replaceBox.setMinimumWidth(boxWidth)

        self._replaceVisible(False)

        logger.debug("GuiSearchBar initialisation complete")

        return

    ##
    #  Get and Set Functions
    ##

    def setSearchText(self, theText):
        """Open the search bar and set the search text to the text
        provided, if any.
        """
        if not self.isVisible():
            self.setVisible(True)
        self.searchBox.setText(theText)
        self.searchBox.setFocus()
        logger.verbose("Setting search text to '%s'" % theText)
        return True

    def setReplaceText(self, theText):
        """Set the replace text.
        """
        self._replaceVisible(True)
        self.replaceBox.setFocus()
        self.replaceBox.setText(theText)
        return True

    def getSearchText(self):
        """Return the current search text.
        """
        return self.searchBox.text()

    def getReplaceText(self):
        """Return the current replace text.
        """
        return self.replaceBox.text()

    ##
    #  Internal Functions
    ##

    def _doClose(self):
        """Hide the search/replace bar.
        """
        self._replaceVisible(False)
        self.setVisible(False)
        return

    def _doSearch(self):
        """Call the search action function for the document editor.
        """
        modKey = qApp.keyboardModifiers()
        if modKey == Qt.ShiftModifier:
            self.theParent.docEditor.docAction(nwDocAction.GO_PREV)
        else:
            self.theParent.docEditor.docAction(nwDocAction.GO_NEXT)
        return

    def _doReplace(self):
        """Call the replace action function for the document editor.
        """
        self.theParent.docEditor.docAction(nwDocAction.REPL_NEXT)
        return

    def _replaceVisible(self, isVisible):
        """Set the visibility of all the replace widgets.
        """
        self.replaceLabel.setVisible(isVisible)
        self.replaceBox.setVisible(isVisible)
        self.replaceButton.setVisible(isVisible)
        self.repVisible = isVisible
        return True

# END Class GuiSearchBar

class GuiDocTitleBar(QWidget):

    def __init__(self, theParent, isEditor):
        QWidget.__init__(self, theParent)

        logger.debug("Initialising GuiDocTitleBar ...")

        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theProject = theParent.theProject
        self.theTheme   = theParent.theTheme
        self.theHandle  = None
        self.isEditor   = isEditor

        # Make a QPalette that matches the Syntax Theme
        self.thePalette = QPalette()
        self.thePalette.setColor(QPalette.Window, QColor(*self.theTheme.colBack))
        self.thePalette.setColor(QPalette.Text, QColor(*self.theTheme.colText))

        fPx = int(0.9*self.theTheme.fontPixelSize)
        hSp = self.mainConf.pxInt(6)
        self.buttonSize = fPx + hSp

        # Main Widget Settings
        self.setContentsMargins(2*self.buttonSize, 0, 0, 0)
        self.setAutoFillBackground(True)
        self.setPalette(self.thePalette)

        # Title Label
        self.theTitle = QLabel()
        self.theTitle.setText("")
        self.theTitle.setIndent(0)
        self.theTitle.setMargin(0)
        self.theTitle.setContentsMargins(0, 0, 0, 0)
        self.theTitle.setAutoFillBackground(True)
        self.theTitle.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.theTitle.setFixedHeight(fPx)
        self.theTitle.setFrameShape(QFrame.NoFrame)
        self.theTitle.setLineWidth(0)
        self.theTitle.setPalette(self.thePalette)

        lblFont = self.theTitle.font()
        lblFont.setPointSizeF(0.9*self.theTheme.fontPointSize)
        self.theTitle.setFont(lblFont)

        buttonStyle = (
            "QToolButton {{border: none; background: transparent;}} "
            "QToolButton:hover {{border: none; background: rgba({0},{1},{2},0.2);}}"
        ).format(*self.theTheme.colText)

        # Buttons
        self.closeButton = QToolButton(self)
        self.closeButton.setIcon(self.theTheme.getIcon("close"))
        self.closeButton.setContentsMargins(0, 0, 0, 0)
        self.closeButton.setIconSize(QSize(fPx, fPx))
        self.closeButton.setFixedSize(fPx, fPx)
        self.closeButton.setStyleSheet(buttonStyle)
        self.closeButton.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.closeButton.setVisible(False)
        self.closeButton.clicked.connect(self._closeDocument)

        if self.isEditor:
            self.minmaxButton = QToolButton(self)
            self.minmaxButton.setIcon(self.theTheme.getIcon("maximise"))
            self.minmaxButton.setContentsMargins(0, 0, 0, 0)
            self.minmaxButton.setIconSize(QSize(fPx, fPx))
            self.minmaxButton.setFixedSize(fPx, fPx)
            self.minmaxButton.setStyleSheet(buttonStyle)
            self.minmaxButton.setToolButtonStyle(Qt.ToolButtonIconOnly)
            self.minmaxButton.setVisible(False)
            self.minmaxButton.clicked.connect(self._minmaxDocument)
        else:
            self.refreshButton = QToolButton(self)
            self.refreshButton.setIcon(self.theTheme.getIcon("refresh"))
            self.refreshButton.setContentsMargins(0, 0, 0, 0)
            self.refreshButton.setIconSize(QSize(fPx, fPx))
            self.refreshButton.setFixedSize(fPx, fPx)
            self.refreshButton.setStyleSheet(buttonStyle)
            self.refreshButton.setToolButtonStyle(Qt.ToolButtonIconOnly)
            self.refreshButton.setVisible(False)
            self.refreshButton.clicked.connect(self._refreshDocument)

        # Assemble Layout
        self.outerBox = QHBoxLayout()
        self.outerBox.setSpacing(hSp)
        self.outerBox.addWidget(self.theTitle, 1)
        if self.isEditor:
            self.outerBox.addWidget(self.minmaxButton, 0)
        else:
            self.outerBox.addWidget(self.refreshButton, 0)
        self.outerBox.addWidget(self.closeButton, 0)
        self.setLayout(self.outerBox)

        logger.debug("GuiDocTitleBar initialisation complete")

        return

    ##
    #  Setters
    ##

    def setTitleFromHandle(self, tHandle):
        """Sets the document title from the handle, or alternatively,
        set the whole document path.
        """
        self.theTitle.setText("")
        self.theHandle = tHandle
        if tHandle is None:
            self.closeButton.setVisible(False)
            if self.isEditor:
                self.minmaxButton.setVisible(False)
            else:
                self.refreshButton.setVisible(False)
            return False

        if self.mainConf.showFullPath:
            tTitle = []
            tTree = self.theProject.projTree.getItemPath(tHandle)
            for aHandle in reversed(tTree):
                nwItem = self.theProject.projTree[aHandle]
                if nwItem is not None:
                    tTitle.append(nwItem.itemName)
            sSep = "  %s  " % nwUnicode.U_RSAQUO
            self.theTitle.setText(sSep.join(tTitle))
        else:
            nwItem = self.theProject.projTree[tHandle]
            if nwItem is None:
                return False
            self.theTitle.setText(nwItem.itemName)

        self.closeButton.setVisible(True)
        if self.isEditor:
            self.minmaxButton.setVisible(True)
        else:
            self.refreshButton.setVisible(True)

        return True

    ##
    #  Slots
    ##

    def _closeDocument(self):
        """Trigger the close editor/viewer on the main window.
        """
        if self.isEditor:
            self.theParent.theParent.closeDocEditor()
        else:
            self.theParent.theParent.closeDocViewer()
        return

    def _minmaxDocument(self):
        """Switch on or off zen mode.
        """
        self.theParent.theParent.toggleZenMode()
        if self.theParent.theParent.isZenMode:
            self.minmaxButton.setIcon(self.theTheme.getIcon("minimise"))
            self.setContentsMargins(self.buttonSize, 0, 0, 0)
            self.closeButton.setVisible(False)
        else:
            self.minmaxButton.setIcon(self.theTheme.getIcon("maximise"))
            self.setContentsMargins(2*self.buttonSize, 0, 0, 0)
            self.closeButton.setVisible(True)
        return

    def _refreshDocument(self):
        """Reload the content of the document.
        """
        self.theParent.reloadText()
        return

    ##
    #  Events
    ##

    def mousePressEvent(self, theEvent):
        """Capture a click on the title and ensure that the item is
        selected in the project tree.
        """
        self.theParent.setSelectedHandle(self.theHandle)
        return

# END Class GuiDocTitleBar

class GuiDocViewFooter(QWidget):

    def __init__(self, theParent):
        QWidget.__init__(self, theParent)

        logger.debug("Initialising GuiDocViewFooter ...")

        self.mainConf  = nw.CONFIG
        self.theParent = theParent
        self.theTheme  = theParent.theTheme
        self.optState  = theParent.theProject.optState
        self.viewMeta  = theParent.theParent.viewMeta
        self.theHandle = None

        # Make a QPalette that matches the Syntax Theme
        self.thePalette = QPalette()
        self.thePalette.setColor(QPalette.Window, QColor(*self.theTheme.colBack))
        self.thePalette.setColor(QPalette.Text, QColor(*self.theTheme.colText))

        fPx = int(0.9*self.theTheme.fontPixelSize)
        hSp = self.mainConf.pxInt(6)

        # Main Widget Settings
        self.setContentsMargins(0, 0, 0, 0)
        self.setAutoFillBackground(True)
        self.setPalette(self.thePalette)

        buttonStyle = (
            "QToolButton {{border: none; background: transparent;}} "
            "QToolButton:hover {{border: none; background: rgba({0},{1},{2},0.2);}}"
        ).format(*self.theTheme.colText)

        # Show/Hide Details
        self.showHide = QToolButton(self)
        self.showHide.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.showHide.setStyleSheet(buttonStyle)
        self.showHide.setIcon(self.theTheme.getIcon("reference"))
        self.showHide.setIconSize(QSize(fPx, fPx))
        self.showHide.setFixedSize(QSize(fPx, fPx))
        self.showHide.clicked.connect(self._doShowHide)

        # Sticky Button
        stickyOn  = self.theTheme.getPixmap("sticky-on", (fPx, fPx))
        stickyOff = self.theTheme.getPixmap("sticky-off", (fPx, fPx))
        stickyIcon = QIcon()
        stickyIcon.addPixmap(stickyOn, QIcon.Normal, QIcon.On)
        stickyIcon.addPixmap(stickyOff, QIcon.Normal, QIcon.Off)
        self.stickyRefs = QToolButton(self)
        self.stickyRefs.setCheckable(True)
        self.stickyRefs.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.stickyRefs.setStyleSheet(buttonStyle)
        self.stickyRefs.setIcon(stickyIcon)
        self.stickyRefs.setIconSize(QSize(fPx, fPx))
        self.stickyRefs.setFixedSize(QSize(fPx, fPx))
        self.stickyRefs.toggled.connect(self._doToggleSticky)

        # Labels
        self.lblRefs = QLabel("References")
        self.lblRefs.setBuddy(self.showHide)
        self.lblRefs.setIndent(0)
        self.lblRefs.setMargin(0)
        self.lblRefs.setContentsMargins(0, 0, 0, 0)
        self.lblRefs.setAutoFillBackground(True)
        self.lblRefs.setFixedHeight(fPx)
        self.lblRefs.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.lblRefs.setPalette(self.thePalette)

        self.lblSticky = QLabel("Sticky")
        self.lblSticky.setBuddy(self.stickyRefs)
        self.lblSticky.setIndent(0)
        self.lblSticky.setMargin(0)
        self.lblSticky.setContentsMargins(0, 0, 0, 0)
        self.lblSticky.setAutoFillBackground(True)
        self.lblSticky.setFixedHeight(fPx)
        self.lblSticky.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.lblSticky.setPalette(self.thePalette)

        lblFont = self.font()
        lblFont.setPointSizeF(0.9*self.theTheme.fontPointSize)
        self.lblRefs.setFont(lblFont)
        self.lblSticky.setFont(lblFont)

        # Assemble Layout
        self.outerBox = QHBoxLayout()
        self.outerBox.setSpacing(hSp)
        self.outerBox.addWidget(self.showHide, 0)
        self.outerBox.addWidget(self.lblRefs, 0)
        self.outerBox.addWidget(self.stickyRefs, 0)
        self.outerBox.addWidget(self.lblSticky, 0)
        self.outerBox.addStretch(1)
        self.setLayout(self.outerBox)

        logger.debug("GuiDocViewFooter initialisation complete")

        return

    ##
    #  Slots
    ##

    def _doShowHide(self):
        """Toggle the expand/collapse of the panel.
        """
        isVisible = self.viewMeta.isVisible()
        self.viewMeta.setVisible(not isVisible)
        return

    def _doToggleSticky(self, theState):
        """Toggle the sticky flag for the reference panel.
        """
        logger.verbose("Reference sticky is %s" % str(theState))
        self.theParent.stickyRef = theState
        if not theState and self.theParent.theHandle is not None:
            self.viewMeta.refreshReferences(self.theParent.theHandle)
        return

# END Class GuiDocViewFooter

class GuiDocViewDetails(QScrollArea):

    def __init__(self, theParent):
        QScrollArea.__init__(self, theParent)

        logger.debug("Initialising DocViewDetails ...")
        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theProject = theParent.theProject
        self.theTheme   = theParent.theTheme
        self.currHandle = None

        self.refList = QLabel("None")
        self.refList.setWordWrap(True)
        self.refList.setAlignment(Qt.AlignTop)
        self.refList.setScaledContents(True)
        self.refList.linkActivated.connect(self._linkClicked)

        hCol = self.palette().highlight().color()
        self.linkStyle = "style='color: rgb({0},{1},{2})'".format(
            *self.theTheme.colLink
        )

        # Assemble
        self.outerWidget = QWidget()
        self.outerBox = QHBoxLayout()
        self.outerBox.addWidget(self.refList, 1)

        self.outerWidget.setLayout(self.outerBox)
        self.setWidget(self.outerWidget)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setWidgetResizable(True)
        self.setMinimumHeight(self.mainConf.pxInt(50))

        logger.debug("DocViewDetails initialisation complete")

        return

    def refreshReferences(self, tHandle):
        """Update the current list of document references from the
        project index.
        """
        self.currHandle = tHandle
        if self.theParent.docViewer.stickyRef:
            return

        theRefs = self.theParent.theIndex.getBackReferenceList(tHandle)
        theList = []
        for tHandle in theRefs:
            tItem = self.theProject.projTree[tHandle]
            if tItem is not None:
                theList.append("<a href='#head_%s:%s' %s>%s</a>" % (
                    tHandle, theRefs[tHandle], self.linkStyle, tItem.itemName
                ))

        self.refList.setText(", ".join(theList))

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

# END Class GuiDocViewDetails
