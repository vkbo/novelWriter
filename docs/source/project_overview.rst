.. _a_proj:

**************
Novel Projects
**************

New projects can be created from the :guilabel:`Project` menu by selecting :guilabel:`New Project`.
This will open the :guilabel:`New Project Wizard` that will assist you in creating a barebone
project suited to your needs. A novelWriter project requires a dedicated folder for storing its
files on the local file system. See :ref:`a_storage` for further details on how files are
organised.

A list of recently opened projects is maintained, and displayed in the :guilabel:`Open Project`
dialog. A project can be removed from this list by selecting it and pressing the :kbd:`Del` key or
by clicking the :guilabel:`Remove` button.

Project-specific settings are available in :guilabel:`Project Settings` in the :guilabel:`Project`
menu. See further details below in the :ref:`a_proj_settings` section. Details about the project,
including word counts, and a table of contents with word and page counts, is available through the
:guilabel:`Project Details` dialog.


.. _a_proj_roots:

Project Roots
=============

Projects are structured into a set of top level folders called "Root Folders". They are visible in
the project tree at the left side of the main window.

The novel documents go into a root folder of type :guilabel:`Novel`. Project notes go into the
other root folders. These other root folder types are intended for your notes on the various
elements of your story. Using them is of course entirely optional.

A new project may not have all of the root folders present, but you can add the ones you want from
:guilabel:`Create Root Folder` in the :guilabel:`Project` menu.

Each root folder has one or more reference keyword associated with it that can be used to reference
content in your notes from other documents and notes. The intended usage of each type of root
folder is listed below. However, aside from the :guilabel:`Novel` folder, no restrictions are
applied by the application. You can use them however you want.

:guilabel:`Novel`
   This is the root folder of all text that goes into the final novel. This class of documents have
   other rules and features than other documents in the project. See :ref:`a_struct` for more
   details.

:guilabel:`Plot`
   This is the root folder where main plots can be outlined. It is optional, but adding at least
   brief notes can be useful in order to tag plot elements for the Outline view. Tags in this
   folder can be references using the ``@plot`` keyword.

:guilabel:`Characters`
   Character notes go in this root folder. These are especially important if one wants to use the
   Outline view to see which character appears where, and which part of the story is told from a
   specific character's point-of-view or focusing on a particular character's storyline. Tags in
   this folder can be referenced using the ``@pov`` keyword for point-of-view characters,
   ``@focus`` for a focus character, or the ``@char`` keyword for any other characters.

:guilabel:`Locations`
   The locations folder is for various scene locations that you want to track. Tags in this folder
   can be references using the ``@location`` keyword.

:guilabel:`Timeline`
   If the story has multiple plot timelines or jumps in time within the same plot, this class of
   notes can be used to track this. Tags in this folder can be references using the ``@time``
   keyword.

:guilabel:`Objects`
   Important objects in the story, for instance important objects that change hands often, can be
   tracked here. Tags in this folder can be references using the ``@object`` keyword.

:guilabel:`Entities`
   Does your plot have many powerful organisations or companies? Or other entities that are part of
   the plot? They can be organised here. Tags in this folder can be references using the
   ``@entity`` keyword.

:guilabel:`Custom`
   The custom root folder can be used for tracking anything else not covered by the above options.
   Tags in this folder can be references using the ``@custom`` keyword.

The root folders correspond to the categories of tags that can be used to reference them. For more
information about the tags listed, see :ref:`a_struct_tags`.

.. tip::
   You can rename root folders to whatever you want. However, this doesn't change the reference
   keyword.


.. _a_proj_roots_del:

Deleted Documents
-----------------

Deleted documents will be moved into a special :guilabel:`Trash` root folder. Documents in the
trash folder can then be deleted permanently, either individually, or by emptying the trash from
the menu. Documents in the trash folder are removed from the project index and cannot be
referenced.

Folders and root folders can only be deleted when they are empty. Recursive deletion is not
supported. A document or a folder can be deleted from the :guilabel:`Project` menu, or by pressing
:kbd:`Ctrl`:kbd:`Shift`:kbd:`Del`.


