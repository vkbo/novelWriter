# -*- coding: utf-8 -*-
"""novelWriter Init

 novelWriter – Init File
=========================
 Application initialisation

 File History:
 Created: 2018-09-22 [0.0.1]

 This file is a part of novelWriter
 Copyright 2018–2020, Veronica Berglyd Olsen

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

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QErrorMessage

from nw.error import exceptionHandler
from nw.config import Config

__package__    = "nw"
__author__     = "Veronica Berglyd Olsen"
__copyright__  = "Copyright 2018–2020, Veronica Berglyd Olsen"
__license__    = "GPLv3"
__version__    = "1.0b4"
__hexversion__ = "0x010000b4"
__date__       = "2020-10-11"
__maintainer__ = "Veronica Berglyd Olsen"
__email__      = "code@vkbo.net"
__status__     = "Beta"
__url__        = "https://novelwriter.io"
__sourceurl__  = "https://github.com/vkbo/novelWriter"
__issuesurl__  = "https://github.com/vkbo/novelWriter/issues"
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
    shortOpt = "hv"
    longOpt  = [
        "help",
        "version",
        "info",
        "debug",
        "verbose",
        "style=",
        "config=",
        "data=",
        "testmode",
    ]

    helpMsg = (
        "novelWriter {version} ({status} {date})\n"
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
        "     --style=    Sets Qt5 style flag. Defaults to 'Fusion'.\n"
        "     --config=   Alternative config file.\n"
        "     --data=     Alternative user data path.\n"
        "     --testmode  Do not display GUI. Used by the test suite.\n"
    ).format(
        version   = __version__,
        status    = __status__,
        copyright = __copyright__,
        date      = __date__,
    )

    # Defaults
    debugLevel = logging.WARN
    logFormat  = "{levelname:8}  {message:}"
    confPath   = None
    dataPath   = None
    testMode   = False
    qtStyle    = "Fusion"
    cmdOpen    = None

    # Parse Options
    try:
        inOpts, inRemain = getopt.getopt(sysArgs, shortOpt, longOpt)
    except getopt.GetoptError as E:
        print(helpMsg)
        print("ERROR: %s" % str(E))
        sys.exit(2)

    if len(inRemain) > 0:
        cmdOpen = inRemain[0]

    for inOpt, inArg in inOpts:
        if inOpt in ("-h", "--help"):
            print(helpMsg)
            sys.exit(0)
        elif inOpt in ("-v", "--version"):
            print("novelWriter %s Version %s [%s]" % (
                __status__, __version__, __date__)
            )
            sys.exit(0)
        elif inOpt == "--info":
            debugLevel = logging.INFO
        elif inOpt == "--debug":
            debugLevel = logging.DEBUG
            logFormat  = "[{asctime:}] {name:>22}:{lineno:<4d}  {levelname:8}  {message:}"
        elif inOpt == "--verbose":
            debugLevel = VERBOSE
            logFormat  = "[{asctime:}] {name:>22}:{lineno:<4d}  {levelname:8}  {message:}"
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
    logFmt = logging.Formatter(fmt=logFormat, style="{")
    cHandle = logging.StreamHandler()
    cHandle.setLevel(debugLevel)
    cHandle.setFormatter(logFmt)
    logger.addHandler(cHandle)

    logger.setLevel(debugLevel)
    logger.info("Starting novelWriter %s (%s) %s" % (
        __version__, __hexversion__, __date__
    ))

    # Check Packages and Versions
    errorData = []
    errorCode = 0
    if sys.hexversion < 0x030403f0:
        errorData.append(
            "At least Python 3.4.3 is required, but 3.6 is highly recommended."
        )
        errorCode |= 4
    if CONFIG.verQtValue < 50200:
        errorData.append(
            "At least Qt5 version 5.2 is required, found %s." % CONFIG.verQtString
        )
        errorCode |= 8
    if CONFIG.verPyQtValue < 50200:
        errorData.append(
            "At least PyQt5 version 5.2 is required, found %s." % CONFIG.verPyQtString
        )
        errorCode |= 16

    try:
        import lxml # noqa: F401
    except ImportError:
        errorData.append("Python module 'lxml' is missing.")
        errorCode |= 32

    if errorData:
        if not testMode:
            errApp = QApplication([])
            errMsg = QErrorMessage()
            errMsg.resize(500, 300)
            errMsg.showMessage((
                "<h3>A critical error has been encountered</h3>"
                "<p>novelWriter cannot start due to the following issues:<p>"
                "<p>&nbsp;-&nbsp;%s</p>"
                "<p>Shutting down ...</p>"
            ) % (
                "<br>&nbsp;-&nbsp;".join(errorData)
            ))
            errApp.exec_()
        sys.exit(errorCode)

    # Finish initialising config
    CONFIG.initConfig(confPath, dataPath)

    if CONFIG.osDarwin:
        try:
            from Foundation import NSBundle
            bundle = NSBundle.mainBundle()
            info = bundle.localizedInfoDictionary() or bundle.infoDictionary()
            info["CFBundleName"] = "novelWriter"
        except ImportError as e:
            logger.error("Failed to set application name")
            logger.error(str(e))

    # Import GUI (after dependency checks), and launch
    from nw.guimain import GuiMain
    if testMode:
        nwGUI = GuiMain()
        return nwGUI

    else:
        nwApp = QApplication([CONFIG.appName, ("-style=%s" % qtStyle)])
        nwApp.setApplicationName(CONFIG.appName)
        nwApp.setApplicationVersion(__version__)
        nwApp.setWindowIcon(QIcon(CONFIG.appIcon))
        nwApp.setOrganizationDomain(__domain__)

        # Connect the exception handler before making the main GUI
        sys.excepthook = exceptionHandler

        nwGUI = GuiMain()
        sys.exit(nwApp.exec_())

    return
