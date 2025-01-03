"""
novelWriter – NWStatus Class Tester
===================================

This file is a part of novelWriter
Copyright (C) 2020 Veronica Berglyd Olsen and novelWriter contributors

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

from PyQt5.QtGui import QColor, QIcon

from novelwriter.core.status import NWStatus, StatusEntry, _ShapeCache
from novelwriter.enum import nwStatusShape

from tests.tools import C

statusKeys = [C.sNew, C.sNote, C.sDraft, C.sFinished]
importKeys = [C.iNew, C.iMinor, C.iMajor, C.iMain]


@pytest.mark.core
def testCoreStatus_StatusEntry():
    """Test the StatusEntry class."""
    color = QColor(255, 0, 0)
    icon = NWStatus.createIcon(24, color, nwStatusShape.CIRCLE)
    entry = StatusEntry("Test", color, nwStatusShape.CIRCLE, icon, 42)

    # Check values
    assert entry.name == "Test"
    assert entry.color is color
    assert entry.shape == nwStatusShape.CIRCLE
    assert entry.icon is icon
    assert entry.count == 42

    # Make a copy
    other = StatusEntry.duplicate(entry)
    assert other is not entry

    # Check copy is not the same
    assert other.name == "Test"
    assert other.color is not color  # Not the same object
    assert other.color == color      # But same colours
    assert other.shape == nwStatusShape.CIRCLE
    assert other.icon is not icon    # Not the same icon, but a copy
    assert other.count == 42


@pytest.mark.core
def testCoreStatus_Internal(mockGUI, mockRnd):
    """Test all the internal functions of the NWStatus class."""
    nStatus = NWStatus(NWStatus.STATUS)
    nImport = NWStatus(NWStatus.IMPORT)

    # Generate Key
    # ============

    assert nStatus._newKey() == statusKeys[0]
    assert nStatus._newKey() == statusKeys[1]

    # Key collision, should move to key 3
    nStatus.add(statusKeys[2], "Crash", (0, 0, 0), "SQUARE", 0)
    assert nStatus._newKey() == statusKeys[3]

    assert nImport._newKey() == importKeys[0]
    assert nImport._newKey() == importKeys[1]

    # Key collision, should move to key 3
    nImport.add(importKeys[2], "Crash", (0, 0, 0), "SQUARE", 0)
    assert nImport._newKey() == importKeys[3]

    # Check Key
    # =========

    assert nStatus._isKey(None) is False        # Not a string
    assert nStatus._isKey("s00000") is False    # Too short
    assert nStatus._isKey("s000000") is True    # Correct length
    assert nStatus._isKey("s0000000") is False  # Too long
    assert nStatus._isKey("i000000") is False   # Wrong type
    assert nStatus._isKey("q000000") is False   # Wrong type
    assert nStatus._isKey("s12345H") is False   # Not a hex value
    assert nStatus._isKey("s12345F") is False   # Not a lower case hex value
    assert nStatus._isKey("s12345f") is True    # Valid hex value

    assert nImport._isKey(None) is False        # Not a string
    assert nImport._isKey("i00000") is False    # Too short
    assert nImport._isKey("i000000") is True    # Correct length
    assert nImport._isKey("i0000000") is False  # Too long
    assert nImport._isKey("s000000") is False   # Wrong type
    assert nImport._isKey("q000000") is False   # Wrong type
    assert nImport._isKey("i12345H") is False   # Not a hex value
    assert nImport._isKey("i12345F") is False   # Not a lower case hex value
    assert nImport._isKey("i12345f") is True    # Valid hex value

    assert nStatus._checkKey(None) == "s000008"       # Creates next key
    assert nStatus._checkKey("s654321") == "s654321"  # Status key accepted
    assert nStatus._checkKey("i123456") == "s000009"  # Import key not accepted

    assert nImport._checkKey(None) == "i00000a"       # Creates next key
    assert nImport._checkKey("s654321") == "i00000b"  # Status key not accepted
    assert nImport._checkKey("i123456") == "i123456"  # Import key accepted


@pytest.mark.core
def testCoreStatus_Iterator(mockGUI, mockRnd):
    """Test the iterator functions of the NWStatus class."""
    nStatus = NWStatus(NWStatus.STATUS)
    nStatus.add(None, "New",      (100, 100, 100), "SQUARE", 0)
    nStatus.add(None, "Note",     (200, 50,  0),   "CIRCLE", 1)
    nStatus.add(None, "Draft",    (200, 150, 0),   "SQUARE", 2)
    nStatus.add(None, "Finished", (50,  200, 0),   "CIRCLE", 3)

    # Direct access
    entry = nStatus[statusKeys[0]]
    assert entry.color == QColor(100, 100, 100)
    assert entry.name == "New"
    assert entry.count == 0
    assert isinstance(entry.icon, QIcon)

    # Length
    assert len(nStatus._store) == 4
    assert len(nStatus) == 4

    # Content : Keys
    assert [k for k, _ in nStatus.iterItems()] == [
        "s000000", "s000001", "s000002", "s000003"
    ]

    # Content : Names
    assert [e.name for _, e in nStatus.iterItems()] == [
        "New", "Note", "Draft", "Finished"
    ]

    # Content : Colours
    assert [e.color for _, e in nStatus.iterItems()] == [
        QColor(100, 100, 100), QColor(200, 50,  0), QColor(200, 150, 0), QColor(50,  200, 0)
    ]

    # Content : Shape
    assert [e.shape for _, e in nStatus.iterItems()] == [
        nwStatusShape.SQUARE, nwStatusShape.CIRCLE, nwStatusShape.SQUARE, nwStatusShape.CIRCLE
    ]

    # Content : Count
    assert [e.count for _, e in nStatus.iterItems()] == [0, 1, 2, 3]


@pytest.mark.core
def testCoreStatus_Entries(mockGUI, mockRnd):
    """Test all the simple setters for the NWStatus class."""
    nStatus = NWStatus(NWStatus.STATUS)

    # Add
    # ===

    # Has a key
    nStatus.add(statusKeys[0], "Entry 1", (200, 100, 50), "SQUARE", 0)
    assert nStatus[statusKeys[0]].name == "Entry 1"
    assert nStatus[statusKeys[0]].color == QColor(200, 100, 50)
    assert nStatus[statusKeys[0]].shape == nwStatusShape.SQUARE

    # Doesn't have a key
    nStatus.add(None, "Entry 2", (210, 110, 60), "SQUARE", 0)
    assert nStatus[statusKeys[1]].name == "Entry 2"
    assert nStatus[statusKeys[1]].color == QColor(210, 110, 60)
    assert nStatus[statusKeys[1]].shape == nwStatusShape.SQUARE

    # Wrong colour spec, unknown shape
    nStatus.add(None, "Entry 3", "what?", "", 0)  # type: ignore
    assert nStatus[statusKeys[2]].name == "Entry 3"
    assert nStatus[statusKeys[2]].color == QColor(100, 100, 100)
    assert nStatus[statusKeys[2]].shape == nwStatusShape.SQUARE

    # Wrong colour count
    nStatus.add(None, "Entry 4", (10, 20), "CIRCLE", 0)  # type: ignore
    assert nStatus[statusKeys[3]].name == "Entry 4"
    assert nStatus[statusKeys[3]].color == QColor(100, 100, 100)
    assert nStatus[statusKeys[3]].shape == nwStatusShape.CIRCLE

    # Check
    # =====

    # Normal lookup
    for key in statusKeys:
        assert nStatus.check(key) == key

    # Non-existing name
    assert nStatus.check("s987654") == statusKeys[0]

    # Name Access
    # ===========

    assert nStatus[statusKeys[0]].name == "Entry 1"
    assert nStatus[statusKeys[1]].name == "Entry 2"
    assert nStatus[statusKeys[2]].name == "Entry 3"
    assert nStatus[statusKeys[3]].name == "Entry 4"
    assert nStatus["blablabla"].name == "Entry 1"

    # Colour Access
    # =============

    assert nStatus[statusKeys[0]].color == QColor(200, 100, 50)
    assert nStatus[statusKeys[1]].color == QColor(210, 110, 60)
    assert nStatus[statusKeys[2]].color == QColor(100, 100, 100)
    assert nStatus[statusKeys[3]].color == QColor(100, 100, 100)
    assert nStatus["blablabla"].color == QColor(200, 100, 50)

    # Icon Access
    # ===========

    assert isinstance(nStatus[statusKeys[0]].icon, QIcon)
    assert isinstance(nStatus[statusKeys[1]].icon, QIcon)
    assert isinstance(nStatus[statusKeys[2]].icon, QIcon)
    assert isinstance(nStatus[statusKeys[3]].icon, QIcon)
    assert isinstance(nStatus["blablabla"].icon, QIcon)

    # Shape Access
    # ============

    assert nStatus[statusKeys[0]].shape == nwStatusShape.SQUARE
    assert nStatus[statusKeys[1]].shape == nwStatusShape.SQUARE
    assert nStatus[statusKeys[2]].shape == nwStatusShape.SQUARE
    assert nStatus[statusKeys[3]].shape == nwStatusShape.CIRCLE
    assert nStatus["blablabla"].shape == nwStatusShape.SQUARE

    # Increment and Count Access
    # ==========================

    countTo = [3, 5, 7, 9]
    for i, n in enumerate(countTo):
        for _ in range(n):
            nStatus.increment(statusKeys[i])

    assert nStatus[statusKeys[0]].count == countTo[0]
    assert nStatus[statusKeys[1]].count == countTo[1]
    assert nStatus[statusKeys[2]].count == countTo[2]
    assert nStatus[statusKeys[3]].count == countTo[3]
    assert nStatus["blablabla"].count == countTo[0]

    nStatus.resetCounts()

    assert nStatus[statusKeys[0]].count == 0
    assert nStatus[statusKeys[1]].count == 0
    assert nStatus[statusKeys[2]].count == 0
    assert nStatus[statusKeys[3]].count == 0

    # Update
    # ======

    assert list(nStatus._store.keys()) == statusKeys

    # Reverse
    order: list[tuple[str | None, StatusEntry]] = list(nStatus.iterItems())
    nStatus.update(list(reversed(order)))
    assert list(nStatus._store.keys()) == list(reversed(statusKeys))

    # Restore
    nStatus.update(order)
    assert list(nStatus._store.keys()) == statusKeys

    # Default
    # =======

    default = nStatus._default
    nStatus._default = None

    assert nStatus.check("Entry 5") == ""
    assert nStatus["blablabla"].name == ""
    assert nStatus["blablabla"].color == QColor(0, 0, 0)
    assert nStatus["blablabla"].shape == nwStatusShape.SQUARE
    assert nStatus["blablabla"].icon.isNull()
    assert nStatus["blablabla"].count == 0

    nStatus._default = default

    # Remove
    # ======
    # This uses update with deleted items

    order: list[tuple[str | None, StatusEntry]] = list(nStatus.iterItems())

    # Remove Entry 0
    nStatus.update([order[1], order[3], order[2]])
    assert list(nStatus._store.keys()) == [statusKeys[1], statusKeys[3], statusKeys[2]]
    assert nStatus._default == statusKeys[1]

    # Remove Entry 1
    nStatus.update([order[3], order[2]])
    assert list(nStatus._store.keys()) == [statusKeys[3], statusKeys[2]]
    assert nStatus._default == statusKeys[3]

    # Create
    # ======

    # A valid entry
    entry = nStatus.fromRaw(["STAR", "#ff7f00", "Test"])
    assert entry is not None
    assert entry.shape == nwStatusShape.STAR
    assert entry.color == QColor(255, 127, 0)
    assert entry.name == "Test"

    # Invalid entries
    assert nStatus.fromRaw(["STAR", "#ff7f00"]) is None
    assert nStatus.fromRaw(["STUFF", "#ff7f00", "Test"]) is None


@pytest.mark.core
def testCoreStatus_Pack(mockGUI, mockRnd):
    """Test data packing of the NWStatus class."""
    nStatus = NWStatus(NWStatus.STATUS)
    nStatus.add(None, "New",      (100, 100, 100), "SQUARE", 0)
    nStatus.add(None, "Note",     (200, 50,  0),   "CIRCLE", 0)
    nStatus.add(None, "Draft",    (200, 150, 0),   "SQUARE", 0)
    nStatus.add(None, "Finished", (50,  200, 0),   "SQUARE", 0)

    countTo = [3, 5, 7, 9]
    for i, n in enumerate(countTo):
        for _ in range(n):
            nStatus.increment(statusKeys[i])

    # Pack
    assert list(nStatus.pack()) == [
        ("New", {
            "key": statusKeys[0],
            "count": "3",
            "red": "100",
            "green": "100",
            "blue": "100",
            "shape": "SQUARE",
        }),
        ("Note", {
            "key": statusKeys[1],
            "count": "5",
            "red": "200",
            "green": "50",
            "blue": "0",
            "shape": "CIRCLE",
        }),
        ("Draft", {
            "key": statusKeys[2],
            "count": "7",
            "red": "200",
            "green": "150",
            "blue": "0",
            "shape": "SQUARE",
        }),
        ("Finished", {
            "key": statusKeys[3],
            "count": "9",
            "red": "50",
            "green": "200",
            "blue": "0",
            "shape": "SQUARE",
        }),
    ]


@pytest.mark.core
def testCoreStatus_ShapeCache():
    """Test the _ShapeCache class."""
    shapes = _ShapeCache()

    # Generate all shapes
    square    = shapes.getShape(nwStatusShape.SQUARE)
    circleQ   = shapes.getShape(nwStatusShape.CIRCLE_Q)
    circleH   = shapes.getShape(nwStatusShape.CIRCLE_H)
    circleT   = shapes.getShape(nwStatusShape.CIRCLE_T)
    circle    = shapes.getShape(nwStatusShape.CIRCLE)
    triangle  = shapes.getShape(nwStatusShape.TRIANGLE)
    nabla     = shapes.getShape(nwStatusShape.NABLA)
    diamond   = shapes.getShape(nwStatusShape.DIAMOND)
    pentagon  = shapes.getShape(nwStatusShape.PENTAGON)
    hexagon   = shapes.getShape(nwStatusShape.HEXAGON)
    star      = shapes.getShape(nwStatusShape.STAR)
    pacman    = shapes.getShape(nwStatusShape.PACMAN)
    bars1     = shapes.getShape(nwStatusShape.BARS_1)
    bars2     = shapes.getShape(nwStatusShape.BARS_2)
    bars3     = shapes.getShape(nwStatusShape.BARS_3)
    bars4     = shapes.getShape(nwStatusShape.BARS_4)
    block1    = shapes.getShape(nwStatusShape.BLOCK_1)
    block2    = shapes.getShape(nwStatusShape.BLOCK_2)
    block3    = shapes.getShape(nwStatusShape.BLOCK_3)
    block4    = shapes.getShape(nwStatusShape.BLOCK_4)

    # Request again should return from cache
    assert shapes.getShape(nwStatusShape.SQUARE) is square
    assert shapes.getShape(nwStatusShape.CIRCLE_Q) is circleQ
    assert shapes.getShape(nwStatusShape.CIRCLE_H) is circleH
    assert shapes.getShape(nwStatusShape.CIRCLE_T) is circleT
    assert shapes.getShape(nwStatusShape.CIRCLE) is circle
    assert shapes.getShape(nwStatusShape.TRIANGLE) is triangle
    assert shapes.getShape(nwStatusShape.NABLA) is nabla
    assert shapes.getShape(nwStatusShape.DIAMOND) is diamond
    assert shapes.getShape(nwStatusShape.PENTAGON) is pentagon
    assert shapes.getShape(nwStatusShape.HEXAGON) is hexagon
    assert shapes.getShape(nwStatusShape.STAR) is star
    assert shapes.getShape(nwStatusShape.PACMAN) is pacman
    assert shapes.getShape(nwStatusShape.BARS_1) is bars1
    assert shapes.getShape(nwStatusShape.BARS_2) is bars2
    assert shapes.getShape(nwStatusShape.BARS_3) is bars3
    assert shapes.getShape(nwStatusShape.BARS_4) is bars4
    assert shapes.getShape(nwStatusShape.BLOCK_1) is block1
    assert shapes.getShape(nwStatusShape.BLOCK_2) is block2
    assert shapes.getShape(nwStatusShape.BLOCK_3) is block3
    assert shapes.getShape(nwStatusShape.BLOCK_4) is block4
