# -*- coding: utf-8 -*-
"""novelWriter Init

 novelWriter – Init File
=========================
 Application initialisation

 File History:
 Created: 2018-09-22 [0.0.1]

 This file is a part of novelWriter
 Copyright 2020, Veronica Berglyd Olsen

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

import sys
import getopt
import logging

from os import path, remove, rename

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QErrorMessage

from nw.config import Config

__package__    = "novelWriter"
__author__     = "Veronica Berglyd Olsen"
__copyright__  = "Copyright 2018–2020, Veronica Berglyd Olsen"
__license__    = "GPLv3"
__version__    = "0.7.0"
__hexversion__ = "0x000700f0"
__date__       = "2020-06-01"
__maintainer__ = "Veronica Berglyd Olsen"
__email__      = "code@vkbo.net"
__status__     = "Pre-Release"
__url__        = "https://github.com/vkbo/novelWriter"
__domain__     = "novelwriter.io"
__docurl__     = "https://novelwriter.readthedocs.io"
__credits__    = [
    "Veronica Berglyd Olsen (developer)",
    "Marian Lückhof (contributor, tester)"
]

#
#  Logging
# =========
#  Standard used for logging levels in novelWriter:
#    CRITICAL  Use for errors that result in termination of the program
#    ERROR     Use when an action fails, but execution continues
#    WARNING   When something unexpected, but non-critical happens
#    INFO      Any useful user information like open, save, exit initiated
#  ----------- SPAM Threshold : Output above should be minimal -----------------
#    DEBUG     Use for descriptions of main program flow
#    VERBOSE   Use for outputting values and program flow details
#

# Add verbose logging level
VERBOSE = 5
logging.addLevelName(VERBOSE, "VERBOSE")
def logVerbose(self, message, *args, **kws):
    if self.isEnabledFor(VERBOSE):
        self._log(VERBOSE, message, args, **kws)
logging.Logger.verbose = logVerbose

# Initiating logging
logger = logging.getLogger(__name__)

#
#  Main Program
# ==============
#

# Load the main config as a global object
CONFIG = Config()

def main(sysArgs=None):
    """Parses command line, sets up logging, and launches main GUI.
    """

    if sysArgs is None:
        sysArgs = sys.argv[1:]

    # Valid Input Options
    shortOpt = "hvq"
    longOpt  = [
        "help",
        "version",
        "info",
        "debug",
        "verbose",
        "quiet",
        "logfile=",
        "style=",
        "config=",
        "data=",
        "testmode",
    ]

    helpMsg = (
        "{appname} {version} ({status} {date})\n"
        "{copyright}\n"
        "\n"
        "This program is distributed in the hope that it will be useful,\n"
        "but WITHOUT ANY WARRANTY; without even the implied warranty of\n"
        "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the\n"
        "GNU General Public License for more details.\n"
        "\n"
        "Usage:\n"
        " -h, --help      Print this message.\n"
        " -v, --version   Print program version and exit.\n"
        "     --info      Print additional runtime information.\n"
        "     --debug     Print debug output. Includes --info.\n"
        "     --verbose   Increase verbosity of debug output. Includes --debug.\n"
        " -q, --quiet     Disable output to command line. Does not affect log file.\n"
        "     --logfile=  Specify log file.\n"
        "     --style=    Sets Qt5 style flag. Defaults to 'Fusion'.\n"
        "     --config=   Alternative config file.\n"
        "     --data=     Alternative user data path.\n"
        "     --testmode  Do not display GUI. Used by the test suite.\n"
    ).format(
        appname   = __package__,
        version   = __version__,
        status    = __status__,
        copyright = __copyright__,
        date      = __date__,
    )

    # Defaults
    debugLevel = logging.WARN
    logFormat  = "{levelname:8}  {message:}"
    logFile    = ""
    toFile     = False
    toStd      = True
    confPath   = None
    dataPath   = None
    testMode   = False
    qtStyle    = "Fusion"
    cmdOpen    = None

    # Parse Options
    try:
        inOpts, inRemain = getopt.getopt(sysArgs,shortOpt,longOpt)
    except getopt.GetoptError as E:
        print(helpMsg)
        print("ERROR: %s" % str(E))
        sys.exit(2)

    if len(inRemain) > 0:
        cmdOpen = inRemain[0]

    for inOpt, inArg in inOpts:
        if inOpt in ("-h","--help"):
            print(helpMsg)
            sys.exit()
        elif inOpt in ("-v", "--version"):
            print("%s %s Version %s [%s]" % (__package__,__status__,__version__,__date__))
            sys.exit()
        elif inOpt == "--info":
            debugLevel = logging.INFO
        elif inOpt == "--debug":
            debugLevel = logging.DEBUG
            logFormat  = "[{asctime:}] {name:>30}:{lineno:<4d}  {levelname:8}  {message:}"
        elif inOpt == "--logfile":
            logFile = inArg
            toFile  = True
        elif inOpt in ("-q","--quiet"):
            toStd = False
        elif inOpt == "--verbose":
            debugLevel = VERBOSE
            logFormat  = "[{asctime:}] {name:>30}:{lineno:<4d}  {levelname:8}  {message:}"
        elif inOpt == "--style":
            qtStyle = inArg
        elif inOpt == "--config":
            confPath = inArg
        elif inOpt == "--data":
            dataPath = inArg
        elif inOpt == "--testmode":
            testMode = True

    # Set Config Options
    CONFIG.showGUI   = not testMode
    CONFIG.debugInfo = debugLevel < logging.INFO
    CONFIG.cmdOpen   = cmdOpen

    # Set Logging
    logFmt = logging.Formatter(fmt=logFormat,datefmt="%Y-%m-%d %H:%M:%S",style="{")

    if not logFile == "" and toFile:
        if path.isfile(logFile+".bak"):
            remove(logFile+".bak")
        if path.isfile(logFile):
            rename(logFile,logFile+".bak")

        fHandle = logging.FileHandler(logFile)
        fHandle.setLevel(debugLevel)
        fHandle.setFormatter(logFmt)
        logger.addHandler(fHandle)

    if toStd:
        cHandle = logging.StreamHandler()
        cHandle.setLevel(debugLevel)
        cHandle.setFormatter(logFmt)
        logger.addHandler(cHandle)

    logger.setLevel(debugLevel)

    # Check Packages and Versions
    errorData = []
    if sys.hexversion < 0x030403F0:
        errorData.append(
            "At least Python 3.4.3 is required, but 3.6 is highly recommended."
        )
    if CONFIG.verQtValue < 50200:
        errorData.append(
            "At least Qt5 version 5.2 is required, found %s." % CONFIG.verQtString
        )
    if CONFIG.verPyQtValue < 50200:
        errorData.append(
            "At least PyQt5 version 5.2 is required, found %s." % CONFIG.verPyQtString
        )
    try:
        import PyQt5.QtSvg
    except:
        errorData.append("Python module 'PyQt5.QtSvg' is missing.")
    try:
        import lxml
    except:
        errorData.append("Python module 'lxml' is missing.")

    if errorData:
        errApp = QApplication([])
        errMsg = QErrorMessage()
        errMsg.setMinimumWidth(500)
        errMsg.setMinimumHeight(300)
        errMsg.showMessage((
            "ERROR: %s cannot start due to the following issues:<br><br>"
            "&nbsp;-&nbsp;%s<br><br>Exiting."
        ) % (
            __package__, "<br>&nbsp;-&nbsp;".join(errorData)
        ))
        errApp.exec_()
        sys.exit(1)

    # Finish initialising config
    CONFIG.initConfig(confPath, dataPath)

    # Import GUI (after dependency checks), and launch
    from nw.guimain import GuiMain
    if testMode:
        nwGUI = GuiMain()
        return nwGUI
    else:
        nwApp = QApplication([__package__,("-style=%s" % qtStyle)])
        nwApp.setApplicationName(__package__)
        nwApp.setApplicationVersion(__version__)
        nwApp.setWindowIcon(QIcon(CONFIG.appIcon))
        nwApp.setOrganizationDomain("novelwriter.io")
        nwGUI = GuiMain()
        sys.exit(nwApp.exec_())

    return
