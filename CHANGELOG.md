# novelWriter ChangeLog

## Version 0.1.1 [2019-05-12]

**User Interface**

* Rewritten the spell check context menu. The previous implementation was adapted from a Qt4 example, but could be improved a great deal. It now also doesn't have the default context menu, and allows for adding words to personal word list. Spell checking can also be enabled and disabled from the menu, and re-run on a the current document. PRs #1 and #3 (V.K. Berglyd Olsen)

**Test Suite**

* Added a unit test framework based on `pytest`. This currently checks basic opening and saving of the main config file and the main project file. PR #2 (V.K. Berglyd Olsen)

## Version 0.1 [2019-05-10]

This is the initial release of a working version of novelWriter, but with very limited capabilities. So far, the following has been implemented:

* A document tree with a set of pre-defined root folders of a given sett of classes for different purposes for novel writing. That is, a root item for the novel itself, one for charcaters, plot elements, timeline, locations, objects, and a custom one.
* A plain text editor with a simplified markdown format that allows for four levels of titles, and bold, italics and underline text.
  * In addition, the format supports comments with lines starting with a `%`.
  * It also allows for keyword/value sets staring with the character `@`. These will later be used to link documents together as tags point to other documents. For instance, a scene file can point the keyword `@POV:name` to a character file with the keyword `@THIS:name`.
* The text editor has a set of autoreplace features:
  * Dashes are made by combining two or three hyphens.
  * Three dots are replaced with the ellipsis.
  * Straight quotes with your quote format of choice.
* The text editor also allows for wrapping either selected text, or the word under the cursor, in:
  * Bold, italics, or underline tags.
  * Single, or double quotes.
