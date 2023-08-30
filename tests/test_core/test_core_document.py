"""
novelWriter – NWDocument Class Tester
=====================================

This file is a part of novelWriter
Copyright 2018–2023, Veronica Berglyd Olsen

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

from tools import C, MOCK_TIME, buildTestProject, readFile, writeFile
from mocked import causeOSError

from novelwriter.enum import nwItemClass, nwItemLayout
from novelwriter.core.project import NWProject
from novelwriter.core.document import NWDocument


@pytest.mark.core
def testCoreDocument_LoadSave(monkeypatch, mockGUI, fncPath, mockRnd):
    """Test loading and saving a document with the NWDocument class."""
    monkeypatch.setattr("novelwriter.core.document.time", lambda: MOCK_TIME)

    theProject = NWProject()
    mockRnd.reset()
    buildTestProject(theProject, fncPath)

    # Read Document
    # =============

    # Not a valid handle
    theDoc = NWDocument(theProject, "stuff")
    assert bool(theDoc) is False
    assert theDoc.readDocument() is None
    assert theDoc.fileExists() is False

    # Non-existent handle
    theDoc = NWDocument(theProject, C.hInvalid)
    assert theDoc.readDocument() is None
    assert theDoc._lastHash == ""
    assert theDoc.fileExists() is False

    # No content path
    with monkeypatch.context() as mp:
        mp.setattr("novelwriter.core.storage.NWStorage.contentPath", property(lambda *a: None))
        theDoc = NWDocument(theProject, C.hSceneDoc)
        assert theDoc.readDocument() is None
        assert theDoc.fileExists() is False

    # Cause open() to fail while loading
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        theDoc = NWDocument(theProject, C.hSceneDoc)
        assert theDoc.fileExists() is True
        assert theDoc.readDocument() is None
        assert theDoc.getError() == "OSError: Mock OSError"

    # Load the text
    theDoc = NWDocument(theProject, C.hSceneDoc)
    assert theDoc.fileExists() is True
    assert theDoc.readDocument() == "### New Scene\n\n"

    # Try to open a new (non-existent) file
    xHandle = theProject.newFile("New File", C.hNovelRoot)
    theDoc = NWDocument(theProject, xHandle)
    assert bool(theDoc) is True
    assert repr(theDoc) == f"<NWDocument handle={xHandle}>"
    assert theDoc.readDocument() == ""

    # Write Document
    # ==============

    # No content path
    with monkeypatch.context() as mp:
        mp.setattr("novelwriter.core.storage.NWStorage.contentPath", property(lambda *a: None))
        theDoc = NWDocument(theProject, xHandle)
        assert theDoc.writeDocument("") is False

    # Set handle and save
    theText = "### Test File\n\nText ...\n\n"
    theDoc = NWDocument(theProject, xHandle)
    assert theDoc.readDocument(xHandle) == ""  # type: ignore
    assert theDoc.writeDocument(theText) is True

    # Save again to ensure temp file and previous file is handled
    assert theDoc.writeDocument(theText) is True

    # Check file content
    docPath = fncPath / "content" / f"{xHandle}.nwd"
    assert readFile(docPath) == (
        "%%~name: New File\n"
        f"%%~path: {C.hNovelRoot}/{xHandle}\n"
        "%%~kind: NOVEL/DOCUMENT\n"
        "%%~hash: b288c3ab03181027d9a16d7fd2291262f5de9ac8\n"
        "%%~date: 2019-05-10 18:52:00/2019-05-10 18:52:00\n"
        "### Test File\n\n"
        "Text ...\n\n"
    )

    # Alter the document on disk and save again
    writeFile(docPath, "blablabla")
    assert theDoc.writeDocument(theText) is False

    # Force the overwrite
    assert theDoc.writeDocument(theText, forceWrite=True) is True

    # Force no meta data
    theDoc._item = None
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
    theDoc._handle = None
    assert theDoc.writeDocument(theText) is False

    # Delete Document
    # ===============

    # Delete a non-existing document
    theDoc = NWDocument(theProject, "stuff")
    assert theDoc.deleteDocument() is False
    assert docPath.exists()

    # No content path
    with monkeypatch.context() as mp:
        mp.setattr("novelwriter.core.storage.NWStorage.contentPath", property(lambda *a: None))
        theDoc = NWDocument(theProject, xHandle)
        assert theDoc.deleteDocument() is False

    # Cause the delete to fail
    with monkeypatch.context() as mp:
        mp.setattr("pathlib.Path.unlink", causeOSError)
        theDoc = NWDocument(theProject, xHandle)
        assert theDoc.deleteDocument() is False
        assert theDoc.getError() == "OSError: Mock OSError"

    # Make the delete pass
    theDoc = NWDocument(theProject, xHandle)
    assert theDoc.deleteDocument() is True
    assert not docPath.exists()

# END Test testCoreDocument_Load


@pytest.mark.core
def testCoreDocument_Methods(monkeypatch, mockGUI, fncPath, mockRnd):
    """Test other methods of the NWDocument class."""
    monkeypatch.setattr("novelwriter.core.document.time", lambda: MOCK_TIME)

    theProject = NWProject()
    mockRnd.reset()
    buildTestProject(theProject, fncPath)

    theDoc = NWDocument(theProject, C.hSceneDoc)
    docPath = fncPath / "content" / f"{C.hSceneDoc}.nwd"

    assert theDoc.readDocument() == "### New Scene\n\n"

    # Check location
    assert theDoc.getFileLocation() == str(docPath)

    # Check the item
    assert theDoc.getCurrentItem() is not None
    assert theDoc.getCurrentItem().itemHandle == C.hSceneDoc  # type: ignore

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
        "%%~hash: dd350c602de803554b2a7c17f191ae25dea1df63\n"
        "%%~date: 2019-05-10 18:52:00/2019-05-10 18:52:00\n"
        "%%~ stuff\n"
        "### Test File\n\n"
        "Text ...\n\n"
    )

    assert theDoc.readDocument() == "### Test File\n\nText ...\n\n"

# END Test testCoreDocument_Methods
