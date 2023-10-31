"""
novelWriter – Project Storage Class
===================================

File History:
Created: 2022-11-01 [2.0rc2] NWStorage

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

import json
import uuid
import hashlib
import logging

from enum import Enum
from time import time
from typing import TYPE_CHECKING
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile, is_zipfile

from novelwriter import CONFIG, __version__, __hexversion__
from novelwriter.error import logException
from novelwriter.common import formatTimeStamp, isHandle, minmax
from novelwriter.constants import nwFiles
from novelwriter.core.document import NWDocument
from novelwriter.core.projectxml import ProjectXMLReader, ProjectXMLWriter
from novelwriter.core.spellcheck import UserDictionary

if TYPE_CHECKING:  # pragma: no cover
    from novelwriter.core.project import NWProject

logger = logging.getLogger(__name__)


class NWStorageState(Enum):

    NO_ERROR       = 0
    NOT_FOUND      = 1
    ALREADY_EXISTS = 2
    FAILED         = 3
    READ_ONLY      = 4

# END Enum NWStorageState


class NWStorage:
    """Core: Project Storage Class

    The class that handles all paths related to the project storage.
    """

    MODE_INACTIVE = 0
    MODE_INPLACE  = 1
    MODE_ARCHIVE  = 2

    def __init__(self, project: NWProject) -> None:
        self._project = project
        self._storagePath = None
        self._runtimePath = None
        self._lockFilePath = None
        self._openMode = self.MODE_INACTIVE
        self._readOnly = True
        self._state = NWStorageState.NO_ERROR
        return

    def clear(self) -> None:
        """Reset internal variables."""
        self._storagePath = None
        self._runtimePath = None
        self._lockFilePath = None
        self._openMode = self.MODE_INACTIVE
        self._readOnly = True
        return

    ##
    #  Properties
    ##

    @property
    def storagePath(self) -> Path | None:
        """Return the path where the project is stored."""
        return self._storagePath

    @property
    def runtimePath(self) -> Path | None:
        """Return the path where the project is stored at runtime."""
        return self._runtimePath

    @property
    def contentPath(self) -> Path | None:
        """Return the path used for project content. The folder must
        already exist, otherwise this property is None.
        """
        if isinstance(self._runtimePath, Path):
            contentPath = self._runtimePath / "content"
            if contentPath.is_dir():
                return contentPath
        logger.error("Content path cannot be resolved")
        return None

    @property
    def readOnly(self) -> bool:
        """Return True of the project is read only."""
        return self._readOnly

    @property
    def state(self) -> NWStorageState:
        """Return the state of the storage instance."""
        return self._state

    ##
    #  Core Methods
    ##

    def isOpen(self) -> bool:
        """Check if the storage location is open."""
        return self._runtimePath is not None

    def createNewProject(self, path: str | Path, asArchive: bool) -> bool:
        """Create a new project in a given location."""
        self._state = NWStorageState.NO_ERROR
        inPath = Path(path).resolve()
        inPath = inPath.with_suffix(".nwproj") if asArchive else inPath.with_suffix("")

        if asArchive:
            if inPath.is_file():
                logger.error("File already exists: %s", inPath)
                self._state = NWStorageState.ALREADY_EXISTS
                return False
            self._storagePath = inPath
            self._runtimePath = CONFIG.dataPath("temp", mkdir=True) / str(uuid.uuid4())
            self._lockFilePath = inPath.parent / f"{inPath.name}.lock"
            self._openMode = self.MODE_ARCHIVE
        else:
            if inPath.is_dir() and len(list(inPath.iterdir())) > 0:
                logger.error("Folder is not empty: %s", inPath)
                self._state = NWStorageState.ALREADY_EXISTS
                return False
            self._storagePath = inPath
            self._runtimePath = inPath
            self._lockFilePath = inPath / nwFiles.PROJ_LOCK
            self._openMode = self.MODE_INPLACE

        basePath = self._runtimePath
        metaPath = basePath / "meta"
        contPath = basePath / "content"
        try:
            basePath.mkdir(exist_ok=True)
            metaPath.mkdir(exist_ok=True)
            contPath.mkdir(exist_ok=True)
        except Exception as exc:
            logger.error("Failed to create project folders", exc_info=exc)
            self._state = NWStorageState.FAILED
            self.clear()
            return False

        return True

    def openProject(self, path: str | Path) -> bool:
        """Open a novelWriter project storage location."""
        self._state = NWStorageState.NO_ERROR
        inPath = Path(path).resolve()
        isArchive = False

        # Check what we're opening. Only three options are allowed:
        # 1. A folder with a nwProject.nwx file in it
        # 2. A zip file with the .nwproj extension
        # 3. A nwProject.nwx file opened directly
        if inPath.is_dir():
            nwxFile = inPath / nwFiles.PROJ_FILE
        elif is_zipfile(inPath) and inPath.suffix == ".nwproj":
            nwxFile = inPath
            isArchive = True
        elif inPath.is_file() and inPath.name == nwFiles.PROJ_FILE:
            nwxFile = inPath
        else:
            logger.error("Not a novelWriter project file")
            return False

        if not nwxFile.exists():
            # The .nwx/.nwproj file must exist to continue
            logger.error("Not found: %s", nwxFile)
            self._state = NWStorageState.NOT_FOUND
            return False

        nwxPath = nwxFile.parent
        if isArchive:
            logger.info("Extracting: %s", nwxFile)
            try:
                with ZipFile(inPath, mode="r") as zipObj:
                    meta = self._parseMetaDataComment(zipObj.comment)
                    hasXml = nwFiles.PROJ_ARCH in zipObj.namelist()
                    hasNwx = nwFiles.PROJ_FILE in zipObj.namelist()
                    if not (hasXml or hasNwx):
                        logger.error("Not a novelWriter project")
                        return False

                    pathID = hashlib.sha1(str(nwxPath).encode()).hexdigest()
                    runtimePath = CONFIG.dataPath("projects", mkdir=True) / pathID
                    zipObj.extractall(runtimePath)

                with open(runtimePath / "instance", mode="w", encoding="utf-8") as of:
                    json.dump({
                        "path": str(nwxFile),
                        "pathID": pathID,
                        "projectID": meta.get("projectID", "None"),
                        "timeStamp": formatTimeStamp(time()),
                    }, of, indent=2)

                self._readOnly = meta.get("novelWriter", "") == "backup"

            except Exception:
                logger.error("Could not extract project archive")
                self._state = NWStorageState.FAILED
                self.clear()
                return False

            self._storagePath = nwxFile
            self._runtimePath = runtimePath
            self._lockFilePath = nwxPath / f"{nwxFile.name}.lock"
            self._openMode = self.MODE_ARCHIVE

        else:
            self._storagePath = nwxPath
            self._runtimePath = nwxPath
            self._lockFilePath = nwxPath / nwFiles.PROJ_LOCK
            self._openMode = self.MODE_INPLACE

        if not self._prepareStorage():
            logger.error("Failed to prepare project folder")
            self._state = NWStorageState.FAILED
            self.clear()
            return False

        return True

    def runPostSaveTasks(self) -> bool:
        """Run tasks after the project has been saved."""
        self._state = NWStorageState.NO_ERROR
        if self._openMode == self.MODE_ARCHIVE and isinstance(self._storagePath, Path):
            if self._readOnly:
                self._state = NWStorageState.READ_ONLY
                return False
            return self.zipIt(self._storagePath, compression=None, isBackup=False)
        return True

    def closeSession(self) -> None:
        """Run tasks related to closing the session."""
        if self._openMode == self.MODE_ARCHIVE:
            self.clearTempStorage()
        self.clearLockFile()
        self.clear()
        return

    ##
    #  Content Access Methods
    ##

    def getXmlReader(self) -> ProjectXMLReader | None:
        """Return a properly configured ProjectXMLReader instance."""
        if isinstance(self._runtimePath, Path):
            if self._openMode == self.MODE_ARCHIVE:
                return ProjectXMLReader(self._runtimePath / nwFiles.PROJ_ARCH)
            else:
                return ProjectXMLReader(self._runtimePath / nwFiles.PROJ_FILE)
        return None

    def getXmlWriter(self) -> ProjectXMLWriter | None:
        """Return a properly configured ProjectXMLWriter instance."""
        if isinstance(self._runtimePath, Path):
            if self._openMode == self.MODE_ARCHIVE:
                return ProjectXMLWriter(self._runtimePath / nwFiles.PROJ_ARCH)
            else:
                return ProjectXMLWriter(self._runtimePath / nwFiles.PROJ_FILE)
        return None

    def getDocument(self, tHandle: str | None) -> NWDocument:
        """Return a document wrapper object."""
        if isinstance(self._runtimePath, Path):
            return NWDocument(self._project, tHandle)
        return NWDocument(self._project, None)

    def getMetaFile(self, fileName: str) -> Path | None:
        """Return the path to a file in the project meta folder."""
        if isinstance(self._runtimePath, Path):
            return self._runtimePath / "meta" / fileName
        return None

    def scanContent(self) -> list[str]:
        """Scan the content folder and return the handle of all files
        found in it. Files that do not match the pattern are ignored.
        """
        contentPath = self.contentPath
        return [
            item.stem for item in contentPath.iterdir()
            if item.suffix == ".nwd" and isHandle(item.stem)
        ] if contentPath else []

    def readLockFile(self) -> list[str]:
        """Read the project lock file."""
        if self._lockFilePath is None:
            return ["ERROR"]

        if not self._lockFilePath.exists():
            return []

        try:
            lines = self._lockFilePath.read_text(encoding="utf-8").strip().split(";")
        except Exception:
            logger.error("Failed to read project lockfile")
            logException()
            return ["ERROR"]

        if len(lines) != 4:
            return ["ERROR"]

        return lines

    def writeLockFile(self) -> bool:
        """Write the project lock file."""
        if self._lockFilePath is None:
            return False

        data = [
            CONFIG.hostName, CONFIG.osType,
            CONFIG.kernelVer, str(int(time()))
        ]
        try:
            self._lockFilePath.write_text(";".join(data), encoding="utf-8")
        except Exception:
            logger.error("Failed to write project lockfile")
            logException()
            return False

        return True

    def clearLockFile(self) -> bool:
        """Remove the lock file, if it exists."""
        if self._lockFilePath is None:
            return False

        if self._lockFilePath.exists():
            try:
                self._lockFilePath.unlink()
            except Exception:
                logger.error("Failed to remove project lockfile")
                logException()
                return False

        return True

    def clearTempStorage(self) -> None:
        """Clear a temporary runtime path if it is safe."""
        runPath = self._runtimePath
        if isinstance(runPath, Path) and runPath.is_relative_to(CONFIG.dataPath()):
            files = self._projectFiles(runPath)
            files.append((runPath / "mimetype", "mimetype"))
            files.append((runPath / "instance", "instance"))
            for filePath, _ in files:
                try:
                    filePath.unlink(missing_ok=True)
                except Exception:
                    logger.error("Could not delete: %s", filePath)
            dirs = [runPath / "content", runPath / "meta", runPath]
            for dirPath in dirs:
                try:
                    dirPath.rmdir()
                except Exception:
                    logger.error("Could not delete: %s", dirPath)

            # Check if anything remains, and move it out of the way
            if runPath.exists():
                try:
                    runPath.rename(CONFIG.dataPath("temp", mkdir=True) / f"error-{uuid.uuid4()}")
                except Exception:
                    logger.error("Could not clean up: %s", runPath)
        return

    def zipIt(self, target: Path, compression: int | None = None, isBackup: bool = False) -> bool:
        """Zip the content of the project at its runtime location into a
        zip file. This process will only grab files that are supposed to
        be in the project. All non-project files will be left out.
        """
        basePath = self._runtimePath
        if not isinstance(basePath, Path):
            logger.error("No path set")
            return False

        comp = ZIP_STORED if compression is None else ZIP_DEFLATED
        level = minmax(compression, 0, 9) if isinstance(compression, int) else None
        try:
            with ZipFile(target, mode="w", compression=comp, compresslevel=level) as zipObj:
                zipObj.writestr("mimetype", "application/x-novelwriter-project")
                logger.info("Creating archive: %s", target)
                zipObj.comment = self._createMetaDataComment(isBackup)
                for srcPath, zipPath in self._projectFiles(basePath):
                    if zipPath and srcPath.is_file():
                        zipObj.write(srcPath, zipPath)
                        logger.debug("Added: %s", zipPath)
        except Exception:
            logger.error("Failed to create acrhive")
            logException()
            return False

        return True

    ##
    #  Internal Functions
    ##

    def _projectFiles(self, basePath: Path) -> list[tuple[Path, str]]:
        """Build a list of files expected to be in a project."""
        files = []
        baseMeta = basePath / "meta"
        baseCont = basePath / "content"

        # Project files
        nwxFile = basePath / nwFiles.PROJ_FILE
        xmlFile = basePath / nwFiles.PROJ_ARCH
        nwxBack = nwxFile.with_suffix(".bak")
        xmlBack = xmlFile.with_suffix(".bak")

        files.append((nwxFile if nwxFile.is_file() else xmlFile, nwFiles.PROJ_ARCH))
        files.append((nwxBack if nwxBack.is_file() else xmlBack, str(xmlBack.name)))

        # Other/meta files
        files.append((basePath / nwFiles.TOC_TXT,     None))
        files.append((baseMeta / nwFiles.BUILDS_FILE, f"meta/{nwFiles.BUILDS_FILE}"))
        files.append((baseMeta / nwFiles.INDEX_FILE,  f"meta/{nwFiles.INDEX_FILE}"))
        files.append((baseMeta / nwFiles.OPTS_FILE,   f"meta/{nwFiles.OPTS_FILE}"))
        files.append((baseMeta / nwFiles.DICT_FILE,   f"meta/{nwFiles.DICT_FILE}"))
        files.append((baseMeta / nwFiles.SESS_FILE,   f"meta/{nwFiles.SESS_FILE}"))

        # Content files
        for item in baseCont.iterdir():
            name = item.name
            if item.is_file() and len(name) == 17 and name.endswith(".nwd"):
                files.append((item, f"content/{name}"))

        return files

    def _createMetaDataComment(self, isBackup: bool) -> bytes:
        """Create the meta data string for zip archives."""
        data = {
            "novelWriter": "backup" if isBackup else "project",
            "projectID": self._project.data.uuid,
            "appVersion": __version__,
            "hexVersion": __hexversion__,
            "timeStamp": formatTimeStamp(time()),
        }
        return ("".join(f"{k}:{v};" for k, v in data.items())).encode(encoding="utf-8")

    def _parseMetaDataComment(self, comment: bytes) -> dict[str, str]:
        """Parse a meta data string from a zip archive."""
        return {
            x[0]: x[2] for x in (
                x.partition(":") for x in comment.decode(encoding="utf-8").split(";") if x
            )
        }

    def _prepareStorage(self) -> bool:
        """Prepare the storage area for the project."""
        path = self._runtimePath
        if not isinstance(path, Path):
            logger.error("No path set")
            self.clear()
            return False

        if path == Path.home().absolute():
            logger.error("Cannot use the user's home path as the root of a project")
            self.clear()
            return False

        try:
            (path / "content").mkdir(exist_ok=True)
            (path / "meta").mkdir(exist_ok=True)
        except Exception as exc:
            logger.error("Failed to create required project folders", exc_info=exc)
            self.clear()
            return False

        # Check for legacy data folders
        legacy = _LegacyStorage(self._project)
        for child in path.iterdir():
            if child.is_dir() and child.name.startswith("data_"):
                legacy.legacyDataFolder(path, child)

        # Check for no longer used files, and delete them
        legacy.deprecatedFiles(path)

        return True

# END Class NWStorage


class _LegacyStorage:
    """Core: Legacy Storage Converter Utils

    A class with various functions to convert old file formats and
    file/folder layout to the current project format.
    """

    def __init__(self, project: NWProject) -> None:
        self._project = project
        return

    def legacyDataFolder(self, path: Path, child: Path) -> None:
        """Handle the content of a legacy data folder from a version 1.0
        project.
        """
        logger.info("Processing legacy data folder: %s", path)

        # Move Documents to Content
        first = child.name[-1]
        if first not in "0123456789abcdef":
            return

        for item in child.iterdir():
            if not item.is_file():
                continue

            name = item.name
            if len(name) == 21 and name.endswith("_main.nwd"):
                newPath = path / "content" / f"{first}{name[:12]}.nwd"
                try:
                    item.rename(newPath)
                    logger.info("Moved file: %s", newPath)
                except Exception as exc:
                    logger.warning("Failed to move: %s", item, exc_info=exc)
            elif len(name) == 21 and name.endswith("_main.bak"):
                try:
                    item.unlink()
                    logger.info("Deleted file: %s", item)
                except Exception as exc:
                    logger.warning("Failed to delete: %s", item, exc_info=exc)

        # Remove Data Folder
        try:
            child.rmdir()
            logger.info("Deleted folder: %s", child)
        except Exception as exc:
            logger.warning("Failed to delete: %s", child, exc_info=exc)

        return

    def deprecatedFiles(self, path: Path) -> None:
        """Handle files that are no longer used by novelWriter."""
        self._convertOldWordList(  # Changed in 2.1 Beta 1
            path / "meta" / "wordlist.txt",
            path / "meta" / nwFiles.DICT_FILE
        )
        self._convertOldLogFile(  # Changed in 2.1 Beta 1
            path / "meta" / "sessionStats.log",
            path / "meta" / nwFiles.SESS_FILE
        )
        self._convertOldOptionsFile(  # Changed in 2.1 Beta 1
            path / "meta" / "guiOptions.json",
            path / "meta" / nwFiles.OPTS_FILE
        )

        remove = [
            path / "meta" / "tagsIndex.json",          # Renamed in 2.1 Beta 1
            path / "meta" / "mainOptions.json",        # Replaced in 0.5
            path / "meta" / "exportOptions.json",      # Replaced in 0.5
            path / "meta" / "outlineOptions.json",     # Replaced in 0.5
            path / "meta" / "timelineOptions.json",    # Replaced in 0.5
            path / "meta" / "docMergeOptions.json",    # Replaced in 0.5
            path / "meta" / "sessionLogOptions.json",  # Replaced in 0.5
            path / "cache" / "prevBuild.json",         # Dropped in 2.1 Beta 1
            path / "cache",                            # Dropped in 2.1 Beta 1
            path / "ToC.json",                         # Dropped in 1.0 RC 1
        ]
        for item in remove:
            if item.exists():
                try:
                    if item.is_dir():
                        item.rmdir()
                    else:
                        item.unlink()
                    logger.info("Deleted: %s", item)
                except Exception as exc:
                    logger.warning("Failed to delete: %s", item, exc_info=exc)

        return

    ##
    #  Internal Functions
    ##

    def _convertOldWordList(self, wordList: Path, wordJson: Path) -> None:
        """Convert the old word list plain text file to new format."""
        if wordJson.exists() or not wordList.exists():
            # If the new file already exists, we won't overwrite it
            return

        userDict = UserDictionary(self._project)
        try:
            logger.info("Converting: %s", wordList)
            with open(wordList, mode="r", encoding="utf-8") as fObj:
                for line in fObj:
                    word = line.strip()
                    if word:
                        userDict.add(word)

            # Save dictionary and clean up old file
            userDict.save()
            wordList.unlink()

        except Exception:
            logger.error("Failed to convert old word list file")
            logException()

        return

    def _convertOldLogFile(self, sessLog: Path, sessJson: Path) -> None:
        """Convert the old text log file format to the new JSON Lines
        format.
        """
        if sessJson.exists() or not sessLog.exists():
            # If the new file already exists, we won't overwrite it
            return

        try:
            data = []
            offset = 0
            session = self._project.session
            logger.info("Converting: %s", sessLog)
            with open(sessLog, mode="r", encoding="utf-8") as fObj:
                for record in fObj:
                    bits = record.split()
                    nBits = len(bits)
                    if record.startswith("# Offset") and nBits == 3:
                        offset = int(bits[2])
                    elif not record.startswith("#") and nBits > 5:
                        data.append(session.createRecord(
                            start=f"{bits[0]} {bits[1]}",
                            end=f"{bits[2]} {bits[3]}",
                            novel=int(bits[4]),
                            notes=int(bits[5]),
                            idle=int(bits[6]) if nBits > 6 else 0,
                        ))

            with open(sessJson, mode="a+", encoding="utf-8") as fObj:
                fObj.write(session.createInitial(offset))
                fObj.write("".join(data))

            # If we're here, we remove the old file
            sessLog.unlink()

        except Exception:
            logger.error("Failed to convert old stats file")
            logException()

        return

    def _convertOldOptionsFile(self, optsOld: Path, optsNew: Path) -> None:
        """Convert the old options state file format to the format."""
        if optsNew.exists() or not optsOld.exists():
            # If the new file already exists, we won't overwrite it
            return

        try:
            data = {}
            logger.info("Converting: %s", optsOld)
            with open(optsOld, mode="r", encoding="utf-8") as fObj:
                data = json.load(fObj)
                if "GuiOutline" in data:
                    # Convert Outline Values
                    state = {}
                    outline = data.get("GuiOutline", {})
                    hidden = outline.get("columnHidden", {})
                    width = outline.get("columnWidth", {})
                    for key in outline.get("headerOrder", []):
                        state[key] = [hidden.get(key, False), width.get(key, 100)]
                    data["GuiOutline"]["columnState"] = state

            with open(optsNew, mode="w", encoding="utf-8") as fObj:
                json.dump({"novelWriter.guiOptions": data}, fObj, indent=2)

            # If we're here, we remove the old file, and then we reload
            # the converted file and save it again
            optsOld.unlink()
            self._project.options.loadSettings()
            self._project.options.saveSettings()

        except Exception:
            logger.error("Failed to convert old options file")
            logException()

        return

# END Class _LegacyStorage
