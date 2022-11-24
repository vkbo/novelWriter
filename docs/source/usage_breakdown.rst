.. _a_breakdown:

************
How it Works
************

.. _Fusion: https://doc.qt.io/qt-6/gallery.html
.. _Pandoc: https://pandoc.org/
.. _Typicons: https://github.com/stephenhutchings/typicons.font
.. _Open Document: https://en.wikipedia.org/wiki/OpenDocument

The main features of novelWriter are listed in the :ref:`a_intro` section. Here, we go into some
more details on how they are implemented. This is intended as an overview. Later on in this
documentation, these features will be covered in even more detail.


.. _a_breakdown_design:

GUI Layout and Design
=====================

The user interface of novelWriter is intended to be as minimalistic as practically possible, while
at the same time provide a complete set of features needed for writing a novel.

The main window does not have an editor toolbar like many other applications do. This reduces
clutter, and since the documents are formatted with style tags, is more or less redundant. However,
most formatting features supported are available through convenient keyboard shortcuts. They are
also available in the main menu so you don't have to look up formatting codes every time you need
them. For reference, a list of all shortcuts can be found in the :ref:`a_kb` section.

.. note::
   novelWriter is not intended to be a full office type word processor. It doesn't support images,
   links, tables, and other complex structures and objects often needed for such documents.
   Formatting is limited to headers, emphasis, text alignment, and a few other simple features.

On the left edge of the main window, you will find a sidebar. This bar has buttons for the standard
views you can switch between, a quick link to the :guilabel:`Build Novel Project` tool, and a set
of project-related tools as well as quick access to settings at the bottom.


Project Tree View
-----------------

When in :guilabel:`Project Tree View` mode, the main work area of the main window is split in two,
or optionally three, panels. The left-most panel contains the project tree and all the documents in
your project. The second panel is the document editor. An optional third panel on the right is a
document viewer which can view any document in your project independently of what is open in the
document editor. This panel is not intended as a preview window, although you can use it for this
if you wish as it will apply the formatting tags you have specified. The main purpose of the viewer
is for viewing your notes next to your editor while you're writing.

The editor also has a :guilabel:`Focus Mode` you can toggle either from the menu, from the icon in
the editor header, or by pressing :kbd:`F8`. When :guilabel:`Focus Mode` is enabled, all the user
interface elements other than the document editor itself are hidden away.


Novel Tree View
---------------

When in :guilabel:`Novel Tree View` mode, the project tree is replaces by an overview of your novel
structure. Instead of showing individual documents, the tree now shows all headings of your novel
text. This includes multiple headings within the same document.

Each heading is indented according to the heading level. You can open and edit your novel documents
from this view as well. All headings contained in the currently open document should be highlighted
in the view to indicate which ones belong together.

If you have multiple Novel root folders, the header of the novel view becomes a droopdown box. You
can then switch between them by clicking the "Outline of ..." text. You can also click the novel
icon button next to it.

Generally, the novel view should update when you make changes to the novel structure, including
edits of the current document in the editor. The information is only updated when the automatic
save of the document is initiated though. You can adjust the aut-save interval in
:guilabel:`Preferences`. You can also regenerate the whole novel view by pressing the refresh
button at the top.

It is possible to show an optional third column in the novel view, The settings are available from
the menu button ath the top.

If you click the arrow icon to the right of each item, a tooltip will pop up showing you all the
meta data collected for that heading entry.


Novel Outline View
------------------

When in :guilabel:`Novel Outline View` mode, the tree, editor and viewer will be replaced by a
large table that shows the entire novel structure with all the tags and references listed. Pretty
much all collected meta data is available here in different columns.

You can select which novel root folder to display from the dropdown box, and you can select which
columns to show or hide from the menu button. You can also rearrange the columns by drag and drop.
The app will remember you column order and size between sessions, and for each individual project.


Colour Themes
-------------

The default colour theme of the user interface is the default theme from the Qt library. By
default, novelWriter is loaded with the Fusion_ style setting. (You can override this with the
``--style=`` setting when starting novelWriter.)

