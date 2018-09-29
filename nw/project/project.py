# -*- coding: utf-8 -*
"""novelWriter Project Wrapper

 novelWriter – Project Wrapper
===============================
 Class holding a project

 File History:
 Created: 2018-09-29 [0.1.0]

"""

import logging
import nw

from os import path

logger = logging.getLogger(__name__)

class NWProject():

    def __init__(self):

        self.projFolder = None
        self.projTree   = []

        return

    def buildProjectTree(self):

        return True

# END Class NWProject
