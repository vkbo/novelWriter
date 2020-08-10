# -*- coding: utf-8 -*-
"""novelWriter Test Dummy GUI Classes
"""

from nw.constants import nwAlert

class DummyMain():

    def __init__(self):
        self.mainConf = None
        self.statusBar = StatusBar()
        return

    def makeAlert(self, theMessage, theLevel):
        if theLevel == nwAlert.WARN:
            lvlMsg = "WARNING: "
        elif theLevel == nwAlert.ERROR:
            lvlMsg = "ERROR: "
        elif theLevel == nwAlert.BUG:
            lvlMsg = "BUG: "
        else:
            lvlMsg = ""
        if isinstance(theMessage, list):
            for msgLine in logMsg:
                print(lvlMsg+msgLine)
        else:
            print(lvlMsg+theMessage)
        return

    def setStatus(self, theMessage):
        return

    def setProjectStatus(self, isChanged):
        return

# END Class GuiMain

class StatusBar():

    def __init__(self):
        return

    def setStatus(self, theText):
        return

# END Class StatusBar
