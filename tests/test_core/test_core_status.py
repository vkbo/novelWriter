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
    theStatus = NWStatus(NWStatus.STATUS)
    theImport = NWStatus(NWStatus.IMPORT)

    with pytest.raises(Exception):
        NWStatus(999)

    # Generate Key
    # ============

    assert theStatus._newKey() == statusKeys[0]
    assert theStatus._newKey() == statusKeys[1]

    # Key collision, should move to key 3
    theStatus.write(statusKeys[2], "Crash", (0, 0, 0))
    assert theStatus._newKey() == statusKeys[3]

    assert theImport._newKey() == importKeys[0]
    assert theImport._newKey() == importKeys[1]

    # Key collision, should move to key 3
    theImport.write(importKeys[2], "Crash", (0, 0, 0))
    assert theImport._newKey() == importKeys[3]

    # Check Key
    # =========

    assert theStatus._isKey(None) is False        # Not a string
    assert theStatus._isKey("s00000") is False    # Too short
    assert theStatus._isKey("s000000") is True    # Correct length
    assert theStatus._isKey("s0000000") is False  # Too long
    assert theStatus._isKey("i000000") is False   # Wrong type
    assert theStatus._isKey("q000000") is False   # Wrong type
    assert theStatus._isKey("s12345H") is False   # Not a hex value
    assert theStatus._isKey("s12345F") is False   # Not a lower case hex value
    assert theStatus._isKey("s12345f") is True    # Valid hex value

    assert theImport._isKey(None) is False        # Not a string
    assert theImport._isKey("i00000") is False    # Too short
    assert theImport._isKey("i000000") is True    # Correct length
    assert theImport._isKey("i0000000") is False  # Too long
    assert theImport._isKey("s000000") is False   # Wrong type
    assert theImport._isKey("q000000") is False   # Wrong type
    assert theImport._isKey("i12345H") is False   # Not a hex value
    assert theImport._isKey("i12345F") is False   # Not a lower case hex value
    assert theImport._isKey("i12345f") is True    # Valid hex value

# END Test testCoreStatus_Internal


@pytest.mark.core
def testCoreStatus_Iterator(mockRnd):
    """Test the iterator functions of the NWStatus class.
    """
    theStatus = NWStatus(NWStatus.STATUS)

    theStatus.write(None, "New",      (100, 100, 100))
    theStatus.write(None, "Note",     (200, 50,  0))
    theStatus.write(None, "Draft",    (200, 150, 0))
    theStatus.write(None, "Finished", (50,  200, 0))

    # Direct access
    entry = theStatus[statusKeys[0]]
    assert entry["cols"] == (100, 100, 100)
    assert entry["name"] == "New"
    assert entry["count"] == 0
    assert isinstance(entry["icon"], QIcon)

    # Iterate
    entries = list(theStatus)
    assert len(entries) == 4
    assert len(theStatus) == 4

    # Keys
    assert list(theStatus.keys()) == statusKeys

    # Items
    for index, (key, entry) in enumerate(theStatus.items()):
        assert key == statusKeys[index]
        assert "cols" in entry
        assert "name" in entry
        assert "count" in entry
        assert "icon" in entry

    # Valuse
    for entry in theStatus.values():
        assert "cols" in entry
        assert "name" in entry
        assert "count" in entry
        assert "icon" in entry

# END Test testCoreStatus_Iterator


