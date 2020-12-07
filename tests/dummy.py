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
        self.theIndex = None
        self.theProject = None
        self.statusBar = DummyStatusBar()

        # Test Variables
        self.askResponse = True
        self.lastAlert = ""

        return

    def makeAlert(self, theMessage, theLevel):
        print("%s: %s" % (str(theLevel), theMessage))
        self.lastAlert = str(theMessage)
        return

    def askQuestion(self, theTitle, theQustion):
        print("Question: %s" % theQustion)
        return self.askResponse

    def setStatus(self, theMessage):
        return

    def setProjectStatus(self, isChanged):
        return

    def openProject(self, projPath):
        return

    def rebuildIndex(self):
        return

    def closeMain(self):
        return "closeMain"

    def close(self):
        return "close"

    # Test Functions

    def undo(self):
        self.askResponse = True
        return

    def clear(self):
        self.lastAlert = ""
        return

# END Class DummyMain

class DummyStatusBar():

    def __init__(self):
        return

    def setStatus(self, theText):
        return

# END Class DummyStatusBar

# =========================================================================== #
#  Error Functions
#  Dummy functions that will raise errors instead.
# =========================================================================== #

def causeOSError(*args, **kwargs):
    raise OSError

def causeException(*args, **kwargs):
    raise Exception
