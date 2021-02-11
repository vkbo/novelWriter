.. _a_ui:

**************
User Interface
**************

The user interface is kept as simple as possible to avoid distractions when writing. This page
lists all the main GUI elements, and explains what they do.

.. _a_ui_tree:

The Project Tree
================

The main window contains a project tree in the left-most panel. It shows the entire structure of
the project. It has four columns:

:guilabel:`Label`
   The first column shows the item icon and its label. The labels can be edited from the
   :guilabel:`Project` menu, or by pressing :kbd:`F2` or :kbd:`Ctrl`:kbd:`E`. The label is not the
   same as the title you set inside the document, but it will appear in the header above the
   document text itself.

:guilabel:`Words`
   The second column shows the word count of the document, or the sum of words of the child items
   if it is a folder. If the counts seem incorrect, they can be updated by rebuilding the project
   index from the :guilabel:`Tools` menu, or by pressing :kbd:`F9`.

:guilabel:`Inc`
   The third column indicates whether the document is included in the final project build or not.
   You may want to filter out documents that you no longer want to keep in the final manuscript,
   but want to keep in the project for reference.

:guilabel:`Flags`
   The fourth column shows various meta data flags for the item. The first is an icon indicating
   the importance or status of the document. These are colour coded status levels that you control
   and define yourself. They can be changed in :guilabel:`Project Settings` from the
   :guilabel:`Project` menu. The first character after the icon indicates the class of the item,
   that is ``N`` for **Novel**, ``C`` for **Character**, etc (see :ref:`a_struct_tags`). The
   characters after the dot indicate the document layout type (see :ref:`a_proj_roots`).

Right-clicking an item in the project tree will open a context menu under the cursor, displaying
a selection of actions that can be performed on the selected item.

Below the project tree you will find a small details panel showing the full information of the
currently selected item. This panel also includes the latest paragraph and character counts in
addition to the word count.


.. _a_ui_tree_dnd:

Project Tree Drag and Drop
--------------------------

The project tree allows drag and drop to a certain extent. This feature is primarily intended for
rearranging the order of your documents within each root folder, and has only limited support for
moving documents elsewhere in the project tree. In general, bulk actions are not allowed. This is
deliberate to avoid accidentally messing up your project. The project tree has no undo function.

Documents and their folders can be rearranged freely within their root folders. Novel documents
cannot be moved out of the :guilabel:`Novel` folder, except to :guilabel:`Trash` and the
:guilabel:`Outtakes` folders. Notes can be moved freely between all root folders.

Folders cannot be moved at all outside their root tree. Neither can a folder containing documents
be deleted. You must first delete the containing documents.

Root folders in the project tree cannot be dragged and dropped at all. If you want to reorder them,
you can move them up or down with respect to eachother from the :guilabel:`Tools` menu, the
right-click context menu, or by pressing :kbd:`Ctrl`:kbd:`Shift` and the :kbd:`Up` or :kbd:`Down`
key.


.. _a_ui_edit:

Editing and Viewing Documents
=============================

To edit a document, double-click it in the project tree, or press the :kbd:`Return` key while
having it selected. This will open the document in the document editor. The editor uses a
simplified markdown format. The format is described in the :ref:`a_ui_md` section below. The editor
has a maximise button (toggles the :guilabel:`Distraction Free Mode`) and a close button in the
top-right corner.

Any document in the project tree can also be viewed in parallel in a right hand side document
viewer. To view a document, press :kbd:`Ctrl`:kbd:`R`, or select :guilabel:`View Document` in the
menu. If you have a middle mouse button, middle-clicking on the document will also open it in the
viewer. The document viewed does not have to be the same document currently being edited. However,
If you *are* viewing the same document, pressing :kbd:`Ctrl`:kbd:`R` again will update the document
with your latest changes. You can also press the reload button in the top-right corner of the view
panel next to the close button to achieve the same thing.

Both the document editor and viewer will show the label of the document in the header at the top of
the edit or view panel. Optionally, the full project path to the document can be shown. This can be
set in the :guilabel:`Preferences` dialog from the :guilabel:`Tools` menu. Clicking on the document
title bar will select and reveal its location in the project tree, making it easier to locate in a
large project.

