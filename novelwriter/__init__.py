"""
novelWriter – Init File
=======================

File History:
Created: 2018-09-22 [0.0.1]

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
from __future__ import annotations

import sys
import getopt
import logging

from PyQt5.QtWidgets import QApplication, QErrorMessage

from novelwriter.error import exceptionHandler, logException
from novelwriter.config import Config
from novelwriter.shared import SharedData

# Package Meta
# ============

__package__    = "novelwriter"
__copyright__  = "Copyright 2018–2023, Veronica Berglyd Olsen"
__license__    = "GPLv3"
__author__     = "Veronica Berglyd Olsen"
__maintainer__ = "Veronica Berglyd Olsen"
__email__      = "code@vkbo.net"
__version__    = "2.2-beta1"
__hexversion__ = "0x020200b1"
__date__       = "2023-11-12"
__status__     = "Stable"
__domain__     = "novelwriter.io"

logger = logging.getLogger(__name__)


##
#  Main Program
##

# Global config and data singletons
CONFIG = Config()
SHARED = SharedData()


def main(sysArgs: list | None = None):
    """Parse command line, set up logging, and launch main GUI."""
    if sysArgs is None:
        sysArgs = sys.argv[1:]

    # Valid Input Options
    shortOpt = "hv"
    longOpt = [
        "help",
        "version",
        "info",
        "debug",
        "style=",
        "config=",
        "data=",
        "testmode",
    ]

    helpMsg = (
        f"novelWriter {__version__} ({__date__})\n"
        f"{__copyright__}\n"
        "\n"
        "This program is distributed in the hope that it will be useful,\n"
        "but WITHOUT ANY WARRANTY; without even the implied warranty of\n"
        "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the\n"
        "GNU General Public Licence for more details.\n"
        "\n"
        "Usage:\n"
        " -h, --help     Print this message.\n"
        " -v, --version  Print program version and exit.\n"
        "     --info     Print additional runtime information.\n"
        "     --debug    Print debug output. Includes --info.\n"
        "     --style=   Sets Qt5 style flag. Defaults to 'Fusion'.\n"
        "     --config=  Alternative config file.\n"
        "     --data=    Alternative user data path.\n"
    )

    # Defaults
    logLevel = logging.WARN
    logFormat = "{levelname:8}  {message:}"
    confPath = None
    dataPath = None
    testMode = False
    qtStyle = "Fusion"
    cmdOpen = None

    # Parse Options
    try:
        inOpts, inRemain = getopt.getopt(sysArgs, shortOpt, longOpt)
    except getopt.GetoptError as exc:
        print(helpMsg)
        print(f"ERROR: {str(exc)}")
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
            logFormat  = "[{asctime:}]  {filename:>17}:{lineno:<4d}  {levelname:8}  {message:}"
        elif inOpt == "--style":
            qtStyle = inArg
        elif inOpt == "--config":
            confPath = inArg
        elif inOpt == "--data":
            dataPath = inArg
        elif inOpt == "--testmode":
            testMode = True

    # Setup Logging
    pkgLogger = logging.getLogger(__package__)
    pkgLogger.setLevel(logLevel)
    if len(pkgLogger.handlers) == 0:
        # Make sure we only create one logger (mostly an issue with tests)
        cHandle = logging.StreamHandler()
        cHandle.setFormatter(logging.Formatter(fmt=logFormat, style="{"))
        pkgLogger.addHandler(cHandle)

    logger.info("Starting novelWriter %s (%s) %s", __version__, __hexversion__, __date__)

    # Check Packages and Versions
    errorData = []
    errorCode = 0
    if sys.hexversion < 0x030800f0:
        errorData.append(
            "At least Python 3.8 is required, found %s" % CONFIG.verPyString
        )
        errorCode |= 0x04
    if CONFIG.verQtValue < 0x050a00:
        errorData.append(
            "At least Qt5 version 5.10 is required, found %s" % CONFIG.verQtString
        )
        errorCode |= 0x08
    if CONFIG.verPyQtValue < 0x050a00:
        errorData.append(
            "At least PyQt5 version 5.10 is required, found %s" % CONFIG.verPyQtString
        )
        errorCode |= 0x10

    if errorData:
        errApp = QApplication([])
        errDlg = QErrorMessage()
        errDlg.resize(500, 300)
        errDlg.showMessage((
            "<h3>A critical error was encountered</h3>"
            "<p>novelWriter cannot start due to the following issues:<p>"
            "<p>&nbsp;-&nbsp;%s</p>"
            "<p>Shutting down ...</p>"
        ) % (
            "<br>&nbsp;-&nbsp;".join(errorData)
        ))
        for errLine in errorData:
            logger.critical(errLine)
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
        except Exception:
            logger.error("Failed to set application name")
            logException()

    elif CONFIG.osWindows:
        try:
            import ctypes
            appID = f"io.novelwriter.{__version__}"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appID)
        except Exception:
            logger.error("Failed to set application name")
            logException()

    # Import GUI (after dependency checks), and launch
    from novelwriter.guimain import GuiMain
    if testMode:
        nwGUI = GuiMain()
        return nwGUI

    else:
        nwApp = QApplication([CONFIG.appName, (f"-style={qtStyle}")])
        nwApp.setApplicationName(CONFIG.appName)
        nwApp.setApplicationVersion(__version__)
        nwApp.setOrganizationDomain(__domain__)
        nwApp.setOrganizationName(__domain__)
        nwApp.setDesktopFileName(CONFIG.appName)

        # Connect the exception handler before making the main GUI
        sys.excepthook = exceptionHandler

        # Run Config steps that require the QApplication
        CONFIG.initLocalisation(nwApp)
        CONFIG.setTextFont(CONFIG.textFont, CONFIG.textSize)  # Makes sure these are valid

        # Launch main GUI
        nwGUI = GuiMain()
        nwGUI.postLaunchTasks(cmdOpen)

        sys.exit(nwApp.exec_())

# END Function main
