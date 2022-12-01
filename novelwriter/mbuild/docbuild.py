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

logger = logging.getLogger(__name__)


class NWBuildDocument:

    def __init__(self, project):

        self._project = project
        self._build = {}
        self._documents = []

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

    def buildOpenDocument(self, fileName, isFlat):
        pass

    def buildHTML(self, fileName):
        pass

    def buildMarkdown(self, fileName, mdFlavour):
        pass

    ##
    #  Internal Functions
    ##

    def _setupBuild(self, bldObj):
        pass

    def _doBuild(self, tHandle):
        pass

# END Class NWBuildDocument
