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

from PyQt5.QtWidgets import QAction, QMessageBox

from novelwriter.guimain import GuiMain
from novelwriter.gui.projtree import GuiProjectTree
from novelwriter.enum import nwItemType, nwItemClass


@pytest.mark.gui
def testGuiProjTree_NewItems(qtbot, caplog, monkeypatch, nwGUI, fncDir):
    """Test adding and removing items from the project tree.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "warning", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "critical", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "information", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(GuiMain, "editItem", lambda *a: None)

    nwTree = nwGUI.treeView

    # Try to add item with no project
    assert nwTree.newTreeItem(nwItemType.FILE) is False

    # Create a project
    nwGUI.theProject.projTree.setSeed(42)
    prjDir = os.path.join(fncDir, "project")
    assert nwGUI.newProject({"projPath": prjDir}) is True

    # No itemType set
    nwTree.clearSelection()
    assert nwTree.newTreeItem(None) is False

    # Root Items
    # ==========

    # No class set
    assert nwTree.newTreeItem(nwItemType.ROOT) is False

    # Create root item
    assert nwTree.newTreeItem(nwItemType.ROOT, nwItemClass.WORLD) is True
    assert "1a6562590ef19" in nwGUI.theProject.projTree

    # File/Folder Items
    # =================

    # No location selected for new item
    nwTree.clearSelection()
    caplog.clear()
    assert nwTree.newTreeItem(nwItemType.FILE) is False
    assert nwTree.newTreeItem(nwItemType.FOLDER) is False
    assert "Did not find anywhere" in caplog.text

    # Create new folder as child of Novel folder
    nwTree.setSelectedHandle("73475cb40a568")
    assert nwTree.newTreeItem(nwItemType.FOLDER) is True
    assert nwGUI.theProject.projTree["031b4af5197ec"].itemParent == "73475cb40a568"
    assert nwGUI.theProject.projTree["031b4af5197ec"].itemRoot == "73475cb40a568"
    assert nwGUI.theProject.projTree["031b4af5197ec"].itemClass == nwItemClass.NOVEL

    # Add a new file in the new folder
    nwTree.setSelectedHandle("031b4af5197ec")
    assert nwTree.newTreeItem(nwItemType.FILE) is True
    assert nwGUI.theProject.projTree["41cfc0d1f2d12"].itemParent == "031b4af5197ec"
    assert nwGUI.theProject.projTree["41cfc0d1f2d12"].itemRoot == "73475cb40a568"
    assert nwGUI.theProject.projTree["41cfc0d1f2d12"].itemClass == nwItemClass.NOVEL

    # Add a new file next to the other new file
    nwTree.setSelectedHandle("41cfc0d1f2d12")
    assert nwTree.newTreeItem(nwItemType.FILE) is True
    assert nwGUI.theProject.projTree["2858dcd1057d3"].itemParent == "031b4af5197ec"
    assert nwGUI.theProject.projTree["2858dcd1057d3"].itemRoot == "73475cb40a568"
    assert nwGUI.theProject.projTree["2858dcd1057d3"].itemClass == nwItemClass.NOVEL
    assert nwGUI.openDocument("2858dcd1057d3")
    assert nwGUI.docEditor.getText() == "### New Document\n\n"

    # Add a new file to the characters folder
    nwTree.setSelectedHandle("71ee45a3c0db9")
    assert nwTree.newTreeItem(nwItemType.FILE) is True
    assert nwGUI.theProject.projTree["2fca346db6561"].itemParent == "71ee45a3c0db9"
    assert nwGUI.theProject.projTree["2fca346db6561"].itemRoot == "71ee45a3c0db9"
    assert nwGUI.theProject.projTree["2fca346db6561"].itemClass == nwItemClass.CHARACTER
    assert nwGUI.openDocument("2fca346db6561")
    assert nwGUI.docEditor.getText() == "# New Note\n\n"

    # Make sure the sibling folder bug trap works
    nwTree.setSelectedHandle("2858dcd1057d3")
    nwGUI.theProject.projTree["2858dcd1057d3"].setParent(None)  # This should not happen
    caplog.clear()
    assert nwTree.newTreeItem(nwItemType.FILE) is False
    assert "Internal error" in caplog.text
    nwGUI.theProject.projTree["2858dcd1057d3"].setParent("031b4af5197ec")

    # Get the trash folder
    nwTree._addTrashRoot()
    trashHandle = nwGUI.theProject.trashFolder()
    nwTree.setSelectedHandle(trashHandle)
    assert nwTree.newTreeItem(nwItemType.FILE) is False
    assert "Cannot add new files or folders to the Trash folder" in caplog.text

    # Other Checks
    # ============

    # Also check error handling in reveal function
    assert nwTree.revealNewTreeItem("abc") is False

    # Add an item that cannot be displayed in the tree
    nHandle = nwGUI.theProject.newFile("Test", None)
    assert nwTree.revealNewTreeItem(nHandle) is False

    # Clean up
    # qtbot.stopForInteraction()
    nwGUI.closeProject()

# END Test testGuiProjTree_NewItems


@pytest.mark.gui
def testGuiProjTree_MoveItems(qtbot, monkeypatch, nwGUI, fncDir):
    """Test adding and removing items from the project tree.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "warning", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "critical", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "information", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(GuiMain, "editItem", lambda *a: None)

    nwTree = nwGUI.treeView

    # Try to move item with no project
    assert nwTree.moveTreeItem(1) is False

    # Create a project
    nwGUI.theProject.projTree.setSeed(42)
    prjDir = os.path.join(fncDir, "project")
    assert nwGUI.newProject({"projPath": prjDir}) is True

    # Move Documents
    # ==============

    # Add some files
    nwTree.setSelectedHandle("31489056e0916")
    assert nwTree.newTreeItem(nwItemType.FILE) is True
    assert nwTree.newTreeItem(nwItemType.FILE) is True
    assert nwTree.newTreeItem(nwItemType.FILE) is True
    assert nwTree.getTreeFromHandle("31489056e0916") == [
        "31489056e0916", "98010bd9270f9", "0e17daca5f3e1",
        "1a6562590ef19", "031b4af5197ec", "41cfc0d1f2d12",
    ]

    # Move item without focus
    monkeypatch.setattr(GuiProjectTree, "hasFocus", lambda *a: False)
    assert nwTree.moveTreeItem(1) is False
    assert nwTree.getTreeFromHandle("31489056e0916") == [
        "31489056e0916", "98010bd9270f9", "0e17daca5f3e1",
        "1a6562590ef19", "031b4af5197ec", "41cfc0d1f2d12",
    ]
    monkeypatch.setattr(GuiProjectTree, "hasFocus", lambda *a: True)

    # Move with no selections
    nwTree.clearSelection()
    assert nwTree.moveTreeItem(1) is False

    # Move second item up twice (should give same result)
    nwTree.setSelectedHandle("0e17daca5f3e1")
    assert nwTree.moveTreeItem(-1) is True
    assert nwTree.getTreeFromHandle("31489056e0916") == [
        "31489056e0916", "0e17daca5f3e1", "98010bd9270f9",
        "1a6562590ef19", "031b4af5197ec", "41cfc0d1f2d12",
    ]
    assert nwTree.moveTreeItem(-1) is False
    assert nwTree.getTreeFromHandle("31489056e0916") == [
        "31489056e0916", "0e17daca5f3e1", "98010bd9270f9",
        "1a6562590ef19", "031b4af5197ec", "41cfc0d1f2d12",
    ]

    # Restore via menu entry
    nwGUI.mainMenu.aMoveDown.activate(QAction.Trigger)
    assert nwTree.getTreeFromHandle("31489056e0916") == [
        "31489056e0916", "98010bd9270f9", "0e17daca5f3e1",
        "1a6562590ef19", "031b4af5197ec", "41cfc0d1f2d12",
    ]

    # Move fifth item down twice (should give same result)
    nwTree.setSelectedHandle("031b4af5197ec")
    assert nwTree.moveTreeItem(1) is True
    assert nwTree.getTreeFromHandle("31489056e0916") == [
        "31489056e0916", "98010bd9270f9", "0e17daca5f3e1",
        "1a6562590ef19", "41cfc0d1f2d12", "031b4af5197ec",
    ]
    assert nwTree.moveTreeItem(1) is False
    assert nwTree.getTreeFromHandle("31489056e0916") == [
        "31489056e0916", "98010bd9270f9", "0e17daca5f3e1",
        "1a6562590ef19", "41cfc0d1f2d12", "031b4af5197ec",
    ]

    # Restore via menu entry
    nwGUI.mainMenu.aMoveUp.activate(QAction.Trigger)
    assert nwTree.getTreeFromHandle("31489056e0916") == [
        "31489056e0916", "98010bd9270f9", "0e17daca5f3e1",
        "1a6562590ef19", "031b4af5197ec", "41cfc0d1f2d12",
    ]

    # Move down again, and restore via undo
    nwTree.setSelectedHandle("031b4af5197ec")
    assert nwTree.moveTreeItem(1) is True
    assert nwTree.getTreeFromHandle("31489056e0916") == [
        "31489056e0916", "98010bd9270f9", "0e17daca5f3e1",
        "1a6562590ef19", "41cfc0d1f2d12", "031b4af5197ec",
    ]
    nwGUI.mainMenu.aMoveUndo.activate(QAction.Trigger)
    assert nwTree.getTreeFromHandle("31489056e0916") == [
        "31489056e0916", "98010bd9270f9", "0e17daca5f3e1",
        "1a6562590ef19", "031b4af5197ec", "41cfc0d1f2d12",
    ]

    # Root Folder
    # ===========

    nwTree.setSelectedHandle("73475cb40a568")
    assert nwGUI.theProject.projTree._treeOrder.index("73475cb40a568") == 0

    # Move novel folder up
    assert nwTree.moveTreeItem(-1) is False
    nwTree.flushTreeOrder()
    assert nwGUI.theProject.projTree._treeOrder.index("73475cb40a568") == 0

    # Move novel folder down
    assert nwTree.moveTreeItem(1) is True
    nwTree.flushTreeOrder()
    assert nwGUI.theProject.projTree._treeOrder.index("73475cb40a568") == 1

    # Move novel folder up again
    assert nwTree.moveTreeItem(-1) is True
    nwTree.flushTreeOrder()
    assert nwGUI.theProject.projTree._treeOrder.index("73475cb40a568") == 0

    # Clean up
    # qtbot.stopForInteraction()
    nwGUI.closeProject()