There is a standard dark theme provided as well, which is similar to the default Qt theme. Some
other light and dark colour themes are also provided. You can select which one you prefer from in
:guilabel:`Preferences` .

A number of syntax highlighting themes are also available in :guilabel:`Preferences`. These are
separate settings because there are a lot more options for syntax highlighting.

.. note::
   If you switch to dark mode on the GUI, you should also switch syntax highlighting theme to
   match, otherwise icons may be hard to see in the editor and viewer.


.. _a_breakdown_project:

Project Layout
==============

This is a brief introduction to how you structure your writing projects. All of this will be
covered in more detail later.

The main point of novelWriter is that you are free to organise your project documents as you wish
into subfolders or subdocuments, and split the text between these documents in whatever way suits
you. All that matters to novelWriter is the linear order the documents appear at in the project
tree (top to bottom). The chapters, scenes and sections of the novel are determined by the headings
within those documents.

The four heading levels (**H1** to **H4**) are treated as follows:

* **H1** is used for the book title, and for partitions.
* **H2** is used for chapter tiles.
* **H3** is used for scene titles – optionally replaced by separators.
* **H4** is for section titles within scenes, if such granularity is needed.

The project tree will select an icon for the document based on the first heading in it.

This header level structure is only taken into account for novel documents. For the project notes,
the header levels have no structural meaning, and the user is free to do whatever they want. See
:ref:`a_struct` and :ref:`a_notes` for more details.

.. note::
   You can add documents as child items of other documents if you wish. This is often more useful
   than adding folders, since you anyway may want to have the chapter heading in a separate
   document from your individual scene documents.


.. _a_breakdown_export:

Building the Manuscript
=======================

The project can at any time be assembled into a range of different formats through the
:guilabel:`Build Novel Project` tool. Natively, novelWriter supports `Open Document`_, HTML5, and
various flavours of Markdown.

The HTML5 format is suitable for conversion by a number of other tools like Pandoc_, or for
importing into word processors if the Open Document format isn't suitable. In addition, printing
and printing to PDF is also possible. 

You can also export the content of the project to a JSON file. This is useful if you want to write
your own processing script in for instance Python, as the entire novel can be read into a Python
dictionary with a couple of lines of code. The JSON file can be populated either with HTML
formatted text, or with the raw text as typed into the novel documents. See :ref:`a_export_options`
for more details.

A number of filter options can be applied to the :guilabel:`Build Novel Project` tool, allowing you
to make a draft manuscript, a reference document of notes, an outline based on chapter and scene
titles with a synopsis each, and so on. See :ref:`a_export` for more details on build features and
formats.


.. _a_breakdown_storage:

Project Storage
===============

The files of a novelWriter project are stored in a dedicated project folder. The project structure
is kept in a file at the root of this folder called ``nwProject.nwx``. All the document files and
associated meta data is stored in the other folders below the project folder. For more technical
details about what all the files mean and how they're organised, see the :ref:`a_storage` section.

This way of storing data was chosen for several reasons. Firstly, all the text you add to your
project is saved directly to your project folder in separate files. Only the project structure and
the text you are currently editing is stored in memory at any given time. Secondly, having multiple
small files means it is very easy to sync them between computers with standard file synchronisation
tools. Thirdly, if you use version control software to track the changes to your project, the file
formats used for the files are well suited. Also the JSON documents have line breaks and indents,
which makes it easier to track them with version control software.

.. note::

   Since novelWriter has to keep track of a bunch of files and folders when a project is open, it
   may not run well on some virtual file systems. A file or folder must be accessible with exactly
   the path it was saved or created with. An example where this is not the case is the way Google
   Drive is mapped on Linux Gnome desktops using gvfs/gio.

.. caution::

   You should not add additional files to the project folder yourself. Nor should you manually edit
   files within it as a general rule. If you really must manually edit the text files, e.g. with
   some automated task you want to perform, you need to rebuild the index when you open the project
   again.

   Editing text files in the ``content`` folder is less risky as they are just plain text. Editing
   the main project XML file, however, may make the project file unreadable and you may crash
   novelWriter and lose project structure information and project settings.

