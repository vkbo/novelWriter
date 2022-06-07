"""
novelWriter – GUI Project Tree
==============================
GUI classes for the main window project tree

File History:
Created: 2018-09-29 [0.0.1] GuiProjectTree
Created: 2020-06-04 [0.7]   GuiProjectTreeMenu
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

from PyQt5.QtCore import Qt, QSize, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon, QPalette
from PyQt5.QtWidgets import (
    qApp, QTreeWidget, QTreeWidgetItem, QAbstractItemView, QMenu, QAction,
    QFrame, QDialog, QHeaderView, QWidget, QVBoxLayout, QLabel, QToolButton,
    QSizePolicy, QInputDialog, QHBoxLayout, QShortcut
)

from novelwriter.core import NWDoc
from novelwriter.enum import nwDocMode, nwItemType, nwItemClass, nwItemLayout, nwAlert
from novelwriter.dialogs.itemeditor import GuiItemEditor
from novelwriter.constants import trConst, nwLabels

logger = logging.getLogger(__name__)


class GuiProjectView(QWidget):
    """This is a wrapper class holding all the elements of the project
    tree. The core object is the project tree itself. Most methods
    available are mapped through to the project tree class.
    """

    # Signals triggered when the meta data values of items change
    treeItemChanged = pyqtSignal(str)
    novelItemChanged = pyqtSignal(str)
    rootFolderChanged = pyqtSignal(str)
    wordCountsChanged = pyqtSignal()

    # Signals for user interaction with the project tree
    selectedItemChanged = pyqtSignal(str)
    openDocumentRequest = pyqtSignal(str, Enum)

    def __init__(self, theParent):
        QWidget.__init__(self, theParent)

        self.theParent = theParent

        # Build GUI
        self.projBar = GuiProjectToolBar(self)
        self.projTree = GuiProjectTree(self)

        # Assemble
        self.outerBox = QVBoxLayout()
        self.outerBox.addWidget(self.projBar, 0)
        self.outerBox.addWidget(self.projTree, 1)
        self.outerBox.setContentsMargins(0, 0, 0, 0)
        self.outerBox.setSpacing(0)

        self.setLayout(self.outerBox)

        # Keyboard Shortcuts
        self.keyCtrlUp = QShortcut(self.projTree)
        self.keyCtrlUp.setKey("Ctrl+Up")
        self.keyCtrlUp.setContext(Qt.WidgetShortcut)
        self.keyCtrlUp.activated.connect(lambda: self.projTree.moveTreeItem(-1))

        self.keyCtrlDown = QShortcut(self.projTree)
        self.keyCtrlDown.setKey("Ctrl+Down")
        self.keyCtrlDown.setContext(Qt.WidgetShortcut)
        self.keyCtrlDown.activated.connect(lambda: self.projTree.moveTreeItem(1))

        # Connect Signals

        # Function Mappings
        self.newTreeItem = self.projTree.newTreeItem
        self.revealNewTreeItem = self.projTree.revealNewTreeItem
        self.editTreeItem = self.projTree.editTreeItem
        self.getTreeFromHandle = self.projTree.getTreeFromHandle
        self.emptyTrash = self.projTree.emptyTrash
        self.deleteItem = self.projTree.deleteItem
        self.setTreeItemValues = self.projTree.setTreeItemValues
        self.propagateCount = self.projTree.propagateCount
        self.undoLastMove = self.projTree.undoLastMove
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

    def treeFocus(self):
        """Check if the project tree has focus.
        """
        return self.projTree.hasFocus()

    def anyFocus(self):
        """Check if any widget or child widget has focus.
        """
        if self.hasFocus():
            return True
        if self.isAncestorOf(qApp.focusWidget()):
            return True
        return False

    ##
    #  Public Solts
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

    ADD_PLAIN  = 0
    ADD_CHAP   = 1
    ADD_SCENE  = 2
    ADD_NOTE   = 3
    ADD_FOLDER = 4

    def __init__(self, projView):
        QTreeWidget.__init__(self, projView)

        logger.debug("Initialising GuiProjectToolBar ...")

        self.mainConf   = novelwriter.CONFIG
        self.projView   = projView
        self.theParent  = projView.theParent
        self.theProject = projView.theParent.theProject
        self.theTheme   = projView.theParent.theTheme

        iPx = self.theTheme.baseIconSize
        mPx = self.mainConf.pxInt(4)

        self.setContentsMargins(0, 0, 0, 0)
        self.setAutoFillBackground(True)

        qPalette = self.palette()
        qPalette.setBrush(QPalette.Window, qPalette.base())
        self.setPalette(qPalette)

        fadeCol = qPalette.text().color()
        buttonStyle = (
            "QToolButton {{border: none; background: transparent;}} "
            "QToolButton:hover {{border: none; background: rgba({0},{1},{2},0.2);}}"
        ).format(fadeCol.red(), fadeCol.green(), fadeCol.blue())

        # Tree Label
        self.projLabel = QLabel("<b>%s</b>" % self.tr("Project Content"))
        self.projLabel.setContentsMargins(0, 0, 0, 0)
        self.projLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Move Buttons
        self.tbMoveU = QToolButton(self)
        self.tbMoveU.setToolTip("%s [Ctrl+Up]" % self.tr("Move Up"))
        self.tbMoveU.setIcon(self.theTheme.getIcon("up"))
        self.tbMoveU.setIconSize(QSize(iPx, iPx))
        self.tbMoveU.setStyleSheet(buttonStyle)
        self.tbMoveU.clicked.connect(lambda: self.projView.projTree.moveTreeItem(-1))

        self.tbMoveD = QToolButton(self)
        self.tbMoveD.setToolTip("%s [Ctrl+Down]" % self.tr("Move Down"))
        self.tbMoveD.setIcon(self.theTheme.getIcon("down"))
        self.tbMoveD.setIconSize(QSize(iPx, iPx))
        self.tbMoveD.setStyleSheet(buttonStyle)
        self.tbMoveD.clicked.connect(lambda: self.projView.projTree.moveTreeItem(1))

        # Items Menu
        self.mItems = QMenu()

        self.aAddEmpty = self.mItems.addAction(self.tr("Plain Document"))
        self.aAddEmpty.setIcon(self.theTheme.getIcon("proj_document"))
        self.aAddEmpty.triggered.connect(lambda: self._forwardNewItem(self.ADD_PLAIN))

        self.aAddChap = self.mItems.addAction(self.tr("Chapter Document"))
        self.aAddChap.setIcon(self.theTheme.getIcon("proj_chapter"))
        self.aAddChap.triggered.connect(lambda: self._forwardNewItem(self.ADD_CHAP))

        self.aAddScene = self.mItems.addAction(self.tr("Scene Document"))
        self.aAddScene.setIcon(self.theTheme.getIcon("proj_scene"))
        self.aAddScene.triggered.connect(lambda: self._forwardNewItem(self.ADD_SCENE))

        self.aAddNote = self.mItems.addAction(self.tr("Project Note"))
        self.aAddNote.setIcon(self.theTheme.getIcon("proj_note"))
        self.aAddNote.triggered.connect(lambda: self._forwardNewItem(self.ADD_NOTE))

        self.aAddFolder = self.mItems.addAction(self.tr("Folder"))
        self.aAddFolder.setIcon(self.theTheme.getIcon("proj_folder"))
        self.aAddFolder.triggered.connect(lambda: self._forwardNewItem(self.ADD_FOLDER))

        self.mAddRoot = self.mItems.addMenu(self.tr("Root Folder"))
        self._addRootFolderEntry(nwItemClass.NOVEL)
        self._addRootFolderEntry(nwItemClass.ARCHIVE)
        self.mAddRoot.addSeparator()
        self._addRootFolderEntry(nwItemClass.PLOT)
        self._addRootFolderEntry(nwItemClass.CHARACTER)
        self._addRootFolderEntry(nwItemClass.WORLD)
        self._addRootFolderEntry(nwItemClass.ARCHIVE)
        self._addRootFolderEntry(nwItemClass.OBJECT)
        self._addRootFolderEntry(nwItemClass.ENTITY)
        self._addRootFolderEntry(nwItemClass.CUSTOM)

        self.tbItems = QToolButton(self)
        self.tbItems.setToolTip("%s [Ctrl+N]" % self.tr("Add Item"))
        self.tbItems.setShortcut("Ctrl+N")
        self.tbItems.setIcon(self.theTheme.getIcon("add"))
        self.tbItems.setIconSize(QSize(iPx, iPx))
        self.tbItems.setStyleSheet(buttonStyle)
        self.tbItems.setMenu(self.mItems)
        self.tbItems.setPopupMode(QToolButton.InstantPopup)

        # Settings Menu
        self.tbSettings = QToolButton(self)
        self.tbSettings.setIcon(self.theTheme.getIcon("menu"))
        self.tbSettings.setIconSize(QSize(iPx, iPx))
        self.tbSettings.setStyleSheet(buttonStyle)
        self.tbSettings.setPopupMode(QToolButton.InstantPopup)

        # Assemble
        self.outerBox = QHBoxLayout()
        self.outerBox.addWidget(self.projLabel)
        self.outerBox.addWidget(self.tbMoveU)
        self.outerBox.addWidget(self.tbMoveD)
        self.outerBox.addWidget(self.tbItems)
        self.outerBox.addWidget(self.tbSettings)
        self.outerBox.setContentsMargins(mPx, mPx, 0, mPx)
        self.outerBox.setSpacing(mPx)

        self.setLayout(self.outerBox)

        logger.debug("GuiProjectToolBar initialisation complete")

        return

    ##
    #  Private Slots
    ##

    @pyqtSlot(Enum)
    def _forwardNewRootFolder(self, itemClass):
        """Forward the request for a new root folder to the tree.
        """
        self.projView.projTree.newTreeItem(nwItemType.ROOT, itemClass)
        return

    @pyqtSlot(int)
    def _forwardNewItem(self, type):
        """Forward the request for a new item of a given type.
        """
        if type == self.ADD_PLAIN:
            self.projView.projTree.newTreeItem(nwItemType.FILE, hLevel=0, isNote=False)
        elif type == self.ADD_CHAP:
            self.projView.projTree.newTreeItem(nwItemType.FILE, hLevel=2, isNote=False)
        elif type == self.ADD_SCENE:
            self.projView.projTree.newTreeItem(nwItemType.FILE, hLevel=3, isNote=False)
        elif type == self.ADD_NOTE:
            self.projView.projTree.newTreeItem(nwItemType.FILE, hLevel=1, isNote=True)
        elif type == self.ADD_FOLDER:
            self.projView.projTree.newTreeItem(nwItemType.FOLDER)
        return

    ##
    #  Internal Functions
    ##

    def _addRootFolderEntry(self, itemClass):
        """Add a menu entry for a root folder of a given class.
        """
        aNew = self.mAddRoot.addAction(trConst(nwLabels.CLASS_NAME[itemClass]))
        aNew.setIcon(self.theTheme.getIcon(nwLabels.CLASS_ICON[itemClass]))
        aNew.triggered.connect(lambda: self._forwardNewRootFolder(itemClass))
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
        self.theParent  = projView.theParent
        self.theTheme   = projView.theParent.theTheme
        self.theProject = projView.theParent.theProject

        # Internal Variables
        self._treeMap = {}
        self._lastMove = {}
        self._timeChanged = 0

        ##
        #  Build GUI
        ##

        # Context Menu
        self.ctxMenu = GuiProjectTreeMenu(self)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._rightClickMenu)

        # Tree Settings
        iPx = self.theTheme.baseIconSize
        cMg = self.mainConf.pxInt(6)
        self.setIconSize(QSize(iPx, iPx))
        self.setFrameStyle(QFrame.NoFrame)
        self.setExpandsOnDoubleClick(False)
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
        if not self.theParent.hasProject:
            logger.error("No project open")
            return False

        nHandle = None
        tHandle = None

        if itemType == nwItemType.ROOT and isinstance(itemClass, nwItemClass):

            tHandle = self.theProject.newRoot(itemClass)

        elif itemType in (nwItemType.FILE, nwItemType.FOLDER):

            sHandle = self.getSelectedHandle()
            if sHandle is None or sHandle not in self.theProject.tree:
                self.theParent.makeAlert(self.tr(
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
                self.theParent.makeAlert(self.tr(
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

            newLabel, dlgOk = QInputDialog.getText(self, "", self.tr("Label:"), text=newLabel)
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
        tItem = self._getTreeItem(tHandle)
        if tItem is None:
            logger.verbose("No item selected")
            return False

        pItem = tItem.parent()
        if pItem is None:
            tIndex = self.indexOfTopLevelItem(tItem)
            nChild = self.topLevelItemCount()
            nIndex = tIndex + nStep
            if nIndex < 0 or nIndex >= nChild:
                return False
            cItem = self.takeTopLevelItem(tIndex)
            self.insertTopLevelItem(nIndex, cItem)

        else:
            tIndex = pItem.indexOfChild(tItem)
            nChild = pItem.childCount()
            nIndex = tIndex + nStep
            if nIndex < 0 or nIndex >= nChild:
                return False
            cItem = pItem.takeChild(tIndex)
            pItem.insertChild(nIndex, cItem)
            self._recordLastMove(cItem, pItem, tIndex)

        self._alertTreeChange(tHandle=tHandle, flush=True)
        self.clearSelection()
        cItem.setSelected(True)

        return True

    def editTreeItem(self, tHandle):
        """Open the edit item dialog.
        """
        tItem = self.theProject.tree[tHandle]
        if tItem is None:
            return False
        if tItem.itemType == nwItemType.NO_TYPE:
            return False

        logger.verbose("Requesting change to item '%s'", tHandle)
        dlgProj = GuiItemEditor(self, tHandle)
        dlgProj.exec_()
        if dlgProj.result() == QDialog.Accepted:
            self.setTreeItemValues(tHandle)
            self._alertTreeChange(tHandle=tHandle, flush=False)

        return True

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
        if not self.theParent.hasProject:
            logger.error("No project open")
            return False

        trashHandle = self.theProject.tree.trashRoot()

        logger.debug("Emptying Trash folder")
        if trashHandle is None:
            self.theParent.makeAlert(self.tr(
                "There is currently no Trash folder in this project."
            ), nwAlert.INFO)
            return False

        theTrash = self.getTreeFromHandle(trashHandle)
        if trashHandle in theTrash:
            theTrash.remove(trashHandle)

        nTrash = len(theTrash)
        if nTrash == 0:
            self.theParent.makeAlert(self.tr(
                "The Trash folder is already empty."
            ), nwAlert.INFO)
            return False

        msgYes = self.theParent.askQuestion(
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
        if not self.theParent.hasProject:
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
                self.theParent.makeAlert(self.tr(
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
                    msgYes = self.theParent.askQuestion(
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
                        if self.theParent.docEditor.docHandle() == dHandle:
                            self.theParent.closeDocument()
                        self._deleteTreeItem(dHandle)

                    self._alertTreeChange(tHandle=tHandle, flush=autoFlush)
                    self.projView.wordCountsChanged.emit()

            else:
                # The item is not already in the trash folder, so we
                # move it there.
                msgYes = self.theParent.askQuestion(
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

        expIcon = QIcon()
        if nwItem.itemType == nwItemType.FILE:
            if nwItem.isExported:
                expIcon = self.theTheme.getIcon("check")
            else:
                expIcon = self.theTheme.getIcon("cross")

        itemStatus, statusIcon = nwItem.getImportStatus()
        hLevel = self.theProject.index.getHandleHeaderLevel(tHandle)
        itemIcon = self.theTheme.getItemIcon(
            nwItem.itemType, nwItem.itemClass, nwItem.itemLayout, hLevel
        )

        trItem.setIcon(self.C_NAME, itemIcon)
        trItem.setText(self.C_NAME, nwItem.itemName)
        trItem.setIcon(self.C_EXPORT, expIcon)
        trItem.setIcon(self.C_STATUS, statusIcon)
        trItem.setToolTip(self.C_STATUS, itemStatus)

        if self.mainConf.emphLabels and nwItem.itemLayout == nwItemLayout.DOCUMENT:
            trFont = trItem.font(self.C_NAME)
            if hLevel in ("H1", "H2"):
                trFont.setBold(True)
                trFont.setUnderline(True)
            else:
                trFont.setBold(False)
                trFont.setUnderline(False)
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

        if not self.projView.anyFocus():
            return False

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
        if tHandle not in self._treeMap:
            return False

        tItem = self._getTreeItem(tHandle)
        if tItem is None:
            return False

        self.clearSelection()
        self._treeMap[tHandle].setSelected(True)

        selItems = self.selectedIndexes()
        if selItems and doScroll:
            self.scrollTo(selItems[0], QAbstractItemView.PositionAtCenter)

        return True

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
            self.projView.openDocumentRequest.emit(tHandle, nwDocMode.EDIT)
        else:
            trItem = self._getTreeItem(tHandle)
            if trItem is not None:
                trItem.setExpanded(not trItem.isExpanded())

        return

    @pyqtSlot("QPoint")
    def _rightClickMenu(self, clickPos):
        """The user right clicked an element in the project tree, so we
        open a context menu in-place.
        """
        selItem = self.itemAt(clickPos)
        if isinstance(selItem, QTreeWidgetItem):
            tHandle = selItem.data(self.C_NAME, Qt.UserRole)
            self.setSelectedHandle(tHandle)  # Just to be safe
            tItem = self.theProject.tree[tHandle]
            if tItem is not None:
                if self.ctxMenu.filterActions(tItem):
                    # Only open menu if any actions remain after filter
                    self.ctxMenu.exec_(self.viewport().mapToGlobal(clickPos))

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

            tHandle = selItem.data(self.C_NAME, Qt.UserRole)
            tItem = self.theProject.tree[tHandle]
            if tItem is None:
                return

            if tItem.itemType == nwItemType.FILE:
                self.projView.openDocumentRequest.emit(tHandle, nwDocMode.VIEW)

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
                self.theParent.makeAlert([
                    self.tr("Could not delete document file."), delDoc.getError()
                ], nwAlert.ERROR)
                return False

        self.theProject.index.deleteHandle(tHandle)
        del self.theProject.tree[tHandle]
        self._treeMap.pop(tHandle, None)

        return True

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
                self.theParent.makeAlert(self.tr(
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
        elif itemType == nwItemType.FILE and tItem.isNovelLike():
            self.projView.novelItemChanged.emit(tHandle)

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


class GuiProjectTreeMenu(QMenu):

    def __init__(self, theTree):
        QMenu.__init__(self, theTree)

        self.theTree = theTree
        self.theItem = None

        self.editItem = QAction(self.tr("Edit Project Item"), self)
        self.editItem.triggered.connect(self._doEditItem)
        self.addAction(self.editItem)

        self.openItem = QAction(self.tr("Open Document"), self)
        self.openItem.triggered.connect(self._doOpenItem)
        self.addAction(self.openItem)

        self.viewItem = QAction(self.tr("View Document"), self)
        self.viewItem.triggered.connect(self._doViewItem)
        self.addAction(self.viewItem)

        self.toggleExp = QAction(self.tr("Toggle Included Flag"), self)
        self.toggleExp.triggered.connect(self._doToggleExported)
        self.addAction(self.toggleExp)

        self.deleteItem = QAction(self.tr("Delete Item"), self)
        self.deleteItem.triggered.connect(self._doDeleteItem)
        self.addAction(self.deleteItem)

        self.emptyTrash = QAction(self.tr("Empty Trash"), self)
        self.emptyTrash.triggered.connect(self._doEmptyTrash)
        self.addAction(self.emptyTrash)

        return

    def filterActions(self, theItem):
        """Filter the menu entries available based on the properties of
        the item the menu was activated on.
        """
        self.theItem = theItem

        if theItem is None:
            logger.error("Failed to extract information to build tree context menu")
            return False

        trashHandle = self.theTree.theProject.tree.trashRoot()

        isTrash = theItem.itemHandle == trashHandle and trashHandle is not None
        isFile = theItem.itemType == nwItemType.FILE

        self.editItem.setVisible(not isTrash)
        self.openItem.setVisible(isFile)
        self.viewItem.setVisible(isFile)
        self.toggleExp.setVisible(isFile)
        self.deleteItem.setVisible(not isTrash)
        self.emptyTrash.setVisible(isTrash)

        return True

    ##
    #  Slots
    ##

    @pyqtSlot()
    def _doOpenItem(self):
        """Forward the open document call to the main GUI window.
        """
        if self.theItem is not None:
            self.theTree.theParent.openDocument(self.theItem.itemHandle, doScroll=False)
        return

    @pyqtSlot()
    def _doViewItem(self):
        """Forward the view document call to the main GUI window.
        """
        if self.theItem is not None:
            self.theTree.theParent.viewDocument(self.theItem.itemHandle)
        return

    @pyqtSlot()
    def _doEditItem(self):
        """Forward the edit item call to the main GUI window.
        """
        if self.theItem is not None:
            self.theTree.theParent.editItem()
        return

    @pyqtSlot()
    def _doToggleExported(self):
        """Flip the isExported flag of the current item.
        """
        if self.theItem is not None:
            self.theItem.setExported(not self.theItem.isExported)
            self.theTree.setTreeItemValues(self.theItem.itemHandle)
        return

    @pyqtSlot()
    def _doDeleteItem(self):
        """Forward the delete item call to the project tree.
        """
        if self.theItem is not None:
            self.theTree.deleteItem()
        return

    @pyqtSlot()
    def _doEmptyTrash(self):
        """Forward the empty trash call to the project tree.
        """
        self.theTree.emptyTrash()
        return

# END Class GuiProjectTreeMenu
