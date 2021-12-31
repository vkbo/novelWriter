"""
novelWriter – Main GUI Project Tree Class Tester
================================================

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

import pytest
import os

from tools import writeFile

from PyQt5.QtCore import QItemSelectionModel
from PyQt5.QtWidgets import QAction, QMessageBox

from novelwriter.guimain import GuiMain
from novelwriter.gui.projtree import GuiProjectTree
from novelwriter.enum import nwItemType, nwItemClass


@pytest.mark.gui
def testGuiProjTree_TreeItems(qtbot, caplog, monkeypatch, nwGUI, nwMinimal):
    """Test adding and removing items from the project tree.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "critical", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "warning", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "information", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(GuiMain, "editItem", lambda *a: None)

    nwGUI.theProject.projTree.setSeed(42)
    nwTree = nwGUI.treeView

    ##
    #  Add New Items
    ##

    # Try to add and move item with no project
    assert not nwTree.newTreeItem(nwItemType.FILE, None)
    assert not nwTree.moveTreeItem(1)

    # Open a project
    assert nwGUI.openProject(nwMinimal)

    # No location selected for new item
    nwTree.clearSelection()
    assert not nwTree.newTreeItem(nwItemType.FILE, None)
    assert not nwTree.newTreeItem(nwItemType.FOLDER, None)
    assert nwTree.newTreeItem(nwItemType.FILE, nwItemClass.NOVEL)

    # No itemType set or ROOT, but no class
    assert not nwTree.newTreeItem(None, None)
    assert not nwTree.newTreeItem(nwItemType.ROOT, None)

    # Select a location
    chItem = nwTree._getTreeItem("a6d311a93600a")
    nwTree.setCurrentItem(chItem, QItemSelectionModel.Current)
    chItem.setExpanded(True)

    # Create new item with no class set (defaults to NOVEL)
    assert nwTree.newTreeItem(nwItemType.FILE, None)
    assert nwTree.newTreeItem(nwItemType.FOLDER, None)

    # Check that we have the correct tree order
    assert nwTree.getTreeFromHandle("a6d311a93600a") == [
        "a6d311a93600a", "f5ab3e30151e1", "8c659a11cd429", "44cb730c42048", "71ee45a3c0db9"
    ]

    # Add roots
    assert not nwTree.newTreeItem(nwItemType.ROOT, nwItemClass.WORLD)  # Duplicate
    assert nwTree.newTreeItem(nwItemType.ROOT, nwItemClass.CUSTOM)     # Valid

    # Change max depth and try to add a subfolder that is too deep
    monkeypatch.setattr("novelwriter.constants.nwConst.MAX_DEPTH", 2)
    chItem = nwTree._getTreeItem("71ee45a3c0db9")
    nwTree.setCurrentItem(chItem, QItemSelectionModel.Current)
    assert not nwTree.newTreeItem(nwItemType.FOLDER, None)

    ##
    #  Move Items
    ##

    nwTree.setSelectedHandle("8c659a11cd429")

    # Shift focus and try to move item
    monkeypatch.setattr(GuiProjectTree, "hasFocus", lambda *a: False)
    assert not nwTree.moveTreeItem(1)
    assert nwTree.getTreeFromHandle("a6d311a93600a") == [
        "a6d311a93600a", "f5ab3e30151e1", "8c659a11cd429", "44cb730c42048", "71ee45a3c0db9"
    ]
    monkeypatch.setattr(GuiProjectTree, "hasFocus", lambda *a: True)

    # Move second item up twice (should give same result)
    nwGUI.mainMenu.aMoveUp.activate(QAction.Trigger)
    assert nwTree.getTreeFromHandle("a6d311a93600a") == [
        "a6d311a93600a", "8c659a11cd429", "f5ab3e30151e1", "44cb730c42048", "71ee45a3c0db9"
    ]
    nwGUI.mainMenu.aMoveUp.activate(QAction.Trigger)
    assert nwTree.getTreeFromHandle("a6d311a93600a") == [
        "a6d311a93600a", "8c659a11cd429", "f5ab3e30151e1", "44cb730c42048", "71ee45a3c0db9"
    ]

    # Move it back down four times (last two should be the same)
    nwGUI.mainMenu.aMoveDown.activate(QAction.Trigger)
    assert nwTree.getTreeFromHandle("a6d311a93600a") == [
        "a6d311a93600a", "f5ab3e30151e1", "8c659a11cd429", "44cb730c42048", "71ee45a3c0db9"
    ]
    nwGUI.mainMenu.aMoveDown.activate(QAction.Trigger)
    assert nwTree.getTreeFromHandle("a6d311a93600a") == [
        "a6d311a93600a", "f5ab3e30151e1", "44cb730c42048", "8c659a11cd429", "71ee45a3c0db9"
    ]
    nwGUI.mainMenu.aMoveDown.activate(QAction.Trigger)
    assert nwTree.getTreeFromHandle("a6d311a93600a") == [
        "a6d311a93600a", "f5ab3e30151e1", "44cb730c42048", "71ee45a3c0db9", "8c659a11cd429"
    ]
    nwGUI.mainMenu.aMoveDown.activate(QAction.Trigger)
    assert nwTree.getTreeFromHandle("a6d311a93600a") == [
        "a6d311a93600a", "f5ab3e30151e1", "44cb730c42048", "71ee45a3c0db9", "8c659a11cd429"
    ]

    # Move up twice, and undo
    nwTree._lastMove = {}
    nwGUI.mainMenu.aMoveUp.activate(QAction.Trigger)
    nwGUI.mainMenu.aMoveUp.activate(QAction.Trigger)
    nwGUI.mainMenu.aMoveUndo.activate(QAction.Trigger)
    assert nwTree.getTreeFromHandle("a6d311a93600a") == [
        "a6d311a93600a", "f5ab3e30151e1", "44cb730c42048", "71ee45a3c0db9", "8c659a11cd429"
    ]

    # Move a root item (top level items are different) twice
    nwTree.flushTreeOrder()
    assert nwGUI.theProject.projTree._treeOrder.index("9d5247ab588e0") == 10
    nwTree.setSelectedHandle("9d5247ab588e0")

    nwGUI.mainMenu.aMoveDown.activate(QAction.Trigger)
    nwTree.flushTreeOrder()
    assert nwGUI.theProject.projTree._treeOrder.index("9d5247ab588e0") == 11

    nwGUI.mainMenu.aMoveDown.activate(QAction.Trigger)
    nwTree.flushTreeOrder()
    assert nwGUI.theProject.projTree._treeOrder.index("9d5247ab588e0") == 11

    ##
    #  Delete and Trash
    ##

    # Add some content to the new file
    nwGUI.openDocument("73475cb40a568")
    nwGUI.docEditor.setText("# Hello World\n")
    nwGUI.saveDocument()
    nwGUI.saveProject()
    assert os.path.isfile(os.path.join(nwMinimal, "content", "73475cb40a568.nwd"))

    # Delete the items we added earlier
    nwTree.clearSelection()
    assert not nwTree.emptyTrash()  # No folder yet
    assert not nwTree.deleteItem(None)
    assert not nwTree.deleteItem("1111111111111")
    assert nwTree.deleteItem("73475cb40a568")  # New File
    assert nwTree.deleteItem("71ee45a3c0db9")  # New Folder
    assert nwTree.deleteItem("811786ad1ae74")  # Custom Root
    assert "73475cb40a568" in nwGUI.theProject.projTree._treeOrder
    assert "71ee45a3c0db9" not in nwGUI.theProject.projTree._treeOrder
    assert "811786ad1ae74" not in nwGUI.theProject.projTree._treeOrder

    # The file is in trash, empty it
    assert os.path.isfile(os.path.join(nwMinimal, "content", "73475cb40a568.nwd"))
    assert nwTree.emptyTrash()
    assert not nwTree.emptyTrash()  # Already empty
    assert not os.path.isfile(os.path.join(nwMinimal, "content", "73475cb40a568.nwd"))
    assert "73475cb40a568" not in nwGUI.theProject.projTree._treeOrder

    # Should not be allowed to add files and folders to Trash
    trashHandle = nwGUI.theProject.projTree.trashRoot()
    chItem = nwTree._getTreeItem(trashHandle)
    nwTree.setCurrentItem(chItem, QItemSelectionModel.Current)
    assert not nwTree.newTreeItem(nwItemType.FILE, None)
    assert not nwTree.newTreeItem(nwItemType.FOLDER, None)

    # Close the project
    nwGUI.closeProject()

    ##
    #  Orphaned Files
    ##

    # Add an orphaned file
    orphFile = os.path.join(nwMinimal, "content", "1234567890abc.nwd")
    writeFile(orphFile, "# Hello World\n")

    # Open the project again
    nwGUI.openProject(nwMinimal)

    # Check that the orphaned file was found and added to the tree
    nwTree.flushTreeOrder()
    assert "1234567890abc" in nwGUI.theProject.projTree._treeOrder
    orItem = nwTree._getTreeItem("1234567890abc")
    assert orItem.text(nwTree.C_NAME) == "Recovered File 1"

    ##
    #  Unexpected Error Handling
    ##

    # Add an item with an invalid type
    assert not nwTree.newTreeItem(nwItemType.NO_TYPE, nwItemClass.NOVEL)
    assert "Failed to add new item" in caplog.messages[-1]

    # Add new file after one that has no parent handle
    chItem = nwTree._getTreeItem("44cb730c42048")
    nwTree.setCurrentItem(chItem, QItemSelectionModel.Current)
    nwTree.theProject.projTree["44cb730c42048"]._parent = None
    assert not nwTree.newTreeItem(nwItemType.FILE, nwItemClass.NOVEL)
    nwTree.clearSelection()

    # Add a file with no parent, and fail to find a suitable parent item
    monkeypatch.setattr("novelwriter.core.tree.NWTree.findRoot", lambda *a: None)

    assert not nwTree.newTreeItem(nwItemType.FILE, nwItemClass.NOVEL)
    assert not nwTree.newTreeItem(nwItemType.FOLDER, nwItemClass.NOVEL)

    # qtbot.stopForInteraction()
    nwGUI.closeProject()

# END Test testGuiProjTree_TreeItems
