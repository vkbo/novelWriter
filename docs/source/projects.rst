.. _a_proj:

**************
Novel Projects
**************

A novelWriter project requires a dedicated folder for storing its files on the local file system.
See the :ref:`a_tech` page for further details.

A new project can be created from the :guilabel:`Project` menu by selecting :guilabel:`New Project`.
A list of recently opened projects is maintained, and displayed in the :guilabel:`Open Project`
dialog. A project can be removed from this list by selecting it and pressing the :kbd:`Del` key.

The project specific settings are available in :guilabel:`Project Settings` in the
:guilabel:`Project` menu. See further details below in the :ref:`a_proj_settings` section.


.. _a_proj_roots:

Project Roots
=============

Projects are structured into a set of top level folders called *root folders*. They are visible in
the project tree at the left side of the main window.

The core novel files go into a root folder of type "Novel". Other supporting files go into the other
root folders. These other root folder types are intended for your notes on the various elements of
your story. Using these is of course entirely optional.

A new project will not have all of the root folders present, but you can add the ones you want from
:guilabel:`Create Root Folder` in the :guilabel:`Project` menu.

The root folders are intended for the following use, but aside from the Novel folder, no
restrictions are enforced by the application. You can use them however you want.

.. note::
   The root folders correspond to the categories of tags that can be used.
   See the :ref:`a_struct` page for further details.

Novel
   This is the root folder of all text that goes into the final novel. This class of files have
   other rules and features than other files in the project. See the :ref:`a_struct` page for more
   details.

Plot
   This is the root folder where main plots can be outlined. It is optional, but adding at least
   dummy files can be useful in order to tag plot elements for the Outline View. Tags in this folder
   can be references using the ``@plot`` keyword.

Characters
   Character files go in this root folder. These are especially important if one wants to use the
   Outline View to see which character appears where, and which part of the story is told from a
   specific character's point-of-view. Tags in this folder can be references using the ``@pov``
   keyword for point-of-view characters, or the ``@char`` keyword for other characters.

Locations
   The locations folder is for various scene locations that you want to track. Tags in this folder
   can be references using the ``@location`` keyword.

Timeline
   If the story has multiple plot timelines or jumps in time within the same plot, this class of
   files can be used to track this. Tags in this folder can be references using the ``@time``
   keyword.

Objects
   Important objects in the story, for instance important objects that change hands often, can be
   tracked here. Tags in this folder can be references using the ``@object`` keyword.

Entities
   Does your plot have many powerful organisations or companies? Or other entities that are part of
   the plot? They can be organised here. Tags in this folder can be references using the ``@entity``
   keyword.

Custom
   The custom root folder can be used for tracking anything else not covered by the above options.
   Tags in this folder can be references using the ``@custom`` keyword.

For more information about the tags listed, see :ref:`a_struct_tags`.

.. note::
   Deleted files will be moved into a special :guilabel`Trash` root folder. Files in the trash
   folder can then be deleted permanently, either individually, or by emptying the trash from the
   menu.


.. _a_proj_roots_orph:

Orphaned Documents
------------------

If novelWriter crashes or otherwise exits without saving the project state, or if you're using a
file synchronisation tool that runs out of sync, there may be files in the project folder that isn't
tracked in the core project file. These files, when discovered, are handled by the Orphaned
Documents routine.

Files that are discovered in the project folder, but not in the project, will be re-added to the
project tree in a special :guilabel:`Orphaned Items` root folder next time the application is
started. These orphaned files will not have most of the meta data preserved, although novelWriter
will try to restore the file label it had in the project tree. Other information will have to be set
again, and the files moved back to the correct location in the project.


.. _a_proj_roots_lock:

Project Lockfile
----------------

To prevent orphaned files caused by file conflicts when novelWriter projects are synced with file
synchronisation tools, a project lockfile is written to the project folder. If you try to open a
project which has such a file, you will be presented with a warning, and some information about
where else novelWriter thinks the project is also open.

You will be give the option to ignore this warning, and continue opening the project. However, if
multiple instances are in fact editing the same project, you are likely to cause inconsistencies and
create diverging project files, potentially resulting in loss of data and orphaned files.

.. note::
   If, for some reason, novelWriter crashes, the lock file may remain even if there are no other
   instances keeping the project open. In such a case it is safe to ignore the lock file warning
   when re-opening the project.


.. _a_proj_roots_dirs:

Using Folders in the Project Tree
---------------------------------

Folders, aside from root folders, have no structural significance to the project. When novelWriter
is processing the files in the novel, like for instance during export, these folders are ignored.
Only the order of the text files themselves matter.

