"""
novelWriter – NWIndex Class Tester
==================================

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

from novelwriter.core.indexdata import IndexHeading


@pytest.mark.core
def testCoreIndexData_IndexHeading():
    """Test the IndexHeading class."""
    # Defaults
    head = IndexHeading("T0001")
    assert repr(head) == "<IndexHeading key='T0001'>"
    assert str(head) == "<IndexHeading key='T0001'>"
    assert head.key == "T0001"
    assert head.line == 0
    assert head.level == "H0"
    assert head.title == ""
    assert head.charCount == 0
    assert head.wordCount == 0
    assert head.paraCount == 0
    assert head.synopsis == ""
    assert head.tag == ""
    assert head.references == {}

    # Set Level
    head.setLevel("Stuff")  # Invalid
    assert head.level == "H0"
    head.setLevel("H1")  # Valid
    assert head.level == "H1"

    # Set Line
    head.setLine(-1)  # Invalid
    assert head.line == 0
    head.setLine(42)  # Valid
    assert head.line == 42

    # Set Counts
    head.setCounts([1, 2])  # Invalid, must be three values
    assert head.charCount == 0
    assert head.wordCount == 0
    assert head.paraCount == 0
    head.setCounts([42, 4, 2])  # Valid
    assert head.charCount == 42
    assert head.wordCount == 4
    assert head.paraCount == 2

    # Set Summary
    head.setSynopsis("In the beginning ...")
    assert head.synopsis == "In the beginning ..."

    # Set Tag
    head.setTag("Stuff")
    assert head.tag == "stuff"  # Case insensitive

    # Add References
    head.addReference("Stuff", "@stuff")  # Invalid type
    assert head.references == {}
    head.addReference("Stuff", "@object")  # Valid type
    assert head.references == {"stuff": {"@object"}}

    # Pack Data
    assert head.packData() == {
        "meta": {"level": "H1", "title": "", "line": 42, "tag": "stuff", "counts": (42, 4, 2)},
        "refs": {"stuff": "@object"},
        "summary": "In the beginning ...",
    }

    # Unpack KeyError
    with pytest.raises(KeyError, match="Unknown key in heading entry"):
        head.unpackData({"stuff": "more stuff"})

    # Unpack Comments
    head.unpackData({"summary": "How it started ..."})
    assert head.synopsis == "How it started ..."


@pytest.mark.core
def testCoreIndexData_IndexHeadingUnpackMeta():
    """Test IndexHeading class meta unpacking."""
    # Valid
    data = {"meta": {
        "level": "H1", "title": "So it Begins", "line": 1, "tag": "begins", "counts": [95, 18, 1]
    }}
    head = IndexHeading("T0001")
    head.unpackData(data)
    assert head.level == "H1"
    assert head.title == "So it Begins"
    assert head.line == 1
    assert head.tag == "begins"
    assert head.charCount == 95
    assert head.wordCount == 18
    assert head.paraCount == 1

    # Invalid
    data = {"meta": {
        "level": "H9", "title": None, "line": None, "tag": None, "counts": [42]
    }}
    head = IndexHeading("T0001")
    head.unpackData(data)
    assert head.level == "H0"
    assert head.title == "None"
    assert head.line == 0
    assert head.tag == "None"
    assert head.charCount == 0
    assert head.wordCount == 0
    assert head.paraCount == 0

    # Empty
    data = {"meta": {}}
    head = IndexHeading("T0001")
    head.unpackData(data)
    assert head.level == "H0"
    assert head.title == ""
    assert head.line == 0
    assert head.tag == ""
    assert head.charCount == 0
    assert head.wordCount == 0
    assert head.paraCount == 0


@pytest.mark.core
def testCoreIndexData_IndexHeadingUnpackRefs():
    """Test IndexHeading class refs unpacking."""
    # Valid
    data = {"refs": {
        "jane": "@char,@pov", "john": "@char", "earth": "@location", "space": "@mention,@location"
    }}
    head = IndexHeading("T0001")
    head.unpackData(data)
    assert head.references["jane"] == {"@char", "@pov"}
    assert head.references["john"] == {"@char"}
    assert head.references["earth"] == {"@location"}
    assert head.references["space"] == {"@location", "@mention"}

    # Invalid key
    data = {"refs": {0: "@char,@pov"}}
    head = IndexHeading("T0001")
    with pytest.raises(ValueError, match="Heading reference key must be a string"):
        head.unpackData(data)

    # Invalid value
    data = {"refs": {"jane": None}}
    head = IndexHeading("T0001")
    with pytest.raises(ValueError, match="Heading reference value must be a string"):
        head.unpackData(data)

    # Invalid keyword
    data = {"refs": {"jane": "@char,@pov,@stuff"}}
    head = IndexHeading("T0001")
    with pytest.raises(ValueError, match="Heading reference contains an invalid keyword"):
        head.unpackData(data)
