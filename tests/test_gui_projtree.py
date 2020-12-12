# -*- coding: utf-8 -*-
"""novelWriter Main GUI Project Tree Class Tester
"""

import pytest
import os

from PyQt5.QtCore import QItemSelectionModel
from PyQt5.QtWidgets import QAction, QMessageBox

from nw.constants import nwItemType, nwItemClass

keyDelay = 2
typeDelay = 1
stepDelay = 20

@pytest.mark.gui
def testGuiProjTree_Main(qtbot, monkeypatch, nwGUI, nwMinimal):
    """Test the project tree.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "question", lambda *args: QMessageBox.Yes)

    nwGUI.theProject.projTree.setSeed(42)
    assert nwGUI.openProject(nwMinimal)
    nwTree = nwGUI.treeView

    # No location selected for new item
    assert not nwTree.newTreeItem(nwItemType.FILE, None)
    assert not nwTree.newTreeItem(nwItemType.FOLDER, None)

    # Select a location
    chItem = nwTree._getTreeItem("a6d311a93600a")
    nwTree.setCurrentItem(chItem, QItemSelectionModel.Current)
    chItem.setExpanded(True)

    # Create new item with no class set
    assert nwTree.newTreeItem(nwItemType.FILE, None)
    assert nwTree.newTreeItem(nwItemType.FOLDER, None)

    # Add roots
    assert not nwTree.newTreeItem(nwItemType.ROOT, None)              # Defaults to NOVEL
    assert not nwTree.newTreeItem(nwItemType.ROOT, nwItemClass.WORLD) # Duplicate
    assert nwTree.newTreeItem(nwItemType.ROOT, nwItemClass.CUSTOM)    # Valid

    # Check that we have the correct tree order
    assert nwTree.getTreeFromHandle("a6d311a93600a") == [
        "a6d311a93600a", "f5ab3e30151e1", "8c659a11cd429", "73475cb40a568", "44cb730c42048"
    ]

    # Move second item up twice (should give same result)
    nwTree.setSelectedHandle("8c659a11cd429")
    nwGUI.mainMenu.aMoveUp.activate(QAction.Trigger)
    assert nwTree.getTreeFromHandle("a6d311a93600a") == [
        "a6d311a93600a", "8c659a11cd429", "f5ab3e30151e1", "73475cb40a568", "44cb730c42048"
    ]
    nwGUI.mainMenu.aMoveUp.activate(QAction.Trigger)
    assert nwTree.getTreeFromHandle("a6d311a93600a") == [
        "a6d311a93600a", "8c659a11cd429", "f5ab3e30151e1", "73475cb40a568", "44cb730c42048"
    ]

    # Move it back down four times (last to should be the same)
    nwGUI.mainMenu.aMoveDown.activate(QAction.Trigger)
    assert nwTree.getTreeFromHandle("a6d311a93600a") == [
        "a6d311a93600a", "f5ab3e30151e1", "8c659a11cd429", "73475cb40a568", "44cb730c42048"
    ]
    nwGUI.mainMenu.aMoveDown.activate(QAction.Trigger)
    assert nwTree.getTreeFromHandle("a6d311a93600a") == [
        "a6d311a93600a", "f5ab3e30151e1", "73475cb40a568", "8c659a11cd429", "44cb730c42048"
    ]
    nwGUI.mainMenu.aMoveDown.activate(QAction.Trigger)
    assert nwTree.getTreeFromHandle("a6d311a93600a") == [
        "a6d311a93600a", "f5ab3e30151e1", "73475cb40a568", "44cb730c42048", "8c659a11cd429"
    ]
    nwGUI.mainMenu.aMoveDown.activate(QAction.Trigger)
    assert nwTree.getTreeFromHandle("a6d311a93600a") == [
        "a6d311a93600a", "f5ab3e30151e1", "73475cb40a568", "44cb730c42048", "8c659a11cd429"
    ]

    # Move a root item (top level items are different) twice
    nwTree.flushTreeOrder()
    assert nwGUI.theProject.projTree._treeOrder.index("9d5247ab588e0") == 9
    nwTree.setSelectedHandle("9d5247ab588e0")

    nwGUI.mainMenu.aMoveDown.activate(QAction.Trigger)
    nwTree.flushTreeOrder()
    assert nwGUI.theProject.projTree._treeOrder.index("9d5247ab588e0") == 10

    nwGUI.mainMenu.aMoveDown.activate(QAction.Trigger)
    nwTree.flushTreeOrder()
    assert nwGUI.theProject.projTree._treeOrder.index("9d5247ab588e0") == 10

    # Add some content to the new file
    nwGUI.openDocument("73475cb40a568")
    nwGUI.docEditor.setText("# Hello World\n")
    nwGUI.saveDocument()
    assert os.path.isfile(os.path.join(nwMinimal, "content", "73475cb40a568.nwd"))

    # Delete the items we added earlier
    nwTree.clearSelection()
    assert not nwTree.emptyTrash() # No folder yet
    assert not nwTree.deleteItem(None)
    assert not nwTree.deleteItem("1111111111111")
    assert nwTree.deleteItem("73475cb40a568") # New File
    assert nwTree.deleteItem("44cb730c42048") # New Folder
    assert nwTree.deleteItem("71ee45a3c0db9") # Custom Root
    assert "73475cb40a568" in nwGUI.theProject.projTree._treeOrder
    assert "44cb730c42048" not in nwGUI.theProject.projTree._treeOrder
    assert "71ee45a3c0db9" not in nwGUI.theProject.projTree._treeOrder

    # The file is in trash, empty it
    assert os.path.isfile(os.path.join(nwMinimal, "content", "73475cb40a568.nwd"))
    assert nwTree.emptyTrash()
    assert not nwTree.emptyTrash() # Already empty
    assert not os.path.isfile(os.path.join(nwMinimal, "content", "73475cb40a568.nwd"))
    assert "73475cb40a568" not in nwGUI.theProject.projTree._treeOrder

    # Close the project
    nwGUI.closeProject()

    # Add an orphaned file
    orphFile = os.path.join(nwMinimal, "content", "1234567890abc.nwd")
    with open(orphFile, mode="w+", encoding="utf8") as outFile:
        outFile.write("# Hello World\n")

    # Open the project again
    nwGUI.openProject(nwMinimal)

    # Check that the orphaned file was found and added to the tree
    assert nwTree.orphRoot is not None
    nwTree.flushTreeOrder()
    assert "1234567890abc" not in nwGUI.theProject.projTree._treeOrder
    orItem = nwTree._getTreeItem("1234567890abc")
    assert orItem.text(nwTree.C_NAME) == "Orphaned File 1"

    # qtbot.stopForInteraction()

# END Test testGuiProjTree_Main
