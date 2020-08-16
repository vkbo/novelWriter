.. _a_proj:

**************
Novel Projects
**************

A novelWriter project requires a dedicated folder for storing its files on the local file system.
See the :ref:`a_tech` page for further details on how files are organised.

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

The core novel files go into a root folder of type :guilabel:`Novel`. Other supporting files go into
the other root folders. These other root folder types are intended for your notes on the various
elements of your story. Using these is of course entirely optional.

A new project will not have all of the root folders present, but you can add the ones you want from
:guilabel:`Create Root Folder` in the :guilabel:`Project` menu.

The root folders are intended for the following use, but aside from the :guilabel:`Novel` folder, no
restrictions are enforced by the application. You can use them however you want.

:guilabel:`Novel`
   This is the root folder of all text that goes into the final novel. This class of files have
   other rules and features than other files in the project. See the :ref:`a_struct` page for more
   details.

:guilabel:`Plot`
   This is the root folder where main plots can be outlined. It is optional, but adding at least
   dummy files can be useful in order to tag plot elements for the Outline view. Tags in this folder
   can be references using the ``@plot`` keyword.

:guilabel:`Characters`
   Character files go in this root folder. These are especially important if one wants to use the
   Outline view to see which character appears where, and which part of the story is told from a
   specific character's point-of-view. Tags in this folder can be references using the ``@pov``
   keyword for point-of-view characters, or the ``@char`` keyword for other characters.

:guilabel:`Locations`
   The locations folder is for various scene locations that you want to track. Tags in this folder
   can be references using the ``@location`` keyword.

:guilabel:`Timeline`
   If the story has multiple plot timelines or jumps in time within the same plot, this class of
   files can be used to track this. Tags in this folder can be references using the ``@time``
   keyword.

:guilabel:`Objects`
   Important objects in the story, for instance important objects that change hands often, can be
   tracked here. Tags in this folder can be references using the ``@object`` keyword.

:guilabel:`Entities`
   Does your plot have many powerful organisations or companies? Or other entities that are part of
   the plot? They can be organised here. Tags in this folder can be references using the ``@entity``
   keyword.

:guilabel:`Custom`
   The custom root folder can be used for tracking anything else not covered by the above options.
   Tags in this folder can be references using the ``@custom`` keyword.

The root folders correspond to the categories of tags that can be used to reference them. For more
information about the tags listed, see :ref:`a_struct_tags`.

.. tip::
   You can rename root folders to whatever you want. The first character in the :guilabel:`Flags`
   column will still indicate what type they are, and so will the icon if you are using one of the
   Typicons icon sets.


.. _a_proj_roots_del:

Deleted Documents
-----------------

Deleted document files will be moved into a special :guilabel:`Trash` root folder. Files in the
trash folder can then be deleted permanently, either individually, or by emptying the trash from the
menu. Files in this folder are removed from the project index and cannot be referenced.

Folders and root folders can only be deleted when they are empty. Recursive deletion is not
supported. A document file or a folder can be deleted from the :guilabel:`project` menu, or by
pressing :kbd:`Ctrl`:kbd:`Del`.


.. _a_proj_roots_out:

Archived Documents (Outtakes)
-----------------------------

If you don't want to delete a file, or put it in the :guilabel:`Trash` folder where it may be
deleted, but still want it out of your main project tree, you can create an :guilabel:`Outtakes`
root folder from the :guilabel:`Project` menu. You are not allowed to move folders to this root
folder, only files. If you need folders in it to organise your files, you can of course create new
ones there.

You can drag any file to this folder and preserve its settings. The file will always be excluded
from the :guilabel:`Build Novel Project` builds. The file is also removed from the project index, so
the tags and references defined in it will not show up anywhere else.


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
again, and the files moved back to the correct location in the project tree.


.. _a_proj_roots_lock:

Project Lockfile
----------------

To prevent orphaned files caused by file conflicts when novelWriter projects are synced with file
synchronisation tools, a project lockfile is written to the project folder. If you try to open a
project which has such a file present, you will be presented with a warning, and some information
about where else novelWriter thinks the project is also open. You will be give the option to ignore
this warning, and continue opening the project.

.. note::
   If, for some reason, novelWriter crashes, the lock file may remain even if there are no other
   instances keeping the project open. In such a case it is safe to ignore the lock file warning
   when re-opening the project.

.. warning::
   If you choose to ignore the warning and continue opening the project, and multiple instances of
   the project are in fact open, you are likely to cause inconsistencies and create diverging
   project files, potentially resulting in loss of data and orphaned files.


.. _a_proj_roots_dirs:

Using Folders in the Project Tree
---------------------------------

Folders, aside from root folders, have no structural significance to the project. When novelWriter
is processing the files in the novel, like for instance during export, these folders are ignored.
Only the order of the document files themselves matter.

The folders are there purely as a way for the user to organise the files in meaningful sections and
to be able to collapse and hide them in the project tree when you're not working on those files.

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
This is covered in the :ref:`a_export_files` section.


.. _a_proj_files_counts:

Word Counts
-----------

A character, word and paragraph count is maintained for each file, as well as dor each section of a
file defined by a header. The word count, and change of words in the current session, is displayed
in the footer of any document open in the editor, and all stats are shown in the details panel below
the project tree for any file selected.

The word counts are not updated in real time, but runs in the background every five seconds for as
long as the document is being actively edited.

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

The :guilabel:`Settings` tab holds the project title and author settings.

The :guilabel:`Working Title` can be set to a different title than the :guilabel:`Book Title`. The
difference between them is simply that the :guilabel:`Working Title` is used for the GUI (main
window title) and for generating the backup files. The intention is that the :guilabel:`Working
Title` should remain unchanged throughput the project, otherwise the name of exported files and
backup files may change too.

The :guilabel:`Book Title` and :guilabel:`Book Authors` settings are currently not used for
anything, so setting then is just for the benefit of the author. Future, planned features will be
using them, and they are exported on some export formats in the :guilabel:`Build Novel Project`
tool.


Details Tab
-----------

This tab presents an overview of meta data for the project. It states where on your file system the
project is saved, how may times it has been saved, how many folders and files it contains, and how
many words exist in the entire project.


Status and Importance Tabs
--------------------------

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
backup files are to be stored must to be provided in :guilabel:`Preferences`.

Backups can be run automatically when a project is closed, which also implies it is run when the
application is closed. Backups are date stamped zip files of the entire project folder, and are
stored in a subfolder of the backup path with the same name as the project :guilabel:`Working Title`
set in :ref:`a_proj_settings`.

The backup feature, when configured, can also be run manually from the :guilabel:`Tools` menu.
It is also possible to dissable automated backup for a given project in :guilabel:`Project
Settings`.

.. note::
   For the backup to be able to run, the :guilabel:`Working Title` must be set in :guilabel:`Project
   Settings`. This value is used to generate the folder name for the zip files. Without it, the
   backup will not run at all, but produce a warning message.

.. _a_proj_stats:

Writing Statistics
==================

When you work on your project, a log file records when you opened it, when you closed it, and how
many words you added to your novel and note files during the session. You can view this file in the
``meta`` folder in the directory where you saved your project. The file is named
``sessionStats.log``.

A small tool to view the content of this file is available in the :guilabel:`Tools` menu under
:guilabel:`Writing Statistics`. You can also launch it by pressing :kbd:`F6`.

The tool will show a list of all your sessions, and a set of filters to apply to it. You can also
export the filtered data to a JSON file or to a CSV file that can be opened by a spreadsheet
application like for instance Libre Office Calc.
