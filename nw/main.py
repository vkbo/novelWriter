# -*- coding: utf-8 -*
"""novelWriter Main Class

 novelWriter – Main Class
==========================
 Sets up the main GUI and holds action and event functions

 File History:
 Created: 2018-09-22 [0.1.0]

"""

import logging
import nw

from nw.gui.winmain import GuiMain

logger = logging.getLogger(__name__)

class NovelWriter():

    def __init__(self):
        super().__init__()

        self.winMain = GuiMain()

        return
# END Class NovelWriter
