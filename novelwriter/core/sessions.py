"""
novelWriter – Project Session Log Class
=======================================

File History:
Created: 2023-06-11 [2.1b1] NWSessionLog

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

import json
import logging

from collections.abc import Iterable
from pathlib import Path
from time import time
from typing import TYPE_CHECKING

from novelwriter.common import formatTimeStamp
from novelwriter.constants import nwFiles
from novelwriter.error import logException

if TYPE_CHECKING:  # pragma: no cover
    from novelwriter.core.project import NWProject

logger = logging.getLogger(__name__)


class NWSessionLog:
    """Core: Session JSON Lines Log File

    The class that wraps the session log file, which is in JSON Lines
    format. That is, one JSON object per line.
    """

    def __init__(self, project: NWProject) -> None:
        self._project = project
        self._start = 0.0
        return

    ##
    #  Properties
    ##

    @property
    def start(self) -> float:
        """The session start time."""
        return self._start

    ##
    #  Methods
    ##

    def startSession(self) -> None:
        """Start the writing session."""
        self._start = time()
        return

    def appendSession(self, idleTime: float) -> bool:
        """Append session statistics to the sessions log file."""
        sessFile = self._project.storage.getMetaFile(nwFiles.SESS_FILE)
        if not isinstance(sessFile, Path):
            return False

        now = time()
        iNovel, iNotes = self._project.data.initCounts
        cNovel, cNotes = self._project.data.currCounts
        iTotal = iNovel + iNotes
        wDiff = cNovel + cNotes - iTotal
        sTime = now - self._start

        logger.info("The session lasted %d sec and added %d words", int(sTime), wDiff)
        if sTime < 300 and wDiff == 0:
            logger.info("Session too short, skipping log entry")
            return False

        try:
            if not sessFile.exists():
                with open(sessFile, mode="w", encoding="utf-8") as fObj:
                    fObj.write(self.createInitial(iTotal))

            with open(sessFile, mode="a+", encoding="utf-8") as fObj:
                fObj.write(self.createRecord(
                    start=formatTimeStamp(self._start),
                    end=formatTimeStamp(now),
                    novel=cNovel,
                    notes=cNotes,
                    idle=round(idleTime)
                ))

        except Exception:
            logger.error("Failed to write to session stats file")
            logException()
            return False

        return True

    def iterRecords(self) -> Iterable[dict]:
        """Iterate through all records in the log."""
        sessFile = self._project.storage.getMetaFile(nwFiles.SESS_FILE)
        if isinstance(sessFile, Path) and sessFile.is_file():
            try:
                with open(sessFile, mode="r", encoding="utf-8") as fObj:
                    for line in fObj:
                        yield json.loads(line)
            except Exception:
                logger.error("Failed to process session stats file")
                logException()
        return

    def createInitial(self, total: int) -> str:
        """Low level function to create the initial log file record."""
        data = json.dumps({"type": "initial", "offset": total})
        return f"{data}\n"

    def createRecord(self, start: str, end: str, novel: int, notes: int, idle: int) -> str:
        """Low level function to create a log record."""
        data = json.dumps({
            "type": "record", "start": start, "end": end,
            "novel": novel, "notes": notes, "idle": idle,
        })
        return f"{data}\n"
