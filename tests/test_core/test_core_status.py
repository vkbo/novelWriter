"""
novelWriter – NWStatus Class Tester
===================================

This file is a part of novelWriter
Copyright 2018–2022, Veronica Berglyd Olsen

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

from PyQt5.QtGui import QIcon

from novelwriter.core.status import NWStatus


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
    assert theStatus._getIndex(None) is None
    assert theStatus._getIndex("stuff") is None
    assert theStatus._getIndex("Main") == 3

    # Checks
    assert theStatus.checkEntry(123) == "New"
    assert theStatus.checkEntry("Stuff") == "New"
    assert theStatus.checkEntry("New ") == "New"
    assert theStatus.checkEntry("  Main ") == "Main"

    # Icons
    assert isinstance(theStatus.getIcon("Stuff"), QIcon)
    assert isinstance(theStatus.getIcon("New"), QIcon)

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
    for i, (sA, sB, sC, sD) in enumerate(theStatus):
        assert sA == theStatus._theLabels[i]
        assert sB == theStatus._theColours[i]
        assert sC == theStatus._theCounts[i]
        assert sD == theStatus._theIcons[i]

    sA, sB, sC, sD = theStatus[9]
    assert sA is None
    assert sB is None
    assert sC is None
    assert isinstance(sD, QIcon)

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
        b'<status>'
        b'<entry red="100" green="100" blue="100">New</entry>'
        b'<entry red="200" green="50" blue="0">Minor</entry>'
        b'<entry red="200" green="150" blue="0">Major</entry>'
        b'<entry red="50" green="200" blue="0">Main</entry>'
        b'</status>'
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