# END Test testGuiProjTree_MoveItems


@pytest.mark.gui
def testGuiProjTree_DeleteItems(qtbot, caplog, monkeypatch, nwGUI, fncDir):
    """Test adding and removing items from the project tree.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "warning", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "critical", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "question", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(QMessageBox, "information", lambda *a: QMessageBox.Yes)
    monkeypatch.setattr(GuiMain, "editItem", lambda *a: None)

    nwTree = nwGUI.treeView

    # Try to run with no project
    assert nwTree.emptyTrash() is False
    assert nwTree.deleteItem() is False

    # Create a project
    nwGUI.theProject.projTree.setSeed(42)
    prjDir = os.path.join(fncDir, "project")
    assert nwGUI.newProject({"projPath": prjDir}) is True

    # Try emptying the trash already now, when there is no trash folder
    assert nwTree.emptyTrash() is False

    # Add some files
    nwTree.setSelectedHandle("31489056e0916")
    assert nwTree.newTreeItem(nwItemType.FILE) is True
    assert nwTree.newTreeItem(nwItemType.FILE) is True
    assert nwTree.newTreeItem(nwItemType.FILE) is True
    assert nwTree.getTreeFromHandle("31489056e0916") == [
        "31489056e0916", "98010bd9270f9", "0e17daca5f3e1",
        "1a6562590ef19", "031b4af5197ec", "41cfc0d1f2d12",
    ]

    # Delete File
    # ===========

    # Delete item without focus -> blocked
    monkeypatch.setattr(GuiProjectTree, "hasFocus", lambda *a: False)
    nwTree.setSelectedHandle("41cfc0d1f2d12")
    caplog.clear()
    assert nwTree.deleteItem() is False
    assert "blocked" in caplog.text
    monkeypatch.setattr(GuiProjectTree, "hasFocus", lambda *a: True)

    # No selection made
    nwTree.clearSelection()
    caplog.clear()
    assert nwTree.deleteItem() is False
    assert "no item to delete" in caplog.text

    # Not a valid handle
    nwTree.clearSelection()
    caplog.clear()
    assert nwTree.deleteItem("0000000000000") is False
    assert "Could not find tree item" in caplog.text

    # Block adding trash folder
    funcPointer = nwTree._addTrashRoot
    nwTree._addTrashRoot = lambda *a: None
    assert nwTree.deleteItem("41cfc0d1f2d12") is False
    nwTree._addTrashRoot = funcPointer

    # Delete last two documents, which also adds the trash folder
    assert nwTree.deleteItem("41cfc0d1f2d12") is True
    assert nwTree.deleteItem("031b4af5197ec") is True
    assert nwTree.getTreeFromHandle("31489056e0916") == [
        "31489056e0916", "98010bd9270f9", "0e17daca5f3e1",
        "1a6562590ef19"
    ]
    trashHandle = nwGUI.theProject.projTree.trashRoot()
    assert nwTree.getTreeFromHandle(trashHandle) == [
        trashHandle, "41cfc0d1f2d12", "031b4af5197ec"
    ]

    # Delete the first file again (permanent), and ask for permission
    # Also open the document in the editor, which should trigger a close
    assert os.path.isfile(os.path.join(prjDir, "content", "41cfc0d1f2d12.nwd"))
    assert "41cfc0d1f2d12" in nwGUI.theProject.projTree
    assert nwGUI.docEditor.docHandle() is None
    assert nwGUI.openDocument("41cfc0d1f2d12") is True
    assert nwGUI.docEditor.docHandle() == "41cfc0d1f2d12"
    assert nwTree.deleteItem("41cfc0d1f2d12") is True
    assert nwGUI.docEditor.docHandle() is None
    assert not os.path.isfile(os.path.join(prjDir, "content", "41cfc0d1f2d12.nwd"))
    assert "41cfc0d1f2d12" not in nwGUI.theProject.projTree
    assert nwTree.getTreeFromHandle(trashHandle) == [
        trashHandle, "031b4af5197ec"
    ]

    # Try to delete the second document, but block the deletion
    with monkeypatch.context() as mp:
        mp.setattr("novelwriter.core.document.NWDoc.deleteDocument", lambda *a: False)
        assert nwTree.deleteItem("031b4af5197ec") is False

    # Delete proper, and skip asking for permission
    assert os.path.isfile(os.path.join(prjDir, "content", "031b4af5197ec.nwd"))
    assert "031b4af5197ec" in nwGUI.theProject.projTree
    assert nwTree.deleteItem("031b4af5197ec", alreadyAsked=True) is True
    assert not os.path.isfile(os.path.join(prjDir, "content", "031b4af5197ec.nwd"))
    assert "031b4af5197ec" not in nwGUI.theProject.projTree
    assert nwTree.getTreeFromHandle(trashHandle) == [trashHandle]

    # Delete Folder/Root
    # ==================

    # Deleting non-empty folders is blocked
    assert nwTree.deleteItem("31489056e0916") is False  # Folder
    assert nwTree.deleteItem("73475cb40a568") is False  # Root

    # Add a folder we can delete
    nwTree.setSelectedHandle("71ee45a3c0db9")  # Character Root
    assert nwTree.newTreeItem(nwItemType.FOLDER) is True
    assert "2fca346db6561" in nwGUI.theProject.projTree

    # Try to delete, but block parent item lookup
    with monkeypatch.context() as mp:
        mp.setattr("PyQt5.QtWidgets.QTreeWidgetItem.parent", lambda *a: None)
        caplog.clear()
        assert nwTree.deleteItem("2fca346db6561") is False
        assert "Could not delete folder" in caplog.text
        assert "2fca346db6561" in nwGUI.theProject.projTree

    # Delete folder properly
    assert nwTree.deleteItem("2fca346db6561") is True
    assert "2fca346db6561" not in nwGUI.theProject.projTree

    # Delete the Character root
    assert nwTree.deleteItem("71ee45a3c0db9") is True
    assert "71ee45a3c0db9" not in nwGUI.theProject.projTree

    # Empty Trash
    # ===========

    # Try to empty trash that is already empty
    caplog.clear()
    assert nwTree.getTreeFromHandle(trashHandle) == [trashHandle]
    assert nwTree.emptyTrash() is False
    assert "already empty" in caplog.text

    # Move the two remaining scene documents to trash
    assert nwTree.deleteItem("0e17daca5f3e1") is True
    assert nwTree.deleteItem("1a6562590ef19") is True
    assert nwTree.getTreeFromHandle("31489056e0916") == [
        "31489056e0916", "98010bd9270f9"
    ]
    assert nwTree.getTreeFromHandle(trashHandle) == [
        trashHandle, "0e17daca5f3e1", "1a6562590ef19"
    ]

    # Empty trash, but select no on question
    with monkeypatch.context() as mp:
        mp.setattr(QMessageBox, "question", lambda *a: QMessageBox.No)
        assert nwTree.emptyTrash() is False

    # Empty the trash proper
    nwTree._setTreeChanged(False)
    assert nwTree.emptyTrash() is True
    assert nwTree.getTreeFromHandle(trashHandle) == [trashHandle]
    assert nwTree._treeChanged is True

    # Clean up
    # qtbot.stopForInteraction()
    nwGUI.closeProject()

# END Test testGuiProjTree_DeleteItems
