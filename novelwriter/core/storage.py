"""
novelWriter – Project Storage Class
===================================
The main class handling the project storage

File History:
Created: 2022-11-01 [2.0rc1] NWStorage

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


class NWStorage:

    def __init__(self, theProject):
        self.theProject = theProject
        return

    ##
    #  Core Methods
    ##

    def openProjectFolder(self, path):
        pass

    def openProjectArchive(self, path):
        pass

    def close(self):
        pass

    ##
    #  Content Access Methods
    ##

    def getXmlReader(self):
        pass

    def getXmlWriter(self):
        pass

    def getDocument(self, tHandle):
        pass

    def getMetaFile(self, kind):
        pass

    ##
    #  Internal Functions
    ##

    def _zipIt(self, target):
        pass

    def _reeadLockFile(self):
        pass

    def _writeLockFile(self):
        pass

# END Class NWStorage
