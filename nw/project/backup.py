# -*- coding: utf-8 -*-
"""novelWriter Project Backup

 novelWriter – Project Backup
==============================
 Class handling project backups

 File History:
 Created: 2019-06-16 [0.1.5]

 This file is a part of novelWriter
 Copyright 2020, Veronica Berglyd Olsen

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
import nw

from os import path
from shutil import make_archive
from datetime import datetime

from nw.constants import nwAlert

logger = logging.getLogger(__name__)

class NWBackup():

    def __init__(self, theParent, theProject):
        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theProject = theProject
        return

    def zipIt(self):

        if self.mainConf.backupPath is None or self.mainConf.backupPath == "":
            self.theParent.makeAlert((
                "Cannot backup project because no backup path is set. "
                "Please set a valid backup location in Tools > Preferences."
            ), nwAlert.WARN)
            return False

        if self.theProject.projName is None or self.theProject.projName == "":
            self.theParent.makeAlert((
                "Cannot backup project because no project name is set. "
                "Please set a Working Title in Project > Project Settings."
            ), nwAlert.WARN)
            return False

        if not path.isdir(self.mainConf.backupPath):
            self.theParent.makeAlert((
                "Cannot backup project because the backup path does not exist. "
                "Please set a valid backup location in Tools > Preferences."
            ), nwAlert.WARN)
            return False

        logger.info("Backing up project")
        self.theParent.statusBar.setStatus("Backing up project ...")

        archName = ""
        for c in self.theProject.projName:
            if c.isalnum():
                archName += c
            else:
                archName += "_"

        archName = archName+"_"+datetime.now().strftime("%Y%m%d-%H%M%S")
        baseName = path.join(self.mainConf.backupPath, archName)

        try:
            self.theProject._clearLockFile()
            make_archive(baseName, "zip", self.theProject.projPath, ".")
            self.theProject._writeLockFile()
            logger.info("Backup written to: %s" % archName)
        except Exception as e:
            self.theParent.makeAlert(
                ["Could not write backup archive.",str(e)],
                nwAlert.ERROR
            )
            return False

        self.theParent.statusBar.setStatus("Project backup complete")

        return True

# END Class NWBackup
