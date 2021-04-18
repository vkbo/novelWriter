# -*- coding: utf-8 -*-
"""
novelWriter – Init File
=======================
Application initialisation

File History:
Created: 2018-09-22 [0.0.1]

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

import sys
import getopt
import logging

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QErrorMessage

from nw.error import exceptionHandler, logException
from nw.config import Config

##
#  Version Scheme
# ================
#  Generally follows PEP 440
#  Hex Version:
#  - Digit 1,2 : Major Version (01-ff)
#  = Digit 3,4 : Minor Version (01-ff)
#  - Digit 5,6 : Patch Version (01-ff)
#  = Digit 7   : Release Type (a: aplha, b: beta, c: candidate, f: final)
#  - Digit 8   : Release Number (0-f)
#
#  Example    : Full        Short      Description
# -------------------------------------------------------------------------
#  0x010200a0 : 1.2-alpha0  1.2a0      Can be used for the dev branch
#  0x010200a1 : 1.2-alpha1  1.2a1      First alpha release
#  0x010200b1 : 1.2-beta1   1.2b1      First beta release
#  0x010200c1 : 1.2-rc1     1.2rc1     First release candidate
#  0x010200f0 : 1.2         1.2        Final release
#  0x010200f1 : 1.2-post1   1.2.post1  Post release, but not a code patch!
#  0x010201f0 : 1.2.1       1.2.1      Patch release
##

__package__    = "nw"
__copyright__  = "Copyright 2018–2021, Veronica Berglyd Olsen"
__license__    = "GPLv3"
__author__     = "Veronica Berglyd Olsen"
__maintainer__ = "Veronica Berglyd Olsen"
__email__      = "code@vkbo.net"
__version__    = "1.2.3"
__hexversion__ = "0x010203f0"
__date__       = "2021-04-18"
__status__     = "Stable"
__domain__     = "novelwriter.io"
__url__        = "https://novelwriter.io"
__sourceurl__  = "https://github.com/vkbo/novelWriter"
__issuesurl__  = "https://github.com/vkbo/novelWriter/issues"
__helpurl__    = "https://github.com/vkbo/novelWriter/discussions"
__releaseurl__ = "https://github.com/vkbo/novelWriter/releases/latest"
__docurl__     = "https://novelwriter.readthedocs.io"
__credits__    = [
    "Veronica Berglyd Olsen (developer)",
    "Marian Lückhof (contributor, tester)"
]

##
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
##

# Add verbose logging level
VERBOSE = 5
logging.addLevelName(VERBOSE, "VERBOSE")
def logVerbose(self, message, *args, **kws):
    if self.isEnabledFor(VERBOSE):
        self._log(VERBOSE, message, args, **kws)

logging.Logger.verbose = logVerbose

# Initiating logging
logger = logging.getLogger(__name__)

##
#  Main Program
##

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
        "novelWriter {version} ({date})\n"
        "{copyright}\n"
        "\n"
        "This program is distributed in the hope that it will be useful,\n"
        "but WITHOUT ANY WARRANTY; without even the implied warranty of\n"
        "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the\n"
        "GNU General Public License for more details.\n"
        "\n"
        "Usage:\n"
        " -h, --help     Print this message.\n"
        " -v, --version  Print program version and exit.\n"
        "     --info     Print additional runtime information.\n"
        "     --debug    Print debug output. Includes --info.\n"
        "     --verbose  Increase verbosity of debug output. Includes --debug.\n"
        "     --style=   Sets Qt5 style flag. Defaults to 'Fusion'.\n"
        "     --config=  Alternative config file.\n"
        "     --data=    Alternative user data path.\n"
    ).format(
        version   = __version__,
        copyright = __copyright__,
        date      = __date__,
    )

    # Defaults
    logLevel  = logging.WARN
    logFormat = "{levelname:8}  {message:}"
    confPath  = None
    dataPath  = None
    testMode  = False
    qtStyle   = "Fusion"
    cmdOpen   = None

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
            print("novelWriter Version %s [%s]" % (__version__, __date__))
            sys.exit(0)
        elif inOpt == "--info":
            logLevel = logging.INFO
        elif inOpt == "--debug":
            logLevel = logging.DEBUG
            logFormat  = "[{asctime:}] {name:>22}:{lineno:<4d}  {levelname:8}  {message:}"
        elif inOpt == "--verbose":
            logLevel = VERBOSE
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
    CONFIG.cmdOpen = cmdOpen

    # Set Logging
    cHandle = logging.StreamHandler()
    cHandle.setFormatter(logging.Formatter(fmt=logFormat, style="{"))

    pkgLogger = logging.getLogger(__package__)
    pkgLogger.addHandler(cHandle)
    pkgLogger.setLevel(logLevel)

    logger.info("Starting novelWriter %s (%s) %s" % (
        __version__, __hexversion__, __date__
    ))

    # Check Packages and Versions
    errorData = []
    errorCode = 0
    if sys.hexversion < 0x030600f0:
        errorData.append(
            "At least Python 3.6.0 is required, found %s." % CONFIG.verPyString
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
        for errMsg in errorData:
            logger.critical(errMsg)
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
        except ImportError:
            logger.error("Failed to set application name")
            logException()

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

        # Launch main GUI
        nwGUI = GuiMain()
        if not nwGUI.hasProject:
            nwGUI.showProjectLoadDialog()
        nwGUI.releaseNotes()

        sys.exit(nwApp.exec_())

# END Function main
