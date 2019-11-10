# novelWriter ChangeLog

## Version 0.4.1 [2019-11-10]

**Features**

* If no external spell check package is available, novelWriter can now fall back to use a simple spell checker based on word similarity comparison provided by the Python standard package distlib. That means spell checking is always available, although the distlib-based spell checker is both slow and lacks many features of other packages. This feature comes with a general English dictionary, and a GB and US dictionary. These are just lists of correct words provided by aspell. PR #130.
* Language information (spell checker) is now shown on the status bar. In addition, the timer has been converted to monospace font and received an icon. PR #136.
* The new icons exist in both dark and neutral mode, and the mode can be set in the preferences. This makes it easier to see the icons on a dark system theme. PR #135.
* Distraction free mode, key shortcut `F8`, and full screen mode, shortcut `F11`, are now available. This PR also fixes some issues with rescaling of text margins when windows or panels are resized. PR #137.

**User Interface**

* Most text boxes now have a character limit. Before, the only limit was the limit set by Qt itself of ~32k characters. PR #126.
* Key combination `Ctrl+G` is now an alternative to `F3`, forward search, and vice versa for backwards search. This makes more sense on macOS. PR #126, issue #124.
* The shortcut for the replace feature is now `Cmd+=` on macOS, and remains `Ctrl+H` on Linux and Windows. PR #126, issue #124.
* The sample project in the source code has been improved to better show the features of novelWriter as they currently are. The old text was a bit out of date. The new text also explains the features it demonstrates. PR #132.

**Bug Fixes**

* Fixed a bug where a long file label would expand the tree pane due to the details panel expanding. The label itself will no longer show more than 100 characters, and is word wrapped. PR #122, issue #120.

**Code Improvements**

* The code has been reorganised, import headers been cleaned up, and the code made more or less PEP8 compliant. PRs #118, #119, and #138.
* The dependency on the pycountry package has been dropped. The feature based on it now uses an internal list of country codes for describing spell checker languages. PR #129.
* The themes manager has been improved, and the loading of icons now supports a number of fallback steps to ensure something is shown in most cases. The final fallback is the system's own icon theme. PR #135.

## Version 0.4 [2019-11-03]

**Features**

* The export dialog now allows limited support for exports using Pandoc. The Pandoc conversion is run as a stage two of the export process. Pandoc integration is fickly on Windows, but works well on Linux. PRs #82 and #104
* The editor now supports Markdown standard hard line breaks, and export these correctly to the various file formats and to the document view pane. Hard line breaks can be inserted by either appending two or more spaces to the end of a line, or by pressing `Shift+Enter`. PR #83
* The editor now supports and preserves non-breaking spaces. Unfortunately, the preservation of these spaces on save and reload is dependent on Qt 5.9 or larger. Non-breaking spaces are preserved on export to html and LaTeX. PR #87
* An option to show tabs/spaces and line endings in the document editor has been added to the Preferences dialog. PR #90
* The document view pane now has a "Referenced By" panel at the bottom, showing links to all documents referring back to the document being viewed. The panel is collapsible, and has a sticky option that will prevent it from updating if links are followed. PRs #109 and #110
* The tag and reference system no longer has any restrictions on file class. That is, any file can have tags and references, and they are indexed by the indexer and displayed as links in the document view pane. The timeline view behaves as before, only listing active Novel files. PR #114
* A new root folder type and keyword for "Entities" has been added. These can be useful for describing plot elements fitting under such a category. PR #115

**User Interface**

* Tags and references in the editor are now "clickable" in the sense that pressing `Ctrl+Enter` with the cursor on them will open the reference in the view pane. PR #98
* Warnings triggered when the user tries to use features with missing package dependencies will now provide a link to the package website. PR #86
* Adding the `~` character in file path boxes is now expanded to the user's home directory. PR #94
* The recent projects submenu no longer has a number prefix, and a "Clear Recent Projects" option has been added. PRs #86 and #94
* Syntax themes based on Night Owl and Light Owl themes have been added. PR #97
* Read-only files now have a notification popping up at the top of the edit pane, and the files are actually not editable. PR #106
* Tabs are now properly exported in formats where this makes sense. For plain text files, a tab is converted to four spaces. For html exports they are converted to a long space, equivalent to four spaces. PR #113
* A toggle button in the Document menu now allows displaying file comments in the document view panel. PR #115

**Bug Fixes**

* Some issues with unicode conversion and LaTeX export have been addressed, but the escaping of unicode characters is prone to errors. The user should be careful with using special symbols if export to LaTeX is intended. The package `latexcodec` should be able to handle Latin based, language specific characters. PRs #73, #79.
* Fixed some long-standing issues with running novelWriter on Windows. The config folder requires a set of two folders to be created on first use, which the config class did not expect. This is now resolved. In addition, Python does not default to utf-8 when writing files on Windows, so all open statements now have encoding defined. Failing to open files also had the risk of truncating them. This has been avoided by distinguishing new files from broken files. PR #81
* Dark theme was not rendering properly on multiple platforms. This was resolved by forcing the QT5 style to "Fusion", which allows further formatting by the novelWriter themes code. The user can override the Qt styling option through the `--style=` flag on the command line. PR #96
* The behaviour of files in the Trash folder has been fixed. These are now read only. PR #106
* Fixed a bug where the last line of a title or partition page would be ignored on export. PR #113
* Drag and drop onto the root level of the tree has been disabled. This was anyway only allowed for root folder items, but it was tricky to enforce this properly for other files. In order to move root folders around now, the move up and down features need to be used instead. #115

**Installation**

* A script for `pyinstaller` has been added, making it possible to generate standalone executables of novelWriter on at least Windows and Linux. PR #91
* novelWriter has been makde `pip install` ready. PRs #107 and 108

## Version 0.3.2 [2019-10-27]

**Documentation**

* The documentation has been rewritten and added to the Read the Docs website. Pressing `F1` or `Help > Documentation` in the menu, opens the novelWriter documentation page. PRs #68 and #69.

**User Interface**

* Filters have been added to the Timeline View windows so unused tags can be hidden, and it's possible to select only certain classes of tags to display. PRs #61 and #62
* The dialog boxes for Timeline View and Session Log now remember the filter choices from previous instance for the same project. PR #62
* When having a document open in the editor, text can be imported into it from a plain text file. No formatting conversion of the imported text is performed. That is up to the user. However, this allows for importing novelWriter documents from other projects or from a previous export, partially addressing request in issue #63. PR #65
* The Export feature now includes exporting to LaTeX, which allows building PDFs with pdflatex or other tools. PR #73
* Export of a novelWriter flavour markdown file is also supported. This file can be imported back in as-is, and almost completes an export-edit-import cycle. A split document into multiple files feature will be added soon. PR #73

## Version 0.3.1 [2019-10-20]

**Bug Fixes**

* The backup request dialog should pop up on any change to the project during the last session, not just on unsaved changes. PR #58
* The regex that searches for words for the spell check highlighter was not including unicode characters, so it would underline parts of words using unicode characters even if the word was spelled correctly. PR #58
* When having unsaved changes in an open document, while changing editor configuration options, the document would be reloaded from disk when the changes were applied. This means the unsaved changes were lost. The document is now saved before the editor is re-initialised. PR #58

**User Interface**

* Added a GUI to display the session log. The log has been around for a while, and records when a project is opened, when it's closed, and how many words were added or removed during the session. This information is now available in a small dialog under `Project > Session Log` in the main menu. PR #59
* The export project feature now also exports the project to Markdown and HTML5 format. PR #57

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
