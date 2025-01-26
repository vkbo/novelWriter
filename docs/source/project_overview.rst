.. _a_proj:

*****************
Managing Projects
*****************

Your text in novelWriter is organised into projects. Each project is meant to contain one novel
and associated notes. If you have multiple novels in a series, with the same characters and shared
notes, it is also possible to keep all of them in the same project.

.. _a_proj_new:

Creating Project
================

New projects can be created from the **Project** menu by selecting **Create or Open Project**. This
will open the **Welcome** dialog, where you can select the :guilabel:`New` button that will assist
you in creating a new project. This dialog is also displayed when you start novelWriter.

A novelWriter project requires a dedicated folder for storing its files on the local file system.
If you're interested in the details, you can have a look at the chapter :ref:`a_storage`.

A list of recently opened projects is maintained, and displayed in the **Welcome** dialog. A
project can be removed from this list by selecting it and pressing the :kbd:`Del` key or by
right-clicking it and selecting the **Remove Project** option.

.. figure:: images/fig_welcome.jpg

   The project list (left) and new project form (right) of the :guilabel:`Welcome` dialog.

Project-specific settings are available in **Project Settings** in the **Project** menu. See
further details below in the :ref:`a_proj_settings` section.

Details about the project's novel text, including word counts, and a table of contents with word
and page counts, is available through the **Novel Details** dialog. Statistics about the project
is also available in the **Manuscript Build** tool.


Template Projects
-----------------

From the Welcome dialog you can also create a new from another existing project. If you have a
specific structure you want to use for all your new projects, you can create a dedicated project to
be used as a template, and select to copy an existing project from the :guilabel:"Prefill Project"
option from the **New Project** form.


.. _a_proj_roots:

Project Structure
=================

Projects are structured into a set of top level folders called "Root Folders". They are visible in
the project tree at the left side of the main window.

The :term:`novel documents` go into a root folder of type **Novel**. :term:`Project notes` go into
the other root folders. These other root folder types are intended for your notes on the various
elements of your story. Using them is of course entirely optional.

A new project may not have all of the root folders present, but you can add the ones you want from
the project tree tool bar.

Each root folder has one or more :term:`reference` :term:`keyword` associated with it that is used
to reference them from other documents and notes. The intended usage of each type of root folder is
listed below. However, aside from the **Novel** folder, no restrictions are applied by the
application on what you put in them. You can use them however you want.

The root folder system is closely connected to how the Tags and References system works. For more
details, see the :ref:`a_references` chapter.


Root Folder Types
-----------------

**Novel**
   This is the root folder type for text that goes into the final novel or novels. This class of
   documents have other rules and features than the project notes. See :ref:`a_struct` for more
   details.

**Plot**
   This is the root folder type where main plots can be outlined. It is optional, but adding at
   least brief notes can be useful in order to tag plot elements for the **Outline View**. Tags in
   this folder can be references using the ``@plot`` keyword.

**Characters**
   Character notes go in this root folder type. These are especially important if you want to use
   the **Outline View** to see which character appears where, which part of the story is told from
   a specific character's point-of-view, or focusing on a particular character's storyline.

   The character names can also be inserted into for instance chapter titles when you create your
   manuscript. Tags in this type of folder can be referenced using the ``@pov`` keyword for
   point-of-view characters, ``@focus`` for a focus character, or the ``@char`` keyword for any
   other character present.

**Locations**
   The locations folder type is for various scene locations that you want to track. Tags in this
   folder can be references using the ``@location`` keyword.

**Timeline**
   If the story has multiple plot timelines or jumps in time within the same plot, this folder type
   can be used to track this. Tags in this type of folder can be references using the ``@time``
   keyword.

**Objects**
   Important objects in the story, for instance physical objects that change hands often, can be
   tracked here. Tags in this type of folder can be references using the ``@object`` keyword.

**Entities**
   Does your plot have many powerful organisations or companies? Or other entities that are part of
   the plot? They can be organised here. Tags in this type of folder can be references using the
   ``@entity`` keyword.

**Custom**
   The custom root folder type can be used for tracking anything else not covered by the above
   options. Tags in this folder type can be references using the ``@custom`` keyword.

The root folders are closely tied to the tags and reference system. Each folder type corresponds to
categories of tags that can be used to reference them. For more information about the tags listed,
see :ref:`a_references_references`.

There is also a ``@mention`` keyword that can be used to reference any tag.
See :ref:`a_references_references` for more details.

.. note::

   You can rename root folders to whatever you want. However, this doesn't change the reference
   keyword or what they do.


.. _a_proj_roots_del:

Deleted Documents
-----------------

Deleted documents are moved into a special **Trash** root folder. Documents in the trash folder can
then be deleted permanently, either individually, or by emptying the trash from the menu. Documents
in the trash folder are removed from the :term:`project index` and cannot be referenced.

