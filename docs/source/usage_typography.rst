.. _a_typ:

*******************
Typographical Notes
*******************

.. _Prime: https://en.wikipedia.org/wiki/Prime_(symbol)
.. _thin space: https://en.wikipedia.org/wiki/Thin_space
.. _Quotation Mark: https://en.wikipedia.org/wiki/Quotation_mark
.. _Modifier letter apostrophe: https://en.wikipedia.org/wiki/Modifier_letter_apostrophe

novelWriter has some support for typographical symbols that are not usually easily available in
many text editors. This includes for instance the proper unicode quotation marks, dashes, ellipsis,
thin spaces, etc. All these symbols are available from the **Insert** menu, and via
keyboard shortcuts. See :ref:`a_kb_ins`.

This chapter provides some additional information on how novelWriter handles these symbols.


.. _a_typ_notes:

Special Notes on Symbols
========================

This section contains additional notes on the available special symbols.


Dashes and Ellipsis
-------------------

With the auto-replace feature enabled (see :ref:`a_ui_edit_auto`), multiple hyphens are converted
automatically to short and long dashes, and three dots to ellipsis. The last auto-replace can
always be reverted with the undo command :kbd:`Ctrl+Z`, reverting the text to what you typed before
the automatic replacement occurred.

In addition, "Figure Dash" is available. The Figure Dash is a dash that has the same width as the
numbers of the same font, for most fonts. It helps to align numbers nicely in columns when you need
to use a dash in them.


Single and Double Quotes
------------------------

All the different quotation marks listed on the `Quotation Mark`_ Wikipedia page are available, and
can be selected as auto-replaced symbols for straight single and double quote key strokes. The
settings can be found in **Preferences**.

Ordinarily, text wrapped in quotes are highlighted by the editor. This is meant as a convenience
for highlighting dialogue between characters. This feature can be disabled in
**Preferences** if this feature isn't wanted.

The editor distinguishes between text wrapped in regular straight double quotes and the
user-selected double quote symbols. This is to help the writer recognise which parts of the text
are not using the chosen quote symbols. Two convenience functions in the **Format** menu
can be used to re-format a selected section of text with the correct quote symbols.


Single and Double Prime
------------------------

Both single and double prime symbols are available in the **Insert** menu. These symbols
are the correct symbols to use for unit symbols for feet, inches, minutes, and seconds. The usage
of these is described in more detail on the Wikipedia Prime_ page. They look very similar to single
and double straight quotes, and may be rendered similarly by the font, but they have different
codes. Using these correctly will also prevent the auto-replace and dialogue highlighting features
misunderstanding their meaning in the text.


Modifier Letter Apostrophe
--------------------------

The auto-replace feature will consider any right-facing single straight quote as a quote symbol,
even if it is intended as an apostrophe. This also includes the syntax highlighter, which may
assume the first following apostrophe is the closing symbol of a single quoted region of text.

To get around this, an alternative apostrophe is available. It is a special Unicode character that
is not categorised as punctuation, but as a modifier. It is usually rendered the same way as the
right single quotation marks, depending on the font. There is a Wikipedia article for the
`Modifier letter apostrophe`_ with more details.

.. note::
   On export with the **Build Manuscript** tool, these apostrophes will be replaced
   automatically with the corresponding right hand single quote symbol as is generally recommended.
   Therefore it doesn't really matter if you only use them to correct syntax highlighting.


Special Space Symbols
---------------------

A few variations of the regular space character is supported. The correct typographical way to
separate a number from its unit is with a `thin space`_. It is usually 2/3 the width of a regular
space. For numbers and units, this should in addition be a non-breaking space, that is, the text
wrapping should not add a line break on this particular space.

A regular space can also be made into a non-breaking space if needed.

All non-breaking spaces are highlighted with a differently coloured background to make it easier to
spot them in the text. The colour will depend on the selected colour theme.

The thin and non-breaking spaces are converted to their corresponding HTML codes on export to HTML
format.
