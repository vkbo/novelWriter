# -*- coding: utf-8 -*-
"""novelWriter Init

 novelWriter – Exception Handling
==================================
 Error handling functions

 File History:
 Created: 2020-08-02 [0.10.2]

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

def formatHtmlErrMsg(exType, exValue, exTrace):
    """Generates a HTML version of an exception.
    """
    try:
        import sys
        from traceback import format_tb
        from nw import __issuesurl__, __version__
        from PyQt5.Qt import PYQT_VERSION_STR
        from PyQt5.QtCore import QT_VERSION_STR, QSysInfo

        fmtTrace = ""
        for trEntry in format_tb(exTrace):
            for trLine in trEntry.split("\n"):
                stripLine = trLine.lstrip(" ")
                nIndent = len(trLine) - len(stripLine)
                fmtTrace += "&nbsp;"*nIndent + stripLine + "<br>"

        theMessage = (
            "<p>Please report this error by submitting an issue report on "
            "GitHub, providing a description and this error message. "
            "URL: &lt;{issueUrl}&gt;.</p>"
            "<p><b>Environment</b><br>Version: {nwVersion}, OS: {osType} ({osKernel}), "
            "Python: {pyVersion} ({pyHexVer:#x}), Qt: {qtVers}, PyQt: {pyqtVers}</p>"
            "<p><b>Error Type</b><br>{exType}: {exMessage}</p>"
            "<p><b>Traceback</b><br>{exTrace}</p>"
        ).format(
            nwVersion = __version__,
            osType    = sys.platform,
            osKernel  = QSysInfo.kernelVersion(),
            pyVersion = sys.version.split()[0],
            pyHexVer  = sys.hexversion,
            qtVers    = QT_VERSION_STR,
            pyqtVers  = PYQT_VERSION_STR,
            issueUrl  = __issuesurl__,
            exType    = exType.__name__,
            exMessage = str(exValue),
            exTrace   = fmtTrace
        )

        return theMessage

    except Exception as e:
        return "Could not generate error message.<br>%s" % str(e)

    return "Could not generate error message."


def exceptionHandler(exType, exValue, exTrace):
    """Function to catch unhandled global exceptions.
    """
    import logging
    from traceback import print_tb
    from nw import CONFIG
    from PyQt5.QtWidgets import qApp, QErrorMessage

    logger = logging.getLogger(__name__)
    logger.error("%s: %s" % (exType.__name__, str(exValue)))
    print_tb(exTrace)

    if not CONFIG.showGUI:
        return

    try:
        nwGUI = None
        for qWin in qApp.topLevelWidgets():
            if qWin.objectName() == "GuiMain":
                nwGUI = qWin
                break

        if nwGUI is None:
            logger.warning("Could not find main GUI window so cannot open error dialog")
            return

        errMsg = QErrorMessage(nwGUI)
        errMsg.setWindowTitle("Unhandled Error")
        errMsg.resize(800, 400)
        errMsg.showMessage((
            "<h3>An unhandled error has been encountered</h3>%s"
        ) % formatHtmlErrMsg(exType, exValue, exTrace))

    except Exception as e:
        logger.error(str(e))

    return
