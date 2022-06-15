"""
novelWriter – GUI Project Outline
=================================
GUI class for the project outline view

File History:
Created: 2022-05-15 [1.7b1] GuiOutlineView
Created: 2022-05-22 [1.7b1] GuiOutlineToolBar
Created: 2019-11-16 [0.4.1] GuiOutlineTree
Created: 2019-11-16 [0.4.1] GuiOutlineHeaderMenu
Created: 2020-06-02 [0.7.0] GuiOutlineDetails

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
from enum import Enum

from PyQt5.QtCore import (
    Qt, pyqtSignal, pyqtSlot, QSize, QT_TRANSLATE_NOOP
)
from PyQt5.QtWidgets import (
    QAbstractItemView, QAction, QGridLayout, QGroupBox, QHBoxLayout, QLabel,
    QMenu, QScrollArea, QSplitter, QTreeWidget, QTreeWidgetItem, QVBoxLayout,
    QWidget, QFrame, QToolBar, QSizePolicy, QComboBox, QToolButton
)

from novelwriter.enum import (
    nwDocMode, nwItemClass, nwItemLayout, nwItemType, nwOutline
)
from novelwriter.common import checkInt
from novelwriter.constants import trConst, nwKeyWords, nwLabels


logger = logging.getLogger(__name__)


class GuiOutlineView(QWidget):

    loadDocumentTagRequest = pyqtSignal(str, Enum)

    def __init__(self, mainGui):
        QWidget.__init__(self, mainGui)

        self.mainConf = novelwriter.CONFIG
        self.mainGui  = mainGui

        # Build GUI
        self.outlineBar  = GuiOutlineToolBar(self)
        self.outlineTree = GuiOutlineTree(self)
        self.outlineData = GuiOutlineDetails(self)

        self.splitOutline = QSplitter(Qt.Vertical)
        self.splitOutline.addWidget(self.outlineTree)
        self.splitOutline.addWidget(self.outlineData)
        self.splitOutline.setSizes(self.mainConf.getOutlinePanePos())

        # Assemble
        self.outerBox = QVBoxLayout()
        self.outerBox.setContentsMargins(0, 0, 0, 0)
        self.outerBox.addWidget(self.outlineBar)
        self.outerBox.addWidget(self.splitOutline)

        self.setLayout(self.outerBox)

        # Connect Signals
        self.outlineTree.hiddenStateChanged.connect(self._updateMenuColumns)
        self.outlineTree.activeItemChanged.connect(self.outlineData.showItem)
        self.outlineData.itemTagClicked.connect(self._tagClicked)
        self.outlineBar.loadNovelRootRequest.connect(self._rootItemChanged)
        self.outlineBar.viewColumnToggled.connect(self.outlineTree.menuColumnToggled)

        # Function Mappings
        self.getSelectedHandle = self.outlineTree.getSelectedHandle

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
        self.outlineTree.initOutline()
        self.outlineData.initDetails()
        return

    def closeOutline(self):
        self.outlineTree.closeOutline()
        self.outlineData.updateClasses()
        return

    def refreshView(self, overRide=False, novelChanged=False):
        self.outlineTree.refreshTree(overRide=overRide, novelChanged=novelChanged)
        return

    def treeHasFocus(self):
        return self.outlineTree.hasFocus()

    def setTreeFocus(self):
        return self.outlineTree.setFocus()

    ##
    #  Public Slots
    ##

    @pyqtSlot(str)
    def updateRootItem(self, tHandle):
        """Should be called whenever a root folders changes.
        """
        self.outlineBar.populateNovelList()
        self.outlineData.updateClasses()
        return

    ##
    #  Private Slots
    ##

    @pyqtSlot()
    def _updateMenuColumns(self):
        """Trigger an update of the toggled state of the column menu
        checkboxes whenever a signal is received that the hidden state
        of columns has changed.
        """
        self.outlineBar.setColumnHiddenState(self.outlineTree.hiddenColumns)
        return

    @pyqtSlot(str)
    def _tagClicked(self, link):
        """Capture the click of a tag in the details panel.
        """
        if link:
            self.loadDocumentTagRequest.emit(link, nwDocMode.VIEW)
        return

    @pyqtSlot(str)
    def _rootItemChanged(self, handle):
        """The root novel handle has changed or needs to be refreshed.
        """
        self.outlineTree.refreshTree(rootHandle=(handle or None), overRide=True)
        return

# END Class GuiOutlineView


class GuiOutlineToolBar(QToolBar):

    loadNovelRootRequest = pyqtSignal(str)
    viewColumnToggled = pyqtSignal(bool, Enum)

    def __init__(self, theOutline):
        QTreeWidget.__init__(self, theOutline)

        logger.debug("Initialising GuiOutlineToolBar ...")

        self.mainConf   = novelwriter.CONFIG
        self.mainGui    = theOutline.mainGui
        self.theProject = theOutline.mainGui.theProject
        self.mainTheme  = theOutline.mainGui.mainTheme

        iPx = self.mainConf.pxInt(22)
        mPx = self.mainConf.pxInt(12)

        self.setMovable(False)
        self.setIconSize(QSize(iPx, iPx))
        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("QToolBar {border: 0px;}")

        stretch = QWidget(self)
        stretch.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Novel Selector
        self.novelLabel = QLabel(self.tr("Outline of"))
        self.novelLabel.setContentsMargins(0, 0, mPx, 0)

        self.novelValue = QComboBox(self)
        self.novelValue.setMinimumWidth(self.mainConf.pxInt(200))
        self.novelValue.currentIndexChanged.connect(self._novelValueChanged)

        # Actions
        self.aRefresh = QAction(self.tr("Refresh"), self)
        self.aRefresh.setIcon(self.mainTheme.getIcon("refresh"))
        self.aRefresh.triggered.connect(self._refreshRequested)

        # Column Menu
        self.mColumns = GuiOutlineHeaderMenu(self)
        self.mColumns.columnToggled.connect(
            lambda isChecked, tItem: self.viewColumnToggled.emit(isChecked, tItem)
        )

        self.tbColumns = QToolButton(self)
        self.tbColumns.setIcon(self.mainTheme.getIcon("menu"))
        self.tbColumns.setMenu(self.mColumns)
        self.tbColumns.setPopupMode(QToolButton.InstantPopup)

        # Assemble
        self.addWidget(self.novelLabel)
        self.addWidget(self.novelValue)
        self.addSeparator()
        self.addAction(self.aRefresh)
        self.addWidget(self.tbColumns)
        self.addWidget(stretch)

        logger.debug("GuiOutlineToolBar initialisation complete")

        return

    ##
    #  Methods
    ##

    def populateNovelList(self):
        """Fill the novel combo box with a list of all novel folders.
        """
        self.novelValue.clear()
        tIcon = self.mainTheme.getIcon(nwLabels.CLASS_ICON[nwItemClass.NOVEL])
        for tHandle, nwItem in self.theProject.tree.iterRoots(nwItemClass.NOVEL):
            self.novelValue.addItem(tIcon, nwItem.itemName, tHandle)
        self.novelValue.insertSeparator(self.novelValue.count())
        self.novelValue.addItem(tIcon, self.tr("All Novel Folders"), "")
        return

    def setColumnHiddenState(self, hiddenState):
        """Forward the change of column hidden states to the menu.
        """
        self.mColumns.setHiddenState(hiddenState)
        return

    ##
    #  Private Slots
    ##

    @pyqtSlot(int)
    def _novelValueChanged(self, index):
        """Emit a signal containing the handle of the selected item.
        """
        if index >= 0:
            self.loadNovelRootRequest.emit(self.novelValue.currentData())
        return

    @pyqtSlot()
    def _refreshRequested(self):
        """Emit a signal containing the handle of the selected item.
        """
        self.loadNovelRootRequest.emit(self.novelValue.currentData())
        return

# END Class GuiOutlineToolBar


class GuiOutlineTree(QTreeWidget):

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

    hiddenStateChanged = pyqtSignal()
    activeItemChanged = pyqtSignal(str, str)

    def __init__(self, theOutline):
        QTreeWidget.__init__(self, theOutline)

        logger.debug("Initialising GuiOutlineTree ...")

        self.mainConf   = novelwriter.CONFIG
        self.mainGui    = theOutline.mainGui
        self.theProject = theOutline.mainGui.theProject
        self.mainTheme  = theOutline.mainGui.mainTheme

        self.setFrameStyle(QFrame.NoFrame)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setExpandsOnDoubleClick(False)
        self.setDragEnabled(False)
        self.itemDoubleClicked.connect(self._treeDoubleClick)
        self.itemSelectionChanged.connect(self._itemSelected)

        iPx = self.mainTheme.baseIconSize
        self.setIconSize(QSize(iPx, iPx))
        self.setIndentation(iPx)

        self.treeHead = self.header()
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

        self.hiddenStateChanged.emit()

        logger.debug("GuiOutlineTree initialisation complete")

        return

    ##
    #  Properties
    ##

    @property
    def hiddenColumns(self):
        return self._colHidden

    ##
    #  Methods
    ##

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

    def refreshTree(self, rootHandle=None, overRide=False, novelChanged=False):
        """Called whenever the Outline tab is activated and controls
        what data to load, and if necessary, force a rebuild of the
        tree.
        """
        # If it's the first time, we always build
        if self._firstView or self._firstView and overRide:
            self._loadHeaderState()
            self._populateTree(rootHandle)
            self._firstView = False
            return

        # If the novel index or novel tree has changed since the tree
        # was last built, we rebuild the tree from the updated index.
        indexChanged = self.theProject.index.rootChangedSince(rootHandle, self._lastBuild)
        doBuild = (novelChanged or indexChanged) and self.theProject.autoOutline
        if doBuild or overRide:
            logger.debug("Rebuilding Project Outline")
            self._populateTree(rootHandle)

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
        self.mainGui.openDocument(tHandle, tLine=tLine - 1, doScroll=True)
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
            self.activeItemChanged.emit(tHandle, sTitle)

        return

    @pyqtSlot(int, int, int)
    def _columnMoved(self, logIdx, oldVisualIdx, newVisualIdx):
        """Make sure the order array is up to date with the actual order
        of the columns.
        """
        self._treeOrder.insert(newVisualIdx, self._treeOrder.pop(oldVisualIdx))
        self._saveHeaderState()
        return

    @pyqtSlot(bool, Enum)
    def menuColumnToggled(self, isChecked, theItem):
        """Receive the changes to column visibility forwarded by the
        column selection menu.
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
        pOptions = self.theProject.options

        # Load whatever we saved last time, regardless of wether it
        # contains the correct names or number of columns. The names
        # must be valid though.
        tempOrder = pOptions.getValue("GuiOutline", "headerOrder", [])
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
        tmpWidth = pOptions.getValue("GuiOutline", "columnWidth", {})
        for hName in tmpWidth:
            try:
                self._colWidth[nwOutline[hName]] = self.mainConf.pxInt(tmpWidth[hName])
            except Exception:
                logger.warning("Ignored unknown outline column '%s'", str(hName))

        tmpHidden = pOptions.getValue("GuiOutline", "columnHidden", {})
        for hName in tmpHidden:
            try:
                self._colHidden[nwOutline[hName]] = tmpHidden[hName]
            except Exception:
                logger.warning("Ignored unknown outline column '%s'", str(hName))

        self.hiddenStateChanged.emit()

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

        pOptions = self.theProject.options
        pOptions.setValue("GuiOutline", "headerOrder",  treeOrder)
        pOptions.setValue("GuiOutline", "columnWidth",  colWidth)
        pOptions.setValue("GuiOutline", "columnHidden", colHidden)
        pOptions.saveSettings()

        return

    def _populateTree(self, rootHandle):
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

        novStruct = self.theProject.index.novelStructure(rootHandle=rootHandle, skipExcl=True)
        for _, tHandle, sTitle, novIdx in novStruct:

            tItem = self._createTreeItem(tHandle, sTitle, novIdx)

            tLevel = novIdx.level
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
        nwItem = self.theProject.tree[tHandle]
        newItem = QTreeWidgetItem()
        hIcon = "doc_%s" % novIdx.level.lower()

        hLevel = self.theProject.index.getHandleHeaderLevel(tHandle)
        dIcon = self.mainTheme.getItemIcon(nwItemType.FILE, None, nwItemLayout.DOCUMENT, hLevel)

        cC = int(novIdx.charCount)
        wC = int(novIdx.wordCount)
        pC = int(novIdx.paraCount)

        newItem.setText(self._colIdx[nwOutline.TITLE],  novIdx.title)
        newItem.setData(self._colIdx[nwOutline.TITLE],  Qt.UserRole, tHandle)
        newItem.setIcon(self._colIdx[nwOutline.TITLE],  self.mainTheme.getIcon(hIcon))
        newItem.setText(self._colIdx[nwOutline.LEVEL],  novIdx.level)
        newItem.setText(self._colIdx[nwOutline.LABEL],  nwItem.itemName)
        newItem.setIcon(self._colIdx[nwOutline.LABEL],  dIcon)
        newItem.setText(self._colIdx[nwOutline.LINE],   sTitle[1:].lstrip("0"))
        newItem.setData(self._colIdx[nwOutline.LINE],   Qt.UserRole, sTitle)
        newItem.setText(self._colIdx[nwOutline.SYNOP],  novIdx.synopsis)
        newItem.setText(self._colIdx[nwOutline.CCOUNT], f"{cC:n}")
        newItem.setText(self._colIdx[nwOutline.WCOUNT], f"{wC:n}")
        newItem.setText(self._colIdx[nwOutline.PCOUNT], f"{pC:n}")
        newItem.setTextAlignment(self._colIdx[nwOutline.CCOUNT], Qt.AlignRight)
        newItem.setTextAlignment(self._colIdx[nwOutline.WCOUNT], Qt.AlignRight)
        newItem.setTextAlignment(self._colIdx[nwOutline.PCOUNT], Qt.AlignRight)

        theRefs = self.theProject.index.getReferences(tHandle, sTitle)
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

