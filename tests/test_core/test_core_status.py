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

from PyQt5.QtGui import QIcon

from novelwriter.core.status import NWStatus

statusKeys = [C.sNew, C.sNote, C.sDraft, C.sFinished]
importKeys = [C.iNew, C.iMinor, C.iMajor, C.iMain]


@pytest.mark.core
def testCoreStatus_Internal(mockRnd):
    """Test all the internal functions of the NWStatus class.
    """
    nStatus = NWStatus(NWStatus.STATUS)
    nImport = NWStatus(NWStatus.IMPORT)

    with pytest.raises(Exception):
        NWStatus(999)

    # Generate Key
    # ============

    assert nStatus._newKey() == statusKeys[0]
    assert nStatus._newKey() == statusKeys[1]

    # Key collision, should move to key 3
    nStatus.write(statusKeys[2], "Crash", (0, 0, 0))
    assert nStatus._newKey() == statusKeys[3]

    assert nImport._newKey() == importKeys[0]
    assert nImport._newKey() == importKeys[1]

    # Key collision, should move to key 3
    nImport.write(importKeys[2], "Crash", (0, 0, 0))
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
    """Test the iterator functions of the NWStatus class.
    """
    nStatus = NWStatus(NWStatus.STATUS)

    nStatus.write(None, "New",      (100, 100, 100))
    nStatus.write(None, "Note",     (200, 50,  0))
    nStatus.write(None, "Draft",    (200, 150, 0))
    nStatus.write(None, "Finished", (50,  200, 0))

    # Direct access
    entry = nStatus[statusKeys[0]]
    assert entry["cols"] == (100, 100, 100)
    assert entry["name"] == "New"
    assert entry["count"] == 0
    assert isinstance(entry["icon"], QIcon)

    # Iterate
    entries = list(nStatus)
    assert len(entries) == 4
    assert len(nStatus) == 4

    # Keys
    assert list(nStatus.keys()) == statusKeys

    # Items
    for index, (key, entry) in enumerate(nStatus.items()):
        assert key == statusKeys[index]
        assert "cols" in entry
        assert "name" in entry
        assert "count" in entry
        assert "icon" in entry

    # Valuse
    for entry in nStatus.values():
        assert "cols" in entry
        assert "name" in entry
        assert "count" in entry
        assert "icon" in entry

# END Test testCoreStatus_Iterator


@pytest.mark.core
def testCoreStatus_Entries(mockRnd):
    """Test all the simple setters for the NWStatus class.
    """
    nStatus = NWStatus(NWStatus.STATUS)

    # Write
    # =====

    # Have a key
    nStatus.write(statusKeys[0], "Entry 1", (200, 100, 50))
    assert nStatus[statusKeys[0]]["name"] == "Entry 1"
    assert nStatus[statusKeys[0]]["cols"] == (200, 100, 50)

    # Don't have a key
    nStatus.write(None, "Entry 2", (210, 110, 60))
    assert nStatus[statusKeys[1]]["name"] == "Entry 2"
    assert nStatus[statusKeys[1]]["cols"] == (210, 110, 60)

    # Wrong colour spec
    nStatus.write(None, "Entry 3", "what?")
    assert nStatus[statusKeys[2]]["name"] == "Entry 3"
    assert nStatus[statusKeys[2]]["cols"] == (100, 100, 100)

    # Wrong colour count
    nStatus.write(None, "Entry 4", (10, 20))
    assert nStatus[statusKeys[3]]["name"] == "Entry 4"
    assert nStatus[statusKeys[3]]["cols"] == (100, 100, 100)

    # Check
    # =====

    # Normal lookup
    for key in statusKeys:
        assert nStatus.check(key) == key

    # Non-existing name
    assert nStatus.check("s987654") == statusKeys[0]

    # Name Access
    # ===========

    assert nStatus.name(statusKeys[0]) == "Entry 1"
    assert nStatus.name(statusKeys[1]) == "Entry 2"
    assert nStatus.name(statusKeys[2]) == "Entry 3"
    assert nStatus.name(statusKeys[3]) == "Entry 4"
    assert nStatus.name("blablabla") == "Entry 1"

    # Colour Access
    # =============

    assert nStatus.cols(statusKeys[0]) == (200, 100, 50)
    assert nStatus.cols(statusKeys[1]) == (210, 110, 60)
    assert nStatus.cols(statusKeys[2]) == (100, 100, 100)
    assert nStatus.cols(statusKeys[3]) == (100, 100, 100)
    assert nStatus.cols("blablabla") == (200, 100, 50)

    # Icon Access
    # ===========

    assert isinstance(nStatus.icon(statusKeys[0]), QIcon)
    assert isinstance(nStatus.icon(statusKeys[1]), QIcon)
    assert isinstance(nStatus.icon(statusKeys[2]), QIcon)
    assert isinstance(nStatus.icon(statusKeys[3]), QIcon)
    assert isinstance(nStatus.icon("blablabla"), QIcon)

    # Increment and Count Access
    # ==========================

    countTo = [3, 5, 7, 9]
    for i, n in enumerate(countTo):
        for _ in range(n):
            nStatus.increment(statusKeys[i])

    assert nStatus.count(statusKeys[0]) == countTo[0]
    assert nStatus.count(statusKeys[1]) == countTo[1]
    assert nStatus.count(statusKeys[2]) == countTo[2]
    assert nStatus.count(statusKeys[3]) == countTo[3]
    assert nStatus.count("blablabla") == countTo[0]

    nStatus.resetCounts()

    assert nStatus.count(statusKeys[0]) == 0
    assert nStatus.count(statusKeys[1]) == 0
    assert nStatus.count(statusKeys[2]) == 0
    assert nStatus.count(statusKeys[3]) == 0

    # Reorder
    # =======

    cOrder = list(nStatus.keys())
    assert cOrder == statusKeys

    # Wrong length
    assert nStatus.reorder([]) is False

    # No change
    assert nStatus.reorder(cOrder) is False

    # Actual reaorder
    nOrder = [
        statusKeys[0],
        statusKeys[2],
        statusKeys[1],
        statusKeys[3],
    ]
    assert nStatus.reorder(nOrder) is True
    assert list(nStatus.keys()) == nOrder

    # Add an unknown key
    wOrder = nOrder.copy()
    wOrder[3] = nStatus._newKey()
    assert nStatus.reorder(wOrder) is False
    assert list(nStatus.keys()) == nOrder

    # Put it back
    assert nStatus.reorder(cOrder) is True
    assert list(nStatus.keys()) == cOrder

    # Default
    # =======

    default = nStatus._default
    nStatus._default = None

    assert nStatus.check("Entry 5") == ""
    assert nStatus.name("blablabla") == ""
    assert nStatus.cols("blablabla") == (100, 100, 100)
    assert nStatus.count("blablabla") == 0
    assert isinstance(nStatus.icon("blablabla"), QIcon)

    nStatus._default = default

    # Remove
    # ======

    # Non-existing entry
    assert nStatus.remove("blablabla") is False

    # Non-zero entry
    nStatus.increment(statusKeys[3])
    assert nStatus.remove(statusKeys[3]) is False

    # Delete last entry
    nStatus.resetCounts()
    lastName = nStatus.name(statusKeys[3])
    assert lastName == "Entry 4"
    assert nStatus.remove(statusKeys[3]) is True
    assert nStatus.check(statusKeys[3]) == nStatus._default
    assert nStatus.check(lastName) == nStatus._default

    # Delete default entry, Entry 2 is new default
    firstName = nStatus.name(nStatus._default)
    assert firstName == "Entry 1"
    assert nStatus.remove(nStatus._default) is True
    assert nStatus.name(firstName) == "Entry 2"

    # Remove remaining entries
    assert nStatus.remove(statusKeys[1]) is True
    assert nStatus.remove(statusKeys[2]) is True

    assert len(nStatus) == 0
    assert nStatus._default is None

