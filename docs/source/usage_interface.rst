.. _a_ui:

***********************
User Interface Overview
***********************

The user interface is kept as simple as possible to avoid distractions when writing. This page
lists all the main GUI elements, and explains what they do.


.. _a_ui_tree:

The Project Tree
================

The main window contains a project tree in the left-most panel. It shows the entire structure of
the project. It has four columns:

**Column 1**
   The first column shows the icon and label of each folder, document, or note in your project. The
   label is not the same as the title you set inside the document. However, the document's label
   will appear in the header above the document text itself so you know where in the project an
   open document belongs.

**Column 2**
   The second column shows the word count of the document, or the sum of words of the child items
   for folders. If the counts seem incorrect, they can be updated by rebuilding the project index
   from the :guilabel:`Tools` menu, or by pressing :kbd:`F9`.

**Column 3**
   The third column indicates whether the document is included in the final project build or not.
   You may want to filter out documents that you no longer want to keep in the final manuscript,
   but want to keep in the project for reference.

**Column 4**
   The fourth column shows the user-defined status or importance labels you've assigned to each
   project item. See :ref:`a_ui_tree_status` for more details.

Right-clicking an item in the project tree will open a context menu under the cursor, displaying
a selection of actions that can be performed on the selected item.

The label, status or importance setting, the layout, and the include flag can all be edited using
the :guilabel:`Item Settings` dialog box. The dialog can be opened from the :guilabel:`Project`
menu, or by pressing :kbd:`F2` with the item selected.

Below the project tree you will find a small details panel showing the full information of the
currently selected item. This panel also includes the latest paragraph and character counts in
addition to the word count.


.. _a_ui_tree_novel:

The Novel Tree
--------------

An alternative way to view the project structure is the novel tree. You can switch to this view by
selecting the :guilabel:`Novel` tab under the project tree. This view is a simplified version of
the view in the :guilabel:`Outline`. It is convenient when you want to browse the structure of the
story itself rather than the document files.

.. note::
   You cannot reorganise the entries in the novel tree, or add any new ones, as that would imply
   restructuring the content of the document files.


.. _a_ui_tree_status:

Document Importance and Status
------------------------------

Each document or folder in your project can have either a "Status" or "Importance" flag set. These
are flags that you control and define yourself. To modify the labels, go to their respective tabs
in :guilabel:`Project Settings`.

The "Status" flag is intended to tag a Novel document as for instance a draft or as completed, and
the "Importance" flag is intended to tag character notes, or other notes, as for instance a main,
major or minor character.

Whether a document uses a "Status" or "Importance" flag depends on which root folder it lives in.
If it's in the :guilabel:`Novel` folder, it uses the "Status" flag, otherwise it uses an
"Importance" flag. Some folders, like :guilabel:`Trash` and :guilabel:`Outtakes` allow both.


.. _a_ui_tree_dnd:

Project Tree Drag & Drop
------------------------

The project tree allows drag & drop to a certain extent. This feature is primarily intended for
reordering your documents within each root folder. Moving a document in the project tree will also
put it in a different place when you build the novel project.

Drag & drop has only limited support for moving documents. In general, bulk actions are not
allowed. This is deliberate to avoid accidentally messing up your project. If you make a mistake,
the last move action can be undone by pressing :kbd:`Ctrl`:kbd:`Shift`:kbd:`Z`.

Documents and their folders can be rearranged freely within their root folders. Novel documents
cannot be moved out of the :guilabel:`Novel` folder, except to :guilabel:`Trash` and the
:guilabel:`Outtakes` folders. Notes can be moved freely between all root folders, but keep in mind
that if you move a note into a :guilabel:`Novel`, its "Importance" setting will be reset to the
default "Status" setting. See :ref:`a_ui_tree_status`.

Folders cannot be moved at all outside their root tree. Neither can a folder containing documents
be deleted. You must first delete the containing documents.

Root folders in the project tree cannot be dragged & dropped at all. If you want to reorder them,
you can move them up or down with respect to eachother from the :guilabel:`Project` menu, the
right-click context menu, or by pressing :kbd:`Ctrl`:kbd:`Shift` and the :kbd:`Up` or :kbd:`Down`
key.


.. _a_ui_edit:

Editing and Viewing Documents
=============================

To edit a document, double-click it in the project tree, or press the :kbd:`Return` key while
having it selected. This will open the document in the document editor. The editor uses a
markdown-like syntax for some features, and a novelWriter-specific syntax for others. The syntax
format is described in the :ref:`a_fmt` section below. The editor has a maximise button (toggles
the :guilabel:`Focus Mode`) and a close button in the top–right corner. On the top–left side you
will find an edit button that opens the :guilabel:`Item Settings` dialog for the currently open
document, and a search button to open the search dialog.

Any document in the project tree can also be viewed in parallel in a right hand side document
viewer. To view a document, press :kbd:`Ctrl`:kbd:`R`, or select :guilabel:`View Document` in the
menu. If you have a middle mouse button, middle-clicking on the document will also open it in the
viewer. The document viewed does not have to be the same document as currently being edited.
However, If you *are* viewing the same document, pressing :kbd:`Ctrl`:kbd:`R` again will update the
document with your latest changes. You can also press the reload button in the top–right corner of
the view panel, next to the close button, to achieve the same thing.

