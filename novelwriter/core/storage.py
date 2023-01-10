"""
novelWriter – Project Storage Class
===================================
The main class handling the project storage

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

import logging
import novelwriter

from time import time
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile

from novelwriter.error import logException
from novelwriter.common import minmax
from novelwriter.constants import nwFiles
from novelwriter.core.document import NWDocument
from novelwriter.core.projectxml import ProjectXMLReader, ProjectXMLWriter

logger = logging.getLogger(__name__)


class NWStorage:

    MODE_INACTIVE = 0
    MODE_INPLACE  = 1
    MODE_ARCHIVE  = 2

    def __init__(self, theProject):

        self.mainConf = novelwriter.CONFIG
        self.theProject = theProject

        self._storagePath = None
        self._runtimePath = None
        self._lockFilePath = None
        self._openMode = self.MODE_INACTIVE

        return

    def clear(self):
        """Reset internal variables.
        """
        self._storagePath = None
        self._runtimePath = None
        self._openMode = self.MODE_INACTIVE
        return

    ##
    #  Properties
    ##

    @property
    def storagePath(self):
        return self._storagePath

    @property
    def runtimePath(self):
        return self._runtimePath

    @property
    def contentPath(self):
        if self._runtimePath is not None:
            return self._runtimePath / "content"
        return None

    ##
    #  Core Methods
    ##

    def isOpen(self):
        """Check if the storage location is open.
        """
        return self._runtimePath is not None

    def openProjectInPlace(self, path, newProject=False):
        """Open a novelWriter project in-place. That is, it is opened
        directly from a project folder.
        """
        inPath = Path(path).resolve()
        if inPath.is_file():
            # The path should not point to an exisitng file,
            # but it can point to a folder containing files
            inPath = inPath.parent

        if not (inPath.is_dir() or newProject):
            # If the project is not new, the folder must already exist.
            return False

        self._storagePath = inPath
        self._runtimePath = inPath
        self._lockFilePath = inPath / nwFiles.PROJ_LOCK
        self._openMode = self.MODE_INPLACE

        if not self._prepareStorage(checkLegacy=True, newProject=newProject):
            self.clear()
            return False

        return True

    def openProjectArchive(self, path):  # pragma: no cover
        """Placeholder for later implementation. See #977.
        """
        return False

    def runPostSaveTasks(self, autoSave=False):  # pragma: no cover
        """Run tasks after the project has been saved.
        """
        if self._openMode == self.MODE_INPLACE:
            # Nothing to do, so we just return
            return True

        return True

    def closeSession(self):
        """Run tasks related to closing the session.
        """
        # Clear lockfile
        self.clear()
        return

    ##
    #  Content Access Methods
    ##

    def getXmlReader(self):
        """Return a properly configured ProjectXMLReader instance.
        """
        if self._runtimePath is None:
            return None

        projFile = self._runtimePath / nwFiles.PROJ_FILE
        xmlReader = ProjectXMLReader(projFile)

        return xmlReader

    def getXmlWriter(self):
        """Return a properly configured ProjectXMLWriter instance.
        """
        if self._runtimePath is None:
            return None

        xmlWriter = ProjectXMLWriter(self._runtimePath)

        return xmlWriter

    def getDocument(self, tHandle):
        """Return a document wrapper object.
        """
        if self._runtimePath is not None:
            return NWDocument(self.theProject, tHandle)
        return NWDocument(self.theProject, None)

    def getMetaFile(self, fileName):
        """Return the path to a file in the project meta folder.
        """
        if self._runtimePath is not None:
            return self._runtimePath / "meta" / fileName
        return None

    def getCacheFile(self, fileName):
        """Return the path to a file in the project cache folder.
        """
        if self._runtimePath is not None:
            return self._runtimePath / "cache" / fileName
        return None

    def readLockFile(self):
        """Read the project lock file.
        """
        if self._lockFilePath is None:
            return ["ERROR"]

        if not self._lockFilePath.exists():
            return []

        try:
            lines = self._lockFilePath.read_text(encoding="utf-8").split(";")
        except Exception:
            logger.error("Failed to read project lockfile")
            logException()
            return ["ERROR"]

        if len(lines) != 4:
            return ["ERROR"]

        return lines

    def writeLockFile(self):
        """Write the project lock file.
        """
        if self._lockFilePath is None:
            return False

        data = [
            self.mainConf.hostName, self.mainConf.osType,
            self.mainConf.kernelVer, str(int(time()))
        ]
        try:
            self._lockFilePath.write_text(";".join(data), encoding="utf-8")
        except Exception:
            logger.error("Failed to write project lockfile")
            logException()
            return False

        return True

    def clearLockFile(self):
        """Remove the lock file, if it exists.
        """
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

    def zipIt(self, target, compression=None):
        """Zip the content of the project at its runtime location into a
        zip file. This process will only grab files that are supposed to
        be in the project. All non-project files will be left out.
        """
        basePath = self._runtimePath
        if not isinstance(basePath, Path):
            logger.error("No path set")
            return False

        baseMeta = basePath / "meta"
        baseCont = basePath / "content"
        files = [
            (basePath / nwFiles.PROJ_FILE,  nwFiles.PROJ_FILE),
            (baseMeta / nwFiles.OPTS_FILE,  f"meta/{nwFiles.OPTS_FILE}"),
            (baseMeta / nwFiles.SESS_STATS, f"meta/{nwFiles.SESS_STATS}"),
            (baseMeta / nwFiles.INDEX_FILE, f"meta/{nwFiles.INDEX_FILE}"),
            (baseMeta / nwFiles.PROJ_DICT,  f"meta/{nwFiles.PROJ_DICT}"),
        ]
        for contItem in baseCont.iterdir():
            name = contItem.name
            if contItem.is_file() and len(name) == 17 and name.endswith(".nwd"):
                files.append((contItem, f"content/{name}"))

        comp = ZIP_STORED if compression is None else ZIP_DEFLATED
        level = minmax(compression, 0, 9) if isinstance(compression, int) else None
        try:
            with ZipFile(target, mode="w", compression=comp, compresslevel=level) as zipObj:
                logger.info("Creating archive: %s", target)
                for srcPath, zipPath in files:
                    if srcPath.is_file():
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

    def _prepareStorage(self, checkLegacy=True, newProject=False):
        """Prepare the storage area for the project.
        """
        path = self._runtimePath
        if not isinstance(path, Path):
            logger.error("No path set")
            self.clear()
            return False

        if path == Path.home().absolute():
            logger.error("Cannot use the user's home path as the root of a project")
            self.clear()
            return False

        if newProject:
            # If it's a new project, we check that there is no existing
            # project in the selected path.
            if path.exists() and len(list(path.iterdir())) > 0:
                logger.error("The new project folder is not empty")
                self.clear()
                return False

        # The folder is not required to exist, as it could be a new
        # project, so we make sure it does. Then we add subfolders.
        try:
            path.mkdir(exist_ok=True)
            (path / "content").mkdir(exist_ok=True)
            (path / "cache").mkdir(exist_ok=True)
            (path / "meta").mkdir(exist_ok=True)
        except Exception as exc:
            logger.error("Failed to create required project folders", exc_info=exc)
            self.clear()
            return False

        if not checkLegacy:
            # The legacy content check is only needed for project folder
            # storage, so if it is not expected to be that, there's no
            # need for the remaning checks.
            return True

        # Check for legacy data folders
        for child in path.iterdir():
            if child.is_dir() and child.name.startswith("data_"):
                self._legacyDataFolder(path, child)

        # Check for no longer used files, and delete them
        self._deleteDeprecatedFiles(path)

        return True

    ##
    #  Legacy Project Data Handlers
    ##

    def _legacyDataFolder(self, path: Path, child: Path):
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

    def _deleteDeprecatedFiles(self, path: Path):
        """Delete files that are no longer used by novelWriter.
        """
        remove = [
            path / "meta" / "mainOptions.json",        # Replaced in 0.5
            path / "meta" / "exportOptions.json",      # Replaced in 0.5
            path / "meta" / "outlineOptions.json",     # Replaced in 0.5
            path / "meta" / "timelineOptions.json",    # Replaced in 0.5
            path / "meta" / "docMergeOptions.json",    # Replaced in 0.5
            path / "meta" / "sessionLogOptions.json",  # Replaced in 0.5
            path / "ToC.json",                         # Dropped in 1.0 RC 1
        ]
        for item in remove:
            if item.is_file():
                try:
                    item.unlink()
                    logger.info("Deleted: %s", item)
                except Exception as exc:
                    logger.warning("Failed to delete: %s", item, exc_info=exc)

        return

# END Class NWStorage
