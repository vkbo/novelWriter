"""
novelWriter – Init File
=======================

File History:
Created: 2018-09-22 [0.0.1]

This file is a part of novelWriter
Copyright 2018–2024, Veronica Berglyd Olsen

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

import getopt
import logging
import sys

from typing import TYPE_CHECKING

from PyQt5.QtWidgets import QApplication, QErrorMessage

from novelwriter.config import Config
from novelwriter.error import exceptionHandler
from novelwriter.shared import SharedData

if TYPE_CHECKING:  # pragma: no cover
    from novelwriter.guimain import GuiMain

# Package Meta
# ============

__package__    = "novelwriter"
__copyright__  = "Copyright 2018–2024, Veronica Berglyd Olsen"
__license__    = "GPLv3"
__author__     = "Veronica Berglyd Olsen"
__maintainer__ = "Veronica Berglyd Olsen"
__email__      = "code@vkbo.net"
__version__    = "2.5.3"
__hexversion__ = "0x020503f0"
__date__       = "2024-11-26"
__status__     = "Stable"
__domain__     = "novelwriter.io"

logger = logging.getLogger(__name__)


##
#  Main Program
##

# Global config and data singletons
CONFIG = Config()
SHARED = SharedData()


def main(sysArgs: list | None = None) -> GuiMain | None:
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
        "meminfo"
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
        "     --meminfo  Show memory usage information in the status bar.\n"
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
            CONFIG.isDebug = True
            logLevel = logging.DEBUG
            logFormat  = "[{asctime:}]  {filename:>18}:{lineno:<4d}  {levelname:8}  {message:}"
        elif inOpt == "--style":
            qtStyle = inArg
        elif inOpt == "--config":
            confPath = inArg
        elif inOpt == "--data":
            dataPath = inArg
        elif inOpt == "--testmode":
            testMode = True
        elif inOpt == "--meminfo":
            CONFIG.memInfo = True

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
    if sys.hexversion < 0x030900f0:
        errorData.append(
            "At least Python 3.9 is required, found %s" % CONFIG.verPyString
        )
        errorCode |= 0x04
    if CONFIG.verQtValue < 0x050f00:
        errorData.append(
            "At least Qt5 version 5.15.0 is required, found %s" % CONFIG.verQtString
        )
        errorCode |= 0x08
    if CONFIG.verPyQtValue < 0x050f00:
        errorData.append(
            "At least PyQt5 version 5.15.0 is required, found %s" % CONFIG.verPyQtString
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
        errApp.exec()
        sys.exit(errorCode)

    # Finish initialising config
    CONFIG.initConfig(confPath, dataPath)

    if sys.platform == "darwin":
        try:
            from Foundation import NSBundle  # type: ignore
            bundle = NSBundle.mainBundle()
            info = bundle.localizedInfoDictionary() or bundle.infoDictionary()
            info["CFBundleName"] = "novelWriter"
        except Exception:
            pass  # Quietly ignore error
    elif sys.platform == "win32":
        try:
            import ctypes
            appID = f"io.novelwriter.{__version__}"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appID)  # type: ignore
        except Exception:
            pass  # Quietly ignore error

    # Import GUI (after dependency checks), and launch
    from novelwriter.guimain import GuiMain

    if testMode:
        # Only used for testing where the test framework creates the app
        CONFIG.loadConfig()
        return GuiMain()

    app = QApplication([CONFIG.appName, (f"-style={qtStyle}")])
    app.setApplicationName(CONFIG.appName)
    app.setApplicationVersion(__version__)
    app.setOrganizationDomain(__domain__)
    app.setOrganizationName(__domain__)
    app.setDesktopFileName(CONFIG.appName)

    # Connect the exception handler before making the main GUI
    sys.excepthook = exceptionHandler

    # Run Config steps that require the QApplication
    CONFIG.loadConfig()
    CONFIG.initLocalisation(app)

    # Launch main GUI
    nwGUI = GuiMain()
    nwGUI.postLaunchTasks(cmdOpen)

    sys.exit(app.exec())
