.. _a_breakdown:

************
How it Works
************

.. _Typicons: https://github.com/stephenhutchings/typicons.font

The main features of novelWriter are listed in the :ref:`a_intro` section. Here, we go into some
more details on how they are implemented. Later on in this documentation, these features will be
covered in more detail.


.. _a_breakdown_design:

GUI Layout and Design
=====================

The user interface of novelWriter is intended to be as minimalistic as practically possible, while
at the same time provide a complete set of features needed for writing a novel.

The main window does not have a toolbar like many other applications do. This reduces clutter, and
since the documents are formatted with style tags, is more or less redundant. However, most
formatting features supported are available through convenient keyboard shortcuts. They are also
available in the main menu so you don't have to look up formatting codes every time you need them.
However, a list of all shortcuts can be found in the :ref:`a_kb` section.

.. note::
   novelWriter is not intended to be a full office type word processor. It doesn't support images,
   links, tables, and other complex structures and objects often needed for such documents.
   Formatting is limited to headers, emphasis, text alignment, and a few other simple features.


Window Tabs and Areas
---------------------

The main window is split in two, or optionally three, panels. The left-most panel contains the
project tree and all the documents in your project. The second panel is the document editor. An
optional third panel is a document viewer which can view any document in your project independently
of what is open in the document editor. It is not intended as a preview window, although you can
use it for this as well as it will apply the formatting tags you have specified. The main purpose
of the viewer is for viewing your notes next to your editor while you're writing.

The editor also has a :guilabel:`Focus Mode` you can toggle either from the menu, or from the icon
in the editor header. When :guilabel:`Focus Mode` is enabled, all the user interface elements other
than the document editor itself are hidden away.

A second tab is also available on the main window. This is the :guilabel:`Outline` tab where the
entire novel structure can be displayed, with all the tags and references listed. Depending on how
you structure your novel documents, this outline can be quite different from your project tree.
Your project tree lists individual documents, your Outline tree lists the structure of the novel
itself in terms of partitions, chapters and scenes as it appears in the text of those documents.


Colour Themes
-------------

The colour theme of the user interface defaults to that of the host operating system. Some other
light and dark colour themes are provided, and can be enabled in :guilabel:`Preferences` from the
:guilabel:`Tools` menu. A number of syntax highlighting themes are also available in
:guilabel:`Preferences`. Icon themes for light and dark GUIs are also available. The icons are
based on the Typicons_ icon set designed by Stephen Hutchings.

.. note::
   The GUI colour theme and the syntax highlighting theme are separate settings in
   :guilabel:`Preferences`. If you switch to dark mode on the GUI, you should also switch the icon
   theme and syntax highlighting theme.


.. _a_breakdown_project:

Project Layout
==============

This is a brief introduction to how you structure your writing projects. All of this will be
covered in more detail later.

The main point is that you are free to organise your project documents as you wish into subfolders,
and split the text between documents in whatever way suits you. All that matters to novelWriter is
the linear order the documents appear at in the project tree (top to bottom). The chapters, scenes
and sections of the novel are determined by the headings within those documents.

The four heading levels (**H1** to **H4**) are treated as follows:

* **H1** is used for the book title, and for partitions.
* **H2** is used for chapter tiles.
* **H3** is used for scene titles – optionally replaced by separators.
* **H4** is for section titles within scenes, if such granularity is needed.

This header level structure is only taken into account for novel documents. For the project notes,
the header levels have no structural meaning, and the user is free to do whatever they want. See
:ref:`a_struct` and :ref:`a_notes` for more details.


.. _a_breakdown_export:

Project Export
==============

The project can at any time be exported to a range of different formats through the
:guilabel:`Build Novel Project` tool. Natively, novelWriter supports export to Open Document,
HTML5, and various flavours of Markdown.

The HTML5 export format is suitable for conversion by a number of other tools like Pandoc, or for
importing into word processors if the Open Document format isn't suitable. In addition, printing
and printing to PDF is also possible. 

You can also export the content of the project to a JSON file. This is useful if you want to write
your own processing script in for instance Python as the entire novel can be read into a Python
dictionary with a couple of lines of code. The JSON file can be populated either with HTML
formatted text, or with the raw text as typed into the novel documents. See :ref:`a_export_options`
for more details.

A number of filter options can be applied to the :guilabel:`Build Novel Project` tool, allowing you
to export a draft manuscript, a reference document of notes, an outline based on chapter and scene
titles with a synopsis each, and so on. See :ref:`a_export` for more details on export features and
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
formats used for the files are well suited. Also the JSON documents have line breaks and indents.

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

