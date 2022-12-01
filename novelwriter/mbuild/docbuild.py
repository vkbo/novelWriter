"""
novelWriter – Build Document Tool
=================================
A class to build one or more novelWriter files to a single document

File History:
Created: 2022-12-01 [2.1b1]

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

import logging

from novelwriter.error import formatException
from novelwriter.core.toodt import ToOdt
from novelwriter.core.tohtml import ToHtml
from novelwriter.core.tomd import ToMarkdown

logger = logging.getLogger(__name__)


class NWBuildDocument:

    def __init__(self, project):

        self._project = project
        self._build = {}
        self._documents = []
        self._error = None

        return

    ##
    #  Properties
    ##

    @property
    def buildLength(self):
        return len(self._documents)

    ##
    #  Setters
    ##

    def setBuildConfig(self, config):
        """Set the build config dictionary.
        """
        self._build = config
        return

    def addDocument(self, tHandle):
        """Add a document to the build queue.
        """
        self._documents.append(tHandle)
        return

    ##
    #  Methods
    ##

    def buildOpenDocument(self, savePath, isFlat):
        """Build an Open Document file.
        """
        makeOdt = ToOdt(self._project, isFlat=isFlat)
        self._setupBuild(makeOdt)

        for i, tHandle in enumerate(self._documents):
            yield i, self._doBuild(makeOdt, tHandle)

        self._error = None
        try:
            if isFlat:
                makeOdt.saveFlatXML(savePath)
            else:
                makeOdt.saveOpenDocText(savePath)
        except Exception as exc:
            self._error = formatException(exc)

        return

    def buildHTML(self, savePath):
        """Build an HTML file.
        """
        makeHtml = ToHtml(self._project)
        self._setupBuild(makeHtml)

        if self._build.get("process.replaceTabs", False):
            makeHtml.replaceTabs()

        for i, tHandle in enumerate(self._documents):
            yield i, self._doBuild(makeHtml, tHandle)

        self._error = None
        try:
            makeHtml.saveHTML5(savePath)
        except Exception as exc:
            self._error = formatException(exc)

        return

    def buildMarkdown(self, savePath, extendedMd):
        """Build a Markdown file.
        """
        makeMd = ToMarkdown(self._project)
        self._setupBuild(makeMd)

        if extendedMd:
            makeMd.setGitHubMarkdown()
        else:
            makeMd.setStandardMarkdown()

        if self._build.get("process.replaceTabs", False):
            makeMd.replaceTabs(nSpaces=4, spaceChar=" ")

        for i, tHandle in enumerate(self._documents):
            yield i, self._doBuild(makeMd, tHandle)

        self._error = None
        try:
            makeMd.saveMarkdown(savePath)
        except Exception as exc:
            self._error = formatException(exc)

        return

    ##
    #  Internal Functions
    ##

    def _setupBuild(self, bldObj):
        pass

    def _doBuild(self, bldObj, tHandle):
        pass

# END Class NWBuildDocument
