# -*- coding: utf-8 -*-
"""
novelWriter – Test Suite Dummy Classes
======================================

This file is a part of novelWriter
Copyright 2018–2021, Veronica Berglyd Olsen

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
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

    def releaseNotes(self):
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

class DummyApp:

    def __init__(self):
        return

    def installTranslator(self, theLang):
        return

# END Class DummyApp

# =========================================================================== #
#  Error Functions
#  Dummy functions that will raise errors instead.
# =========================================================================== #

def causeOSError(*args, **kwargs):
    raise OSError

def causeException(*args, **kwargs):
    raise Exception