Any tag reference in the editor can be opened in the viewer by moving the cursor to the label and
pressing :kbd:`Ctrl`:kbd:`Return`. You can also control-click them with your mouse. In the viewer,
the references become clickable links. Clicking them will replace the content of the viewer with
the content of the document the reference points to. The document viewer keeps a history of viewed
documents, which you can navigate with the arrow buttons in the top-left corner of the viewer. If
your mouse has back and forward navigation buttons, these can be used as well.

At the bottom of the view panel there is a :guilabel:`References` panel. (If it is hidden, click
the icon to reveal it.) This panel will show links to all documents referring back to it, if any
has been defined. The :guilabel:`Sticky` button will freeze the content of the panel to the current
document, even if you navigate to another document. This is convenient if you want to quickly look
through all documents in the list in the :guilabel:`References` panel without losing the list in
the process.

.. note::
   The :guilabel:`References` panel relies on an up-to-date index of the project. The index is
   maintained automatically. However, if anything is missing, or seems wrong, the index can always
   be rebuilt by selecting :guilabel:`Rebuild Index` from the :guilabel:`Tools` menu, or by
   pressing :kbd:`F9`.


.. _a_ui_edit_auto:

Auto-Replace as You Type
========================

A few auto-replace features are supported by the editor. You can control every aspect of the
auto-replace feature from :guilabel:`Preferences`. You can also disable it entirely.

.. tip::
   If you don't like auto-replacement, all symbols inserted by this feature are also available in
   the :guilabel:`Insert` menu, and via convenient :ref:`a_ui_shortcuts_ins`.

The editor is able to replace two and three hyphens with short and long dashes, triple points with
ellipsis, and replace straight single and double quotes with user-defined quote symbols. It will
also try to determine whether to use the opening or closing symbol, although this feature isn't
always accurate. Especially distinguishing between closing single quote and apostrophe can be
tricky for languages that use the same symbol for these.

.. tip::
   If the auto-replace feature changes a symbol when you did not want it to change, pressing
   :kbd:`Ctrl`:kbd:`Z` immediately after the auto-replacement will undo it without undoing the
   character you typed.


.. _a_ui_md:

Markdown Format
===============

The document editor uses a simplified markdown format. That is, it supports basic formatting like
emphasis (italic), strong importance (bold) and strikethrough text, as well as four levels of
headings.

Some non-standard markdown features have been added. For instance, novelWriter allows for comments,
a synopsis tag, and a set of keyword and value sets used for tags and references.


.. _a_ui_md_head:

Headings
--------

Four levels of headings are allowed. For documents of layout ``Note``, they are free to be used as
you see fit, but for all other layouts used for the novel text itself, they indicate the structural
level of the novel. See :ref:`a_struct_heads` for more details.

``# Title``
   Heading level one. If the document is a novel file, the header level indicates the start of a
   new partition. This heading level can also be used for the title page's novel title.

``## Title``
   Heading level two. If the document is a novel file, the header level indicates the start of a
   new chapter. Chapter numbers can be inserted automatically when exporting the manuscript.

``### Title``
   Heading level three. If the document is a novel file, the header level indicates the start of a
   new scene. Scene numbers or scene separators can be inserted automatically when exporting the
   manuscript, so you can use the title field as a working title for your scenes.

``#### Title``
   Heading level four. If the document is a novel file, the header level indicates the start of a
   new section. Scene titles can be replaced by separators or removed when exporting the
   manuscript, so you can use the title field as a working title for your sections.

.. note::
   The space after the ``#`` characters is mandatory. The syntax highlighter will change colour and
   font size when the heading is correctly formatted.


.. _a_ui_md_emph:

Text Emphasis
-------------

A minimal set of text emphasis styles are supported.

``_text_``
   The text is rendered as emphasised text (italicised).

``**text**``
   The text is rendered as strongly important text (bold).

``~~text~~``
   Strikethrough text.

In markdown guides it is often recommended to differentiate between strong importance and emphasis
by using ``**`` for strong and ``_`` for emphasis, although markdown generally also supports ``__``
for strong and ``*`` for emphasis. However, since the differentiation makes the highlighting and
conversion significantly simpler and faster, in novelWriter this is a rule, not just a
recommendation.

