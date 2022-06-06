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

from tools import buildTestProject

from PyQt5.QtWidgets import QAction, QMessageBox

from novelwriter.guimain import GuiMain
from novelwriter.gui.projtree import GuiProjectTree
from novelwriter.enum import nwItemType, nwItemClass


@pytest.mark.gui
def testGuiProjTree_NewItems(qtbot, caplog, monkeypatch, nwGUI, fncDir, mockRnd):
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
    prjDir = os.path.join(fncDir, "project")
    buildTestProject(nwGUI, prjDir)

    # No itemType set
    nwTree.projTree.clearSelection()
    assert nwTree.newTreeItem(None) is False

    # Root Items
    # ==========

    # No class set
    assert nwTree.newTreeItem(nwItemType.ROOT) is False

    # Create root item
    assert nwTree.newTreeItem(nwItemType.ROOT, nwItemClass.WORLD) is True
    assert "0000000000010" in nwGUI.theProject.tree

    # File/Folder Items
    # =================

    # No location selected for new item
    nwTree.projTree.clearSelection()
    caplog.clear()
    assert nwTree.newTreeItem(nwItemType.FILE) is False
    assert nwTree.newTreeItem(nwItemType.FOLDER) is False
    assert "Did not find anywhere" in caplog.text

    # Create new folder as child of Novel folder
    nwTree.setSelectedHandle("0000000000008")
    assert nwTree.newTreeItem(nwItemType.FOLDER) is True
    assert nwGUI.theProject.tree["0000000000011"].itemParent == "0000000000008"
    assert nwGUI.theProject.tree["0000000000011"].itemRoot == "0000000000008"
    assert nwGUI.theProject.tree["0000000000011"].itemClass == nwItemClass.NOVEL

    # Add a new file in the new folder
    nwTree.setSelectedHandle("0000000000011")
    assert nwTree.newTreeItem(nwItemType.FILE) is True
    assert nwGUI.theProject.tree["0000000000012"].itemParent == "0000000000011"
    assert nwGUI.theProject.tree["0000000000012"].itemRoot == "0000000000008"
    assert nwGUI.theProject.tree["0000000000012"].itemClass == nwItemClass.NOVEL

    # Add a new file next to the other new file
    nwTree.setSelectedHandle("0000000000012")
    assert nwTree.newTreeItem(nwItemType.FILE) is True
    assert nwGUI.theProject.tree["0000000000013"].itemParent == "0000000000011"
    assert nwGUI.theProject.tree["0000000000013"].itemRoot == "0000000000008"
    assert nwGUI.theProject.tree["0000000000013"].itemClass == nwItemClass.NOVEL
    assert nwGUI.openDocument("0000000000013")
    assert nwGUI.docEditor.getText() == "## New Document\n\n"

    # Add a new file to the characters folder
    nwTree.setSelectedHandle("000000000000a")
    assert nwTree.newTreeItem(nwItemType.FILE) is True
    assert nwGUI.theProject.tree["0000000000014"].itemParent == "000000000000a"
    assert nwGUI.theProject.tree["0000000000014"].itemRoot == "000000000000a"
    assert nwGUI.theProject.tree["0000000000014"].itemClass == nwItemClass.CHARACTER
    assert nwGUI.openDocument("0000000000014")
    assert nwGUI.docEditor.getText() == "# New Note\n\n"

    # Make sure the sibling folder bug trap works
    nwTree.setSelectedHandle("0000000000013")
    nwGUI.theProject.tree["0000000000013"].setParent(None)  # This should not happen
    caplog.clear()
    assert nwTree.newTreeItem(nwItemType.FILE) is False
    assert "Internal error" in caplog.text
    nwGUI.theProject.tree["0000000000013"].setParent("0000000000011")

    # Get the trash folder
    nwTree.projTree._addTrashRoot()
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
def testGuiProjTree_MoveItems(qtbot, monkeypatch, nwGUI, fncDir, mockRnd):
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
    prjDir = os.path.join(fncDir, "project")
    buildTestProject(nwGUI, prjDir)

    # Move Documents
    # ==============

    # Add some files
    nwTree.setSelectedHandle("000000000000d")
    assert nwTree.newTreeItem(nwItemType.FILE) is True
    assert nwTree.newTreeItem(nwItemType.FILE) is True
    assert nwTree.newTreeItem(nwItemType.FILE) is True
    assert nwTree.getTreeFromHandle("000000000000d") == [
        "000000000000d", "000000000000e", "000000000000f",
        "0000000000010", "0000000000011", "0000000000012",
    ]

    # Move item without focus
    monkeypatch.setattr(GuiProjectTree, "hasFocus", lambda *a: False)
    assert nwTree.moveTreeItem(1) is False
    assert nwTree.getTreeFromHandle("000000000000d") == [
        "000000000000d", "000000000000e", "000000000000f",
        "0000000000010", "0000000000011", "0000000000012",
    ]
    monkeypatch.setattr(GuiProjectTree, "hasFocus", lambda *a: True)

    # Move with no selections
    nwTree.projTree.clearSelection()
    assert nwTree.moveTreeItem(1) is False

    # Move second item up twice (should give same result)
    nwTree.setSelectedHandle("000000000000f")
    assert nwTree.moveTreeItem(-1) is True
    assert nwTree.getTreeFromHandle("000000000000d") == [
        "000000000000d", "000000000000f", "000000000000e",
        "0000000000010", "0000000000011", "0000000000012",
    ]
    assert nwTree.moveTreeItem(-1) is False
    assert nwTree.getTreeFromHandle("000000000000d") == [
        "000000000000d", "000000000000f", "000000000000e",
        "0000000000010", "0000000000011", "0000000000012",
    ]

    # Restore via menu entry
    nwGUI.mainMenu.aMoveDown.activate(QAction.Trigger)
    assert nwTree.getTreeFromHandle("000000000000d") == [
        "000000000000d", "000000000000e", "000000000000f",
        "0000000000010", "0000000000011", "0000000000012",
    ]

    # Move fifth item down twice (should give same result)
    nwTree.setSelectedHandle("0000000000011")
    assert nwTree.moveTreeItem(1) is True
    assert nwTree.getTreeFromHandle("000000000000d") == [
        "000000000000d", "000000000000e", "000000000000f",
        "0000000000010", "0000000000012", "0000000000011",
    ]
    assert nwTree.moveTreeItem(1) is False
    assert nwTree.getTreeFromHandle("000000000000d") == [
        "000000000000d", "000000000000e", "000000000000f",
        "0000000000010", "0000000000012", "0000000000011",
    ]

    # Restore via menu entry
    nwGUI.mainMenu.aMoveUp.activate(QAction.Trigger)
    assert nwTree.getTreeFromHandle("000000000000d") == [
        "000000000000d", "000000000000e", "000000000000f",
        "0000000000010", "0000000000011", "0000000000012",
    ]

    # Move down again, and restore via undo
    nwTree.setSelectedHandle("0000000000011")
    assert nwTree.moveTreeItem(1) is True
    assert nwTree.getTreeFromHandle("000000000000d") == [
        "000000000000d", "000000000000e", "000000000000f",
        "0000000000010", "0000000000012", "0000000000011",
    ]
    nwGUI.mainMenu.aMoveUndo.activate(QAction.Trigger)
    assert nwTree.getTreeFromHandle("000000000000d") == [
        "000000000000d", "000000000000e", "000000000000f",
        "0000000000010", "0000000000011", "0000000000012",
    ]

    # Root Folder
    # ===========

    nwTree.setSelectedHandle("0000000000008")
    assert nwGUI.theProject.tree._treeOrder.index("0000000000008") == 0

    # Move novel folder up
    assert nwTree.moveTreeItem(-1) is False
    assert nwGUI.theProject.tree._treeOrder.index("0000000000008") == 0

    # Move novel folder down
    assert nwTree.moveTreeItem(1) is True
    assert nwGUI.theProject.tree._treeOrder.index("0000000000008") == 1

    # Move novel folder up again
    assert nwTree.moveTreeItem(-1) is True
    assert nwGUI.theProject.tree._treeOrder.index("0000000000008") == 0

    # Clean up
    # qtbot.stopForInteraction()
    nwGUI.closeProject()