A document or a folder can be moved to trash from the **Project** menu, or by pressing
:kbd:`Ctrl+Shift+Del`. Root folders can only be removed when they are empty.


.. _a_proj_roots_out:

Archived Documents
------------------

If you don't want to delete a document, or put it in the **Trash** folder where it may be deleted
accidentally, but still want it out of your main project tree, you can create an **Archive** root
folder instead and move it there. It has the same effect as moving it to **Trash**, but it is safe
from deletion.

You can drag any document to this folder and preserve its settings. The document will always be
excluded from the **Build Manuscript** tool. It is also removed from the :term:`project index`, so
the tags and references defined in it will not show up anywhere else.


.. _a_proj_roots_dirs:

Using Folders in the Project Tree
---------------------------------

Regular folders, those that are not root folders, have no structural significance to the project.
When novelWriter is processing the documents in a project, like for instance when you create a
manuscript from it, these folders are ignored. Only the order of the documents themselves matter.

The folders are there purely as a way for you to organise the documents in meaningful sections and
to be able to collapse and hide them in the project tree when you're not working on those
documents.

In addition to using folders. it is also possible to add child documents to other documents. This
is particularly  useful when you create chapters and scenes. If you add separate scene documents,
you should also  add separate chapter documents, even if they only contain a chapter heading. You
can then add scene documents as child items to the chapters.


.. _a_proj_roots_orphaned:

Recovered Documents
-------------------

If novelWriter crashes or otherwise exits without saving the project state, or if you're using a
file synchronisation tool that runs out of sync, there may be files in the project storage folder
that aren't tracked in the core project file. These files, when discovered, are recovered and added
back into the project when a project is opened.

The discovered files are scanned for metadata that give clues as to where the document may
previously have been located in the project. The project loading routine will try to put them back
as close as possible to this location, if it still exists. Generally, it will be appended to the
end of the folder where it previously was located. If that folder doesn't exist, it will try to add
it to the correct root folder type. If it cannot figure out which root folder is correct, the
document will be added to the **Novel** root folder. Finally, if a **Novel** does not exist, one
will be created.

If the title of the document can be recovered, the word "Recovered:" will be added as a prefix to
indicate that it may need further attention. If the title cannot be determined, the document will
be named after its internal key, which is a string of characters and numbers.


.. _a_proj_roots_lock:

Project Lockfile
----------------

To prevent data loss caused by file conflicts when novelWriter projects are synchronised via file
synchronisation tools, a project lockfile is written to the project storage folder when a project
is open. If you try to open a project which already has such a file present, you will be presented
with a warning, and some information about where else novelWriter thinks the project is also open.
You will be given the option to ignore this warning, and continue opening the project at your own
risk.

.. note::

   If, for some reason, novelWriter or your computer crashes, the lock file may remain even if
   there are no other instances keeping the project open. In such a case it is safe to ignore the
   lock file warning when re-opening the project.

.. warning::

   If you choose to ignore the warning and continue opening the project, and multiple instances of
   the project are in fact open, you are likely to cause inconsistencies and create diverging
   project files, potentially resulting in loss of data and orphaned files. You are not likely to
   lose any actual text unless both instances have the same document open in the editor, and
   novelWriter will try to resolve project inconsistencies the next time you open the project.


.. _a_proj_files:

Project Documents
=================

New documents can be created from the toolbar in the project tree, or by pressing :kbd:`Ctrl+N`.
This will open the create new item menu and let you choose between a number of pre-defined
documents and folders. You will be prompted for a label for the new item.

You can always rename an item by selecting **Rename Item** from the **Project** menu, or by
pressing :kbd:`F2` when a document or folder is selected.

Other settings for project documents and folders are available from the context menu that you can
activate by right-clicking on an it in the tree. The **Transform** submenu includes options for
converting, splitting, or merging documents. See :ref:`a_ui_tree_split_merge` for more details on
the latter two.


Document Templates
------------------

If you wish to create template documents to be used when creating new project documents, like for
instance a character note template, you can add a **Templates** root folder to your project. Any
document added to this root folder will show up in the **Add Item** menu in the project tree
toolbar. When selected, a new document is created with its content copied from the chosen template.

.. versionadded:: 2.3


.. _a_proj_files_counts:

Word Counts
-----------

A character, word and paragraph count is maintained for each document, as well as for each section
of a document following a :term:`heading<headings>`. The word count and change of words in the
current session is displayed in the footer of any document open in the editor, and all stats are
shown in the details panel below the project tree for any document selected in the project or novel
trees.

The word counts are not updated in real time, but run in the background every few seconds for as
long as the document is being actively edited.

