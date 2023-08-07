"""
novelWriter – Alert Functions
=============================

File History:
Created: 2023-08-07 [2.1b2]

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

import logging

from PyQt5.QtWidgets import QMessageBox

from novelwriter import GLOBAL
from novelwriter.enum import nwAlert
from novelwriter.constants import nwLabels

logger = logging.getLogger(__name__)


def makeAlert(message: list[str] | str, level: nwAlert, exc: Exception | None = None) -> None:
    """Alert both the user and the logger at the same time. The
    message can be either a string or a list of strings.
    """
    if isinstance(message, list):
        message = list(filter(None, message))  # Strip empty strings
        popMsg = "<br>".join(message)
        logMsg = " ".join(message)
    else:
        popMsg = str(message)
        logMsg = str(message)

    kw = {}
    if exc is not None:
        kw["exc_info"] = exc
        popMsg = f"{popMsg}<br>{type(exc).__name__}: {str(exc)}"

    # Write to Log
    if level == nwAlert.INFO:
        logger.info(logMsg, **kw)
    elif level == nwAlert.WARN:
        logger.warning(logMsg, **kw)
    elif level == nwAlert.ERROR:
        logger.error(logMsg, **kw)

    # Popup
    msgBox = QMessageBox()
    if level == nwAlert.INFO:
        msgBox.information(GLOBAL.gui, nwLabels.ALERT_NAME[level], popMsg)
    elif level == nwAlert.WARN:
        msgBox.warning(GLOBAL.gui, nwLabels.ALERT_NAME[level], popMsg)
    elif level == nwAlert.ERROR:
        msgBox.critical(GLOBAL.gui, nwLabels.ALERT_NAME[level], popMsg)

    return


def askQuestion(title: str, question: str) -> bool:
    """Ask the user a Yes/No question, and return the answer."""
    msgBox = QMessageBox()
    msgRes = msgBox.question(GLOBAL.gui, title, question, QMessageBox.Yes | QMessageBox.No)
    return msgRes == QMessageBox.Yes
