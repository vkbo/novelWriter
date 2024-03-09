.. _a_fmt:

********************
Formatting Your Text
********************

The novelWriter text editor is a plain text editor that uses formatting codes for setting meta data
values and allowing for some text formatting. The syntax is based on Markdown, but novelWriter is
**not** a Markdown editor. It supports basic formatting like emphasis (italic), strong importance
(bold) and strike through text, as well as four levels of headings. For some further complex
formatting needs, a set of shortcodes can be used.

In addition to formatting codes, novelWriter allows for comments, a synopsis tag, and a set of
keyword and value sets used for :term:`tags<tag>` and :term:`references<reference>`. There are also
some codes that apply to whole paragraphs. See :ref:`a_fmt_text` for more details.


.. _a_fmt_hlight:

Syntax Highlighting
===================

The editor has a syntax highlighter feature that is meant to help you know when you've used the
formatting tags or other features correctly. It will change the colour and font size of your
headings, change the text colour of emphasised text, and it can also show you where you have
dialogue in your text.

.. figure:: images/fig_references.png

   An example of the colour highlighting of references. "Bob" is not defined, and "@blabla" is not
   a valid reference type.

When you use the keywords to set tags and references, these also change colour. Correct keywords
have a distinct colour, and the references themselves will get a colour if they are valid. Invalid
references will get a squiggly error line underneath. The same applies to duplicate tags.

There are a number of syntax highlighter colour themes available, both for light and dark GUIs. You
can select them from :guilabel:`Preferences`.


.. _a_fmt_head:

Headings
========

.. figure:: images/fig_header_levels.png

   An illustration of how heading levels correspond to the novel structure.

Four levels of headings are allowed. For :term:`project notes`, they are free to be used as you see
fit. That is, novelWriter doesn't assign the different headings any particular meaning. However,
for :term:`novel documents` they indicate the structural level of the novel and must be used
correctly to produce the intended result. See :ref:`a_struct_heads` for more details.

``# Title Text``
   Heading level one. For novel documents, the level indicates the start of a new partition.

``## Title Text``
   Heading level two. For novel documents, the level indicates the start of a new chapter. Chapter
   numbers can be inserted automatically when building the manuscript.

``### Title Text``
   Heading level three. For novel documents, the level indicates the start of a new scene. Scene
   numbers or scene separators can be inserted automatically when building the manuscript, so you
   can use the title field as a working title for your scenes if you wish.

``#### Title Text``
   Heading level four. For novel documents, the level indicates the start of a new section. Section
   titles can be replaced by separators or ignored completely when building the manuscript.

For headings level one and two, adding a ``!`` modifies its meaning:

``#! Title Text``
   This tells the build tool that the level one heading is intended to be used for the novel's or
   notes folder's main title, like for instance on the front page. When building the manuscript,
   this will use a different styling and will exclude the title from, for instance, a Table of
   Contents in Libre Office.

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

In addition, the editor supports a few additional types of white spaces:

* A non-breaking space can be inserted with :kbd:`Ctrl+K`, :kbd:`Space`.
* Thin spaces are also supported, and can be inserted with :kbd:`Ctrl+K`, :kbd:`Shift+Space`.
* Non-breaking thin space can be inserted with :kbd:`Ctrl+K`, :kbd:`Ctrl+Space`.

These are all insert features, and the :guilabel:`Insert` menu has more. The keyboard shortcuts for
them are also listed in :ref:`a_kb_ins`.

Non-breaking spaces are highlighted by the syntax highlighter with an alternate coloured
background, depending on the selected theme.

.. tip::
   Non-breaking spaces are for instance the correct type of space to separate a number from its
   unit. Generally, non-breaking spaces are used to prevent line wrapping algorithms from adding
   line breaks where they shouldn't.


.. _a_fmt_emph:

Text Emphasis
=============

A minimal set of Markdown text emphasis styles are supported for text paragraphs.

``_text_``
   The text is rendered as emphasised text (italicised).

``**text**``
   The text is rendered as strongly important text (bold).

``~~text~~``
   Strike through text.

In Markdown guides it is often recommended to differentiate between strong importance and emphasis
by using ``**`` for strong and ``_`` for emphasis, although Markdown generally also supports ``__``
for strong and ``*`` for emphasis. However, since the differentiation makes the highlighting and
conversion significantly simpler and faster, in novelWriter this is a rule, not just a
recommendation.

In addition, the following rules apply:

1. The emphasis and strike through formatting tags do not allow spaces between the words and the
   tag itself. That is, ``**text**`` is valid, ``**text **`` is not.
2. More generally, the delimiters must be on the outer edge of words. That is, ``some **text in
   bold** here`` is valid, ``some** text in bold** here`` is not.
3. If using both ``**`` and ``_`` to wrap the same text, the underscore must be the **inner**
   wrapper. This is due to the underscore also being a valid word character, so if they are on the
   outside, they violate rule 2.
4. Text emphasis does not span past line breaks. If you need to add emphasis to multiple lines or
   paragraphs, you must apply it to each of them in turn.
5. Text emphasis can only be used in plain paragraphs. Comments, titles, and meta data tags don't
   allow for formatting, and any formatting markup will be rendered as-is.

.. tip::
   novelWriter supports standard escape syntax for the emphasis markup characters in case the
   editor misunderstands your intended usage of them. That is, ``\*``, ``\_`` and ``\~`` will
   generate a plain ``*``, ``_`` and ``~``, respectively, without interpreting them as part of the
   markup.


