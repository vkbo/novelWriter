"""
novelWriter – NWDocument Class Tester
=====================================

This file is a part of novelWriter
Copyright (C) 2020 Veronica Berglyd Olsen

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
from __future__ import annotations

import pytest

from novelwriter.core.document import NWDocument
from novelwriter.core.project import NWProject
from novelwriter.enum import nwItemClass, nwItemLayout

from tests.mocked import causeOSError
from tests.tools import MOCK_TIME, C, buildTestProject, readFile, writeFile


@pytest.mark.core
def testCoreDocument_LoadSave(monkeypatch, mockGUI, fncPath, mockRnd):
    """Test loading and saving a document with the NWDocument class."""
    monkeypatch.setattr("novelwriter.core.document.time", lambda: MOCK_TIME)

    project = NWProject()
    mockRnd.reset()
    buildTestProject(project, fncPath)

    # Read Document
    # =============

    # Not a valid handle
    doc = NWDocument(project, "stuff")
    assert bool(doc) is False
    assert doc.readDocument() is None
    assert doc.fileExists() is False
    assert doc.hashError is False
    assert doc.createdDate == "Unknown"
    assert doc.updatedDate == "Unknown"

    # Non-existent handle
    doc = NWDocument(project, C.hInvalid)
    assert doc.readDocument() is None
    assert doc._lastHash == ""
    assert doc.fileExists() is False

    # No content path
    with monkeypatch.context() as mp:
        mp.setattr("novelwriter.core.storage.NWStorage.contentPath", property(lambda *a: None))
        doc = NWDocument(project, C.hSceneDoc)
        assert doc.readDocument() is None
        assert doc.fileExists() is False

    # Cause open() to fail while loading
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        doc = NWDocument(project, C.hSceneDoc)
        assert doc.fileExists() is True
        assert doc.readDocument() is None
        assert doc.getError() == "OSError: Mock OSError"

    # Load the text
    doc = NWDocument(project, C.hSceneDoc)
    assert doc.fileExists() is True
    assert doc.readDocument() == "### New Scene\n\n"

    # Try to open a new (non-existent) file
    xHandle = project.newFile("New File", C.hNovelRoot)
    assert xHandle is not None
    doc = NWDocument(project, xHandle)
    assert bool(doc) is True
    assert repr(doc) == f"<NWDocument handle={xHandle}>"
    assert doc.readDocument() == ""

    # Write Document
    # ==============

    # No content path
    with monkeypatch.context() as mp:
        mp.setattr("novelwriter.core.storage.NWStorage.contentPath", property(lambda *a: None))
        doc = NWDocument(project, xHandle)
        assert doc.writeDocument("") is False

    # Set handle and save
    text = "### Test File\n\nText ...\n\n"
    doc = NWDocument(project, xHandle)
    assert doc.writeDocument(text) is True

    # Save again to ensure temp file and previous file is handled
    assert doc.writeDocument(text) is True

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
    assert doc.writeDocument(text) is False

    # Force the overwrite
    assert doc.writeDocument(text, forceWrite=True) is True

    # Force no meta data
    doc._item = None
    assert doc.writeDocument(text) is True
    assert readFile(docPath) == text

    # Cause open() to fail while saving
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        assert doc.writeDocument(text) is False
        assert doc.getError() == "OSError: Mock OSError"

    doc._docError = ""
    assert doc.getError() == ""

    # Cause os.replace() to fail while saving
    with monkeypatch.context() as mp:
        mp.setattr("pathlib.Path.replace", causeOSError)
        assert doc.writeDocument(text) is False
        assert doc.getError() == "OSError: Mock OSError"

    doc._docError = ""
    assert doc.getError() == ""

    # Saving with no handle
    doc._handle = None
    assert doc.writeDocument(text) is False

    # Quick Read
    # ==========

    contPath = fncPath / "content"
    assert NWDocument.quickReadText(contPath, xHandle) == (
        "### Test File\n\n"
        "Text ...\n\n"
    )

    # Check read text fallback
    assert NWDocument.quickReadText(contPath, "0000000000000") == ""
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        assert NWDocument.quickReadText(contPath, xHandle) == ""

    # Delete Document
    # ===============

    # Delete a non-existing document
    doc = NWDocument(project, "stuff")
    assert doc.deleteDocument() is False
    assert docPath.exists()

    # No content path
    with monkeypatch.context() as mp:
        mp.setattr("novelwriter.core.storage.NWStorage.contentPath", property(lambda *a: None))
        doc = NWDocument(project, xHandle)
        assert doc.deleteDocument() is False

    # Cause the delete to fail
    with monkeypatch.context() as mp:
        mp.setattr("pathlib.Path.unlink", causeOSError)
        doc = NWDocument(project, xHandle)
        assert doc.deleteDocument() is False
        assert doc.getError() == "OSError: Mock OSError"

    # Make the delete pass
    doc = NWDocument(project, xHandle)
    assert doc.deleteDocument() is True
    assert not docPath.exists()


@pytest.mark.core
def testCoreDocument_Methods(monkeypatch, mockGUI, fncPath, mockRnd):
    """Test other methods of the NWDocument class."""
    monkeypatch.setattr("novelwriter.core.document.time", lambda: MOCK_TIME)

    project = NWProject()
    mockRnd.reset()
    buildTestProject(project, fncPath)

    doc = NWDocument(project, C.hSceneDoc)
    docPath = fncPath / "content" / f"{C.hSceneDoc}.nwd"

    assert doc.readDocument() == "### New Scene\n\n"

    # Check location
    assert doc.fileLocation == str(docPath)

    # Check the item
    assert doc.nwItem is not None
    assert doc.nwItem.itemHandle == C.hSceneDoc  # type: ignore

    # Check the meta
    name, parent, itemClass, itemLayout = doc.getMeta()
    assert name == "New Scene"
    assert parent == C.hChapterDir
    assert itemClass == nwItemClass.NOVEL
    assert itemLayout == nwItemLayout.DOCUMENT

    # Add meta data garbage
    assert doc.writeDocument("%%~ stuff\n### Test File\n\nText ...\n\n")
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

    assert doc.readDocument() == "### Test File\n\nText ...\n\n"
