# -*- coding: utf-8 -*-
"""novelWriter Test Dummy GUI Classes
"""

# =========================================================================== #
#  Mock GUI
# =========================================================================== #

class DummyMain():

    def __init__(self):
        self.mainConf = None
        self.hasProject = True
        self.statusBar = StatusBar()
        return

    def makeAlert(self, theMessage, theLevel):
        print("%s: %s" % (str(theLevel), theMessage))
        return

    def setStatus(self, theMessage):
        return

    def setProjectStatus(self, isChanged):
        return

    def openProject(self, projPath):
        return

    def rebuildIndex(self):
        return

# END Class GuiMain

class StatusBar():

    def __init__(self):
        return

    def setStatus(self, theText):
        return

# END Class StatusBar

# =========================================================================== #
#  Error Functions
#  Dummy functions that will raise errors instead.
# =========================================================================== #

def dummyIO(*args, **kwargs):
    raise OSError