# END Test testGuiProjTree_MoveItems


@pytest.mark.gui
def testGuiProjTree_DeleteItems(qtbot, caplog, monkeypatch, nwGUI, fncDir, mockRnd):
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
    prjDir = os.path.join(fncDir, "project")
    buildTestProject(nwGUI, prjDir)

    # Try emptying the trash already now, when there is no trash folder
    assert nwTree.emptyTrash() is False

    # Add some files
    nwTree.setSelectedHandle("000000000000d")
    assert nwTree.newTreeItem(nwItemType.FILE) is True
    assert nwTree.newTreeItem(nwItemType.FILE) is True
    assert nwTree.newTreeItem(nwItemType.FILE) is True
    assert nwTree.getTreeFromHandle("000000000000d") == [
        "000000000000d", "000000000000e", "000000000000f",
        "0000000000010", "0000000000011", "0000000000012",
    ]

    # Delete item without focus -> blocked
    monkeypatch.setattr(GuiProjectTree, "hasFocus", lambda *a: False)
    nwTree.setSelectedHandle("0000000000012")
    assert nwTree.deleteItem() is False
    monkeypatch.setattr(GuiProjectTree, "hasFocus", lambda *a: True)

    # No selection made
    nwTree.projTree.clearSelection()
    caplog.clear()
    assert nwTree.deleteItem() is False
    assert "no item to delete" in caplog.text

    # Not a valid handle
    nwTree.projTree.clearSelection()
    caplog.clear()
    assert nwTree.deleteItem("0000000000000") is False
    assert "Could not find tree item" in caplog.text

    # Delete Folder/Root
    # ==================

    # Deleting non-empty folders is blocked
    assert nwTree.deleteItem("0000000000008") is False  # Novel Root
    assert nwTree.deleteItem("000000000000a") is True   # Character Root

    # Delete File
    # ===========

    # Block adding trash folder
    funcPointer = nwTree.projTree._addTrashRoot
    nwTree.projTree._addTrashRoot = lambda *a: None
    assert nwTree.deleteItem("0000000000012") is False
    nwTree.projTree._addTrashRoot = funcPointer

    # Delete last two documents, which also adds the trash folder
    assert nwTree.deleteItem("0000000000012") is True
    assert nwTree.deleteItem("0000000000011") is True
    assert nwTree.getTreeFromHandle("000000000000d") == [
        "000000000000d", "000000000000e", "000000000000f",
        "0000000000010"
    ]
    trashHandle = nwGUI.theProject.tree.trashRoot()
    assert nwTree.getTreeFromHandle(trashHandle) == [
        trashHandle, "0000000000012", "0000000000011"
    ]

    # Delete the first file again (permanent), and ask for permission
    # Also open the document in the editor, which should trigger a close
    assert os.path.isfile(os.path.join(prjDir, "content", "0000000000012.nwd"))
    assert "0000000000012" in nwGUI.theProject.tree
    assert nwGUI.docEditor.docHandle() is None
    assert nwGUI.openDocument("0000000000012") is True
    assert nwGUI.docEditor.docHandle() == "0000000000012"
    assert nwTree.deleteItem("0000000000012") is True
    assert nwGUI.docEditor.docHandle() is None
    assert not os.path.isfile(os.path.join(prjDir, "content", "0000000000012.nwd"))
    assert "0000000000012" not in nwGUI.theProject.tree
    assert nwTree.getTreeFromHandle(trashHandle) == [
        trashHandle, "0000000000011"
    ]

    # Delete the second file, and skip asking for permission
    assert os.path.isfile(os.path.join(prjDir, "content", "0000000000011.nwd"))
    assert "0000000000011" in nwGUI.theProject.tree
    assert nwTree.deleteItem("0000000000011", alreadyAsked=True) is True
    assert not os.path.isfile(os.path.join(prjDir, "content", "0000000000011.nwd"))
    assert "0000000000011" not in nwGUI.theProject.tree
    assert nwTree.getTreeFromHandle(trashHandle) == [trashHandle]

    # Delete Folder
    # =============

    trashHandle = nwGUI.theProject.tree.trashRoot()

    # Add a folder with two files
    nwTree.setSelectedHandle("0000000000009")
    assert nwTree.newTreeItem(nwItemType.FOLDER) is True
    nwTree.setSelectedHandle("0000000000014")
    assert nwTree.newTreeItem(nwItemType.FILE) is True
    assert nwTree.newTreeItem(nwItemType.FILE) is True
    assert os.path.isfile(os.path.join(fncDir, "project", "content", "0000000000015.nwd"))
    assert os.path.isfile(os.path.join(fncDir, "project", "content", "0000000000016.nwd"))

    # Delete the folder, which moves everything to Trash
    assert nwTree.getTreeFromHandle("0000000000014") == [
        "0000000000014", "0000000000015", "0000000000016"
    ]
    assert nwTree.deleteItem("0000000000014") is True
    assert nwTree.getTreeFromHandle(trashHandle) == [
        trashHandle, "0000000000014", "0000000000015", "0000000000016"
    ]
    assert os.path.isfile(os.path.join(fncDir, "project", "content", "0000000000015.nwd"))
    assert os.path.isfile(os.path.join(fncDir, "project", "content", "0000000000016.nwd"))

    # Delete again, which should delete folder and all files
    assert nwTree.deleteItem("0000000000014") is True
    assert nwTree.getTreeFromHandle(trashHandle) == [trashHandle]
    assert not os.path.isfile(os.path.join(fncDir, "project", "content", "0000000000015.nwd"))
    assert not os.path.isfile(os.path.join(fncDir, "project", "content", "0000000000016.nwd"))

    # Add an empty folder, which can be deleted with no further restrictions
    nwTree.setSelectedHandle("0000000000009")
    assert nwTree.newTreeItem(nwItemType.FOLDER) is True
    assert nwTree.getTreeFromHandle("0000000000009") == ["0000000000009", "0000000000017"]

    nwTree.setSelectedHandle("0000000000017")
    assert nwTree.deleteItem("0000000000017") is True
    assert nwTree.getTreeFromHandle("0000000000009") == ["0000000000009"]

    # Empty Trash
    # ===========

    # Try to empty trash that is already empty
    assert nwTree.getTreeFromHandle(trashHandle) == [trashHandle]
    assert nwTree.emptyTrash() is False

    # Move the two remaining scene documents to trash
    assert nwTree.deleteItem("000000000000f") is True
    assert nwTree.deleteItem("0000000000010") is True
    assert nwTree.getTreeFromHandle("000000000000d") == [
        "000000000000d", "000000000000e"
    ]
    assert nwTree.getTreeFromHandle(trashHandle) == [
        trashHandle, "000000000000f", "0000000000010"
    ]

    # Empty trash, but select no on question
    with monkeypatch.context() as mp:
        mp.setattr(QMessageBox, "question", lambda *a: QMessageBox.No)
        assert nwTree.emptyTrash() is False

    # Empty the trash proper
    assert nwTree.emptyTrash() is True
    assert nwTree.getTreeFromHandle(trashHandle) == [trashHandle]

    # Try to delete a file, but block the underlying deletion of the file on disk
    assert os.path.isfile(os.path.join(fncDir, "project", "content", "000000000000e.nwd"))
    with monkeypatch.context() as mp:
        mp.setattr("novelwriter.core.document.NWDoc.deleteDocument", lambda *a: False)
        assert nwTree.deleteItem("000000000000e") is True
        assert nwTree.deleteItem("000000000000e") is True
        assert os.path.isfile(os.path.join(fncDir, "project", "content", "000000000000e.nwd"))

    # Delete proper
    assert nwTree.projTree._deleteTreeItem("000000000000e") is True
    assert not os.path.isfile(os.path.join(fncDir, "project", "content", "000000000000e.nwd"))

    # Clean up
    # qtbot.stopForInteraction()
    nwGUI.closeProject()

# END Test testGuiProjTree_DeleteItems
