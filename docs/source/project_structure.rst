.. _a_struct:

***************
Novel Structure
***************

This section covers the structure of a novel project.

It concerns documents under the :guilabel:`Novel` type root folder only. There are some
restrictions and features that only apply to these types of documents.


.. _a_struct_heads:

Importance of Headings
======================

Subfolders under root folders have no impact on the structure of the novel itself. The structure is
instead dictated by the heading level of the headers within the documents.

Four levels of headings are supported, signified by the number of hashes (``#``) preceding the
title. See also the :ref:`a_fmt` section for more details about the markdown syntax.

.. note::
   The header levels are not only important when generating the exported novel file, they are also
   used by the indexer when building the outline tree in the :guilabel:`Outline` tab as well as the
   :guilabel:`Novel` tab of the project tree. Each heading also starts a new region where new
   references and tags can be defined.

The syntax for the four basic header types, and the two special header types, is listed in section
:ref:`a_fmt_head`. The meaning of the four levels for the structure of your novel is as follows:

**Header Level 1: Partition**
   This header level signifies that the text refers to a top level partition. This is useful when
   you want to split the manuscript up into books, parts, or acts. These headings are not required.
   The novel title itself should use the special header level one code explained in
   :ref:`a_fmt_head`.

**Header Level 2: Chapter**
   This header level signifies a chapter level partition. Each time you want to start a new
   chapter, you must add such a heading. If you choose to split your manuscript up into one
   document per scene, you need a single chapter document with just the heading. You can of course
   also add a synopsis and reference keywords to the chapter document. If you want to open the
   chapter with a quote or other introductory text that isn't part of a scene, this is also where
   you'd put that text.

**Header Level 3: Scene**
   This header level signifies a scene level partition. You must provide a title text, but the
   title text can be replaced with a scene separator or just skipped entirely when you export your
   manuscript.

**Header Level 4: Section**
   This header level signifies a sub-scene level partition, usually called a "section" in the
   documentation and the user interface. These can be useful if you want to change tag references
   mid-scene, like if you change the point-of-view character. You are free to use sections as you
   wish, and can filter them out of the final manuscript just like with scene titles.

Page breaks are automatically added before level 1 and 2 headers when you export your project to a
format that supports page breaks, or when you print the document directly from the build tool. If
you want page breaks in other places, you have to specify them manually. See :ref:`a_fmt_break`.

.. tip::
   There are multiple options of how to process novel titles when exporting the manuscript. For
   instance, chapter numbers can be applied automatically, and so can scene numbers if you want
   them in a draft manuscript. See the :ref:`a_export` page for more details.


.. _a_struct_heads_title:

Novel Title and Front Matter
----------------------------

It is recommended that you add a document at the very top of your project with the novel title as
the first line. You should modify the level 1 header format code with an ``!`` in order to render
it as a document title that is excluded from any automatic Table of Content in an exported
document, like so:

``#! My Novel``

The title is by default centred on the page when exported. You can add more text to the page as you
wish, like for instance the author's name and details.

If you want an additional page of text after the title page, starting on a fresh page, you can add
``[NEW PAGE]`` on a line by itself, and continue the text after it. This will insert a page break
when the project is exported.


.. _a_struct_heads_unnum:

Unnumbered Chapter Headings
---------------------------

If you use the automatic numbering feature for your chapters, but you want to keep some special
chapters separate from this, you cam add a ``!`` to the level 2 header formatting code to tell the
build tool to skip these chapters.

``##! Unnumbered Chapter Title``

There is a separate formatting feature for such chapters in the :guilabel:`Build Novel Project`
tool as well. See the :ref:`a_export` page for more details. When exporting to a format that
supports page breaks, also unnumbered chapters will have a page break added just like for normal
chapters.

.. Note::
   Previously, you could also disable the automatic numbering of a chapter by adding an ``*`` as
   the first character of the chapter title itself. This feature has been dropped in favour of the
   current format in order to keep level 1 and 2 headers consistent. Please update your chapter
   headings if you've used this syntax.


.. _a_struct_tags:

Tag References
==============

Each text partition, indicated by a heading of any level, can contain references to tags set in the
supporting notes of the project. The references are gathered by the indexer and used to generate an
outline view on the :guilabel:`Outline` tab of how the different parts of the novel are connected.
This section covers how to set references to tags. See :ref:`a_notes_tags` for how to define tags
the references can point to.

References and tags are also clickable in the document editor and viewer, making it easy to
navigate between reference notes while writing. Clicked links are always opened in the view panel.

References are set as a keyword and a list of corresponding tags. The valid keywords are listed
below. The format of a reference line is ``@keyword: value1, [value2] ... [valueN]``. All keywords
allow multiple values.

``@pov``
   The point-of-view character for the current section. The target must be a note tag in the
   :guilabel:`Character` type root folder.

``@focus``
   The character that has the focus for the current section. This can be used in cases where the
   focus is not a point-of-view character. The target must be a note tag in the
   :guilabel:`Character` type root folder.

``@char``
   Other characters in the current section. The target must be a note tag in the
   :guilabel:`Character` type root folder. This should not include the point-of-view character.

``@plot``
   The plot or subplot advanced in the current section. The target must be a note tag in the
   :guilabel:`Plot` type root folder.

``@time``
   The timelines touched by the current section. The target must be a note tag in the
   :guilabel:`Timeline` type root folder.

``@location``
   The location the current section takes place in. The target must be a note tag in the
   :guilabel:`Locations` type root folder.

``@object``
   Objects present in the current section. The target must be a note tag in the :guilabel:`Object`
   type root folder.

``@entity``
   Entities present in the current section. The target must be a note tag in the
   :guilabel:`Entities` type root folder.

``@custom``
   Custom references in the current section. The target must be a note tag in a :guilabel:`Custom`
   type root folder. You can add more than one Custom folder, but they all use the same reference
   keyword.

The syntax highlighter will alert the user that the tags and references are used correctly, and
that the tags referenced exist.

The highlighter may be mistaken if the index of defined tags is out of date. If so, press :kbd:`F9`
to regenerate it, or select :guilabel:`Rebuild Index` from the :guilabel:`Tools` menu. In general,
the index for a document is regenerated when it is saved, so this shouldn't normally be necessary.


.. _a_struct_layout:

Document Layout
===============

All documents in the project can have a layout format set. Previously, there were multiple layouts
available to change how the documents where formatted on export. These have now been reduced to
just two layouts: :guilabel:`Novel Document` and :guilabel:`Project Note`.

Novel documents can only live in the :guilabel:`Novel` root folder. You can also move them to
:guilabel:`Outtakes` and :guilabel:`Trash` of course. Project notes can be added anywhere in the
project.

Depending on which icon theme you're using, the project tree can distinguish between the different
layouts and header levels of the documents to help indicate which are project notes and which are
novel documents containing a partition, chapter, or scene. If the icon theme you've selected
doesn't show a difference, you can still see the layout description in the details panel below the
project tree.

.. tip::
   You can always start writing with a coarse setup with one or a few documents, and then later use
   the split tool to automatically split the documents into separate chapter and scene documents.
   You can split a document on any of the four header levels.
