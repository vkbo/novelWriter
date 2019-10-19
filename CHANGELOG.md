# novelWriter ChangeLog

## Version 0.3 [2019-10-19]

**User Interface**

* Added project export feature with a new GUI dialog and a number of export setting. The export feature currently only exports to a plain text file. PR #55

## Version 0.2.3 [2019-10-06]

**User Interface**

* The search feature now also allows for replacing text, so the basic search/replace tools in now complete. PRs #51 and #52
* All icons have been removed from the menu, and the dark theme has received a new set of basic icons. They are not very fancy, so will perhaps be replaced by a proper icon set later. PR #53

## Version 0.2.2 [2019-09-29]

**Bug Fixes**

* Fixed a bug where loading a config file with the dictionary language set to "none", or presumably an missing dictionary, would trigger a fatal error. PR #47

**User Interface**

* Added a basic search function for the currently open document. This is a simple interface to the find command that exists in the Qt document editor. It will be extended further in the future. PR #49

## Version 0.2.1 [2019-09-14]

**Bug Fixes**

* The _Tomorrow_ theme had the wrong set of colours. PR #39

**Documentation**

* Added the backup feature to the documentation. PR #40

**User Interface**

* The auto-replace list in project settings is now sorted alphabetically. PR #43
* Added version checking of the Qt5 and PyQt5 dependencies. Non-essential functionality that depends on very recent versions of Qt5 are now switched off if version is too low. Currently only affects the custom tab stop length, which requires version 5.10. this resolves issue #44. PR #45

**Code Improvements**

* Minor changes to the About novelWriter dialog and to how backup filenames are generated. PR #41

## Version 0.2 [2019-06-27]

**Documentation**

* Added documentation in English. The help file opens in the document view pane when the user presses `F1` or selects it from the Help menu. #27

**Themes**

* Complete rewrite of how syntax highlighting and GUI themes are handled. These are now set separately, and the dark theme uses QPalette to handle the dark colours, which makes the dark theme a lot more portable between operating systems. #34 and #35
* Added the five Tomorrow colour themes to list of syntax highlighter themes. #34 and #35

**User Interface**

* Added a preferences dialog for the program settings. No longer necessary to edit the config file. #30
* The document viewer remembers scroll bar position when pressing `Ctrl+R` on a document already being viewed. #28
* Removed version number from windows title. #28
* The auto-replace items in Project Settings are now editable. #29
* Changed how document margins are handled. This implementation works better and drops the difference between horizontal and vertical margins in favour of using the QDocument margin setting. #33

**Code Improvements**

* Spell checking is now handled by a standard class that can be subclassed to support different spell check tools. This was done because pyenchant is no longer maintained and having a standard wrapper makes it easier to support other tools. #31

## Version 0.1.5 [2019-06-08]

**Bug Fixes**

* Closing the application with the window X button, and selecting No on the dialog, still closed the application. Properly handled the close event now so that the closing is cancelled. #21
* Many of the menu option would cause novelWriter to exit or otherwise make mistakes when clicked if no project was open. They all check for this now. #23

**Timeline**

* Added an index to the project that holds the position of all headers in the novel part of the project and all tags set in the notes part. It also holds all the links from novel files to notes. The relationship can be viewed in a new TimeLineView GUI. It's in the tools menu, and can also be opened with `Ctrl+T`. #22
* The spell checker now used this index to highlight keywords/value sets. If the keyword or value is not valid, it will not be highlighted and will instead have a wiggly line under it. This also checks that references point to valid tags. For this to work, the index has to be up to date. The index of a file is saved when the file is saved, but the entire index can be rebuilt by pressing `F9`. #22

**Status Bar**

* Redesign of the status bar adding project and session stats as well as a session timer. #21
* Project word count is written to the project file, which is needed for the session word count. #21
* Closing a project now clears the status bar. #21

**Editor**

* Spell checker now ignores lines staring with `@` and words in all uppercase. #21
* A document can be closed, which also clears it from last edited document in the project file. I.e. it is not re-opened on next start. #21
* Tab width is now by default 40 pixels, and can be set in the config. #21

## Version 0.1.4 [2019-05-25]

**Bug Fixes**

* Fixed a bug where an item had to be selected in the tree view for a root item to be created. #16.

**User Interface**

* The main area can now be split into two, with the document editor on the left and a document viewer on the right. PR #13.
* The list of novel document status and plot element importance levels can now be edited through the Project Settings fialog. The values are per project, and saved in the main project XML file. PR #17.
* Cleaned up opening and closing projects, as well as how new projects are created. A new project can also not be saved in a folder already containing a novelWriter project. That was previously possible. resulting in the old XML file being overwritten. PR #18.
* Some minor GUI improvements were added, PR #19:
  * Pressing `F2` also opens the edit item dialog, like `Ctrl+E` does.
  * When the document editor and viewer split slider is moved, the editor resizes properly.
  * The document viewer can be closed, expanding the editor to the full window size again.
  * A project can be closed with `Ctrl+Shift+W`, and the menu entry has an icon.
  * Exit button/menu now asks if you want to close.

**Themes**

* The colours for syntax highlighting can now be edited in a config file in the themes folder. The main GUI css file also lives in the same folder. The default theme lives in the default subfolder, and more folders can be added. Switching themes involve changing the theme setting in the main config file to the name of the themes subfolder. PR #15.

**Code Improvements**

* Loading the project with the items in the wrong order is possible. That is, the child item is stored before its parent. A saved file should not ever be like that, but an edited file might. Even if the file shouldn't be edited manually. PR #16.

## Version 0.1.3 [2019-05-18]

**User Interface**

* Cursor position is now saved when a document is saved, and restored when the document is opened. PR #12.

**Test Suite**

* Major upgrades to the test suite, now also testing GUI elements. Coverage at 73%. PRs #9 and #11.

## Version 0.1.2 [2019-05-12]

**Bugfixes**

* Fixed a critical GUI bug when trying to create new folders and files in the tree.
* Caught a bug when creating a new file, but novelWriter couldn't figure out what class the parent item had and returned a None. Could not recreate the bug, but added a check for it.

**Code Improvements**

* Changed the way user alerts are generated, and added the alert levels to an enum class named `nwAlert`. Also added a new level named `BUG`.

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
