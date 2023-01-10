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

from novelwriter.core.project import NWProject
from novelwriter.mbuild.docbuild import NWBuildDocument

BUILD_CONF = {
    "format.fmtTitle": "Title: %title%",
    "format.fmtChapter": "Chapter: %title%",
    "format.fmtUnnumbered": "%title%",
    "format.fmtScene": "Scene: %title%",
    "format.fmtSection": "Section: %title%",
    "format.buildLang": "en_GB",
    "format.hideScene": False,
    "format.hideSection": False,
    "format.textFont": "Arial",
    "format.textSize": 12,
    "format.lineHeight": 1.5,
    "format.justifyText": True,
    "format.noStyling": False,
    "format.replaceUCode": False,
    "filter.includeSynopsis": True,
    "filter.includeComments": True,
    "filter.includeKeywords": True,
    "filter.includeBody": True,
}


@pytest.mark.core
def testMBuildDocBuild_OpenDocument(mockGUI, prjLipsum, fncPath, tstPaths):
    """Test builing an open document manuscript.
    """
    theProject = NWProject(mockGUI)
    theProject.openProject(prjLipsum)

    docBuild = NWBuildDocument(theProject)
    docBuild.setBuildConfig(BUILD_CONF)

    for tItem in theProject.tree:
        docBuild.addDocument(tItem.itemHandle)

    count = 0
    error = []
    for _, success in docBuild.buildOpenDocument(fncPath / "Lorem Ipsum.fodt", True):
        count += 1 if success else 0
        if docBuild.error:
            error.append(docBuild.error)

    assert count == 21
    assert error == []

# END Test testMBuildDocBuild_OpenDocument
