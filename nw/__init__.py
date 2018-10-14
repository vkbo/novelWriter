# -*- coding: utf-8 -*
"""novelWriter Init

 novelWriter – Init File
=========================
 Application initialisation

 File History:
 Created: 2018-09-22 [0.1.0]

"""

import logging
import getopt
import gi

gi.require_version("Gtk","3.0")

from os              import path, remove, rename
from PyQt5.QtWidgets import QApplication
from nw.main         import NovelWriter
from nw.config       import Config

__package__    = "novelWriter"
__author__     = "Veronica Berglyd Olsen"
__copyright__  = "Copyright 2016-2018, Veronica Berglyd Olsen"
__credits__    = ["Veronica Berglyd Olsen"]
__license__    = "GPLv3"
__version__    = "0.1.0"
__date__       = "2018"
__maintainer__ = "Veronica Berglyd Olsen"
__email__      = "code@vkbo.net"
__status__     = "Development"
__website__    = "https://github.com/vkbo/novelWriter"

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
#    VVERBOSE  Use for describing what the user does, like clicks and entries
#

# Adding verbose and vverbose logging levels

VERBOSE  = 9
VVERBOSE = 8
logging.addLevelName(VERBOSE, "DEBUGV")
logging.addLevelName(VVERBOSE,"DEBUGVV")

def logVerbose(self, message, *args, **kws):
    if self.isEnabledFor(VERBOSE):
        self._log(VERBOSE, message, args, **kws)
def logVVerbose(self, message, *args, **kws):
    if self.isEnabledFor(VVERBOSE):
        self._log(VVERBOSE, message, args, **kws)

logging.Logger.verbose  = logVerbose
logging.Logger.vverbose = logVVerbose

# Initiating logging
logger = logging.getLogger(__name__)

#
#  Main Program
# ==============
#

# Load the main config as a global object
CONFIG = Config()

# Constants
DOCTYPE_ABOUT   = 0
DOCTYPE_DOC     = 1
DOCTYPE_PROJECT = 2

def main(sysArgs):
    """
    Parses command line, sets up logging, and launches main GUI.
    """

    # Valid Input Options
    shortOpt = "hd:qtl:v"
    longOpt  = [
        "help",
        "debug=",
        "verbose",
        "vverbose",
        "quiet",
        "time",
        "logfile=",
        "version",
        "config=",
        "headless",
    ]

    helpMsg = (
        "novelWriter {version} ({status})\n"
        "{copyright}\n"
        "\n"
        "Usage:\n"
        " -h, --help      Print this message.\n"
        " -v, --version   Print program version and exit.\n"
        " -d, --debug     Debug level. Valid options are DEBUG, INFO, WARN or ERROR.\n"
        "     --verbose   Increase verbosity of debug.\n"
        "     --vverbose  Increase verbosity of debug even more.\n"
        " -q, --quiet     Disable output to command line. Does not affect log file.\n"
        " -t, --time      Shows time stamp in logging output. Adds milliseconds for verbose.\n"
        " -l, --logfile   Specify log file.\n"
        "     --config    Alternative config file.\n"
        "     --headless  Do not display GUI. Useful for testing scripts.\n"
    ).format(
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
    showGUI    = True

    # Parse Options
    try:
        inOpts, inArgs = getopt.getopt(sysArgs,shortOpt,longOpt)
    except getopt.GetoptError:
        print(helpMsg)
        exit(2)

    for inOpt, inArg in inOpts:
        if   inOpt in ("-h","--help"):
            print(helpMsg)
            exit()
        elif inOpt in ("-v", "--version"):
            print("makeNovel %s Version %s" % (__status__,__version__))
            exit()
        elif inOpt in ("-d", "--debug"):
            if   inArg == "ERROR":
                debugLevel = logging.ERROR
            elif inArg == "WARN":
                debugLevel = logging.WARNING
            elif inArg == "INFO":
                debugLevel = logging.INFO
            elif inArg == "DEBUG":
                debugLevel = logging.DEBUG
                debugStr   = "{name:>22}:{lineno:<4d}  {levelname:8}  {message:}"
            else:
                print("Invalid debug level")
                exit(2)
        elif inOpt in ("-l","--logfile"):
            logFile = inArg
            toFile  = True
        elif inOpt in ("-q","--quiet"):
            toStd = False
        elif inOpt in ("--verbose"):
            debugLevel = VERBOSE
            timeStr    = "[{asctime:}.{msecs:03.0f}] "
        elif inOpt in ("--vverbose"):
            debugLevel = VVERBOSE
            timeStr    = "[{asctime:}.{msecs:03.0f}] "
        elif inOpt in ("-t","--time"):
            showTime = True
        elif inOpt in ("--config"):
            confPath = inArg
        elif inOpt in ("--headless"):
            showGUI = False

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

    nwApp = QApplication([])
    nwGUI = NovelWriter()
    exit(nwApp.exec_())

    return
