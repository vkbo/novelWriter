# -*- coding: utf-8 -*-
"""novelWriter Test Dummy GUI Classes
"""

class DummyMain():

    def __init__(self):
        self.mainConf = None
        return

    def makeAlert(self, theMessage, theLevel):
        if theLevel == 1:
            lvlMsg = "WARNING: "
        elif theLevel == 2:
            lvlMsg = "ERROR: "
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
