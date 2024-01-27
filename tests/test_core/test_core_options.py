"""
novelWriter – OptionState Class Tester
======================================

This file is a part of novelWriter
Copyright 2018–2024, Veronica Berglyd Olsen

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
    project = NWProject()
    options = OptionState(project)

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
    project.storage._runtimePath = None
    assert options.loadSettings() is False
    assert options.saveSettings() is False

    # Set path
    project.storage._runtimePath = fncPath
    project.storage._ready = True
    assert project.storage.getMetaFile(nwFiles.OPTS_FILE) == optFile

    # Cause open() to fail
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        assert options.loadSettings() is False
        assert options.saveSettings() is False

    # Load proper
    assert options.loadSettings()

    # Check that unwanted items have been removed
    assert options._state == {
        "GuiProjectSettings": {
            "winWidth": 570,
            "winHeight": 375,
            "replaceColW": 130,
            "statusColW": 130,
            "importColW": 130
        },
    }

    # Save proper
    assert options.saveSettings()

    # Load again to check we get the values back
    assert options.loadSettings()
    assert options._state == {
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
    project = NWProject()
    options = OptionState(project)

    nwColHidden = NovelTreeColumn.HIDDEN

    # Set invalid values
    assert options.setValue("MockGroup", "mockItem", None) is False
    assert options.setValue("GuiProjectSettings", "mockItem", None) is False

    # Set valid value
    assert options.setValue("GuiProjectSettings", "winWidth", 100) is True

    # Set some values of different types
    assert options.setValue("GuiNovelDetails", "winWidth", 100) is True
    assert options.setValue("GuiNovelDetails", "winHeight", 12.34) is True
    assert options.setValue("GuiNovelDetails", "clearDouble", True) is True
    assert options.setValue("GuiNovelView", "lastCol", nwColHidden) is True

    # Generic get, doesn't check type
    assert options.getValue("GuiNovelDetails", "winWidth", None) == 100
    assert options.getValue("GuiNovelDetails", "winHeight", None) == 12.34
    assert options.getValue("GuiNovelDetails", "clearDouble", None) is True
    assert options.getValue("GuiNovelDetails", "mockItem", None) is None

    # Get type-specific
    assert options.getString("GuiNovelDetails", "winWidth", None) is None  # type: ignore
    assert options.getString("GuiNovelDetails", "mockItem", None) is None  # type: ignore
    assert options.getInt("GuiNovelDetails", "winWidth", None) == 100  # type: ignore
    assert options.getInt("GuiNovelDetails", "textFont", None) is None  # type: ignore
    assert options.getInt("GuiNovelDetails", "mockItem", None) is None  # type: ignore
    assert options.getFloat("GuiNovelDetails", "winWidth", None) == 100.0  # type: ignore
    assert options.getFloat("GuiNovelDetails", "mockItem", None) is None  # type: ignore
    assert options.getBool("GuiNovelDetails", "clearDouble", None) is True  # type: ignore
    assert options.getBool("GuiNovelDetails", "mockItem", None) is None  # type: ignore
    assert options.getEnum("GuiNovelView", "lastCol", NovelTreeColumn, nwColHidden) == nwColHidden

    # Get from non-existent  groups
    assert options.getValue("SomeGroup", "mockItem", None) is None
    assert options.getString("SomeGroup", "mockItem", None) is None  # type: ignore
    assert options.getInt("SomeGroup", "mockItem", None) is None  # type: ignore
    assert options.getFloat("SomeGroup", "mockItem", None) is None  # type: ignore
    assert options.getBool("SomeGroup", "mockItem", None) is None  # type: ignore
    assert options.getEnum("SomeGroup", "mockItem", NovelTreeColumn, None) is None  # type: ignore

# END Test testCoreOptions_SetGet