The folders are there purely as a way for the user to organise the files in meaningful sections and
to be able to close them in the Project Tree when you're not working on those files, and thus reduce
clutter.

.. tip::
   You can use folders to sort your scene files into chapters. You will then need to add a chapter
   file as the first file of your folder, and the scene files as the following files.


.. _a_proj_files:

Project Files
=============

New document files can be created from the :guilabel:`Document` menu, or by pressing
:kbd:`Ctrl`:kbd:`N` while in the Project Tree. This will create a new, empty file, and open the
:guilabel:`:Item Settings` dialog where the filename and various other settings can be changed.
This dialog can also be opened again later from either the :guilabel:`Project` menu, selecting
:guilabel:`Edit Item`, or by pressing :kbd:`Ctrl`:kbd:`E` or :kbd:`F2` with the item selected.

The layout of the file is also defined here. For Novel files, the full list of layout options are
available. For non-Novel files, only "Note" is available. See :ref:`a_struct_layout` for more
details.

You can also select whether the file is by default included when building the project. This setting
can be overridden in the :guilabel:`Build Novel Project` tool if you wish to include them anyway.


.. _a_proj_files_counts:

Word Counts
-----------

A character, word and paragraph count is maintained for each file, as well as dor each section of a
file defined by a header. The word count, and change of words in the current session, is displayed
in the footer of any document open in the editor, and all stats are shown in the details panel below
the project tree for any file selected.

The word counts are not updated in real time, but runs in the background every five seconds.

A total project word count is displayed in the status bar. The total count depends on the sum of the
values in the project tree, which again depend on an up to date index. If the counts seem wrong, a
full project word recount can be initiated by rebuilding the project's index. Either form the
:guilabel:`Tools` menu, or by pressing :kbd:`F9`.


.. _a_proj_settings:

Project Settings
================

The :guilabel:`Project Settings` can be accessed from the :guilabel:`Project` menu, or by pressing
:kbd:`Ctrl`:kbd:`Shift`:kbd:`,`. This will open a dialog box, with a set of tabs.


Settings Tab
------------

The Settings tab holds the project title and author settings.

Working Title can be set to a different title than the Book Title. The difference between them is
simply that the Working Title is used for the GUI (main window title) and for generating the backup
files. The intention is that the working title should remain unchanged throughput the project,
otherwise the name of exported files and backup files may change too.

The Book Title amd Book Authors settings are currently not used for anything, so setting then is
just for the benefit of the author. Future, planned features will be using them, and they are
exported on some export formats in the Build Novel Project tool.


Details Tab
-----------

This tab presents an overview of meta data for the project. It states where on your file system the
project is saved, how may times it has been saved, how many folders and files it contains, and how
many words exist in the entire project.


Status  and Importance Tabs
---------------------------

Each file of type "Novel" can be given a status level, signified by a coloured icon and each file of
the remaining types can be given an importance level. These are colour coded icons and labels that
can be applied to each file.

These are purely there for the user's convenience, and you are not required to use them for any
other feature to work. No other part of novelWriter accesses this information. The intention is to
use these to indicate at what stage of completeion each novel file is, or how important the content
of a note file is to the plot. You don't have to use them this way, that's just what they were
intended for, but you can make them whatever you want.

.. note::
   The status or importance level currently in use by one or more files cannot be deleted, but they
   can be edited.


Auto-Replace Tab
----------------

A set of automatically replaced keywords can be added in this tab. The keywords in the left column
will be replaced by the text in the right column when documents are opened in the viewer. They will
also be applied to exports.

.. note::
   A keyword cannot contain any spaces. The angle brackets are added by default, and when used in
   the text are a part of the keyword to be replaced. This is to ensure that parts of the text isn't
   unintentionally replaced by the content of the list.


.. _a_proj_backup:

Backup
======

An automatic backup system is built into novelWriter. In order to use it, a backup path to where the
backup files are to be stored must to be provided in Preferences.

Backups can be run automatically when a project is closed, which also implies it is run when the
application is closed. Backups are date stamped zip files of the entire project folder, and are
stored in a subfolder of the backup path with the same name as the project :guilabel:`Working Title`
set in :ref:`a_proj_settings`.

The backup feature, when configured, can also be run manually from the :guilabel:`Tools` menu.
It is also possible to dissable automated backup for a given project in :guilabel:`Project Settings`.

.. note::
   For the backup to be able to run, the :guilabel:`Working Title` must be set in :guilabel:`Project
   Settings`. This value is used to generate the folder name for the zip files. Without it, the
   backup will not run at all, but produce a warning message.
