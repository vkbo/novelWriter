"""
novelWriter – GUI Project Tree
==============================
GUI classes for the main window project tree

File History:
Created: 2018-09-29 [0.0.1] GuiProjectTree
Created: 2022-06-06 [1.7b1] GuiProjectView
Created: 2022-06-06 [1.7b1] GuiProjectToolBar

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

from enum import Enum
from time import time

from PyQt5.QtGui import QPalette
from PyQt5.QtCore import Qt, QSize, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import (
    QAbstractItemView, QFrame, QHBoxLayout, QHeaderView, QLabel,
    QMenu, QShortcut, QSizePolicy, QToolButton, QTreeWidget, QTreeWidgetItem,
    QVBoxLayout, QWidget
)

from novelwriter.core import NWDoc
from novelwriter.enum import nwDocMode, nwItemType, nwItemClass, nwItemLayout, nwAlert
from novelwriter.constants import trConst, nwLabels
from novelwriter.dialogs.editlabel import GuiEditLabel

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
    openDocumentRequest = pyqtSignal(str, Enum, int, str)

    def __init__(self, mainGui):
        QWidget.__init__(self, mainGui)

        self.mainGui = mainGui

        # Build GUI
        self.projTree = GuiProjectTree(self)
        self.projBar = GuiProjectToolBar(self)

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

        self.keyUndoMv = QShortcut(self.projTree)
        self.keyUndoMv.setKey("Ctrl+Shift+Z")
        self.keyUndoMv.setContext(Qt.WidgetShortcut)
        self.keyUndoMv.activated.connect(lambda: self.projTree.undoLastMove())

        self.keyContext = QShortcut(self.projTree)
        self.keyContext.setKey("Ctrl+.")
        self.keyContext.setContext(Qt.WidgetShortcut)
        self.keyContext.activated.connect(lambda: self.projTree.openContextOnSelected())

        # Function Mappings
        self.revealNewTreeItem = self.projTree.revealNewTreeItem
        self.renameTreeItem = self.projTree.renameTreeItem
        self.getTreeFromHandle = self.projTree.getTreeFromHandle
        self.emptyTrash = self.projTree.emptyTrash
        self.deleteItem = self.projTree.deleteItem
        self.setTreeItemValues = self.projTree.setTreeItemValues
        self.propagateCount = self.projTree.propagateCount
        self.getSelectedHandle = self.projTree.getSelectedHandle
        self.setSelectedHandle = self.projTree.setSelectedHandle
        self.changedSince = self.projTree.changedSince

        return

    ##
    #  Methods
    ##

    def initSettings(self):
        self.projTree.initSettings()
        return

    def clearProject(self):
        self.projTree.clearTree()
        return

    def saveProjectTree(self):
        self.projTree.saveTreeOrder()
        return

    def populateTree(self):
        self.projTree.buildTree()
        return

    def setFocus(self):
        """Forward the set focus call to the tree widget.
        """
        self.projTree.setFocus()
        return

    def treeHasFocus(self):
        """Check if the project tree has focus.
        """
        return self.projTree.hasFocus()

    ##
    #  Public Slots
    ##

    @pyqtSlot(str, int, int, int)
    def updateCounts(self, tHandle, cCount, wCount, pCount):
        """Slot for updating the word count of a specific item.
        """
        self.projTree.propagateCount(tHandle, wCount, countChildren=True)
        self.wordCountsChanged.emit()
        return

# END Class GuiProjectView


class GuiProjectToolBar(QWidget):

    def __init__(self, projView):
        QTreeWidget.__init__(self, projView)

        logger.debug("Initialising GuiProjectToolBar ...")

        self.mainConf   = novelwriter.CONFIG
        self.projView   = projView
        self.projTree   = projView.projTree
        self.mainGui    = projView.mainGui
        self.theProject = projView.mainGui.theProject
        self.mainTheme  = projView.mainGui.mainTheme

        iPx = self.mainTheme.baseIconSize
        mPx = self.mainConf.pxInt(2)

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
        self.viewLabel = QLabel("<b>%s</b>" % self.tr("Project Content"))
        self.viewLabel.setContentsMargins(0, 0, 0, 0)
        self.viewLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Move Buttons
        self.tbMoveU = QToolButton(self)
        self.tbMoveU.setToolTip("%s [Ctrl+Up]" % self.tr("Move Up"))
        self.tbMoveU.setIcon(self.mainTheme.getIcon("up"))
        self.tbMoveU.setIconSize(QSize(iPx, iPx))
        self.tbMoveU.setStyleSheet(buttonStyle)
        self.tbMoveU.clicked.connect(lambda: self.projTree.moveTreeItem(-1))

        self.tbMoveD = QToolButton(self)
        self.tbMoveD.setToolTip("%s [Ctrl+Down]" % self.tr("Move Down"))
        self.tbMoveD.setIcon(self.mainTheme.getIcon("down"))
        self.tbMoveD.setIconSize(QSize(iPx, iPx))
        self.tbMoveD.setStyleSheet(buttonStyle)
        self.tbMoveD.clicked.connect(lambda: self.projTree.moveTreeItem(1))

        # Add Item Menu
        self.mAdd = QMenu()

        self.aAddEmpty = self.mAdd.addAction(trConst(nwLabels.ITEM_DESCRIPTION["document"]))
        self.aAddEmpty.setIcon(self.mainTheme.getIcon("proj_document"))
        self.aAddEmpty.triggered.connect(
            lambda: self.projTree.newTreeItem(nwItemType.FILE, hLevel=0, isNote=False)
        )

        self.aAddChap = self.mAdd.addAction(trConst(nwLabels.ITEM_DESCRIPTION["doc_h2"]))
        self.aAddChap.setIcon(self.mainTheme.getIcon("proj_chapter"))
        self.aAddChap.triggered.connect(
            lambda: self.projTree.newTreeItem(nwItemType.FILE, hLevel=2, isNote=False)
        )

        self.aAddScene = self.mAdd.addAction(trConst(nwLabels.ITEM_DESCRIPTION["doc_h3"]))
        self.aAddScene.setIcon(self.mainTheme.getIcon("proj_scene"))
        self.aAddScene.triggered.connect(
            lambda: self.projTree.newTreeItem(nwItemType.FILE, hLevel=3, isNote=False)
        )

        self.aAddNote = self.mAdd.addAction(trConst(nwLabels.ITEM_DESCRIPTION["note"]))
        self.aAddNote.setIcon(self.mainTheme.getIcon("proj_note"))
        self.aAddNote.triggered.connect(
            lambda: self.projTree.newTreeItem(nwItemType.FILE, hLevel=1, isNote=True)
        )

        self.aAddFolder = self.mAdd.addAction(trConst(nwLabels.ITEM_DESCRIPTION["folder"]))
        self.aAddFolder.setIcon(self.mainTheme.getIcon("proj_folder"))
        self.aAddFolder.triggered.connect(
            lambda: self.projTree.newTreeItem(nwItemType.FOLDER)
        )

        self.mAddRoot = self.mAdd.addMenu(trConst(nwLabels.ITEM_DESCRIPTION["root"]))
        self._addRootFolderEntry(nwItemClass.NOVEL)
        self._addRootFolderEntry(nwItemClass.ARCHIVE)
        self.mAddRoot.addSeparator()
        self._addRootFolderEntry(nwItemClass.PLOT)
        self._addRootFolderEntry(nwItemClass.CHARACTER)
        self._addRootFolderEntry(nwItemClass.WORLD)
        self._addRootFolderEntry(nwItemClass.TIMELINE)
        self._addRootFolderEntry(nwItemClass.OBJECT)
        self._addRootFolderEntry(nwItemClass.ENTITY)
        self._addRootFolderEntry(nwItemClass.CUSTOM)

        self.tbAdd = QToolButton(self)
        self.tbAdd.setToolTip("%s [Ctrl+N]" % self.tr("Add Item"))
        self.tbAdd.setShortcut("Ctrl+N")
        self.tbAdd.setIcon(self.mainTheme.getIcon("add"))
        self.tbAdd.setIconSize(QSize(iPx, iPx))
        self.tbAdd.setStyleSheet(buttonStyle)
        self.tbAdd.setMenu(self.mAdd)
        self.tbAdd.setPopupMode(QToolButton.InstantPopup)

        # More Options Menu
        self.mMore = QMenu()

        self.aMoreUndo = self.mMore.addAction(self.tr("Undo Move"))
        self.aMoreUndo.triggered.connect(lambda: self.projTree.undoLastMove())

        self.aEmptyTrash = self.mMore.addAction(self.tr("Empty Trash"))
        self.aEmptyTrash.triggered.connect(lambda: self.projTree.emptyTrash())

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
        self.outerBox.addWidget(self.tbMoveU)
        self.outerBox.addWidget(self.tbMoveD)
        self.outerBox.addWidget(self.tbAdd)
        self.outerBox.addWidget(self.tbMore)
        self.outerBox.setContentsMargins(mPx, mPx, 0, mPx)
        self.outerBox.setSpacing(0)

        self.setLayout(self.outerBox)

        logger.debug("GuiProjectToolBar initialisation complete")

        return

    ##
    #  Internal Functions
    ##

    def _addRootFolderEntry(self, itemClass):
        """Add a menu entry for a root folder of a given class.
        """
        aNew = self.mAddRoot.addAction(trConst(nwLabels.CLASS_NAME[itemClass]))
        aNew.setIcon(self.mainTheme.getIcon(nwLabels.CLASS_ICON[itemClass]))
        aNew.triggered.connect(lambda: self.projTree.newTreeItem(nwItemType.ROOT, itemClass))
        self.mAddRoot.addAction(aNew)

# END Class GuiProjectToolBar


class GuiProjectTree(QTreeWidget):

    C_NAME   = 0
    C_COUNT  = 1
    C_EXPORT = 2
    C_STATUS = 3

    def __init__(self, projView):
        QTreeWidget.__init__(self, projView)

        logger.debug("Initialising GuiProjectTree ...")

        self.mainConf   = novelwriter.CONFIG
        self.projView   = projView
        self.mainGui    = projView.mainGui
        self.mainTheme   = projView.mainGui.mainTheme
        self.theProject = projView.mainGui.theProject

        # Internal Variables
        self._treeMap = {}
        self._lastMove = {}
        self._timeChanged = 0

        # Build GUI
        # =========

        # Context Menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._openContextMenu)

        # Tree Settings
        iPx = self.mainTheme.baseIconSize
        cMg = self.mainConf.pxInt(6)

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
        treeHeader.setSectionResizeMode(self.C_EXPORT, QHeaderView.Fixed)
        treeHeader.setSectionResizeMode(self.C_STATUS, QHeaderView.Fixed)
        treeHeader.resizeSection(self.C_EXPORT, iPx + cMg)
        treeHeader.resizeSection(self.C_STATUS, iPx + cMg)

        # Allow Move by Drag & Drop
        self.setDragEnabled(True)
        self.setDragDropMode(QAbstractItemView.InternalMove)

        # But don't allow drop on root level
        trRoot = self.invisibleRootItem()
        trRoot.setFlags(trRoot.flags() ^ Qt.ItemIsDropEnabled)

        # Set Multiple Selection by CTRL
        # Disabled for now, until the merge files option has been added
        # self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)

        # Connect signals
        self.itemDoubleClicked.connect(self._treeDoubleClick)
        self.itemSelectionChanged.connect(self._treeSelectionChange)

        # Set custom settings
        self.initSettings()

        logger.debug("GuiProjectTree initialisation complete")

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
        """Clear the GUI content and the related map.
        """
        self.clear()
        self._treeMap = {}
        self._lastMove = {}
        self._timeChanged = 0
        return

    def newTreeItem(self, itemType, itemClass=None, hLevel=1, isNote=False):
        """Add new item to the tree, with a given itemType (and
        itemClass if Root), and attach it to the selected handle. Also
        make sure the item is added in a place it can be added, and that
        other meta data is set correctly to ensure a valid project tree.
        """
        if not self.mainGui.hasProject:
            logger.error("No project open")
            return False

        nHandle = None
        tHandle = None

        if itemType == nwItemType.ROOT and isinstance(itemClass, nwItemClass):

            tHandle = self.theProject.newRoot(itemClass)

        elif itemType in (nwItemType.FILE, nwItemType.FOLDER):

            sHandle = self.getSelectedHandle()
            if sHandle is None or sHandle not in self.theProject.tree:
                self.mainGui.makeAlert(self.tr(
                    "Did not find anywhere to add the file or folder!"
                ), nwAlert.ERROR)
                return False

            # If the selected item is a file, the new item will be a
            # sibling if the file has no children, otherwise a child
            pItem = self.theProject.tree[sHandle]
            qItem = self._getTreeItem(sHandle)
            if pItem.itemType == nwItemType.FILE and qItem.childCount() == 0:
                nHandle = sHandle
                sHandle = pItem.itemParent
                if sHandle is None:
                    logger.error("Internal error")  # Bug
                    return False

            if self.theProject.tree.isTrash(sHandle):
                self.mainGui.makeAlert(self.tr(
                    "Cannot add new files or folders to the Trash folder."
                ), nwAlert.ERROR)
                return False

            # Ask for label
            if itemType == nwItemType.FILE:
                if isNote:
                    newLabel = self.tr("New Note")
                elif hLevel == 2:
                    newLabel = self.tr("New Chapter")
                elif hLevel == 3:
                    newLabel = self.tr("New Scene")
                else:
                    newLabel = self.tr("New Document")
            else:
                newLabel = self.tr("New Folder")

            newLabel, dlgOk = GuiEditLabel.getLabel(self, text=newLabel)
            if not dlgOk:
                logger.info("New item creation cancelled by user")
                return False

            # Add the file or folder
            if itemType == nwItemType.FILE:
                tHandle = self.theProject.newFile(newLabel, sHandle)
            else:
                tHandle = self.theProject.newFolder(newLabel, sHandle)

        else:
            logger.error("Failed to add new item")
            return False

        # If there is no handle set, return here. This is a bug.
        if tHandle is None:  # pragma: no cover
            logger.error("Internal error")
            return True

        # Handle new file creation
        if itemType == nwItemType.FILE and hLevel > 0:
            if self.theProject.writeNewFile(tHandle, hLevel, not isNote):
                # If successful, update word count
                wC = self.theProject.index.getCounts(tHandle)[1]
                self.propagateCount(tHandle, wC)
                self.projView.wordCountsChanged.emit()

        # Add the new item to the project tree
        self.revealNewTreeItem(tHandle, nHandle)

        return True

    def revealNewTreeItem(self, tHandle, nHandle=None):
        """Reveal a newly added project item in the project tree.
        """
        nwItem = self.theProject.tree[tHandle]
        if nwItem is None:
            return False

        trItem = self._addTreeItem(nwItem, nHandle)
        if trItem is None:
            return False

        pHandle = nwItem.itemParent
        if pHandle is not None and pHandle in self._treeMap:
            self._treeMap[pHandle].setExpanded(True)

        self._alertTreeChange(tHandle=tHandle, flush=True)
        self.clearSelection()
        trItem.setSelected(True)

        return True

    def moveTreeItem(self, nStep):
        """Move an item up or down in the tree.
        """
        tHandle = self.getSelectedHandle()
        trItem = self._getTreeItem(tHandle)
        if trItem is None:
            logger.verbose("No item selected")
            return False

        pItem = trItem.parent()
        isExp = trItem.isExpanded()
        if pItem is None:
            tIndex = self.indexOfTopLevelItem(trItem)
            nChild = self.topLevelItemCount()

            nIndex = tIndex + nStep
            if nIndex < 0 or nIndex >= nChild:
                return False

            cItem = self.takeTopLevelItem(tIndex)
            self.insertTopLevelItem(nIndex, cItem)

        else:
            tIndex = pItem.indexOfChild(trItem)
            nChild = pItem.childCount()

            nIndex = tIndex + nStep
            if nIndex < 0 or nIndex >= nChild:
                return False

            cItem = pItem.takeChild(tIndex)
            pItem.insertChild(nIndex, cItem)
            self._recordLastMove(cItem, pItem, tIndex)

        self._alertTreeChange(tHandle=tHandle, flush=True)
        self.clearSelection()
        trItem.setSelected(True)
        trItem.setExpanded(isExp)

        return True

    def renameTreeItem(self, tHandle):
        """Open a dialog to edit the label of an item.
        """
        tItem = self.theProject.tree[tHandle]
        if tItem is None:
            return False

        newLabel, dlgOk = GuiEditLabel.getLabel(self, text=tItem.itemName)
        if dlgOk:
            tItem.setName(newLabel)
            self.setTreeItemValues(tHandle)
            self._alertTreeChange(tHandle=tHandle, flush=False)

        return

    def saveTreeOrder(self):
        """Build a list of the items in the project tree and send them
        to the project class. This syncs up the two versions of the
        project structure, and must be called before any code that
        depends on this order to be up to date.
        """
        theList = []
        for i in range(self.topLevelItemCount()):
            theList = self._scanChildren(theList, self.topLevelItem(i), i)
        logger.debug("Saving project tree item order")
        self.theProject.setTreeOrder(theList)
        return True

    def getTreeFromHandle(self, tHandle):
        """Recursively return all the child items starting from a given
        item handle.
        """
        theList = []
        theItem = self._getTreeItem(tHandle)
        if theItem is not None:
            theList = self._scanChildren(theList, theItem, 0)
        return theList

    def emptyTrash(self):
        """Permanently delete all documents in the Trash folder. This
        function only asks for confirmation once, and calls the regular
        deleteItem function for each document in the Trash folder.
        """
        if not self.mainGui.hasProject:
            logger.error("No project open")
            return False

        trashHandle = self.theProject.tree.trashRoot()

        logger.debug("Emptying Trash folder")
        if trashHandle is None:
            self.mainGui.makeAlert(self.tr(
                "There is currently no Trash folder in this project."
            ), nwAlert.INFO)
            return False

        theTrash = self.getTreeFromHandle(trashHandle)
        if trashHandle in theTrash:
            theTrash.remove(trashHandle)

        nTrash = len(theTrash)
        if nTrash == 0:
            self.mainGui.makeAlert(self.tr(
                "The Trash folder is already empty."
            ), nwAlert.INFO)
            return False

        msgYes = self.mainGui.askQuestion(
            self.tr("Empty Trash"),
            self.tr("Permanently delete {0} file(s) from Trash?").format(nTrash)
        )
        if not msgYes:
            return False

        logger.verbose("Deleting %d file(s) from Trash", nTrash)
        for tHandle in reversed(self.getTreeFromHandle(trashHandle)):
            if tHandle == trashHandle:
                continue
            self.deleteItem(tHandle, alreadyAsked=True, bulkAction=True)

        if nTrash > 0:
            self._alertTreeChange(tHandle=trashHandle, flush=True)

        return True

    def deleteItem(self, tHandle=None, alreadyAsked=False, bulkAction=False):
        """Delete an item from the project tree. As a first step, files are
        moved to the Trash folder. Permanent deletion is a second step. This
        second step also deletes the item from the project object as well as
        delete the files on disk. Root folders are deleted if they're empty
        only, and the deletion is always permanent.
        """
        if not self.mainGui.hasProject:
            logger.error("No project open")
            return False

        if not self.hasFocus() and not bulkAction:
            logger.info("Delete action blocked due to no widget focus")
            return False

        if tHandle is None:
            tHandle = self.getSelectedHandle()

        if tHandle is None:
            logger.error("There is no item to delete")
            return False

        trItemS = self._getTreeItem(tHandle)
        nwItemS = self.theProject.tree[tHandle]

        if trItemS is None or nwItemS is None:
            logger.error("Could not find tree item for deletion")
            return False

        wCount = self._getItemWordCount(tHandle)
        autoFlush = not bulkAction
        if nwItemS.itemType == nwItemType.ROOT:
            # Only an empty ROOT folder can be deleted
            logger.debug("User requested a root folder '%s' deleted", tHandle)
            tIndex = self.indexOfTopLevelItem(trItemS)
            if trItemS.childCount() == 0:
                self.takeTopLevelItem(tIndex)
                self._deleteTreeItem(tHandle)
                self._alertTreeChange(tHandle=tHandle, flush=True)
            else:
                self.mainGui.makeAlert(self.tr(
                    "Cannot delete root folder. It is not empty. "
                    "Recursive deletion is not supported. "
                    "Please delete the content first."
                ), nwAlert.ERROR)
                return False

        elif nwItemS.itemType == nwItemType.FOLDER and trItemS.childCount() == 0:
            # An empty FOLDER is just deleted without any further checks
            logger.debug("User requested an empty folder '%s' deleted", tHandle)
            trItemP = trItemS.parent()
            tIndex = trItemP.indexOfChild(trItemS)
            trItemP.takeChild(tIndex)
            self._deleteTreeItem(tHandle)
            self._alertTreeChange(tHandle=tHandle, flush=autoFlush)

        else:
            # A populated FOLDER or a FILE requires confirmtation
            logger.debug("User requested a file or folder '%s' deleted", tHandle)
            trItemP = trItemS.parent()
            trItemT = self._addTrashRoot()
            if trItemP is None or trItemT is None:
                logger.error("Could not delete item")
                return False

            if self.theProject.tree.isTrash(tHandle):
                # If the file is in the trash folder already, as the
                # user if they want to permanently delete the file.
                doPermanent = False
                if not alreadyAsked:
                    msgYes = self.mainGui.askQuestion(
                        self.tr("Delete"),
                        self.tr("Permanently delete '{0}'?").format(nwItemS.itemName)
                    )
                    if msgYes:
                        doPermanent = True
                else:
                    doPermanent = True

                if doPermanent:
                    logger.debug("Permanently deleting item with handle '%s'", tHandle)

                    self.propagateCount(tHandle, 0)
                    tIndex = trItemP.indexOfChild(trItemS)
                    trItemC = trItemP.takeChild(tIndex)
                    for dHandle in reversed(self.getTreeFromHandle(tHandle)):
                        if self.mainGui.docEditor.docHandle() == dHandle:
                            self.mainGui.closeDocument()
                        self._deleteTreeItem(dHandle)

                    self._alertTreeChange(tHandle=tHandle, flush=autoFlush)
                    self.projView.wordCountsChanged.emit()

            else:
                # The item is not already in the trash folder, so we
                # move it there.
                msgYes = self.mainGui.askQuestion(
                    self.tr("Delete"),
                    self.tr("Move '{0}' to Trash?").format(nwItemS.itemName),
                )
                if msgYes:
                    logger.debug("Moving item '%s' to trash", tHandle)

                    self.propagateCount(tHandle, 0)
                    tIndex = trItemP.indexOfChild(trItemS)
                    trItemC = trItemP.takeChild(tIndex)
                    trItemT.addChild(trItemC)
                    self._postItemMove(tHandle, wCount)
                    self._recordLastMove(trItemS, trItemP, tIndex)
                    self._alertTreeChange(tHandle=tHandle, flush=autoFlush)

        return True

    def setTreeItemValues(self, tHandle):
        """Set the name and flag values for a tree item from a handle in
        the project tree. Does not trigger a tree change as the data is
        already coming from the project tree.
        """
        trItem = self._getTreeItem(tHandle)
        nwItem = self.theProject.tree[tHandle]
        if trItem is None or nwItem is None:
            return

        itemStatus, statusIcon = nwItem.getImportStatus()
        hLevel = self.theProject.index.getHandleHeaderLevel(tHandle)
        itemIcon = self.mainTheme.getItemIcon(
            nwItem.itemType, nwItem.itemClass, nwItem.itemLayout, hLevel
        )

        trItem.setIcon(self.C_NAME, itemIcon)
        trItem.setText(self.C_NAME, nwItem.itemName)
        trItem.setIcon(self.C_STATUS, statusIcon)
        trItem.setToolTip(self.C_STATUS, itemStatus)

        if nwItem.itemType == nwItemType.FILE:
            trItem.setIcon(
                self.C_EXPORT, self.mainTheme.getIcon("check" if nwItem.isExported else "cross")
            )

        if self.mainConf.emphLabels and nwItem.itemLayout == nwItemLayout.DOCUMENT:
            trFont = trItem.font(self.C_NAME)
            trFont.setBold(hLevel == "H1" or hLevel == "H2")
            trFont.setUnderline(hLevel == "H1")
            trItem.setFont(self.C_NAME, trFont)

        return

    def propagateCount(self, tHandle, newCount, countChildren=False):
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
                newCount += int(tItem.child(i).data(self.C_COUNT, Qt.UserRole))

        tItem.setText(self.C_COUNT, f"{newCount:n}")
        tItem.setData(self.C_COUNT, Qt.UserRole, int(newCount))

        pItem = tItem.parent()
        if pItem is None:
            return

        pCount = 0
        pHandle = None
        for i in range(pItem.childCount()):
            pCount += int(pItem.child(i).data(self.C_COUNT, Qt.UserRole))
            pHandle = pItem.data(self.C_NAME, Qt.UserRole)

        if pHandle:
            if self.theProject.tree.checkType(pHandle, nwItemType.FILE):
                # A file has an internal word count we need to account
                # for, but a folder always has 0 words on its own.
                pCount += self.theProject.index.getCounts(pHandle)[1]

            self.propagateCount(pHandle, pCount, countChildren=False)

        return

    def buildTree(self):
        """Build the entire project tree from scratch. This depends on
        the save project item iterator in the project class which will
        always make sure items with a parent have had their parent item
        sent first.
        """
        logger.debug("Building the project tree ...")
        self.clearTree()

        iCount = 0
        for nwItem in self.theProject.getProjectItems():
            iCount += 1
            self._addTreeItem(nwItem)

        logger.debug("%d item(s) added to the project tree", iCount)
        return True

    def undoLastMove(self):
        """Attempt to undo the last action.
        """
        srcItem = self._lastMove.get("item", None)
        dstItem = self._lastMove.get("parent", None)
        dstIndex = self._lastMove.get("index", None)

        if srcItem is None or dstItem is None or dstIndex is None:
            logger.verbose("No tree move to undo")
            return False

        if srcItem not in self._treeMap.values():
            logger.warning("Source item no longer exists")
            return False

        if dstItem not in self._treeMap.values():
            logger.warning("Previous parent item no longer exists")
            return False

        dstIndex = min(max(0, dstIndex), dstItem.childCount())
        sHandle = srcItem.data(self.C_NAME, Qt.UserRole)
        dHandle = dstItem.data(self.C_NAME, Qt.UserRole)
        logger.debug("Moving item '%s' back to '%s', index %d", sHandle, dHandle, dstIndex)

        wCount = self._getItemWordCount(sHandle)
        self.propagateCount(sHandle, 0)
        parItem = srcItem.parent()
        srcIndex = parItem.indexOfChild(srcItem)
        movItem = parItem.takeChild(srcIndex)
        dstItem.insertChild(dstIndex, movItem)

        self._postItemMove(sHandle, wCount)
        self._alertTreeChange(tHandle=sHandle, flush=True)

        self.clearSelection()
        movItem.setSelected(True)
        self._lastMove = {}

        return True

    def getSelectedHandle(self):
        """Get the currently selected handle. If multiple items are
        selected, return the first.
        """
        selItem = self.selectedItems()
        if selItem:
            return selItem[0].data(self.C_NAME, Qt.UserRole)

        return None

    def setSelectedHandle(self, tHandle, doScroll=False):
        """Set a specific handle as the selected item.
        """
        tItem = self._getTreeItem(tHandle)
        if tItem is None:
            return False

        self.clearSelection()
        self._treeMap[tHandle].setSelected(True)

        selItems = self.selectedIndexes()
        if selItems and doScroll:
            self.scrollTo(selItems[0], QAbstractItemView.PositionAtCenter)

        return True

    def openContextOnSelected(self):
        """Open the context menu on the current selected item.
        """
        selItem = self.selectedItems()
        if selItem:
            pos = self.visualItemRect(selItem[0]).center()
            return self._openContextMenu(pos)
        return False

    def changedSince(self, checkTime):
        """Check if the tree has changed since a given time.
        """
        return self._timeChanged > checkTime

    ##
    #  Private Slots
    ##

    @pyqtSlot()
    def _treeSelectionChange(self):
        """The user changed which item is selected.
        """
        tHandle = self.getSelectedHandle()
        if tHandle is not None:
            self.projView.selectedItemChanged.emit(tHandle)
        return

    @pyqtSlot("QTreeWidgetItem*", int)
    def _treeDoubleClick(self, tItem, colNo):
        """Capture a double-click event and either request the document
        for editing if it is a file, or expand/close the node it is not.
        """
        tHandle = self.getSelectedHandle()
        if tHandle is None:
            return

        tItem = self.theProject.tree[tHandle]
        if tItem is None:
            return

        if tItem.itemType == nwItemType.FILE:
            self.projView.openDocumentRequest.emit(tHandle, nwDocMode.EDIT, -1, "")
        else:
            trItem = self._getTreeItem(tHandle)
            if trItem is not None:
                trItem.setExpanded(not trItem.isExpanded())

        return

    @pyqtSlot("QPoint")
    def _openContextMenu(self, clickPos):
        """The user right clicked an element in the project tree, so we
        open a context menu in-place.
        """
        tItem = None
        selItem = self.itemAt(clickPos)
        if isinstance(selItem, QTreeWidgetItem):
            tHandle = selItem.data(self.C_NAME, Qt.UserRole)
            tItem = self.theProject.tree[tHandle]

        if tItem is None:
            logger.debug("No item found")
            return False

        ctxMenu = QMenu()

        # Trash Folder
        # ============

        trashHandle = self.theProject.tree.trashRoot()
        if tItem.itemHandle == trashHandle and trashHandle is not None:
            # The trash folder only has one option
            ctxMenu.addAction(
                self.tr("Empty Trash"), lambda: self.emptyTrash()
            )
            ctxMenu.exec_(self.viewport().mapToGlobal(clickPos))
            return True

        # Document Actions
        # ================

        isFile = tItem.itemType == nwItemType.FILE
        if isFile:
            ctxMenu.addAction(
                self.tr("Open Document"),
                lambda: self.projView.openDocumentRequest.emit(tHandle, nwDocMode.EDIT, -1, "")
            )
            ctxMenu.addAction(
                self.tr("View Document"),
                lambda: self.projView.openDocumentRequest.emit(tHandle, nwDocMode.VIEW, -1, "")
            )
            ctxMenu.addSeparator()

        # Edit Item Settings
        # ==================

        ctxMenu.addAction(
            self.tr("Change Label"), lambda: self.renameTreeItem(tHandle)
        )

        if isFile:
            ctxMenu.addAction(
                self.tr("Toggle Exported"), lambda: self._toggleItemExported(tHandle)
            )

        if tItem.isNovelLike():
            mStatus = ctxMenu.addMenu(self.tr("Change Status"))
            for n, (key, entry) in enumerate(self.theProject.statusItems.items()):
                aStatus = mStatus.addAction(entry["icon"], entry["name"])
                aStatus.triggered.connect(
                    lambda n, key=key: self._changeItemStatus(tHandle, key)
                )
        else:
            mImport = ctxMenu.addMenu(self.tr("Change Importance"))
            for n, (key, entry) in enumerate(self.theProject.importItems.items()):
                aImport = mImport.addAction(entry["icon"], entry["name"])
                aImport.triggered.connect(
                    lambda n, key=key: self._changeItemImport(tHandle, key)
                )

        if isFile and tItem.documentAllowed():
            if tItem.itemLayout == nwItemLayout.NOTE:
                ctxMenu.addAction(
                    self.tr("Change to {0}").format(
                        trConst(nwLabels.LAYOUT_NAME[nwItemLayout.DOCUMENT])
                    ),
                    lambda: self._changeItemLayout(tHandle, nwItemLayout.DOCUMENT)
                )
            else:
                ctxMenu.addAction(
                    self.tr("Change to {0}").format(
                        trConst(nwLabels.LAYOUT_NAME[nwItemLayout.NOTE])
                    ),
                    lambda: self._changeItemLayout(tHandle, nwItemLayout.NOTE)
                )

        ctxMenu.addSeparator()

        # Delete Item
        # ===========

        if tItem.itemClass == nwItemClass.TRASH or tItem.itemType == nwItemType.ROOT:
            ctxMenu.addAction(
                self.tr("Delete Permanently"), lambda: self.deleteItem(tHandle)
            )
        else:
            ctxMenu.addAction(
                self.tr("Move to Trash"), lambda: self.deleteItem(tHandle)
            )

        ctxMenu.exec_(self.viewport().mapToGlobal(clickPos))

        return True

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

            tHandle = selItem.data(self.C_NAME, Qt.UserRole)
            tItem = self.theProject.tree[tHandle]
            if tItem is None:
                return

            if tItem.itemType == nwItemType.FILE:
                self.projView.openDocumentRequest.emit(tHandle, nwDocMode.VIEW, -1, "")

        return

    def dropEvent(self, theEvent):
        """Overload the drop item event to ensure relevant data has been
        updated.
        """
        sHandle = self.getSelectedHandle()
        if sHandle is None:
            logger.error("Invalid drag and drop event")
            return

        logger.debug("Drag'n'drop of item '%s' accepted", sHandle)

        sItem = self._getTreeItem(sHandle)
        isExpanded = False
        if sItem is not None:
            isExpanded = sItem.isExpanded()

        pItem = sItem.parent()
        pIndex = 0
        if pItem is not None:
            pIndex = pItem.indexOfChild(sItem)

        wCount = self._getItemWordCount(sHandle)
        self.propagateCount(sHandle, 0)

        QTreeWidget.dropEvent(self, theEvent)
        self._postItemMove(sHandle, wCount)
        self._recordLastMove(sItem, pItem, pIndex)
        self._alertTreeChange(tHandle=sHandle, flush=True)
        sItem.setExpanded(isExpanded)

        return

    ##
    #  Internal Functions
    ##

    def _postItemMove(self, tHandle, wCount):
        """Run various maintenance tasks for a moved item.
        """
        trItemS = self._getTreeItem(tHandle)
        nwItemS = self.theProject.tree[tHandle]
        trItemP = trItemS.parent()
        if trItemP is None:
            logger.error("Failed to find new parent item of '%s'", tHandle)
            return False

        # Update item parent handle in the project, make sure meta data
        # is updated accordingly, and update word count
        pHandle = trItemP.data(self.C_NAME, Qt.UserRole)
        nwItemS.setParent(pHandle)
        trItemP.setExpanded(True)
        logger.debug("The parent of item '%s' has been changed to '%s'", tHandle, pHandle)

        mHandles = self.getTreeFromHandle(tHandle)
        logger.debug("A total of %d item(s) were moved", len(mHandles))
        for mHandle in mHandles:
            logger.debug("Updating item '%s'", mHandle)
            self.theProject.tree.updateItemData(mHandle)

            # Update the index
            if nwItemS.isInactive():
                self.theProject.index.deleteHandle(mHandle)
            else:
                self.theProject.index.reIndexHandle(mHandle)

            self.setTreeItemValues(mHandle)

        # Trigger dependent updates
        self.propagateCount(tHandle, wCount)

        return True

    def _getItemWordCount(self, tHandle):
        """Retrun the word count of a given item handle.
        """
        tItem = self._getTreeItem(tHandle)
        if tItem is None:
            return 0
        return int(tItem.data(self.C_COUNT, Qt.UserRole))

    def _getTreeItem(self, tHandle):
        """Return the QTreeWidgetItem of a given item handle.
        """
        return self._treeMap.get(tHandle, None)

    def _deleteTreeItem(self, tHandle):
        """Permanently delete a tree item from the project and the map.
        """
        if self.theProject.tree.checkType(tHandle, nwItemType.FILE):
            delDoc = NWDoc(self.theProject, tHandle)
            if not delDoc.deleteDocument():
                self.mainGui.makeAlert([
                    self.tr("Could not delete document file."), delDoc.getError()
                ], nwAlert.ERROR)
                return False

        self.theProject.index.deleteHandle(tHandle)
        del self.theProject.tree[tHandle]
        self._treeMap.pop(tHandle, None)

        return True

    def _toggleItemExported(self, tHandle):
        """Toggle the exported status of an item.
        """
        tItem = self.theProject.tree[tHandle]
        if tItem is not None:
            tItem.setExported(not tItem.isExported)
            self.setTreeItemValues(tItem.itemHandle)
        return

    def _changeItemStatus(self, tHandle, tStatus):
        """Set a new status value of an item.
        """
        tItem = self.theProject.tree[tHandle]
        if tItem is not None:
            tItem.setStatus(tStatus)
            self.setTreeItemValues(tItem.itemHandle)
        return

    def _changeItemImport(self, tHandle, tImport):
        """Set a new importance value of an item.
        """
        tItem = self.theProject.tree[tHandle]
        if tItem is not None:
            tItem.setImport(tImport)
            self.setTreeItemValues(tItem.itemHandle)
        return

    def _changeItemLayout(self, tHandle, itemLayout):
        """Set a new item layout value of an item.
        """
        tItem = self.theProject.tree[tHandle]
        if tItem is not None:
            if itemLayout == nwItemLayout.DOCUMENT and tItem.documentAllowed():
                tItem.setLayout(nwItemLayout.DOCUMENT)
                self.setTreeItemValues(tItem.itemHandle)
            elif itemLayout == nwItemLayout.NOTE:
                tItem.setLayout(nwItemLayout.NOTE)
                self.setTreeItemValues(tItem.itemHandle)
        return

    def _scanChildren(self, theList, tItem, tIndex):
        """This is a recursive function returning all items in a tree
        starting at a given QTreeWidgetItem.
        """
        tHandle = tItem.data(self.C_NAME, Qt.UserRole)
        cCount = tItem.childCount()

        # Update tree-related meta data
        nwItem = self.theProject.tree[tHandle]
        nwItem.setExpanded(tItem.isExpanded() and cCount > 0)
        nwItem.setOrder(tIndex)

        theList.append(tHandle)
        for i in range(cCount):
            self._scanChildren(theList, tItem.child(i), i)

        return theList

    def _addTreeItem(self, nwItem, nHandle=None):
        """Create a QTreeWidgetItem from an NWItem and add it to the
        project tree.
        """
        tHandle = nwItem.itemHandle
        pHandle = nwItem.itemParent
        newItem = QTreeWidgetItem([""]*4)

        newItem.setText(self.C_NAME, "")
        newItem.setText(self.C_COUNT, "0")
        newItem.setText(self.C_EXPORT, "")
        newItem.setText(self.C_STATUS, "")

        newItem.setTextAlignment(self.C_NAME, Qt.AlignLeft)
        newItem.setTextAlignment(self.C_COUNT, Qt.AlignRight)
        newItem.setTextAlignment(self.C_EXPORT, Qt.AlignLeft)
        newItem.setTextAlignment(self.C_STATUS, Qt.AlignLeft)

        newItem.setData(self.C_NAME, Qt.UserRole, tHandle)
        newItem.setData(self.C_COUNT, Qt.UserRole, 0)

        self._treeMap[tHandle] = newItem
        if pHandle is None:
            if nwItem.itemType == nwItemType.ROOT:
                newItem.setFlags(newItem.flags() ^ Qt.ItemIsDragEnabled)
                self.addTopLevelItem(newItem)
            else:
                self.mainGui.makeAlert(self.tr(
                    "There is nowhere to add item with name '{0}'."
                ).format(nwItem.itemName), nwAlert.ERROR)
                del self._treeMap[tHandle]
                return None

        else:
            byIndex = -1
            if nHandle is not None and nHandle in self._treeMap:
                try:
                    byIndex = self._treeMap[pHandle].indexOfChild(self._treeMap[nHandle])
                except Exception:
                    logger.error("Failed to get index of item with handle '%s'", nHandle)
            if byIndex >= 0:
                self._treeMap[pHandle].insertChild(byIndex + 1, newItem)
            else:
                self._treeMap[pHandle].addChild(newItem)
            self.propagateCount(tHandle, nwItem.wordCount, countChildren=True)

        self.setTreeItemValues(tHandle)
        newItem.setExpanded(nwItem.isExpanded)

        return newItem

    def _addTrashRoot(self):
        """Adds the trash root folder if it doesn't already exist in the
        project tree.
        """
        trashHandle = self.theProject.trashFolder()
        if trashHandle is None:
            return None

        trItem = self._getTreeItem(trashHandle)
        if trItem is None:
            trItem = self._addTreeItem(self.theProject.tree[trashHandle])
            if trItem is not None:
                trItem.setExpanded(True)
                self._alertTreeChange(tHandle=trashHandle, flush=True)

        return trItem

    def _alertTreeChange(self, tHandle=None, flush=True):
        """Update information on tree change state, and emit necessary
        signals.
        """
        self._timeChanged = time()
        self.theProject.setProjectChanged(True)
        if flush:
            self.saveTreeOrder()

        tItem = self.theProject.tree[tHandle]
        if tItem is None:
            return

        itemType = tItem.itemType
        if itemType == nwItemType.ROOT:
            self.projView.rootFolderChanged.emit(tHandle)

        self.projView.treeItemChanged.emit(tHandle)

        return

    def _recordLastMove(self, srcItem, parItem, parIndex):
        """Record the last action so that it can be undone.
        """
        prevItem = self._lastMove.get("item", None)
        if prevItem is None or srcItem != prevItem:
            self._lastMove = {
                "item": srcItem,
                "parent": parItem,
                "index": parIndex,
            }

        return

# END Class GuiProjectTree
