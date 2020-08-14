# -*- coding: utf-8 -*-
"""novelWriter Test Dummy GUI Classes
"""

class DummyMain():

    def __init__(self):
        self.mainConf = None
        self.statusBar = StatusBar()
        return

    def makeAlert(self, theMessage, theLevel):
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
