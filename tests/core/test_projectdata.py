"""
novelWriter – Project Data Class Tester
=======================================

This file is a part of novelWriter
Copyright (C) 2026 Veronica Berglyd Olsen and novelWriter contributors

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
"""  # noqa

from __future__ import annotations

import pytest

from novelwriter.core.projectdata import NWProjectData


class MockProject:
    """Fake project object that just counts change notifications."""

    def __init__(self) -> None:
        self.changed = 0

    def setProjectChanged(self, state: bool) -> None:
        """Fake project method."""
        self.changed += 1 if state else 0


@pytest.mark.core
def testNWProjectData_Uuid(mockGUI):
    """Test the setUuid setter."""
    project = MockProject()
    data = NWProjectData(project)  # type: ignore

    # An empty/invalid value generates a new uuid
    data.setUuid("not-a-uuid")
    assert data.uuid != ""
    firstUuid = data.uuid

    # Setting the same uuid again does nothing
    project.changed = 0
    data.setUuid(firstUuid)
    assert data.uuid == firstUuid
    assert project.changed == 0

    # Setting a new, valid uuid updates it and flags the change
    data.setUuid("d0f3fe10-c6e6-4310-8bfd-181eb4224eed")
    assert data.uuid == "d0f3fe10-c6e6-4310-8bfd-181eb4224eed"
    assert project.changed == 1


@pytest.mark.core
def testNWProjectData_Language(mockGUI):
    """Test the setLanguage setter."""
    project = MockProject()
    data = NWProjectData(project)  # type: ignore

    data.setLanguage("en_GB")
    assert data.language == "en_GB"

    # Setting the same language again does nothing
    project.changed = 0
    data.setLanguage("en_GB")
    assert data.language == "en_GB"
    assert project.changed == 0


@pytest.mark.core
def testNWProjectData_LastHandle(mockGUI):
    """Test the setLastHandle and setLastHandles setters."""
    project = MockProject()
    data = NWProjectData(project)  # type: ignore

    # Setting with a non-string component does nothing
    project.changed = 0
    data.setLastHandle("0123456789abc", None)  # type: ignore
    assert project.changed == 0

    # Setting with a valid component works
    data.setLastHandle("0123456789abc", "editor")
    assert data.getLastHandle("editor") == "0123456789abc"

    # setLastHandles requires a dict
    project.changed = 0
    data.setLastHandles(["not", "a", "dict"])  # type: ignore
    assert project.changed == 0

    # Unknown keys in the dict are skipped, known keys are updated
    data.setLastHandles({"unknownKey": "0123456789abc", "editor": "0123456789abd"})
    assert data.getLastHandle("editor") == "0123456789abd"


@pytest.mark.core
def testNWProjectData_CurrCounts(mockGUI):
    """Test the setCurrCounts setter."""
    project = MockProject()
    data = NWProjectData(project)  # type: ignore

    data.setCurrCounts(1, 2, 3, 4)
    assert data.currCounts == (1, 2, 3, 4)

    # Only the given values are updated, others are left as-is
    data.setCurrCounts(wNovel=None, wNotes=None, cNovel=9, cNotes=None)
    assert data.currCounts == (1, 2, 9, 4)


@pytest.mark.core
def testNWProjectData_AutoReplace(mockGUI):
    """Test the setAutoReplace setter."""
    project = MockProject()
    data = NWProjectData(project)  # type: ignore

    # Requires a dict
    project.changed = 0
    data.setAutoReplace(["not", "a", "dict"])  # type: ignore
    assert project.changed == 0
    assert data.autoReplace == {}

    # Non-string entries are skipped
    data.setAutoReplace({"A": "B", "C": 123})  # type: ignore
    assert data.autoReplace == {"A": "B"}
