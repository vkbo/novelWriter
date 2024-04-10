"""
novelWriter – NWStatus Class Tester
===================================

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

import pytest

from tools import C

from PyQt5.QtGui import QColor, QIcon

from novelwriter.core.status import NWStatus
from novelwriter.enum import nwStatusShape

statusKeys = [C.sNew, C.sNote, C.sDraft, C.sFinished]
importKeys = [C.iNew, C.iMinor, C.iMajor, C.iMain]


@pytest.mark.core
def testCoreStatus_Internal(mockRnd):
    """Test all the internal functions of the NWStatus class."""
    nStatus = NWStatus(NWStatus.STATUS)
    nImport = NWStatus(NWStatus.IMPORT)

    with pytest.raises(Exception):
        NWStatus(999)  # type: ignore

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

# END Test testCoreStatus_Internal


@pytest.mark.core
def testCoreStatus_Iterator(mockRnd):
    """Test the iterator functions of the NWStatus class."""
    nStatus = NWStatus(NWStatus.STATUS)

    nStatus.add(None, "New",      (100, 100, 100), "SQUARE", 0)
    nStatus.add(None, "Note",     (200, 50,  0),   "SQUARE", 0)
    nStatus.add(None, "Draft",    (200, 150, 0),   "SQUARE", 0)
    nStatus.add(None, "Finished", (50,  200, 0),   "SQUARE", 0)

    # Direct access
    entry = nStatus[statusKeys[0]]
    assert entry.color == QColor(100, 100, 100)
    assert entry.name == "New"
    assert entry.count == 0
    assert isinstance(entry.icon, QIcon)

    # Length
    assert len(nStatus._store) == 4
    assert len(nStatus) == 4

# END Test testCoreStatus_Iterator


@pytest.mark.core
def testCoreStatus_Entries(mockRnd):
    """Test all the simple setters for the NWStatus class."""
    nStatus = NWStatus(NWStatus.STATUS)

    # Write
    # =====

    # Have a key
    nStatus.add(statusKeys[0], "Entry 1", (200, 100, 50), "SQUARE", 0)
    assert nStatus[statusKeys[0]].name == "Entry 1"
    assert nStatus[statusKeys[0]].color == QColor(200, 100, 50)

    # Don't have a key
    nStatus.add(None, "Entry 2", (210, 110, 60), "SQUARE", 0)
    assert nStatus[statusKeys[1]].name == "Entry 2"
    assert nStatus[statusKeys[1]].color == QColor(210, 110, 60)

    # Wrong colour spec
    nStatus.add(None, "Entry 3", "what?", "SQUARE", 0)  # type: ignore
    assert nStatus[statusKeys[2]].name == "Entry 3"
    assert nStatus[statusKeys[2]].color == QColor(100, 100, 100)

    # Wrong colour count
    nStatus.add(None, "Entry 4", (10, 20), "SQUARE", 0)  # type: ignore
    assert nStatus[statusKeys[3]].name == "Entry 4"
    assert nStatus[statusKeys[3]].color == QColor(100, 100, 100)

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

    # Reorder
    # =======

    # cOrder = list(nStatus._store.keys())
    # assert cOrder == statusKeys

    # # Wrong length
    # assert nStatus.reorder([]) is False

    # # No change
    # assert nStatus.reorder(cOrder) is False

    # # Actual re-order
    # nOrder = [
    #     statusKeys[0],
    #     statusKeys[2],
    #     statusKeys[1],
    #     statusKeys[3],
    # ]
    # assert nStatus.reorder(nOrder) is True
    # assert list(nStatus._store.keys()) == nOrder

    # # Add an unknown key
    # wOrder = nOrder.copy()
    # wOrder[3] = nStatus._newKey()
    # assert nStatus.reorder(wOrder) is False
    # assert list(nStatus._store.keys()) == nOrder

    # # Put it back
    # assert nStatus.reorder(cOrder) is True
    # assert list(nStatus._store.keys()) == cOrder

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

    # # Remove
    # # ======

    # # Non-existing entry
    # assert nStatus.remove("blablabla") is False

    # # Non-zero entry
    # nStatus.increment(statusKeys[3])
    # assert nStatus.remove(statusKeys[3]) is False

    # # Delete last entry
    # nStatus.resetCounts()
    # lastName = nStatus[statusKeys[3]].name
    # assert lastName == "Entry 4"
    # assert nStatus.remove(statusKeys[3]) is True
    # assert nStatus.check(statusKeys[3]) == nStatus._default
    # assert nStatus.check(lastName) == nStatus._default

    # # Delete default entry, Entry 2 is new default
    # firstName = nStatus[nStatus._default].name
    # assert firstName == "Entry 1"
    # assert nStatus.remove(nStatus._default) is True  # type: ignore
    # assert nStatus[firstName].name == "Entry 2"

    # # Remove remaining entries
    # assert nStatus.remove(statusKeys[1]) is True
    # assert nStatus.remove(statusKeys[2]) is True

    # assert len(nStatus) == 0
    # assert nStatus._default is None

# END Test testCoreStatus_Entries


@pytest.mark.core
def testCoreStatus_PackUnpack(mockRnd):
    """Test all the pack/unpack of the NWStatus class."""
    nStatus = NWStatus(NWStatus.STATUS)
    nStatus.add(None, "New",      (100, 100, 100), "SQUARE", 0)
    nStatus.add(None, "Note",     (200, 50,  0),   "SQUARE", 0)
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
            "shape": "SQUARE",
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

# END Test testCoreStatus_PackUnpack
