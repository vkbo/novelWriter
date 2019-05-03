# ToDo List

## High Priority

**Deleting Files and Folders**

Add a trash root folder that will hold deleted files. The trash folder will have a handle, and this becomes the new parent of the file. In addition, the nwItemType changes to type `TRASHFILE`. Other item settings are retained so that they can easily be restored.

Files in the trash folder can be permanently deleted, which means they must also be removed from the data folder and project XML. Potentially, these files can be moved to a `discarded` folder in the project directory. It is not necessarily a bad idea to never fully delete anything.

Deleting empty folders. This one is straight forward. These do not go to trash. Should probably allow for deleting non-empty folders as well by recursively moving the files to trash.

**File and Project Save**

Autosave is high priority. Both the currently open document and the project XML should be saved on a timer.

Also needed is a check that a file has been altered so the user doesn't open a new document and loses latest changes.

## Medium Priority

**Multiple Views**

Vertical and horizontal split view is very useful. Maybe even as two editors, or one editor + one view. Dual editor panes is preferred, but it requires checking focus before applying key shortcuts. This should be straight forward by reading the Qt keyboard focus widget.

**Editor Enhancements**

Spell checking. Very important.

## Low Priority

**Side Panel**

A side panel with a clickable tree view of the current document layout would be nice. Useful for quick navigation between headers.

A side panel with an overview of the project tags would also be useful. Probably also in a treeview, and grouped by item class. this will also require an XML file to store the tags. Possibly by handle. Each file item should only have one tag, and the tags must be unique. Mapping from other files back to tags may be useful as well, but the tag to handle mapping is essential for quick lookups and generating overview.

## Implemented

**Orphaned File Handling**

Handling of orphaned items. That is, files that are in the data directories, but not in the project XML. This can happen either due to bugs, a crash, or weird things happening to the file system. The orphaned items feature is an easy way to recover files lost from the project. Orphaned items have no meta data, so they are set to `NO_LAYOUT`, `NO_TYPE` and `NO_CLASS`.
