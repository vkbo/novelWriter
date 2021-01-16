# -*- coding: utf-8 -*-
"""
novelWriter – NWStatus Class Tester
===================================

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

import pytest

from lxml import etree

from nw.core.status import NWStatus

@pytest.mark.core
def testCoreStatus_Entries():
    """Test all the simple setters for the NWItem class.
    """
    theStatus = NWStatus()

    # Add entries
    theStatus.addEntry("New",   (100, 100, 100))
    theStatus.addEntry("Minor", (200, 50,  0))
    theStatus.addEntry("Major", (200, 150, 0))
    theStatus.addEntry("Main",  (50,  200, 0))

    assert theStatus._theLabels == ["New", "Minor", "Major", "Main"]
    assert theStatus._theColours == [(100, 100, 100), (200, 50, 0), (200, 150, 0), (50, 200, 0)]
    assert theStatus._theCounts == [0, 0, 0, 0]
    assert theStatus._theMap["New"] == 0
    assert theStatus._theMap["Minor"] == 1
    assert theStatus._theMap["Major"] == 2
    assert theStatus._theMap["Main"] == 3
    assert theStatus._theLength == 4

    # Lookups
    assert theStatus.lookupEntry(None) is None
    assert theStatus.lookupEntry("dummy") is None
    assert theStatus.lookupEntry("Main") == 3

    # Checks
    assert theStatus.checkEntry(123) == "New"
    assert theStatus.checkEntry("Stuff") == "New"
    assert theStatus.checkEntry("New ") == "New"
    assert theStatus.checkEntry("  Main ") == "Main"

    # Set new list
    newList = [
        ("New", 1, 1, 1, "New"),
        ("Minor", 2, 2, 2, "Minor"),
        ("Major", 3, 3, 3, "Major"),
        ("Min", 4, 4, 4, "Main"),
        ("Max", 5, 5, 5, None),
    ]
    assert theStatus.setNewEntries(None) == {}
    assert theStatus.setNewEntries(newList) == {"Main": "Min"}

    assert theStatus._theLabels == ["New", "Minor", "Major", "Min", "Max"]
    assert theStatus._theColours == [(1, 1, 1), (2, 2, 2), (3, 3, 3), (4, 4, 4), (5, 5, 5)]
    assert theStatus._theCounts == [0, 0, 0, 0, 0]
    assert theStatus._theMap["New"] == 0
    assert theStatus._theMap["Minor"] == 1
    assert theStatus._theMap["Major"] == 2
    assert theStatus._theMap["Min"] == 3
    assert theStatus._theMap["Max"] == 4
    assert theStatus._theLength == 5

    # Add counts
    countTo = [3, 5, 7, 9, 11]
    for i, n in enumerate(countTo):
        for _ in range(n):
            theStatus.countEntry(theStatus._theLabels[i])
    assert theStatus._theCounts == countTo

    # Iterate
    for i, (sA, sB, sC) in enumerate(theStatus):
        assert sA == theStatus._theLabels[i]
        assert sB == theStatus._theColours[i]
        assert sC == theStatus._theCounts[i]

    assert theStatus[9] == (None, None, None)

    # Clear counts
    theStatus.resetCounts()
    assert theStatus._theCounts == [0, 0, 0, 0, 0]

# END Test testCoreStatus_Entries

@pytest.mark.core
def testCoreStatus_XMLPackUnpack():
    """Test all the simple setters for the NWItem class.
    """
    theStatus = NWStatus()
    theStatus.addEntry("New",   (100, 100, 100))
    theStatus.addEntry("Minor", (200, 50,  0))
    theStatus.addEntry("Major", (200, 150, 0))
    theStatus.addEntry("Main",  (50,  200, 0))

    countTo = [3, 5, 7, 9]
    for i, n in enumerate(countTo):
        for _ in range(n):
            theStatus.countEntry(theStatus._theLabels[i])

    nwXML = etree.Element("novelWriterXML")

    # Pack
    xStatus = etree.SubElement(nwXML, "status")
    theStatus.packXML(xStatus)
    assert etree.tostring(xStatus, pretty_print=False, encoding="utf-8") == (
        b"<status>"
        b"<entry blue=\"100\" green=\"100\" red=\"100\">New</entry>"
        b"<entry blue=\"0\" green=\"50\" red=\"200\">Minor</entry>"
        b"<entry blue=\"0\" green=\"150\" red=\"200\">Major</entry>"
        b"<entry blue=\"0\" green=\"200\" red=\"50\">Main</entry>"
        b"</status>"
    )

    # Unpack
    theStatus = NWStatus()
    assert theStatus.unpackXML(xStatus)
    assert theStatus._theLabels == ["New", "Minor", "Major", "Main"]
    assert theStatus._theColours == [(100, 100, 100), (200, 50, 0), (200, 150, 0), (50, 200, 0)]
    assert theStatus._theCounts == [0, 0, 0, 0]
    assert theStatus._theMap["New"] == 0
    assert theStatus._theMap["Minor"] == 1
    assert theStatus._theMap["Major"] == 2
    assert theStatus._theMap["Main"] == 3
    assert theStatus._theLength == 4

# END Test testCoreStatus_XMLPackUnpack
