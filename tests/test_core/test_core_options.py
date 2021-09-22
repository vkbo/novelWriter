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

from mock import causeOSError
from tools import writeFile

from novelwriter.core import NWProject
from novelwriter.core.options import OptionState
from novelwriter.constants import nwFiles


@pytest.mark.core
def testCoreOptions_LoadSave(monkeypatch, mockGUI, tmpDir):
    """Test loading and saving from the OptionState class.
    """
    theProject = NWProject(mockGUI)
    theOpts = OptionState(theProject)

    # Write a test file
    optFile = os.path.join(tmpDir, nwFiles.OPTS_FILE)
    writeFile(optFile, json.dumps({
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
    }))

    # Load and save with no path set
    theProject.projMeta = None
    assert not theOpts.loadSettings()
    assert not theOpts.saveSettings()

    # Set path
    theProject.projMeta = tmpDir
    assert theProject.projMeta == tmpDir

    # Cause open() to fail
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        assert not theOpts.loadSettings()
        assert not theOpts.saveSettings()

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

    # Set invalid values
    assert not theOpts.setValue("MockGroup", "mockItem", None)
    assert not theOpts.setValue("GuiBuildNovel", "mockItem", None)

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

    # Check integer validators
    assert theOpts.validIntRange(5, 0, 9, 3) == 5
    assert theOpts.validIntRange(5, 0, 4, 3) == 3
    assert theOpts.validIntRange(5, 0, 5, 3) == 5
    assert theOpts.validIntRange(0, 0, 5, 3) == 0

    assert theOpts.validIntTuple(0, (0, 1, 2), 3) == 0
    assert theOpts.validIntTuple(5, (0, 1, 2), 3) == 3

# END Test testCoreOptions_SetGet