.. _a_proj_roots_out:

Archived Documents
------------------

If you don't want to delete a document, or put it in the :guilabel:`Trash` folder where it may be
deleted, but still want it out of your main project tree, you can create an :guilabel:`Archive`
root folder from the :guilabel:`Project` menu. You are not allowed to move entire folders to this
root folder, only documents. If you need folders in it to organise your documents, you can of
course create new ones there.

You can drag any document to this folder and preserve its settings. The document will always be
excluded from the :guilabel:`Build Novel Project` builds. It is also removed from the project
index, so the tags and references defined in it will not show up anywhere else.


.. _a_proj_roots_orph:

Recovered Documents
-------------------

If novelWriter crashes or otherwise exits without saving the project state, or if you're using a
file synchronisation tool that runs out of sync, there may be files in the project folder that
aren't tracked in the core project file. These files, when discovered, are recovered and added back
into the project if possible.

The discovered files are scanned for meta information that give clues as to where the document may
previously have been located in the project. The project loading routines will try to put them back
as close as possible to this location, if it still exists. Generally, it will be appended to the
end of the folder where it previously was located. If that folder doesn't exist, it will try to add
it to the correct root folder. If it cannot figure out which root folder is correct, the document
will be added to the :guilabel:`Novel` root folder. Only if the :guilabel:`Novel` folder is
missing will it give up.

If the title of the document can be recovered, the word "Recovered:" will be added as a prefix. If
the title cannot be determined, the document will be named "Recovered File N" where N is a
sequential number.


.. _a_proj_roots_lock:

Project Lockfile
----------------

To prevent lost documents caused by file conflicts when novelWriter projects are synced with file
synchronisation tools, a project lockfile is written to the project folder. If you try to open a
project which has such a file present, you will be presented with a warning, and some information
about where else novelWriter thinks the project is also open. You will be give the option to ignore
this warning, and continue opening the project at your own risk.

.. note::
   If, for some reason, novelWriter crashes, the lock file may remain even if there are no other
   instances keeping the project open. In such a case it is safe to ignore the lock file warning
   when re-opening the project.

.. warning::
   If you choose to ignore the warning and continue opening the project, and multiple instances of
   the project are in fact open, you are likely to cause inconsistencies and create diverging
   project files, potentially resulting in loss of data and orphaned files. You are not likely to
   lose any actual text unless both instances have the same document open in the editor, and
   novelWriter will try to resolve inconsistencies the next time you open the project.


.. _a_proj_roots_dirs:

Using Folders in the Project Tree
---------------------------------

Folders, aside from root folders, have no structural significance to the project. When novelWriter
is processing the documents in the novel, like for instance during export, these folders are
ignored. Only the order of the documents themselves matter.

The folders are there purely as a way for the user to organise the documents in meaningful sections
and to be able to collapse and hide them in the project tree when you're not working on those
documents.

.. tip::
   You can use folders to sort your scene documents into chapters. You will still need to add a
   chapter document as the first item of your chapter folder, and the scene documents as the
   following items. Other ways to use folders is to make a folder for each act or part.


.. _a_proj_files:

Project Documents
=================

New documents can be created from the :guilabel:`Document` menu, or by pressing :kbd:`Ctrl`:kbd:`N`
while in the project tree. This will create a new, empty document, and open the :guilabel:`Item
Settings` dialog where the document label and various other settings can be changed. This dialog
can also be opened again later from either the :guilabel:`Project` menu, selecting :guilabel:`Edit
Project Item`, or by pressing :kbd:`F2` with the item selected.

The layout of the document is also defined here. The two options available are :guilabel:`Novel
Document` and :guilabel:`Project Note`. These behave differently when the project is built. A
project note is never treated as part of the novel, no matter where in the project it is located.
See :ref:`a_struct_layout` for more details.

You can also select whether the document is by default included when building the project. This
setting can be overridden in the :guilabel:`Build Novel Project` tool if you wish to include them
anyway. This is covered in the :ref:`a_export_files` section. You can also toggle the included
state of a document from the right-click context menu.


.. _a_proj_files_counts:

Word Counts
-----------