In addition, the following rules apply:

1. The emphasis and strikethrough formatting tags do not allow spaces between the words and the tag
   itself. That is, ``**text**`` is valid, ``**text **`` is not.
2. More generally, the delimiters must be on the outer edge of words. That is, ``some **text in
   bold** here`` is valid, ``some** text in bold** here`` is not.
3. If using both ``**`` and ``_`` to wrap the same text, the underscore must be the inner wrapper.
   This is due to the underscore also being a valid word character, so if they are on the outside,
   they violate rule 2.
4. Text emphasis does not span past line breaks. If you need to add emphasis to multiple lines or
   paragraphs, you must apply it to each of them in turn.


.. _a_ui_md_comm:

Comments and Synopsis
---------------------

In addition to these standard markdown features, novelWriter also allows for comments in documents.
The text of a comment is ignored by the word counter. The text can also be filtered out when
exporting or viewing the document.

If the first word of a comment is ``Synopsis:`` (with the colon), the comment is treated specially
and will show up in the :ref:`a_ui_outline` in a dedicated column. The word ``synopsis`` is not
case sensitive. If it is correctly formatted, the syntax highlighter will indicate this by altering
the colour of the word.

``% text...``
   This is a comment. The text is not exported by default (this can be overridden), seen in the
   Viewer, or counted towards word counts.

``% Synopsis: text...``
   This is a synopsis comment. It is generally treated in the same way as a regular comment, except
   that it is also captured by the indexing algorithm and displayed in the :ref:`a_ui_outline`. It
   can also be filtered separately when exporting the project to for instance generate an outline
   document of the whole project.

.. note::
   Only one comment can be flagged as a synopsis comment for each heading. If multiple comments are
   flagged as synopsis comments, the last one will be used and the rest ignored.


.. _a_ui_md_tags:

Tags and References
-------------------

The document editor supports a minimal set of keywords used for setting tags, and making references
between documents. The tags and references can be set once per section defined by a heading. Using
them multiple times under the same heading will just override the previous setting.

``@keyword: value``
   A keyword argument followed by a value, or a comma separated list of values.

The available tag and reference keywords are listed in the :ref:`a_struct_tags` section. They can
also be inserted at the cursor position in the editor via the :guilabel:`Insert` menu.


.. _a_ui_md_add:

Additional Markdown and Non-Standard Features
---------------------------------------------

The editor and viewer also support markdown standard hard line breaks, and preserves non-breaking
spaces if running with Qt 5.9 or higher. For older versions, the non-breaking spaces are lost when
the document is saved. This is unfortunately hard-coded in the Qt text editor.

* A hard line break can be achieved by leaving two or more spaces at the end of the line. This is
  standard markdown syntax. Alternatively, the user can press :kbd:`Ctrl`:kbd:`K`, :kbd:`Return` to
  insert this type of space.
* A non-breaking space can be inserted with :kbd:`Ctrl`:kbd:`K`, :kbd:`Space`.
* Thin spaces are also supported, and can be inserted with :kbd:`Ctrl`:kbd:`K`,
  :kbd:`Shift`:kbd:`Space`.
* Non-breaking thin space can be inserted  with :kbd:`Ctrl`:kbd:`K`, :kbd:`Ctrl`:kbd:`Space`.

These are all insert features, and the :guilabel:`Insert` menu has more. They are also listed
in :ref:`a_ui_shortcuts_ins`.

Both hard line breaks and non-breaking spaces are highlighted by the syntax highlighter as an
alternate coloured background, depending on the selected theme.


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
its best to keep the index up to date when content changes, you can always rebuild it manually by
pressing :kbd:`F9` if something isn't right.

The outline view itself can be regenerated by pressing :kbd:`F10`. You can also enable automatic
updating in the :guilabel:`Tools` menu, which will trigger an update whenever the index is updated
and the :guilabel:`Outline` tab is active. You may want to disable this feature if your project is
very large,

The :guilabel:`Synopsis` column of the outline view takes its information from a specially
formatted comment. See :ref:`a_ui_md_comm`.


