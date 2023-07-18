"""
novelWriter – Manuscript Build Settings Tester
==============================================

This file is a part of novelWriter
Copyright 2018–2023, Veronica Berglyd Olsen

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

import json
import uuid
import pytest
import shutil

from pathlib import Path

from tools import C, buildTestProject
from mocked import causeOSError

from novelwriter.enum import nwBuildFmt, nwItemClass
from novelwriter.constants import nwFiles
from novelwriter.core.item import NWItem
from novelwriter.core.project import NWProject
from novelwriter.core.buildsettings import BuildCollection, BuildSettings, FilterMode


def isUUID(value):
    """Checks if a value is a valid UUID object."""
    try:
        uuid.UUID(value)
        return True
    except Exception:
        return False


@pytest.mark.core
def testCoreBuildSettings_ClassAttributes(fncPath: Path):
    """Test the BuildSettings class attributes."""
    build = BuildSettings()
    assert build.changed is False

    # Name is always converted to string
    build.setName(None)  # type: ignore
    assert build.name == "None"

    build.setName("Test Build")
    assert build.name == "Test Build"

    # Only valid UUIDs are accpeted, anything else generates a new UUID
    build.setBuildID("5cf45d24-f496-42c9-8733-529a9e52a62b")
    assert build.buildID == "5cf45d24-f496-42c9-8733-529a9e52a62b"

    build.setBuildID(None)  # type: ignore
    assert build.buildID != "5cf45d24-f496-42c9-8733-529a9e52a62b"
    assert isUUID(build.buildID)

    build.setBuildID("qcf45d24-f496-42c9-8733-529a9e52a62b")
    assert build.buildID != "qcf45d24-f496-42c9-8733-529a9e52a62b"
    assert isUUID(build.buildID)

    # Last path must be valid, if not it defaults to $HOME
    build.setLastPath("/path/to/nowhere")
    assert build.lastPath == Path.home()

    build.setLastPath(None)
    assert build.lastPath == Path.home()

    (fncPath / "test.txt").write_text("foobar")
    build.setLastPath(fncPath / "test.txt")  # Can't be a file
    assert build.lastPath == Path.home()

    build.setLastPath(fncPath)
    assert build.lastPath == fncPath

    build.setLastPath(str(fncPath))  # String paths are also ok
    assert build.lastPath == fncPath

    # Last path no longer exists -> fallback to $HOME
    testDir = fncPath / "test_dir"
    testDir.mkdir()
    build.setLastPath(testDir)
    assert build.lastPath == testDir
    testDir.rmdir()
    assert build.lastPath == Path.home()

    # Last build name
    build.setLastBuildName(None)  # type: ignore
    assert build.lastBuildName == "None"

    build.setLastBuildName("\tBuild Name    ")
    assert build.lastBuildName == "Build Name"

    # Last build format
    build.setLastFormat(None)  # type: ignore
    assert build.lastFormat == nwBuildFmt.ODT  # Default value

    build.setLastFormat(nwBuildFmt.FODT)
    assert build.lastFormat == nwBuildFmt.FODT

    # Changes are recorded
    assert build.changed is True
    build.resetChangedState()
    assert build.changed is False

    # Set some sensible values
    build.setName("Test Build")
    build.setBuildID("5cf45d24-f496-42c9-8733-529a9e52a62b")
    build.setLastPath(fncPath)
    build.setLastBuildName("Build Name")
    build.setLastFormat(nwBuildFmt.HTML)

    # Pack the values
    data = build.pack()
    assert data["name"] == "Test Build"
    assert data["uuid"] == "5cf45d24-f496-42c9-8733-529a9e52a62b"
    assert data["path"] == str(fncPath)
    assert data["build"] == "Build Name"
    assert data["format"] == nwBuildFmt.HTML.name

    # Unpack into new object
    another = BuildSettings()
    another.unpack(data)
    more = another.pack()
    assert more["name"] == "Test Build"
    assert more["uuid"] == "5cf45d24-f496-42c9-8733-529a9e52a62b"
    assert more["path"] == str(fncPath)
    assert more["build"] == "Build Name"
    assert more["format"] == nwBuildFmt.HTML.name

# END Test testCoreBuildSettings_ClassAttributes


@pytest.mark.core
def testCoreBuildSettings_BuildValues():
    """Test BuildSettings get/set of build values."""
    build = BuildSettings()

    strSetting = "headings.fmtTitle"
    intSetting = "format.textSize"
    boolSetting = "filter.includeNovel"
    floatSetting = "format.lineHeight"

    # Invalid setting
    assert build.setValue("foo", "bar") is False

    # Value must be correct type
    assert build.setValue(strSetting, 15) is False
    assert build.setValue(intSetting, 15.0) is False
    assert build.setValue(boolSetting, "string") is False
    assert build.setValue(floatSetting, 15) is False

    # Check min/max range
    assert build.setValue(floatSetting, 200.0) is True
    assert build.getFloat(floatSetting) == 3.0
    assert build.setValue(floatSetting, 0.0) is True
    assert build.getFloat(floatSetting) == 0.75

    # Check string values
    assert build.setValue(strSetting, "foobar") is True
    assert build.getStr(strSetting) == "foobar"
    assert build.getInt(strSetting) == 0
    assert build.getBool(strSetting) is True
    assert build.getFloat(strSetting) == 0.0

    # Check int values
    assert build.setValue(intSetting, 42) is True
    assert build.getStr(intSetting) == "42"
    assert build.getInt(intSetting) == 42
    assert build.getBool(intSetting) is True
    assert build.getFloat(intSetting) == 42.0

    # Check bool values
    assert build.setValue(boolSetting, True) is True
    assert build.getStr(boolSetting) == "True"
    assert build.getInt(boolSetting) == 1
    assert build.getBool(boolSetting) is True
    assert build.getFloat(boolSetting) == 1.0

    # Check float values
    assert build.setValue(floatSetting, 2.5) is True
    assert build.getStr(floatSetting) == "2.5"
    assert build.getInt(floatSetting) == 2
    assert build.getBool(floatSetting) is True
    assert build.getFloat(floatSetting) == 2.5

    # Check labels
    assert build.getLabel(strSetting) == "Title Headings"
    assert BuildSettings.getLabel(strSetting) == "Title Headings"

    # Pack the values
    data = build.pack()
    assert data["settings"][strSetting] == "foobar"
    assert data["settings"][intSetting] == 42
    assert data["settings"][boolSetting] is True
    assert data["settings"][floatSetting] == 2.5

    # Unpack into new object
    another = BuildSettings()
    another.unpack(data)
    more = another.pack()
    assert more["settings"][strSetting] == "foobar"
    assert more["settings"][intSetting] == 42
    assert more["settings"][boolSetting] is True
    assert more["settings"][floatSetting] == 2.5

# END Test testCoreBuildSettings_BuildValues


@pytest.mark.core
def testCoreBuildSettings_Filters(mockGUI, fncPath: Path, mockRnd):
    """Test filters for project items."""
    project = NWProject(mockGUI)
    buildTestProject(project, fncPath)
    build = BuildSettings()

    # Add some more items
    hArchRoot = project.newRoot(nwItemClass.ARCHIVE, "Archive")
    hPlotDoc  = project.newFile("Main Plot", C.hPlotRoot)
    hCharDoc  = project.newFile("Jane Doe", C.hCharRoot)
    initLen = len(project.tree)

    # With no changes
    assert build.isRootAllowed(C.hNovelRoot) is True
    assert build.isRootAllowed(C.hPlotRoot) is True
    assert build.isRootAllowed(C.hCharRoot) is True
    assert build.isRootAllowed(C.hWorldRoot) is True

    assert build.buildItemFilter(project, withRoots=False) == {
        C.hNovelRoot:  (False, FilterMode.SKIPPED),
        C.hPlotRoot:   (False, FilterMode.SKIPPED),
        C.hCharRoot:   (False, FilterMode.SKIPPED),
        C.hWorldRoot:  (False, FilterMode.SKIPPED),
        C.hTitlePage:  (True,  FilterMode.FILTERED),
        C.hChapterDir: (False, FilterMode.SKIPPED),
        C.hChapterDoc: (True,  FilterMode.FILTERED),
        C.hSceneDoc:   (True,  FilterMode.FILTERED),
        hArchRoot:     (False, FilterMode.SKIPPED),
        hPlotDoc:      (False, FilterMode.FILTERED),
        hCharDoc:      (False, FilterMode.FILTERED),
    }

    # Enable notes and roots
    build.setValue("filter.includeNotes", True)
    assert build.buildItemFilter(project, withRoots=True) == {
        C.hNovelRoot:  (True,  FilterMode.ROOT),
        C.hPlotRoot:   (True,  FilterMode.ROOT),
        C.hCharRoot:   (True,  FilterMode.ROOT),
        C.hWorldRoot:  (False, FilterMode.SKIPPED),  # World folder is empty
        C.hTitlePage:  (True,  FilterMode.FILTERED),
        C.hChapterDir: (False, FilterMode.SKIPPED),
        C.hChapterDoc: (True,  FilterMode.FILTERED),
        C.hSceneDoc:   (True,  FilterMode.FILTERED),
        hArchRoot:     (False, FilterMode.SKIPPED),
        hPlotDoc:      (True,  FilterMode.FILTERED),
        hCharDoc:      (True,  FilterMode.FILTERED),
    }

    # Skip plot and char roots
    build.setValue("filter.includeNotes", True)
    build.setAllowRoot(C.hPlotRoot, False)
    build.setAllowRoot(C.hCharRoot, False)
    assert build.isRootAllowed(C.hNovelRoot) is True
    assert build.isRootAllowed(C.hPlotRoot) is False
    assert build.isRootAllowed(C.hCharRoot) is False
    assert build.isRootAllowed(C.hWorldRoot) is True
    assert build.buildItemFilter(project, withRoots=True) == {
        C.hNovelRoot:  (True,  FilterMode.ROOT),
        C.hPlotRoot:   (False, FilterMode.SKIPPED),
        C.hCharRoot:   (False, FilterMode.SKIPPED),
        C.hWorldRoot:  (False, FilterMode.SKIPPED),
        C.hTitlePage:  (True,  FilterMode.FILTERED),
        C.hChapterDir: (False, FilterMode.SKIPPED),
        C.hChapterDoc: (True,  FilterMode.FILTERED),
        C.hSceneDoc:   (True,  FilterMode.FILTERED),
        hArchRoot:     (False, FilterMode.SKIPPED),
        hPlotDoc:      (False, FilterMode.SKIPPED),  # Now also skipped since in plot
        hCharDoc:      (False, FilterMode.SKIPPED),  # Now also skipped since in char
    }

    # Enable char root again, but exclude char doc and scene doc
    build.setValue("filter.includeNotes", True)
    build.setAllowRoot(C.hPlotRoot, False)
    build.setAllowRoot(C.hCharRoot, True)
    build.setExcluded(C.hSceneDoc)
    build.setExcluded(hCharDoc)  # type: ignore
    assert build.isRootAllowed(C.hNovelRoot) is True
    assert build.isRootAllowed(C.hPlotRoot) is False
    assert build.isRootAllowed(C.hCharRoot) is True
    assert build.isRootAllowed(C.hWorldRoot) is True
    assert build.buildItemFilter(project, withRoots=True) == {
        C.hNovelRoot:  (True,  FilterMode.ROOT),
        C.hPlotRoot:   (False, FilterMode.SKIPPED),
        C.hCharRoot:   (False, FilterMode.SKIPPED),  # Is skipped anyway since doc is skipped
        C.hWorldRoot:  (False, FilterMode.SKIPPED),
        C.hTitlePage:  (True,  FilterMode.FILTERED),
        C.hChapterDir: (False, FilterMode.SKIPPED),
        C.hChapterDoc: (True,  FilterMode.FILTERED),
        C.hSceneDoc:   (False, FilterMode.EXCLUDED),
        hArchRoot:     (False, FilterMode.SKIPPED),
        hPlotDoc:      (False, FilterMode.SKIPPED),
        hCharDoc:      (False, FilterMode.EXCLUDED),
    }

    # Disable notes, but include char doc
    build.setValue("filter.includeNotes", False)
    build.setAllowRoot(C.hPlotRoot, False)
    build.setAllowRoot(C.hCharRoot, True)
    build.setExcluded(C.hSceneDoc)
    build.setIncluded(hCharDoc)  # type: ignore
    assert build.isRootAllowed(C.hNovelRoot) is True
    assert build.isRootAllowed(C.hPlotRoot) is False
    assert build.isRootAllowed(C.hCharRoot) is True
    assert build.isRootAllowed(C.hWorldRoot) is True
    assert build.buildItemFilter(project, withRoots=True) == {
        C.hNovelRoot:  (True,  FilterMode.ROOT),
        C.hPlotRoot:   (False, FilterMode.SKIPPED),
        C.hCharRoot:   (True,  FilterMode.ROOT),
        C.hWorldRoot:  (False, FilterMode.SKIPPED),
        C.hTitlePage:  (True,  FilterMode.FILTERED),
        C.hChapterDir: (False, FilterMode.SKIPPED),
        C.hChapterDoc: (True,  FilterMode.FILTERED),
        C.hSceneDoc:   (False, FilterMode.EXCLUDED),
        hArchRoot:     (False, FilterMode.SKIPPED),
        hPlotDoc:      (False, FilterMode.SKIPPED),
        hCharDoc:      (True,  FilterMode.INCLUDED),
    }

    # Set everything back to filered
    build.setValue("filter.includeNotes", False)
    build.setAllowRoot(C.hPlotRoot, False)
    build.setAllowRoot(C.hCharRoot, True)
    build.setFiltered(C.hSceneDoc)
    build.setFiltered(hCharDoc)  # type: ignore
    assert build.isRootAllowed(C.hNovelRoot) is True
    assert build.isRootAllowed(C.hPlotRoot) is False
    assert build.isRootAllowed(C.hCharRoot) is True
    assert build.isRootAllowed(C.hWorldRoot) is True
    assert build.buildItemFilter(project, withRoots=True) == {
        C.hNovelRoot:  (True,  FilterMode.ROOT),
        C.hPlotRoot:   (False, FilterMode.SKIPPED),
        C.hCharRoot:   (False, FilterMode.SKIPPED),
        C.hWorldRoot:  (False, FilterMode.SKIPPED),
        C.hTitlePage:  (True,  FilterMode.FILTERED),
        C.hChapterDir: (False, FilterMode.SKIPPED),
        C.hChapterDoc: (True,  FilterMode.FILTERED),
        C.hSceneDoc:   (True,  FilterMode.FILTERED),
        hArchRoot:     (False, FilterMode.SKIPPED),
        hPlotDoc:      (False, FilterMode.SKIPPED),
        hCharDoc:      (False, FilterMode.FILTERED),
    }

    # Check error handling
    project.tree._treeOrder.append("00000000000ff")
    project.tree._projTree["00000000000ff"] = NWItem(project)
    assert project.tree["00000000000ff"].itemHandle is None  # type: ignore
    filtered = build.buildItemFilter(project, withRoots=False)
    assert len(filtered) == initLen

    # No valid project provided
    assert build.buildItemFilter(None) == {}  # type: ignore

# END Test testCoreBuildSettings_Filters


@pytest.mark.core
def testCoreBuildSettings_Collection(monkeypatch, mockGUI, fncPath: Path, mockRnd):
    """Test the collections class for builds."""
    project = NWProject(mockGUI)
    buildTestProject(project, fncPath)
    buildsFile = project.storage.getMetaFile(nwFiles.BUILDS_FILE)
    assert isinstance(buildsFile, Path)

    # No initial builds in a fresh project
    builds = BuildCollection(project)
    assert len(builds) == 0
    assert not buildsFile.exists()

    # Greate a default build
    buildOne = BuildSettings()
    buildOne.setName("Build One")
    buildIDOne = buildOne.buildID

    # Check that invalid type is ahndled
    builds.setBuild(None)  # type: ignore
    assert len(builds) == 0
    assert not buildsFile.exists()
    assert builds.getBuild(buildIDOne) is None

    # Add the build
    builds.setBuild(buildOne)
    assert len(builds) == 1
    assert buildsFile.exists()
    assert builds.getBuild(buildIDOne).buildID == buildIDOne  # type: ignore

    # Create another build
    buildTwo = BuildSettings()
    buildTwo.setName("Build Two")
    buildIDTwo = buildTwo.buildID

    # Check that we can extract infor about the builds
    builds.setBuild(buildTwo)
    assert len(builds) == 2
    assert buildsFile.exists()
    assert builds.getBuild(buildIDTwo).buildID == buildIDTwo  # type: ignore
    assert list(builds.builds()) == [
        (buildIDOne, "Build One"),
        (buildIDTwo, "Build Two"),
    ]

    # Check the file content
    data = json.loads(buildsFile.read_text(encoding="utf-8"))
    assert list(data["novelWriter.builds"].keys()) == [buildIDOne, buildIDTwo]

    # Remove a build
    builds.removeBuild(buildIDOne)
    assert builds.getBuild(buildIDOne) is None
    assert list(builds.builds()) == [
        (buildIDTwo, "Build Two"),
    ]

    # Check the file content
    data = json.loads(buildsFile.read_text(encoding="utf-8"))
    assert list(data["novelWriter.builds"].keys()) == [buildIDTwo]
    builds.setBuild(buildOne)
    assert list(builds.builds()) == [
        (buildIDTwo, "Build Two"),
        (buildIDOne, "Build One"),
    ]

    # Check errors: No valid path
    with monkeypatch.context() as mp:
        mp.setattr("novelwriter.core.storage.NWStorage.getMetaFile", lambda *a: None)
        assert builds._loadCollection() is False
        assert builds._saveCollection() is False

    # Check errors: I/O error
    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        assert builds._loadCollection() is False
        assert builds._saveCollection() is False

    # Check errors: Can't parse json file
    shutil.copy(buildsFile, buildsFile.with_suffix(".bak"))
    buildsFile.write_text("foobar")
    assert builds._loadCollection() is False

    # Check errors: Valid jason file, but list instead of object
    buildsFile.write_text("[]")
    assert builds._loadCollection() is False
    buildsFile.unlink()
    shutil.copy(buildsFile.with_suffix(".bak"), buildsFile)

    # Load builds file into new object
    another = BuildCollection(project)
    assert list(another.builds()) == [
        (buildIDTwo, "Build Two"),
        (buildIDOne, "Build One"),
    ]

# END Test testCoreBuildSettings_Collection
