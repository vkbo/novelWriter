# -*- coding: utf-8 -*-
"""novelWriter Project Backup

 novelWriter – Project Backup
==============================
 Class handling project backups

 File History:
 Created: 2019-06-16 [0.1.5]

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

        if self.mainConf.backupPath is None:
            self.theParent.makeAlert(
                "Cannot backup project because no backup path is set.",nwAlert.WARN
            )
            return False

        if self.theProject.projName is None:
            self.theParent.makeAlert(
                "Cannot backup project because no project name is set.",nwAlert.WARN
            )
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
            make_archive(baseName, "zip", self.theProject.projPath, ".")
        except Exception as e:
            self.theParent.makeAlert(
                ["Could not write backup archive.",str(e)],
                nwAlert.ERROR
            )
            return False

        self.theParent.statusBar.setStatus("Project backup complete")

        return True

# END Class NWBackup
