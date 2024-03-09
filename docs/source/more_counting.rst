.. _a_counting:

********************
Word and Text Counts
********************

This is an overview of how words and other counts of your text are performed. The counting rules
should be relatively standard, and are compared to LibreOffice Writer rules. The counts provided in
the app on the raw text are only meant to be approximate.


Text Word Counts and Stats
==========================

These are the rules for the main counts available for for each document in a project.

For all counts, the following rules apply.

#. Short (–) and long (—) dashes are considered word separators.
#. Any line starting with ``%`` or ``@`` is ignored.
#. Trailing white spaces are ignored, including line breaks.
#. Leading ``>`` and trailing ``<`` are ignored with any spaces next to them.
#. Valid shortcodes and other commands wrapped in brackets ``[]`` are ignored.
#. In-line Markdown syntax in text paragraphs is treated as part of the text.

After the above preparation of the text, the following counts are available.

**Character Count**
   The character count is the sum of characters per line, including leading and in-text white space
   characters, but excluding trailing white space characters. Shortcodes in the text are not
   included, but Markdown codes are. Only headers and text are counted.

**Word Count**
   The words count is the sum of blocks of continuous character per line separated by any number of
   white space characters or dashes. Only headers and text are counted.

**Paragraph Count**
   The paragraph count is the number of text blocks separated by one or more empty line. A line
   consisting only of white spaces is considered empty.
