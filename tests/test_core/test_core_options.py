"""
novelWriter – OptionState Class Tester
======================================

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

import json
import pytest

from mocked import causeOSError

from novelwriter.constants import nwFiles
from novelwriter.core.options import OptionState
from novelwriter.core.project import NWProject
from novelwriter.gui.noveltree import NovelTreeColumn


@pytest.mark.core
def testCoreOptions_LoadSave(monkeypatch, mockGUI, fncPath):
    """Test loading and saving from the OptionState class."""
    theProject = NWProject()
    theOpts = OptionState(theProject)

    metaDir = fncPath / "meta"
    metaDir.mkdir()

    # Write a test file
    optFile = metaDir / nwFiles.OPTS_FILE
    optFile.write_text(json.dumps({
        "novelWriter.guiOptions": {
            "GuiProjectSettings": {
                "winWidth": 570,
                "winHeight": 375,
                "replaceColW": 130,
                "statusColW": 130,
                "importColW": 130
            },
            "MockGroup": {
                "mockItem": None,
            },
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
    assert theOpts._state == {
        "GuiProjectSettings": {
            "winWidth": 570,
            "winHeight": 375,
            "replaceColW": 130,
            "statusColW": 130,
            "importColW": 130
        },
    }

    # Save proper
    assert theOpts.saveSettings()

    # Load again to check we get the values back
    assert theOpts.loadSettings()
    assert theOpts._state == {
        "GuiProjectSettings": {
            "winWidth": 570,
            "winHeight": 375,
            "replaceColW": 130,
            "statusColW": 130,
            "importColW": 130
        },
    }

# END Test testCoreOptions_LoadSave


@pytest.mark.core
def testCoreOptions_SetGet(mockGUI):
    """Test setting and getting values from the OptionState class."""
    theProject = NWProject()
    theOpts = OptionState(theProject)

    nwColHidden = NovelTreeColumn.HIDDEN

    # Set invalid values
    assert theOpts.setValue("MockGroup", "mockItem", None) is False
    assert theOpts.setValue("GuiProjectSettings", "mockItem", None) is False

    # Set valid value
    assert theOpts.setValue("GuiProjectSettings", "winWidth", 100) is True

    # Set some values of different types
    assert theOpts.setValue("GuiProjectDetails", "winWidth", 100) is True
    assert theOpts.setValue("GuiProjectDetails", "winHeight", 12.34) is True
    assert theOpts.setValue("GuiProjectDetails", "clearDouble", True) is True
    assert theOpts.setValue("GuiNovelView", "lastCol", nwColHidden) is True

    # Generic get, doesn't check type
    assert theOpts.getValue("GuiProjectDetails", "winWidth", None) == 100
    assert theOpts.getValue("GuiProjectDetails", "winHeight", None) == 12.34
    assert theOpts.getValue("GuiProjectDetails", "clearDouble", None) is True
    assert theOpts.getValue("GuiProjectDetails", "mockItem", None) is None

    # Get type-specific
    assert theOpts.getString("GuiProjectDetails", "winWidth", None) is None
    assert theOpts.getString("GuiProjectDetails", "mockItem", None) is None
    assert theOpts.getInt("GuiProjectDetails", "winWidth", None) == 100
    assert theOpts.getInt("GuiProjectDetails", "textFont", None) is None
    assert theOpts.getInt("GuiProjectDetails", "mockItem", None) is None
    assert theOpts.getFloat("GuiProjectDetails", "winWidth", None) == 100.0
    assert theOpts.getFloat("GuiProjectDetails", "mockItem", None) is None
    assert theOpts.getBool("GuiProjectDetails", "clearDouble", None) is True
    assert theOpts.getBool("GuiProjectDetails", "mockItem", None) is None
    assert theOpts.getEnum("GuiNovelView", "lastCol", NovelTreeColumn, None) == nwColHidden

    # Get from non-existent  groups
    assert theOpts.getValue("SomeGroup", "mockItem", None) is None
    assert theOpts.getString("SomeGroup", "mockItem", None) is None
    assert theOpts.getInt("SomeGroup", "mockItem", None) is None
    assert theOpts.getFloat("SomeGroup", "mockItem", None) is None
    assert theOpts.getBool("SomeGroup", "mockItem", None) is None
    assert theOpts.getEnum("SomeGroup", "mockItem", NovelTreeColumn, None) is None

# END Test testCoreOptions_SetGet