# END Test testCoreStatus_Entries


@pytest.mark.core
def testCoreStatus_PackUnpack(mockRnd):
    """Test all the pack/unpack of the NWStatus class.
    """
    nStatus = NWStatus(NWStatus.STATUS)
    nStatus.write(None, "New",      (100, 100, 100))
    nStatus.write(None, "Note",     (200, 50,  0))
    nStatus.write(None, "Draft",    (200, 150, 0))
    nStatus.write(None, "Finished", (50,  200, 0))

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
            "blue": "100"
        }),
        ("Note", {
            "key": statusKeys[1],
            "count": "5",
            "red": "200",
            "green": "50",
            "blue": "0"
        }),
        ("Draft", {
            "key": statusKeys[2],
            "count": "7",
            "red": "200",
            "green": "150",
            "blue": "0"
        }),
        ("Finished", {
            "key": statusKeys[3],
            "count": "9",
            "red": "50",
            "green": "200",
            "blue": "0"
        }),
    ]

    # Unpack
    nStatus = NWStatus(NWStatus.STATUS)
    nStatus.unpack({
        statusKeys[0]: {"label": "New0", "colour": (100, 100, 100), "count": countTo[0]},
        statusKeys[1]: {"label": "New1", "colour": (150, 150, 150), "count": countTo[1]},
        statusKeys[2]: {"label": "New2", "colour": (200, 200, 200), "count": countTo[2]},
        statusKeys[3]: {"label": "New3", "colour": (250, 250, 250), "count": countTo[3]},
    })
    assert len(nStatus._store) == 4
    assert list(nStatus._store.keys()) == statusKeys
    assert nStatus._store[statusKeys[0]]["name"] == "New0"
    assert nStatus._store[statusKeys[1]]["name"] == "New1"
    assert nStatus._store[statusKeys[2]]["name"] == "New2"
    assert nStatus._store[statusKeys[3]]["name"] == "New3"
    assert nStatus._store[statusKeys[0]]["cols"] == (100, 100, 100)
    assert nStatus._store[statusKeys[1]]["cols"] == (150, 150, 150)
    assert nStatus._store[statusKeys[2]]["cols"] == (200, 200, 200)
    assert nStatus._store[statusKeys[3]]["cols"] == (250, 250, 250)
    assert nStatus._store[statusKeys[0]]["count"] == countTo[0]
    assert nStatus._store[statusKeys[1]]["count"] == countTo[1]
    assert nStatus._store[statusKeys[2]]["count"] == countTo[2]
    assert nStatus._store[statusKeys[3]]["count"] == countTo[3]

# END Test testCoreStatus_PackUnpack
