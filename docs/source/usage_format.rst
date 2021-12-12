.. _a_fmt:

********************
Formatting Your Text
********************

The editor itself is a plain text editor that uses formatting codes for setting meta data values
and allowing for some text formatting. The syntax is based on Markdown, but novelWriter is *not* a
Markdown editor. It supports basic formatting like emphasis (italic), strong importance (bold)
and strikethrough text, as well as four levels of headings.

In addition to formatting codes, novelWriter allows for comments, a synopsis tag, and a set of
keyword and value sets used for tags and references. There are also some codes that apply two whole
paragraphs. See :ref:`a_fmt_text` below for more details.


.. _a_fmt_head:

Headings
========

Four levels of headings are allowed. For project notes they are free to be used as you see fit.
That is, novelWriter doesn't assign the different headings any importance. However, for novel
documents they indicate the structural level of the novel and must be used correctly to produce the
intended result. See :ref:`a_struct_heads` for more details.

``# Title Text``
   Heading level one. For novel documents, the header level indicates the start of a new partition.

``## Title Text``
   Heading level two. For novel documents, the header level indicates the start of a new chapter.
   Chapter numbers can be inserted automatically when exporting the manuscript.

``### Title Text``
   Heading level three. For novel documents, the header level indicates the start of a new scene.
   Scene numbers or scene separators can be inserted automatically when exporting the manuscript,
   so you can use the title field as a working title for your scenes if you wish.

``#### Title Text``
   Heading level four. For novel documents, the header level indicates the start of a new section.
   Section titles can be replaced by separators or removed completely when exporting the
   manuscript.

For headers level one and two, adding a ``!`` modifies the behaviour of the heading:

``#! Title Text``
   This tells the build tool that the level one heading is intended to be used for the novel's
   main title, like for instance on the front page. When exporting, this will use a different
   styling and will exclude the title from for instance a Table of Contents in Libre Office.

``##! Title Text``
   This tells the build tool to not assign a chapter number to this chapter title if automatic
   chapter numbers are being used. Such titles are useful for a prologue for instance. See
   :ref:`a_struct_heads_unnum` for more details.

.. note::
   The space after the ``#`` or ``!`` character is mandatory. The syntax highlighter will change
   colour and font size when the heading is correctly formatted.


.. _a_fmt_text:

Text Paragraphs
===============

A text paragraph is indicated by a blank line. That is, you need two line breaks to separate two
fragments of text into two paragraphs. Single line breaks are treated as line breaks within a
paragraph.

In addition, the editor supports a few additional types of whitespaces:

* A non-breaking space can be inserted with :kbd:`Ctrl`:kbd:`K`, :kbd:`Space`.
* Thin spaces are also supported, and can be inserted with :kbd:`Ctrl`:kbd:`K`, 
  :kbd:`Shift`:kbd:`Space`.
* Non-breaking thin space can be inserted  with :kbd:`Ctrl`:kbd:`K`, :kbd:`Ctrl`:kbd:`Space`.

These are all insert features, and the :guilabel:`Insert` menu has more. They are also listed
in :ref:`a_kb_ins`.

Non-breaking spaces are highlighted by the syntax highlighter with an alternate coloured
background, depending on the selected theme.

.. tip::
   Non-breaking spaces are the correct type of space to separate a number from its unit. Generally,
   it prevents the line wrapping algorithms from adding line breaks where it shouldn't.


.. _a_fmt_emph:

Text Emphasis
=============

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


.. _a_fmt_comm:

Comments and Synopsis
=====================

In addition to these standard markdown features, novelWriter also allows for comments in documents.
The text of a comment is ignored by the word counter. The text can also be filtered out when
exporting or viewing the document.

If the first word of a comment is ``Synopsis:`` (with the colon included), the comment is treated
specially and will show up in the :ref:`a_ui_outline` in a dedicated column. The word ``synopsis``
is not case sensitive. If it is correctly formatted, the syntax highlighter will indicate this by
altering the colour of the word.

``% text...``
   This is a comment. The text is not exported by default (this can be overridden), seen in the
   document viewer, or counted towards word counts.

``% Synopsis: text...``
   This is a synopsis comment. It is generally treated in the same way as a regular comment, except
   that it is also captured by the indexing algorithm and displayed in the :ref:`a_ui_outline`. It
   can also be filtered separately when exporting the project to for instance generate an outline
   document of the whole project.

.. note::
   Only one comment can be flagged as a synopsis comment for each heading. If multiple comments are
   flagged as synopsis comments, the last one will be used and the rest ignored.


.. _a_fmt_tags:

Tags and References
===================

The document editor supports a minimal set of keywords used for setting tags, and making references
between documents. The tags and references can be set once per section defined by a heading. Using
them multiple times under the same heading will just override the previous setting.

``@keyword: value``
   A keyword argument followed by a value, or a comma separated list of values.

The available tag and reference keywords are listed in the :ref:`a_struct_tags` section. They can
also be inserted at the cursor position in the editor via the :guilabel:`Insert` menu.


.. _a_fmt_align:

Paragraph Alignment and Indentation
===================================

All documents have the text by default aligned to the left or justified, depending on your
Preferences.

You can override the default text alignment on individual paragraphs by specifying alignment tags.
These tags are double angle brackets. Either ``>>`` or ``<<``. You put them either before or after
the paragraph, and they will "push" the text towards the edge the brackets point towards. This
should be fairly intuitive.

Indentation uses a similar syntax. But here you use a single ``>`` or ``<`` to push the text away
from the edge.

Examples:

.. csv-table:: Text Alignment and Indentation
   :header: "Syntax", "Description"
   :widths: 40, 60
   :class: "tight-table"

   "``>> Right aligned text``", "The text paragraph is right-aligned."
   "``Left aligned text <<``",  "The text paragraph is left-aligned."
   "``>> Centred text <<``",    "The text paragraph is centred."
   "``> Indented text``",       "The text has an increased left margin."
   "``Indented text <``",       "The text has an increased right margin."
   "``> Indented text <``",     "The text has an both margins increased."

.. note::
   The text editor will not show the alignment and indentation live. But the viewer will show them
   when you open the document there. It will of course also be reflected in the document generated
   from the build tool as long as the format supports paragraph alignment.


.. _a_fmt_break:

Vertical Space and Page Breaks
==============================

Adding more than one line break between paragraphs will *not* increase the space between those
paragraphs when exporting the project. To add additional space between paragraphs, add the text
``[VSPACE]`` on a line of its own, and the build tool will insert a blank paragraph in its place.

If you need multiple blank paragraphs just add a colon and a number to the above code. For
instance, writing ``[VSPACE:3]`` will insert three blank paragraphs.

Normally, the build tool will insert a page break before all headers of level one and for all
headers of level two for novel documents, i.e. chapters, but not for project notes.

If you need to add a page break somewhere else, put the text ``[NEW PAGE]`` on a line by itself
before the text you wish to start on a new page.

Page breaks are automatically added to partition, chapter and unnumbered chapter headers of novel
documents. If you want such breaks for scenes and sections, you must add them manually.

.. note::
   The page break code is applied to the text that follows. It adds a "page break before" mark to
   the text when exporting to HTML or Open Document. This means that a ``[NEW PAGE]`` which has no
   text following it will not result in a page break.