.. _a_fmt_shortcodes:

Extended Formatting with Shortcodes
===================================

For additional formatting options, you can use shortcodes. Shortcodes is a form of in-line codes
that can be used to change the format of the text that follows and opening code, and last until
that formatting region is ended with a closing code.

These shortcodes are intended for special formatting cases, or more complex cases that cannot be
solved with simple Markdown-like formatting codes. Available shortcodes are listed below.

.. csv-table:: Shortcodes Formats
   :header: "Syntax", "Description"
   :widths: 40, 60
   :class: "tight-table"

   "``[b]text[/b]``",     "Text is rendered as bold text."
   "``[i]text[/i]``",     "Text is rendered as italicised text."
   "``[s]text[/s]``",     "Text is rendered as strike through text."
   "``[u]text[/u]``",     "Text is rendered as underlined text."
   "``[sup]text[/sup]``", "Text is rendered as superscript text."
   "``[sub]text[/sub]``", "Text is rendered as subscript text."

Unlike Markdown style codes, these can be used anywhere within a paragraph. Even in the middle of a
word if you need to. You can also freely combine them to form more complex formatting.

The shortcodes are available from the :guilabel:`Format` menu and in the editor toolbar, which can
be activated by clicking the three dots in the editor header.

.. versionadded:: 2.2


.. _a_fmt_comm:

Comments and Synopsis
=====================

In addition to these standard Markdown features, novelWriter also allows for comments in documents.
The text of a comment is ignored by the word counter. The text can also be filtered out when
building the manuscript or viewing the document.

If the first word of a comment is ``Synopsis:`` (with the colon included), the comment is treated
in a special manner and will show up in the :ref:`a_ui_outline` in a dedicated column. The word
``synopsis`` is not case sensitive. If it is correctly formatted, the syntax highlighter will
indicate this by altering the colour of the word.

``% text ...``
   This is a comment. The text is not rendered by default (this can be overridden), seen in the
   document viewer, or counted towards word counts.

``%Synopsis: text ...``
   This is a synopsis comment. It is generally treated in the same way as a regular comment, except
   that it is also captured by the indexing algorithm and displayed in the :ref:`a_ui_outline`. It
   can also be filtered separately when building the project to for instance generate an outline
   document of the whole project.

``%Short: text ...``
   This is a short description comment. It is identical to the synopsis comment (they are
   interchangeable), but is intended to be used for project notes. The text shows up in the
   Reference panel below the document viewer in the last column labelled
   :guilabel:`Short Description`.

.. note::
   Only one comment can be flagged as a synopsis or short comment for each heading. If multiple
   comments are flagged as synopsis or short comments, the last one will be used and the rest
   ignored.


.. _a_fmt_tags:

Tags and References
===================

The document editor supports a set of keywords used for setting tags, and making references between
documents.

Tags use the keyword ``@tag:`` to define a tag. The tag can be set once per section defined by a
heading. Setting it multiple times under the same heading will just override the previous setting.

``@tag: value``
   A tag keyword followed by the tag value, like for instance the name of a character.

References can be set anywhere within a section, and are collected according to their category.
References are in the form:

``@keyword: value``
   A reference keyword followed by a value, or a comma separated list of values.

Tags and references are covered in detail in the :ref:`a_references` chapter. The keywords can be
inserted at the cursor position in the editor via the :guilabel:`Insert` menu. If you start typing
an ``@`` on a new line, and auto-complete menu will also pop up suggesting keywords.


.. _a_fmt_align:

Paragraph Alignment and Indentation
===================================

All documents have the text by default aligned to the left or justified, depending on your
settings in :guilabel:`Preferences`.

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

   "``>> Right aligned text``",        "The text paragraph is right-aligned."
   "``Left aligned text <<``",         "The text paragraph is left-aligned."
   "``>> Centred text <<``",           "The text paragraph is centred."
   "``> Left indented text``",         "The text has an increased left margin."
   "``Right indented text <``",        "The text has an increased right margin."
   "``> Left/right indented text <``", "The text has both margins increased."

.. note::
   The text editor will not show the alignment and indentation live. But the viewer will show them
   when you open the document there. It will of course also be reflected in the document generated
   from the manuscript build tool as long as the format supports paragraph alignment.


.. _a_fmt_break:

Vertical Space and Page Breaks
==============================

Adding more than one line break between paragraphs will **not** increase the space between those
paragraphs when building the project. To add additional space between paragraphs, add the text
``[vspace]`` on a line of its own, and the build tool will insert a blank paragraph in its place.

If you need multiple blank paragraphs just add a colon and a number to the above code. For
instance, writing ``[vspace:3]`` will insert three blank paragraphs.

Normally, the manuscript build tool will insert a page break before all headings of level one and
for all headings of level two for novel documents, i.e. chapters, but not for project notes.

If you need to add a page break somewhere else, put the text ``[new page]`` on a line by itself
before the text you wish to start on a new page.

If you want page breaks for scenes and sections, you must add them manually.

.. note::
   The page break code is applied to the text that follows it. It adds a "page break before" mark
   to the text when exporting to HTML or Open Document. This means that a ``[new page]`` which has
   no text following it, it will not result in a page break.

**Example:**

.. code-block:: md

   This is a text paragraph.

   [vspace:2]

   This is another text paragraph, but there will be two empty paragraphs
   in-between them.

   [new page]

   This text will always start on a new page if the build format has pages.
