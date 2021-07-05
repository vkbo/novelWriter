"""
novelWriter – NWDoc Class Tester
================================

This file is a part of novelWriter
Copyright 2018–2021, Veronica Berglyd Olsen

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

import os
import pytest

from mock import causeOSError
from tools import readFile

from nw.core import NWProject, NWDoc
from nw.enum import nwItemClass, nwItemLayout


@pytest.mark.core
def testCoreDocument_LoadSave(monkeypatch, mockGUI, nwMinimal):
    """Test loading and saving a document with the NWDoc class.
    """
    theProject = NWProject(mockGUI)
    assert theProject.openProject(nwMinimal)
    assert theProject.projPath == nwMinimal

    sHandle = "8c659a11cd429"

    # Not a valid handle
    theDoc = NWDoc(theProject, "stuff")
    assert theDoc.readDocument() is None

    # Non-existent handle
    theDoc = NWDoc(theProject, "0000000000000")
    assert theDoc.readDocument() is None

    # Cause open() to fail while loading
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        theDoc = NWDoc(theProject, sHandle)
        assert theDoc.readDocument() is None
        assert theDoc.getError() == "OSError"

    # Load the text
    theDoc = NWDoc(theProject, sHandle)
    assert theDoc.readDocument() == "### New Scene\n\n"

    # Try to open a new (non-existent) file
    nHandle = theProject.projTree.findRoot(nwItemClass.NOVEL)
    assert nHandle is not None
    xHandle = theProject.newFile("New File", nwItemClass.NOVEL, nHandle)
    theDoc = NWDoc(theProject, xHandle)
    assert theDoc.readDocument() == ""

    # Set handle and save again
    theText = "### Test File\n\nText ...\n\n"
    theDoc = NWDoc(theProject, xHandle)
    assert theDoc.readDocument(xHandle) == ""
    assert theDoc.writeDocument(theText)

    # Save again to ensure temp file and previous file is handled
    assert theDoc.writeDocument(theText)

    # Check file content
    docPath = os.path.join(nwMinimal, "content", xHandle+".nwd")
    assert readFile(docPath) == (
        "%%~name: New File\n"
        f"%%~path: a508bb932959c/{xHandle}\n"
        "%%~kind: NOVEL/SCENE\n"
        "### Test File\n\n"
        "Text ...\n\n"
    )

    # Force no meta data
    theDoc._theItem = None
    assert theDoc.writeDocument(theText)
    assert readFile(docPath) == theText

    # Cause open() to fail while saving
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        assert not theDoc.writeDocument(theText)
        assert theDoc.getError() == "OSError"

    # Saving with no handle
    theDoc._docHandle = None
    assert not theDoc.writeDocument(theText)

    # Delete the last document
    theDoc = NWDoc(theProject, "stuff")
    assert not theDoc.deleteDocument()
    assert os.path.isfile(docPath)

    # Cause the delete to fail
    with monkeypatch.context() as mp:
        mp.setattr("os.unlink", causeOSError)
        theDoc = NWDoc(theProject, xHandle)
        assert not theDoc.deleteDocument()
        assert theDoc.getError() == "OSError"

    # Make the delete pass
    theDoc = NWDoc(theProject, xHandle)
    assert theDoc.deleteDocument()
    assert not os.path.isfile(docPath)

# END Test testCoreDocument_Load


@pytest.mark.core
def testCoreDocument_Methods(mockGUI, nwMinimal):
    """Test other methods of the NWDoc class.
    """
    theProject = NWProject(mockGUI)
    assert theProject.openProject(nwMinimal)
    assert theProject.projPath == nwMinimal

    sHandle = "8c659a11cd429"
    theDoc = NWDoc(theProject, sHandle)
    docPath = os.path.join(nwMinimal, "content", sHandle+".nwd")

    assert theDoc.readDocument() == "### New Scene\n\n"

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
    assert theDoc.writeDocument("%%~ stuff\n### Test File\n\nText ...\n\n")
    assert readFile(docPath) == (
        "%%~name: New Scene\n"
        f"%%~path: a6d311a93600a/{sHandle}\n"
        "%%~kind: NOVEL/SCENE\n"
        "%%~ stuff\n"
        "### Test File\n\n"
        "Text ...\n\n"
    )

    assert theDoc.readDocument() == "### Test File\n\nText ...\n\n"

# END Test testCoreDocument_Methods
