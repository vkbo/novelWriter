.. _a_struct:

***************
Novel Structure
***************

This chapter covers the structure of a novel project.

There are two different types of documents in a project, :guilabel:`Novel Documents` and
:guilabel:`Project Notes`. Novel documents can only live in a :guilabel:`Novel` type root folder.
You can also move them to :guilabel:`Archive` and :guilabel:`Trash` of course.

The :guilabel:`Project Tree` can distinguish between the different header levels of the novel
documents using coloured icons, and optionally add emphasis on the label, set in
:guilabel:`Preferences`.


.. _a_struct_heads:

Importance of Headings
======================

Subfolders under root folders have no impact on the structure of the novel itself. The structure is
instead dictated by the heading level of the headings within the documents.

Four levels of headings are supported, signified by the number of hashes (``#``) preceding the
title. See also the :ref:`a_fmt` section for more details about the markup syntax.

.. note::
   The header levels are not only important when generating the manuscript, they are also used by
   the indexer when building the outline tree in the :guilabel:`Outline View` as well as in the
   :guilabel:`Novel Tree`. Each heading also starts a new region where new Tags and References
   can be defined. See :ref:`a_references` for more details.

The syntax for the four basic header types, and the two special header types, is listed in section
:ref:`a_fmt_head`. The meaning of the four levels for the structure of your novel is as follows:

**Header Level 1: Partition**
   This header level signifies that the text refers to a top level partition. This is useful when
   you want to split the manuscript up into books, parts, or acts. These headings are not required.
   The novel title itself should use the special header level ``#!`` covered in :ref:`a_fmt_head`.

**Header Level 2: Chapter**
   This header level signifies a chapter level partition. Each time you want to start a new
   chapter, you must add such a heading. If you choose to split your manuscript up into one
   document per scene, you need a single chapter document with just the heading. You can of course
   also add a synopsis and reference keywords to the chapter document. If you want to open the
   chapter with a quote or other introductory text that isn't part of a scene, this is also where
   you'd put that text.

**Header Level 3: Scene**
   This header level signifies a scene level partition. You must provide a title text, but the
   title text can be replaced with a scene separator or just skipped entirely when you build your
   manuscript.

**Header Level 4: Section**
   This header level signifies a sub-scene level partition, usually called a "section" in the
   documentation and the user interface. These can be useful if you want to change references
   mid-scene, like if you change the point-of-view character. You are free to use sections as you
   wish, and you can filter them out of the final manuscript just like with scene titles.

Page breaks are automatically added before level 1 and 2 headers when you build your project to a
format that supports page breaks, or when you print the document directly from the
:guilabel:`Manuscript Build` tool. If you want page breaks in other places, you have to specify
them manually. See :ref:`a_fmt_break`.

.. tip::
   There are multiple options of how to process novel titles when building the manuscript. For
   instance, chapter numbers can be applied automatically, and so can scene numbers if you want
   them in a draft manuscript. See the :ref:`a_manuscript` page for more details.


.. _a_struct_heads_title:

Novel Title and Front Matter
----------------------------

It is recommended that you add a document at the very top of each Novel root folder with the novel
title as the first line. You should modify the level 1 header format code with an ``!`` in order to
render it as a document title that is excluded from any automatic Table of Content in a manuscript
build document, like so:

``#! My Novel``

The title is by default centred on the page. You can add more text to the page as you wish, like
for instance the author's name and details.

If you want an additional page of text after the title page, starting on a fresh page, you can add
``[NEW PAGE]`` on a line by itself, and continue the text after it. This will insert a page break
before the text. See also :ref:`a_fmt_break`.


.. _a_struct_heads_unnum:

Unnumbered Chapter Headings
---------------------------

If you use the automatic numbering feature for your chapters, but you want to keep some special
chapters separate from this, you cam add an ``!`` to the level 2 header formatting code to tell the
build tool to skip these chapters.

``##! Unnumbered Chapter Title``

There is a separate formatting feature for such chapters in the :guilabel:`Manuscript Build` tool
as well. See the :ref:`a_manuscript` page for more details. When building a document of a format
that supports page breaks, also unnumbered chapters will have a page break added just like for
normal chapters.

.. Note::
   Previously, you could also disable the automatic numbering of a chapter by adding an ``*`` as
   the first character of the chapter title itself. This feature has been dropped in favour of the
   current format in order to keep level 1 and 2 headers consistent. Please update your chapter
   headings if you've used this syntax.
