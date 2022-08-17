"""
novelWriter – Logging
=======================
Application logging setup
split off form __init__.py to make type checking happy

File History:
Created: 2022-08-15

This file is a part of novelWriter
Copyright 2018–2022, Veronica Berglyd Olsen

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


import logging
from typing import cast


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

class VerboseLogger(logging.Logger):

    def verbose(self, message: object, *args, **kws) -> None:
        if self.isEnabledFor(VERBOSE):
            self._log(VERBOSE, message, args, **kws)

logging.setLoggerClass(VerboseLogger)


# Initiating logging
logger: VerboseLogger = cast(VerboseLogger, logging.getLogger())

def getLogger(suffix: str) -> VerboseLogger:
    return logger.getChild(suffix)