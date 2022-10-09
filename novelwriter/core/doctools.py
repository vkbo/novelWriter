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

logger = logging.getLogger(__name__)

# logger.verbose("GuiDocMerge merge button clicked")

# finalOrder = []
# for i in range(self.listBox.count()):
#     finalOrder.append(self.listBox.item(i).data(Qt.UserRole))

# if len(finalOrder) == 0:
#     self.mainGui.makeAlert(self.tr(
#         "No source documents found. Nothing to do."
#     ), nwAlert.ERROR)
#     return False

# theText = ""
# for tHandle in finalOrder:
#     inDoc = NWDoc(self.theProject, tHandle)
#     docText = inDoc.readDocument()
#     docErr = inDoc.getError()
#     if docText is None and docErr:
#         self.mainGui.makeAlert([
#             self.tr("Failed to open document file."), docErr
#         ], nwAlert.ERROR)
#     if docText:
#         theText += docText.rstrip("\n")+"\n\n"

# if self.sourceItem is None:
#     self.mainGui.makeAlert(self.tr(
#         "No source folder selected. Nothing to do."
#     ), nwAlert.ERROR)
#     return False

# srcItem = self.theProject.tree[self.sourceItem]
# if srcItem is None:
#     self.mainGui.makeAlert(self.tr("Internal error."), nwAlert.ERROR)
#     return False

# nHandle = self.theProject.newFile(srcItem.itemName, srcItem.itemParent)
# newItem = self.theProject.tree[nHandle]
# newItem.setStatus(srcItem.itemStatus)
# newItem.setImport(srcItem.itemImport)

# outDoc = NWDoc(self.theProject, nHandle)
# if not outDoc.writeDocument(theText):
#     self.mainGui.makeAlert([
#         self.tr("Could not save document."), outDoc.getError()
#     ], nwAlert.ERROR)
#     return False

# self.mainGui.projView.revealNewTreeItem(nHandle)
# self.mainGui.openDocument(nHandle, doScroll=True)

# self._doClose()


class DocMerger:

    def __init__(self, theProject):

        self.theProject = theProject

        self._targetDoc = None

        return

    def setTargetDoc(self, tHandle):
        return

    def createNewDoc(self, docLabel, pHandle, itemLayout):
        return

    def appendDoc(self, tHandle):
        return

# END Class DocMerger
