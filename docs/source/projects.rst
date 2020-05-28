**************
Novel Projects
**************

A novelWriter project requires a dedicated folder for storing its files on the local file system.
See the Technical Information section for further details.

A new project can be created from the Project menu by selecting :menuselection:`Project --> New Project`.
A list of recently opened projects is maintained, and displayed in the "Open Project" dialog.

The project specific settings are available in :menuselection:`Project --> Project Settings`.
See further details below.

Project Structure
=================

Projects are structured into a set of root folders, visible in the left side tree view panel.

The core novel files go into a root folder of type "Novel".
Other supporting files go into root folders of types "Plot", "Characters", "Locations", "Timeline", "Objects", "Entities" or "Custom".
These other root folder types are intended for your notes on the various elements of your story.
Using these is of course entirely optional.
A new project will not have all of the root folders present, but you can add the ones you want from :menuselection:`Project --> Create Root Folder`.

The root folders are intended for the following use, but aside from the Novel folder, no restrictions apply.
You can use them however you want.
The root folders correspond to the categories of tags that can be used.
See the "Project Structure" section for further details.

* **Novel:** The root folder of all text that goes into the final novel.
  This class of files have other rules and features than other files in the project.
  See the Novel Structure section for more details.
* **Plot:** This is the root folder where main plots can be outlined.
  It is optional, but adding at least dummy files can be useful in order to tag plot elements for the Outline View.
* **Characters:** Character files go in this root folder.
  These are especially important if one wants to use the Outline View to see which character appears where, and which part of the story is told from a specific character's point-of-view.
* **Locations:** Location is for various scene locations that one wants to track.
* **Timeline:** If the story jumps in time within the same plot, this class of files can be used to track this.
* **Objects:** Important objects in the story can be tracked here.
* **Entities:** Entities, like organisations or companies, that are part of the plot, can be organised here.
* **Custom:** The custom root folder can be used for tracking anything else not covered by the above options.

Deleted files will be moved into a special "Trash" root folder.
Files in the Trash folder can be deleted permanently.

Orphaned Documents
------------------

In the event the editor crashes or otherwise exits without saving the project state, files that have been added to the project tree and are saved to disk will appear in a special "Orphaned Items" root folder next time the application is started.
These orphaned files will not have any meta data associated with them, although novelWriter will try to restore the file label it had in the project tree. Other information will have to be set again, and the files moved back to the correct location in the project.

Project Lockfile
----------------

To prevent orphaned files caused by file conflicts when novelWriter projects are synced with file synchronisation tools, a project lockfile is written to the project folder.
If you try to open a project which has such a file, you will be presented with a warning, and some information about where the project is potentially open.
You will be give the option to ignore this warning, and continue opening the project.
However, if multiple instances are in fact editing the same project, you are likely to cause inconsistencies and create diverging project files.

.. note::
   If, for some reason, novelWriter crashes, the lock file may remain. If so, it is safe to ignore the lock file warning when re-opening the project.

Using Folders in the Project Tree
---------------------------------

Folders, aside from root folders, have no structural significance to the project.
They are there purely as a way for the user to organise the files in meaningful sections and to be able to close them in the tree view.
When processing the files in the novel, like for instance during export, the folders are ignored.

Project Settings
================

The project settings can be accessed from the :menuselection:`Project --> Project Settings` menu entry.
This will open a dialog box, with a set of tabs.

Settings Tab
------------

The Settings tab holds the project title and author settings.
Working Title can be set to a different title than the Book Title.
The difference between them is simply that the Working Title is used for the GUI (main window title) and for generating the backup files.
The intention is that the working title should remain unchanged, while changing the final title has no effect on features relying on the project name.
The Book Title is currently not ues for anything, so setting it is just for the benefit of the author.

The Book Authors text box takes one author per line.

Status Tab
----------

Each file of type "Novel" can be given a status level, signified by a coloured icon.
These are purely there for the user's convenience, and you are not required to use them for any other feature to work.
The intention is to use this list to set what stage of writing you are on, although you can in principle make them whatever you want.

.. note::
   The status levels currently in use by a file cannot be deleted.

Importance Tab
--------------

Each file of types "Plot", "Character", "World", "Timeline", "Object", "Entity", or "Custom", can be given an importance level, signified by a coloured icon like for status level.
These are also purely there for the user's convenience, and you are not required to use them for any other feature to work.
The intention is to use this list to set how important the character, plot element, or otherwise, is for the story.
Again, these can in principle be used for whatever you want.

.. note::
   The importance levels currently in use by a file cannot be deleted.

Auto-Replace Tab
----------------

A set of automatically replaced keywords can be added in this tab.
The keywords in the left column wile be replaced by the text in the right column when documents are opened in the viewer.
This will also be applied to exports when the feature is added.

Note that a keyword cannot contain any spaces.
The angle brackets are added by default, and when used in the text are a part of the keyword to be replaced.
This is to ensure that parts of the text isn't unintentionally replaced by the content of the list.

Writing Files
=============

New document files can be created from the Document menu, or by pressing :kbd:`Ctrl-N` while in the tree view pane.
This will create a new, empty file, and open the item settings dialog where the filename and various other settings can be set.
This dialog can also be opened again later from either the menu, :menuselection:`Project -> Edit` item, or by pressing :kbd:`Ctrl-E` or :kbd:`F2` with the item selected.

The layout of the file is also defined here.
For Novel files, the full list of layout options are available.
For non-Novel files, only "Note" is available.

See the Project Structure section for more details.

Backup
======

An automatic backup system is built into novelWriter.
In order to use it, a backup path to where the backups are to be stored needs to be provided in :menuselection:`Tools --> Preferences`.
Backups can be run automatically when a project is closed, which also implies it is run when the application is closed.
Backups are date stamped zip files of the entire project folder, and are stored in a subfolder of the backup path with the same name as the project working title set in Project Settings.

The backup feature, when configured, can also be run manually from the :menuselection:`Tools` menu.
It is also possible to dissable automated backup for a given project in Project Settings.

.. note::
   For the backup to be able to run, the Working Title must be set in Project Settings.
   This value is used to generate the folder name for the zip files.
