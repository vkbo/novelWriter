"""
novelWriter – ProjectXMLReader/Writer Class Tester
==================================================

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

import json
import pytest

from shutil import copyfile
from datetime import datetime
from novelwriter.constants import nwFiles

from tools import cmpFiles, writeFile
from mocked import causeOSError

from novelwriter.core.item import NWItem
from novelwriter.core.projectxml import ProjectXMLReader, ProjectXMLWriter, XMLReadState
from novelwriter.core.projectdata import NWProjectData


class MockProject:
    """Fake project object."""

    def setProjectChanged(self, *a):
        """Fake project method."""
        pass


@pytest.fixture(scope="function", autouse=True)
def mockVersion(monkeypatch):
    """Mock the version info to prevent diff from failing."""
    monkeypatch.setattr("novelwriter.core.projectxml.__version__", "2.0-rc1")
    monkeypatch.setattr("novelwriter.core.projectxml.__hexversion__", "0x020000c1")
    return


@pytest.mark.core
def testCoreProjectXML_ReadCurrent(monkeypatch, tstPaths, fncPath):
    """Test reading the current XML file format."""
    refFile = tstPaths.filesDir / "nwProject-1.5.nwx"
    tstFile = tstPaths.outDir / "ProjectXML_ReadCurrent.nwx"
    xmlFile = fncPath / "nwProject-1.5.nwx"
    outFile = fncPath / "nwProject.nwx"

    xmlReader = ProjectXMLReader(xmlFile)
    assert xmlReader.state == XMLReadState.NO_ACTION

    data = NWProjectData(MockProject())  # type: ignore
    content = []

    # With no valid files, the read should fail
    writeFile(xmlFile, "")
    assert xmlReader.read(data, content) is False
    assert xmlReader.state == XMLReadState.CANNOT_PARSE

    # Add a valid project file, that is not novelWriter
    writeFile(xmlFile, "<xml/>")
    assert xmlReader.read(data, content) is False
    assert xmlReader.state == XMLReadState.NOT_NWX_FILE

    # Add a valid novelWriter file without a file version
    writeFile(xmlFile, "<novelWriterXML/>")
    assert xmlReader.read(data, content) is False
    assert xmlReader.state == XMLReadState.UNKNOWN_VERSION

    # Check parsing of unknown sections
    writeFile(xmlFile, (
        "<novelWriterXML fileVersion='1.5'>"
        "  <project>"
        "    <stuff></stuff>"
        "  </project>"
        "  <settings>"
        "    <stuff></stuff>"
        "  </settings>"
        "  <content>"
        "    <item>"
        "      <stuff></stuff>"
        "    </item>"
        "    <stuff></stuff>"
        "  </content>"
        "  <stuff></stuff>"
        "</novelWriterXML>"
    ))
    assert xmlReader.read(data, content) is True
    assert xmlReader.state == XMLReadState.PARSED_OK

    writeFile(xmlFile, (
        "<novelWriterXML fileVersion='1.0'>"
        "  <project>"
        "    <stuff></stuff>"
        "  </project>"
        "  <settings>"
        "    <stuff></stuff>"
        "  </settings>"
        "  <content>"
        "    <item>"
        "      <stuff></stuff>"
        "    </item>"
        "    <stuff></stuff>"
        "  </content>"
        "  <stuff></stuff>"
        "</novelWriterXML>"
    ))
    assert xmlReader.read(data, content) is True
    assert xmlReader.state == XMLReadState.WAS_LEGACY

    # Reset data objects
    data = NWProjectData(MockProject())  # type: ignore
    content = []

    # Parse a valid, complete file
    copyfile(refFile, xmlFile)
    assert xmlReader.read(data, content) is True
    assert xmlReader.state == XMLReadState.PARSED_OK
    assert xmlReader.xmlRoot == "novelWriterXML"
    assert xmlReader.xmlVersion == 0x0105
    assert xmlReader.xmlRevision == 4
    assert xmlReader.appVersion == "2.0-rc1"
    assert xmlReader.hexVersion == 0x020000c1

    # Check loaded data
    assert data.name == "Sample Project"
    assert data.author == "Jane Smith"
    assert data.saveCount == 5
    assert data.autoCount == 10
    assert data.editTime == 1000

    assert data.doBackup is True
    assert data.language == "en_GB"
    assert data.spellCheck is True
    assert data.spellLang == "en_GB"
    assert data.initCounts == (954, 409)
    assert data.currCounts == (954, 409)

    assert data.getLastHandle("editor") == "636b6aa9b697b"
    assert data.getLastHandle("viewer") == "636b6aa9b697b"
    assert data.getLastHandle("novelTree") == "7031beac91f75"
    assert data.getLastHandle("outline") == "7031beac91f75"

    assert data.itemStatus.name("sf12341") == "New"
    assert data.itemStatus.name("sf24ce6") == "Notes"
    assert data.itemStatus.name("sc24b8f") == "Started"
    assert data.itemStatus.name("s90e6c9") == "1st Draft"
    assert data.itemStatus.name("sd51c5b") == "2nd Draft"
    assert data.itemStatus.name("s8ae72a") == "3rd Draft"
    assert data.itemStatus.name("s78ea90") == "Finished"

    assert data.itemImport.name("ia857f0") == "None"
    assert data.itemImport.name("icfb3a5") == "Minor"
    assert data.itemImport.name("i2d7a54") == "Major"
    assert data.itemImport.name("i56be10") == "Main"

    assert data.itemStatus.cols("sf12341") == (100, 100, 100)
    assert data.itemStatus.cols("sf24ce6") == (200, 50, 0)
    assert data.itemStatus.cols("sc24b8f") == (182, 60, 0)
    assert data.itemStatus.cols("s90e6c9") == (193, 129, 0)
    assert data.itemStatus.cols("sd51c5b") == (193, 129, 0)
    assert data.itemStatus.cols("s8ae72a") == (193, 129, 0)
    assert data.itemStatus.cols("s78ea90") == (58, 180, 58)

    assert data.itemImport.cols("ia857f0") == (100, 100, 100)
    assert data.itemImport.cols("icfb3a5") == (0, 122, 188)
    assert data.itemImport.cols("i2d7a54") == (21, 0, 180)
    assert data.itemImport.cols("i56be10") == (117, 0, 175)

    assert data.itemStatus.count("sf12341") == 4
    assert data.itemStatus.count("sf24ce6") == 2
    assert data.itemStatus.count("sc24b8f") == 3
    assert data.itemStatus.count("s90e6c9") == 7
    assert data.itemStatus.count("sd51c5b") == 0
    assert data.itemStatus.count("s8ae72a") == 0
    assert data.itemStatus.count("s78ea90") == 1

    assert data.itemImport.count("ia857f0") == 5
    assert data.itemImport.count("icfb3a5") == 2
    assert data.itemImport.count("i2d7a54") == 2
    assert data.itemImport.count("i56be10") == 1

    # Compare content
    dumpFile = tstPaths.outDir / "projectXML_ReadCurrent.json"
    compFile = tstPaths.refDir / "projectXML_ReadCurrent.json"
    with open(dumpFile, mode="w", encoding="utf-8") as dump:
        json.dump(content, dump, indent=2)
    assert cmpFiles(dumpFile, compFile)

    packedContent = []
    mockProject = MockProject()
    mockProject.__setattr__("data", data)
    for entry in content:
        item = NWItem(mockProject, "0000000000000")  # type: ignore
        item.unpack(entry)
        packedContent.append(item.pack())

    # Save the project again, which should produce an identical project xml
    timeStamp = int(datetime.fromisoformat(xmlReader.timeStamp).timestamp())
    xmlWriter = ProjectXMLWriter(fncPath / nwFiles.PROJ_FILE)

    # Fail saving
    with monkeypatch.context() as mp:
        mp.setattr("xml.etree.ElementTree.ElementTree.write", causeOSError)
        assert xmlWriter.write(data, packedContent, timeStamp, 1000) is False
        assert str(xmlWriter.error) == "Mock OSError"

    with monkeypatch.context() as mp:
        mp.setattr("pathlib.Path.replace", causeOSError)
        assert xmlWriter.write(data, packedContent, timeStamp, 1000) is False
        assert str(xmlWriter.error) == "Mock OSError"

    # Successful save (should be twice)
    assert xmlWriter.write(data, packedContent, timeStamp, 1000) is True
    assert xmlWriter.write(data, packedContent, timeStamp, 1000) is True
    copyfile(outFile, tstFile)
    assert cmpFiles(tstFile, refFile)

# END Test testCoreProjectXML_ReadCurrent


@pytest.mark.core
def testCoreProjectXML_ReadLegacy10(tstPaths, fncPath, mockRnd):
    """Test reading the version 1.0 XML file format."""
    refFile = tstPaths.filesDir / "nwProject-1.0.nwx"
    xmlFile = fncPath / "nwProject-1.0.nwx"
    outFile = fncPath / "nwProject.nwx"
    copyfile(refFile, xmlFile)

    xmlReader = ProjectXMLReader(xmlFile)
    assert xmlReader.state == XMLReadState.NO_ACTION

    data = NWProjectData(MockProject())  # type: ignore
    content = []

    assert xmlReader.read(data, content) is True
    assert xmlReader.state == XMLReadState.WAS_LEGACY
    assert xmlReader.xmlRoot == "novelWriterXML"
    assert xmlReader.xmlVersion == 0x0100
    assert xmlReader.appVersion == "0.6.1"
    assert xmlReader.hexVersion == 0x000601f0

    # Check loaded data
    assert data.name == "Sample Project"
    assert data.author == "Jay Doh"  # Only last author is preserved
    assert data.saveCount == 0  # Doesn't exist in 1.0
    assert data.autoCount == 0  # Doesn't exist in 1.0
    assert data.editTime == 0  # Doesn't exist in 1.0

    assert data.doBackup is True
    assert data.language is None  # Doesn't exist in 1.0
    assert data.spellCheck is True
    assert data.spellLang is None  # Doesn't exist in 1.0
    assert data.initCounts == (0, 0)
    assert data.currCounts == (0, 0)

    assert data.getLastHandle("editor") is None  # Dropped by conversion
    assert data.getLastHandle("viewer") is None  # Dropped by conversion
    assert data.getLastHandle("novelTree") is None  # Doesn't exist in 1.0
    assert data.getLastHandle("outline") is None  # Doesn't exist in 1.0

    assert data.itemStatus.name("s000000") == "New"
    assert data.itemStatus.name("s000001") == "Notes"
    assert data.itemStatus.name("s000002") == "Started"
    assert data.itemStatus.name("s000003") == "1st Draft"
    assert data.itemStatus.name("s000004") == "2nd Draft"
    assert data.itemStatus.name("s000005") == "3rd Draft"
    assert data.itemStatus.name("s000006") == "Finished"

    assert data.itemImport.name("i000007") == "None"
    assert data.itemImport.name("i000008") == "Minor"
    assert data.itemImport.name("i000009") == "Major"
    assert data.itemImport.name("i00000a") == "Main"

    assert data.itemStatus.cols("s000000") == (100, 100, 100)
    assert data.itemStatus.cols("s000001") == (200, 50, 0)
    assert data.itemStatus.cols("s000002") == (182, 60, 0)
    assert data.itemStatus.cols("s000003") == (193, 129, 0)
    assert data.itemStatus.cols("s000004") == (193, 129, 0)
    assert data.itemStatus.cols("s000005") == (193, 129, 0)
    assert data.itemStatus.cols("s000006") == (58, 180, 58)

    assert data.itemImport.cols("i000007") == (100, 100, 100)
    assert data.itemImport.cols("i000008") == (0, 122, 188)
    assert data.itemImport.cols("i000009") == (21, 0, 180)
    assert data.itemImport.cols("i00000a") == (117, 0, 175)

    assert data.itemStatus.count("s000000") == 0
    assert data.itemStatus.count("s000001") == 0
    assert data.itemStatus.count("s000002") == 0
    assert data.itemStatus.count("s000003") == 0
    assert data.itemStatus.count("s000004") == 0
    assert data.itemStatus.count("s000005") == 0
    assert data.itemStatus.count("s000006") == 0

    assert data.itemImport.count("i000007") == 0
    assert data.itemImport.count("i000008") == 0
    assert data.itemImport.count("i000009") == 0
    assert data.itemImport.count("i00000a") == 0

    # Compare content
    dumpFile = tstPaths.outDir / "projectXML_ReadLegacy10.json"
    compFile = tstPaths.refDir / "projectXML_ReadLegacy10.json"
    with open(dumpFile, mode="w", encoding="utf-8") as dump:
        json.dump(content, dump, indent=2)
    assert cmpFiles(dumpFile, compFile)

    packedContent = []
    mockProject = MockProject()
    mockProject.__setattr__("data", data)
    status = {}
    for entry in content:
        item = NWItem(mockProject, "0000000000000")  # type: ignore
        item.unpack(entry)
        status[item.itemHandle] = item.getImportStatus(incIcon=False)[0]
        packedContent.append(item.pack())

    assert status == {
        "7031beac91f75": "Started",
        "53b69b83cdafc": "Started",
        "974e400180a99": "New",
        "edca4be2fcaf8": "New",
        "e7ded148d6e4a": "1st Draft",
        "6a2d6d5f4f401": "Notes",
        "636b6aa9b697b": "1st Draft",
        "bc0cbd2a407f3": "1st Draft",
        "ba8a28a246524": "Finished",
        "96b68994dfa3d": "2nd Draft",
        "88706ddc78b1b": "1st Draft",
        "ae7339df26ded": "1st Draft",
        "f6622b4617424": "None",
        "f7e2d9f330615": "None",
        "14298de4d9524": "Minor",
        "bb2c23b3c42cc": "Major",
        "15c4492bd5107": "None",
        "b3e74dbc1f584": "Main",
        "f1471bef9f2ae": "Minor",
        "5eaea4e8cdee8": "Major",
        "98acd8c76c93a": "None",
        "b8136a5a774a0": "New",
    }

    # Save the project again, which should produce an identical project xml
    timeStamp = int(datetime.fromisoformat(xmlReader.timeStamp).timestamp())
    xmlWriter = ProjectXMLWriter(fncPath / nwFiles.PROJ_FILE)
    data.setUuid("d0f3fe10-c6e6-4310-8bfd-181eb4224eed")
    assert xmlWriter.write(data, packedContent, timeStamp, 1000) is True
    testFile = tstPaths.outDir / "projectXML_ReadLegacy10.nwx"
    compFile = tstPaths.refDir / "projectXML_ReadLegacy10.nwx"
    copyfile(outFile, testFile)
    assert cmpFiles(testFile, compFile)

# END Test testCoreProjectXML_ReadLegacy10


@pytest.mark.core
def testCoreProjectXML_ReadLegacy11(tstPaths, fncPath, mockRnd):
    """Test reading the version 1.1 XML file format."""
    refFile = tstPaths.filesDir / "nwProject-1.1.nwx"
    xmlFile = fncPath / "nwProject-1.1.nwx"
    outFile = fncPath / "nwProject.nwx"
    copyfile(refFile, xmlFile)

    xmlReader = ProjectXMLReader(xmlFile)
    assert xmlReader.state == XMLReadState.NO_ACTION

    data = NWProjectData(MockProject())  # type: ignore
    content = []

    assert xmlReader.read(data, content) is True
    assert xmlReader.state == XMLReadState.WAS_LEGACY
    assert xmlReader.xmlRoot == "novelWriterXML"
    assert xmlReader.xmlVersion == 0x0101
    assert xmlReader.appVersion == "0.9.2"
    assert xmlReader.hexVersion == 0x000902f0

    # Check loaded data
    assert data.name == "Sample Project"
    assert data.author == "Jay Doh"  # Only last author is preserved
    assert data.saveCount == 5
    assert data.autoCount == 10
    assert data.editTime == 1000

    assert data.doBackup is True
    assert data.language is None  # Doesn't exist in 1.1
    assert data.spellCheck is True
    assert data.spellLang is None  # Doesn't exist in 1.1
    assert data.initCounts == (0, 0)
    assert data.currCounts == (0, 0)

    assert data.getLastHandle("editor") is None  # Dropped by conversion
    assert data.getLastHandle("viewer") is None  # Dropped by conversion
    assert data.getLastHandle("novelTree") is None  # Doesn't exist in 1.1
    assert data.getLastHandle("outline") is None  # Doesn't exist in 1.1

    assert data.itemStatus.name("s000000") == "New"
    assert data.itemStatus.name("s000001") == "Notes"
    assert data.itemStatus.name("s000002") == "Started"
    assert data.itemStatus.name("s000003") == "1st Draft"
    assert data.itemStatus.name("s000004") == "2nd Draft"
    assert data.itemStatus.name("s000005") == "3rd Draft"
    assert data.itemStatus.name("s000006") == "Finished"

    assert data.itemImport.name("i000007") == "None"
    assert data.itemImport.name("i000008") == "Minor"
    assert data.itemImport.name("i000009") == "Major"
    assert data.itemImport.name("i00000a") == "Main"

    assert data.itemStatus.cols("s000000") == (100, 100, 100)
    assert data.itemStatus.cols("s000001") == (200, 50, 0)
    assert data.itemStatus.cols("s000002") == (182, 60, 0)
    assert data.itemStatus.cols("s000003") == (193, 129, 0)
    assert data.itemStatus.cols("s000004") == (193, 129, 0)
    assert data.itemStatus.cols("s000005") == (193, 129, 0)
    assert data.itemStatus.cols("s000006") == (58, 180, 58)

    assert data.itemImport.cols("i000007") == (100, 100, 100)
    assert data.itemImport.cols("i000008") == (0, 122, 188)
    assert data.itemImport.cols("i000009") == (21, 0, 180)
    assert data.itemImport.cols("i00000a") == (117, 0, 175)

    assert data.itemStatus.count("s000000") == 0
    assert data.itemStatus.count("s000001") == 0
    assert data.itemStatus.count("s000002") == 0
    assert data.itemStatus.count("s000003") == 0
    assert data.itemStatus.count("s000004") == 0
    assert data.itemStatus.count("s000005") == 0
    assert data.itemStatus.count("s000006") == 0

    assert data.itemImport.count("i000007") == 0
    assert data.itemImport.count("i000008") == 0
    assert data.itemImport.count("i000009") == 0
    assert data.itemImport.count("i00000a") == 0

    # Compare content
    dumpFile = tstPaths.outDir / "projectXML_ReadLegacy11.json"
    compFile = tstPaths.refDir / "projectXML_ReadLegacy11.json"
    with open(dumpFile, mode="w", encoding="utf-8") as dump:
        json.dump(content, dump, indent=2)
    assert cmpFiles(dumpFile, compFile)

    packedContent = []
    mockProject = MockProject()
    mockProject.__setattr__("data", data)
    status = {}
    for entry in content:
        item = NWItem(mockProject, "0000000000000")  # type: ignore
        item.unpack(entry)
        status[item.itemHandle] = item.getImportStatus(incIcon=False)[0]
        packedContent.append(item.pack())

    assert status == {
        "7031beac91f75": "Started",
        "53b69b83cdafc": "Started",
        "974e400180a99": "New",
        "edca4be2fcaf8": "New",
        "e7ded148d6e4a": "1st Draft",
        "6a2d6d5f4f401": "Notes",
        "636b6aa9b697b": "1st Draft",
        "bc0cbd2a407f3": "1st Draft",
        "ba8a28a246524": "Finished",
        "96b68994dfa3d": "2nd Draft",
        "88706ddc78b1b": "1st Draft",
        "ae7339df26ded": "1st Draft",
        "f6622b4617424": "None",
        "f7e2d9f330615": "None",
        "14298de4d9524": "Minor",
        "bb2c23b3c42cc": "Major",
        "15c4492bd5107": "None",
        "b3e74dbc1f584": "Main",
        "f1471bef9f2ae": "Minor",
        "5eaea4e8cdee8": "Major",
        "98acd8c76c93a": "None",
        "b8136a5a774a0": "New",
    }

    # Save the project again, which should produce an identical project xml
    timeStamp = int(datetime.fromisoformat(xmlReader.timeStamp).timestamp())
    xmlWriter = ProjectXMLWriter(fncPath / nwFiles.PROJ_FILE)
    data.setUuid("d0f3fe10-c6e6-4310-8bfd-181eb4224eed")
    assert xmlWriter.write(data, packedContent, timeStamp, 1000) is True
    testFile = tstPaths.outDir / "projectXML_ReadLegacy11.nwx"
    compFile = tstPaths.refDir / "projectXML_ReadLegacy11.nwx"
    copyfile(outFile, testFile)
    assert cmpFiles(testFile, compFile)

# END Test testCoreProjectXML_ReadLegacy11


@pytest.mark.core
def testCoreProjectXML_ReadLegacy12(tstPaths, fncPath, mockRnd):
    """Test reading the version 1.2 XML file format."""
    refFile = tstPaths.filesDir / "nwProject-1.2.nwx"
    xmlFile = fncPath / "nwProject-1.2.nwx"
    outFile = fncPath / "nwProject.nwx"
    copyfile(refFile, xmlFile)

    xmlReader = ProjectXMLReader(xmlFile)
    assert xmlReader.state == XMLReadState.NO_ACTION

    data = NWProjectData(MockProject())  # type: ignore
    content = []

    assert xmlReader.read(data, content) is True
    assert xmlReader.state == XMLReadState.WAS_LEGACY
    assert xmlReader.xmlRoot == "novelWriterXML"
    assert xmlReader.xmlVersion == 0x0102
    assert xmlReader.appVersion == "1.4.2"
    assert xmlReader.hexVersion == 0x010402f0

    # Check loaded data
    assert data.name == "Sample Project"
    assert data.author == "Jay Doh"  # Only last author is preserved
    assert data.saveCount == 5
    assert data.autoCount == 10
    assert data.editTime == 1000

    assert data.doBackup is True
    assert data.language == "en_GB"
    assert data.spellCheck is True
    assert data.spellLang == "en_GB"
    assert data.initCounts == (840, 376)
    assert data.currCounts == (840, 376)

    assert data.getLastHandle("editor") is None  # Dropped by conversion
    assert data.getLastHandle("viewer") is None  # Dropped by conversion
    assert data.getLastHandle("novelTree") is None  # Doesn't exist in 1.2
    assert data.getLastHandle("outline") is None  # Doesn't exist in 1.2

    assert data.itemStatus.name("s000000") == "New"
    assert data.itemStatus.name("s000001") == "Notes"
    assert data.itemStatus.name("s000002") == "Started"
    assert data.itemStatus.name("s000003") == "1st Draft"
    assert data.itemStatus.name("s000004") == "2nd Draft"
    assert data.itemStatus.name("s000005") == "3rd Draft"
    assert data.itemStatus.name("s000006") == "Finished"

    assert data.itemImport.name("i000007") == "None"
    assert data.itemImport.name("i000008") == "Minor"
    assert data.itemImport.name("i000009") == "Major"
    assert data.itemImport.name("i00000a") == "Main"

    assert data.itemStatus.cols("s000000") == (100, 100, 100)
    assert data.itemStatus.cols("s000001") == (200, 50, 0)
    assert data.itemStatus.cols("s000002") == (182, 60, 0)
    assert data.itemStatus.cols("s000003") == (193, 129, 0)
    assert data.itemStatus.cols("s000004") == (193, 129, 0)
    assert data.itemStatus.cols("s000005") == (193, 129, 0)
    assert data.itemStatus.cols("s000006") == (58, 180, 58)

    assert data.itemImport.cols("i000007") == (100, 100, 100)
    assert data.itemImport.cols("i000008") == (0, 122, 188)
    assert data.itemImport.cols("i000009") == (21, 0, 180)
    assert data.itemImport.cols("i00000a") == (117, 0, 175)

    assert data.itemStatus.count("s000000") == 0
    assert data.itemStatus.count("s000001") == 0
    assert data.itemStatus.count("s000002") == 0
    assert data.itemStatus.count("s000003") == 0
    assert data.itemStatus.count("s000004") == 0
    assert data.itemStatus.count("s000005") == 0
    assert data.itemStatus.count("s000006") == 0

    assert data.itemImport.count("i000007") == 0
    assert data.itemImport.count("i000008") == 0
    assert data.itemImport.count("i000009") == 0
    assert data.itemImport.count("i00000a") == 0

    # Compare content
    dumpFile = tstPaths.outDir / "projectXML_ReadLegacy12.json"
    compFile = tstPaths.refDir / "projectXML_ReadLegacy12.json"
    with open(dumpFile, mode="w", encoding="utf-8") as dump:
        json.dump(content, dump, indent=2)
    assert cmpFiles(dumpFile, compFile)

    packedContent = []
    mockProject = MockProject()
    mockProject.__setattr__("data", data)
    status = {}
    for entry in content:
        item = NWItem(mockProject, "0000000000000")  # type: ignore
        item.unpack(entry)
        status[item.itemHandle] = item.getImportStatus(incIcon=False)[0]
        packedContent.append(item.pack())

    assert status == {
        "7031beac91f75": "Started",
        "53b69b83cdafc": "Started",
        "974e400180a99": "New",
        "edca4be2fcaf8": "New",
        "e7ded148d6e4a": "1st Draft",
        "6a2d6d5f4f401": "Notes",
        "636b6aa9b697b": "1st Draft",
        "bc0cbd2a407f3": "1st Draft",
        "ba8a28a246524": "New",
        "96b68994dfa3d": "2nd Draft",
        "88706ddc78b1b": "1st Draft",
        "ae7339df26ded": "1st Draft",
        "f6622b4617424": "None",
        "f7e2d9f330615": "None",
        "14298de4d9524": "Minor",
        "bb2c23b3c42cc": "Major",
        "15c4492bd5107": "None",
        "b3e74dbc1f584": "Main",
        "f1471bef9f2ae": "Minor",
        "5eaea4e8cdee8": "Major",
        "6827118336ac1": "New",  # Is now treated as novel-like
        "ae9bf3c3ea159": "New",  # Is now treated as novel-like
        "8a5deb88c0e97": "1st Draft",
        "98acd8c76c93a": "None",
        "b8136a5a774a0": "New",
    }

    # Save the project again, which should produce an identical project xml
    timeStamp = int(datetime.fromisoformat(xmlReader.timeStamp).timestamp())
    xmlWriter = ProjectXMLWriter(fncPath / nwFiles.PROJ_FILE)
    data.setUuid("d0f3fe10-c6e6-4310-8bfd-181eb4224eed")
    assert xmlWriter.write(data, packedContent, timeStamp, 1000) is True
    testFile = tstPaths.outDir / "projectXML_ReadLegacy12.nwx"
    compFile = tstPaths.refDir / "projectXML_ReadLegacy12.nwx"
    copyfile(outFile, testFile)
    assert cmpFiles(testFile, compFile)

# END Test testCoreProjectXML_ReadLegacy12


@pytest.mark.core
def testCoreProjectXML_ReadLegacy13(tstPaths, fncPath, mockRnd):
    """Test reading the version 1.3 XML file format."""
    refFile = tstPaths.filesDir / "nwProject-1.3.nwx"
    xmlFile = fncPath / "nwProject-1.3.nwx"
    outFile = fncPath / "nwProject.nwx"
    copyfile(refFile, xmlFile)

    xmlReader = ProjectXMLReader(xmlFile)
    assert xmlReader.state == XMLReadState.NO_ACTION

    data = NWProjectData(MockProject())  # type: ignore
    content = []

    assert xmlReader.read(data, content) is True
    assert xmlReader.state == XMLReadState.WAS_LEGACY
    assert xmlReader.xmlRoot == "novelWriterXML"
    assert xmlReader.xmlVersion == 0x0103
    assert xmlReader.appVersion == "1.6.6"
    assert xmlReader.hexVersion == 0x010606f0

    # Check loaded data
    assert data.name == "Sample Project"
    assert data.author == "Jay Doh"  # Only last author is preserved
    assert data.saveCount == 5
    assert data.autoCount == 10
    assert data.editTime == 1000

    assert data.doBackup is True
    assert data.language == "en_GB"
    assert data.spellCheck is True
    assert data.spellLang == "en_GB"
    assert data.initCounts == (830, 376)
    assert data.currCounts == (830, 376)

    assert data.getLastHandle("editor") is None  # Dropped by conversion
    assert data.getLastHandle("viewer") is None  # Dropped by conversion
    assert data.getLastHandle("novelTree") is None  # Doesn't exist in 1.3
    assert data.getLastHandle("outline") is None  # Doesn't exist in 1.3

    assert data.itemStatus.name("s000000") == "New"
    assert data.itemStatus.name("s000001") == "Notes"
    assert data.itemStatus.name("s000002") == "Started"
    assert data.itemStatus.name("s000003") == "1st Draft"
    assert data.itemStatus.name("s000004") == "2nd Draft"
    assert data.itemStatus.name("s000005") == "3rd Draft"
    assert data.itemStatus.name("s000006") == "Finished"

    assert data.itemImport.name("i000007") == "None"
    assert data.itemImport.name("i000008") == "Minor"
    assert data.itemImport.name("i000009") == "Major"
    assert data.itemImport.name("i00000a") == "Main"

    assert data.itemStatus.cols("s000000") == (100, 100, 100)
    assert data.itemStatus.cols("s000001") == (200, 50, 0)
    assert data.itemStatus.cols("s000002") == (182, 60, 0)
    assert data.itemStatus.cols("s000003") == (193, 129, 0)
    assert data.itemStatus.cols("s000004") == (193, 129, 0)
    assert data.itemStatus.cols("s000005") == (193, 129, 0)
    assert data.itemStatus.cols("s000006") == (58, 180, 58)

    assert data.itemImport.cols("i000007") == (100, 100, 100)
    assert data.itemImport.cols("i000008") == (0, 122, 188)
    assert data.itemImport.cols("i000009") == (21, 0, 180)
    assert data.itemImport.cols("i00000a") == (117, 0, 175)

    assert data.itemStatus.count("s000000") == 0
    assert data.itemStatus.count("s000001") == 0
    assert data.itemStatus.count("s000002") == 0
    assert data.itemStatus.count("s000003") == 0
    assert data.itemStatus.count("s000004") == 0
    assert data.itemStatus.count("s000005") == 0
    assert data.itemStatus.count("s000006") == 0

    assert data.itemImport.count("i000007") == 0
    assert data.itemImport.count("i000008") == 0
    assert data.itemImport.count("i000009") == 0
    assert data.itemImport.count("i00000a") == 0

    # Compare content
    dumpFile = tstPaths.outDir / "projectXML_ReadLegacy13.json"
    compFile = tstPaths.refDir / "projectXML_ReadLegacy13.json"
    with open(dumpFile, mode="w", encoding="utf-8") as dump:
        json.dump(content, dump, indent=2)
    assert cmpFiles(dumpFile, compFile)

    packedContent = []
    mockProject = MockProject()
    mockProject.__setattr__("data", data)
    status = {}
    for entry in content:
        item = NWItem(mockProject, "0000000000000")  # type: ignore
        item.unpack(entry)
        status[item.itemHandle] = item.getImportStatus(incIcon=False)[0]
        packedContent.append(item.pack())

    assert status == {
        "7031beac91f75": "Started",
        "53b69b83cdafc": "Started",
        "974e400180a99": "New",
        "edca4be2fcaf8": "New",
        "e7ded148d6e4a": "1st Draft",
        "6a2d6d5f4f401": "Notes",
        "636b6aa9b697b": "1st Draft",
        "bc0cbd2a407f3": "1st Draft",
        "ba8a28a246524": "New",
        "96b68994dfa3d": "2nd Draft",
        "88706ddc78b1b": "1st Draft",
        "ae7339df26ded": "1st Draft",
        "f6622b4617424": "None",
        "f7e2d9f330615": "None",
        "14298de4d9524": "Minor",
        "bb2c23b3c42cc": "Major",
        "15c4492bd5107": "None",
        "b3e74dbc1f584": "Main",
        "f1471bef9f2ae": "Minor",
        "5eaea4e8cdee8": "Major",
        "6827118336ac1": "New",  # Is now treated as novel-like
        "ae9bf3c3ea159": "New",  # Is now treated as novel-like
        "8a5deb88c0e97": "1st Draft",
        "98acd8c76c93a": "None",
        "b8136a5a774a0": "New",
    }

    # Save the project again, which should produce an identical project xml
    timeStamp = int(datetime.fromisoformat(xmlReader.timeStamp).timestamp())
    xmlWriter = ProjectXMLWriter(fncPath / nwFiles.PROJ_FILE)
    data.setUuid("d0f3fe10-c6e6-4310-8bfd-181eb4224eed")
    assert xmlWriter.write(data, packedContent, timeStamp, 1000) is True
    testFile = tstPaths.outDir / "projectXML_ReadLegacy13.nwx"
    compFile = tstPaths.refDir / "projectXML_ReadLegacy13.nwx"
    copyfile(outFile, testFile)
    assert cmpFiles(testFile, compFile)

# END Test testCoreProjectXML_ReadLegacy13


@pytest.mark.core
def testCoreProjectXML_ReadLegacy14(tstPaths, fncPath, mockRnd):
    """Test reading the version 1.4 XML file format."""
    refFile = tstPaths.filesDir / "nwProject-1.4.nwx"
    xmlFile = fncPath / "nwProject-1.4.nwx"
    outFile = fncPath / "nwProject.nwx"
    copyfile(refFile, xmlFile)

    xmlReader = ProjectXMLReader(xmlFile)
    assert xmlReader.state == XMLReadState.NO_ACTION

    data = NWProjectData(MockProject())  # type: ignore
    content = []

    assert xmlReader.read(data, content) is True
    assert xmlReader.state == XMLReadState.WAS_LEGACY
    assert xmlReader.xmlRoot == "novelWriterXML"
    assert xmlReader.xmlVersion == 0x0104
    assert xmlReader.appVersion == "2.0-rc1"
    assert xmlReader.hexVersion == 0x020000c1

    # Check loaded data
    assert data.name == "Sample Project"
    assert data.author == "Jay Doh"  # Only last author is preserved
    assert data.saveCount == 5
    assert data.autoCount == 10
    assert data.editTime == 1000

    assert data.doBackup is True
    assert data.language == "en_GB"
    assert data.spellCheck is True
    assert data.spellLang == "en_GB"
    assert data.initCounts == (954, 409)
    assert data.currCounts == (954, 409)

    assert data.getLastHandle("editor") is None  # Dropped by conversion
    assert data.getLastHandle("viewer") is None  # Dropped by conversion
    assert data.getLastHandle("novelTree") is None  # Doesn't exist in 1.3
    assert data.getLastHandle("outline") is None  # Doesn't exist in 1.3

    assert data.itemStatus.name("sf12341") == "New"
    assert data.itemStatus.name("sf24ce6") == "Notes"
    assert data.itemStatus.name("sc24b8f") == "Started"
    assert data.itemStatus.name("s90e6c9") == "1st Draft"
    assert data.itemStatus.name("sd51c5b") == "2nd Draft"
    assert data.itemStatus.name("s8ae72a") == "3rd Draft"
    assert data.itemStatus.name("s78ea90") == "Finished"

    assert data.itemImport.name("ia857f0") == "None"
    assert data.itemImport.name("icfb3a5") == "Minor"
    assert data.itemImport.name("i2d7a54") == "Major"
    assert data.itemImport.name("i56be10") == "Main"

    assert data.itemStatus.cols("sf12341") == (100, 100, 100)
    assert data.itemStatus.cols("sf24ce6") == (200, 50, 0)
    assert data.itemStatus.cols("sc24b8f") == (182, 60, 0)
    assert data.itemStatus.cols("s90e6c9") == (193, 129, 0)
    assert data.itemStatus.cols("sd51c5b") == (193, 129, 0)
    assert data.itemStatus.cols("s8ae72a") == (193, 129, 0)
    assert data.itemStatus.cols("s78ea90") == (58, 180, 58)

    assert data.itemImport.cols("ia857f0") == (100, 100, 100)
    assert data.itemImport.cols("icfb3a5") == (0, 122, 188)
    assert data.itemImport.cols("i2d7a54") == (21, 0, 180)
    assert data.itemImport.cols("i56be10") == (117, 0, 175)

    assert data.itemStatus.count("sf12341") == 4
    assert data.itemStatus.count("sf24ce6") == 2
    assert data.itemStatus.count("sc24b8f") == 3
    assert data.itemStatus.count("s90e6c9") == 7
    assert data.itemStatus.count("sd51c5b") == 0
    assert data.itemStatus.count("s8ae72a") == 0
    assert data.itemStatus.count("s78ea90") == 1

    assert data.itemImport.count("ia857f0") == 5
    assert data.itemImport.count("icfb3a5") == 2
    assert data.itemImport.count("i2d7a54") == 2
    assert data.itemImport.count("i56be10") == 1

    # Compare content
    dumpFile = tstPaths.outDir / "projectXML_ReadLegacy14.json"
    compFile = tstPaths.refDir / "projectXML_ReadLegacy14.json"
    with open(dumpFile, mode="w", encoding="utf-8") as dump:
        json.dump(content, dump, indent=2)
    assert cmpFiles(dumpFile, compFile)

    packedContent = []
    mockProject = MockProject()
    mockProject.__setattr__("data", data)
    status = {}
    for entry in content:
        item = NWItem(mockProject, "0000000000000")  # type: ignore
        item.unpack(entry)
        status[item.itemHandle] = item.getImportStatus(incIcon=False)[0]
        packedContent.append(item.pack())

    assert status == {
        "7031beac91f75": "Started",
        "53b69b83cdafc": "Started",
        "974e400180a99": "New",
        "edca4be2fcaf8": "1st Draft",
        "6a2d6d5f4f401": "Notes",
        "636b6aa9b697b": "1st Draft",
        "bc0cbd2a407f3": "1st Draft",
        "ba8a28a246524": "Finished",
        "96b68994dfa3d": "Notes",
        "88706ddc78b1b": "1st Draft",
        "ae7339df26ded": "1st Draft",
        "e5e47ebf63b1c": "New",
        "bacb7059e3083": "Started",
        "a520879ca0b45": "1st Draft",
        "f6622b4617424": "None",
        "f7e2d9f330615": "None",
        "14298de4d9524": "Minor",
        "bb2c23b3c42cc": "Major",
        "15c4492bd5107": "None",
        "b3e74dbc1f584": "Main",
        "f1471bef9f2ae": "Minor",
        "5eaea4e8cdee8": "Major",
        "6827118336ac1": "New",
        "ae9bf3c3ea159": "New",
        "8a5deb88c0e97": "1st Draft",
        "98acd8c76c93a": "None",
        "b8136a5a774a0": "None",
    }

    # Save the project again, which should produce an identical project xml
    timeStamp = int(datetime.fromisoformat(xmlReader.timeStamp).timestamp())
    xmlWriter = ProjectXMLWriter(fncPath / nwFiles.PROJ_FILE)
    data.setUuid("d0f3fe10-c6e6-4310-8bfd-181eb4224eed")
    assert xmlWriter.write(data, packedContent, timeStamp, 1000) is True
    testFile = tstPaths.outDir / "projectXML_ReadLegacy14.nwx"
    compFile = tstPaths.refDir / "projectXML_ReadLegacy14.nwx"
    copyfile(outFile, testFile)
    assert cmpFiles(testFile, compFile)

# END Test testCoreProjectXML_ReadLegacy14
