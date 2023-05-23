"""
novelWriter – Manuscript Builder Class Tests
============================================

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

import pytest

from shutil import copyfile

from mock import causeException, causeOSError
from novelwriter.core.buildsettings import BuildSettings
from tools import ODT_IGNORE, cmpFiles

from novelwriter.core.project import NWProject
from novelwriter.core.docbuild import NWBuildDocument

# BUILD_CONF = {
#     "format.fmtTitle": "Title: %title%",
#     "format.fmtChapter": "Chapter: %title%",
#     "format.fmtUnnumbered": "%title%",
#     "format.fmtScene": "Scene: %title%",
#     "format.fmtSection": "Section: %title%",
#     "format.buildLang": "en_GB",
#     "format.hideScene": False,
#     "format.hideSection": False,
#     "format.textFont": "Arial",
#     "format.textSize": 12,
#     "format.lineHeight": 1.5,
#     "format.justifyText": True,
#     "format.noStyling": False,
#     "format.replaceUCode": False,
#     "filter.includeSynopsis": True,
#     "filter.includeComments": True,
#     "filter.includeKeywords": True,
#     "filter.includeBody": True,
#     "process.replaceTabs": True,
# }

BUILD_CONF = {
    "name": "Test Build",
    "uuid": "f8796eee-e234-4e8a-8355-b2709177e53c",
    "settings": {
        "filter.includeNovel": True,
        "filter.includeNotes": True,
        "filter.includeInactive": False,
        "headings.fmtTitle": "Title: {Title}",
        "headings.fmtChapter": "Chapter: {Title}",
        "headings.fmtUnnumbered": "{Title}",
        "headings.fmtScene": "Scene: {Title}",
        "headings.fmtSection": "Section: {Title}",
        "headings.hideScene": False,
        "headings.hideSection": False,
        "text.includeSynopsis": True,
        "text.includeComments": True,
        "text.includeKeywords": True,
        "text.includeBodyText": True,
        "text.addNoteHeadings": True,
        "format.buildLang": "en_GB",
        "format.textFont": "Arial",
        "format.textSize": 12,
        "format.lineHeight": 1.5,
        "format.justifyText": True,
        "format.stripUnicode": False,
        "format.replaceTabs": False,
        "odt.addColours": True,
        "html.addStyles": True,
    },
    "content": {
        "included": [],
        "excluded": [],
        "skipRoot": [],
    },
}


@pytest.mark.core
def testCoreDocBuild_OpenDocument(monkeypatch, mockGUI, prjLipsum, fncPath, tstPaths):
    """Test builing an open document manuscript.
    """
    project = NWProject(mockGUI)
    project.openProject(prjLipsum)

    build = BuildSettings()
    build.unpack(BUILD_CONF)

    docBuild = NWBuildDocument(project, build)
    docBuild.queueAll()

    assert docBuild.buildLength == 21

    # Check FODT Build
    # ================

    docFile = fncPath / "Lorem Ipsum.fodt"
    tstFile = tstPaths.outDir / "mBuildDocBuild_OpenDocument_Lorem_Ipsum.fodt"
    cmpFile = tstPaths.refDir / "mBuildDocBuild_OpenDocument_Lorem_Ipsum.fodt"

    count = 0
    error = []
    for _, success in docBuild.iterBuildOpenDocument(docFile, True):
        count += 1 if success else 0
        if docBuild.error:
            error.append(docBuild.error)

    assert count == 21
    assert error == []

    copyfile(docFile, tstFile)
    assert cmpFiles(tstFile, cmpFile, ignoreStart=ODT_IGNORE)

    # Check ODT Build
    # ===============

    docFile = fncPath / "Lorem Ipsum.odt"

    count = 0
    error = []
    for _, success in docBuild.iterBuildOpenDocument(docFile, False):
        count += 1 if success else 0
        if docBuild.error:
            error.append(docBuild.error)

    assert count == 21
    assert error == []

    assert docFile.is_file()

    # Check Error Handling
    # ====================

    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)

        docFile = fncPath / "Lorem Ipsum Err.fodt"
        for _ in docBuild.iterBuildOpenDocument(docFile, True):
            pass

        assert docBuild.error == "OSError: Mock OSError"
        assert not docFile.is_file()

    # Check Build Issues
    # ==================

    with monkeypatch.context() as mp:
        mp.setattr("novelwriter.core.toodt.ToOdt.doConvert", causeException)

        docBuild.addDocument("0000000000000")
        assert docBuild.buildLength == 22

        count = 0
        error = []
        docFile = fncPath / "Lorem Ipsum Err.fodt"
        for _, success in docBuild.iterBuildOpenDocument(docFile, True):
            count += 1 if success else 0
            if docBuild.error:
                error.append(docBuild.error)

        assert count == 3
        assert error == [
            "Build: Failed to build '7a992350f3eb6'",
            "Build: Failed to build '8c58a65414c23'",
            "Build: Failed to build '88d59a277361b'",
            "Build: Failed to build 'db7e733775d4d'",
            "Build: Failed to build 'fb609cd8319dc'",
            "Build: Failed to build '88243afbe5ed8'",
            "Build: Failed to build 'f96ec11c6a3da'",
            "Build: Failed to build '846352075de7d'",
            "Build: Failed to build '441420a886d82'",
            "Build: Failed to build 'eb103bc70c90c'",
            "Build: Failed to build 'f8c0562e50f1b'",
            "Build: Failed to build '47666c91c7ccf'",
            "Build: Failed to build '67a8707f2f249'",
            "Build: Failed to build '4c4f28287af27'",
            "Build: Failed to build '6c6afb1247750'",
            "Build: Failed to build '2426c6f0ca922'",
            "Build: Failed to build '60bdf227455cc'",
            "Build: Failed to build '04468803b92e1'",
            "Build: Unknown item '0000000000000'",
        ]

# END Test testCoreDocBuild_OpenDocument


@pytest.mark.core
def testCoreDocBuild_HTML(monkeypatch, mockGUI, prjLipsum, fncPath, tstPaths):
    """Test builing an HTML manuscript.
    """
    project = NWProject(mockGUI)
    project.openProject(prjLipsum)

    build = BuildSettings()
    build.unpack(BUILD_CONF)

    docBuild = NWBuildDocument(project, build)
    docBuild.queueAll()

    assert docBuild.buildLength == 21

    # Check HTML5 Build
    # =================

    docFile = fncPath / "Lorem Ipsum.htm"
    tstFile = tstPaths.outDir / "mBuildDocBuild_HTML5_Lorem_Ipsum.htm"
    cmpFile = tstPaths.refDir / "mBuildDocBuild_HTML5_Lorem_Ipsum.htm"

    count = 0
    error = []
    for _, success in docBuild.iterBuildHTML(docFile):
        count += 1 if success else 0
        if docBuild.error:
            error.append(docBuild.error)

    assert count == 21
    assert error == []

    copyfile(docFile, tstFile)
    assert cmpFiles(tstFile, cmpFile)

    # Check Error Handling
    # ====================

    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)

        docFile = fncPath / "Lorem Ipsum Err.htm"
        for _ in docBuild.iterBuildHTML(docFile):
            pass

        assert docBuild.error == "OSError: Mock OSError"
        assert not docFile.is_file()

# END Test testCoreDocBuild_HTML


@pytest.mark.core
def testCoreDocBuild_Markdown(monkeypatch, mockGUI, prjLipsum, fncPath, tstPaths):
    """Test builing an Markdown manuscript.
    """
    project = NWProject(mockGUI)
    project.openProject(prjLipsum)

    build = BuildSettings()
    build.unpack(BUILD_CONF)

    docBuild = NWBuildDocument(project, build)
    docBuild.queueAll()

    assert docBuild.buildLength == 21

    # Check Standard Markdown Build
    # =============================

    docFile = fncPath / "Lorem Ipsum Standard.md"
    tstFile = tstPaths.outDir / "mBuildDocBuild_Standard_Markdown_Lorem_Ipsum.md"
    cmpFile = tstPaths.refDir / "mBuildDocBuild_Standard_Markdown_Lorem_Ipsum.md"

    count = 0
    error = []
    for _, success in docBuild.iterBuildMarkdown(docFile, False):
        count += 1 if success else 0
        if docBuild.error:
            error.append(docBuild.error)

    assert count == 21
    assert error == []

    copyfile(docFile, tstFile)
    assert cmpFiles(tstFile, cmpFile)

    # Check Extended Markdown Build
    # =============================

    docFile = fncPath / "Lorem Ipsum Standard.md"
    tstFile = tstPaths.outDir / "mBuildDocBuild_Extended_Markdown_Lorem_Ipsum.md"
    cmpFile = tstPaths.refDir / "mBuildDocBuild_Extended_Markdown_Lorem_Ipsum.md"

    count = 0
    error = []
    for _, success in docBuild.iterBuildMarkdown(docFile, True):
        count += 1 if success else 0
        if docBuild.error:
            error.append(docBuild.error)

    assert count == 21
    assert error == []

    copyfile(docFile, tstFile)
    assert cmpFiles(tstFile, cmpFile)

    # Check Error Handling
    # ====================

    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)

        docFile = fncPath / "Lorem Ipsum Err.md"
        for _ in docBuild.iterBuildMarkdown(docFile, False):
            pass

        assert docBuild.error == "OSError: Mock OSError"
        assert not docFile.is_file()

# END Test testCoreDocBuild_Markdown
