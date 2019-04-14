# -*- coding: utf-8 -*-
"""novelWriter GUI Document Tree Context Menu

 novelWriter – GUI Document Tree Context Menu
==============================================
 Class holding the context menu of the left side document tree view

 File History:
 Created: 2019-04-14 [0.0.1]

"""

import logging
import nw

from PyQt5.QtGui     import QIcon
from PyQt5.QtWidgets import QMenu, QAction

from nw.enum         import nwItemType, nwItemClass, nwItemAction

logger = logging.getLogger(__name__)

class GuiDocTreeCtx(QMenu):

    def __init__(self, theDocTree, theProject, thePosition):
        QMenu.__init__(self, theDocTree)

        logger.debug("Initialising DocTree ContextMenu ...")
        self.mainConf   = nw.CONFIG
        self.theProject = theProject
        self.theDocTree = theDocTree

        self.selAction  = None
        self.selClass   = None
        self.selType    = None
        self.selTarget  = None

        selItems = self.theDocTree.selectedItems()
        if len(selItems) == 0:
            self.selHandle = None
        else:
            self.selHandle = selItems[0].text(3)
            print(self.selHandle)

        self._buildMenu()

        logger.debug("DocTree ContextMenu initialisation complete")

        self.exec_(self.theDocTree.viewport().mapToGlobal(thePosition))

        return

    def _buildMenu(self):
        vActs = self.theProject.getActionList(self.selHandle)
        if nwItemAction.ADD_ROOT in vActs.keys():
            self._buildMenuAddRoot(vActs)
        if nwItemAction.ADD_FOLDER in vActs.keys():
            self._buildMenuAddFolder(vActs)
        if nwItemAction.ADD_FILE in vActs.keys():
            self._buildMenuAddFile(vActs)
        if nwItemAction.MOVE_UP in vActs.keys():
            self._buildMenuMoveUp(vActs)
        if nwItemAction.MOVE_DOWN in vActs.keys():
            self._buildMenuMoveDown(vActs)
        if nwItemAction.MOVE_TRASH in vActs.keys():
            self._buildMenuMoveTrash(vActs)
        if nwItemAction.MOVE_TO in vActs.keys():
            self._buildMenuMoveTo(vActs)
        if nwItemAction.SPLIT in vActs.keys():
            self._buildMenuSplit(vActs)
        if nwItemAction.MERGE in vActs.keys():
            self._buildMenuMerge(vActs)
        if nwItemAction.DELETE in vActs.keys():
            self._buildMenuDelete(vActs)
        if nwItemAction.DELETE_ROOT in vActs.keys():
            self._buildMenuDeleteRoot(vActs)
        if nwItemAction.EMPTY_TRASH in vActs.keys():
            self._buildMenuEmptyTrash(vActs)

    ##
    #  Build Sub Menus
    ##

    def _buildMenuDelete(self, vActs):
        mnuItem = QAction("Delete Permanently", self)
        mnuItem.triggered.connect(lambda: self._ctxSignal(
            nwItemAction.DELETE, None, None
        ))
        self.addAction(mnuItem)

    def _buildMenuDeleteRoot(self, vActs):
        mnuItem = QAction("Remove Root", self)
        mnuItem.triggered.connect(lambda: self._ctxSignal(
            nwItemAction.DELETE_ROOT, None, None
        ))
        self.addAction(mnuItem)

    def _buildMenuEmptyTrash(self, vActs):
        mnuItem = QAction("Empty Trash", self)
        mnuItem.triggered.connect(lambda: self._ctxSignal(
            nwItemAction.EMPTY_TRASH, None, None
        ))
        self.addAction(mnuItem)

    def _buildMenuSplit(self, vActs):
        mnuItem = QAction("Split File", self)
        mnuItem.triggered.connect(lambda: self._ctxSignal(
            nwItemAction.SPLIT, None, None
        ))
        self.addAction(mnuItem)

    def _buildMenuMerge(self, vActs):
        mnuItem = QAction("Merge Folder", self)
        mnuItem.triggered.connect(lambda: self._ctxSignal(
            nwItemAction.MERGE, None, None
        ))
        self.addAction(mnuItem)

    def _buildMenuMoveUp(self, vActs):
        mnuItem = QAction("Move Up", self)
        mnuItem.triggered.connect(lambda: self._ctxSignal(
            nwItemAction.MOVE_UP, None, None
        ))
        self.addAction(mnuItem)

    def _buildMenuMoveDown(self, vActs):
        mnuItem = QAction("Move Down", self)
        mnuItem.triggered.connect(lambda: self._ctxSignal(
            nwItemAction.MOVE_DOWN, None, None
        ))
        self.addAction(mnuItem)

    def _buildMenuMoveTrash(self, vActs):
        mnuItem = QAction("Move to Trash", self)
        mnuItem.triggered.connect(lambda: self._ctxSignal(
            nwItemAction.MOVE_TRASH, None, None
        ))
        self.addAction(mnuItem)

    def _buildMenuMoveTo(self, vActs):
        mnuItem = QAction("Move to", self)
        mnuItem.triggered.connect(lambda: self._ctxSignal(
            nwItemAction.MOVE_TO, None, None,
            None
        ))
        self.addAction(mnuItem)

    def _buildMenuAddFile(self, vActs):
        mnuItem = QAction("Add File", self)
        mnuItem.triggered.connect(lambda: self._ctxSignal(
            nwItemAction.ADD_FILE,
            vActs[nwItemAction.ADD_FILE]["Class"],
            nwItemType.FILE
        ))
        self.addAction(mnuItem)

    def _buildMenuAddFolder(self, vActs):
        mnuItem = QAction("Add Folder", self)
        mnuItem.triggered.connect(lambda: self._ctxSignal(
            nwItemAction.ADD_FOLDER,
            vActs[nwItemAction.ADD_FOLDER]["Class"],
            nwItemType.FOLDER
        ))
        self.addAction(mnuItem)

    def _buildMenuAddRoot(self, vActs):

        vClass  = vActs[nwItemAction.ADD_ROOT]["Class"]
        mnuItem = QMenu("Add Root Item", self)

        if nwItemClass.NOVEL in vClass:
            mnuSub = QAction("Novel", self)
            mnuSub.triggered.connect(lambda: self._ctxSignal(
                nwItemAction.ADD_ROOT,
                nwItemClass.NOVEL,
                nwItemType.ROOT
            ))
            mnuItem.addAction(mnuSub)

        if nwItemClass.CHARACTER in vClass:
            mnuSub = QAction("Characters", self)
            mnuSub.triggered.connect(lambda: self._ctxSignal(
                nwItemAction.ADD_ROOT,
                nwItemClass.CHARACTER,
                nwItemType.ROOT
            ))
            mnuItem.addAction(mnuSub)

        if nwItemClass.WORLD in vClass:
            mnuSub = QAction("Locations", self)
            mnuSub.triggered.connect(lambda: self._ctxSignal(
                nwItemAction.ADD_ROOT,
                nwItemClass.WORLD,
                nwItemType.ROOT
            ))
            mnuItem.addAction(mnuSub)

        if nwItemClass.TIMELINE in vClass:
            mnuSub = QAction("Timeline", self)
            mnuSub.triggered.connect(lambda: self._ctxSignal(
                nwItemAction.ADD_ROOT,
                nwItemClass.TIMELINE,
                nwItemType.ROOT
            ))
            mnuItem.addAction(mnuSub)

        if nwItemClass.OBJECT in vClass:
            mnuSub = QAction("Objects", self)
            mnuSub.triggered.connect(lambda: self._ctxSignal(
                nwItemAction.ADD_ROOT,
                nwItemClass.OBJECT,
                nwItemType.ROOT
            ))
            mnuItem.addAction(mnuSub)

        self.addMenu(mnuItem)
        return

    ##
    #  Menu Signal
    ##

    def _ctxSignal(self, theAction, theClass, theType, theTarget=None):
        self.selAction = theAction
        self.selClass  = theClass
        self.selType   = theType
        self.selTarget = theTarget
        return

# END Class GuiDocTreeCtx
