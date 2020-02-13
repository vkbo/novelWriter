# -*- coding: utf-8 -*-
"""novelWriter Legacy Tools

 novelWriter – Legacy Tools
============================
 Various functions to handle old projects

 File History:
 Created: 2020-02-13 [0.4.3]

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

    return