@pytest.mark.core
def testCoreStatus_Entries(mockRnd):
    """Test all the simple setters for the NWStatus class.
    """
    theStatus = NWStatus(NWStatus.STATUS)

    # Write
    # =====

    # Have a key
    theStatus.write(statusKeys[0], "Entry 1", (200, 100, 50))
    assert theStatus[statusKeys[0]]["name"] == "Entry 1"
    assert theStatus[statusKeys[0]]["cols"] == (200, 100, 50)

    # Don't have a key
    theStatus.write(None, "Entry 2", (210, 110, 60))
    assert theStatus[statusKeys[1]]["name"] == "Entry 2"
    assert theStatus[statusKeys[1]]["cols"] == (210, 110, 60)

    # Wrong colour spec
    theStatus.write(None, "Entry 3", "what?")
    assert theStatus[statusKeys[2]]["name"] == "Entry 3"
    assert theStatus[statusKeys[2]]["cols"] == (100, 100, 100)

    # Wrong colour count
    theStatus.write(None, "Entry 4", (10, 20))
    assert theStatus[statusKeys[3]]["name"] == "Entry 4"
    assert theStatus[statusKeys[3]]["cols"] == (100, 100, 100)

    # Check
    # =====

    # Normal lookup
    for key in statusKeys:
        assert theStatus.check(key) == key

    # Non-existing name
    assert theStatus.check("s987654") == statusKeys[0]

    # Name Access
    # ===========

    assert theStatus.name(statusKeys[0]) == "Entry 1"
    assert theStatus.name(statusKeys[1]) == "Entry 2"
    assert theStatus.name(statusKeys[2]) == "Entry 3"
    assert theStatus.name(statusKeys[3]) == "Entry 4"
    assert theStatus.name("blablabla") == "Entry 1"

    # Colour Access
    # =============

    assert theStatus.cols(statusKeys[0]) == (200, 100, 50)
    assert theStatus.cols(statusKeys[1]) == (210, 110, 60)
    assert theStatus.cols(statusKeys[2]) == (100, 100, 100)
    assert theStatus.cols(statusKeys[3]) == (100, 100, 100)
    assert theStatus.cols("blablabla") == (200, 100, 50)

    # Icon Access
    # ===========

    assert isinstance(theStatus.icon(statusKeys[0]), QIcon)
    assert isinstance(theStatus.icon(statusKeys[1]), QIcon)
    assert isinstance(theStatus.icon(statusKeys[2]), QIcon)
    assert isinstance(theStatus.icon(statusKeys[3]), QIcon)
    assert isinstance(theStatus.icon("blablabla"), QIcon)

    # Increment and Count Access
    # ==========================

    countTo = [3, 5, 7, 9]
    for i, n in enumerate(countTo):
        for _ in range(n):
            theStatus.increment(statusKeys[i])

    assert theStatus.count(statusKeys[0]) == countTo[0]
    assert theStatus.count(statusKeys[1]) == countTo[1]
    assert theStatus.count(statusKeys[2]) == countTo[2]
    assert theStatus.count(statusKeys[3]) == countTo[3]
    assert theStatus.count("blablabla") == countTo[0]

    theStatus.resetCounts()

    assert theStatus.count(statusKeys[0]) == 0
    assert theStatus.count(statusKeys[1]) == 0
    assert theStatus.count(statusKeys[2]) == 0
    assert theStatus.count(statusKeys[3]) == 0

    # Reorder
    # =======

    cOrder = list(theStatus.keys())
    assert cOrder == statusKeys

    # Wrong length
    assert theStatus.reorder([]) is False

    # No change
    assert theStatus.reorder(cOrder) is False

    # Actual reaorder
    nOrder = [
        statusKeys[0],
        statusKeys[2],
        statusKeys[1],
        statusKeys[3],
    ]
    assert theStatus.reorder(nOrder) is True
    assert list(theStatus.keys()) == nOrder

    # Add an unknown key
    wOrder = nOrder.copy()
    wOrder[3] = theStatus._newKey()
    assert theStatus.reorder(wOrder) is False
    assert list(theStatus.keys()) == nOrder

    # Put it back
    assert theStatus.reorder(cOrder) is True
    assert list(theStatus.keys()) == cOrder

    # Default
    # =======

    default = theStatus._default
    theStatus._default = None

    assert theStatus.check("Entry 5") == ""
    assert theStatus.name("blablabla") == ""
    assert theStatus.cols("blablabla") == (100, 100, 100)
    assert theStatus.count("blablabla") == 0
    assert isinstance(theStatus.icon("blablabla"), QIcon)

    theStatus._default = default

    # Remove
    # ======

    # Non-existing entry
    assert theStatus.remove("blablabla") is False

    # Non-zero entry
    theStatus.increment(statusKeys[3])
    assert theStatus.remove(statusKeys[3]) is False

    # Delete last entry
    theStatus.resetCounts()
    lastName = theStatus.name(statusKeys[3])
    assert lastName == "Entry 4"
    assert theStatus.remove(statusKeys[3]) is True
    assert theStatus.check(statusKeys[3]) == theStatus._default
    assert theStatus.check(lastName) == theStatus._default

    # Delete default entry, Entry 2 is new default
    firstName = theStatus.name(theStatus._default)
    assert firstName == "Entry 1"
    assert theStatus.remove(theStatus._default) is True
    assert theStatus.name(firstName) == "Entry 2"

    # Remove remaining entries
    assert theStatus.remove(statusKeys[1]) is True
    assert theStatus.remove(statusKeys[2]) is True

    assert len(theStatus) == 0
    assert theStatus._default is None

# END Test testCoreStatus_Entries


@pytest.mark.core
def testCoreStatus_PackUnpack(mockRnd):
    """Test all the pack/unpack of the NWStatus class.
    """
    theStatus = NWStatus(NWStatus.STATUS)
    theStatus.write(None, "New",      (100, 100, 100))
    theStatus.write(None, "Note",     (200, 50,  0))
    theStatus.write(None, "Draft",    (200, 150, 0))
    theStatus.write(None, "Finished", (50,  200, 0))

    countTo = [3, 5, 7, 9]
    for i, n in enumerate(countTo):
        for _ in range(n):
            theStatus.increment(statusKeys[i])

    # Pack
    assert list(theStatus.pack()) == [
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
    theStatus = NWStatus(NWStatus.STATUS)
    theStatus.unpack({
        statusKeys[0]: {"label": "New0", "colour": (100, 100, 100), "count": countTo[0]},
        statusKeys[1]: {"label": "New1", "colour": (150, 150, 150), "count": countTo[1]},
        statusKeys[2]: {"label": "New2", "colour": (200, 200, 200), "count": countTo[2]},
        statusKeys[3]: {"label": "New3", "colour": (250, 250, 250), "count": countTo[3]},
    })
    assert len(theStatus._store) == 4
    assert list(theStatus._store.keys()) == statusKeys
    assert theStatus._store[statusKeys[0]]["name"] == "New0"
    assert theStatus._store[statusKeys[1]]["name"] == "New1"
    assert theStatus._store[statusKeys[2]]["name"] == "New2"
    assert theStatus._store[statusKeys[3]]["name"] == "New3"
    assert theStatus._store[statusKeys[0]]["cols"] == (100, 100, 100)
    assert theStatus._store[statusKeys[1]]["cols"] == (150, 150, 150)
    assert theStatus._store[statusKeys[2]]["cols"] == (200, 200, 200)
    assert theStatus._store[statusKeys[3]]["cols"] == (250, 250, 250)
    assert theStatus._store[statusKeys[0]]["count"] == countTo[0]
    assert theStatus._store[statusKeys[1]]["count"] == countTo[1]
    assert theStatus._store[statusKeys[2]]["count"] == countTo[2]
    assert theStatus._store[statusKeys[3]]["count"] == countTo[3]

# END Test testCoreStatus_PackUnpack