.. _a_ui_shortcuts:

Keyboard Shortcuts
==================

Most features are available as keyboard shortcuts. These are as follows:

.. csv-table:: Keyboard Shortcuts
   :header: "Shortcut", "Description"
   :widths: 30, 70
   :class: "tight-table"

   ":kbd:`Alt`:kbd:`1`",                 "Switch focus to the project tree."
   ":kbd:`Alt`:kbd:`2`",                 "Switch focus to document editor."
   ":kbd:`Alt`:kbd:`3`",                 "Switch focus to document viewer."
   ":kbd:`Alt`:kbd:`4`",                 "Switch focus to outline view."
   ":kbd:`Alt`:kbd:`Left`",              "Move backward in the view history of the document viewer."
   ":kbd:`Alt`:kbd:`Right`",             "Move forward in the view history of the document viewer."
   ":kbd:`Ctrl`:kbd:`.`",                "Open menu to correct word under cursor."
   ":kbd:`Ctrl`:kbd:`,`",                "Open the :guilabel:`Preferences` dialog."
   ":kbd:`Ctrl`:kbd:`/`",                "Change block format to comment."
   ":kbd:`Ctrl`:kbd:`0`",                "Remove block formatting for block under cursor."
   ":kbd:`Ctrl`:kbd:`1`",                "Change block format to header level 1."
   ":kbd:`Ctrl`:kbd:`2`",                "Change block format to header level 2."
   ":kbd:`Ctrl`:kbd:`3`",                "Change block format to header level 3."
   ":kbd:`Ctrl`:kbd:`4`",                "Change block format to header level 4."
   ":kbd:`Ctrl`:kbd:`A`",                "Select all text in the document."
   ":kbd:`Ctrl`:kbd:`B`",                "Format selected text, or word under cursor, with strong emphasis (bold)."
   ":kbd:`Ctrl`:kbd:`C`",                "Copy selected text to clipboard."
   ":kbd:`Ctrl`:kbd:`D`",                "Strikethrough selected text, or word under cursor."
   ":kbd:`Ctrl`:kbd:`E`",                "If in the project tree, edit a document or folder settings. (Same as :kbd:`F2`.)"
   ":kbd:`Ctrl`:kbd:`F`",                "Open the search bar and search for the selected word, if any is selected."
   ":kbd:`Ctrl`:kbd:`G`",                "Find next occurrence of search word in current document. (Same as :kbd:`F3`.)"
   ":kbd:`Ctrl`:kbd:`H`",                "Open the search and replace bar and search for the selected word, if any is selected. (On Mac, this is :kbd:`Cmd`:kbd:`=`.)"
   ":kbd:`Ctrl`:kbd:`I`",                "Format selected text, or word under cursor, with emphasis (italic)."
   ":kbd:`Ctrl`:kbd:`K`",                "Activate the insert commands. The commands are listed in :ref:`a_ui_shortcuts_ins`."
   ":kbd:`Ctrl`:kbd:`N`",                "Create new document."
   ":kbd:`Ctrl`:kbd:`O`",                "Open selected document."
   ":kbd:`Ctrl`:kbd:`Q`",                "Exit novelWriter."
   ":kbd:`Ctrl`:kbd:`R`",                "If in the project tree, open a document for viewing. If the editor has focus, open current document for viewing."
   ":kbd:`Ctrl`:kbd:`S`",                "Save the current document in the document editor."
   ":kbd:`Ctrl`:kbd:`V`",                "Paste text from clipboard to cursor position."
   ":kbd:`Ctrl`:kbd:`W`",                "Close the current document in the document editor."
   ":kbd:`Ctrl`:kbd:`X`",                "Cut selected text to clipboard."
   ":kbd:`Ctrl`:kbd:`Y`",                "Redo latest undo."
   ":kbd:`Ctrl`:kbd:`Z`",                "Undo latest changes."
   ":kbd:`Ctrl`:kbd:`F7`",               "Toggle spell checking."
   ":kbd:`Ctrl`:kbd:`F10`",              "Toggle automatic updating of project outline."
   ":kbd:`Ctrl`:kbd:`'`",                "Wrap selected text, or word under cursor, in single quotes."
   ":kbd:`Ctrl`:kbd:`""`",               "Wrap selected text, or word under cursor, in double quotes."
   ":kbd:`Ctrl`:kbd:`Enter`",            "Open the tag or reference under the cursor in the Viewer."
   ":kbd:`Ctrl`:kbd:`Shift`:kbd:`,`",    "Open the :guilabel:`Project Settings` dialog."
   ":kbd:`Ctrl`:kbd:`Shift`:kbd:`/`",    "Remove block formatting for block under cursor."
   ":kbd:`Ctrl`:kbd:`Shift`:kbd:`1`",    "Replace occurrence of search word in current document, and search for next occurrence."
   ":kbd:`Ctrl`:kbd:`Shift`:kbd:`A`",    "Select all text in current paragraph."
   ":kbd:`Ctrl`:kbd:`Shift`:kbd:`G`",    "Find previous occurrence of search word in current document. (Same as :kbd:`Shift`:kbd:`F3`.)"
   ":kbd:`Ctrl`:kbd:`Shift`:kbd:`I`",    "Import text to the current document from a text file."
   ":kbd:`Ctrl`:kbd:`Shift`:kbd:`N`",    "Create new folder."
   ":kbd:`Ctrl`:kbd:`Shift`:kbd:`O`",    "Open a project."
   ":kbd:`Ctrl`:kbd:`Shift`:kbd:`R`",    "Close the document viewer."
   ":kbd:`Ctrl`:kbd:`Shift`:kbd:`S`",    "Save the current project."
   ":kbd:`Ctrl`:kbd:`Shift`:kbd:`W`",    "Close the current project."
   ":kbd:`Ctrl`:kbd:`Shift`:kbd:`Z`",    "Alternative sequence for redo last undo."
   ":kbd:`Ctrl`:kbd:`Shift`:kbd:`Up`",   "Move item one step up in the project tree."
   ":kbd:`Ctrl`:kbd:`Shift`:kbd:`Down`", "Move item one step down in the project tree."
   ":kbd:`Ctrl`:kbd:`Shift`:kbd:`Del`",  "If in the project tree, move a document to trash, or delete a folder."
   ":kbd:`F1`",                          "Open the documentation. This will either open the Qt Assistant, if available, or send you to the documentation website."
   ":kbd:`F2`",                          "If in the project tree, edit a document or folder settings. (Same as :kbd:`Ctrl`:kbd:`E`)"
   ":kbd:`F3`",                          "Find next occurrence of search word in current document. (Same as :kbd:`Ctrl`:kbd:`G`)"
   ":kbd:`F5`",                          "Open the :guilabel:`Build Novel Project` dialog."
   ":kbd:`F6`",                          "Open the :guilabel:`Writing Statistics` dialog."
   ":kbd:`F7`",                          "Re-run spell checker."
   ":kbd:`F8`",                          "Activate :guilabel:`Focus Mode`, hiding the project tree and document viewer."
   ":kbd:`F9`",                          "Re-build the project index."
   ":kbd:`F10`",                         "Re-build the project outline."
   ":kbd:`F11`",                         "Activate full screen mode."
   ":kbd:`Shift`:kbd:`F1`",              "Open the online documentation in the system default browser."
   ":kbd:`Shift`:kbd:`F3`",              "Find previous occurrence of search word in current document. (Same as :kbd:`Ctrl`:kbd:`Shift`:kbd:`G`.)"
   ":kbd:`Shift`:kbd:`F6`",              "Open the :guilabel:`Project Details` dialog."
   ":kbd:`Return`",                      "If in the project tree, open a document for editing."

