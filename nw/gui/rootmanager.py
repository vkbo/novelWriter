# -*- coding: utf-8 -*-
"""novelWriter GUI Root Manager

 novelWriter – GUI Root Manager
================================
 Dialog to manage root folders

 File History:
 Created: 2020-12-18 [1.1a0]

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

import nw
import logging

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import (
    QDialog, QHBoxLayout, QVBoxLayout, QDialogButtonBox, QLabel, QListWidget,
    QListWidgetItem, QAbstractItemView, QPushButton
)
from nw.constants import nwItemType, nwItemClass, nwLabels

logger = logging.getLogger(__name__)

class GuiRootManager(QDialog):

    def __init__(self, theParent, theProject):
        QDialog.__init__(self, theParent)

        logger.debug("Initialising GuiRootManager ...")
        self.setObjectName("GuiRootManager")

        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theProject = theProject
        self.theTheme   = theParent.theTheme

        self.rootOrder = []
        self.rootState = {}
        self.newRoots  = []
        self.delRoots  = []

        iPx = self.theTheme.baseIconSize
        mSp = self.mainConf.pxInt(16)
        iSp = self.mainConf.pxInt(4)

        self.setWindowTitle("Manage Root Folders")
        self.setMinimumWidth(self.mainConf.pxInt(600))
        self.setMinimumHeight(self.mainConf.pxInt(400))

        # Root Folder Lists
        self.projRoots = QListWidget()
        self.projRoots.setIconSize(QSize(iPx, iPx))
        self.projRoots.setDragEnabled(True)
        self.projRoots.setDragDropMode(QAbstractItemView.InternalMove)

        self.availRoots = QListWidget()
        self.availRoots.setIconSize(QSize(iPx, iPx))

        # Action Buttons
        self.addRoot = QPushButton()
        self.addRoot.setIcon(self.theTheme.getIcon("backward"))
        self.addRoot.clicked.connect(self._addRootFolder)

        self.removeRoot = QPushButton()
        self.removeRoot.setIcon(self.theTheme.getIcon("forward"))
        self.removeRoot.clicked.connect(self._removeRootFolder)

        self.moveUp = QPushButton()
        self.moveUp.setIcon(self.theTheme.getIcon("up"))
        self.moveUp.clicked.connect(lambda: self._moveProjRoot(-1))

        self.moveDown = QPushButton()
        self.moveDown.setIcon(self.theTheme.getIcon("down"))
        self.moveDown.clicked.connect(lambda: self._moveProjRoot(+1))

        # OK Button
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self._doSave)
        self.buttonBox.rejected.connect(self._doClose)

        self.projBox = QVBoxLayout()
        self.projBox.setSpacing(iSp)
        self.projBox.addWidget(QLabel("Current"))
        self.projBox.addWidget(self.projRoots)

        self.actionBox = QVBoxLayout()
        self.actionBox.setSpacing(iSp)
        self.actionBox.addStretch(1)
        self.actionBox.addWidget(self.addRoot)
        self.actionBox.addWidget(self.removeRoot)
        self.actionBox.addSpacing(mSp)
        self.actionBox.addWidget(self.moveUp)
        self.actionBox.addWidget(self.moveDown)
        self.actionBox.addStretch(1)

        self.availBox = QVBoxLayout()
        self.availBox.setSpacing(iSp)
        self.availBox.addWidget(QLabel("Available"))
        self.availBox.addWidget(self.availRoots)

        self.innerBox = QHBoxLayout()
        self.innerBox.setSpacing(mSp)
        self.innerBox.addLayout(self.projBox)
        self.innerBox.addLayout(self.actionBox)
        self.innerBox.addLayout(self.availBox)

        self.outerBox = QVBoxLayout()
        self.outerBox.addLayout(self.innerBox)
        self.outerBox.addWidget(self.buttonBox)
        self.setLayout(self.outerBox)

        self._populateGUI()

        logger.debug("GuiRootManager initialisation complete")

        return

    ##
    #  Slots
    ##

    def _addRootFolder(self):
        """Add a root folder to the project.
        """
        aItem = self.availRoots.currentItem()
        aClass = aItem.data(Qt.UserRole)
        self._appendProjRoot(
            nwLabels.CLASS_NAME[aClass], aClass, None
        )
        if aClass != nwItemClass.CUSTOM:
            self.availRoots.takeItem(self.availRoots.currentRow())

        return

    def _removeRootFolder(self):
        """Remove a root folder from the project.
        """
        pItem = self.projRoots.currentItem()
        pHandle, pClass = pItem.data(Qt.UserRole)
        if self.rootState.get(pHandle, False):
            return

        self.projRoots.takeItem(self.projRoots.currentRow())
        if pClass != nwItemClass.CUSTOM:
            self._appendAvailRoot(pClass)

        return

    def _moveProjRoot(self, nStep):
        """Move a root folder up or down.
        """
        tIndex = self.projRoots.currentRow()
        nChild = self.projRoots.count()
        nIndex = tIndex + nStep
        if nIndex < 0 or nIndex >= nChild:
            return

        cItem = self.projRoots.takeItem(tIndex)
        self.projRoots.insertItem(nIndex, cItem)
        self.projRoots.setCurrentRow(nIndex)

        return

    def _doSave(self):
        """Accept the changes.
        """
        self.newRoots = []
        remainRoots = []
        for i in range(self.projRoots.count()):
            rItem = self.projRoots.item(i)
            rTuple = rItem.data(Qt.UserRole)
            self.newRoots.append(rTuple)
            if rTuple[0] is not None:
                remainRoots.append(rTuple[0])

        self.delRoots = []
        for tHandle in self.rootOrder:
            if tHandle not in remainRoots:
                self.delRoots.append(tHandle)

        self.accept()

        return

    def _doClose(self):
        """Reject the changes.
        """
        self.newRoots = []
        self.reject()
        return

    ##
    #  Internal Functions
    ##

    def _populateGUI(self):
        """Load the values and populate the GUI.
        """
        self.rootOrder = []
        self.rootState = {}

        self.theParent.treeView.flushTreeOrder()

        for tItem in self.theProject.projTree:
            if tItem is None:
                continue

            tHandle = tItem.itemHandle
            if tItem.itemType == nwItemType.ROOT:
                self.rootOrder.append(tHandle)
                self.rootState[tHandle] = False
                self._appendProjRoot(tItem.itemName, tItem.itemClass, tHandle)
            else:
                if tItem.itemParent in self.rootOrder:
                    self.rootState[tItem.itemParent] = True

        for itemClass in nwLabels.CLASS_NAME:
            if itemClass in (nwItemClass.NO_CLASS, nwItemClass.TRASH):
                continue
            if self.theProject.projTree.checkRootUnique(itemClass):
                self._appendAvailRoot(itemClass)

        if self.projRoots.count() > 0:
            self.projRoots.setCurrentRow(0)

        if self.availRoots.count() > 0:
            self.availRoots.setCurrentRow(0)

        return

    def _appendProjRoot(self, itemLabel, itemClass, itemHandle=None):
        """Append an item to the project roots list.
        """
        className = nwLabels.CLASS_NAME[itemClass]
        classIcon = nwLabels.CLASS_ICON[itemClass]

        newItem = QListWidgetItem()
        if itemLabel == className:
            newItem.setText(itemLabel)
        else:
            newItem.setText(f"{className} [{itemLabel}]")
        newItem.setIcon(self.theTheme.getIcon(classIcon))
        newItem.setData(Qt.UserRole, (itemHandle, itemClass))
        self.projRoots.addItem(newItem)

        return

    def _appendAvailRoot(self, itemClass):
        """Append an item to the available roots list.
        """
        className = nwLabels.CLASS_NAME[itemClass]
        classIcon = nwLabels.CLASS_ICON[itemClass]

        newItem = QListWidgetItem()
        newItem.setText(className)
        newItem.setIcon(self.theTheme.getIcon(classIcon))
        newItem.setData(Qt.UserRole, itemClass)
        self.availRoots.addItem(newItem)

        return

# END Class GuiRootManager
