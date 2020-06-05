# novelWriter ChangeLog

## Version 0.8 [2020-xx-xx]

**User Interface**

* A details panel below the Outline tree view has been added. The panel shows all the information of a selected row in the tree view above, including hidden columns, and some additional information. The tags and references also become clickable links that when clicked will open in the document viewer. PR #281.
* Added a context menu to the project tree for easier access to some of the most use actions on the tree. PR #282.
* Improved the support for High DPI screens. Margins and box sizes that are hardcoded should now scale. User settings should also scale back and forth when switching between scale factors. Issue #280, PR #285.

**Project Structure**

* The way GUI states of switches, column widths, etc., is saved has been improved a bit during the High DPI updates. PRs #285 and #286.
* Some settings have been moved around to more appropriate sections in the project XML file. The project load function still reads the values from the previous location if opening an older project file. PR #288.

## Version 0.7 [2020-06-01]

**Bugfixes**

* Fixed a bug where novelWriter might crash if a file is deleted immediately after being created, and also additional points-of-failure if the project was new. PR #267.

**User Interface**

* The back-references list in the project view panel now shows references to any tag in the open document, not just the first tag. Issue #227, PR #234.
* Clicking a tag now tries to scroll to the header where the tag is set. The index needed a couple of minor changes for this feature, so this will invalidate the old index for a project saved with an older version, and require a new to be built. This is done automatically. PR #234.
* Moved the Close button on the "Build Novel Project" dialog to the area with the other buttons since we anyway increased the size of that area. PR #256.
* Updated the unit for Preferences > Editor > Big document limit from `kb` to `kB`. Issue #258, PR #260.
* Added Typicons-based coloured icon set also for light GUI background. PR #265.
* The export check mark that was added to the Flags column in the project tree in Version 0.6 has been moved to its own column, and been replaced with a proper icon. The details panel below it has been updated as well. PR #268.
* Icon sizes are now calculated based on the size of the text, and all text and icons should scale relative to the default GUI font size. PR #268.
* The font family and size of the main GUI font can now be changed in Preferences. For Windows, this defaults to Cantarell 11pt, which is now shipped with novelWriter. On other systems it defaults to the system font. Special accommodations had be made for Ubuntu where the font size of the tree widget was not updated automatically (Issue #273). PRs #269, #270, #274 and #275.
* There are no Monospace fonts on the main GUI any more. Where fixed width is needed, the size is calculated beforehand with Qt's font metrics class. PR #271.
* Fonts are now selected via the system's font dialog rather than the font combo box. PR #270.
* Word, character and paragraph counts are now updated on the project tree details panel if the file currently being edited is also selected in the tree. PR #272.
* The Build Novel Project dialog now shows the previous generated content when it's opened. PR #272.
* The Build Novel Project tool can now export the HTML and NWD output into a JSON data file. This file is convenient if the user wants to post-process the output with for instance Python, or one of the other numerous languages that can read JSON files. PR #272.

**Project Structure**

* The project folder structure has been simplified and cleaned up. We also now freeze the main entry values in the main XML file. The XML file is now given version 1.1, and no further core changes to its structure will be made without bumping this version. We're also locking it to only be opened by version 0.7 or later. An old project file is converted on first open. PRs #253 and #261.
* When a project is closed, two table of contents files are written to the project folder. They are named `ToC.txt` and `ToC.json` and are there for the user's convenience if they want to find a specific file from the project in the data folders. As discussed in Issue #259, PRs #261 and #262.
* The expanded node flag from the project tree was also saved for file entries, which cannot actually be expanded. These flags are no longer saved in the XML file. PR #261.

**Other Changes**

* Dropped the usage of `.bak` copies of document files. This was the old method to ensure the document data was written successfully, but it uses twice the storage space. Instead, writing via a temp file is the current safe way to save files. PR #248.
* The project class now records the accumulated time in seconds a project has been opened. This data is not yet displayed anywhere, but it is being tracked in the project XML file. PR #261.

**Test Suite**

* Added tests for Build Novel Project, Merge Folder and Split Document tools. PRs #263 and #264.


## Version 0.6.3 [2020-05-28]

**Bugfixes**

* It was possible to have the backup folder set to the same folder as the project, resulting in an infinite loop when `make_archive` was building the zip file. This crash of paths is now checked for before moving to the archive step. Issue #240, PR #241.
* Fixed an issue with the Build Novel Project tool on Ubuntu 16.04 LTS where the dialog wouldn't open. Issue #243, PR #246.

**User Interface**

* Renamed the "Generate Preview" button on the "Build Novel Project" tool to "Build Novel Project". You must actually click this to be able to export or print. Issue #237, PR #238.
* Added font family and font size selectors to the "Build Novel Project" tool. You may want a different print font than used in the editor itself. Issue #230, PR #238.
* Removed the "Help" feature in "Build Novel Project" and instead added detailed tooltips. Issue #250, PR #249.
* Changed the title formatting codes for "Build Novel Project" to something less verbose. The old codes are translated automatically. Issue #247, PR #249.
* A margin of the viewport (outside the document) has been added to the document editor and viewer to make room for the document title bar. Previously, the title bar would sit on top of the document's top margin, which would sometimes hide text that would otherwise be visible (when scrolling). PR #236.
* Fixed an alignment issue for the status icon on the project tree details panel. Mentioned in #235, PR #239.
* Removed the `Xo` icon for NO_LAYOUT in the project tree details panel. Mentioned in #235, PR #239.
* Added a "Details" tab to the "Project Settings" dialog, which also lists the project path. Issue #242, PR #239.


## Version 0.6.2 [2020-05-28]

* Botched release. Replaced with 0.6.3. Crashes when Build Novel Project is opened.


## Version 0.6.1 [2020-05-25]

**Bugfixes**

* The Outline view now takes into consideration the exported flag, and does not show excluded files in the outline. PR #224.
* Page layout format was ignored when exporting project. The formatting of this layout has now been added. PR #224.
* If multiple headings were present in a file, the sorting of headings in the Outline view would follow a text sort not a numerical sort of the line numbers. That is, it would be sorted as "1", "10", "2", "20", etc. This has been fixed. PR #226.
* The text justification in the preview in the  Build Novel Project was following the main Preferences settings, not the Build settings. This did not affect the formatting of the exported file itself, but the preview is now made consistent with the build settings. Issue #228, PR #231.

**User Interface**

* Recent projects in the open project dialog can be removed from the list by hitting the delete key. PR #225.
* Moved the browse button to after the path box in the open project dialog. PR #225.

**Other Changes**

* The three remaining dependencies now have a minimum version set. PR #224.
* Moved the sample project up one folder level. PR #224.

**Documentation**

* The export page in the documentation erroneously stated that line breaks could be added to titles by adding `%\\%`. The correct syntax is `\\`. Issue #229, PR #231.


## Version 0.6 [2020-05-24]

**Bugfixes**

* Fixed a bug in validation of `@tag:` meta tags where one or more spaces before the `:` would still pass as a valid tag, but the keyword index array would be missing those spaces in its counter. This mainly affected the highlighting of keywords, which would be misaligned. PR #206.

**User Interface**

* The Export Tool has been removed and replaced by a new tool called "Build Novel Project". The new tool has the same filtering options as the Export Tool, but with more formatting options for titles. It also has a preview window to display the generated document. A Save As button provides exports to HTML, novelWriter Markdown, plain text, PDF and Open Document format. LaTeX export has not been ported over, and interfacing with Pandoc is no longer supported either. Although, as before, the HTML export can be converted with Pandoc to other formats outside of novelWriter. The new tool also supports printing. PRs #204, #220 and #221.
* The Project Settings, Preferences, Item Editor, Merge Documents, and Split Documents dialogs have been redesigned. The ones with tabs now have vertical tabs on the left with horizontal labels. The dialog design should be more compact, and have room for more tabs for future settings. PR #212.
* A new icon, as well as a mimetype icon for the project files, have been designed and added to the app. PRs #213 and #214.
* The About dialog has been completely redesigned to allow more information. PR #217.
* The Open Project dialog has been cleaned up and made more readable. The project paths have been moved out of the list, and are now displayed when an item is selected instead. Icons have been added, and the New project dialog can also be triggered from this dialog. PR #218.
* The document stats have been added to the details panel below the project tree. PR #219.


## Version 0.5.2 [2020-05-21]

**Bugfixes**

* When running on Windows 10, some of the buttons were missing icons. More fallback icons have been added to ensure that all current buttons have a fallback path that always ends in an icon. PR #211.

**User Interface**

* The statusbar has been redesigned a bit. The block icons showing document and project saved status have been replaced by LED icons. The statistics has been moved to a separate label, and most of the detailed stats moved to its tooltip. PR #210.
* Default icon theme is now `Typicons Grey Light`. PR #211.
* Clicking on the document header selects the document in the project tree, but this functionality has been enhanced to also ensure the document is expanded and visible in the tree. If it's scrolled out of view, the tree will scroll it into view. PR #215.
* Syntax highlighting of text in quotes can now be turned off in Preferences. PR #215.

**Core Functionality**

* Checking for version dependencies and a few packages (aside from PyQt5) is now done later in the start-up so that it is possible to alert the user with a dialog box instead of terminal error messages. PR #210.
* Made a few minor changes to the code so novelWriter can run with Python 3.4.3 and Qt 5.2.1, that is, it runs on last version of Ubuntu 14.04. This level of compatibility is not guaranteed to remain in the future, but for now, the changes have no impact on functionality. PR #210.


## Version 0.5.1 [2020-05-14]

**Bugfixes**

* Fixed a bug where only some of the text would be rendered in the editor window when a large text document was loaded. The text is there in the buffer, but the rendering process was interrupted by the function that recalculates margins. This recalculation was added with the document tiles in 0.5. The re-rendering of the text could be triggered by opening the search bar, indicating that it was caused by the shifting of the vertical document frame. PR #208.

**User Interface**

* The icon theme functionality of novelWriter has been reworked. For the default system theme, very little has changed. It should still load whatever the system provides, but this doesn't work for all icons on Windows 10 for instance. It is now possible to select between three icon themes in the Preferences dialog, independent of the GUI theme. Using a theme breaks the dependency on the operating system to provide standard icons. Qt provides some, but not all needed by novelWriter. PR #207.
* Added a check that warns if the project file was saved with a newer version of novelWriter as that may cause meta information to be lost. This warning will remain there until the file format is finalised. This is an issue with preserving certain settings, not the project structure itself. PR #205

**Debugging**

* Reduced the number of command line switches needed for debug runs. PR #205.


## Version 0.5 [2020-05-09]

This release of novelWriter has a number of feature updates, bringing it one step closer to initial feature completeness for a version 1.0 release.

In the pipeline for 1.0 is a completely new export tool with improved and added options, including printing. Further improvements are also planned for the new Outline View added in this version. When these additions are completed, novelWriter will start moving towards a 1.0 release via release candidates. I'm hoping to wrap up this year and a half long stage of initial development soon so that I can spend more time using it than creating it.

**Additional thanks** to @countjocular for PRs #173 and #174, and to @johnblommers for all the helpful feedback and issue reports for the new features added in this, and previous releases.

### Noteable Changes

* The Timeline View dialog is now gone. Instead, the main window area has been split into two tabs. The first, the "Editor", contains the Document Editor and Viewer panels. The second, the "Outline", contains a new Outline View of the novel part of the project, broken down into a tree view of all the project headings. All meta data associated with each part of the novel can be viewed in further columns, selectable from a drop down menu by right-clicking the header. These columns can also be rearranged.
* Both the Editor and Viewer panels now have a header showing the document label as seen in the Project Tree. Optionally, the full path of the document can be viewed. Clicking this header will select the document in the Project Tree, making it easier to find where the document belongs in the structure.
* A project load dialog has been added when novelWriter is launched. It will show you your recently opened projects, let you browse for those that aren't listed, or create a new project. More features will be added to this dialog later on.
* The Preferences dialog has been completely redesigned to make it easier to find the various settings and understand what they do.

### Detailed Changelog

**Features**

* An Outline View panel has been added to the main GUI window. The Outline View can show all meta data associated with a novel heading in a column-wise manner. The Timeline View feature has been dropped in favour of the new Outline View. PRs #140, #181 and #191.
* A synopsis feature has been added. It allows a comment to be flagged as a synopsis comment to be picked up by the indexer and displayed in the GUI. Currently available in the Outline View. PRs #140 and #191.
* A document title bar has been added to the top of the editor and viewer. These show the document label as seen in the project tree. Optionally, the full document path can be shown. Clicking the title will highlight the document in the project tree. PRs #192 and #194.

**User Interface**

* A Project Load dialog has been added, which pops up when novelWriter is launched. It allows for opening other recent projects, browse for projects, or start a new project. This replaces the former Open and New Project features, as well as the Recent Projects menu entry. PRs #177 and #183.
* The command line switches for debugging have been changed a bit. Higher level of debugging now includes the lower levels, preventing the need for specifying for instance both debug and verbose debug. PR #182.
* The Preference dialog has been completely redesigned. The options are now displayed vertically, in four tabs instead of two, and with more informative text explaining what they do. Some previously unconnected options have also been added. PR #193.

**Bug Fixes**

* The `install.py` script has been fixed to reflect changes in storage location of the themes. PR #174.
* Fixed a bug with launching Preferences without Enchant spell checking installed. PR #190.
* A minor issue with running backups with no backup path set has been fixed. The backups would be written into the source folder, or wherever novelWriter was launched from, which is a very messy fallback. PR #195.

**Documentation**

* Some outdated links and a number of typos and spelling errors have been corrected. PR #173.
* Documentation has been brought up to date with the current set of features of novelWriter. PR #202.

**Project Structure**

* Opening a project now writes a lock file to alert the user if the same project is opened more than once. The warning can be ignored if the user wants to proceed. PR #179.
* Two new meta tags have been added to the project file to store a counter for the number of times the project has been saved or autosaved. The meta information is not currently displayed in the GUI, but could be added to an About Project dialog in the future. The PR also adds checks to ensure XML attributes exist before attempting to load them. PR #180.
* A single line of document meta data is now written to the top of document files. They mainly serve to identify the file content if one opens the file directly in an external editor, but also assist the Orphaned Files tool to identify the files when they are found, but missing from the project tree. PRs #200 and #201.

**Code Improvements**

* For the Outline View, the `NWIndex` class has been restructure and extensively rewritten. It is more fault tolerant, and will automatically rebuild a corrupt index loaded from cache. PR #140.
* The way that dialog options (which options were selected last time a dialog was open) has been rewritten. All data is now stored in a single JSON file in the project meta folder. PR #175.
* Since the config class is instanciated before the GUI, error reporting to the user was tricky. An error cache has now been added to allow non-critical errors to be displayed after the GUI is built. PR #176.
* All source files now have the minimal GPLv3 license note at the top. PR #188.
* Also added license info to the command line output. PR #189.
* Large chunks of the code has been restructured. Mainly the non-GUI parts, which have mostly been merged into a new `core` folder. Several classes which are only used by a single object have been merged into the same file, reducing the total number of source files a bit. PR #199.


## Version 0.4.5 [2020-02-17]

**Features**

* A project can now be opened from the command line by providing the project path to the launching script. PRs #164 and #166.

**User Interface**

* Added functionality to split a document into a folder of multiple documents, and also to merge a folder of documents into a single document. PRs #159 and #163.
* It is now possible to permanently delete files from the Trash folder. This can be done file-by-file or by using the Empty Trash option in the menu. PRs #159 and #163.
* When running the spell checker, a wait cursor is displayed. This will alert the user that novelWriter is working on something when, for instance, a very large document is opened and initial spell checking is running. PR #158.

**Bug Fixes**

* Fixed a few keyboard shortcuts that were not working in distraction free mode. PR #157.
* Added a check to ensure the user does not drag and drop an item into the Orphaned Items folder. Since this folder is not an actual project item, novelWriter would crash when trying to change the dropped item's parent item to the Orphaned Items folder. Now, instead, the drop event is cancelled if the target folder is Orphaned Items. PR #163.

**Code Improvements**

* The way project files are saved has been altered slightly. When a project file or document file is saved, the data is first streamed to a temp file. Then the old storage file is renamed to .bak, and and the temp file is renamed to the correct storage file name. This ensures that the storage file is only replaced after a complete and successful write. PR #165.
* The cache folder has been removed. It was used to store the 10 most recent versions of the project file. Instead, the previous project file is renamed to .bak, and can be restored if opening from the latest project file fails. Any additional restore capabilities should be ensured by backup solutions, either the internal simple zip backup, or other third party tools. PR #165.
* The dependency on the Python package `appdirs` has been dropped. It was used only for extracting the path to the user's config folder, a feature which is also provided by Qt. PR #169.


## Version 0.4.4 [2020-02-17]

* Botched release. Replaced with 0.4.5.


## Version 0.4.3 [2019-11-24]

**User Interface**

* Added keyboard shortcuts and menu entries for formatting headers, comments, and removing block formats. PR #155.
* Disable re-highlighting of open file when resizing window. This is potentially a slow process if the spell checker is on and the file is large. There is no need to do this just for reflowing text, so it is now disabled on resize events. Issue #150, PR #153.
* Improved the speed of the syntax highlighter by about 40% by not using regular expressions for highlighting block formats and by skipping empty lines entirely. PR #154.

**Bug Fixes**

* Fixed an issue when closing the import file dialog without selecting a file, the import would procede, but fail on file not found. The import is now cancelled when there is no file selected. PR #149.
* Fixed an issue with markdown export where it did not take into account hard line breaks. Issue #151, PR #152.
* Fixed a crash when running file status check when the project contains orphaned files. PR #152.


## Version 0.4.2 [2019-11-17]

**User Interface**

* Distraction free mode now also hides the menu bar, but all keyboard shortcuts used for editing remain active. The rest are disabled. PR #142.

**Bug Fixes**

* Fixed various issues with spell checking highlighting. The highlighting and the editor didn't always agree on what words were spelled wrong. PR #141.
* The status bar now shows what spell checking language is actually loaded. Previously, it just showed the language selected in the settings. That was a bit misleading as the available dictionaries can change due to the change in installed dictionary on the system. PR #145.


## Version 0.4.1 [2019-11-10]

**Features**

* If no external spell check package is available, novelWriter can now fall back to use a simple spell checker based on word similarity comparison provided by the Python standard package `difflib`. That means spell checking is always available, although the difflib-based spell checker is both slow and lacks many features of other packages. This feature comes with a general English dictionary, and a GB and US dictionary. These are just lists of correct words provided by aspell. PR #130.
* Language information (spell checker) is now shown on the status bar. In addition, the timer has been converted to monospace font and received an icon. PR #136.
* The new icons exist in both dark and neutral mode, and the mode can be set in the preferences. This makes it easier to see the icons on a dark system theme. PR #135.
* Distraction free mode, key shortcut `F8`, and full screen mode, shortcut `F11`, are now available. This PR also fixes some issues with rescaling of text margins when windows or panels are resized. PR #137.

**User Interface**

* Most text boxes now have a character limit. Before, the only limit was the limit set by Qt itself of ~32k characters. PR #126.
* Key combination `Ctrl+G` is now an alternative to `F3`, forward search, and vice versa for backwards search. This makes more sense on macOS. Issue #124, PR #126.
* The shortcut for the replace feature is now `Cmd+=` on macOS, and remains `Ctrl+H` on Linux and Windows. Issue #124, PR #126.
* The sample project in the source code has been improved to better show the features of novelWriter as they currently are. The old text was a bit out of date. The new text also explains the features it demonstrates. PR #132.

**Bug Fixes**

* Fixed a bug where a long file label would expand the tree pane due to the details panel expanding. The label itself will no longer show more than 100 characters, and is word wrapped. Issue #120, PR #122.

**Code Improvements**

* The code has been reorganised, import headers been cleaned up, and the code made more or less PEP8 compliant. PRs #118, #119, and #138.
* The dependency on the `pycountry` package has been dropped. The feature based on it now uses an internal list of country codes for describing spell checker languages. PR #129.
* The themes manager has been improved, and the loading of icons now supports a number of fallback steps to ensure something is shown in most cases. The final fallback is the system's own icon theme. PR #135.


## Version 0.4 [2019-11-03]

**Features**

* The export dialog now allows limited support for exports using Pandoc. The Pandoc conversion is run as a stage two of the export process. Pandoc integration is fickly on Windows, but works well on Linux. PRs #82 and #104.
* The editor now supports Markdown standard hard line breaks, and exports these correctly to the various file formats and to the document view pane. Hard line breaks can be inserted by either appending two or more spaces to the end of a line, or by pressing `Shift+Enter`. PR #83.
* The editor now supports and preserves non-breaking spaces. Unfortunately, the preservation of these spaces on save and reload is dependent on Qt 5.9 or later. Non-breaking spaces are preserved on export to html and LaTeX. PR #87.
* An option to show tabs/spaces and line endings in the document editor has been added to the Preferences dialog. PR #90.
* The document view pane now has a "Referenced By" panel at the bottom, showing links to all documents referring back to the document being viewed. The panel is collapsible, and has a sticky option that will prevent it from updating if links are followed. PRs #109 and #110.
* The tag and reference system no longer has any restrictions on file class. That is, any file can have tags and references, and they are indexed by the indexer and displayed as links in the document view pane. The timeline view behaves as before, only listing active Novel files. PR #114.
* A new root folder type and keyword for "Entities" has been added. These can be useful for describing plot elements fitting under such a category. PR #115.

**User Interface**

* Tags and references in the editor are now "clickable" in the sense that pressing `Ctrl+Enter` with the cursor on them will open the reference in the view pane. PR #98.
* Warnings triggered when the user tries to use features with missing package dependencies will now provide a link to the package website. PR #86.
* Adding the `~` character in file path boxes is now expanded to the user's home directory. PR #94.
* The recent projects submenu no longer has a number prefix, and a "Clear Recent Projects" option has been added. PRs #86 and #94.
* Syntax themes based on Night Owl and Light Owl themes have been added. PR #97.
* Read-only files now have a notification popping up at the top of the edit pane, and the files are actually not editable. PR #106.
* Tabs are now properly exported in formats where this makes sense. For plain text files, a tab is converted to four spaces. For html exports they are converted to a long space, equivalent to four spaces. PR #113.
* A toggle button in the Document menu now allows displaying file comments in the document view panel. PR #115.

**Bug Fixes**

* Some issues with unicode conversion and LaTeX export have been addressed, but the escaping of unicode characters is prone to errors. The user should be careful with using special symbols if export to LaTeX is intended. The package `latexcodec` should be able to handle Latin based, language specific characters. PRs #73 and #79.
* Fixed some long-standing issues with running novelWriter on Windows. The config folder requires a set of two folders to be created on first use, which the config class did not expect. This is now resolved. In addition, Python does not default to utf-8 when writing files on Windows, so all open statements now have encoding defined. Failing to open files also had the risk of truncating them. This has been avoided by distinguishing new files from broken files. PR #81.
* Dark theme was not rendering properly on multiple platforms. This was resolved by forcing the Qt5 style to "Fusion", which allows further formatting by the novelWriter themes code. The user can override the Qt styling option through the `--style=` flag on the command line. PR #96.
* The behaviour of files in the Trash folder has been fixed. These are now read only. PR #106.
* Fixed a bug where the last line of a title or partition page would be ignored on export. PR #113.
* Drag and drop onto the root level of the tree has been disabled. This was anyway only allowed for root folder items, but it was tricky to enforce this properly for other files. In order to move root folders around now, the move up and down features need to be used instead. #115.

**Installation**

* A script for `pyinstaller` has been added, making it possible to generate standalone executables of novelWriter on at least Windows and Linux. PR #91.
* novelWriter has been made `pip install` ready. PRs #107 and #108.


## Version 0.3.2 [2019-10-27]

**Documentation**

* The documentation has been rewritten and added to the Read the Docs website. Pressing `F1` or `Help > Documentation` in the menu opens the novelWriter documentation page. PRs #68 and #69.

**User Interface**

* Filters have been added to the Timeline View window so unused tags can be hidden, and it's possible to select only certain classes of tags to display. PRs #61 and #62.
* The dialog boxes for Timeline View and Session Log now remember the filter choices from previous instance for the same project. PR #62.
* When having a document open in the editor, text can be imported into it from a plain text file. No formatting conversion of the imported text is performed. That is up to the user. However, this allows for importing novelWriter documents from other projects or from a previous export, partially addressing request in issue #63. PR #65.
* The Export feature now includes exporting to LaTeX, which allows building PDFs with pdflatex or other tools. PR #73.
* Export of a novelWriter flavour markdown file is also supported. This file can be imported back in as-is, and almost completes an export-edit-import cycle. A split document into multiple files feature will be added soon. PR #73.


## Version 0.3.1 [2019-10-20]

**Bug Fixes**

* The backup request dialog should pop up on any change to the project during the last session, not just on unsaved changes. PR #58.
* The regex that searches for words for the spell check highlighter was not including unicode characters, so it would underline parts of words using unicode characters even if the word was spelled correctly. PR #58.
* When having unsaved changes in an open document, while changing editor configuration options, the document would be reloaded from disk when the changes were applied. This meant the unsaved changes were lost. The document is now saved before the editor is re-initialised. PR #58.

**User Interface**

* Added a GUI to display the session log. The log has been around for a while, and records when a project is opened, when it's closed, and how many words were added or removed during the session. This information is now available in a small dialog under `Project > Session Log` in the main menu. PR #59.
* The export project feature now also exports the project to Markdown and HTML5 format. PR #57.


## Version 0.3 [2019-10-19]

**User Interface**

* Added project export feature with a new GUI dialog and a number of export setting. The export feature currently only exports to a plain text file. PR #55.


## Version 0.2.3 [2019-10-06]

**User Interface**

* The search feature now also allows for replacing text, so the basic search/replace tools in now complete. PRs #51 and #52.
* All icons have been removed from the menu, and the dark theme has received a new set of basic icons. They are not very fancy, so will perhaps be replaced by a proper icon set later. PR #53.


## Version 0.2.2 [2019-09-29]

**Bug Fixes**

* Fixed a bug where loading a config file with the dictionary language set to `None`, or presumably a missing dictionary, would trigger a fatal error. PR #47.

**User Interface**

* Added a basic search function for the currently open document. This is a simple interface to the find command that exists in the Qt document editor. It will be extended further in the future. PR #49.


## Version 0.2.1 [2019-09-14]

**Bug Fixes**

* The _Tomorrow_ theme had the wrong set of colours. PR #39.

**Documentation**

* Added the backup feature to the documentation. PR #40.

**User Interface**

* The auto-replace list in project settings is now sorted alphabetically. PR #43.
* Added version checking of the Qt5 and PyQt5 dependencies. Non-essential functionality that depends on very recent versions of Qt5 are now switched off if version is too low. Currently only affects the custom tab stop length, which requires version 5.10. Issue #44, PR #45.

**Code Improvements**

* Minor changes to the About novelWriter dialog and to how backup filenames are generated. PR #41.


## Version 0.2 [2019-06-27]

**Documentation**

* Added documentation in English. The help file opens in the document view pane when the user presses `F1` or selects it from the Help menu. PR #27.

**Themes**

* Complete rewrite of how syntax highlighting and GUI themes are handled. These are now set separately, and the dark theme uses QPalette to handle the dark colours, which makes the dark theme a lot more portable between operating systems. #34 and #35.
* Added the five "Tomorrow" colour themes to list of syntax highlighter themes. PRs #34 and #35.

**User Interface**

* Added a preferences dialog for the program settings. No longer necessary to edit the config file. PR #30.
* The document viewer remembers scroll bar position when pressing `Ctrl+R` on a document already being viewed. PR #28.
* Removed version number from windows title. PR #28.
* The auto-replace items in Project Settings are now editable. PR #29.
* Changed how document margins are handled. This implementation works better and drops the difference between horizontal and vertical margins in favour of using the QTextDocument margin setting. PR #33.

**Code Improvements**

* Spell checking is now handled by a standard class that can be subclassed to support different spell check tools. This was done because pyenchant is no longer maintained and having a standard wrapper makes it easier to support other tools. PR #31.


## Version 0.1.5 [2019-06-08]

**Bug Fixes**

* Closing the application with the window X button, and selecting No on the dialog, still closed the application. Properly handling the close event now so that the closing is cancelled. PR #21.
* Many of the menu option would cause novelWriter to exit or otherwise make mistakes when clicked if no project was open. They all check for this now. PR #23.

**Timeline**

* Added an index to the project that holds the position of all headers in the novel part of the project and all tags set in the notes part. It also holds all the links from novel files to notes. The relationship can be viewed in a new TimeLineView GUI. It's in the tools menu, and can also be opened with `Ctrl+T`. PR #22.
* The spell checker now used this index to highlight keywords/value sets. If the keyword or value is not valid, it will not be highlighted and will instead have a wiggly line under it. This also checks that references point to valid tags. For this to work, the index has to be up to date. The index of a file is saved when the file is saved, but the entire index can be rebuilt by pressing `F9`. PR #22.

**Status Bar**

* Redesign of the status bar adding project and session stats as well as a session timer. PR #21.
* Project word count is written to the project file, which is needed for the session word count. PR #21.
* Closing a project now clears the status bar. PR #21.

**Editor**

* Spell checker now ignores lines staring with `@`, and words in all uppercase. PR #21.
* A document can be closed, which also clears it from last edited document setting in the project file. I.e. it is not re-opened on next start. PR #21.
* Tab width is now by default 40 pixels, and can be set in the config. PR #21.


## Version 0.1.4 [2019-05-25]

**Bug Fixes**

* Fixed a bug where an item had to be selected in the tree view for a root item to be created. PR #16.

**User Interface**

* The main area can now be split into two, with the document editor on the left and a document viewer on the right. PR #13.
* The list of novel document status and plot element importance levels can now be edited through the Project Settings dialog. The values are per project, and saved in the main project XML file. PR #17.
* Cleaned up opening and closing projects, as well as how new projects are created. A new project can also not be saved in a folder already containing a novelWriter project. That was previously possible, resulting in the old XML file being overwritten. PR #18.
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

* The cursor position is now saved when a document is saved, and restored when the document is opened. PR #12.

**Test Suite**

* Major upgrades to the test suite, now also testing GUI elements. Coverage at 73%. PRs #9 and #11.


## Version 0.1.2 [2019-05-12]

**Bugfixes**

* Fixed a critical GUI bug when trying to create new folders and files in the tree.
* Caught a bug when creating a new file, but novelWriter couldn't figure out what class the parent item had and returned a `None`. Could not recreate the bug, but added a check for it anyway.

**Code Improvements**

* Changed the way user alerts are generated, and added the alert levels to an enum class named `nwAlert`. Also added a new level named `BUG`.


## Version 0.1.1 [2019-05-12]

**User Interface**

* Rewritten the spell check context menu. The previous implementation was adapted from a Qt4 example, but could be improved a great deal. It now also doesn't have the default context menu, and allows for adding words to personal word list. Spell checking can also be enabled and disabled from the menu, and re-run on a the current document. PRs #1 and #3

**Test Suite**

* Added a unit test framework based on `pytest`. This currently checks basic opening and saving of the main config file and the main project file. PR #2


## Version 0.1 [2019-05-10]

This is the initial release of a working version of novelWriter, but with very limited capabilities. So far, the following has been implemented:

* A document tree with a set of pre-defined root folders of a given set of classes for different purposes for novel writing. That is, a root item for the novel itself, one for charcaters, plot elements, timeline, locations, objects, and a custom one.
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
