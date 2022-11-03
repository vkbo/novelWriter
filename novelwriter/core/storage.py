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

from pathlib import Path

from novelwriter.constants import nwFiles
from novelwriter.core.projectxml import ProjectXMLReader, ProjectXMLWriter

logger = logging.getLogger(__name__)


class NWStorage:

    MODE_INACTIVE = 0
    MODE_INPLACE  = 1
    MODE_ARCHIVE  = 2

    def __init__(self, theProject):

        self.theProject = theProject

        self._storagePath = None
        self._runtimePath = None
        self._openMode = self.MODE_INACTIVE

        return

    def clear(self):
        """Reset internal variables.
        """
        self._storagePath = None
        self._runtimePath = None
        self._openMode = self.MODE_INACTIVE
        return

    ##
    #  Core Methods
    ##

    def isOpen(self):
        """Check if the storage location is open.
        """
        return self._runtimePath is not None

    def openProjectInPlace(self, path):
        """Open a novelWriter project in-place. That is, it is opened
        directly from a project folder.
        """
        inPath = Path(path)
        if inPath.is_file():
            inPath = inPath.parent

        if not inPath.is_dir():
            logger.error("No such folder: %s", inPath)
            self.clear()
            return False

        self._storagePath = inPath
        self._runtimePath = inPath
        self._openMode = self.MODE_INPLACE

        return True

    def openProjectArchive(self, path):
        pass

    def runPostSaveTasks(self, autoSave=False):
        """Run tasks after the project has been saved.
        """
        if self._openMode == self.MODE_INPLACE:
            # Nothing to do, so we just return
            return True

        return True

    def closeSession(self):
        """Run tasks related to closing the session.
        """
        # Clear lockfile
        self.clear()
        return

    ##
    #  Content Access Methods
    ##

    def getXmlReader(self):
        """
        """
        if self._runtimePath is None:
            return None

        projFile = self._runtimePath / nwFiles.PROJ_FILE
        xmlReader = ProjectXMLReader(projFile)

        return xmlReader

    def getXmlWriter(self):
        """
        """
        if self._runtimePath is None:
            return None

        xmlWriter = ProjectXMLWriter(self._runtimePath)

        return xmlWriter

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
