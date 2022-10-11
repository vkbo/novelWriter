"""
novelWriter – Project Document Tools Tester
===========================================

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

from shutil import copyfile

from mock import causeOSError
from tools import C, buildTestProject, cmpFiles

from novelwriter.core.project import NWProject
from novelwriter.core.doctools import DocMerger


@pytest.mark.core
def testCoreDocTools_DocMerger(monkeypatch, mockGUI, fncDir, outDir, refDir, mockRnd, ipsumText):
    """Test the DocMerger utility.
    """
    theProject = NWProject(mockGUI)
    mockRnd.reset()
    buildTestProject(theProject, fncDir)

    # Create File to Merge
    # ====================

    hChapter1 = theProject.newFile("Chapter 1", C.hNovelRoot)
    hSceneOne11 = theProject.newFile("Scene 1.1", hChapter1)
    hSceneOne12 = theProject.newFile("Scene 1.2", hChapter1)
    hSceneOne13 = theProject.newFile("Scene 1.3", hChapter1)

    docText1 = "\n\n".join(ipsumText[0:2]) + "\n\n"
    docText2 = "\n\n".join(ipsumText[1:3]) + "\n\n"
    docText3 = "\n\n".join(ipsumText[2:4]) + "\n\n"
    docText4 = "\n\n".join(ipsumText[3:5]) + "\n\n"

    theProject.writeNewFile(hChapter1, 2, True, docText1)
    theProject.writeNewFile(hSceneOne11, 3, True, docText2)
    theProject.writeNewFile(hSceneOne12, 3, True, docText3)
    theProject.writeNewFile(hSceneOne13, 3, True, docText4)

    # Basic Checks
    # ============

    docMerger = DocMerger(theProject)

    # No writing without a target set
    assert docMerger.writeTargetDoc() is False

    # Cannot append invalid handle
    assert docMerger.appendText(C.hInvalid, True, "Merge") is False

    # Cannot create new target from invalid handle
    assert docMerger.newTargetDoc(C.hInvalid, "Test") is None

    # Merge to New
    # ============

    saveFile = os.path.join(fncDir, "content", "0000000000014.nwd")
    testFile = os.path.join(outDir, "coreDocTools_DocMerger_0000000000014.nwd")
    compFile = os.path.join(refDir, "coreDocTools_DocMerger_0000000000014.nwd")

    assert docMerger.newTargetDoc(hChapter1, "All of Chapter 1") == "0000000000014"

    assert docMerger.appendText(hChapter1, True, "Merge") is True
    assert docMerger.appendText(hSceneOne11, True, "Merge") is True
    assert docMerger.appendText(hSceneOne12, True, "Merge") is True
    assert docMerger.appendText(hSceneOne13, True, "Merge") is True

    # Block writing and check error handling
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        assert docMerger.writeTargetDoc() is False
        assert not os.path.isfile(saveFile)
        assert docMerger.getError() != ""

    # Write properly, and compare
    assert docMerger.writeTargetDoc() is True
    copyfile(saveFile, testFile)
    assert cmpFiles(testFile, compFile)

    # Merge into Existing
    # ===================

    saveFile = os.path.join(fncDir, "content", "0000000000010.nwd")
    testFile = os.path.join(outDir, "coreDocTools_DocMerger_0000000000010.nwd")
    compFile = os.path.join(refDir, "coreDocTools_DocMerger_0000000000010.nwd")

    docMerger.setTargetDoc(hChapter1)

    assert docMerger.appendText(hSceneOne11, True, "Merge") is True
    assert docMerger.appendText(hSceneOne12, True, "Merge") is True
    assert docMerger.appendText(hSceneOne13, True, "Merge") is True

    assert docMerger.writeTargetDoc() is True
    copyfile(saveFile, testFile)
    assert cmpFiles(testFile, compFile)

    # Just for debugging
    docMerger.writeTargetDoc()

# END Test testCoreDocTools_DocMerger
