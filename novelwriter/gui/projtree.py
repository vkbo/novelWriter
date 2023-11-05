"""
novelWriter – GUI Project Tree
==============================

File History:
Created: 2018-09-29 [0.0.1]  GuiProjectTree
Created: 2022-06-06 [2.0rc1] GuiProjectView
Created: 2022-06-06 [2.0rc1] GuiProjectToolBar

This file is a part of novelWriter
Copyright 2018–2023, Veronica Berglyd Olsen

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
from __future__ import annotations

import logging

from enum import Enum
from time import time
from typing import TYPE_CHECKING

from PyQt5.QtGui import QDragMoveEvent, QDropEvent, QMouseEvent, QPalette
from PyQt5.QtCore import QPoint, QTimer, Qt, QSize, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import (
    QAbstractItemView, QDialog, QFrame, QHBoxLayout, QHeaderView, QLabel,
    QMenu, QShortcut, QSizePolicy, QToolButton, QTreeWidget, QTreeWidgetItem,
    QVBoxLayout, QWidget
)

from novelwriter import CONFIG, SHARED
from novelwriter.common import minmax
from novelwriter.constants import nwHeaders, nwUnicode, trConst, nwLabels
from novelwriter.core.item import NWItem
from novelwriter.core.coretools import DocDuplicator, DocMerger, DocSplitter
from novelwriter.dialogs.docmerge import GuiDocMerge
from novelwriter.dialogs.docsplit import GuiDocSplit
from novelwriter.dialogs.editlabel import GuiEditLabel
from novelwriter.dialogs.projsettings import GuiProjectSettings
from novelwriter.enum import (
    nwDocMode, nwItemType, nwItemClass, nwItemLayout, nwWidget
)

if TYPE_CHECKING:  # pragma: no cover
    from novelwriter.guimain import GuiMain

logger = logging.getLogger(__name__)


class GuiProjectView(QWidget):
    """This is a wrapper class holding all the elements of the project
    tree. The core object is the project tree itself. Most methods
    available are mapped through to the project tree class.
    """

    # Signals triggered when the meta data values of items change
    treeItemChanged = pyqtSignal(str)
    rootFolderChanged = pyqtSignal(str)
    wordCountsChanged = pyqtSignal()

    # Signals for user interaction with the project tree
    selectedItemChanged = pyqtSignal(str)
    openDocumentRequest = pyqtSignal(str, Enum, str, bool)

    # Requests for the main GUI
    projectSettingsRequest = pyqtSignal(int)

    def __init__(self, mainGui: GuiMain) -> None:
        super().__init__(parent=mainGui)

        self.mainGui = mainGui

        # Build GUI
        self.projTree = GuiProjectTree(self)
        self.projBar = GuiProjectToolBar(self)
        self.projBar.setEnabled(False)

        # Assemble
        self.outerBox = QVBoxLayout()
        self.outerBox.addWidget(self.projBar, 0)
        self.outerBox.addWidget(self.projTree, 1)
        self.outerBox.setContentsMargins(0, 0, 0, 0)
        self.outerBox.setSpacing(0)

        self.setLayout(self.outerBox)

        # Keyboard Shortcuts
        self.keyMoveUp = QShortcut(self.projTree)
        self.keyMoveUp.setKey("Ctrl+Up")
        self.keyMoveUp.setContext(Qt.WidgetShortcut)
        self.keyMoveUp.activated.connect(lambda: self.projTree.moveTreeItem(-1))

        self.keyMoveDn = QShortcut(self.projTree)
        self.keyMoveDn.setKey("Ctrl+Down")
        self.keyMoveDn.setContext(Qt.WidgetShortcut)
        self.keyMoveDn.activated.connect(lambda: self.projTree.moveTreeItem(1))

        self.keyGoPrev = QShortcut(self.projTree)
        self.keyGoPrev.setKey("Alt+Up")
        self.keyGoPrev.setContext(Qt.WidgetShortcut)
        self.keyGoPrev.activated.connect(lambda: self.projTree.moveToNextItem(-1))

        self.keyGoNext = QShortcut(self.projTree)
        self.keyGoNext.setKey("Alt+Down")
        self.keyGoNext.setContext(Qt.WidgetShortcut)
        self.keyGoNext.activated.connect(lambda: self.projTree.moveToNextItem(1))

        self.keyGoUp = QShortcut(self.projTree)
        self.keyGoUp.setKey("Alt+Left")
        self.keyGoUp.setContext(Qt.WidgetShortcut)
        self.keyGoUp.activated.connect(lambda: self.projTree.moveToLevel(-1))

        self.keyGoDown = QShortcut(self.projTree)
        self.keyGoDown.setKey("Alt+Right")
        self.keyGoDown.setContext(Qt.WidgetShortcut)
        self.keyGoDown.activated.connect(lambda: self.projTree.moveToLevel(1))

        self.keyUndoMv = QShortcut(self.projTree)
        self.keyUndoMv.setKey("Ctrl+Shift+Z")
        self.keyUndoMv.setContext(Qt.WidgetShortcut)
        self.keyUndoMv.activated.connect(lambda: self.projTree.undoLastMove())

        self.keyContext = QShortcut(self.projTree)
        self.keyContext.setKey("Ctrl+.")
        self.keyContext.setContext(Qt.WidgetShortcut)
        self.keyContext.activated.connect(lambda: self.projTree.openContextOnSelected())

        # Signals
        self.selectedItemChanged.connect(self.projBar._treeSelectionChanged)

        # Function Mappings
        self.emptyTrash = self.projTree.emptyTrash
        self.requestDeleteItem = self.projTree.requestDeleteItem
        self.setTreeItemValues = self.projTree.setTreeItemValues
        self.propagateCount = self.projTree.propagateCount
        self.getSelectedHandle = self.projTree.getSelectedHandle
        self.setSelectedHandle = self.projTree.setSelectedHandle
        self.changedSince = self.projTree.changedSince

        return

    ##
    #  Methods
    ##

    def updateTheme(self) -> None:
        """Update theme elements."""
        self.projBar.updateTheme()
        self.populateTree()
        return

    def initSettings(self) -> None:
        """Initialise GUI elements that depend on specific settings."""
        self.projTree.initSettings()
        return

    def clearProjectView(self) -> None:
        """Clear project-related GUI content."""
        self.projBar.clearContent()
        self.projBar.setEnabled(False)
        self.projTree.clearTree()
        return

    def openProjectTasks(self) -> None:
        """Run open project tasks."""
        self.projBar.buildQuickLinkMenu()
        self.projBar.setEnabled(True)
        return

    def saveProjectTasks(self) -> None:
        """Run save project tasks."""
        self.projTree.saveTreeOrder()
        return

    def populateTree(self) -> None:
        """Build the tree structure from project data."""
        self.projTree.buildTree()
        return

    def setFocus(self) -> None:
        """Forward the set focus call to the tree widget."""
        self.projTree.setFocus()
        return

    def treeHasFocus(self) -> bool:
        """Check if the project tree has focus."""
        return self.projTree.hasFocus()

    def renameTreeItem(self, tHandle: str | None = None) -> bool:
        """External request to rename an item or the currently selected
        item. This is triggered by the global menu or keyboard shortcut.
        """
        if tHandle is None:
            tHandle = self.projTree.getSelectedHandle()
        return self.projTree.renameTreeItem(tHandle) if tHandle else False

    ##
    #  Public Slots
    ##

    @pyqtSlot(str, int, int, int)
    def updateCounts(self, tHandle: str, cCount: int, wCount: int, pCount: int) -> None:
        """Slot for updating the word count of a specific item."""
        self.projTree.propagateCount(tHandle, wCount, countChildren=True)
        self.wordCountsChanged.emit()
        return

    @pyqtSlot(str)
    def updateRootItem(self, tHandle: str) -> None:
        """If any root item changes, rebuild the quick link menu."""
        self.projBar.buildQuickLinkMenu()
        return

# END Class GuiProjectView


class GuiProjectToolBar(QWidget):

    def __init__(self, projView: GuiProjectView) -> None:
        super().__init__(parent=projView)

        logger.debug("Create: GuiProjectToolBar")

        self.projView = projView
        self.projTree = projView.projTree
        self.mainGui  = projView.mainGui

        iPx = SHARED.theme.baseIconSize
        mPx = CONFIG.pxInt(2)

        self.setContentsMargins(0, 0, 0, 0)
        self.setAutoFillBackground(True)

        # Widget Label
        self.viewLabel = QLabel("<b>%s</b>" % self.tr("Project Content"))
        self.viewLabel.setContentsMargins(0, 0, 0, 0)
        self.viewLabel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Quick Links
        self.mQuick = QMenu(self)

        self.tbQuick = QToolButton(self)
        self.tbQuick.setToolTip("%s [Ctrl+L]" % self.tr("Quick Links"))
        self.tbQuick.setShortcut("Ctrl+L")
        self.tbQuick.setIconSize(QSize(iPx, iPx))
        self.tbQuick.setMenu(self.mQuick)
        self.tbQuick.setPopupMode(QToolButton.InstantPopup)

        # Move Buttons
        self.tbMoveU = QToolButton(self)
        self.tbMoveU.setToolTip("%s [Ctrl+Up]" % self.tr("Move Up"))
        self.tbMoveU.setIconSize(QSize(iPx, iPx))
        self.tbMoveU.clicked.connect(lambda: self.projTree.moveTreeItem(-1))

        self.tbMoveD = QToolButton(self)
        self.tbMoveD.setToolTip("%s [Ctrl+Down]" % self.tr("Move Down"))
        self.tbMoveD.setIconSize(QSize(iPx, iPx))
        self.tbMoveD.clicked.connect(lambda: self.projTree.moveTreeItem(1))

        # Add Item Menu
        self.mAdd = QMenu(self)

        self.aAddEmpty = self.mAdd.addAction(trConst(nwLabels.ITEM_DESCRIPTION["document"]))
        self.aAddEmpty.triggered.connect(
            lambda: self.projTree.newTreeItem(nwItemType.FILE, hLevel=0, isNote=False)
        )

        self.aAddChap = self.mAdd.addAction(trConst(nwLabels.ITEM_DESCRIPTION["doc_h2"]))
        self.aAddChap.triggered.connect(
            lambda: self.projTree.newTreeItem(nwItemType.FILE, hLevel=2, isNote=False)
        )

        self.aAddScene = self.mAdd.addAction(trConst(nwLabels.ITEM_DESCRIPTION["doc_h3"]))
        self.aAddScene.triggered.connect(
            lambda: self.projTree.newTreeItem(nwItemType.FILE, hLevel=3, isNote=False)
        )

        self.aAddNote = self.mAdd.addAction(trConst(nwLabels.ITEM_DESCRIPTION["note"]))
        self.aAddNote.triggered.connect(
            lambda: self.projTree.newTreeItem(nwItemType.FILE, hLevel=1, isNote=True)
        )

        self.aAddFolder = self.mAdd.addAction(trConst(nwLabels.ITEM_DESCRIPTION["folder"]))
        self.aAddFolder.triggered.connect(
            lambda: self.projTree.newTreeItem(nwItemType.FOLDER)
        )

        self.mAddRoot = self.mAdd.addMenu(trConst(nwLabels.ITEM_DESCRIPTION["root"]))
        self._buildRootMenu()

        self.tbAdd = QToolButton(self)
        self.tbAdd.setToolTip("%s [Ctrl+N]" % self.tr("Add Item"))
        self.tbAdd.setShortcut("Ctrl+N")
        self.tbAdd.setIconSize(QSize(iPx, iPx))
        self.tbAdd.setMenu(self.mAdd)
        self.tbAdd.setPopupMode(QToolButton.InstantPopup)

        # More Options Menu
        self.mMore = QMenu(self)

        self.aExpand = self.mMore.addAction(self.tr("Expand All"))
        self.aExpand.triggered.connect(lambda: self.projTree.setExpandedFromHandle(None, True))

        self.aCollapse = self.mMore.addAction(self.tr("Collapse All"))
        self.aCollapse.triggered.connect(lambda: self.projTree.setExpandedFromHandle(None, False))

        self.aMoreUndo = self.mMore.addAction(self.tr("Undo Move"))
        self.aMoreUndo.triggered.connect(lambda: self.projTree.undoLastMove())

        self.aEmptyTrash = self.mMore.addAction(self.tr("Empty Trash"))
        self.aEmptyTrash.triggered.connect(lambda: self.projTree.emptyTrash())

        self.tbMore = QToolButton(self)
        self.tbMore.setToolTip(self.tr("More Options"))
        self.tbMore.setIconSize(QSize(iPx, iPx))
        self.tbMore.setMenu(self.mMore)
        self.tbMore.setPopupMode(QToolButton.InstantPopup)

        # Assemble
        self.outerBox = QHBoxLayout()
        self.outerBox.addWidget(self.viewLabel)
        self.outerBox.addWidget(self.tbQuick)
        self.outerBox.addWidget(self.tbMoveU)
        self.outerBox.addWidget(self.tbMoveD)
        self.outerBox.addWidget(self.tbAdd)
        self.outerBox.addWidget(self.tbMore)
        self.outerBox.setContentsMargins(mPx, mPx, 0, mPx)
        self.outerBox.setSpacing(0)

        self.setLayout(self.outerBox)
        self.updateTheme()

        logger.debug("Ready: GuiProjectToolBar")

        return

    ##
    #  Methods
    ##

    def updateTheme(self) -> None:
        """Update theme elements."""
        qPalette = self.palette()
        qPalette.setBrush(QPalette.Window, qPalette.base())
        self.setPalette(qPalette)

        fadeCol = qPalette.text().color()
        buttonStyle = (
            "QToolButton {{padding: {0}px; border: none; background: transparent;}} "
            "QToolButton:hover {{border: none; background: rgba({1},{2},{3},0.2);}}"
        ).format(CONFIG.pxInt(2), fadeCol.red(), fadeCol.green(), fadeCol.blue())

        self.tbQuick.setStyleSheet(buttonStyle)
        self.tbMoveU.setStyleSheet(buttonStyle)
        self.tbMoveD.setStyleSheet(buttonStyle)
        self.tbAdd.setStyleSheet(buttonStyle)
        self.tbMore.setStyleSheet(buttonStyle)

        self.tbQuick.setIcon(SHARED.theme.getIcon("bookmark"))
        self.tbMoveU.setIcon(SHARED.theme.getIcon("up"))
        self.tbMoveD.setIcon(SHARED.theme.getIcon("down"))
        self.aAddEmpty.setIcon(SHARED.theme.getIcon("proj_document"))
        self.aAddChap.setIcon(SHARED.theme.getIcon("proj_chapter"))
        self.aAddScene.setIcon(SHARED.theme.getIcon("proj_scene"))
        self.aAddNote.setIcon(SHARED.theme.getIcon("proj_note"))
        self.aAddFolder.setIcon(SHARED.theme.getIcon("proj_folder"))
        self.tbAdd.setIcon(SHARED.theme.getIcon("add"))
        self.tbMore.setIcon(SHARED.theme.getIcon("menu"))

        self.buildQuickLinkMenu()
        self._buildRootMenu()

        return

    def clearContent(self) -> None:
        """Clear dynamic content on the tool bar."""
        self.mQuick.clear()
        return

    def buildQuickLinkMenu(self) -> None:
        """Build the quick link menu."""
        logger.debug("Rebuilding quick links menu")
        self.mQuick.clear()
        for n, (tHandle, nwItem) in enumerate(SHARED.project.tree.iterRoots(None)):
            aRoot = self.mQuick.addAction(nwItem.itemName)
            aRoot.setData(tHandle)
            aRoot.setIcon(SHARED.theme.getIcon(nwLabels.CLASS_ICON[nwItem.itemClass]))
            aRoot.triggered.connect(
                lambda n, tHandle=tHandle: self.projView.setSelectedHandle(tHandle, doScroll=True)
            )
        return

    ##
    #  Internal Functions
    ##

    def _buildRootMenu(self) -> None:
        """Build the rood folder menu."""
        def addClass(itemClass):
            aNew = self.mAddRoot.addAction(trConst(nwLabels.CLASS_NAME[itemClass]))
            aNew.setIcon(SHARED.theme.getIcon(nwLabels.CLASS_ICON[itemClass]))
            aNew.triggered.connect(lambda: self.projTree.newTreeItem(nwItemType.ROOT, itemClass))
            self.mAddRoot.addAction(aNew)
            return

        self.mAddRoot.clear()
        addClass(nwItemClass.NOVEL)
        addClass(nwItemClass.ARCHIVE)
        self.mAddRoot.addSeparator()
        addClass(nwItemClass.PLOT)
        addClass(nwItemClass.CHARACTER)
        addClass(nwItemClass.WORLD)
        addClass(nwItemClass.TIMELINE)
        addClass(nwItemClass.OBJECT)
        addClass(nwItemClass.ENTITY)
        addClass(nwItemClass.CUSTOM)

        return

    ##
    #  Slots
    ##

    @pyqtSlot(str)
    def _treeSelectionChanged(self, tHandle: str) -> None:
        """Toggle the visibility of the new item entries for novel
        documents. They should only be visible if novel documents can
        actually be added.
        """
        nwItem = SHARED.project.tree[tHandle]
        allowDoc = isinstance(nwItem, NWItem) and nwItem.documentAllowed()
        self.aAddEmpty.setVisible(allowDoc)
        self.aAddChap.setVisible(allowDoc)
        self.aAddScene.setVisible(allowDoc)
        return

# END Class GuiProjectToolBar


class GuiProjectTree(QTreeWidget):

    C_DATA   = 0
    C_NAME   = 0
    C_COUNT  = 1
    C_ACTIVE = 2
    C_STATUS = 3

    D_HANDLE = Qt.ItemDataRole.UserRole
    D_WORDS  = Qt.ItemDataRole.UserRole + 1

    def __init__(self, projView: GuiProjectView) -> None:
        super().__init__(parent=projView)

        logger.debug("Create: GuiProjectTree")

        self.projView = projView
        self.mainGui  = projView.mainGui

        # Internal Variables
        self._treeMap = {}
        self._lastMove = {}
        self._timeChanged = 0.0

        # Build GUI
        # =========

        # Context Menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._openContextMenu)

        # Tree Settings
        iPx = SHARED.theme.baseIconSize
        cMg = CONFIG.pxInt(6)

        self.setIconSize(QSize(iPx, iPx))
        self.setFrameStyle(QFrame.NoFrame)
        self.setUniformRowHeights(True)
        self.setAllColumnsShowFocus(True)
        self.setExpandsOnDoubleClick(False)
        self.setAutoExpandDelay(1000)
        self.setHeaderHidden(True)
        self.setIndentation(iPx)
        self.setColumnCount(4)

        # Lock the column sizes
        treeHeader = self.header()
        treeHeader.setStretchLastSection(False)
        treeHeader.setMinimumSectionSize(iPx + cMg)
        treeHeader.setSectionResizeMode(self.C_NAME, QHeaderView.Stretch)
        treeHeader.setSectionResizeMode(self.C_COUNT, QHeaderView.ResizeToContents)
        treeHeader.setSectionResizeMode(self.C_ACTIVE, QHeaderView.Fixed)
        treeHeader.setSectionResizeMode(self.C_STATUS, QHeaderView.Fixed)
        treeHeader.resizeSection(self.C_ACTIVE, iPx + cMg)
        treeHeader.resizeSection(self.C_STATUS, iPx + cMg)

        # Allow Move by Drag & Drop
        self.setDragEnabled(True)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setDropIndicatorShown(True)

        # Disable built-in autoscroll as it isn't working in some Qt
        # releases (see #1561) and instead use our own implementation
        self.setAutoScroll(False)

        # But don't allow drop on root level
        # Due to a bug, this stops working somewhere between Qt 5.15.3
        # and 5.15.8, so this is also blocked in dropEvent (see #1569)
        trRoot = self.invisibleRootItem()
        trRoot.setFlags(trRoot.flags() ^ Qt.ItemIsDropEnabled)

        # Cached values
        self._lblActive = self.tr("Active")
        self._lblInactive = self.tr("Inactive")

        # Set selection options
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)

        # Connect signals
        self.itemDoubleClicked.connect(self._treeDoubleClick)
        self.itemSelectionChanged.connect(self._treeSelectionChange)

        # Autoscroll
        self._scrollMargin = SHARED.theme.baseIconSize
        self._scrollDirection = 0
        self._scrollTimer = QTimer()
        self._scrollTimer.timeout.connect(self._doAutoScroll)
        self._scrollTimer.setInterval(250)

        # Set custom settings
        self.initSettings()

        logger.debug("Ready: GuiProjectTree")

        return

    def initSettings(self) -> None:
        """Set or update tree widget settings."""
        # Scroll bars
        if CONFIG.hideVScroll:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        else:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        if CONFIG.hideHScroll:
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        else:
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        return

    ##
    #  Class Methods
    ##

    def clearTree(self) -> None:
        """Clear the GUI content and the related map."""
        self.clear()
        self._treeMap = {}
        self._lastMove = {}
        self._timeChanged = 0.0
        return

    def newTreeItem(self, itemType: nwItemType, itemClass: nwItemClass | None = None,
                    hLevel: int = 1, isNote: bool = False) -> bool:
        """Add new item to the tree, with a given itemType (and
        itemClass if Root), and attach it to the selected handle. Also
        make sure the item is added in a place it can be added, and that
        other meta data is set correctly to ensure a valid project tree.
        """
        if not SHARED.hasProject:
            logger.error("No project open")
            return False

        nHandle = None
        tHandle = None

        if itemType == nwItemType.ROOT and isinstance(itemClass, nwItemClass):

            tHandle = SHARED.project.newRoot(itemClass)
            sHandle = self.getSelectedHandle()
            pItem = SHARED.project.tree[sHandle] if sHandle else None
            nHandle = pItem.itemRoot if pItem else None

        elif itemType in (nwItemType.FILE, nwItemType.FOLDER):

            sHandle = self.getSelectedHandle()
            pItem = SHARED.project.tree[sHandle] if sHandle else None
            if sHandle is None or pItem is None:
                SHARED.error(self.tr("Did not find anywhere to add the file or folder!"))
                return False

            # Collect some information about the selected item
            qItem = self._getTreeItem(sHandle)
            sLevel = nwHeaders.H_LEVEL.get(pItem.mainHeading, 0)
            sIsParent = False if qItem is None else qItem.childCount() > 0

            if SHARED.project.tree.isTrash(sHandle):
                SHARED.error(self.tr("Cannot add new files or folders to the Trash folder."))
                return False

            # Set default label and determine if new item is to be added
            # as child or sibling to the selected item
            if itemType == nwItemType.FILE:
                if isNote:
                    newLabel = self.tr("New Note")
                    asChild = sIsParent
                elif hLevel == 2:
                    newLabel = self.tr("New Chapter")
                    asChild = sIsParent and pItem.isDocumentLayout() and sLevel < 2
                elif hLevel == 3:
                    newLabel = self.tr("New Scene")
                    asChild = sIsParent and pItem.isDocumentLayout() and sLevel < 3
                else:
                    newLabel = self.tr("New Document")
                    asChild = sIsParent and pItem.isDocumentLayout()
            else:
                newLabel = self.tr("New Folder")
                asChild = False

            if not (asChild or pItem.isFolderType() or pItem.isRootType()):
                # Move to the parent item so that the new item is added
                # as a sibling instead
                nHandle = sHandle
                sHandle = pItem.itemParent
                if sHandle is None:
                    # Bug: We have a condition that is unhandled
                    logger.error("Internal error")
                    return False

            # Ask for label
            newLabel, dlgOk = GuiEditLabel.getLabel(self, text=newLabel)
            if not dlgOk:
                logger.info("New item creation cancelled by user")
                return False

            # Add the file or folder
            if itemType == nwItemType.FILE:
                tHandle = SHARED.project.newFile(newLabel, sHandle)
            else:
                tHandle = SHARED.project.newFolder(newLabel, sHandle)

        else:
            logger.error("Failed to add new item")
            return False

        # If there is no handle set, return here. This is a bug.
        if tHandle is None:  # pragma: no cover
            logger.error("Internal error")
            return True

        # Handle new file creation
        if itemType == nwItemType.FILE and hLevel > 0:
            SHARED.project.writeNewFile(tHandle, hLevel, not isNote)

        # Add the new item to the project tree
        self.revealNewTreeItem(tHandle, nHandle=nHandle, wordCount=True)
        self.mainGui.switchFocus(nwWidget.TREE)

        return True

    def revealNewTreeItem(self, tHandle: str | None, nHandle: str | None = None,
                          wordCount: bool = False) -> bool:
        """Reveal a newly added project item in the project tree."""
        nwItem = SHARED.project.tree[tHandle] if tHandle else None
        if tHandle is None or nwItem is None:
            return False

        trItem = self._addTreeItem(nwItem, nHandle)
        if trItem is None:
            return False

        if nwItem.isFileType() and wordCount:
            wC = SHARED.project.index.getCounts(tHandle)[1]
            self.propagateCount(tHandle, wC)
            self.projView.wordCountsChanged.emit()

        pHandle = nwItem.itemParent
        if pHandle is not None and pHandle in self._treeMap:
            self._treeMap[pHandle].setExpanded(True)

        self._alertTreeChange(tHandle, flush=True)
        self.setCurrentItem(trItem)

        return True

    def moveTreeItem(self, step: int) -> bool:
        """Move an item up or down in the tree."""
        tHandle = self.getSelectedHandle()
        tItem = self._getTreeItem(tHandle)
        if tItem is None:
            logger.debug("No item selected")
            return False

        pItem = tItem.parent()
        isExp = tItem.isExpanded()
        if pItem is None:
            tIndex = self.indexOfTopLevelItem(tItem)
            nChild = self.topLevelItemCount()

            nIndex = tIndex + step
            if nIndex < 0 or nIndex >= nChild:
                return False

            cItem = self.takeTopLevelItem(tIndex)
            self.insertTopLevelItem(nIndex, cItem)

        else:
            tIndex = pItem.indexOfChild(tItem)
            nChild = pItem.childCount()

            nIndex = tIndex + step
            if nIndex < 0 or nIndex >= nChild:
                return False

            cItem = pItem.takeChild(tIndex)
            pItem.insertChild(nIndex, cItem)
            self._recordLastMove(cItem, pItem, tIndex)

        self._alertTreeChange(tHandle, flush=True)
        self.setCurrentItem(tItem)
        tItem.setExpanded(isExp)

        return True

    def moveToNextItem(self, step: int) -> None:
        """Move to the next item of the same tree level."""
        tHandle = self.getSelectedHandle()
        tItem = self._getTreeItem(tHandle) if tHandle else None
        if tItem:
            pItem = tItem.parent() or self.invisibleRootItem()
            next = minmax(pItem.indexOfChild(tItem) + step, 0, pItem.childCount() - 1)
            self.setCurrentItem(pItem.child(next))
        return

    def moveToLevel(self, step: int) -> None:
        """Move to the next item in the parent/child chain."""
        tHandle = self.getSelectedHandle()
        tItem = self._getTreeItem(tHandle) if tHandle else None
        if tItem:
            if step < 0 and tItem.parent():
                self.setCurrentItem(tItem.parent())
            elif step > 0 and tItem.childCount() > 0:
                self.setCurrentItem(tItem.child(0))
        return

    def renameTreeItem(self, tHandle: str) -> bool:
        """Open a dialog to edit the label of an item."""
        tItem = SHARED.project.tree[tHandle]
        if tItem is None:
            return False

        newLabel, dlgOk = GuiEditLabel.getLabel(self, text=tItem.itemName)
        if dlgOk:
            tItem.setName(newLabel)
            self.setTreeItemValues(tHandle)
            self._alertTreeChange(tHandle, flush=False)

        return True

    def saveTreeOrder(self) -> None:
        """Build a list of the items in the project tree and send them
        to the project class. This syncs up the two versions of the
        project structure, and must be called before any code that
        depends on this order to be up to date.
        """
        theList = []
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            if isinstance(item, QTreeWidgetItem):
                theList = self._scanChildren(theList, item, i)
        logger.debug("Saving project tree item order")
        SHARED.project.setTreeOrder(theList)
        return

    def getTreeFromHandle(self, tHandle: str) -> list[str]:
        """Recursively return all the child items starting from a given
        item handle.
        """
        theList = []
        theItem = self._getTreeItem(tHandle)
        if theItem is not None:
            theList = self._scanChildren(theList, theItem, 0)
        return theList

    def requestDeleteItem(self, tHandle: str | None = None) -> bool:
        """Request an item deleted from the project tree. This function
        can be called on any item, and will check whether to attempt a
        permanent deletion or moving the item to Trash.
        """
        if not SHARED.hasProject:
            logger.error("No project open")
            return False

        if not self.hasFocus():
            logger.info("Delete action blocked due to no widget focus")
            return False

        if tHandle is None:
            tHandle = self.getSelectedHandle()

        if tHandle is None:
            logger.error("There is no item to delete")
            return False

        trashHandle = SHARED.project.tree.trashRoot
        if tHandle == trashHandle:
            logger.error("Cannot delete the Trash folder")
            return False

        nwItem = SHARED.project.tree[tHandle]
        if nwItem is None:
            return False

        if SHARED.project.tree.isTrash(tHandle) or nwItem.isRootType():
            status = self.permDeleteItem(tHandle)
        else:
            status = self.moveItemToTrash(tHandle)

        return status

    def emptyTrash(self) -> bool:
        """Permanently delete all documents in the Trash folder. This
        function only asks for confirmation once, and calls the regular
        deleteItem function for each document in the Trash folder.
        """
        if not SHARED.hasProject:
            logger.error("No project open")
            return False

        trashHandle = SHARED.project.tree.trashRoot

        logger.debug("Emptying Trash folder")
        if trashHandle is None:
            SHARED.info(self.tr("There is currently no Trash folder in this project."))
            return False

        theTrash = self.getTreeFromHandle(trashHandle)
        if trashHandle in theTrash:
            theTrash.remove(trashHandle)

        nTrash = len(theTrash)
        if nTrash == 0:
            SHARED.info(self.tr("The Trash folder is already empty."))
            return False

        msgYes = SHARED.question(
            self.tr("Permanently delete {0} file(s) from Trash?").format(nTrash)
        )
        if not msgYes:
            logger.info("Action cancelled by user")
            return False

        logger.debug("Deleting %d file(s) from Trash", nTrash)
        for tHandle in reversed(self.getTreeFromHandle(trashHandle)):
            if tHandle == trashHandle:
                continue
            self.permDeleteItem(tHandle, askFirst=False, flush=False)

        if nTrash > 0:
            self._alertTreeChange(trashHandle, flush=True)

        return True

    def moveItemToTrash(self, tHandle: str, askFirst: bool = True, flush: bool = True) -> bool:
        """Move an item to Trash. Root folders cannot be moved to Trash,
        so such a request is cancelled.
        """
        trItemS = self._getTreeItem(tHandle)
        nwItemS = SHARED.project.tree[tHandle]

        if trItemS is None or nwItemS is None:
            logger.error("Could not find tree item for deletion")
            return False

        if SHARED.project.tree.isTrash(tHandle):
            logger.error("Item is already in the Trash folder")
            return False

        if nwItemS.isRootType():
            logger.error("Root folders cannot be moved to Trash")
            return False

        logger.debug("User requested file or folder '%s' move to Trash", tHandle)

        trItemP = trItemS.parent()
        trItemT = self._addTrashRoot()
        if trItemP is None or trItemT is None:
            logger.error("Could not delete item")
            return False

        if askFirst:
            msgYes = SHARED.question(
                self.tr("Move '{0}' to Trash?").format(nwItemS.itemName)
            )
            if not msgYes:
                logger.info("Action cancelled by user")
                return False

        wCount = self._getItemWordCount(tHandle)
        self.propagateCount(tHandle, 0)

        tIndex = trItemP.indexOfChild(trItemS)
        trItemC = trItemP.takeChild(tIndex)
        trItemT.addChild(trItemC)

        self._postItemMove(tHandle, wCount)
        self._recordLastMove(trItemS, trItemP, tIndex)
        self._alertTreeChange(tHandle, flush=flush)

        logger.debug("Moved item '%s' to Trash", tHandle)

        return True

    def permDeleteItem(self, tHandle: str, askFirst: bool = True, flush: bool = True) -> bool:
        """Permanently delete a tree item from the project and the map.
        Root items are handled a little different than other items.
        """
        trItemS = self._getTreeItem(tHandle)
        nwItemS = SHARED.project.tree[tHandle]
        if trItemS is None or nwItemS is None:
            logger.error("Could not find tree item for deletion")
            return False

        if nwItemS.isRootType():
            # Only an empty ROOT folder can be deleted
            if trItemS.childCount() > 0:
                SHARED.error(self.tr("Root folders can only be deleted when they are empty."))
                return False

            logger.debug("Permanently deleting root folder '%s'", tHandle)

            tIndex = self.indexOfTopLevelItem(trItemS)
            self.takeTopLevelItem(tIndex)
            SHARED.project.removeItem(tHandle)
            self._treeMap.pop(tHandle, None)
            self._alertTreeChange(tHandle, flush=True)

            # These are not emitted by the alert function because the
            # item has already been deleted
            self.projView.rootFolderChanged.emit(tHandle)
            self.projView.treeItemChanged.emit(tHandle)

        else:
            if askFirst:
                msgYes = SHARED.question(
                    self.tr("Permanently delete '{0}'?").format(nwItemS.itemName)
                )
                if not msgYes:
                    logger.info("Action cancelled by user")
                    return False

            logger.debug("Permanently deleting item '%s'", tHandle)

            self.propagateCount(tHandle, 0)

            trItemP = trItemS.parent()
            tIndex = trItemP.indexOfChild(trItemS)
            trItemP.takeChild(tIndex)

            for dHandle in reversed(self.getTreeFromHandle(tHandle)):
                if self.mainGui.docEditor.docHandle == dHandle:
                    self.mainGui.closeDocument()
                SHARED.project.removeItem(dHandle)
                self._treeMap.pop(dHandle, None)

            self._alertTreeChange(tHandle, flush=flush)
            self.projView.wordCountsChanged.emit()

            # This is not emitted by the alert function because the item
            # has already been deleted
            self.projView.treeItemChanged.emit(tHandle)

        return True

    def setTreeItemValues(self, tHandle: str) -> None:
        """Set the name and flag values for a tree item from a handle in
        the project tree. Does not trigger a tree change as the data is
        already coming from the project tree.
        """
        trItem = self._getTreeItem(tHandle)
        nwItem = SHARED.project.tree[tHandle]
        if trItem is None or nwItem is None:
            return

        itemStatus, statusIcon = nwItem.getImportStatus(incIcon=True)
        hLevel = nwItem.mainHeading
        itemIcon = SHARED.theme.getItemIcon(
            nwItem.itemType, nwItem.itemClass, nwItem.itemLayout, hLevel
        )

        trItem.setIcon(self.C_NAME, itemIcon)
        trItem.setText(self.C_NAME, nwItem.itemName)
        trItem.setIcon(self.C_STATUS, statusIcon)
        trItem.setToolTip(self.C_STATUS, itemStatus)

        if nwItem.isFileType():
            iconName = "checked" if nwItem.isActive else "unchecked"
            toolTip = self._lblActive if nwItem.isActive else self._lblInactive
            trItem.setToolTip(self.C_ACTIVE, toolTip)
        else:
            iconName = "noncheckable"

        trItem.setIcon(self.C_ACTIVE, SHARED.theme.getIcon(iconName))

        if CONFIG.emphLabels and nwItem.isDocumentLayout():
            trFont = trItem.font(self.C_NAME)
            trFont.setBold(hLevel == "H1" or hLevel == "H2")
            trFont.setUnderline(hLevel == "H1")
            trItem.setFont(self.C_NAME, trFont)

        return

    def propagateCount(self, tHandle: str, newCount: int, countChildren: bool = False) -> None:
        """Recursive function setting the word count for a given item,
        and propagating that count upwards in the tree until reaching a
        root item. This function is more efficient than recalculating
        everything each time the word count is updated, but is also
        prone to diverging from the true values if the counts are not
        properly reported to the function.
        """
        tItem = self._getTreeItem(tHandle)
        if tItem is None:
            return

        if countChildren:
            for i in range(tItem.childCount()):
                newCount += int(tItem.child(i).data(self.C_DATA, self.D_WORDS))

        tItem.setText(self.C_COUNT, f"{newCount:n}")
        tItem.setData(self.C_DATA, self.D_WORDS, int(newCount))

        pItem = tItem.parent()
        if pItem is None:
            return

        pCount = 0
        pHandle = None
        for i in range(pItem.childCount()):
            pCount += int(pItem.child(i).data(self.C_DATA, self.D_WORDS))
            pHandle = pItem.data(self.C_DATA, self.D_HANDLE)

        if pHandle:
            if SHARED.project.tree.checkType(pHandle, nwItemType.FILE):
                # A file has an internal word count we need to account
                # for, but a folder always has 0 words on its own.
                pCount += SHARED.project.index.getCounts(pHandle)[1]

            self.propagateCount(pHandle, pCount, countChildren=False)

        return

    def buildTree(self) -> None:
        """Build the entire project tree from scratch. This depends on
        the save project item iterator in the project class which will
        always make sure items with a parent have had their parent item
        sent first.
        """
        logger.debug("Building the project tree ...")
        self.clearTree()
        count = 0
        for nwItem in SHARED.project.iterProjectItems():
            count += 1
            self._addTreeItem(nwItem)
        if count > 0:
            logger.info("%d item(s) added to the project tree", count)
        return

    def undoLastMove(self) -> bool:
        """Attempt to undo the last action."""
        srcItem = self._lastMove.get("item", None)
        dstItem = self._lastMove.get("parent", None)
        dstIndex = self._lastMove.get("index", None)

        srcOK = isinstance(srcItem, QTreeWidgetItem)
        dstOk = isinstance(dstItem, QTreeWidgetItem)
        if not srcOK or not dstOk or dstIndex is None:
            logger.debug("No tree move to undo")
            return False

        if srcItem not in self._treeMap.values():
            logger.warning("Source item no longer exists")
            return False

        if dstItem not in self._treeMap.values():
            logger.warning("Previous parent item no longer exists")
            return False

        dstIndex = min(max(0, dstIndex), dstItem.childCount())
        sHandle = srcItem.data(self.C_DATA, self.D_HANDLE)
        dHandle = dstItem.data(self.C_DATA, self.D_HANDLE)
        logger.debug("Moving item '%s' back to '%s', index %d", sHandle, dHandle, dstIndex)

        wCount = self._getItemWordCount(sHandle)
        self.propagateCount(sHandle, 0)
        parItem = srcItem.parent()
        srcIndex = parItem.indexOfChild(srcItem)
        movItem = parItem.takeChild(srcIndex)
        dstItem.insertChild(dstIndex, movItem)

        self._postItemMove(sHandle, wCount)
        self._alertTreeChange(sHandle, flush=True)

        self.setCurrentItem(movItem)
        self._lastMove = {}

        return True

    def getSelectedHandle(self) -> str | None:
        """Get the currently selected handle. If multiple items are
        selected, return the first.
        """
        selItem = self.selectedItems()
        if selItem:
            return selItem[0].data(self.C_DATA, self.D_HANDLE)
        return None

    def setSelectedHandle(self, tHandle: str | None, doScroll: bool = False) -> bool:
        """Set a specific handle as the selected item."""
        tItem = self._getTreeItem(tHandle)
        if tItem is None:
            return False

        if tHandle in self._treeMap:
            self.setCurrentItem(self._treeMap[tHandle])

        selIndex = self.selectedIndexes()
        if selIndex and doScroll:
            self.scrollTo(selIndex[0], QAbstractItemView.PositionAtCenter)

        return True

    def setExpandedFromHandle(self, tHandle: str | None, isExpanded: bool) -> None:
        """Iterate through items below tHandle and change expanded
        status for all child items. If tHandle is None, it affects the
        entire tree.
        """
        trItem = self._getTreeItem(tHandle) or self.invisibleRootItem()
        self._recursiveSetExpanded(trItem, isExpanded)
        return

    def openContextOnSelected(self) -> bool:
        """Open the context menu on the current selected item."""
        selItem = self.selectedItems()
        if selItem:
            pos = self.visualItemRect(selItem[0]).center()
            return self._openContextMenu(pos)
        return False

    def changedSince(self, checkTime: float) -> bool:
        """Check if the tree has changed since a given time."""
        return self._timeChanged > checkTime

    ##
    #  Private Slots
    ##

    @pyqtSlot()
    def _treeSelectionChange(self) -> None:
        """The user changed which item is selected."""
        tHandle = self.getSelectedHandle()
        if tHandle is not None:
            self.projView.selectedItemChanged.emit(tHandle)
        return

    @pyqtSlot("QTreeWidgetItem*", int)
    def _treeDoubleClick(self, trItem: QTreeWidgetItem, colNo: int) -> None:
        """Capture a double-click event and either request the document
        for editing if it is a file, or expand/close the node it is not.
        """
        tHandle = self.getSelectedHandle()
        if tHandle is None:
            return

        tItem = SHARED.project.tree[tHandle]
        if tItem is None:
            return

        if tItem.isFileType():
            self.projView.openDocumentRequest.emit(tHandle, nwDocMode.EDIT, "", True)
        else:
            trItem.setExpanded(not trItem.isExpanded())

        return

    @pyqtSlot("QPoint")
    def _openContextMenu(self, clickPos: QPoint) -> bool:
        """The user right clicked an element in the project tree, so we
        open a context menu in-place.
        """
        tItem = None
        tHandle = None
        hasChild = False
        selItem = self.itemAt(clickPos)
        if isinstance(selItem, QTreeWidgetItem):
            tHandle = selItem.data(self.C_DATA, self.D_HANDLE)
            tItem = SHARED.project.tree[tHandle]
            hasChild = selItem.childCount() > 0

        if tItem is None or tHandle is None:
            logger.debug("No item found")
            return False

        ctxMenu = QMenu(self)

        # Trash Folder
        # ============

        trashHandle = SHARED.project.tree.trashRoot
        if tItem.itemHandle == trashHandle and trashHandle is not None:
            # The trash folder only has one option
            aEmptyTrash = ctxMenu.addAction(self.tr("Empty Trash"))
            aEmptyTrash.triggered.connect(lambda: self.emptyTrash())
            ctxMenu.exec_(self.viewport().mapToGlobal(clickPos))
            return True

        # Document Actions
        # ================

        isRoot = tItem.isRootType()
        isFolder = tItem.isFolderType()
        isFile = tItem.isFileType()

        if isFile:
            aOpenDoc = ctxMenu.addAction(self.tr("Open Document"))
            aOpenDoc.triggered.connect(
                lambda: self.projView.openDocumentRequest.emit(tHandle, nwDocMode.EDIT, "", True)
            )
            aViewDoc = ctxMenu.addAction(self.tr("View Document"))
            aViewDoc.triggered.connect(
                lambda: self.projView.openDocumentRequest.emit(tHandle, nwDocMode.VIEW, "", False)
            )
            ctxMenu.addSeparator()

        # Edit Item Settings
        # ==================

        aLabel = ctxMenu.addAction(self.tr("Rename"))
        aLabel.triggered.connect(lambda: self.renameTreeItem(tHandle))

        if isFile:
            aActive = ctxMenu.addAction(self.tr("Toggle Active"))
            aActive.triggered.connect(lambda: self._toggleItemActive(tHandle))

        checkMark = f" ({nwUnicode.U_CHECK})"
        if tItem.isNovelLike():
            mStatus = ctxMenu.addMenu(self.tr("Set Status to ..."))
            for n, (key, entry) in enumerate(SHARED.project.data.itemStatus.items()):
                entryName = entry["name"] + (checkMark if tItem.itemStatus == key else "")
                aStatus = mStatus.addAction(entry["icon"], entryName)
                aStatus.triggered.connect(
                    lambda n, key=key: self._changeItemStatus(tHandle, key)
                )
            mStatus.addSeparator()
            aManage1 = mStatus.addAction("Manage Labels ...")
            aManage1.triggered.connect(
                lambda: self.projView.projectSettingsRequest.emit(GuiProjectSettings.TAB_STATUS)
            )
        else:
            mImport = ctxMenu.addMenu(self.tr("Set Importance to ..."))
            for n, (key, entry) in enumerate(SHARED.project.data.itemImport.items()):
                entryName = entry["name"] + (checkMark if tItem.itemImport == key else "")
                aImport = mImport.addAction(entry["icon"], entryName)
                aImport.triggered.connect(
                    lambda n, key=key: self._changeItemImport(tHandle, key)
                )
            mImport.addSeparator()
            aManage2 = mImport.addAction("Manage Labels ...")
            aManage2.triggered.connect(
                lambda: self.projView.projectSettingsRequest.emit(GuiProjectSettings.TAB_IMPORT)
            )

        # Transform Item
        # ==============

        if not isRoot:
            mTrans = ctxMenu.addMenu(self.tr("Transform"))

            trDoc = trConst(nwLabels.LAYOUT_NAME[nwItemLayout.DOCUMENT])
            trNote = trConst(nwLabels.LAYOUT_NAME[nwItemLayout.NOTE])

            isDocFile = isFile and tItem.isDocumentLayout()
            isNoteFile = isFile and tItem.isNoteLayout()

            if isNoteFile and tItem.documentAllowed():
                aConvert1 = mTrans.addAction(self.tr("Convert to {0}").format(trDoc))
                aConvert1.triggered.connect(
                    lambda: self._changeItemLayout(tHandle, nwItemLayout.DOCUMENT)
                )

            if isDocFile:
                aConvert2 = mTrans.addAction(self.tr("Convert to {0}").format(trNote))
                aConvert2.triggered.connect(
                    lambda: self._changeItemLayout(tHandle, nwItemLayout.NOTE)
                )

            if isFolder and tItem.documentAllowed():
                aConvert3 = mTrans.addAction(self.tr("Convert to {0}").format(trDoc))
                aConvert3.triggered.connect(
                    lambda: self._covertFolderToFile(tHandle, nwItemLayout.DOCUMENT)
                )

            if isFolder:
                aConvert4 = mTrans.addAction(self.tr("Convert to {0}").format(trNote))
                aConvert4.triggered.connect(
                    lambda: self._covertFolderToFile(tHandle, nwItemLayout.NOTE)
                )

            if hasChild and isFile:
                aMerge1 = mTrans.addAction(self.tr("Merge Child Items into Self"))
                aMerge1.triggered.connect(lambda: self._mergeDocuments(tHandle, False))
                aMerge2 = mTrans.addAction(self.tr("Merge Child Items into New"))
                aMerge2.triggered.connect(lambda: self._mergeDocuments(tHandle, True))

            if hasChild and isFolder:
                aMerge3 = mTrans.addAction(self.tr("Merge Documents in Folder"))
                aMerge3.triggered.connect(lambda: self._mergeDocuments(tHandle, True))

            if isFile:
                aSplit1 = mTrans.addAction(self.tr("Split Document by Headers"))
                aSplit1.triggered.connect(lambda: self._splitDocument(tHandle))

        # Expand/Collapse/Delete/Duplicate
        # ================================

        ctxMenu.addSeparator()

        if hasChild:
            aExpand = ctxMenu.addAction(self.tr("Expand All"))
            aExpand.triggered.connect(lambda: self.setExpandedFromHandle(tHandle, True))
            aCollapse = ctxMenu.addAction(self.tr("Collapse All"))
            aCollapse.triggered.connect(lambda: self.setExpandedFromHandle(tHandle, False))
            aDuplicate = ctxMenu.addAction(self.tr("Duplicate from Here"))
            aDuplicate.triggered.connect(lambda: self._duplicateFromHandle(tHandle))
        elif isFile:
            aDuplicate = ctxMenu.addAction(self.tr("Duplicate Document"))
            aDuplicate.triggered.connect(lambda: self._duplicateFromHandle(tHandle))

        if tItem.itemClass == nwItemClass.TRASH or isRoot or (isFolder and not hasChild):
            aDelete = ctxMenu.addAction(self.tr("Delete Permanently"))
            aDelete.triggered.connect(lambda: self.permDeleteItem(tHandle))
        else:
            aMoveTrash = ctxMenu.addAction(self.tr("Move to Trash"))
            aMoveTrash.triggered.connect(lambda: self.moveItemToTrash(tHandle))

        # Show Context Menu
        ctxMenu.exec_(self.viewport().mapToGlobal(clickPos))

        return True

    @pyqtSlot()
    def _doAutoScroll(self) -> None:
        """Scroll one item up or down based on direction value."""
        if self._scrollDirection == -1:
            self.scrollToItem(self.itemAbove(self.itemAt(1, 1)))
        elif self._scrollDirection == 1:
            self.scrollToItem(self.itemBelow(self.itemAt(1, self.height() - 1)))
        self._scrollDirection = 0
        self._scrollTimer.stop()
        return

    ##
    #  Events
    ##

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Overload mousePressEvent to clear selection if clicking the
        mouse in a blank area of the tree view, and to load a document
        for viewing if the user middle-clicked.
        """
        super().mousePressEvent(event)

        if event.button() == Qt.LeftButton:
            selItem = self.indexAt(event.pos())
            if not selItem.isValid():
                self.clearSelection()

        elif event.button() == Qt.MiddleButton:
            selItem = self.itemAt(event.pos())
            if not isinstance(selItem, QTreeWidgetItem):
                return

            tHandle = selItem.data(self.C_DATA, self.D_HANDLE)
            tItem = SHARED.project.tree[tHandle]
            if tItem is None:
                return

            if tItem.isFileType():
                self.projView.openDocumentRequest.emit(tHandle, nwDocMode.VIEW, "", False)

        return

    def dragMoveEvent(self, event: QDragMoveEvent) -> None:
        """Capture the drag move event to enable edge autoscroll."""
        y = event.pos().y()
        if y < self._scrollMargin:
            if not self._scrollTimer.isActive():
                self._scrollDirection = -1
                self._scrollTimer.start()
        elif y > self.height() - self._scrollMargin:
            if not self._scrollTimer.isActive():
                self._scrollDirection = 1
                self._scrollTimer.start()
        super().dragMoveEvent(event)
        return

    def dropEvent(self, event: QDropEvent) -> None:
        """Overload the drop item event to ensure relevant data has been
        updated.
        """
        sHandle = self.getSelectedHandle()
        sItem = self._getTreeItem(sHandle) if sHandle else None
        if sHandle is None or sItem is None or sItem.parent() is None:
            logger.error("Invalid drag and drop event")
            event.ignore()
            return

        if not self.indexAt(event.pos()).isValid():
            # Needed due to a bug somewhere around Qt 5.15.8 that
            # ignores the invisible root item flags
            logger.error("Invalid drop location")
            event.ignore()
            return

        logger.debug("Drag'n'drop of item '%s' accepted", sHandle)

        isExpanded = sItem.isExpanded()
        pItem = sItem.parent()
        pIndex = pItem.indexOfChild(sItem) if pItem else 0

        wCount = self._getItemWordCount(sHandle)
        self.propagateCount(sHandle, 0)

        super().dropEvent(event)
        self._postItemMove(sHandle, wCount)
        self._recordLastMove(sItem, pItem, pIndex)
        self._alertTreeChange(sHandle, flush=True)

        sItem.setExpanded(isExpanded)

        return

    ##
    #  Internal Functions
    ##

    def _postItemMove(self, tHandle: str, wCount: int) -> bool:
        """Run various maintenance tasks for a moved item."""
        trItemS = self._getTreeItem(tHandle)
        nwItemS = SHARED.project.tree[tHandle]
        trItemP = trItemS.parent() if trItemS else None
        if trItemP is None or nwItemS is None:
            logger.error("Failed to find new parent item of '%s'", tHandle)
            return False

        # Update item parent handle in the project, make sure meta data
        # is updated accordingly, and update word count
        pHandle = trItemP.data(self.C_DATA, self.D_HANDLE)
        nwItemS.setParent(pHandle)
        trItemP.setExpanded(True)
        logger.debug("The parent of item '%s' has been changed to '%s'", tHandle, pHandle)

        mHandles = self.getTreeFromHandle(tHandle)
        logger.debug("A total of %d item(s) were moved", len(mHandles))
        for mHandle in mHandles:
            logger.debug("Updating item '%s'", mHandle)
            SHARED.project.tree.updateItemData(mHandle)

            # Update the index
            if nwItemS.isInactiveClass():
                SHARED.project.index.deleteHandle(mHandle)
            else:
                SHARED.project.index.reIndexHandle(mHandle)

            self.setTreeItemValues(mHandle)

        # Trigger dependent updates
        self.propagateCount(tHandle, wCount)

        return True

    def _getItemWordCount(self, tHandle: str) -> int:
        """Return the word count of a given item handle."""
        tItem = self._getTreeItem(tHandle)
        return int(tItem.data(self.C_DATA, self.D_WORDS)) if tItem else 0

    def _getTreeItem(self, tHandle: str | None) -> QTreeWidgetItem | None:
        """Return the QTreeWidgetItem of a given item handle."""
        return self._treeMap.get(tHandle, None) if tHandle else None

    def _toggleItemActive(self, tHandle: str) -> None:
        """Toggle the active status of an item."""
        tItem = SHARED.project.tree[tHandle]
        if tItem is not None:
            tItem.setActive(not tItem.isActive)
            self.setTreeItemValues(tItem.itemHandle)
            self._alertTreeChange(tHandle, flush=False)
        return

    def _recursiveSetExpanded(self, trItem: QTreeWidgetItem, isExpanded: bool) -> None:
        """Recursive function to set expanded status starting from (and
        not including) a given item.
        """
        if isinstance(trItem, QTreeWidgetItem):
            chCount = trItem.childCount()
            for i in range(chCount):
                chItem = trItem.child(i)
                chItem.setExpanded(isExpanded)
                self._recursiveSetExpanded(chItem, isExpanded)
        return

    def _changeItemStatus(self, tHandle: str, tStatus: str) -> None:
        """Set a new status value of an item."""
        tItem = SHARED.project.tree[tHandle]
        if tItem is not None:
            tItem.setStatus(tStatus)
            self.setTreeItemValues(tItem.itemHandle)
            self._alertTreeChange(tHandle, flush=False)
        return

    def _changeItemImport(self, tHandle: str, tImport: str) -> None:
        """Set a new importance value of an item."""
        tItem = SHARED.project.tree[tHandle]
        if tItem is not None:
            tItem.setImport(tImport)
            self.setTreeItemValues(tItem.itemHandle)
            self._alertTreeChange(tHandle, flush=False)
        return

    def _changeItemLayout(self, tHandle: str, itemLayout: nwItemLayout) -> None:
        """Set a new item layout value of an item."""
        tItem = SHARED.project.tree[tHandle]
        if tItem is not None:
            if itemLayout == nwItemLayout.DOCUMENT and tItem.documentAllowed():
                tItem.setLayout(nwItemLayout.DOCUMENT)
                self.setTreeItemValues(tHandle)
                self._alertTreeChange(tHandle, flush=False)
            elif itemLayout == nwItemLayout.NOTE:
                tItem.setLayout(nwItemLayout.NOTE)
                self.setTreeItemValues(tHandle)
                self._alertTreeChange(tHandle, flush=False)
        return

    def _covertFolderToFile(self, tHandle: str, itemLayout: nwItemLayout) -> None:
        """Convert a folder to a note or document."""
        tItem = SHARED.project.tree[tHandle]
        if tItem is not None and tItem.isFolderType():
            msgYes = SHARED.question(self.tr(
                "Do you want to convert the folder to a {0}? "
                "This action cannot be reversed."
            ).format(trConst(nwLabels.LAYOUT_NAME[itemLayout])))
            if msgYes and itemLayout == nwItemLayout.DOCUMENT and tItem.documentAllowed():
                tItem.setType(nwItemType.FILE)
                tItem.setLayout(nwItemLayout.DOCUMENT)
                self.setTreeItemValues(tHandle)
                self._alertTreeChange(tHandle, flush=False)
            elif msgYes and itemLayout == nwItemLayout.NOTE:
                tItem.setType(nwItemType.FILE)
                tItem.setLayout(nwItemLayout.NOTE)
                self.setTreeItemValues(tHandle)
                self._alertTreeChange(tHandle, flush=False)
            else:
                logger.info("Folder conversion cancelled")
        return

    def _mergeDocuments(self, tHandle: str, newFile: bool) -> bool:
        """Merge an item's child documents into a single document."""
        logger.info("Request to merge items under handle '%s'", tHandle)
        itemList = self.getTreeFromHandle(tHandle)

        tItem = SHARED.project.tree[tHandle]
        if tItem is None:
            return False

        if tItem.isRootType():
            logger.error("Cannot merge root item")
            return False

        if not newFile:
            itemList.remove(tHandle)

        dlgMerge = GuiDocMerge(self.mainGui, tHandle, itemList)
        dlgMerge.exec_()

        if dlgMerge.result() == QDialog.Accepted:

            mrgData = dlgMerge.getData()
            mrgList = mrgData.get("finalItems", [])
            if not mrgList:
                SHARED.info(self.tr("No documents selected for merging."))
                return False

            # Save the open document first, in case it's part of merge
            self.mainGui.saveDocument()

            # Create merge object, and append docs
            docMerger = DocMerger(SHARED.project)
            mLabel = self.tr("Merged")

            if newFile:
                docLabel = f"[{mLabel}] {tItem.itemName}"
                mHandle = docMerger.newTargetDoc(tHandle, docLabel)
            elif tItem.isFileType():
                docMerger.setTargetDoc(tHandle)
                mHandle = tHandle
            else:
                return False

            for sHandle in mrgList:
                docMerger.appendText(sHandle, True, mLabel)

            if not docMerger.writeTargetDoc():
                SHARED.error(
                    self.tr("Could not write document content."),
                    info=docMerger.getError()
                )
                return False

            SHARED.project.index.reIndexHandle(mHandle)
            if newFile:
                self.revealNewTreeItem(mHandle, nHandle=tHandle, wordCount=True)

            self.mainGui.openDocument(mHandle, doScroll=True)

            if mrgData.get("moveToTrash", False):
                for sHandle in reversed(mrgData.get("finalItems", [])):
                    trItem = self._getTreeItem(sHandle)
                    if isinstance(trItem, QTreeWidgetItem) and trItem.childCount() == 0:
                        self.moveItemToTrash(sHandle, askFirst=False, flush=False)

            self._alertTreeChange(mHandle, flush=True)
            self.projView.wordCountsChanged.emit()

        else:
            logger.info("Action cancelled by user")
            return False

        return True

    def _splitDocument(self, tHandle: str) -> bool:
        """Split a document into multiple documents."""
        logger.info("Request to split items with handle '%s'", tHandle)

        tItem = SHARED.project.tree[tHandle]
        if tItem is None:
            return False

        if not tItem.isFileType() or tItem.itemParent is None:
            logger.error("Only valid document items can be split")
            return False

        dlgSplit = GuiDocSplit(self.mainGui, tHandle)
        dlgSplit.exec_()

        if dlgSplit.result() == QDialog.Accepted:

            splitData, splitText = dlgSplit.getData()

            headerList = splitData.get("headerList", [])
            intoFolder = splitData.get("intoFolder", False)
            docHierarchy = splitData.get("docHierarchy", False)

            docSplit = DocSplitter(SHARED.project, tHandle)
            if intoFolder:
                fHandle = docSplit.newParentFolder(tItem.itemParent, tItem.itemName)
                self.revealNewTreeItem(fHandle, nHandle=tHandle)
                self._alertTreeChange(fHandle, flush=False)
            else:
                docSplit.setParentItem(tItem.itemParent)

            docSplit.splitDocument(headerList, splitText)
            for writeOk, dHandle, nHandle in docSplit.writeDocuments(docHierarchy):
                SHARED.project.index.reIndexHandle(dHandle)
                self.revealNewTreeItem(dHandle, nHandle=nHandle, wordCount=True)
                self._alertTreeChange(dHandle, flush=False)
                if not writeOk:
                    SHARED.error(
                        self.tr("Could not write document content."),
                        info=docSplit.getError()
                    )

            if splitData.get("moveToTrash", False):
                self.moveItemToTrash(tHandle, askFirst=False, flush=True)

            self.saveTreeOrder()

        else:
            logger.info("Action cancelled by user")
            return False

        return True

    def _duplicateFromHandle(self, tHandle: str) -> bool:
        """Duplicate the item hierarchy from a given item."""
        itemTree = self.getTreeFromHandle(tHandle)
        nItems = len(itemTree)
        if nItems == 0:
            return False
        elif nItems == 1:
            question = self.tr("Do you want to duplicate this document?")
        else:
            question = self.tr("Do you want to duplicate this item and all child items?")

        if not SHARED.question(question):
            return False

        docDup = DocDuplicator(SHARED.project)
        dupCount = 0
        for dHandle, nHandle in docDup.duplicate(itemTree):
            SHARED.project.index.reIndexHandle(dHandle)
            self.revealNewTreeItem(dHandle, nHandle=nHandle, wordCount=True)
            self._alertTreeChange(dHandle, flush=False)
            dupCount += 1

        if dupCount != nItems:
            SHARED.warn(self.tr("Could not duplicate all items."))

        self.saveTreeOrder()

        return True

    def _scanChildren(self, itemList: list, tItem: QTreeWidgetItem, tIndex: int) -> list[str]:
        """This is a recursive function returning all items in a tree
        starting at a given QTreeWidgetItem.
        """
        tHandle = tItem.data(self.C_DATA, self.D_HANDLE)
        cCount = tItem.childCount()

        # Update tree-related meta data
        nwItem = SHARED.project.tree[tHandle]
        if nwItem is not None:
            nwItem.setExpanded(tItem.isExpanded() and cCount > 0)
            nwItem.setOrder(tIndex)

        itemList.append(tHandle)
        for i in range(cCount):
            self._scanChildren(itemList, tItem.child(i), i)

        return itemList

    def _addTreeItem(self, nwItem: NWItem | None,
                     nHandle: str | None = None) -> QTreeWidgetItem | None:
        """Create a QTreeWidgetItem from an NWItem and add it to the
        project tree. Returns the widget if the item is valid, otherwise
        a None is returned.
        """
        if not nwItem:
            logger.error("Invalid item cannot be added to project tree")
            return None

        tHandle = nwItem.itemHandle
        pHandle = nwItem.itemParent
        newItem = QTreeWidgetItem()

        newItem.setText(self.C_NAME, "")
        newItem.setText(self.C_COUNT, "0")
        newItem.setText(self.C_ACTIVE, "")
        newItem.setText(self.C_STATUS, "")

        newItem.setTextAlignment(self.C_NAME, Qt.AlignLeft)
        newItem.setTextAlignment(self.C_COUNT, Qt.AlignRight)
        newItem.setTextAlignment(self.C_ACTIVE, Qt.AlignLeft)
        newItem.setTextAlignment(self.C_STATUS, Qt.AlignLeft)

        newItem.setData(self.C_DATA, self.D_HANDLE, tHandle)
        newItem.setData(self.C_DATA, self.D_WORDS, 0)

        if pHandle is None and nwItem.isRootType():
            pItem = self.invisibleRootItem()
        elif pHandle and pHandle in self._treeMap:
            pItem = self._treeMap[pHandle]
        else:
            SHARED.error(self.tr(
                "There is nowhere to add item with name '{0}'."
            ).format(nwItem.itemName))
            return None

        byIndex = -1
        if nHandle is not None and nHandle in self._treeMap:
            byIndex = pItem.indexOfChild(self._treeMap[nHandle])
        if byIndex >= 0:
            pItem.insertChild(byIndex + 1, newItem)
        else:
            pItem.addChild(newItem)

        self._treeMap[tHandle] = newItem
        self.propagateCount(tHandle, nwItem.wordCount, countChildren=True)
        self.setTreeItemValues(tHandle)
        newItem.setExpanded(nwItem.isExpanded)

        return newItem

    def _addTrashRoot(self) -> QTreeWidgetItem | None:
        """Adds the trash root folder if it doesn't already exist in the
        project tree.
        """
        trashHandle = SHARED.project.trashFolder()
        if trashHandle is None:
            return None

        trItem = self._getTreeItem(trashHandle)
        if trItem is None:
            trItem = self._addTreeItem(SHARED.project.tree[trashHandle])
            if trItem is not None:
                trItem.setExpanded(True)
                self._alertTreeChange(trashHandle, flush=True)

        return trItem

    def _alertTreeChange(self, tHandle: str | None, flush: bool = False) -> None:
        """Update information on tree change state, and emit necessary
        signals. A flush is only needed if an item is moved, created or
        deleted.
        """
        self._timeChanged = time()
        SHARED.project.setProjectChanged(True)
        if flush:
            self.saveTreeOrder()

        if tHandle is None or tHandle not in SHARED.project.tree:
            return

        tItem = SHARED.project.tree[tHandle]
        if tItem and tItem.isRootType():
            self.projView.rootFolderChanged.emit(tHandle)

        self.projView.treeItemChanged.emit(tHandle)

        return

    def _recordLastMove(self, srcItem: QTreeWidgetItem,
                        parItem: QTreeWidgetItem, parIndex: int) -> None:
        """Record the last action so that it can be undone."""
        prevItem = self._lastMove.get("item", None)
        if prevItem is None or srcItem != prevItem:
            self._lastMove = {
                "item": srcItem,
                "parent": parItem,
                "index": parIndex,
            }
        return

# END Class GuiProjectTree
