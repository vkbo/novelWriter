.. _docs_usage_align_indent:

*************************
Alignment and Indentation
*************************

The Markdown standard doesn't have commands for aligning text, so novelWriter adds its own syntax
for this. It also has syntax for indentation, which is similar to Markdown block quotes.


Paragraph Alignment and Indentation
===================================

All documents have the text by default aligned to the left or justified, depending on your setting
in **Preferences**.

You can override the default text alignment on individual paragraphs by specifying alignment tags.
These tags are double angle brackets. Either ``>>`` or ``<<``. You put them either before or after
the paragraph, and they will "push" the text towards the edge the brackets point towards. This
should be fairly intuitive.

Indentation uses a similar syntax. But here you use a single ``>`` or ``<`` to "push" the text away
from the edge.

:bdg-info:`Example`

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
   from the **Manuscript Build** tool as long as the format supports paragraph alignment.


Alignment with Line Breaks
==========================

If you have line breaks in the paragraph, the markers for all the lines are combined and used for
the entire paragraph. For the following text, all lines will be centred:

:bdg-info:`Example`

.. code-block:: md

   >> I am the very model of a modern Major-General
   I've information vegetable, animal, and mineral
   I know the kings of England, and I quote the fights historical
   From Marathon to Waterloo, in order categorical <<


Alignment with First Line Indent
================================

If you have first line indent enabled in your manuscript build settings, you probably want to
disable it for text in verses. Adding any alignment tags will cause the first line indent to be
switched off for that paragraph.

:bdg-info:`Example`

The following text will always be aligned against the left margin:

.. code-block:: md

   I am the very model of a modern Major-General <<
   I've information vegetable, animal, and mineral
   I know the kings of England, and I quote the fights historical
   From Marathon to Waterloo, in order categorical
