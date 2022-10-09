"""
novelWriter – Project Document Tools
====================================
A collection of tools to create and manipulate documents

File History:
Created: 2022-10-02 [2.0b1]

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

import logging

from novelwriter.core.document import NWDoc

logger = logging.getLogger(__name__)


class DocMerger:

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

        inDoc = NWDoc(self.theProject, srcHandle)
        docText = (inDoc.readDocument() or "").rstrip("\n")

        if addComment:
            docInfo = srcItem.describeMe("H0")
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

        outDoc = NWDoc(self.theProject, self._targetDoc)
        docText = (outDoc.readDocument() or "").rstrip("\n")
        if docText:
            self._targetText.insert(0, docText)

        status = outDoc.writeDocument("\n\n".join(self._targetText))
        if not status:
            self._error = outDoc.getError()

        return status

# END Class DocMerger
