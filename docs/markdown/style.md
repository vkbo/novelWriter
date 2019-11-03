# Code Style Guide

The source code of novelWriter broadly follows the style guide [PEP8](https://www.python.org/dev/peps/pep-0008/), but with a few modifications and exceptions.

### Source Code Exceptions

* Methods are camelCase, not underscore based.
  The reason is partially because of the maintainers personal preference, and partially because that is what Qt5 and PyQt5 uses.
  The maintainer generally, across multiple programming languages, uses underscores for defining namespaces.
* The maximum length of a code line is 99 characters, not 79.
  The reason for this is that novelWriter is almost entirely made up of classes, meaning nearly all lines of code already have 8 leading spaces.
  A 79 character limitation is too strict, and causes too many wrapped lines.
  99 characters is suitable for GitHub diff readability, and therefore the preferred limit.
  It is also permitted under PEP8 as the maximum.
  Comments and docstrings should comply with the 72 character limit.
* Aligning code with additional spaces is acceptable in those cases where it improves readability.
  Otherwise, the PEP8 standard should be applied.

### Documentation

The documentation does not adhere to the 80 character limit either.
The standard used in documentation is one line break after each sentence.
This is an alternative style that greatly improves readability of diffs as re-wrapping text is not needed when inserting new text in paragraphs.
Instead, the diff will show changes to each sentence.
