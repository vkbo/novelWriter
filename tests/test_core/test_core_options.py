# -*- coding: utf-8 -*-
"""
novelWriter – OptionState Class Tester
======================================

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
import json
import pytest

from dummy import causeOSError

from nw.core import NWProject
from nw.core.options import OptionState
from nw.constants import nwFiles

@pytest.mark.core
def testCoreOptions_LoadSave(monkeypatch, dummyGUI, tmpDir):
    """Test loading and saving from the OptionState class.
    """
    theProject = NWProject(dummyGUI)
    theOpts = OptionState(theProject)

    # Write a test file
    optFile = os.path.join(tmpDir, nwFiles.OPTS_FILE)
    with open(optFile, mode="w+", encoding="utf8") as outFile:
        json.dump({
            "GuiBuildNovel": {
                "winWidth": 1000,
                "winHeight": 700,
                "addNovel": True,
                "addNotes": False,
                "textFont": "Cantarell",
                "dummyItem": None,
            },
            "DummyGroup": {
                "dummyItem": None,
            },
        }, outFile)

    # Load and save with no path set
    theProject.projMeta = None
    assert not theOpts.loadSettings()
    assert not theOpts.saveSettings()

    # Set path
    theProject.projMeta = tmpDir
    assert theProject.projMeta == tmpDir

    # Cause open() to fail
    monkeypatch.setattr("builtins.open", causeOSError)
    assert not theOpts.loadSettings()
    assert not theOpts.saveSettings()
    monkeypatch.undo()

    # Load proper
    assert theOpts.loadSettings()

    # Check that unwanted items have been removed
    assert theOpts.theState == {
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
    assert theOpts.theState == {
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
def testCoreOptions_SetGet(monkeypatch, dummyGUI, tmpDir):
    """Test setting and getting values from the OptionState class.
    """
    theProject = NWProject(dummyGUI)
    theOpts = OptionState(theProject)

    # Set invalid values
    assert not theOpts.setValue("DummyGroup", "dummyItem", None)
    assert not theOpts.setValue("GuiBuildNovel", "dummyItem", None)

    # Set valid value
    assert theOpts.setValue("GuiBuildNovel", "winWidth", 100)

    # Set some values of different types
    assert theOpts.setValue("GuiBuildNovel", "winWidth", 100)
    assert theOpts.setValue("GuiBuildNovel", "winHeight", 12.34)
    assert theOpts.setValue("GuiBuildNovel", "addNovel", True)
    assert theOpts.setValue("GuiBuildNovel", "textFont", "Cantarell")

    # Generic get, doesn't check type
    assert theOpts.getValue("GuiBuildNovel", "winWidth", None) == 100
    assert theOpts.getValue("GuiBuildNovel", "winHeight", None) == 12.34
    assert theOpts.getValue("GuiBuildNovel", "addNovel", None) is True
    assert theOpts.getValue("GuiBuildNovel", "textFont", None) == "Cantarell"
    assert theOpts.getValue("GuiBuildNovel", "dummyItem", None) is None

    # Get type-specific
    assert theOpts.getString("GuiBuildNovel", "winWidth", None) == "100"
    assert theOpts.getString("GuiBuildNovel", "dummyItem", None) is None
    assert theOpts.getInt("GuiBuildNovel", "winWidth", None) == 100
    assert theOpts.getInt("GuiBuildNovel", "textFont", None) is None
    assert theOpts.getInt("GuiBuildNovel", "dummyItem", None) is None
    assert theOpts.getFloat("GuiBuildNovel", "winWidth", None) == 100.0
    assert theOpts.getFloat("GuiBuildNovel", "textFont", None) is None
    assert theOpts.getFloat("GuiBuildNovel", "dummyItem", None) is None
    assert theOpts.getBool("GuiBuildNovel", "addNovel", None) is True
    assert theOpts.getBool("GuiBuildNovel", "dummyItem", None) is None

    # Check integer validators
    assert theOpts.validIntRange(5, 0, 9, 3) == 5
    assert theOpts.validIntRange(5, 0, 4, 3) == 3
    assert theOpts.validIntRange(5, 0, 5, 3) == 5
    assert theOpts.validIntRange(0, 0, 5, 3) == 0

    assert theOpts.validIntTuple(0, (0, 1, 2), 3) == 0
    assert theOpts.validIntTuple(5, (0, 1, 2), 3) == 3

# END Test testCoreOptions_SetGet
