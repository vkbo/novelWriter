"""
novelWriter – Project Document Tools
====================================
A collection of tools to create and manipulate documents

File History:
Created: 2022-10-02 [2.0rc1] DocMerger
Created: 2022-10-11 [2.0rc1] DocSplitter

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

import shutil
import logging
import novelwriter

from time import time
from functools import partial

from PyQt5.QtCore import QCoreApplication

from novelwriter.enum import nwAlert
from novelwriter.common import minmax, simplified
from novelwriter.constants import nwItemClass
from novelwriter.core.project import NWProject

logger = logging.getLogger(__name__)


class DocMerger:
    """Document tool for merging a set of documents into a single new
    document. The parameters are defined by the user using the
    GuiDocMerge dialog.
    """

    def __init__(self, theProject):

        self.theProject = theProject

        self._error = ""
        self._targetDoc = None
        self._targetText = []

        return

    ##
    #  Methods
    ##

    def getError(self):
        """Return any collected errors.
        """
        return self._error

    def setTargetDoc(self, tHandle):
        """Set the target document for the merging. Calling this
        function resets the class.
        """
        self._targetDoc = tHandle
        self._targetText = []
        return

    def newTargetDoc(self, srcHandle, docLabel):
        """Create a barnd new target document based on a source handle
        and a new doc label. Calling this function resets the class.
        """
        srcItem = self.theProject.tree[srcHandle]
        if srcItem is None:
            return None

        newHandle = self.theProject.newFile(docLabel, srcItem.itemParent)
        newItem = self.theProject.tree[newHandle]
        newItem.setLayout(srcItem.itemLayout)
        newItem.setStatus(srcItem.itemStatus)
        newItem.setImport(srcItem.itemImport)

        self._targetDoc = newHandle
        self._targetText = []

        return newHandle

    def appendText(self, srcHandle, addComment, cmtPrefix):
        """Append text from an existing document to the text buffer.
        """
        srcItem = self.theProject.tree[srcHandle]
        if srcItem is None:
            return False

        inDoc = self.theProject.storage.getDocument(srcHandle)
        docText = (inDoc.readDocument() or "").rstrip("\n")

        if addComment:
            docInfo = srcItem.describeMe()
            docSt, _ = srcItem.getImportStatus(incIcon=False)
            cmtLine = f"% {cmtPrefix} {docInfo}: {srcItem.itemName} [{docSt}]\n\n"
            docText = cmtLine + docText

        self._targetText.append(docText)

        return True

    def writeTargetDoc(self):
        """Write the accumulated text into the designated target
        document, appending any existing text.
        """
        if self._targetDoc is None:
            return False

        outDoc = self.theProject.storage.getDocument(self._targetDoc)
        docText = (outDoc.readDocument() or "").rstrip("\n")
        if docText:
            self._targetText.insert(0, docText)

        status = outDoc.writeDocument("\n\n".join(self._targetText) + "\n\n")
        if not status:
            self._error = outDoc.getError()

        return status

# END Class DocMerger


class DocSplitter:
    """Document tool for splitting a document into a set of new
    documents. The parameters are defined by the user using the
    GuiDocSplit dialog.
    """

    def __init__(self, theProject, sHandle):

        self.theProject = theProject

        self._error = ""
        self._parHandle = None
        self._srcHandle = None
        self._srcItem = None

        self._inFolder = False
        self._rawData = []

        srcItem = self.theProject.tree[sHandle]
        if srcItem is not None and srcItem.isFileType():
            self._srcHandle = sHandle
            self._srcItem = srcItem

        return

    ##
    #  Methods
    ##

    def getError(self):
        """Return any collected errors.
        """
        return self._error

    def setParentItem(self, pHandle):
        """Set the item that will be the top level parent item for the
        new documents.
        """
        self._parHandle = pHandle
        self._inFolder = False
        return

    def newParentFolder(self, pHandle, folderLabel):
        """Create a new folder that will be the top level parent item
        for the new documents.
        """
        if self._srcItem is None:
            return None

        newHandle = self.theProject.newFolder(folderLabel, pHandle)
        newItem = self.theProject.tree[newHandle]
        newItem.setStatus(self._srcItem.itemStatus)
        newItem.setImport(self._srcItem.itemImport)

        self._parHandle = newHandle
        self._inFolder = True

        return newHandle

    def splitDocument(self, splitData, splitText):
        """Loop through the split data record and perform the split job.
        """
        self._rawData = []
        buffer = splitText.copy()
        for lineNo, hLevel, hLabel in reversed(splitData):
            chunk = buffer[lineNo:]
            buffer = buffer[:lineNo]
            self._rawData.insert(0, (chunk, hLevel, hLabel))

        return True

    def writeDocuments(self, docHierarchy):
        """An iterator that will write each document in the buffer, and
        return its new handle, parent handle, and sibling handle.
        """
        if self._srcHandle is None or self._srcItem is None:
            return

        pHandle = self._parHandle
        nHandle = self._parHandle if self._inFolder else self._srcHandle
        hHandle = [self._parHandle, None, None, None, None]

        pLevel = 0
        for docText, hLevel, docLabel in self._rawData:

            hLevel = minmax(hLevel, 1, 4)
            if pLevel == 0:
                pLevel = hLevel

            if docHierarchy:
                if hLevel == 1:
                    pHandle = self._parHandle
                elif hLevel == 2:
                    pHandle = hHandle[1] or hHandle[0]
                elif hLevel == 3:
                    pHandle = hHandle[2] or hHandle[1] or hHandle[0]
                elif hLevel == 4:
                    pHandle = hHandle[3] or hHandle[2] or hHandle[1] or hHandle[0]

                if hLevel < pLevel:
                    nHandle = hHandle[hLevel] or hHandle[0]
                elif hLevel > pLevel:
                    nHandle = pHandle

            dHandle = self.theProject.newFile(docLabel, pHandle)
            hHandle[hLevel] = dHandle

            newItem = self.theProject.tree[dHandle]
            newItem.setStatus(self._srcItem.itemStatus)
            newItem.setImport(self._srcItem.itemImport)

            outDoc = self.theProject.storage.getDocument(dHandle)
            status = outDoc.writeDocument("\n".join(docText))
            if not status:
                self._error = outDoc.getError()

            yield status, dHandle, nHandle

            hHandle[hLevel] = dHandle
            nHandle = dHandle
            pLevel = hLevel

        return

# END Class DocSplitter


class ProjectBuilder:
    """A class to build a new project from a set of user-defined
    parameter provided by the New Projecty Wizard.
    """

    def __init__(self, mainGui):

        self.mainGui = mainGui
        self.mainConf = novelwriter.CONFIG

        self.tr = partial(QCoreApplication.translate, "NWProject")

        return

    ##
    #  Methods
    ##

    def buildProject(self, data):
        """Build a project from a data dictionary of specifications
        provided by the wizard.
        """
        if not isinstance(data, dict):
            logger.error("Invalid call to newProject function")
            return False

        popMinimal = data.get("popMinimal", True)
        popCustom = data.get("popCustom", False)
        popSample = data.get("popSample", False)

        # Check if we're extracting the sample project. This is handled
        # differently as it isn't actually a new project, so we forward
        # this to another function and return here.
        if popSample:
            return self._extractSampleProject(data)

        projPath = data.get("projPath", None)
        if projPath is None:
            logger.error("No project path set for the new project")
            return False

        project = NWProject(self.mainGui)
        if not project.storage.openProjectInPlace(projPath, newProject=True):
            return False

        lblNewProject = self.tr("New Project")
        lblNewChapter = self.tr("New Chapter")
        lblNewScene   = self.tr("New Scene")
        lblTitlePage  = self.tr("Title Page")
        lblByAuthors  = self.tr("By")

        # Settings
        projName = data.get("projName", lblNewProject)
        projTitle = data.get("projTitle", lblNewProject)
        projAuthor = data.get("projAuthor", "")

        project.data.setUuid(None)
        project.data.setName(projName)
        project.data.setTitle(projTitle)
        project.data.setAuthor(projAuthor)
        project.setDefaultStatusImport()
        project._projOpened = int(time())

        # Add Root Folders
        hNovelRoot = project.newRoot(nwItemClass.NOVEL)
        hTitlePage = project.newFile(lblTitlePage, hNovelRoot)
        novelTitle = project.data.title if project.data.title else project.data.name

        titlePage = f"#! {novelTitle}\n\n"
        if project.data.author:
            titlePage += f">> {lblByAuthors} {project.data.author} <<\n\n"

        aDoc = project.storage.getDocument(hTitlePage)
        aDoc.writeDocument(titlePage)

        if popMinimal:
            # Creating a minimal project with a few root folders and a
            # single chapter with a single scene.
            hChapter = project.newFile(lblNewChapter, hNovelRoot)
            aDoc = project.storage.getDocument(hChapter)
            aDoc.writeDocument(f"## {lblNewChapter}\n\n")

            hScene = project.newFile(lblNewScene, hChapter)
            aDoc = project.storage.getDocument(hScene)
            aDoc.writeDocument(f"### {lblNewScene}\n\n")

            project.newRoot(nwItemClass.PLOT)
            project.newRoot(nwItemClass.CHARACTER)
            project.newRoot(nwItemClass.WORLD)
            project.newRoot(nwItemClass.ARCHIVE)

            project.saveProject()
            project.closeProject()

        elif popCustom:
            # Create a project structure based on selected root folders
            # and a number of chapters and scenes selected in the
            # wizard's custom page.

            # Create chapters and scenes
            numChapters = data.get("numChapters", 0)
            numScenes = data.get("numScenes", 0)

            chSynop = self.tr("Summary of the chapter.")
            scSynop = self.tr("Summary of the scene.")

            # Create chapters
            if numChapters > 0:
                for ch in range(numChapters):
                    chTitle = self.tr("Chapter {0}").format(f"{ch+1:d}")
                    cHandle = project.newFile(chTitle, hNovelRoot)
                    aDoc = project.storage.getDocument(cHandle)
                    aDoc.writeDocument(f"## {chTitle}\n\n% Synopsis: {chSynop}\n\n")

                    # Create chapter scenes
                    if numScenes > 0:
                        for sc in range(numScenes):
                            scTitle = self.tr("Scene {0}").format(f"{ch+1:d}.{sc+1:d}")
                            sHandle = project.newFile(scTitle, cHandle)
                            aDoc = project.storage.getDocument(sHandle)
                            aDoc.writeDocument(f"### {scTitle}\n\n% Synopsis: {scSynop}\n\n")

            # Create scenes (no chapters)
            elif numScenes > 0:
                for sc in range(numScenes):
                    scTitle = self.tr("Scene {0}").format(f"{sc+1:d}")
                    sHandle = project.newFile(scTitle, hNovelRoot)
                    aDoc = project.storage.getDocument(sHandle)
                    aDoc.writeDocument(f"### {scTitle}\n\n% Synopsis: {scSynop}\n\n")

            # Create notes folders
            noteTitles = {
                nwItemClass.PLOT: self.tr("Main Plot"),
                nwItemClass.CHARACTER: self.tr("Protagonist"),
                nwItemClass.WORLD: self.tr("Main Location"),
            }

            addNotes = data.get("addNotes", False)
            for newRoot in data.get("addRoots", []):
                if newRoot in nwItemClass:
                    rHandle = project.newRoot(newRoot)
                    if addNotes:
                        aHandle = project.newFile(noteTitles[newRoot], rHandle)
                        ntTag = simplified(noteTitles[newRoot]).replace(" ", "")
                        aDoc = project.storage.getDocument(aHandle)
                        aDoc.writeDocument(f"# {noteTitles[newRoot]}\n\n@tag: {ntTag}\n\n")

            # Also add the archive and trash folders
            project.newRoot(nwItemClass.ARCHIVE)
            project.trashFolder()

            project.saveProject()
            project.closeProject()

        return True

    ##
    #  Internal Functions
    ##

    def _extractSampleProject(self, data):
        """Make a copy of the sample project by extracting the
        sample.zip file to the new path.
        """
        projPath = data.get("projPath", None)
        if projPath is None:
            logger.error("No project path set for the example project")
            return False

        pkgSample = self.mainConf.assetPath("sample.zip")
        if pkgSample.is_file():
            try:
                shutil.unpack_archive(pkgSample, projPath)
            except Exception as exc:
                self.mainGui.makeAlert(self.tr(
                    "Failed to create a new example project."
                ), nwAlert.ERROR, exception=exc)
                return False

        else:
            self.mainGui.makeAlert(self.tr(
                "Failed to create a new example project. "
                "Could not find the necessary files. "
                "They seem to be missing from this installation."
            ), nwAlert.ERROR)
            return False

        return True

# END Class ProjectBuilder
