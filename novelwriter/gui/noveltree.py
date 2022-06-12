"""
novelWriter – GUI Novel Tree
============================
GUI classe for the main window novel tree

File History:
Created: 2020-12-20 [1.1a0]

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

from time import time
from enum import Enum

from PyQt5.QtCore import Qt, QSize, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import (
    QAbstractItemView, QActionGroup, QFrame, QHBoxLayout, QHeaderView, QLabel,
    QMenu, QSizePolicy, QToolButton, QTreeWidget, QTreeWidgetItem, QVBoxLayout,
    QWidget
)

from novelwriter.enum import nwDocMode, nwItemClass
from novelwriter.common import checkInt
from novelwriter.constants import nwKeyWords, nwLabels, trConst

logger = logging.getLogger(__name__)


class NovelColumnType(Enum):

    HIDDEN = 0
    POV    = 1
    FOCUS  = 2
    PLOT   = 3

# END Enum NovelColumnType


class GuiNovelView(QWidget):

    # Signals for user interaction with the novel tree
    selectedItemChanged = pyqtSignal(str)
    openDocumentRequest = pyqtSignal(str, Enum, int, str)

    def __init__(self, mainGui):
        QWidget.__init__(self, mainGui)

        self.mainGui    = mainGui
        self.theProject = mainGui.theProject

        # Build GUI
        self.novelTree = GuiNovelTree(self)
        self.novelBar = GuiNovelToolBar(self)

        # Assemble
        self.outerBox = QVBoxLayout()
        self.outerBox.addWidget(self.novelBar, 0)
        self.outerBox.addWidget(self.novelTree, 1)
        self.outerBox.setContentsMargins(0, 0, 0, 0)
        self.outerBox.setSpacing(0)

        self.setLayout(self.outerBox)

        # Connect Signals
        self.novelBar.rootFolderSelectionChanged.connect(
            lambda tHandle: self.novelTree.refreshTree(rootHandle=tHandle, overRide=True)
        )

        # Function Mappings
        self.refreshTree = self.novelTree.refreshTree
        self.updateWordCounts = self.novelTree.updateWordCounts
        self.getSelectedHandle = self.novelTree.getSelectedHandle

        return

    ##
    #  Methods
    ##

    def initSettings(self):
        self.novelTree.initSettings()
        return

    def clearProject(self):
        self.novelTree.clearTree()
        return

    def openProjectTasks(self):
        """Run tasks when opening a project.
        """
        lastNovel = self.theProject.lastNovel
        if lastNovel is None:
            lastNovel = self.theProject.tree.findRoot(nwItemClass.NOVEL)

        logger.debug("Setting novel tree to root item '%s'", lastNovel)

        self.clearProject()
        self.novelBar.rebuildNovelRootMenu(selHandle=lastNovel)
        self.novelTree.loadOptions()
        self.novelTree.refreshTree(rootHandle=lastNovel, overRide=True)

        return

    def closeProjectTasks(self):
        """Run tasks when closing a project.
        """
        self.novelTree.saveOptions()
        return

    def setFocus(self):
        """Forward the set focus call to the tree widget.
        """
        self.novelTree.setFocus()
        return

    def treeFocus(self):
        """Check if the novel tree has focus.
        """
        return self.novelTree.hasFocus()

    ##
    #  Public Slots
    ##

    @pyqtSlot(str)
    def updateRootItem(self, tHandle):
        """Should be called whenever a root folders changes.
        """
        self.novelBar.rebuildNovelRootMenu()
        return

# END Class GuiNovelView


class GuiNovelToolBar(QWidget):

    rootFolderSelectionChanged = pyqtSignal(str)

    def __init__(self, novelView):
        QTreeWidget.__init__(self, novelView)

        logger.debug("Initialising GuiNovelToolBar ...")

        self.mainConf   = novelwriter.CONFIG
        self.novelView  = novelView
        self.theProject = novelView.mainGui.theProject
        self.mainTheme  = novelView.mainGui.mainTheme

        iPx = self.mainTheme.baseIconSize
        mPx = self.mainConf.pxInt(4)

        self.setContentsMargins(0, 0, 0, 0)
        self.setAutoFillBackground(True)

        qPalette = self.palette()
        qPalette.setBrush(QPalette.Window, qPalette.base())
        self.setPalette(qPalette)

        fadeCol = qPalette.text().color()
        buttonStyle = (
            "QToolButton {{padding: {0}px; border: none; background: transparent;}} "
            "QToolButton:hover {{border: none; background: rgba({1},{2},{3},0.2);}}"
        ).format(mPx, fadeCol.red(), fadeCol.green(), fadeCol.blue())

        # Widget Label
        self.viewLabel = QLabel("<b>%s</b>" % self.tr("Novel Outline"))
        self.viewLabel.setContentsMargins(0, 0, 0, 0)
        self.viewLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Refresh Button
        self.tbRefresh = QToolButton(self)
        self.tbRefresh.setToolTip(self.tr("Refresh"))
        self.tbRefresh.setIcon(self.mainTheme.getIcon("refresh"))
        self.tbRefresh.setIconSize(QSize(iPx, iPx))
        self.tbRefresh.setStyleSheet(buttonStyle)
        self.tbRefresh.clicked.connect(self._refreshNovelTree)

        # Novel Root Menu
        self.mRoot = QMenu()

        self.tbRoot = QToolButton(self)
        self.tbRoot.setToolTip(self.tr("Novel Root"))
        self.tbRoot.setIcon(self.mainTheme.getIcon(nwLabels.CLASS_ICON[nwItemClass.NOVEL]))
        self.tbRoot.setIconSize(QSize(iPx, iPx))
        self.tbRoot.setStyleSheet(buttonStyle)
        self.tbRoot.setMenu(self.mRoot)
        self.tbRoot.setPopupMode(QToolButton.InstantPopup)

        # More Options Menu
        self.mMore = QMenu()

        self.mCol3 = self.mMore.addMenu(self.tr("Third Column"))
        self.mCol3.addAction(self.tr("Hide Column")).triggered.connect(
            lambda: self.novelView.novelTree.setLastColType(NovelColumnType.HIDDEN)
        )
        self.mCol3.addAction(self.tr("Point of View Character")).triggered.connect(
            lambda: self.novelView.novelTree.setLastColType(NovelColumnType.POV)
        )
        self.mCol3.addAction(self.tr("Focus Character")).triggered.connect(
            lambda: self.novelView.novelTree.setLastColType(NovelColumnType.FOCUS)
        )
        self.mCol3.addAction(self.tr("Novel Plot")).triggered.connect(
            lambda: self.novelView.novelTree.setLastColType(NovelColumnType.PLOT)
        )

        self.tbMore = QToolButton(self)
        self.tbMore.setToolTip(self.tr("More Options"))
        self.tbMore.setIcon(self.mainTheme.getIcon("menu"))
        self.tbMore.setIconSize(QSize(iPx, iPx))
        self.tbMore.setStyleSheet(buttonStyle)
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

        logger.debug("GuiNovelToolBar initialisation complete")

        return

    ##
    #  Methods
    ##

    def rebuildNovelRootMenu(self, selHandle=None):
        """Build the novel root menu.
        """
        self.mRoot.clear()

        agRoot = QActionGroup(self.mRoot)
        for n, (tHandle, nwItem) in enumerate(self.theProject.tree.iterRoots(nwItemClass.NOVEL)):
            aRoot = self.mRoot.addAction(nwItem.itemName)
            aRoot.setData(tHandle)
            aRoot.setCheckable(True)
            aRoot.triggered.connect(
                lambda n, tHandle=tHandle: self.rootFolderSelectionChanged.emit(tHandle)
            )
            agRoot.addAction(aRoot)

            if n == 0:
                aRoot.setChecked(True)
            if selHandle == tHandle:
                aRoot.setChecked(True)

        return

    ##
    #  Private Slots
    ##

    @pyqtSlot()
    def _refreshNovelTree(self):
        """Rebuild the current tree.
        """
        rootHandle = self.theProject.lastNovel
        self.novelView.novelTree.refreshTree(rootHandle=rootHandle, overRide=True)
        return

# END Class GuiNovelToolBar


class GuiNovelTree(QTreeWidget):

    C_TITLE = 0
    C_WORDS = 1
    C_LAST  = 2

    def __init__(self, novelView):
        QTreeWidget.__init__(self, novelView)

        logger.debug("Initialising GuiNovelTree ...")

        self.mainConf   = novelwriter.CONFIG
        self.novelView  = novelView
        self.mainGui    = novelView.mainGui
        self.mainTheme  = novelView.mainGui.mainTheme
        self.theProject = novelView.mainGui.theProject

        # Internal Variables
        self._treeMap   = {}
        self._lastBuild = 0
        self._lastCol   = NovelColumnType.POV

        # Cached i18n Strings
        self._povLabel = trConst(nwLabels.KEY_NAME[nwKeyWords.POV_KEY])
        self._focLabel = trConst(nwLabels.KEY_NAME[nwKeyWords.FOCUS_KEY])
        self._pltLabel = trConst(nwLabels.KEY_NAME[nwKeyWords.PLOT_KEY])

        # Build GUI
        # =========

        iPx = self.mainTheme.baseIconSize
        cMg = self.mainConf.pxInt(6)

        self.setIconSize(QSize(iPx, iPx))
        self.setFrameStyle(QFrame.NoFrame)
        self.setHeaderHidden(True)
        self.setIndentation(iPx)
        self.setColumnCount(3)
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
        treeHeader.setSectionResizeMode(self.C_LAST, QHeaderView.ResizeToContents)

        # Connect signals
        self.itemDoubleClicked.connect(self._treeDoubleClick)
        self.itemSelectionChanged.connect(self._treeSelectionChange)

        # Set custom settings
        self.initSettings()

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

    ##
    #  Class Methods
    ##

    def clearTree(self):
        """Clear the GUI content and the related maps.
        """
        self.clear()
        self._treeMap = {}
        self._lastBuild = 0
        return

    def loadOptions(self):
        """Load user options.
        """
        self._lastCol = self.theProject.options.getEnum(
            "GuiNovelView", "lastCol", NovelColumnType, NovelColumnType.POV
        )
        self.setColumnHidden(self.C_LAST, self._lastCol == NovelColumnType.HIDDEN)
        return True

    def saveOptions(self):
        """Save user options.
        """
        self.theProject.options.setValue("GuiNovelView", "lastCol", self._lastCol)
        return

    def refreshTree(self, rootHandle=None, overRide=False):
        """Called whenever the Novel tab is activated.
        """
        logger.verbose("Requesting refresh of the novel tree")
        if rootHandle is None:
            rootHandle = self.theProject.tree.findRoot(nwItemClass.NOVEL)

        treeChanged = self.mainGui.projView.changedSince(self._lastBuild)
        indexChanged = self.theProject.index.rootChangedSince(rootHandle, self._lastBuild)
        if not (treeChanged or indexChanged or overRide):
            logger.verbose("No changes have been made to the novel index")
            return

        selItem = self.selectedItems()
        titleKey = None
        if selItem:
            titleKey = selItem[0].data(self.C_TITLE, Qt.UserRole)[2]

        self._populateTree(rootHandle)
        self.theProject.setLastNovelViewed(rootHandle)

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
            tHandle = selItem[0].data(self.C_TITLE, Qt.UserRole)[0]
            tLine = checkInt(selItem[0].data(self.C_TITLE, Qt.UserRole)[1], 1) - 1

        return tHandle, tLine

    def setLastColType(self, colType):
        """Change the content type of the last column and rebuild.
        """
        if self._lastCol != colType:
            logger.debug("Changing last column to %s", colType.name)
            self._lastCol = colType
            self.setColumnHidden(self.C_LAST, colType == NovelColumnType.HIDDEN)
            self.refreshTree(rootHandle=self.theProject.lastNovel, overRide=True)
        return

    ##
    #  Events
    ##

    def mousePressEvent(self, theEvent):
        """Overload mousePressEvent to clear selection if clicking the
        mouse in a blank area of the tree view, and to load a document
        for viewing if the user middle-clicked.
        """
        QTreeWidget.mousePressEvent(self, theEvent)

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

    ##
    #  Private Slots
    ##

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
        self.clearTree()

        currTitle = None
        currChapter = None
        currScene = None

        tStart = time()

        logger.verbose("Building novel tree for root item '%s'", rootHandle)
        novStruct = self.theProject.index.novelStructure(rootHandle=rootHandle, skipExcl=True)
        for tKey, tHandle, sTitle, novIdx in novStruct:

            tItem = self._createTreeItem(tHandle, sTitle, tKey, novIdx)
            self._treeMap[tKey] = tItem

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

        logger.verbose("Novel Tree built in %.3f ms", (time() - tStart)*1000)

        self._lastBuild = time()

        return

    def _createTreeItem(self, tHandle, sTitle, titleKey, novIdx):
        """Populate a tree item with all the column values.
        """
        newItem = QTreeWidgetItem()
        hIcon   = "doc_%s" % novIdx.level.lower()
        theData = (tHandle, sTitle[1:].lstrip("0"), titleKey)

        wC = int(novIdx.wordCount)

        newItem.setText(self.C_TITLE, novIdx.title)
        newItem.setData(self.C_TITLE, Qt.UserRole, theData)
        newItem.setIcon(self.C_TITLE, self.mainTheme.getIcon(hIcon))
        newItem.setText(self.C_WORDS, f"{wC:n}")
        newItem.setTextAlignment(self.C_WORDS, Qt.AlignRight)

        if self._lastCol == NovelColumnType.HIDDEN:
            newItem.setText(self.C_LAST, "")
        else:
            theRefs = self.theProject.index.getReferences(tHandle, sTitle)
            if self._lastCol == NovelColumnType.POV:
                newText = ", ".join(theRefs[nwKeyWords.POV_KEY])
                newItem.setText(self.C_LAST, newText)
                if newText:
                    newItem.setToolTip(self.C_LAST, f"{self._povLabel}: {newText}")
            elif self._lastCol == NovelColumnType.FOCUS:
                newText = ", ".join(theRefs[nwKeyWords.FOCUS_KEY])
                newItem.setText(self.C_LAST, newText)
                if newText:
                    newItem.setToolTip(self.C_LAST, f"{self._focLabel}: {newText}")
            elif self._lastCol == NovelColumnType.PLOT:
                newText = ", ".join(theRefs[nwKeyWords.PLOT_KEY])
                newItem.setText(self.C_LAST, newText)
                if newText:
                    newItem.setToolTip(self.C_LAST, f"{self._pltLabel}: {newText}")

        return newItem

# END Class GuiNovelTree
