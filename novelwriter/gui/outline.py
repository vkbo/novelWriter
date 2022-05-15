"""
novelWriter – GUI Project Outline
=================================
GUI class for the project outline view

File History:
Created: 2019-11-16 [0.4.1] GuiOutlineView, GuiOutlineHeaderMenu
Created: 2020-06-02 [0.7.0] GuiOutlineDetails
Created: 2022-05-15 [1.7b1] GuiOutline

This file is a part of novelWriter
Copyright 2018–2022, Veronica Berglyd Olsen

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
import novelwriter

from time import time

from PyQt5.QtCore import (
    Qt, pyqtSignal, pyqtSlot, QSize, QT_TRANSLATE_NOOP
)
from PyQt5.QtWidgets import (
    QAbstractItemView, QAction, QGridLayout, QGroupBox, QHBoxLayout, QLabel,
    QMenu, QScrollArea, QSplitter, QTreeWidget, QTreeWidgetItem, QVBoxLayout,
    QWidget
)

from novelwriter.enum import nwItemLayout, nwItemType, nwOutline, nwView
from novelwriter.common import checkInt
from novelwriter.constants import trConst, nwKeyWords, nwLabels


logger = logging.getLogger(__name__)


class GuiOutline(QWidget):

    viewChangeRequested = pyqtSignal(nwView)

    def __init__(self, theParent):
        QWidget.__init__(self, theParent)

        self.mainConf   = novelwriter.CONFIG
        self.theParent  = theParent
        self.theProject = theParent.theProject

        self.outlineView = GuiOutlineView(self)
        self.outlineData = GuiOutlineDetails(self)

        self.splitOutline = QSplitter(Qt.Vertical)
        self.splitOutline.addWidget(self.outlineView)
        self.splitOutline.addWidget(self.outlineData)
        self.splitOutline.setSizes(self.mainConf.getOutlinePanePos())

        # Assemble
        self.outerBox = QVBoxLayout()
        self.outerBox.setContentsMargins(0, 0, 0, 0)
        self.outerBox.addWidget(self.splitOutline)

        self.setLayout(self.outerBox)

        # Function Mappings
        self.getSelectedHandle = self.outlineView.getSelectedHandle

        return

    ##
    #  Methods
    ##

    def splitSizes(self):
        return self.splitOutline.sizes()

    def clearOutline(self):
        self.outlineData.clearDetails()
        return

    def initOutline(self):
        self.outlineView.initOutline()
        self.outlineData.initDetails()
        return

    def closeOutline(self):
        self.outlineView.closeOutline()
        return

    def refreshView(self, overRide=False, novelChanged=False):
        self.outlineView.refreshTree(overRide=overRide, novelChanged=novelChanged)
        return

    def treeFocus(self):
        return self.outlineView.hasFocus()

    def setTreeFocus(self):
        return self.outlineView.setFocus()

# END Class GuiOutline


class GuiOutlineView(QTreeWidget):

    DEF_WIDTH = {
        nwOutline.TITLE:  200,
        nwOutline.LEVEL:  40,
        nwOutline.LABEL:  150,
        nwOutline.LINE:   40,
        nwOutline.CCOUNT: 50,
        nwOutline.WCOUNT: 50,
        nwOutline.PCOUNT: 50,
        nwOutline.POV:    100,
        nwOutline.FOCUS:  100,
        nwOutline.CHAR:   100,
        nwOutline.PLOT:   100,
        nwOutline.TIME:   100,
        nwOutline.WORLD:  100,
        nwOutline.OBJECT: 100,
        nwOutline.ENTITY: 100,
        nwOutline.CUSTOM: 100,
        nwOutline.SYNOP:  200,
    }

    DEF_HIDDEN = {
        nwOutline.TITLE:  False,
        nwOutline.LEVEL:  True,
        nwOutline.LABEL:  False,
        nwOutline.LINE:   True,
        nwOutline.CCOUNT: True,
        nwOutline.WCOUNT: False,
        nwOutline.PCOUNT: False,
        nwOutline.POV:    False,
        nwOutline.FOCUS:  True,
        nwOutline.CHAR:   False,
        nwOutline.PLOT:   False,
        nwOutline.TIME:   True,
        nwOutline.WORLD:  False,
        nwOutline.OBJECT: True,
        nwOutline.ENTITY: True,
        nwOutline.CUSTOM: True,
        nwOutline.SYNOP:  False,
    }

    def __init__(self, theOutline):
        QTreeWidget.__init__(self, theOutline)

        logger.debug("Initialising GuiOutline ...")

        self.mainConf   = novelwriter.CONFIG
        self.theOutline = theOutline
        self.theParent  = theOutline.theParent
        self.theProject = theOutline.theParent.theProject
        self.theTheme   = theOutline.theParent.theTheme
        self.theIndex   = theOutline.theParent.theIndex
        self.optState   = theOutline.theParent.theProject.optState
        self.headerMenu = GuiOutlineHeaderMenu(self)

        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setExpandsOnDoubleClick(False)
        self.setDragEnabled(False)
        self.itemDoubleClicked.connect(self._treeDoubleClick)
        self.itemSelectionChanged.connect(self._itemSelected)

        iPx = self.theTheme.baseIconSize
        self.setIconSize(QSize(iPx, iPx))
        self.setIndentation(iPx)

        self.treeHead = self.header()
        self.treeHead.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeHead.customContextMenuRequested.connect(self._headerRightClick)
        self.treeHead.sectionMoved.connect(self._columnMoved)

        # Internals
        self._treeOrder = []
        self._colWidth  = {}
        self._colHidden = {}
        self._colIdx    = {}
        self._treeNCols = 0
        self._firstView = True
        self._lastBuild = 0

        self.initOutline()
        self.clearOutline()
        self.headerMenu.setHiddenState(self._colHidden)

        logger.debug("GuiOutline initialisation complete")

        return

    def initOutline(self):
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

    def clearOutline(self):
        """Clear the tree and header and set the default values for the
        columns arrays.
        """
        self.clear()
        self.setColumnCount(1)
        self.setHeaderLabel(trConst(nwLabels.OUTLINE_COLS[nwOutline.TITLE]))

        self._treeOrder = []
        self._colWidth  = {}
        self._colHidden = {}
        self._colIdx    = {}
        self._treeNCols = 0

        for hItem in nwOutline:
            self._treeOrder.append(hItem)
            self._colWidth[hItem] = self.DEF_WIDTH[hItem]
            self._colHidden[hItem] = self.DEF_HIDDEN[hItem]

        self._treeNCols = len(self._treeOrder)

        return

    def refreshTree(self, overRide=False, novelChanged=False):
        """Called whenever the Outline tab is activated and controls
        what data to load, and if necessary, force a rebuild of the
        tree.
        """
        # If it's the first time, we always build
        if self._firstView or self._firstView and overRide:
            self._loadHeaderState()
            self._populateTree()
            self._firstView = False
            return

        # If the novel index or novel tree has changed since the tree
        # was last built, we rebuild the tree from the updated index.
        indexChanged = self.theIndex.novelChangedSince(self._lastBuild)
        doBuild = (novelChanged or indexChanged) and self.theProject.autoOutline
        if doBuild or overRide:
            logger.debug("Rebuilding Project Outline")
            self._populateTree()

        return

    def closeOutline(self):
        """Called before a project is closed.
        """
        self._saveHeaderState()
        self.clearOutline()
        self._firstView = True
        return

    def getSelectedHandle(self):
        """Get the currently selected handle. If multiple items are
        selected, return the first.
        """
        selItem = self.selectedItems()
        tHandle = None
        tLine = 0
        if selItem:
            tHandle = selItem[0].data(self._colIdx[nwOutline.TITLE], Qt.UserRole)
            tLine = checkInt(selItem[0].text(self._colIdx[nwOutline.LINE]), 1) - 1

        return tHandle, tLine

    ##
    #  Slots
    ##

    @pyqtSlot("QTreeWidgetItem*", int)
    def _treeDoubleClick(self, tItem, tCol):
        """Extract the handle and line number of the title double-
        clicked, and send it to the main gui class for opening in the
        document editor.
        """
        tHandle, tLine = self.getSelectedHandle()
        self.theParent.openDocument(tHandle, tLine=tLine-1, doScroll=True)
        return

    @pyqtSlot()
    def _itemSelected(self):
        """Extract the handle and line number of the currently selected
        title, and send it to the details panel.
        """
        selItems = self.selectedItems()
        if selItems:
            tHandle = selItems[0].data(self._colIdx[nwOutline.TITLE], Qt.UserRole)
            sTitle  = selItems[0].data(self._colIdx[nwOutline.LINE], Qt.UserRole)
            self.theOutline.outlineData.showItem(tHandle, sTitle)
            self.theParent.treeView.setSelectedHandle(tHandle)

        return

    @pyqtSlot("QPoint")
    def _headerRightClick(self, clickPos):
        """Show the header column menu.
        """
        self.headerMenu.exec_(self.mapToGlobal(clickPos))
        return

    @pyqtSlot(int, int, int)
    def _columnMoved(self, logIdx, oldVisualIdx, newVisualIdx):
        """Make sure the order array is up to date with the actual order
        of the columns.
        """
        self._treeOrder.insert(newVisualIdx, self._treeOrder.pop(oldVisualIdx))
        self._saveHeaderState()
        return

    def _menuColumnToggled(self, isChecked, theItem):
        """Receive the changes to column visibility forwarded by the
        header context menu.
        """
        logger.verbose("User toggled Outline column '%s'", theItem.name)
        if theItem in self._colIdx:
            self.setColumnHidden(self._colIdx[theItem], not isChecked)
            self._saveHeaderState()

        return

    ##
    #  Internal Functions
    ##

    def _loadHeaderState(self):
        """Load the state of the main tree header, that is, column order
        and column width.
        """
        # Load whatever we saved last time, regardless of wether it
        # contains the correct names or number of columns. The names
        # must be valid though.
        tempOrder = self.optState.getValue("GuiOutline", "headerOrder", [])
        treeOrder = []
        for hName in tempOrder:
            try:
                treeOrder.append(nwOutline[hName])
            except Exception:
                logger.warning("Ignored unknown outline column '%s'", str(hName))

        # Add columns that was not in the file to the treeOrder array.
        for hItem in nwOutline:
            if hItem not in treeOrder:
                treeOrder.append(hItem)

        # Check that we now have a complete list, and only if so, save
        # the order loaded from file. Otherwise, we keep the default.
        if len(treeOrder) == self._treeNCols:
            self._treeOrder = treeOrder
        else:
            logger.error("Failed to extract outline column order from previous session")
            logger.error("Column count doesn't match %d != %d", len(treeOrder), self._treeNCols)

        # We load whatever column widths and hidden states we find in
        # the file, and leave the rest in their default state.
        tmpWidth = self.optState.getValue("GuiOutline", "columnWidth", {})
        for hName in tmpWidth:
            try:
                self._colWidth[nwOutline[hName]] = self.mainConf.pxInt(tmpWidth[hName])
            except Exception:
                logger.warning("Ignored unknown outline column '%s'", str(hName))

        tmpHidden = self.optState.getValue("GuiOutline", "columnHidden", {})
        for hName in tmpHidden:
            try:
                self._colHidden[nwOutline[hName]] = tmpHidden[hName]
            except Exception:
                logger.warning("Ignored unknown outline column '%s'", str(hName))

        self.headerMenu.setHiddenState(self._colHidden)

        return

    def _saveHeaderState(self):
        """Save the state of the main tree header, that is, column
        order, column width and column hidden state. We don't want to
        save the current width of hidden columns though. This preserves
        the last known width in case they're unhidden again.
        """
        # If we haven't built the tree, there is nothing to save.
        if self._lastBuild == 0:
            return

        treeOrder = []
        colWidth = {}
        colHidden = {}

        for hItem in nwOutline:
            colWidth[hItem.name] = self.mainConf.rpxInt(self._colWidth[hItem])
            colHidden[hItem.name] = self._colHidden[hItem]

        for iCol in range(self.columnCount()):
            hName = self._treeOrder[iCol].name
            treeOrder.append(hName)

            iLog = self.treeHead.logicalIndex(iCol)
            logWidth = self.mainConf.rpxInt(self.columnWidth(iLog))
            logHidden = self.isColumnHidden(iLog)

            colHidden[hName] = logHidden
            if not logHidden and logWidth > 0:
                colWidth[hName] = logWidth

        self.optState.setValue("GuiOutline", "headerOrder",  treeOrder)
        self.optState.setValue("GuiOutline", "columnWidth",  colWidth)
        self.optState.setValue("GuiOutline", "columnHidden", colHidden)
        self.optState.saveSettings()

        return

    def _populateTree(self):
        """Build the tree based on the project index, and the header
        based on the defined constants, default values and user selected
        width, order and hidden state. All columns are populated, even
        if they are hidden. This ensures that showing and hiding columns
        is fast and doesn't require a rebuild of the tree.
        """
        self.clear()

        if self._firstView:
            theLabels = []
            for i, hItem in enumerate(self._treeOrder):
                theLabels.append(trConst(nwLabels.OUTLINE_COLS[hItem]))
                self._colIdx[hItem] = i

            self.setHeaderLabels(theLabels)
            for hItem in self._treeOrder:
                self.setColumnWidth(self._colIdx[hItem], self._colWidth[hItem])
                self.setColumnHidden(self._colIdx[hItem], self._colHidden[hItem])

            # Make sure title column is always visible,
            # and handle column always hidden
            self.setColumnHidden(self._colIdx[nwOutline.TITLE], False)

            headItem = self.headerItem()
            headItem.setTextAlignment(self._colIdx[nwOutline.CCOUNT], Qt.AlignRight)
            headItem.setTextAlignment(self._colIdx[nwOutline.WCOUNT], Qt.AlignRight)
            headItem.setTextAlignment(self._colIdx[nwOutline.PCOUNT], Qt.AlignRight)

        currTitle = None
        currChapter = None
        currScene = None

        for tKey, tHandle, sTitle, novIdx in self.theIndex.novelStructure(skipExcluded=True):

            tItem = self._createTreeItem(tHandle, sTitle, novIdx)

            tLevel = novIdx["level"]
            if tLevel == "H1":
                self.addTopLevelItem(tItem)
                currTitle = tItem
                currChapter = None
                currScene = None

            elif tLevel == "H2":
                if currTitle is None:
                    self.addTopLevelItem(tItem)
                else:
                    currTitle.addChild(tItem)
                currChapter = tItem
                currScene = None

            elif tLevel == "H3":
                if currChapter is None:
                    if currTitle is None:
                        self.addTopLevelItem(tItem)
                    else:
                        currTitle.addChild(tItem)
                else:
                    currChapter.addChild(tItem)
                currScene = tItem

            elif tLevel == "H4":
                if currScene is None:
                    if currChapter is None:
                        if currTitle is None:
                            self.addTopLevelItem(tItem)
                        else:
                            currTitle.addChild(tItem)
                    else:
                        currChapter.addChild(tItem)
                else:
                    currScene.addChild(tItem)

            tItem.setExpanded(True)

        self._lastBuild = time()

        return

    def _createTreeItem(self, tHandle, sTitle, novIdx):
        """Populate a tree item with all the column values.
        """
        nwItem = self.theProject.projTree[tHandle]
        newItem = QTreeWidgetItem()
        hIcon = "doc_%s" % novIdx["level"].lower()

        hLevel = self.theIndex.getHandleHeaderLevel(tHandle)
        dIcon = self.theTheme.getItemIcon(nwItemType.FILE, None, nwItemLayout.DOCUMENT, hLevel)

        cC = int(novIdx["cCount"])
        wC = int(novIdx["wCount"])
        pC = int(novIdx["pCount"])

        newItem.setText(self._colIdx[nwOutline.TITLE],  novIdx["title"])
        newItem.setData(self._colIdx[nwOutline.TITLE],  Qt.UserRole, tHandle)
        newItem.setIcon(self._colIdx[nwOutline.TITLE],  self.theTheme.getIcon(hIcon))
        newItem.setText(self._colIdx[nwOutline.LEVEL],  novIdx["level"])
        newItem.setText(self._colIdx[nwOutline.LABEL],  nwItem.itemName)
        newItem.setIcon(self._colIdx[nwOutline.LABEL],  dIcon)
        newItem.setText(self._colIdx[nwOutline.LINE],   sTitle[1:].lstrip("0"))
        newItem.setData(self._colIdx[nwOutline.LINE],   Qt.UserRole, sTitle)
        newItem.setText(self._colIdx[nwOutline.SYNOP],  novIdx["synopsis"])
        newItem.setText(self._colIdx[nwOutline.CCOUNT], f"{cC:n}")
        newItem.setText(self._colIdx[nwOutline.WCOUNT], f"{wC:n}")
        newItem.setText(self._colIdx[nwOutline.PCOUNT], f"{pC:n}")
        newItem.setTextAlignment(self._colIdx[nwOutline.CCOUNT], Qt.AlignRight)
        newItem.setTextAlignment(self._colIdx[nwOutline.WCOUNT], Qt.AlignRight)
        newItem.setTextAlignment(self._colIdx[nwOutline.PCOUNT], Qt.AlignRight)

        theRefs = self.theIndex.getReferences(tHandle, sTitle)
        newItem.setText(self._colIdx[nwOutline.POV],    ", ".join(theRefs[nwKeyWords.POV_KEY]))
        newItem.setText(self._colIdx[nwOutline.FOCUS],  ", ".join(theRefs[nwKeyWords.FOCUS_KEY]))
        newItem.setText(self._colIdx[nwOutline.CHAR],   ", ".join(theRefs[nwKeyWords.CHAR_KEY]))
        newItem.setText(self._colIdx[nwOutline.PLOT],   ", ".join(theRefs[nwKeyWords.PLOT_KEY]))
        newItem.setText(self._colIdx[nwOutline.TIME],   ", ".join(theRefs[nwKeyWords.TIME_KEY]))
        newItem.setText(self._colIdx[nwOutline.WORLD],  ", ".join(theRefs[nwKeyWords.WORLD_KEY]))
        newItem.setText(self._colIdx[nwOutline.OBJECT], ", ".join(theRefs[nwKeyWords.OBJECT_KEY]))
        newItem.setText(self._colIdx[nwOutline.ENTITY], ", ".join(theRefs[nwKeyWords.ENTITY_KEY]))
        newItem.setText(self._colIdx[nwOutline.CUSTOM], ", ".join(theRefs[nwKeyWords.CUSTOM_KEY]))

        return newItem

# END Class GuiOutlineView


class GuiOutlineHeaderMenu(QMenu):

    def __init__(self, theParent):
        QMenu.__init__(self, theParent)

        self.theParent = theParent
        self.acceptToggle = True

        mnuHead = QAction(self.tr("Select Columns"), self)
        self.addAction(mnuHead)
        self.addSeparator()

        self.actionMap = {}
        for hItem in nwOutline:
            if hItem == nwOutline.TITLE:
                continue
            self.actionMap[hItem] = QAction(trConst(nwLabels.OUTLINE_COLS[hItem]), self)
            self.actionMap[hItem].setCheckable(True)
            self.actionMap[hItem].toggled.connect(
                lambda isChecked, tItem=hItem: self._columnToggled(isChecked, tItem)
            )
            self.addAction(self.actionMap[hItem])

        return

    def setHiddenState(self, hiddenState):
        """Overwrite the checked state of the columns as the inverse of
        the hidden state. Skip the TITLE column as it cannot be hidden.
        """
        self.acceptToggle = False

        for hItem in nwOutline:
            if hItem == nwOutline.TITLE or hItem not in hiddenState:
                continue
            self.actionMap[hItem].setChecked(not hiddenState[hItem])

        self.acceptToggle = True

        return

    ##
    #  Slots
    ##

    def _columnToggled(self, isChecked, theItem):
        """The user has toggled the visibility of a column. Forward the
        event to the parent class only if we're accepting changes.
        """
        if self.acceptToggle:
            self.theParent._menuColumnToggled(isChecked, theItem)
        return

# END Class GuiOutlineHeaderMenu


class GuiOutlineDetails(QScrollArea):

    LVL_MAP = {
        "H1": QT_TRANSLATE_NOOP("GuiOutlineDetails", "Title"),
        "H2": QT_TRANSLATE_NOOP("GuiOutlineDetails", "Chapter"),
        "H3": QT_TRANSLATE_NOOP("GuiOutlineDetails", "Scene"),
        "H4": QT_TRANSLATE_NOOP("GuiOutlineDetails", "Section"),
    }

    def __init__(self, theOutline):
        QScrollArea.__init__(self, theOutline)

        logger.debug("Initialising GuiOutlineDetails ...")

        self.mainConf   = novelwriter.CONFIG
        self.theOutline = theOutline
        self.theParent  = theOutline.theParent
        self.theProject = theOutline.theParent.theProject
        self.theTheme   = theOutline.theParent.theTheme
        self.theIndex   = theOutline.theParent.theIndex
        self.optState   = theOutline.theParent.theProject.optState

        # Sizes
        minTitle = 30*self.theTheme.textNWidth
        maxTitle = 40*self.theTheme.textNWidth
        wCount = self.theTheme.getTextWidth("999,999")
        hSpace = int(self.mainConf.pxInt(10))
        vSpace = int(self.mainConf.pxInt(4))

        # Details Area
        self.titleLabel = QLabel("<b>%s</b>" % self.tr("Title"))
        self.fileLabel  = QLabel("<b>%s</b>" % self.tr("Document"))
        self.itemLabel  = QLabel("<b>%s</b>" % self.tr("Status"))
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
        self.cCLabel = QLabel("<b>%s</b>" % self.tr("Characters"))
        self.wCLabel = QLabel("<b>%s</b>" % self.tr("Words"))
        self.pCLabel = QLabel("<b>%s</b>" % self.tr("Paragraphs"))
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
        self.synopLabel = QLabel("<b>%s</b>" % self.tr("Synopsis"))
        self.synopValue = QLabel("")
        self.synopLWrap = QHBoxLayout()
        self.synopValue.setWordWrap(True)
        self.synopValue.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.synopLWrap.addWidget(self.synopValue, 1)

        # Tags
        self.povKeyLabel = QLabel("<b>%s</b>" % trConst(nwLabels.KEY_NAME[nwKeyWords.POV_KEY]))
        self.focKeyLabel = QLabel("<b>%s</b>" % trConst(nwLabels.KEY_NAME[nwKeyWords.FOCUS_KEY]))
        self.chrKeyLabel = QLabel("<b>%s</b>" % trConst(nwLabels.KEY_NAME[nwKeyWords.CHAR_KEY]))
        self.pltKeyLabel = QLabel("<b>%s</b>" % trConst(nwLabels.KEY_NAME[nwKeyWords.PLOT_KEY]))
        self.timKeyLabel = QLabel("<b>%s</b>" % trConst(nwLabels.KEY_NAME[nwKeyWords.TIME_KEY]))
        self.wldKeyLabel = QLabel("<b>%s</b>" % trConst(nwLabels.KEY_NAME[nwKeyWords.WORLD_KEY]))
        self.objKeyLabel = QLabel("<b>%s</b>" % trConst(nwLabels.KEY_NAME[nwKeyWords.OBJECT_KEY]))
        self.entKeyLabel = QLabel("<b>%s</b>" % trConst(nwLabels.KEY_NAME[nwKeyWords.ENTITY_KEY]))
        self.cstKeyLabel = QLabel("<b>%s</b>" % trConst(nwLabels.KEY_NAME[nwKeyWords.CUSTOM_KEY]))

        self.povKeyLWrap = QHBoxLayout()
        self.focKeyLWrap = QHBoxLayout()
        self.chrKeyLWrap = QHBoxLayout()
        self.pltKeyLWrap = QHBoxLayout()
        self.timKeyLWrap = QHBoxLayout()
        self.wldKeyLWrap = QHBoxLayout()
        self.objKeyLWrap = QHBoxLayout()
        self.entKeyLWrap = QHBoxLayout()
        self.cstKeyLWrap = QHBoxLayout()

        self.povKeyValue = QLabel("")
        self.focKeyValue = QLabel("")
        self.chrKeyValue = QLabel("")
        self.pltKeyValue = QLabel("")
        self.timKeyValue = QLabel("")
        self.wldKeyValue = QLabel("")
        self.objKeyValue = QLabel("")
        self.entKeyValue = QLabel("")
        self.cstKeyValue = QLabel("")

        self.povKeyValue.setWordWrap(True)
        self.focKeyValue.setWordWrap(True)
        self.chrKeyValue.setWordWrap(True)
        self.pltKeyValue.setWordWrap(True)
        self.timKeyValue.setWordWrap(True)
        self.wldKeyValue.setWordWrap(True)
        self.objKeyValue.setWordWrap(True)
        self.entKeyValue.setWordWrap(True)
        self.cstKeyValue.setWordWrap(True)

        self.povKeyValue.linkActivated.connect(self._tagClicked)
        self.focKeyValue.linkActivated.connect(self._tagClicked)
        self.chrKeyValue.linkActivated.connect(self._tagClicked)
        self.pltKeyValue.linkActivated.connect(self._tagClicked)
        self.timKeyValue.linkActivated.connect(self._tagClicked)
        self.wldKeyValue.linkActivated.connect(self._tagClicked)
        self.objKeyValue.linkActivated.connect(self._tagClicked)
        self.entKeyValue.linkActivated.connect(self._tagClicked)
        self.cstKeyValue.linkActivated.connect(self._tagClicked)

        self.povKeyLWrap.addWidget(self.povKeyValue, 1)
        self.focKeyLWrap.addWidget(self.focKeyValue, 1)
        self.chrKeyLWrap.addWidget(self.chrKeyValue, 1)
        self.pltKeyLWrap.addWidget(self.pltKeyValue, 1)
        self.timKeyLWrap.addWidget(self.timKeyValue, 1)
        self.wldKeyLWrap.addWidget(self.wldKeyValue, 1)
        self.objKeyLWrap.addWidget(self.objKeyValue, 1)
        self.entKeyLWrap.addWidget(self.entKeyValue, 1)
        self.cstKeyLWrap.addWidget(self.cstKeyValue, 1)

        # Selected Item Details
        self.mainGroup = QGroupBox(self.tr("Title Details"), self)
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
        self.tagsGroup = QGroupBox(self.tr("Reference Tags"), self)
        self.tagsForm = QGridLayout()
        self.tagsGroup.setLayout(self.tagsForm)

        self.tagsForm.addWidget(self.povKeyLabel, 0, 0, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.tagsForm.addLayout(self.povKeyLWrap, 0, 1, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.tagsForm.addWidget(self.focKeyLabel, 1, 0, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.tagsForm.addLayout(self.focKeyLWrap, 1, 1, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.tagsForm.addWidget(self.chrKeyLabel, 2, 0, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.tagsForm.addLayout(self.chrKeyLWrap, 2, 1, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.tagsForm.addWidget(self.pltKeyLabel, 3, 0, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.tagsForm.addLayout(self.pltKeyLWrap, 3, 1, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.tagsForm.addWidget(self.timKeyLabel, 4, 0, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.tagsForm.addLayout(self.timKeyLWrap, 4, 1, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.tagsForm.addWidget(self.wldKeyLabel, 5, 0, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.tagsForm.addLayout(self.wldKeyLWrap, 5, 1, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.tagsForm.addWidget(self.objKeyLabel, 6, 0, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.tagsForm.addLayout(self.objKeyLWrap, 6, 1, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.tagsForm.addWidget(self.entKeyLabel, 7, 0, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.tagsForm.addLayout(self.entKeyLWrap, 7, 1, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.tagsForm.addWidget(self.cstKeyLabel, 8, 0, 1, 1, Qt.AlignTop | Qt.AlignLeft)
        self.tagsForm.addLayout(self.cstKeyLWrap, 8, 1, 1, 1, Qt.AlignTop | Qt.AlignLeft)

        self.tagsForm.setColumnStretch(1, 1)
        self.tagsForm.setRowStretch(8, 1)
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
        self.titleLabel.setText("<b>%s</b>" % self.tr("Title"))
        self.titleValue.setText("")
        self.fileValue.setText("")
        self.itemValue.setText("")
        self.cCValue.setText("")
        self.wCValue.setText("")
        self.pCValue.setText("")
        self.synopValue.setText("")
        self.povKeyValue.setText("")
        self.focKeyValue.setText("")
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
        nwItem = self.theProject.projTree[tHandle]
        novIdx = self.theIndex.getNovelData(tHandle, sTitle)
        theRefs = self.theIndex.getReferences(tHandle, sTitle)
        if nwItem is None or novIdx is None:
            return False

        if novIdx["level"] in self.LVL_MAP:
            self.titleLabel.setText("<b>%s</b>" % self.tr(self.LVL_MAP[novIdx["level"]]))
        else:
            self.titleLabel.setText("<b>%s</b>" % self.tr("Title"))
        self.titleValue.setText(novIdx["title"])

        itemStatus, _ = nwItem.getImportStatus()

        self.fileValue.setText(nwItem.itemName)
        self.itemValue.setText(itemStatus)

        cC = checkInt(novIdx["cCount"], 0)
        wC = checkInt(novIdx["wCount"], 0)
        pC = checkInt(novIdx["pCount"], 0)

        self.cCValue.setText(f"{cC:n}")
        self.wCValue.setText(f"{wC:n}")
        self.pCValue.setText(f"{pC:n}")

        self.synopValue.setText(novIdx["synopsis"])

        self.povKeyValue.setText(self._formatTags(theRefs, nwKeyWords.POV_KEY))
        self.focKeyValue.setText(self._formatTags(theRefs, nwKeyWords.FOCUS_KEY))
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
        logger.verbose("Clicked link: '%s'", theLink)
        if len(theLink) > 0:
            theBits = theLink.split("=")
            if len(theBits) == 2:
                self.theOutline.viewChangeRequested.emit(nwView.PROJECT)
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
