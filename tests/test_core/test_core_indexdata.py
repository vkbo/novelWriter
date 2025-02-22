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

from novelwriter.core.indexdata import IndexHeading, IndexNode
from novelwriter.core.item import NWItem
from novelwriter.core.project import NWProject


@pytest.mark.core
def testCoreIndexData_IndexNode(mockGUI):
    """Test the IndexNode class."""
    handle = "0123456789abc"
    project = NWProject()
    item = NWItem(project, handle)

    # Defaults
    node = IndexNode(handle, item)
    assert node.handle == handle
    assert node.item is item
    assert str(node) == f"<IndexNode handle='{handle}'>"
    assert repr(node) == f"<IndexNode handle='{handle}'>"
    assert len(node) == 1
    assert "T0000" in node  # Placeholder heading

    # Add a heading
    head1 = IndexHeading(node.nextHeading(), line=1, level="H1", title="Heading 1")
    head2 = IndexHeading(node.nextHeading(), line=10, level="H2", title="Heading 2")
    node.addHeading(head1)
    node.addHeading(head2)
    assert len(node) == 2
    assert "T0000" not in node  # Placeholder heading should be gone
    assert "T0001" in node
    assert "T0002" in node
    assert node["T0001"] is head1
    assert node["T0002"] is head2
    assert node.headings() == ["T0001", "T0002"]
    assert dict(node.items()) == {"T0001": head1, "T0002": head2}

    # Next heading should be T0003
    assert node.nextHeading() == "T0003"

    # Set counts
    node.setHeadingCounts("T0001", 42, 13, 3)
    node.setHeadingCounts("T0002", 84, 26, 6)
    assert head1.charCount == 42
    assert head1.wordCount == 13
    assert head1.paraCount == 3
    assert head2.charCount == 84
    assert head2.wordCount == 26
    assert head2.paraCount == 6

    # Set synopsis
    node.setHeadingSynopsis("T0001", "The first")
    node.setHeadingSynopsis("T0002", "The second")
    assert head1.synopsis == "The first"
    assert head2.synopsis == "The second"

    # Set tags
    node.setHeadingTag("T0001", "part1")
    node.setHeadingTag("T0002", "part2")
    assert head1.tag == "part1"
    assert head2.tag == "part2"
    assert node.allTags() == ["part1", "part2"]

    # Add references
    node.addHeadingRef("T0001", ["jane"], "@pov")
    node.addHeadingRef("T0001", ["jane", "john"], "@char")
    node.addHeadingRef("T0002", ["earth", "space"], "@location")
    assert head1.references["jane"] == {"@char", "@pov"}
    assert head1.references["john"] == {"@char"}
    assert head2.references["earth"] == {"@location"}
    assert head2.references["space"] == {"@location"}

    # Add note keys
    assert node.noteKeys("footnotes") == set()
    node.addNoteKey("footnotes", "key1")
    node.addNoteKey("footnotes", "key2")
    assert node.noteKeys("footnotes") == {"key1", "key2"}


@pytest.mark.core
def testCoreIndexData_IndexNodePackUnpack(mockGUI):
    """Test the pack and unpack methods of the IndexNode class."""
    handle = "0123456789abc"
    project = NWProject()
    item = NWItem(project, handle)
    node = IndexNode(handle, item)

    # Add some headings and notes
    head1 = IndexHeading(node.nextHeading(), line=1, level="H1", title="Heading 1")
    head2 = IndexHeading(node.nextHeading(), line=10, level="H2", title="Heading 2")
    node.addHeading(head1)
    node.addHeading(head2)
    node.setHeadingCounts("T0001", 42, 13, 3)
    node.setHeadingCounts("T0002", 84, 26, 6)
    node.addNoteKey("footnotes", "key1")
    node.addNoteKey("footnotes", "key2")

    # Check packing
    data = node.packData()
    assert data["T0001"] == {"meta": {
        "level": "H1", "title": "Heading 1", "line": 1, "tag": "", "counts": (42, 13, 3)
    }}
    assert data["T0002"] == {"meta": {
        "level": "H2", "title": "Heading 2", "line": 10, "tag": "", "counts": (84, 26, 6)
    }}
    assert set(data["document"]["footnotes"]) == {"key1", "key2"}

    # Create a new node
    new = IndexNode(handle, item)

    # Unpack heading one
    data = {"T0001": {"meta": {
        "level": "H1", "title": "Heading 1", "line": 1, "tag": "", "counts": (42, 13, 3)
    }}}
    new.unpackData(data)
    data = new.packData()
    assert data["T0001"] == {"meta": {
        "level": "H1", "title": "Heading 1", "line": 1, "tag": "", "counts": (42, 13, 3)
    }}

    # Unpack invalid key
    data = {"stuff": "whatever"}
    with pytest.raises(KeyError, match="Index node contains an invalid key"):
        new.unpackData(data)

    # Unpack invalid document keys
    data = {"document": {"whatever": []}}
    with pytest.raises(ValueError, match="The notes style is invalid"):
        new.unpackData(data)

    # Unpack invalid document values
    data = {"document": {"footnotes": [1, 2, 3]}}
    with pytest.raises(ValueError, match="The notes keys must be a list of strings"):
        new.unpackData(data)

    # Unpack valid keys
    data = {"document": {"footnotes": ["key1", "key2"]}}
    new.unpackData(data)
    assert set(new.packData()["document"]["footnotes"]) == {"key1", "key2"}


@pytest.mark.core
def testCoreIndexData_IndexHeading():
    """Test the IndexHeading class."""
    # Defaults
    head = IndexHeading("T0001")
    assert str(head) == "<IndexHeading key='T0001'>"
    assert repr(head) == "<IndexHeading key='T0001'>"
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
