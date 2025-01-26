.. _a_struct:

***************
Novel Structure
***************

This chapter covers the structure of a novel project.

There are two different types of documents in a project, **Novel Documents** and **Project Notes**.
Active novel documents can only live in a **Novel** type root folder. You can also move them to
**Archive** and **Trash** of course, where they become inactive.

The project tree can distinguish between the different heading levels of the novel documents using
coloured icons, and optionally add emphasis on the label. Emphasis can be enabled in
**Preferences**.


.. _a_struct_heads:

Importance of Headings
======================

Subfolders under root folders have no impact on the structure of the novel itself. The structure is
instead dictated by the heading level of the headings within the documents.

Four levels of headings are supported, signified by the number of hashes (``#``) preceding the
title. See also the :ref:`a_fmt` section for more details about the markup syntax.

.. note::

   The heading levels are not only important when generating the manuscript, they are also used by
   the indexer when building the outline tree in the **Outline View** as well as in the **Novel
   Tree**. Each heading also starts a new region where new Tags and References can be defined. See
   :ref:`a_references` for more details.

The syntax for the four basic heading types, and the three special types, is listed in section
:ref:`a_fmt_head`. The meaning of the four levels for the structure of your novel is as follows:

**Heading Level 1: Partition**
   This heading level signifies that the text refers to a top level heading. This is useful when
   you want to split the manuscript up into books, parts, or acts. These headings are not required.
   The novel title itself should use the special heading level ``#!`` covered in :ref:`a_fmt_head`.

**Heading Level 2: Chapter**
   This heading level signifies a chapter. Each time you want to start a new chapter, you must add
   such a heading. If you choose to split your manuscript up into one document per scene, you need
   a single chapter document with just the heading. You can of course also add a synopsis and
   reference keywords to the chapter document. If you want to open the chapter with a quote or
   other introductory text that isn't part of a scene, this is also where you'd put that text.

**Heading Level 3: Scene**
   This heading level signifies a scene. You must provide a title text, but the title text can be
   replaced with a scene separator or just skipped entirely when you build your manuscript. If you
   need to distinguish between hard and soft scene breaks, there is an alternative format for
   scenes you can use for this distinction. The formatting is covered in :ref:`a_fmt_head`. See
   also :ref:`a_struct_heads_scenes`.

**Heading Level 4: Section**
   This heading level can be used to split up a scene, usually called a "section" in the
   documentation and the user interface. These can be useful if you want to change references
   mid-scene, like if you change the point-of-view character. You are free to use sections as you
   wish, and you can filter them out of the final manuscript.

Page breaks can be automatically added before titles, partition, chapter and scene headings from
the **Manuscript Build** tool when you build your project to a format that supports page breaks. If
you want page breaks in other places, you have to specify them manually. See :ref:`a_fmt_break`.

.. tip::

   There are multiple options of how to process novel headings when building the manuscript. For
   instance, chapter numbers can be applied automatically, and so can scene numbers if you want
   them in a draft manuscript. You can also insert point-of-view character names in chapter titles.
   See the :ref:`a_manuscript` page for more details.

.. note::

   As of 2.6, the heading levels internally in novelWriter do not map directly to heading levels in
   manuscript documents. In manuscript documents, chapters are considered the top level heading,
   and partitions become plain text paragraphs with a larger font.

   .. versionadded:: 2.6


.. _a_struct_heads_title:

Novel Title and Front Matter
----------------------------

It is recommended that you add a document at the very top of each **Novel** root folder with the
novel title in it. You should modify the level 1 heading format code with an ``!`` in order to
render it as a document title that is excluded from any automatic Table of Content in a manuscript
build document.

You can also add the author name and address above this if this is required by the manuscript
format you use, and additional space added before the title.

This is the title page novelWriter generates automatically for a new project as of version 2.6:

.. code-block:: md

   Jane Doe[br]
   Address 1[br]
   Address 2 <<

   [vspace:5]

   #! My Novel

   >> **By Jane Doe** <<

   >> Word Count: [field:textWords] <<

The title is by default centred on the page. You can add more text to the page as you wish, like
for instance the author's name and details.

If you want an additional page of text after the title page, starting on a fresh page, you can add
``[new page]`` on a line by itself, and continue the text after it. This will insert a page break
before the text. See also :ref:`a_fmt_break`.


.. _a_struct_heads_unnum:

Unnumbered Chapter Headings
---------------------------

If you use the automatic numbering feature for your chapters, but you want to keep some special
chapters separate from this, you can add an ``!`` to the level 2 heading formatting code to tell
the build tool to skip these chapters when adding numbers.

.. code-block:: md

   ##! Unnumbered Chapter Title

   Chapter Text

There is a separate formatting feature for such chapter titles in the **Manuscript Build** tool as
well. See the :ref:`a_manuscript` page for more details. When building a document of a format that
supports page breaks, also unnumbered chapters can have a page break added just like for normal
chapters.


.. _a_struct_heads_scenes:

Hard and Soft Scene Breaks
--------------------------

If you need two different ways to style scenes in your manuscript, like if you want to insert
different scene separators for soft and hard scene breaks, there is an alternative scene format
available for scene headings with a ``!`` added to the formatting code.

.. code-block:: md

   ### Soft Scene Transition

   A soft scene break.

   ###! Hard Scene Transition

   A hard scene break.

There is a separate formatting feature for these titles in the **Manuscript Build** tool.

.. versionadded:: 2.4
