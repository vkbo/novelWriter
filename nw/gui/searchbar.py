# -*- coding: utf-8 -*-
"""novelWriter GUI Main Window SearchBar

 novelWriter – GUI Main Window SearchBar
=========================================
 Class holding the main window search bar

 File History:
 Created: 2019-09-29 [0.2.1]

"""

import logging
import nw

from PyQt5.QtWidgets import QFrame

logger = logging.getLogger(__name__)

class GuiSearchBar(QFrame):

    def __init__(self, theParent):

        logger.debug("Initialising GuiSearchBar ...")

        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.refTime    = None

        logger.debug("GuiSearchBar initialisation complete")

        return

# END Class GuiSearchBar
