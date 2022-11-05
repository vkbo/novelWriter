"""
novelWriter – NWDoc Class Tester
================================

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

import os
import pytest

from mock import causeOSError
from tools import C, buildTestProject, readFile, writeFile

from novelwriter.enum import nwItemClass, nwItemLayout
from novelwriter.core.project import NWProject
from novelwriter.core.document import NWDoc


@pytest.mark.core
def testCoreDocument_LoadSave(monkeypatch, mockGUI, fncDir, mockRnd):
    """Test loading and saving a document with the NWDoc class.
    """
    theProject = NWProject(mockGUI)
    mockRnd.reset()
    buildTestProject(theProject, fncDir)

    # Read Document
    # =============

    # Not a valid handle
    theDoc = NWDoc(theProject, "stuff")
    assert bool(theDoc) is False
    assert theDoc.readDocument() is None

    # Non-existent handle
    theDoc = NWDoc(theProject, C.hInvalid)
    assert theDoc.readDocument() is None
    assert theDoc._currHash is None

    # Cause open() to fail while loading
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        theDoc = NWDoc(theProject, C.hSceneDoc)
        assert theDoc.readDocument() is None
        assert theDoc.getError() == "OSError: Mock OSError"

    # Load the text
    theDoc = NWDoc(theProject, C.hSceneDoc)
    assert theDoc.readDocument() == "### New Scene\n\n"

    # Try to open a new (non-existent) file
    xHandle = theProject.newFile("New File", C.hNovelRoot)
    theDoc = NWDoc(theProject, xHandle)
    assert bool(theDoc) is True
    assert repr(theDoc) == f"<NWDoc handle={xHandle}>"
    assert theDoc.readDocument() == ""

    # Write Document
    # ==============

    # Set handle and save again
    theText = "### Test File\n\nText ...\n\n"
    theDoc = NWDoc(theProject, xHandle)
    assert theDoc.readDocument(xHandle) == ""
    assert theDoc.writeDocument(theText) is True

    # Save again to ensure temp file and previous file is handled
    assert theDoc.writeDocument(theText)

    # Check file content
    docPath = os.path.join(fncDir, "content", xHandle+".nwd")
    assert readFile(docPath) == (
        "%%~name: New File\n"
        f"%%~path: {C.hNovelRoot}/{xHandle}\n"
        "%%~kind: NOVEL/DOCUMENT\n"
        "### Test File\n\n"
        "Text ...\n\n"
    )

    # Alter the document on disk and save again
    writeFile(docPath, "blablabla")
    assert theDoc.writeDocument(theText) is False

    # Force the overwrite
    assert theDoc.writeDocument(theText, forceWrite=True) is True

    # Force no meta data
    theDoc._theItem = None
    assert theDoc.writeDocument(theText) is True
    assert readFile(docPath) == theText

    # Cause open() to fail while saving
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        assert theDoc.writeDocument(theText) is False
        assert theDoc.getError() == "OSError: Mock OSError"

    theDoc._docError = ""
    assert theDoc.getError() == ""

    # Cause os.replace() to fail while saving
    with monkeypatch.context() as mp:
        mp.setattr("pathlib.Path.replace", causeOSError)
        assert theDoc.writeDocument(theText) is False
        assert theDoc.getError() == "OSError: Mock OSError"

    theDoc._docError = ""
    assert theDoc.getError() == ""

    # Saving with no handle
    theDoc._docHandle = None
    assert theDoc.writeDocument(theText) is False

    # Delete Document
    # ===============

    # Delete the last document
    theDoc = NWDoc(theProject, "stuff")
    assert theDoc.deleteDocument() is False
    assert os.path.isfile(docPath)

    # Cause the delete to fail
    with monkeypatch.context() as mp:
        mp.setattr("pathlib.Path.unlink", causeOSError)
        theDoc = NWDoc(theProject, xHandle)
        assert theDoc.deleteDocument() is False
        assert theDoc.getError() == "OSError: Mock OSError"

    # Make the delete pass
    theDoc = NWDoc(theProject, xHandle)
    assert theDoc.deleteDocument() is True
    assert not os.path.isfile(docPath)

# END Test testCoreDocument_Load


@pytest.mark.core
def testCoreDocument_Methods(mockGUI, fncDir, mockRnd):
    """Test other methods of the NWDoc class.
    """
    theProject = NWProject(mockGUI)
    mockRnd.reset()
    buildTestProject(theProject, fncDir)

    theDoc = NWDoc(theProject, C.hSceneDoc)
    docPath = os.path.join(fncDir, "content", C.hSceneDoc+".nwd")

    assert theDoc.readDocument() == "### New Scene\n\n"

    # Check location
    assert theDoc.getFileLocation() == docPath

    # Check the item
    assert theDoc.getCurrentItem() is not None
    assert theDoc.getCurrentItem().itemHandle == C.hSceneDoc

    # Check the meta
    theName, theParent, theClass, theLayout = theDoc.getMeta()
    assert theName == "New Scene"
    assert theParent == C.hChapterDir
    assert theClass == nwItemClass.NOVEL
    assert theLayout == nwItemLayout.DOCUMENT

    # Add meta data garbage
    assert theDoc.writeDocument("%%~ stuff\n### Test File\n\nText ...\n\n")
    assert readFile(docPath) == (
        "%%~name: New Scene\n"
        f"%%~path: {C.hChapterDir}/{C.hSceneDoc}\n"
        "%%~kind: NOVEL/DOCUMENT\n"
        "%%~ stuff\n"
        "### Test File\n\n"
        "Text ...\n\n"
    )

    assert theDoc.readDocument() == "### Test File\n\nText ...\n\n"

# END Test testCoreDocument_Methods
