"""
novelWriter – GUI Novel Tree
============================
GUI classe for the main window novel tree

File History:
Created: 2020-12-20 [1.1rc1] GuiNovelTree
Created: 2022-06-12 [2.0rc1] GuiNovelView
Created: 2022-06-12 [2.0rc1] GuiNovelToolBar

This file is a part of novelWriter
Copyright 2018–2020, Veronica Berglyd Olsen

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

from enum import Enum
from time import time

from PyQt5.QtGui import QFont, QPalette
from PyQt5.QtCore import Qt, QSize, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import (
    QAbstractItemView, QActionGroup, QFrame, QHBoxLayout, QHeaderView, QMenu,
    QSizePolicy, QToolButton, QToolTip, QTreeWidget, QTreeWidgetItem,
    QVBoxLayout, QWidget
)

from novelwriter.enum import nwDocMode, nwItemClass, nwOutline
from novelwriter.constants import nwHeaders, nwKeyWords, nwLabels, trConst
from novelwriter.gui.components import NovelSelector

logger = logging.getLogger(__name__)


class NovelTreeColumn(Enum):

    HIDDEN = 0
    POV    = 1
    FOCUS  = 2
    PLOT   = 3

# END Enum NovelTreeColumn


class GuiNovelView(QWidget):

    # Signals for user interaction with the novel tree
    selectedItemChanged = pyqtSignal(str)
    openDocumentRequest = pyqtSignal(str, Enum, str, bool)

    def __init__(self, mainGui):
        super().__init__(parent=mainGui)

        self.mainGui    = mainGui
        self.theProject = mainGui.theProject

        # Build GUI
        self.novelTree = GuiNovelTree(self)
        self.novelBar = GuiNovelToolBar(self)
        self.novelBar.setEnabled(False)

        # Assemble
        self.outerBox = QVBoxLayout()
        self.outerBox.addWidget(self.novelBar, 0)
        self.outerBox.addWidget(self.novelTree, 1)
        self.outerBox.setContentsMargins(0, 0, 0, 0)
        self.outerBox.setSpacing(0)

        self.setLayout(self.outerBox)

        # Function Mappings
        self.getSelectedHandle = self.novelTree.getSelectedHandle
        self.setActiveHandle = self.novelTree.setActiveHandle

        return

    ##
    #  Methods
    ##

    def updateTheme(self):
        """Update theme elements.
        """
        self.novelBar.updateTheme()
        self.novelTree.updateTheme()
        self.refreshTree()
        return

    def initSettings(self):
        """Initialise GUI elements that depend on specific settings.
        """
        self.novelTree.initSettings()
        return

    def clearProject(self):
        """Clear project-related GUI content.
        """
        self.novelTree.clearContent()
        self.novelBar.clearContent()
        self.novelBar.setEnabled(False)
        return

    def openProjectTasks(self):
        """Run open project tasks.
        """
        lastNovel = self.theProject.data.getLastHandle("novelTree")
        if lastNovel not in self.theProject.tree:
            lastNovel = self.theProject.tree.findRoot(nwItemClass.NOVEL)

        logger.debug("Setting novel tree to root item '%s'", lastNovel)

        lastCol = self.theProject.options.getEnum(
            "GuiNovelView", "lastCol", NovelTreeColumn, NovelTreeColumn.HIDDEN
        )

        self.clearProject()
        self.novelBar.buildNovelRootMenu()
        self.novelBar.setLastColType(lastCol, doRefresh=False)
        self.novelBar.setCurrentRoot(lastNovel)
        self.novelBar.setEnabled(True)

        return

    def closeProjectTasks(self):
        """Run closing project tasks.
        """
        lastColType = self.novelTree.lastColType
        self.theProject.options.setValue("GuiNovelView", "lastCol", lastColType)
        return

    def setTreeFocus(self):
        """Set the focus to the tree widget.
        """
        self.novelTree.setFocus()
        return

    def treeHasFocus(self):
        """Check if the novel tree has focus.
        """
        return self.novelTree.hasFocus()

    ##
    #  Public Slots
    ##

    @pyqtSlot()
    def refreshTree(self):
        """Refresh the current tree.
        """
        self.novelTree.refreshTree(rootHandle=self.theProject.data.getLastHandle("novelTree"))
        return

    @pyqtSlot(str)
    def updateRootItem(self, tHandle):
        """If any root item changes, rebuild the novel root menu.
        """
        self.novelBar.buildNovelRootMenu()
        return

    @pyqtSlot(str)
    def updateNovelItemMeta(self, tHandle):
        """The meta data of a novel item has changed, and the tree item
        needs to be refreshed.
        """
        self.novelTree.refreshHandle(tHandle)
        return

# END Class GuiNovelView


class GuiNovelToolBar(QWidget):

    def __init__(self, novelView):
        super().__init__(parent=novelView)

        logger.debug("Initialising GuiNovelToolBar ...")

        self.mainConf   = novelwriter.CONFIG
        self.novelView  = novelView
        self.mainGui    = novelView.mainGui
        self.theProject = novelView.mainGui.theProject
        self.mainTheme  = novelView.mainGui.mainTheme

        iPx = self.mainTheme.baseIconSize
        mPx = self.mainConf.pxInt(2)

        self.setContentsMargins(0, 0, 0, 0)
        self.setAutoFillBackground(True)

        # Novel Selector
        selFont = self.font()
        selFont.setWeight(QFont.Bold)
        self.novelPrefix = self.tr("Outline of {0}")
        self.novelValue = NovelSelector(self, self.theProject, self.mainGui)
        self.novelValue.setFont(selFont)
        self.novelValue.setMinimumWidth(self.mainConf.pxInt(150))
        self.novelValue.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.novelValue.novelSelectionChanged.connect(self.setCurrentRoot)

        self.tbNovel = QToolButton(self)
        self.tbNovel.setToolTip(self.tr("Novel Root"))
        self.tbNovel.setIconSize(QSize(iPx, iPx))
        self.tbNovel.clicked.connect(self._openNovelSelector)

        # Refresh Button
        self.tbRefresh = QToolButton(self)
        self.tbRefresh.setToolTip(self.tr("Refresh"))
        self.tbRefresh.setIconSize(QSize(iPx, iPx))
        self.tbRefresh.clicked.connect(self._refreshNovelTree)

        # More Options Menu
        self.mMore = QMenu()

        self.mLastCol = self.mMore.addMenu(self.tr("Last Column"))
        self.gLastCol = QActionGroup(self.mMore)
        self.aLastCol = {}
        self._addLastColAction(NovelTreeColumn.HIDDEN, self.tr("Hidden"))
        self._addLastColAction(NovelTreeColumn.POV,    self.tr("Point of View Character"))
        self._addLastColAction(NovelTreeColumn.FOCUS,  self.tr("Focus Character"))
        self._addLastColAction(NovelTreeColumn.PLOT,   self.tr("Novel Plot"))

        self.tbMore = QToolButton(self)
        self.tbMore.setToolTip(self.tr("More Options"))
        self.tbMore.setIconSize(QSize(iPx, iPx))
        self.tbMore.setMenu(self.mMore)
        self.tbMore.setPopupMode(QToolButton.InstantPopup)

        # Assemble
        self.outerBox = QHBoxLayout()
        self.outerBox.addWidget(self.novelValue)
        self.outerBox.addWidget(self.tbNovel)
        self.outerBox.addWidget(self.tbRefresh)
        self.outerBox.addWidget(self.tbMore)
        self.outerBox.setContentsMargins(mPx, mPx, 0, mPx)
        self.outerBox.setSpacing(0)

        self.setLayout(self.outerBox)

        self.updateTheme()

        logger.debug("GuiNovelToolBar initialisation complete")

        return

    ##
    #  Methods
    ##

    def updateTheme(self):
        """Update theme elements.
        """
        # Icons
        self.tbNovel.setIcon(self.mainTheme.getIcon("cls_novel"))
        self.tbRefresh.setIcon(self.mainTheme.getIcon("refresh"))
        self.tbMore.setIcon(self.mainTheme.getIcon("menu"))

        qPalette = self.palette()
        qPalette.setBrush(QPalette.Window, qPalette.base())
        self.setPalette(qPalette)

        # StyleSheets
        fadeCol = qPalette.text().color()
        buttonStyle = (
            "QToolButton {{padding: {0}px; border: none; background: transparent;}} "
            "QToolButton:hover {{border: none; background: rgba({1},{2},{3},0.2);}}"
        ).format(self.mainConf.pxInt(2), fadeCol.red(), fadeCol.green(), fadeCol.blue())

        self.tbNovel.setStyleSheet(buttonStyle)
        self.tbRefresh.setStyleSheet(buttonStyle)
        self.tbMore.setStyleSheet(buttonStyle)

        self.novelValue.setStyleSheet(
            "QComboBox {border-style: none; padding-left: 0;} "
            "QComboBox::drop-down {border-style: none}"
        )
        self.novelValue.updateList(prefix=self.novelPrefix)
        self.tbNovel.setVisible(self.novelValue.count() > 1)

        return

    def clearContent(self):
        """Run clearing project tasks.
        """
        self.novelValue.clear()
        self.novelValue.setToolTip("")
        return

    def buildNovelRootMenu(self):
        """Build the novel root menu.
        """
        self.novelValue.updateList(prefix=self.novelPrefix)
        self.tbNovel.setVisible(self.novelValue.count() > 1)
        return

    def setCurrentRoot(self, rootHandle):
        """Set the current active root handle.
        """
        self.novelValue.setHandle(rootHandle)
        self.novelView.novelTree.refreshTree(rootHandle=rootHandle, overRide=True)
        return

    def setLastColType(self, colType, doRefresh=True):
        """Set the last column type.
        """
        self.aLastCol[colType].setChecked(True)
        self.novelView.novelTree.setLastColType(colType, doRefresh=doRefresh)
        return

    ##
    #  Private Slots
    ##

    @pyqtSlot()
    def _openNovelSelector(self):
        """Trigger the dropdown list of the novel selector.
        """
        self.novelValue.showPopup()
        return

    @pyqtSlot()
    def _refreshNovelTree(self):
        """Rebuild the current tree.
        """
        rootHandle = self.theProject.data.getLastHandle("novelTree")
        self.novelView.novelTree.refreshTree(rootHandle=rootHandle, overRide=True)
        return

    ##
    #  Internal Functions
    ##

    def _addLastColAction(self, colType, actionLabel):
        """Add a column selection entry to the last column menu.
        """
        aLast = self.mLastCol.addAction(actionLabel)
        aLast.setCheckable(True)
        aLast.setActionGroup(self.gLastCol)
        aLast.triggered.connect(lambda: self.setLastColType(colType))
        self.aLastCol[colType] = aLast
        return

# END Class GuiNovelToolBar


class GuiNovelTree(QTreeWidget):

    C_TITLE = 0
    C_WORDS = 1
    C_EXTRA = 2
    C_MORE  = 3

    D_HANDLE = Qt.UserRole
    D_TITLE  = Qt.UserRole + 1
    D_KEY    = Qt.UserRole + 2

    def __init__(self, novelView):
        super().__init__(parent=novelView)

        logger.debug("Initialising GuiNovelTree ...")

        self.mainConf   = novelwriter.CONFIG
        self.novelView  = novelView
        self.mainGui    = novelView.mainGui
        self.mainTheme  = novelView.mainGui.mainTheme
        self.theProject = novelView.mainGui.theProject

        # Internal Variables
        self._treeMap   = {}
        self._lastBuild = 0
        self._lastCol   = NovelTreeColumn.POV
        self._actHandle = None

        # Cached Strings
        self._povLabel = trConst(nwLabels.KEY_NAME[nwKeyWords.POV_KEY])
        self._focLabel = trConst(nwLabels.KEY_NAME[nwKeyWords.FOCUS_KEY])
        self._pltLabel = trConst(nwLabels.KEY_NAME[nwKeyWords.PLOT_KEY])

        # Build GUI
        # =========

        iPx = self.mainTheme.baseIconSize
        cMg = self.mainConf.pxInt(6)

        self.setIconSize(QSize(iPx, iPx))
        self.setFrameStyle(QFrame.NoFrame)
        self.setUniformRowHeights(True)
        self.setAllColumnsShowFocus(True)
        self.setHeaderHidden(True)
        self.setIndentation(0)
        self.setColumnCount(4)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setExpandsOnDoubleClick(False)
        self.setDragEnabled(False)

        # Lock the column sizes
        treeHeader = self.header()
        treeHeader.setStretchLastSection(False)
        treeHeader.setMinimumSectionSize(iPx + cMg)
        treeHeader.setSectionResizeMode(self.C_TITLE, QHeaderView.Stretch)
        treeHeader.setSectionResizeMode(self.C_WORDS, QHeaderView.ResizeToContents)
        treeHeader.setSectionResizeMode(self.C_EXTRA, QHeaderView.ResizeToContents)
        treeHeader.setSectionResizeMode(self.C_MORE, QHeaderView.ResizeToContents)

        # Pre-Generate Tree Formatting
        fH1 = self.font()
        fH1.setBold(True)
        fH1.setUnderline(True)

        fH2 = self.font()
        fH2.setBold(True)

        self._hFonts = [self.font(), fH1, fH2, self.font(), self.font()]

        # Connect signals
        self.clicked.connect(self._treeItemClicked)
        self.itemDoubleClicked.connect(self._treeDoubleClick)
        self.itemSelectionChanged.connect(self._treeSelectionChange)

        # Set custom settings
        self.initSettings()
        self.updateTheme()

        logger.debug("GuiNovelTree initialisation complete")

        return

    def initSettings(self):
        """Set or update tree widget settings.
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

    def updateTheme(self):
        """Update theme elements.
        """
        iPx = self.mainTheme.baseIconSize
        self._pMore = self.mainTheme.loadDecoration("deco_doc_more", pxH=iPx)
        return

    ##
    #  Properties
    ##

    @property
    def lastColType(self):
        return self._lastCol

    ##
    #  Class Methods
    ##

    def clearContent(self):
        """Clear the GUI content and the related maps.
        """
        self.clear()
        self._treeMap = {}
        self._lastBuild = 0
        return

    def refreshTree(self, rootHandle=None, overRide=False):
        """Refresh the tree if it has been changed.
        """
        logger.debug("Requesting refresh of the novel tree")
        if rootHandle is None:
            rootHandle = self.theProject.tree.findRoot(nwItemClass.NOVEL)

        treeChanged = self.mainGui.projView.changedSince(self._lastBuild)
        indexChanged = self.theProject.index.rootChangedSince(rootHandle, self._lastBuild)
        if not (treeChanged or indexChanged or overRide):
            logger.debug("No changes have been made to the novel index")
            return

        selItem = self.selectedItems()
        titleKey = None
        if selItem:
            titleKey = selItem[0].data(self.C_TITLE, self.D_KEY)

        self._populateTree(rootHandle)
        self.theProject.data.setLastHandle(rootHandle, "novelTree")

        if titleKey is not None and titleKey in self._treeMap:
            self._treeMap[titleKey].setSelected(True)

        return

    def refreshHandle(self, tHandle):
        """Refresh the data for a given handle.
        """
        idxData = self.theProject.index.getItemData(tHandle)
        if idxData is None:
            return

        logger.debug("Refreshing meta data for item '%s'", tHandle)
        for sTitle, tHeading in idxData.items():
            sKey = f"{tHandle}:{sTitle}"
            trItem = self._treeMap.get(sKey, None)
            if trItem is None:
                logger.debug("Heading '%s' not in novel tree", sKey)
                self.refreshTree()
                return

            self._updateTreeItemValues(trItem, tHeading, tHandle, sTitle)

        return

    def getSelectedHandle(self):
        """Get the currently selected or active handle. If multiple
        items are selected, return the first.
        """
        selList = self.selectedItems()
        trItem = selList[0] if selList else self.currentItem()
        if isinstance(trItem, QTreeWidgetItem):
            tHandle = trItem.data(self.C_TITLE, self.D_HANDLE)
            sTitle = trItem.data(self.C_TITLE, self.D_TITLE)
            return tHandle, sTitle
        return None, None

    def setLastColType(self, colType, doRefresh=True):
        """Change the content type of the last column and rebuild.
        """
        if self._lastCol != colType:
            logger.debug("Changing last column to %s", colType.name)
            self._lastCol = colType
            self.setColumnHidden(self.C_EXTRA, colType == NovelTreeColumn.HIDDEN)
            if doRefresh:
                lastNovel = self.theProject.data.getLastHandle("novelTree")
                self.refreshTree(rootHandle=lastNovel, overRide=True)
        return

    def setActiveHandle(self, tHandle):
        """Highlight the rows associated with a given handle.
        """
        tStart = time()

        self._actHandle = tHandle
        for i in range(self.topLevelItemCount()):
            tItem = self.topLevelItem(i)
            if tItem is not None:
                if tItem.data(self.C_TITLE, self.D_HANDLE) == tHandle:
                    tItem.setBackground(self.C_TITLE, self.palette().alternateBase())
                    tItem.setBackground(self.C_WORDS, self.palette().alternateBase())
                    tItem.setBackground(self.C_EXTRA, self.palette().alternateBase())
                    tItem.setBackground(self.C_MORE, self.palette().alternateBase())
                else:
                    tItem.setBackground(self.C_TITLE, self.palette().base())
                    tItem.setBackground(self.C_WORDS, self.palette().base())
                    tItem.setBackground(self.C_EXTRA, self.palette().base())
                    tItem.setBackground(self.C_MORE, self.palette().base())

        logger.debug("Highlighted Novel Tree in %.3f ms", (time() - tStart)*1000)

        return

    ##
    #  Events
    ##

    def mousePressEvent(self, theEvent):
        """Overload mousePressEvent to clear selection if clicking the
        mouse in a blank area of the tree view, and to load a document
        for viewing if the user middle-clicked.
        """
        super().mousePressEvent(theEvent)

        if theEvent.button() == Qt.LeftButton:
            selItem = self.indexAt(theEvent.pos())
            if not selItem.isValid():
                self.clearSelection()

        elif theEvent.button() == Qt.MiddleButton:
            selItem = self.itemAt(theEvent.pos())
            if not isinstance(selItem, QTreeWidgetItem):
                return

            tHandle, sTitle = self.getSelectedHandle()
            if tHandle is None:
                return

            self.novelView.openDocumentRequest.emit(tHandle, nwDocMode.VIEW, sTitle or "", False)

        return

    def focusOutEvent(self, theEvent):
        """Clear the selection when the tree no longer has focus.
        """
        super().focusOutEvent(theEvent)
        self.clearSelection()
        return

    def resizeEvent(self, event):
        """Elide labels in the extra column.
        """
        super().resizeEvent(event)
        newW = event.size().width()
        oldW = event.oldSize().width()
        if newW != oldW:
            eliW = int(0.25 * newW)
            fMetric = self.fontMetrics()
            for i in range(self.topLevelItemCount()):
                trItem = self.topLevelItem(i)
                if isinstance(trItem, QTreeWidgetItem):
                    lastText = trItem.data(self.C_EXTRA, Qt.UserRole)
                    trItem.setText(self.C_EXTRA, fMetric.elidedText(lastText, Qt.ElideRight, eliW))
        return

    ##
    #  Private Slots
    ##

    @pyqtSlot("QModelIndex")
    def _treeItemClicked(self, mIndex):
        """The user clicked on an item in the tree.
        """
        if mIndex.column() == self.C_MORE:
            tHandle = mIndex.siblingAtColumn(self.C_TITLE).data(self.D_HANDLE)
            sTitle = mIndex.siblingAtColumn(self.C_TITLE).data(self.D_TITLE)
            tipPos = self.mapToGlobal(self.visualRect(mIndex).topRight())
            self._popMetaBox(tipPos, tHandle, sTitle)
        return

    @pyqtSlot()
    def _treeSelectionChange(self):
        """Extract the handle and line number of the currently selected
        title, and send it to the tree meta panel.
        """
        tHandle, _ = self.getSelectedHandle()
        if tHandle is not None:
            self.novelView.selectedItemChanged.emit(tHandle)
        return

    @pyqtSlot("QTreeWidgetItem*", int)
    def _treeDoubleClick(self, tItem, colNo):
        """Extract the handle and line number of the title double-
        clicked, and send it to the main gui class for opening in the
        document editor.
        """
        tHandle, sTitle = self.getSelectedHandle()
        self.novelView.openDocumentRequest.emit(tHandle, nwDocMode.EDIT, sTitle or "", True)
        return

    ##
    #  Internal Functions
    ##

    def _populateTree(self, rootHandle):
        """Build the tree based on the project index.
        """
        self.clearContent()
        tStart = time()
        logger.debug("Building novel tree for root item '%s'", rootHandle)

        novStruct = self.theProject.index.novelStructure(rootHandle=rootHandle, skipExcl=True)
        for tKey, tHandle, sTitle, novIdx in novStruct:
            if novIdx.level == "H0":
                continue

            newItem = QTreeWidgetItem()
            newItem.setData(self.C_TITLE, self.D_HANDLE, tHandle)
            newItem.setData(self.C_TITLE, self.D_TITLE, sTitle)
            newItem.setData(self.C_TITLE, self.D_KEY, tKey)
            newItem.setTextAlignment(self.C_WORDS, Qt.AlignRight)

            self._updateTreeItemValues(newItem, novIdx, tHandle, sTitle)
            self._treeMap[tKey] = newItem
            self.addTopLevelItem(newItem)

        self.setActiveHandle(self._actHandle)

        logger.debug("Novel Tree built in %.3f ms", (time() - tStart)*1000)
        self._lastBuild = time()

        return

    def _updateTreeItemValues(self, trItem, idxItem, tHandle, sTitle):
        """Set the tree item values from the index entry.
        """
        iLevel = nwHeaders.H_LEVEL.get(idxItem.level, 0)
        hDec = self.mainTheme.getHeaderDecoration(iLevel)

        trItem.setData(self.C_TITLE, Qt.DecorationRole, hDec)
        trItem.setText(self.C_TITLE, idxItem.title)
        trItem.setFont(self.C_TITLE, self._hFonts[iLevel])
        trItem.setText(self.C_WORDS, f"{idxItem.wordCount:n}")
        trItem.setData(self.C_MORE, Qt.DecorationRole, self._pMore)

        # Custom column
        mW = int(0.25 * self.viewport().width())
        lastText, toolTip = self._getLastColumnText(tHandle, sTitle)
        elideText = self.fontMetrics().elidedText(lastText, Qt.ElideRight, mW)
        trItem.setText(self.C_EXTRA, elideText)
        trItem.setData(self.C_EXTRA, Qt.UserRole, lastText)
        trItem.setToolTip(self.C_EXTRA, toolTip)

        return

    def _getLastColumnText(self, tHandle, sTitle):
        """Generate the text for the last column based on user settings.
        """
        if self._lastCol == NovelTreeColumn.HIDDEN:
            return "", ""

        refData = []
        refName = ""
        theRefs = self.theProject.index.getReferences(tHandle, sTitle)
        if self._lastCol == NovelTreeColumn.POV:
            refData = theRefs[nwKeyWords.POV_KEY]
            refName = self._povLabel

        elif self._lastCol == NovelTreeColumn.FOCUS:
            refData = theRefs[nwKeyWords.FOCUS_KEY]
            refName = self._focLabel

        elif self._lastCol == NovelTreeColumn.PLOT:
            refData = theRefs[nwKeyWords.PLOT_KEY]
            refName = self._pltLabel

        if refData:
            toolText = ", ".join(refData)
            return refData[0], f"{refName}: {toolText}"

        return "", ""

    def _popMetaBox(self, qPos, tHandle, sTitle):
        """Show the novel meta data box.
        """
        logger.debug("Generating meta data tooltip for '%s:%s'", tHandle, sTitle)

        pIndex = self.theProject.index
        novIdx = pIndex.getItemHeader(tHandle, sTitle)
        refTags = pIndex.getReferences(tHandle, sTitle)

        synopText = novIdx.synopsis
        if synopText:
            synopLabel = trConst(nwLabels.OUTLINE_COLS[nwOutline.SYNOP])
            synopText = f"<p><b>{synopLabel}</b>: {synopText}</p>"

        refLines = []
        refLines = self._appendMetaTag(refTags, nwKeyWords.POV_KEY, refLines)
        refLines = self._appendMetaTag(refTags, nwKeyWords.FOCUS_KEY, refLines)
        refLines = self._appendMetaTag(refTags, nwKeyWords.CHAR_KEY, refLines)
        refLines = self._appendMetaTag(refTags, nwKeyWords.PLOT_KEY, refLines)
        refLines = self._appendMetaTag(refTags, nwKeyWords.TIME_KEY, refLines)
        refLines = self._appendMetaTag(refTags, nwKeyWords.WORLD_KEY, refLines)
        refLines = self._appendMetaTag(refTags, nwKeyWords.OBJECT_KEY, refLines)
        refLines = self._appendMetaTag(refTags, nwKeyWords.ENTITY_KEY, refLines)
        refLines = self._appendMetaTag(refTags, nwKeyWords.CUSTOM_KEY, refLines)

        refText = ""
        if refLines:
            refList = "<br>".join(refLines)
            refText = f"<p>{refList}</p>"

        ttText = refText + synopText or self.tr("No meta data")
        if ttText:
            QToolTip.showText(qPos, ttText)

        return

    @staticmethod
    def _appendMetaTag(refs, key, lines):
        """Generate a reference list for a given reference key.
        """
        tags = ", ".join(refs.get(key, []))
        if tags:
            lines.append(f"<b>{trConst(nwLabels.KEY_NAME[key])}</b>: {tags}")
        return lines

# END Class GuiNovelTree
