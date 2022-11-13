"""
novelWriter – OptionState Class Tester
======================================

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

import json
import pytest

from mock import causeOSError

from novelwriter.constants import nwFiles
from novelwriter.core.options import OptionState
from novelwriter.core.project import NWProject
from novelwriter.gui.noveltree import NovelTreeColumn


@pytest.mark.core
def testCoreOptions_LoadSave(monkeypatch, mockGUI, fncPath):
    """Test loading and saving from the OptionState class.
    """
    theProject = NWProject(mockGUI)
    theOpts = OptionState(theProject)

    metaDir = fncPath / "meta"
    metaDir.mkdir()

    # Write a test file
    optFile = metaDir / nwFiles.OPTS_FILE
    optFile.write_text(json.dumps({
        "GuiBuildNovel": {
            "winWidth": 1000,
            "winHeight": 700,
            "addNovel": True,
            "addNotes": False,
            "textFont": "Cantarell",
            "mockItem": None,
        },
        "MockGroup": {
            "mockItem": None,
        },
    }), encoding="utf-8")

    # Load and save with no path set
    theProject.storage._runtimePath = None
    assert theOpts.loadSettings() is False
    assert theOpts.saveSettings() is False

    # Set path
    theProject.storage._runtimePath = fncPath
    assert theProject.storage.getMetaFile(nwFiles.OPTS_FILE) == optFile

    # Cause open() to fail
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        assert theOpts.loadSettings() is False
        assert theOpts.saveSettings() is False

    # Load proper
    assert theOpts.loadSettings()

    # Check that unwanted items have been removed
    assert theOpts._theState == {
        "GuiBuildNovel": {
            "winWidth": 1000,
            "winHeight": 700,
            "addNovel": True,
            "addNotes": False,
            "textFont": "Cantarell",
        },
    }

    # Save proper
    assert theOpts.saveSettings()

    # Load again to check we get the values back
    assert theOpts.loadSettings()
    assert theOpts._theState == {
        "GuiBuildNovel": {
            "winWidth": 1000,
            "winHeight": 700,
            "addNovel": True,
            "addNotes": False,
            "textFont": "Cantarell",
        },
    }

# END Test testCoreOptions_LoadSave


@pytest.mark.core
def testCoreOptions_SetGet(mockGUI):
    """Test setting and getting values from the OptionState class.
    """
    theProject = NWProject(mockGUI)
    theOpts = OptionState(theProject)

    nwColHidden = NovelTreeColumn.HIDDEN

    # Set invalid values
    assert theOpts.setValue("MockGroup", "mockItem", None) is False
    assert theOpts.setValue("GuiBuildNovel", "mockItem", None) is False

    # Set valid value
    assert theOpts.setValue("GuiBuildNovel", "winWidth", 100)

    # Set some values of different types
    assert theOpts.setValue("GuiBuildNovel", "winWidth", 100)
    assert theOpts.setValue("GuiBuildNovel", "winHeight", 12.34)
    assert theOpts.setValue("GuiBuildNovel", "addNovel", True)
    assert theOpts.setValue("GuiBuildNovel", "textFont", "Cantarell")
    assert theOpts.setValue("GuiNovelView", "lastCol", nwColHidden)

    # Generic get, doesn't check type
    assert theOpts.getValue("GuiBuildNovel", "winWidth", None) == 100
    assert theOpts.getValue("GuiBuildNovel", "winHeight", None) == 12.34
    assert theOpts.getValue("GuiBuildNovel", "addNovel", None) is True
    assert theOpts.getValue("GuiBuildNovel", "textFont", None) == "Cantarell"
    assert theOpts.getValue("GuiBuildNovel", "mockItem", None) is None

    # Get type-specific
    assert theOpts.getString("GuiBuildNovel", "winWidth", None) is None
    assert theOpts.getString("GuiBuildNovel", "mockItem", None) is None
    assert theOpts.getInt("GuiBuildNovel", "winWidth", None) == 100
    assert theOpts.getInt("GuiBuildNovel", "textFont", None) is None
    assert theOpts.getInt("GuiBuildNovel", "mockItem", None) is None
    assert theOpts.getFloat("GuiBuildNovel", "winWidth", None) == 100.0
    assert theOpts.getFloat("GuiBuildNovel", "textFont", None) is None
    assert theOpts.getFloat("GuiBuildNovel", "mockItem", None) is None
    assert theOpts.getBool("GuiBuildNovel", "addNovel", None) is True
    assert theOpts.getBool("GuiBuildNovel", "mockItem", None) is None
    assert theOpts.getEnum("GuiNovelView", "lastCol", NovelTreeColumn, None) == nwColHidden

    # Get from non-existent  groups
    assert theOpts.getValue("SomeGroup", "mockItem", None) is None
    assert theOpts.getString("SomeGroup", "mockItem", None) is None
    assert theOpts.getInt("SomeGroup", "mockItem", None) is None
    assert theOpts.getFloat("SomeGroup", "mockItem", None) is None
    assert theOpts.getBool("SomeGroup", "mockItem", None) is None
    assert theOpts.getEnum("SomeGroup", "mockItem", NovelTreeColumn, None) is None

# END Test testCoreOptions_SetGet
