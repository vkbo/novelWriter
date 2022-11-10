"""
novelWriter – GUI Novel Tree
============================
GUI classe for the main window novel tree

File History:
Created: 2020-12-20 [1.1a0] GuiNovelTree
Created: 2022-06-12 [1.7b1] GuiNovelView
Created: 2022-06-12 [1.7b1] GuiNovelToolBar

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

from PyQt5.QtGui import QPalette
from PyQt5.QtCore import Qt, QSize, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import (
    QAbstractItemView, QActionGroup, QFrame, QHBoxLayout, QHeaderView, QLabel,
    QMenu, QSizePolicy, QToolButton, QToolTip, QTreeWidget, QTreeWidgetItem,
    QVBoxLayout, QWidget
)

from novelwriter.enum import nwDocMode, nwItemClass, nwOutline
from novelwriter.common import checkInt
from novelwriter.constants import nwHeaders, nwKeyWords, nwLabels, trConst

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
    openDocumentRequest = pyqtSignal(str, Enum, int, str)

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
        self.updateWordCounts = self.novelTree.updateWordCounts
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

    def refreshTree(self):
        """Refresh the current tree.
        """
        self.novelTree.refreshTree(rootHandle=self.theProject.data.getLastHandle("novelTree"))
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

    @pyqtSlot(str)
    def updateRootItem(self, tHandle):
        """If any root item changes, rebuild the novel root menu.
        """
        self.novelBar.buildNovelRootMenu()
        return

# END Class GuiNovelView


class GuiNovelToolBar(QWidget):

    def __init__(self, novelView):
        super().__init__(parent=novelView)

        logger.debug("Initialising GuiNovelToolBar ...")

        self.mainConf   = novelwriter.CONFIG
        self.novelView  = novelView
        self.theProject = novelView.mainGui.theProject
        self.mainTheme  = novelView.mainGui.mainTheme

        iPx = self.mainTheme.baseIconSize
        mPx = self.mainConf.pxInt(2)

        self.setContentsMargins(0, 0, 0, 0)
        self.setAutoFillBackground(True)

        # Widget Label
        self.viewLabel = QLabel("<b>%s</b>" % self.tr("Novel Outline"))
        self.viewLabel.setContentsMargins(0, 0, 0, 0)
        self.viewLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Refresh Button
        self.tbRefresh = QToolButton(self)
        self.tbRefresh.setToolTip(self.tr("Refresh"))
        self.tbRefresh.setIconSize(QSize(iPx, iPx))
        self.tbRefresh.clicked.connect(self._refreshNovelTree)

        # Novel Root Menu
        self.mRoot = QMenu()
        self.gRoot = QActionGroup(self.mRoot)
        self.aRoot = {}

        self.tbRoot = QToolButton(self)
        self.tbRoot.setToolTip(self.tr("Novel Root"))
        self.tbRoot.setIconSize(QSize(iPx, iPx))
        self.tbRoot.setMenu(self.mRoot)
        self.tbRoot.setPopupMode(QToolButton.InstantPopup)

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
        self.outerBox.addWidget(self.viewLabel)
        self.outerBox.addWidget(self.tbRefresh)
        self.outerBox.addWidget(self.tbRoot)
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
        self.tbRefresh.setIcon(self.mainTheme.getIcon("refresh"))
        self.tbRoot.setIcon(self.mainTheme.getIcon(nwLabels.CLASS_ICON[nwItemClass.NOVEL]))
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

        self.tbRefresh.setStyleSheet(buttonStyle)
        self.tbRoot.setStyleSheet(buttonStyle)
        self.tbMore.setStyleSheet(buttonStyle)

        return

    def clearContent(self):
        """Run clearing project tasks.
        """
        self.mRoot.clear()
        self.aRoot = {}
        return

    def buildNovelRootMenu(self):
        """Build the novel root menu.
        """
        self.mRoot.clear()
        self.aRoot = {}
        for n, (tHandle, nwItem) in enumerate(self.theProject.tree.iterRoots(nwItemClass.NOVEL)):
            aRoot = self.mRoot.addAction(nwItem.itemName)
            aRoot.setData(tHandle)
            aRoot.setCheckable(True)
            aRoot.triggered.connect(lambda n, tHandle=tHandle: self.setCurrentRoot(tHandle))
            self.gRoot.addAction(aRoot)
            self.aRoot[tHandle] = aRoot

        return

    def setCurrentRoot(self, rootHandle):
        """Set the current active root handle.
        """
        if rootHandle in self.aRoot:
            self.aRoot[rootHandle].setChecked(True)
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
        """Called whenever the Novel tab is activated.
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

    def updateWordCounts(self, tHandle):
        """Update the word count for a given handle.
        """
        tHeaders = self.theProject.index.getHandleWordCounts(tHandle)
        for titleKey, wCount in tHeaders:
            if titleKey in self._treeMap:
                self._treeMap[titleKey].setText(self.C_WORDS, f"{wCount:n}")
        return

    def getSelectedHandle(self):
        """Get the currently selected handle. If multiple items are
        selected, return the first.
        """
        selItem = self.selectedItems()
        tHandle = None
        tLine = 0
        if selItem:
            tHandle = selItem[0].data(self.C_TITLE, self.D_HANDLE)
            sTitle = selItem[0].data(self.C_TITLE, self.D_TITLE)
            tLine = checkInt(sTitle[1:], 1) - 1

        return tHandle, tLine

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

            tHandle, _ = self.getSelectedHandle()
            if tHandle is None:
                return

            self.novelView.openDocumentRequest.emit(tHandle, nwDocMode.VIEW, -1, "")

        return

    def focusOutEvent(self, theEvent):
        """Clear the selection when the tree no longer has focus.
        """
        super().focusOutEvent(theEvent)
        self.clearSelection()
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
        tHandle, tLine = self.getSelectedHandle()
        self.novelView.openDocumentRequest.emit(tHandle, nwDocMode.EDIT, tLine, "")
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

            iLevel = nwHeaders.H_LEVEL.get(novIdx.level, 0)
            if iLevel == 0:
                continue

            hDec = self.mainTheme.getHeaderDecoration(iLevel)

            newItem = QTreeWidgetItem()
            newItem.setData(self.C_TITLE, Qt.DecorationRole, hDec)
            newItem.setText(self.C_TITLE, novIdx.title)
            newItem.setData(self.C_TITLE, self.D_HANDLE, tHandle)
            newItem.setData(self.C_TITLE, self.D_TITLE, sTitle)
            newItem.setData(self.C_TITLE, self.D_KEY, tKey)
            newItem.setFont(self.C_TITLE, self._hFonts[iLevel])
            newItem.setText(self.C_WORDS, f"{novIdx.wordCount:n}")
            newItem.setTextAlignment(self.C_WORDS, Qt.AlignRight)
            newItem.setData(self.C_MORE, Qt.DecorationRole, self._pMore)

            # Custom column
            lastText, toolTip = self._getLastColumnText(tHandle, sTitle)
            newItem.setText(self.C_EXTRA, lastText)
            if lastText:
                newItem.setToolTip(self.C_EXTRA, toolTip)

            self._treeMap[tKey] = newItem
            self.addTopLevelItem(newItem)

        self.setActiveHandle(self._actHandle)

        logger.debug("Novel Tree built in %.3f ms", (time() - tStart)*1000)
        self._lastBuild = time()

        return

    def _getLastColumnText(self, tHandle, sTitle):
        """Generate the text for the last column based on user settings.
        """
        if self._lastCol == NovelTreeColumn.HIDDEN:
            return "", ""

        theRefs = self.theProject.index.getReferences(tHandle, sTitle)
        if self._lastCol == NovelTreeColumn.POV:
            newText = ", ".join(theRefs[nwKeyWords.POV_KEY])
            return newText, f"{self._povLabel}: {newText}"

        elif self._lastCol == NovelTreeColumn.FOCUS:
            newText = ", ".join(theRefs[nwKeyWords.FOCUS_KEY])
            return newText, f"{self._focLabel}: {newText}"

        elif self._lastCol == NovelTreeColumn.PLOT:
            newText = ", ".join(theRefs[nwKeyWords.PLOT_KEY])
            return newText, f"{self._pltLabel}: {newText}"

        return "", ""

    def _popMetaBox(self, qPos, tHandle, sTitle):
        """Show the novel meta data box.
        """
        logger.debug("Generating meta data tooltip for '%s:%s'", tHandle, sTitle)

        pIndex = self.theProject.index
        novIdx = pIndex.getNovelData(tHandle, sTitle)
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