A character, word and paragraph count is maintained for each document, as well as for each section
of a document following a header. The word count, and change of words in the current session, is
displayed in the footer of any document open in the editor, and all stats are shown in the details
panel below the project tree for any document selected in the project or novel tree.

The word counts are not updated in real time, but run in the background every few seconds for as
long as the document is being actively edited.

A total project word count is displayed in the status bar. The total count depends on the sum of
the values in the project tree, which again depend on an up to date index. If the counts seem
wrong, a full project word recount can be initiated by rebuilding the project's index. Either form
the :guilabel:`Tools` menu, or by pressing :kbd:`F9`.


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
Title` should remain unchanged throughout the project, otherwise the name of exported files and
backup files may change too.

The :guilabel:`Book Title` and :guilabel:`Book Authors` settings are currently not used for
anything, so setting them is just for the benefit of the author. Future features may use them, and
they are exported on some export formats in the :guilabel:`Build Novel Project` tool.

If your project is in a different language than your main spell checking is set to, you can
override the default spell checking language here. You can also override the automatic backup
setting.


Status and Importance Tabs
--------------------------

Each document or folder of type :guilabel:`Novel` can be given a status level, signified by a
coloured icon, and each document or folder of the remaining types can be given an importance level.
These are colour coded icons and labels that can be applied to each document or folder.

These are purely there for the user's convenience, and you are not required to use them for any
other features to work. No other part of novelWriter accesses this information. The intention is to
use these to indicate at what stage of completion each novel document is, or how important the
content of a note is to the plot. You don't have to use them this way, that's just what they were
intended for, but you can make them whatever you want.

See also :ref:`a_ui_tree_status`.

.. note::
   The status or importance level currently in use by one or more documents cannot be deleted, but
   they can be edited.


Auto-Replace Tab
----------------

A set of automatically replaced keywords can be added in this tab. The keywords in the left column
will be replaced by the text in the right column when documents are opened in the viewer. They will
also be applied to exports.

The auto-replace feature will replace text in angle brackets that are in this list. The syntax
highlighter will add an alternate colour to text marching the syntax, but it doesn't check if the
text is in this list.

.. note::
   A keyword cannot contain spaces. The angle brackets are added by default, and when used in the
   text are a part of the keyword to be replaced. This is to ensure that parts of the text aren't
   unintentionally replaced by the content of the list.


.. _a_proj_backup:

Backup
======

An automatic backup system is built into novelWriter. In order to use it, a backup path to where
the backup files are to be stored must be provided in :guilabel:`Preferences`.

Backups can be run automatically when a project is closed, which also implies it is run when the
application itself is closed. Backups are date stamped zip files of the entire project folder, and
are stored in a subfolder of the backup path. The subfolder will have the same name as the project
:guilabel:`Working Title` set in :ref:`a_proj_settings`.

The backup feature, when configured, can also be run manually from the :guilabel:`Tools` menu.
It is also possible to disable automated backups for a given project in :guilabel:`Project
Settings`.

.. note::
   For the backup to be able to run, the :guilabel:`Working Title` must be set in
   :guilabel:`Project Settings`. This value is used to generate the folder name for the zip files.
   Without it, the backup will not run at all, but it will produce a warning message.


.. _a_proj_stats:

Writing Statistics
==================

When you work on a project, a log file records when you opened it, when you closed it, and the
total word counts of your novel documents and notes at the end of the session. You can view this
file in the ``meta`` folder in the directory where you saved your project. The file is named
``sessionStats.log``.

A tool to view the content of this file is available in the :guilabel:`Tools` menu under
:guilabel:`Writing Statistics`. You can also launch it by pressing :kbd:`F6`.

The tool will show a list of all your sessions, and a set of filters to apply to the data. You can
also export the filtered data to a JSON file or to a CSV file that can be opened by a spreadsheet
application like for instance Libre Office Calc.

As of version 1.2, the log file also stores how much of the session time was spent idle. The
definition of idle here is that the novelWriter main window loses focus, or the user hasn't made
any changes to the currently open document in five minutes. The number of minutes can be altered in
:guilabel:`Preferences`.
