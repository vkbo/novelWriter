# -*- coding: utf-8 -*-
"""novelWriter Init

 novelWriter – Exception Handling
==================================
 Error handling functions

 File History:
 Created: 2020-08-02 [0.10.2]

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

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    qApp, QDialog, QGridLayout, QStyle, QPlainTextEdit, QLabel,
    QDialogButtonBox
)

class NWErrorMessage(QDialog):

    def __init__(self, parent):
        QDialog.__init__(self, parent=parent)
        self.setObjectName("NWErrorMessage")

        # Widgets
        self.msgIcon = QLabel()
        self.msgIcon.setPixmap(
            qApp.style().standardIcon(QStyle.SP_MessageBoxCritical).pixmap(64, 64)
        )
        self.msgHead = QLabel()
        self.msgHead.setOpenExternalLinks(True)
        self.msgHead.setWordWrap(True)

        self.msgBody = QPlainTextEdit()
        self.msgBody.setReadOnly(True)

        self.btnBox = QDialogButtonBox(QDialogButtonBox.Close)
        self.btnBox.rejected.connect(self._doClose)

        # Assemble
        self.mainBox = QGridLayout()
        self.mainBox.addWidget(self.msgIcon, 0, 0, 2, 1, Qt.AlignTop)
        self.mainBox.addWidget(self.msgHead, 0, 1, 1, 1, Qt.AlignTop)
        self.mainBox.addWidget(self.msgBody, 1, 1, 1, 1)
        self.mainBox.addWidget(self.btnBox,  2, 0, 1, 2)
        self.mainBox.setSpacing(16)

        self.setLayout(self.mainBox)

        self.setMinimumWidth(500)
        self.setMinimumHeight(300)
        self.setSizeGripEnabled(True)
        self.resize(800, 400)

        return

    def setMessage(self, exType, exValue, exTrace):
        """Generate a message and append session data, error info and
        error traceback.
        """
        import sys
        from traceback import format_tb
        from nw import __issuesurl__, __version__
        from PyQt5.Qt import PYQT_VERSION_STR
        from PyQt5.QtCore import QT_VERSION_STR, QSysInfo

        self.msgHead.setText((
            "<p>An unhandled error has been encountered.</p>"
            "<p>Please report this error by submitting an issue report on "
            "GitHub, providing a description and including the error "
            "message and traceback shown below.</p>"
            "<p>URL: <a href='{issueUrl}'>{issueUrl}</a></p>"
        ).format(
            issueUrl = __issuesurl__,
        ))

        try:
            kernelVersion = QSysInfo.kernelVersion()
        except Exception:
            kernelVersion = "Unknown"

        try:
            self.msgBody.setPlainText((
                "Environment:\n"
                "novelWriter Version: {nwVersion}\n"
                "Host OS: {osType} ({osKernel})\n"
                "Python: {pyVersion} ({pyHexVer:#x})\n"
                "Qt: {qtVers}, PyQt: {pyqtVers}\n"
                "\n"
                "{exType}:\n{exMessage}\n"
                "\n"
                "Traceback:\n{exTrace}\n"
            ).format(
                nwVersion = __version__,
                osType    = sys.platform,
                osKernel  = kernelVersion,
                pyVersion = sys.version.split()[0],
                pyHexVer  = sys.hexversion,
                qtVers    = QT_VERSION_STR,
                pyqtVers  = PYQT_VERSION_STR,
                exType    = exType.__name__,
                exMessage = str(exValue),
                exTrace   = "\n".join(format_tb(exTrace)),
            ))
        except Exception:
            self.msgBody.setPlainText("Failed to generate error report ...")

        return

    ##
    #  Slots
    ##

    def _doClose(self):
        """Close the dialog.
        """
        self.close()
        return

# END Class NWErrorMessage


def exceptionHandler(exType, exValue, exTrace, testMode=False):
    """Function to catch unhandled global exceptions.
    """
    import nw
    import logging
    from traceback import print_tb
    from PyQt5.QtWidgets import qApp

    logger = logging.getLogger(__name__)
    logger.critical("%s: %s" % (exType.__name__, str(exValue)))
    print_tb(exTrace)

    try:
        nwGUI = None
        for qWin in qApp.topLevelWidgets():
            if qWin.objectName() == "GuiMain":
                nwGUI = qWin
                break

        if nwGUI is None:
            logger.warning("Could not find main GUI window so cannot open error dialog")
            return

        errMsg = NWErrorMessage(nwGUI)
        errMsg.setMessage(exType, exValue, exTrace)
        if nw.CONFIG.showGUI:
            errMsg.exec_()

        try:
            # Try a controlled shudown
            nwGUI.closeProject(isYes=True)
            nwGUI.closeMain()
            logger.info("Emergency shutdown successful")

        except Exception as e:
            logger.critical("Could not close the project before exiting")
            logger.critical(str(e))

        if testMode:
            return errMsg.msgBody.toPlainText()
        else:
            qApp.exit(1)

    except Exception as e:
        logger.critical(str(e))

    return