# END Class GuiOutlineTree


class GuiOutlineHeaderMenu(QMenu):

    columnToggled = pyqtSignal(bool, Enum)

    def __init__(self, theOutline):
        QMenu.__init__(self, theOutline)

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
                lambda isChecked, tItem=hItem: self.columnToggled.emit(isChecked, tItem)
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

# END Class GuiOutlineHeaderMenu


class GuiOutlineDetails(QScrollArea):

    LVL_MAP = {
        "H1": QT_TRANSLATE_NOOP("GuiOutlineDetails", "Title"),
        "H2": QT_TRANSLATE_NOOP("GuiOutlineDetails", "Chapter"),
        "H3": QT_TRANSLATE_NOOP("GuiOutlineDetails", "Scene"),
        "H4": QT_TRANSLATE_NOOP("GuiOutlineDetails", "Section"),
    }

    itemTagClicked = pyqtSignal(str)

    def __init__(self, theOutline):
        QScrollArea.__init__(self, theOutline)

        logger.debug("Initialising GuiOutlineDetails ...")

        self.mainConf   = novelwriter.CONFIG
        self.theOutline = theOutline
        self.mainGui    = theOutline.mainGui
        self.theProject = theOutline.mainGui.theProject
        self.mainTheme  = theOutline.mainGui.mainTheme

        # Sizes
        minTitle = 30*self.mainTheme.textNWidth
        maxTitle = 40*self.mainTheme.textNWidth
        wCount = self.mainTheme.getTextWidth("999,999")
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

        def tagClicked(link):
            self.itemTagClicked.emit(link)

        self.povKeyValue.linkActivated.connect(tagClicked)
        self.focKeyValue.linkActivated.connect(tagClicked)
        self.chrKeyValue.linkActivated.connect(tagClicked)
        self.pltKeyValue.linkActivated.connect(tagClicked)
        self.timKeyValue.linkActivated.connect(tagClicked)
        self.wldKeyValue.linkActivated.connect(tagClicked)
        self.objKeyValue.linkActivated.connect(tagClicked)
        self.entKeyValue.linkActivated.connect(tagClicked)
        self.cstKeyValue.linkActivated.connect(tagClicked)

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
        self.setFrameStyle(QFrame.NoFrame)

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

        self.updateClasses()

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
        self.updateClasses()
        return

    ##
    #  Slots
    ##

    @pyqtSlot(str, str)
    def showItem(self, tHandle, sTitle):
        """Update the content of the tree with the given handle and line
        number pointing to a header.
        """
        pIndex = self.theProject.index
        nwItem = self.theProject.tree[tHandle]
        novIdx = pIndex.getNovelData(tHandle, sTitle)
        theRefs = pIndex.getReferences(tHandle, sTitle)
        if nwItem is None or novIdx is None:
            return False

        if novIdx.level in self.LVL_MAP:
            self.titleLabel.setText("<b>%s</b>" % self.tr(self.LVL_MAP[novIdx.level]))
        else:
            self.titleLabel.setText("<b>%s</b>" % self.tr("Title"))
        self.titleValue.setText(novIdx.title)

        itemStatus, _ = nwItem.getImportStatus()

        self.fileValue.setText(nwItem.itemName)
        self.itemValue.setText(itemStatus)

        cC = checkInt(novIdx.charCount, 0)
        wC = checkInt(novIdx.wordCount, 0)
        pC = checkInt(novIdx.paraCount, 0)

        self.cCValue.setText(f"{cC:n}")
        self.wCValue.setText(f"{wC:n}")
        self.pCValue.setText(f"{pC:n}")

        self.synopValue.setText(novIdx.synopsis)

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

    @pyqtSlot()
    def updateClasses(self):
        """Update the visibility status of class details.
        """
        usedClasses = self.theProject.tree.rootClasses()

        pltVisible = nwItemClass.PLOT in usedClasses
        timVisible = nwItemClass.TIMELINE in usedClasses
        wldVisible = nwItemClass.WORLD in usedClasses
        objVisible = nwItemClass.OBJECT in usedClasses
        entVisible = nwItemClass.ENTITY in usedClasses
        cstVisible = nwItemClass.CUSTOM in usedClasses

        self.pltKeyLabel.setVisible(pltVisible)
        self.pltKeyValue.setVisible(pltVisible)
        self.timKeyLabel.setVisible(timVisible)
        self.timKeyValue.setVisible(timVisible)
        self.wldKeyLabel.setVisible(wldVisible)
        self.wldKeyValue.setVisible(wldVisible)
        self.objKeyLabel.setVisible(objVisible)
        self.objKeyValue.setVisible(objVisible)
        self.entKeyLabel.setVisible(entVisible)
        self.entKeyValue.setVisible(entVisible)
        self.cstKeyLabel.setVisible(cstVisible)
        self.cstKeyValue.setVisible(cstVisible)

        return

    @staticmethod
    def _formatTags(refs, key):
        """Convert a list of tags into a list of clickable tag links.
        """
        return ", ".join(
            [f"<a href='{tag}'>{tag}</a>" for tag in refs.get(key, [])]
        )

# END Class GuiOutlineDetails