A total project word count is displayed in the status bar. The total count depends on the sum of
the values in the project tree, which again depend on an up to date :term:`project index`. If the
counts seem wrong, a full project word recount can be initiated by rebuilding the project's index.
Either from the **Tools** menu, or by pressing :kbd:`F9`.

The rules for how the counts are made is covered in more detail in :ref:`a_counting`.


.. _a_proj_settings:

Project Settings
================

The **Project Settings** can be accessed from the **Project** menu, or by pressing
:kbd:`Ctrl+Shift+,`. This will open a dialog box, with a set of tabs.


Settings Tab
------------

The **Settings** tab holds the project name, author, and language settings.

The **Project Name** can be edited here. It is used for the main window title and for generating
backup files. So keep in mind that if you do change this setting, the backup file names will change
too.

You can also change the **Authors** and **Project Language** setting. These are only used when
building the manuscript, for some formats. The language setting is also used when inserting text
into documents in the viewer, like for instance labels for keywords and special comments.

If your project is in a different language than your main spell checking language is set to, you
can override the default setting here. The project language can also be changed from the **Tools**
menu.

You can also override the automatic backup setting for the project if you wish.


Status and Importance Tabs
--------------------------

Each document or folder of type **Novel** can be given a "Status" label accompanied by a coloured
icon with an optional shape selected from a list of pre-defined shapes. Each document or folder of
the remaining types can be given an "Importance" label with the same customisation options.

These labels are there purely for your convenience, and you are not required to use them for any
other features to work. No other part of novelWriter accesses this information. The intention is to
use these to indicate at what stage of completion each novel document is, or how important the
content of a note is to the story. You don't have to use them this way, that's just what they were
intended for, but you can make them whatever you want.

Both status and importance labels can be exported and imported so you can share them between
projects, or define a standard set for all your writing projects. When you import labels to a
project, they are always added as *new* labels.

See also :ref:`a_ui_tree_status`.

.. note::

   The status or importance level currently in use by one or more documents cannot be deleted, but
   they can be edited.


Auto-Replace Tab
----------------

A set of automatically replaced keywords can be added in this tab. The keywords in the left column
will be replaced by the text in the right column when documents are opened in the viewer. They will
also be applied to manuscript builds.

The auto-replace feature will replace text in angle brackets that is in this list. The syntax
highlighter will add an alternate colour to text matching the syntax, but it doesn't check if the
text is in this list.

.. note::
   A keyword cannot contain spaces. The angle brackets are added by default, and when used in the
   text are a part of the keyword to be replaced. This is to ensure that parts of the text aren't
   unintentionally replaced by the content of the list.


.. _a_proj_backup:

Backup
======

An automatic backup system is built into novelWriter. In order to use it, a backup path to where
the backup files are to be stored must be provided in **Preferences**. The path defaults to a
folder named "Backups" in your home directory.

Backups can be run automatically when a project is closed, which also implies it is run when the
application itself is closed. Backups are date stamped zip files of the project files in the
project folder (files not strictly a part of the project are ignored). The zip archives are stored
in a subfolder of the backup path. The subfolder will have the same name as the **Project Name** as
defined in :ref:`a_proj_settings`.

The backup feature, when configured, can also be run manually from the **Tools** menu. It is also
possible to disable automated backups for a given project in **Project Settings**.

.. note::
   For the backup to be able to run, the **Project Name** must be set in **Project Settings**. This
   value is used to generate the name and path of the backups. Without it, the backup will not run
   at all, but it will produce a warning message.


.. _a_proj_stats:

Writing Statistics
==================

When you work on a project, a log file records when you opened it, when you closed it, and the
total word counts of your novel documents and notes at the end of the session, provided that the
session lasted either more than 5 minutes, or that the total word count changed. For more details
about the log file, see :ref:`a_storage`.

A tool to view the content of the log file is available in the **Tools** menu under **Writing
Statistics**. You can also launch it by pressing :kbd:`F6`, or find it on the sidebar.

The tool will show a list of all your sessions, and a set of filters to apply to the data. You can
also export the filtered data to a JSON file or to a CSV file that can be opened by a spreadsheet
application like for instance Libre Office Calc or Excel.

.. versionadded:: 1.2

   As of version 1.2, the log file also stores how much of the session time was spent idle. The
   definition of idle here is that the novelWriter main window loses focus, or the user hasn't made
   any changes to the currently open document in five minutes. The number of minutes can be altered
   in **Preferences**.


Session Timer
-------------

A session timer is by default visible in the status bar. The icon will show you a clock icon when
you are active, and a pause icon when you are considered "idle" per the criteria mentioned above.

If you do not wish to see the timer, you can click on it once to hide it. The icon will still be
visible. Click the icon once more to display the timer again.

.. versionadded:: 2.6

   As of version 2.6, clicking the timer text or icon in the status bar will toggle its visibility.
