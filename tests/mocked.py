"""
novelWriter – Test Suite Mocked Classes
=======================================

This file is a part of novelWriter
Copyright 2018–2023, Veronica Berglyd Olsen

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

from PyQt5.QtCore import QObject


# =========================================================================== #
#  Mock GUI
# =========================================================================== #

class MockGuiMain(QObject):

    def __init__(self):
        super().__init__()

        self.hasProject = True
        self.theProject = None
        self.mainStatus = MockStatusBar()
        self.projPath = ""

        # Test Variables
        self.askResponse = True
        self.lastAlert = ""
        self.lastQuestion = ""

        return

    def postLaunchTasks(self, cmdOpen):
        return

    def makeAlert(self, text, info="", detals="", level=0, exception=None):
        assert isinstance(text, str)
        print("%s: %s" % (str(level), text))
        self.lastAlert = str(text)
        return

    def askQuestion(self, text, info="", details="", level=3):
        print("Question: %s" % text)
        self.lastQuestion = text
        return self.askResponse

    def setStatus(self, theMessage):
        return

    def openProject(self, projPath):
        self.projPath = projPath
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

# END Class MockGuiMain


class MockStatusBar:

    def __init__(self):
        return

    def setStatus(self, theText):
        return

    def doUpdateProjectStatus(self, theStatus):
        return

# END Class MockStatusBar


class MockApp:

    def __init__(self):
        return

    def installTranslator(self, theLang):
        return

# END Class MockApp


# =========================================================================== #
#  Error Functions
#  Mock functions that will raise errors instead.
# =========================================================================== #

def causeOSError(*args, **kwargs):
    raise OSError("Mock OSError")


def causeException(*args, **kwargs):
    raise Exception("Mock Exception")
