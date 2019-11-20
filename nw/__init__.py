# -*- coding: utf-8 -*-
"""novelWriter Init

 novelWriter – Init File
=========================
 Application initialisation

 File History:
 Created: 2018-09-22 [0.0.1]

"""

import sys
import getopt
import logging

from os import path, remove, rename

from PyQt5.QtWidgets import QApplication

from nw.guimain import GuiMain
from nw.config import Config

__package__    = "novelWriter"
__author__     = "Veronica Berglyd Olsen"
__copyright__  = "Copyright 2018–2019, Veronica Berglyd Olsen"
__license__    = "GPLv3"
__version__    = "0.4.2"
__date__       = "2019-11-17"
__maintainer__ = "Veronica Berglyd Olsen"
__email__      = "code@vkbo.net"
__status__     = "Development"
__url__        = "https://github.com/vkbo/novelWriter"
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

# Adding verbose logging levels
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
    shortOpt = "hdiqtl:v"
    longOpt  = [
        "help",
        "debug",
        "info",
        "verbose",
        "quiet",
        "time",
        "logfile=",
        "version",
        "config=",
        "testmode",
        "style=",
    ]

    helpMsg = (
        "{appname} {version} ({status})\n"
        "{copyright}\n"
        "\n"
        "Usage:\n"
        " -h, --help      Print this message.\n"
        " -v, --version   Print program version and exit.\n"
        " -i, --info      Print additional runtime information.\n"
        " -d, --debug     Print debug output.\n"
        "     --verbose   Increase verbosity of debug output.\n"
        " -q, --quiet     Disable output to command line. Does not affect log file.\n"
        " -t, --time      Shows time stamp in logging output.\n"
        " -l, --logfile=  Specify log file.\n"
        "     --style=    Set Qt5 style flag. Defaults to 'Fusion'.\n"
        "     --config=   Alternative config file.\n"
        "     --headless  Do not display GUI. Useful for testing scripts.\n"
    ).format(
        appname   = __package__,
        version   = __version__,
        status    = __status__,
        copyright = __copyright__
    )

    # Defaults
    debugLevel = logging.WARN
    debugStr   = "{levelname:8}  {message:}"
    timeStr    = "[{asctime:}] "
    logFile    = ""
    toFile     = False
    toStd      = True
    showTime   = False
    confPath   = None
    testMode   = False
    qtStyle    = "Fusion"

    # Parse Options
    try:
        inOpts, inArgs = getopt.getopt(sysArgs,shortOpt,longOpt)
    except getopt.GetoptError:
        print(helpMsg)
        sys.exit(2)

    for inOpt, inArg in inOpts:
        if inOpt in ("-h","--help"):
            print(helpMsg)
            sys.exit()
        elif inOpt in ("-v", "--version"):
            print("%s %s Version %s" % (__package__,__status__,__version__))
            sys.exit()
        elif inOpt in ("-i", "--info"):
            debugLevel = logging.INFO
        elif inOpt in ("-d", "--debug"):
            debugLevel = logging.DEBUG
            debugStr   = "{name:>30}:{lineno:<4d}  {levelname:8}  {message:}"
        elif inOpt in ("-l","--logfile"):
            logFile = inArg
            toFile  = True
        elif inOpt in ("-q","--quiet"):
            toStd = False
        elif inOpt in ("--verbose"):
            debugLevel = VERBOSE
        elif inOpt in ("-t","--time"):
            showTime = True
        elif inOpt in ("--style"):
            qtStyle = inArg
        elif inOpt in ("--config"):
            confPath = inArg
        elif inOpt in ("--testmode"):
            testMode = True

    # Set Config Options
    CONFIG.showGUI   = not testMode
    CONFIG.debugInfo = debugLevel < logging.INFO

    # Set Logging
    if showTime: debugStr = timeStr+debugStr
    logFmt = logging.Formatter(fmt=debugStr,datefmt="%Y-%m-%d %H:%M:%S",style="{")

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

    CONFIG.initConfig(confPath)

    if testMode:
        nwGUI = GuiMain()
        return nwGUI
    else:
        nwApp = QApplication([__package__,("-style=%s" % qtStyle)])
        nwGUI = GuiMain()
        sys.exit(nwApp.exec_())

    return