.. note::
   On macOS, replace :kbd:`Ctrl` with :kbd:`Cmd`.


.. _a_ui_shortcuts_ins:

Insert Shortcuts
----------------

A set of insert features are also available through shortcuts, but they require a double
combination of key sequences. The insert feature is activated with :kbd:`Ctrl`:kbd:`K`, followed by
a key or key combination for the inserted content.

.. csv-table:: Keyboard Shortcuts
   :header: "Shortcut", "Description"
   :widths: 40, 60
   :class: "tight-table"

   ":kbd:`Ctrl`:kbd:`K`, :kbd:`−`",                 "Insert a short dash (en dash)."
   ":kbd:`Ctrl`:kbd:`K`, :kbd:`_`",                 "Insert a long dash (em dash)."
   ":kbd:`Ctrl`:kbd:`K`, :kbd:`Ctrl`:kbd:`_`",      "Insert a horizontal bar (quotation dash)."
   ":kbd:`Ctrl`:kbd:`K`, :kbd:`~`",                 "Insert a figure dash (same width as a number)."
   ":kbd:`Ctrl`:kbd:`K`, :kbd:`1`",                 "Insert a left single quote."
   ":kbd:`Ctrl`:kbd:`K`, :kbd:`2`",                 "Insert a right single quote."
   ":kbd:`Ctrl`:kbd:`K`, :kbd:`3`",                 "Insert a left double quote."
   ":kbd:`Ctrl`:kbd:`K`, :kbd:`4`",                 "Insert a right double quote."
   ":kbd:`Ctrl`:kbd:`K`, :kbd:`'`",                 "Insert a modifier apostrophe."
   ":kbd:`Ctrl`:kbd:`K`, :kbd:`.`",                 "Insert an ellipsis."
   ":kbd:`Ctrl`:kbd:`K`, :kbd:`Ctrl`:kbd:`'`",      "Insert a prime."
   ":kbd:`Ctrl`:kbd:`K`, :kbd:`Ctrl`:kbd:`""`",     "Insert a double prime."
   ":kbd:`Ctrl`:kbd:`K`, :kbd:`Return`",            "Insert a hard line break."
   ":kbd:`Ctrl`:kbd:`K`, :kbd:`Space`",             "Insert a non-breaking space."
   ":kbd:`Ctrl`:kbd:`K`, :kbd:`Shift`:kbd:`Space`", "Insert a thin space."
   ":kbd:`Ctrl`:kbd:`K`, :kbd:`Ctrl`:kbd:`Space`",  "Insert a thin non-breaking space."
   ":kbd:`Ctrl`:kbd:`K`, :kbd:`*`",                 "Insert a list bullet."
   ":kbd:`Ctrl`:kbd:`K`, :kbd:`Ctrl`:kbd:`−`",      "Insert a hyphen bullet (alternative bullet)."
   ":kbd:`Ctrl`:kbd:`K`, :kbd:`Ctrl`:kbd:`*`",      "Insert a flower mark (alternative bullet)."
   ":kbd:`Ctrl`:kbd:`K`, :kbd:`%`",                 "Insert a per mille symbol."
   ":kbd:`Ctrl`:kbd:`K`, :kbd:`Ctrl`:kbd:`O`",      "Insert a degree symbol."
   ":kbd:`Ctrl`:kbd:`K`, :kbd:`Ctrl`:kbd:`X`",      "Insert a times sign."
   ":kbd:`Ctrl`:kbd:`K`, :kbd:`Ctrl`:kbd:`D`",      "Insert a division sign."
   ":kbd:`Ctrl`:kbd:`K`, :kbd:`G`",                 "Insert a ``@tag`` keyword."
   ":kbd:`Ctrl`:kbd:`K`, :kbd:`V`",                 "Insert a ``@pov`` keyword."
   ":kbd:`Ctrl`:kbd:`K`, :kbd:`C`",                 "Insert a ``@char`` keyword."
   ":kbd:`Ctrl`:kbd:`K`, :kbd:`P`",                 "Insert a ``@plot`` keyword."
   ":kbd:`Ctrl`:kbd:`K`, :kbd:`T`",                 "Insert a ``@time`` keyword."
   ":kbd:`Ctrl`:kbd:`K`, :kbd:`L`",                 "Insert a ``@location`` keyword."
   ":kbd:`Ctrl`:kbd:`K`, :kbd:`O`",                 "Insert an ``@object`` keyword."
   ":kbd:`Ctrl`:kbd:`K`, :kbd:`E`",                 "Insert an ``@entity`` keyword."
   ":kbd:`Ctrl`:kbd:`K`, :kbd:`X`",                 "Insert a ``@custom`` keyword."
