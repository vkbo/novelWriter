# -*- coding: utf-8 -*-
"""novelWriter Project Index

 novelWriter – Project Index
=============================
 Class holding the index of tags

 File History:
 Created: 2019-05-27 [0.1.4]

"""

import logging
import nw

logger = logging.getLogger(__name__)

class NWIndex():

    def __init__(self, theParent):

        # Internal
        self.theParent = theParent
        self.mainConf  = self.theParent.mainConf

        return

# END Class NWIndex
