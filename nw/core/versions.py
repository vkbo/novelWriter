# -*- coding: utf-8 -*-
"""
novelWriter – Versions Class
============================
Data class for tracking file versions

File History:
Created: 2021-04-23 [1.4a0]

This file is a part of novelWriter
Copyright 2018–2021, Veronica Berglyd Olsen

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

import nw
import os
import shutil
import logging

from nw.common import isHandle, safeUnlink, safeFileRead, safeMakeDir

logger = logging.getLogger(__name__)

class NWVersions():

    def __init__(self, theProject):

        self.theProject = theProject

        # Internals
        self._docHandle   = None
        self._docLocation = None
        self._versionPath = None
        self._docVersions = []

        return

    def clearVersions(self):
        """Clear the versions object.
        """
        self._docHandle   = None
        self._docLocation = None
        self._versionPath = None
        self._docVersions = []
        return

    ##
    #  Methods
    ##

    def setDocument(self, docHandle):
        """Set which document to extract version information from.
        """
        self.clearVersions()

        if not isHandle(docHandle):
            logger.warning("Not a handle: %s" % docHandle)
            return False

        if self.theProject.projVers is None:
            logger.error("Versions path is not set")
            return False

        if not os.path.isdir(self.theProject.projVers):
            logger.error("Versions path does not exist: %s" % self.theProject.projVers)
            return False

        self._docHandle = docHandle
        self._docLocation = os.path.join(self.theProject.projContent, self._docHandle+".nwd")
        self._versionPath = os.path.join(self.theProject.projVers, docHandle)

        if not os.path.isdir(self._versionPath):
            logger.verbose("No previous version information exists for %s" % docHandle)
            return True

        return True

    def saveSessionVersion(self):
        """Save a backup copy of the current document from the previous
        session. This is called before a document is edited.
        """
        if self._versionPath is None:
            return False

        if not safeMakeDir(self._versionPath):
            return False

        sessID = "ID:" + self.theProject.sessionID
        prevID = "ID:None"

        dataFile = os.path.join(self._versionPath, "session.dat")
        if os.path.isfile(dataFile):
            prevID = safeFileRead(dataFile, prevID)

        sessFile = os.path.join(self._versionPath, self._docHandle+"_session.nwd")
        if os.path.isfile(sessFile):
            logger.verbose("Session file stamps: %s vs %s" % (sessID, prevID))
            if sessID == prevID:
                logger.debug("Session file already saved")
                return True
            else:
                logger.debug("Deleting old session file")
                safeUnlink(sessFile)

        if os.path.isfile(self._docLocation):
            try:
                shutil.copy2(self._docLocation, sessFile)
                with open(dataFile, mode="w", encoding="utf8") as outFile:
                    outFile.write(sessID)
                logger.debug("Session version of %s created" % self._docHandle)

            except Exception:
                logger.error("Failed to save session version file")
                nw.logException()
                return False

        return True

# END Class NWVersions