Both the document editor and viewer will show the label of the document in the header at the top of
the edit or view panel. Optionally, the full project path to the document can be shown. This can be
set in :guilabel:`Preferences`. Clicking on the document title bar will select and reveal its
location in the project tree, making it easier to locate in a large project.

Any tag reference in the editor can be opened in the viewer by moving the cursor to the label and
pressing :kbd:`Ctrl`:kbd:`Return`. You can also control-click them with your mouse. In the viewer,
the references become clickable links. Clicking them will replace the content of the viewer with
the content of the document the reference points to.

The document viewer keeps a history of viewed documents, which you can navigate through with the
arrow buttons in the top–left corner of the viewer. If your mouse has back and forward navigation
buttons, these can be used as well. They work just like the backward and forward features in a
browser.

At the bottom of the view panel there is a :guilabel:`References` panel. (If it is hidden, click
the icon to reveal it.) This panel will show links to all documents referring back to the one
you're currently viewing, if any has been defined. The :guilabel:`Sticky` button will freeze the
content of the panel to the current document, even if you navigate to another document. This is
convenient if you want to quickly look through all documents in the list in the
:guilabel:`References` panel without losing the list in the process.

.. note::
   The :guilabel:`References` panel relies on an up-to-date index of the project. The index is
   maintained automatically. However, if anything is missing, or seems wrong, the index can always
   be rebuilt by selecting :guilabel:`Rebuild Index` from the :guilabel:`Tools` menu, or by
   pressing :kbd:`F9`.


.. _a_ui_edit_search:

Search & Replace
----------------

The document editor has a search and replace tool that can be activated with :kbd:`Ctrl`:kbd:`F`
for search mode or :kbd:`Ctrl`:kbd:`H` for search and replace mode.

Pressing :kbd:`Return` while in the search box will search for the next occurrence of the word, and
:kbd:`Shift`:kbd:`Return` for the previous. Pressing :kbd:`Return` in the replace box, will replace
the highlighted text and move to the next result.

There are a number of settings for the search tool available as toggle switches above the search
box. They allows you to search for, in order: matched case only, whole word results only, search
using regular expressions, loop search when reaching the end of the document, and move to the next
document when reaching the end. There is also a switch that will try to match the case of the word
when the replacement is made. That is, it will try to keep the word upper, lower, or capitalised to
match the word being replaced.

The regular expression search is somewhat dependant on which version of Qt your system has. If you
have Qt 5.13 or higher, there is better support for unicode symbols in the search.


.. _a_ui_edit_auto:

Auto-Replace as You Type
========================

A few auto-replace features are supported by the editor. You can control every aspect of the
auto-replace feature from :guilabel:`Preferences`. You can also disable this feature entirely if
you wish.

.. tip::
   If you don't like auto-replacement, all symbols inserted by this feature are also available in
   the :guilabel:`Insert` menu, and via convenient :ref:`a_kb_ins`. You may also be using a
   `Compose Key`_ setup, which means you may not need the auto-replace feature.

.. _Compose Key: https://en.wikipedia.org/wiki/Compose_key

The editor is able to replace two and three hyphens with short and long dashes, triple points with
ellipsis, and replace straight single and double quotes with user-defined quote symbols. It will
also try to determine whether to use the opening or closing symbol, although this feature isn't
always accurate. Especially distinguishing between closing single quote and apostrophe can be
tricky for languages that use the same symbol for these, like English does.

.. tip::
   If the auto-replace feature changes a symbol when you did not want it to change, pressing
   :kbd:`Ctrl`:kbd:`Z` immediately after the auto-replacement will undo it without undoing the
   character you typed.


.. _a_ui_outline:

Project Outline View
====================

The project's Outline view is available as the second tab on the right hand side of the main window
labelled :guilabel:`Outline`. The outline provides an overview of the novel structure, displaying a
tree hierarchy of the elements of the novel, that is, the level 1 to 4 headings representing
partitions, chapters, scenes and sections.

The document containing the heading can also be displayed as a separate column, as well as the line
number where it occurs. Double-clicking an entry will open the corresponding document in the
editor.

.. note::
   Since the internal structure of the novel does not depend directly on the folder and document
   structure of the project tree, these will not necessarily look the same, depending on how you
   choose to organise your documents. See the :ref:`a_struct` page for more details.

Various meta data and information extracted from tags can be displayed in columns in the outline.
A default set of such columns is visible, but you can turn on or off more columns by right clicking
the header and selecting the columns you want to show. The order of the columns can also be
rearranged by dragging them to a different position.

.. note::
   The :guilabel:`Title` column cannot be disabled or moved.

The information viewed in the outline is based on the project's main index. While novelWriter does
its best to keep the index up to date when contents change, you can always rebuild it manually by
pressing :kbd:`F9` if something isn't right.

The outline view itself can be regenerated by pressing :kbd:`F10`. You can also enable automatic
updating in the :guilabel:`Tools` menu, which will trigger an update whenever the index is updated
and the :guilabel:`Outline` tab is active. You may want to disable this feature if your project is
very large,

The :guilabel:`Synopsis` column of the outline view takes its information from a specially
formatted comment. See :ref:`a_fmt_comm`.
