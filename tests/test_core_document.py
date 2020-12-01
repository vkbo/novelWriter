# -*- coding: utf-8 -*-
"""novelWriter NWDoc Class Tester
"""

import os
import pytest

from nw.core import NWProject, NWDoc
from nw.core.item import NWItem
from nw.constants import nwItemClass, nwItemLayout

@pytest.mark.core
def testCoreDocument_LoadSave(monkeypatch, dummyGUI, nwMinimal):
    """Test loading and saving a document with the NWDoc class.
    """
    theProject = NWProject(dummyGUI)
    assert theProject.openProject(nwMinimal)
    assert theProject.projPath == nwMinimal

    theDoc = NWDoc(theProject, dummyGUI)
    sHandle = "8c659a11cd429"

    # Not a valid handle
    assert theDoc.openDocument("dummy") is None

    # Non-existent handle
    assert theDoc.openDocument("0000000000000") is None

    # Cause open() to fail while loading
    def dummyOpen(*args, **kwargs):
        raise OSError

    monkeypatch.setattr("builtins.open", dummyOpen)
    assert theDoc.openDocument(sHandle) is None
    monkeypatch.undo()

    # Load the text
    assert theDoc.openDocument(sHandle) == "### New Scene\n\n"

    # Try to open a new (non-existent) file
    nHandle = theProject.projTree.findRoot(nwItemClass.NOVEL)
    assert nHandle is not None
    xHandle = theProject.newFile("New File", nwItemClass.NOVEL, nHandle)
    assert theDoc.openDocument(xHandle) == ""

    # Check cached item
    assert isinstance(theDoc._theItem, NWItem)
    assert theDoc.openDocument(xHandle, isOrphan=True) == ""
    assert theDoc._theItem is None

    # Set handle and save again
    theText = "### Test File\n\nText ...\n\n"
    assert theDoc.openDocument(xHandle) == ""
    assert theDoc.saveDocument(theText)

    # Save again to ensure temp file and previous file is handled
    assert theDoc.saveDocument(theText)

    # Check file content
    docPath = os.path.join(nwMinimal, "content", xHandle+".nwd")
    with open(docPath, mode="r", encoding="utf8") as inFile:
        assert inFile.read() == (
            "%%~name: New File\n"
            f"%%~path: a508bb932959c/{xHandle}\n"
            "%%~kind: NOVEL/SCENE\n"
            "### Test File\n\n"
            "Text ...\n\n"
        )

    # Force no meta data
    theDoc._theItem = None
    assert theDoc.saveDocument(theText)

    with open(docPath, mode="r", encoding="utf8") as inFile:
        assert inFile.read() == theText

    # Cause open() to fail while saving
    def dummyIO(*args, **kwargs):
        raise OSError

    monkeypatch.setattr("builtins.open", dummyIO)
    assert not theDoc.saveDocument(theText)
    monkeypatch.undo()

    # Saving with no handle
    theDoc.clearDocument()
    assert not theDoc.saveDocument(theText)

    # Delete the last document
    assert not theDoc.deleteDocument("dummy")
    assert os.path.isfile(docPath)

    # Cause the delete to fail
    monkeypatch.setattr("os.unlink", dummyIO)
    assert not theDoc.deleteDocument(xHandle)
    monkeypatch.undo()

    # Make the delete pass
    assert theDoc.deleteDocument(xHandle)
    assert not os.path.isfile(docPath)

# END Test testCoreDocument_Load

@pytest.mark.core
def testCoreDocument_Methods(monkeypatch, dummyGUI, nwMinimal):
    """Test other methods of the NWDoc class.
    """
    theProject = NWProject(dummyGUI)
    assert theProject.openProject(nwMinimal)
    assert theProject.projPath == nwMinimal

    theDoc = NWDoc(theProject, dummyGUI)
    sHandle = "8c659a11cd429"
    docPath = os.path.join(nwMinimal, "content", sHandle+".nwd")

    assert theDoc.openDocument(sHandle) == "### New Scene\n\n"

    # Check location
    assert theDoc.getFileLocation() == docPath

    # Check the item
    assert theDoc.getCurrentItem() is not None
    assert theDoc.getCurrentItem().itemHandle == sHandle

    # Check the meta
    theName, theParent, theClass, theLayout = theDoc.getMeta()
    assert theName == "New Scene"
    assert theParent == "a6d311a93600a"
    assert theClass == nwItemClass.NOVEL
    assert theLayout == nwItemLayout.SCENE

    # Add meta data garbage
    assert theDoc.saveDocument("%%~ stuff\n### Test File\n\nText ...\n\n")
    with open(docPath, mode="r", encoding="utf8") as inFile:
        assert inFile.read() == (
            "%%~name: New Scene\n"
            f"%%~path: a6d311a93600a/{sHandle}\n"
            "%%~kind: NOVEL/SCENE\n"
            "%%~ stuff\n"
            "### Test File\n\n"
            "Text ...\n\n"
        )

    assert theDoc.openDocument(sHandle) == "### Test File\n\nText ...\n\n"

# END Test testCoreDocument_Methods
