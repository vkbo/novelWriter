# -*- coding: utf-8 -*-
"""novelWriter Legacy Tools

 novelWriter – Legacy Tools
============================
 Various functions to handle old projects

 File History:
 Created: 2020-02-13 [0.4.3]

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
 along with this program. If not, see https://www.gnu.org/licenses/.
"""

import logging
import nw

from os import path, unlink, rmdir

logger = logging.getLogger(__name__)

def projectMaintenance(theProject):
    """Wrapper class for handling various tasks related to managing old
    projects with content from older versions of novelWriter.
    """

    # Remove no longer used project cache folder
    if path.isdir(theProject.projPath):
        cacheDir = path.join(theProject.projPath, "cache")
        if path.isdir(cacheDir):
            logger.info("Deprecated cache folder found")
            rmList = []
            for i in range(10):
                rmList.append(path.join(cacheDir, "nwProject.nwx.%d" % i))
            rmList.append(path.join(cacheDir, "projCount.txt"))
            for rmFile in rmList:
                if path.isfile(rmFile):
                    logger.info("Deleting: %s" % rmFile)
                    try:
                        unlink(rmFile)
                    except Exception as e:
                        logger.error(str(e))
            logger.info("Deleting: %s" % cacheDir)
            try:
                rmdir(cacheDir)
            except Exception as e:
                logger.error(str(e))

    # Remove no longer used meta files
    rmList = []
    rmList.append(path.join(theProject.projMeta, "mainOptions.json"))
    rmList.append(path.join(theProject.projMeta, "exportOptions.json"))
    rmList.append(path.join(theProject.projMeta, "outlineOptions.json"))
    rmList.append(path.join(theProject.projMeta, "timelineOptions.json"))
    rmList.append(path.join(theProject.projMeta, "docMergeOptions.json"))
    rmList.append(path.join(theProject.projMeta, "sessionLogOptions.json"))
    for rmFile in rmList:
        if path.isfile(rmFile):
            logger.info("Deleting: %s" % rmFile)
            try:
                unlink(rmFile)
            except Exception as e:
                logger.error(str(e))

    return
