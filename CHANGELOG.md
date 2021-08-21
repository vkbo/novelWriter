# novelWriter Changelog

## Version 1.5 Beta 1 [2021-08-22]

### Release Notes

This is a beta release of the next release version, and is intended for testing purposes. Please be
careful when using this version on live writing projects, and make sure you make frequent backups.

This release introduces a new project file format, which has been given a file format version 1.3.
The project file and index is updated automatically when you open the project, which means you can
no longer open it in an older version of novelWriter.

You may also have to make a handful of changes in your novel documents as these are not updated
automatically. However, the changes are minimal and in any case only affects the way your
manuscript looks like when exported via the Build Novel Project tool. The details are described
below.

#### Novel Document Layouts

The main change in this release is the significant simplification of document layouts. Previously,
there were seven different layouts available for novel documents, in addition to the one layout for
project notes. The original intention of these layouts were partially to define some default
formatting behaviour when exporting your project, and partially a way to indicate whether a
specific document was a partition, chapter or scene.

With this release, all the seven layouts for novel documents have been merged into a single layout
called simply "Novel Document". The other layout for "Project Note" remains unchanged. The
functionality provided by the various novel layouts have been implemented in other ways, and a few
new formatting codes have been added to accommodate the formatting functionality lost with the
removal of the layouts. They are all available in the Format and Insert menu.

The changes you need to make to your project should be limited to altering a handful of titles and
maybe insert a page break code here and there. The only title formats you need to update are those
for the main novel title and for your unnumbered chapters, if you have any.

Novel titles need to be altered from `# Novel Title` to `#! Novel Title` and unnumbered chapters
from `## Chapter Name` or `## *Chapter Name` to `##! Chapter Name`. That is all. For inserting page
breaks, you can add a single line with the command `[NEW PAGE]` where you want the break to be
inserted. As before, page breaks are automatically inserted in front of all partition and chapter
titles.

You will find these changes described in more detail the documentation in the
"[Format 1.3 Changes](https://novelwriter.readthedocs.io/en/latest/usage_projectformat.html#a-prjfmt-1-3)"
section.

#### GUI Changes

Due to the above changes, the GUI has been altered a bit. The main changes are in the project tree.
These changes are also reflected in the details panel below the project tree, and to a lesser
extent in the Outline tab.

The layouts were previously a way to indicate the purpose of a specific novel document, like
whether it was a chapter or scene. With these layouts gone, the distinction is instead indicated by
other visual means.

The project index will now record the level of the first header of your document, and select a
different icon for documents with a partition, chapter or scene header. These are colour coded as
green, red and blue respectively. This only works for the coloured icon themes. The project notes
have also received a new icon, with a yellow colour code.

In addition, novel documents with a partition or chapter header will have the document label viewed
as bold and underlined. This feature can be disabled in Preferences if you want a cleaner look in
the project tree.

#### Other Changes

Several improvements have been made to the project index, which means the index will be
automatically rebuilt when you open a project for the first time in the new version. You will get a
notification about this.

The ODT export tool has also been improved. The code that writes out text paragraphs has been
rewritten and now conforms more closely to the Open Document standard. Most of these improvements
will not be noticeable to you as a user, but you may notice that the exported document will now
allow multiple consecutive spaces. Previously, two spaces, or more, would be concatenated into a
single space in the exported document.

### Detailed Changelog

**Bugfixes**

* Fix an inconsistency on the minimum required version of Qt and PyQt between the config files and
  the code. PR #846.
* Ensure that an item's status setting is parsed after its class when parsing the main project
  XML. This is just a precaution as the XML writing function always writes the class setting first.
  PR #852.
* On Windows, the Python icon is shown on the task bar when novelWriter is run directly from code.
  This has now been fixed by setting a unique application ID. Issue #860. PR #861.

**Open Document Exports**

* The ODT file writer class has been improved, and the code that writes out paragraphs and header
  section to the XML has been completely rewritten. The new algorithm is more robust and follows
  the open document standard more closely. It still diverts from the standard in a few cases, but
  these are the same points where Open Office and Libre Office diverts. Issue #783. PR #843.
* The previous exporter class would sometimes insert additional line breaks in the generated XML
  for paragraphs. This does not break with the open document standard, but it was unintentional and
  trivial to fix. PR #843.
* Some final clean-up was included in PR #859.

**Novel Layouts**

* All novel layouts, that is "TITLE", "PAGE", "BOOK", "PARTITION", "UNNUMBERED", "CHAPTER" and
  "SCENE" have been merged into a single layout "DOCUMENT". The "NOTE" layout remains unchanged.
  The special formatting of level one header on the title page and chapter headers for unnumbered
  chapters is now handled by a modified header formatting code. Issue #835. PR #837.
* A formatting code for manually inserting page breaks in the text has been added. In the process,
  similar codes were added to insert vertical spaces in the text. Issue #835. PRs #837 and #848.
* Dropping the layouts also triggered several changes to how project items are now displayed. The
  difference between document types is now indicated with a combination of icons and item label
  emphasis. The last column in the project tree also now only shows the item status or importance,
  not item class and layout. The Item Details panel below the tree has also been updated to show
  a usage description instead of layout as the last entry. Issue #835. PRs #847, #849 and #852.

**Other Features**

* A warning will pop up when you launch an alpha version of novelWriter. Since the main branch is
  now also the development branch, people may run novelWriter directly from source without checking
  out a release version. Alpha versions are not considered stable. PR #844.
* Two new settings have been added to Preferences. One to control how much information is shown in
  the last column of the project tree, and one to control whether emphasis is used to indicate
  which novel documents contain a level one or two header. PRs #847 and #852.
* The label on the first column of the project and novel trees have been renamed to "Project Tree"
  and "Novel Outline", respectively. PR #852.
* The Help > User Manual (Online) menu entry sends you to the online documentation, and the local
  documentation is handled by Help > User Manual (PDF), replacing the old Qt Assistant
  implementation. PRs #856, #859 and #862.

**Documentation**

* The documentation has been updated and extended to cover the new layout behaviour and to provide
  information and instruction on how to update the project with the new formats. PRs #850, #851 and
  #855.
* The technical section of the documentation has been updated, and information on how to run tests
  has been added. PR #859.

**Code Improvements**

* The loading and saving of user preferences in the config class has been improved a bit and the
  code modernised to the current recommended practice for the ConfigParser module. PR #826.
* The index class has been improved. Some data fields that were not being used have been dropped.
  In addition, a new function has been added that provides a custom indentation scheme for JSON
  files. The default indentation inserts far too many line breaks. The new function only indents up
  to a certain level. Indenting the JSON files is useful for people who use version control
  software on their projects. The limited indentation scheme reduces the number of diff lines as
  well as reduces the overall file size. PR #840.

----

## Version 1.4.1 [2021-07-27]

### Release Notes

This release fixes a couple of minor issue with some of the dialog boxes. The fix was accidentally
left out of release 1.4.

### Detailed Changelog

**Bugfixes**

* The way margins are determined in the paged dialogs used many places, including Preferences, has
  been improved. These margins would sometimes be set to zero when they shouldn't. PR #834.
* Dialogs that are non-modal are no longer duplicated when opened multiple times. Instead, the
  existing dialog is moved to the front. PR #834.

----

## Version 1.4 [2021-07-27]

### Release Notes

This release contains some new features and a lot of code refactoring. Among the main new features
is paragraph alignment and indentation. Regular line breaks within paragraphs are now also
supported. The changes are described in more detail below.

#### Internationalisation

Translation files have been added for Simplified Chinese by Qianzhi Long.

#### Line Breaks

The way line breaks inside paragraphs work has been changed. A single line break is now treated as
a proper line break and will show up in the document viewer and exported documents. A single line
break does not start a new paragraph, but forces a break inside the paragraph like a Shift + Enter
does in most rich text editors. Two line breaks is still needed to start a new paragraph.

The old syntax of adding two spaces at the end of a line to force a line break within a paragraph
will still work as before, so there is no need to change your existing text if you've used this
feature. However, there is a new highlighting feature that will show you where in the text you have
redundant spaces. If you are used to having double spaces between sentences, you may want to switch
off this highlighting feature in Preferences as it will also detect those.

A helper function has been added to the Format menu that can look through a paragraph and remove
line breaks in case you've been using line breaks inside your existing text under the assumption
that the exporter and viewer will ignore them.

I hope this change will not be too inconvenient. I believe the new behaviour will make more sense
for most people. Especially considering some of the feedback I've gotten on how line breaks work.
The original implementation was following the Markdown standard, but since novelWriter is not a
proper Markdown editor and instead just borrows from Markdown, this behaviour always seemed a bit
unnecessary.

#### Text Alignment and Indentation

The default text alignment is left or justified based on your preferences. For documents with the
layout set to Title Page or Partitions, the default is centred. However, sometimes you may want to
override this default. A new set of codes have therefore been added to allow specifying alignment
as well as additional text margins on individual paragraphs.

The logic of the syntax is as follows:

A single angle bracket will push the text away from the edge it points away from. Therefore, a
single `>` before the paragraph, or a single `<` after the paragraph, will add indentation on the
respective side. It's perfectly valid to do this on both sides at the same time.

A double set of angle brackets will push the text all the way towards the opposite side. Therefore,
a double set of `>>` before the paragraph will indicate right alignment, and a double set of `<<`
after the paragraph will force left alignment. Also here both can be used at the same time, which
results in the paragraph being centred.

Format menu entries and keyboard shortcuts have been added so that you don't have to memorise these
codes.

_These Release Notes also include the changes from 1.4 Beta 1 and RC 1._

### Detailed Changelog

**Internationalisation**

* US English and Norwegian translations have been updated by @vkbo. PR #825.
* French translations have been updated by @jyhelle. PR #829.

----

## Version 1.4 RC 1 [2021-07-12]

### Release Notes

This is a preview release of novelWriter 1.4. It contains some new features and a lot of code
refactoring. This release is a testing release, and may contain bugs. Please be careful when using
this version to work on your projects.

### Detailed Changelog

**Internationalisation**

* Translation files have been added for Simplified Chinese. The translation has been provided by
  Qianzhi Long (@longqzh). PR #817.

**Code Improvements**

* Improve PEP8 compliance for the source code. PRs #816 and #820.
* The way messages are written to the logging tool has been improved. PR #818.
* Some improvements to parsing and encoding of HTML has been added. PR #821.
* Test coverage of the document editor has been improved. PR #787.

----

## Version 1.4 Beta 1 [2021-06-13]

### Release Notes

This is a preview release of novelWriter 1.4. It contains some new features and a lot of code
refactoring. This release is a testing release, and may contain bugs. Please be careful when using
this version to work on your projects.

### Detailed Changelog

**Bugfixes**

* A number of calls for the pop-up alert box were missing translation wrappers. That means they
  could not be translated into other languages. The alerts have been fixed, but the PR does not add
  the missing translations. PR #806.
* A duplicate error message from the index class has been removed. PR #758.

**Features**

* Single line breaks are now treated as proper line breaks within paragraphs. Paragraphs are still
  separated by two line breaks like before. This means that it is no longer necessary to leave two
  spaces at the end of the line to force a line break. This is a rather obscure and little known
  feature taken from Markdown, and it isn't very intuitive. Issue #785. PR #786.
* It is now possible to specify text alignment and additional indentation on individual paragraphs
  in the text. Both features use a similar syntax that I hope is fairly intuitive. Menu entries and
  keyboard shortcuts have also been added to make it easier to use these features. Issues #595 and
  #803. PR #804.

**Code Improvements**

* Class initialisation has been made consistent. All GUI classes now inherit the main window as its
  parent class, and all other classes inherit the main project class as its parent. Since the
  project class and the main window class have pointers to each other, all needed pointers are
  available from their respective classes. PR #758.
* The document class has been changed from a reusable class to a class that is intended to wrap a
  single document via its handle. The class was originally written for the document editor where
  the reusable approach made more sense. But it is much simple to create and destroy them in other
  parts of the code when they are not reusable. PRs #758 and #760.
* The document class no longer generates any pop-up alerts. Errors are recorded and retrieved and
  displayed by the parent or caller class. PR #758.
* Refactored the code of the editor class to make it more isolated by making most class variables
  private. PR #779.
* Made similar changes to the viewer class and item details class. PR #780.

----

## Version 1.3.3 [2021-06-13]

### Release Notes

This patch release fixes a potential file encoding issue when running setup on Windows, and a minor
issue with the project word count not being updated immediately when a file is deleted. In
addition, the keyboard shortcuts to change focus between the project tree, the editor, the viewer,
and the outline panel, have been changed for Windows users. They keyboard shortcuts were
interfering with the Alt codes used for special characters. The shortcuts are unchanged for Linux
and macOS.

### Detailed Changelog

**Bugfixes**

* Fix an issue with file encoding when extracting version information from the source code during
  setup on Windows. This seems to be a limited issue, but the changes make the relevant function
  more fault tolerant. Issue #805. PR #807.
* The project word count on the status bar was not always updated when a file was permanently
  deleted from the project. This has now been resolved. Issue #799. PR #810.
* The keyboard shortcuts to change focus will on Windows interfere with the alt key codes as the
  focus shortcuts used `Alt+` to `Alt+4`. On Windows, these are now instead `Ctrl+Alt+1` to
  `Ctrl+Alt+4`. Part of issue #740. PR #808.

**Source Code**

* Remove a redundant line in the source code. PR #802.
* Make the XML parse for project items a little less panicky when encountering unexpected XML tags.
  Generally, this shouldn't be a problem, but the XML parser should silently ignore unexpected tags
  when parsing the project file. This may occur if a project is opened in an earlier version of
  novelWriter. If so, a warning is issued anyway, so it is safe to disregard unrecognised tags as
  the user has already actively selected to proceed and been sufficiently warned. PR #809.

----

## Version 1.3.2 [2021-05-30]

### Release Notes

This is a patch release that fixes some minor issues. One issue was with the split tool, which
would drop the last line from the source document during a split if it was missing a final line
break. A minor issue with the display of word counts on the details panel under the project tree
has also been fixed. In addition, the setup script commands for Linux have been improved a bit.

### Detailed Changelog

**Bugfixes**

* The details panel under the tree would sometimes show character, word and paragraph counts even
  when there was no document selected. This has now been fixed. Issue #781. PR #782.
* The split document tool would drop the last line of the source document. This is generally not a
  problem if the last line has a line break after it, but if it doesn't, it is lost in the split.
  This was caused by an offset error when calculating the split positions in the file and has been
  resolved. Issue #795. PR #796.

**Installation**

* Due to an error in the setup script in the past, a desktop icon was created for novelWriter when
  running the `xdg-install` command. This is no longer the case, but the old icon was still left on
  some user's desktops. The setup script will now remove that icon if it exists when the
  `xdg-install` or `xdg-uninstall` commands are run. PR #784.

----

## Version 1.3.1 [2021-05-06]

### Release Notes

This is a patch release primarily to fix a problem with the Qt translation library used to make
novelWriter available in multiple languages. One of the function calls made to the library was
added recently, in Qt 5.15, which many users on Linux will not have installed on their system. The
issue could be resolved by updating the library, but it's an unnecessary and inconvenient
restriction.

### Detailed Changelog

**Bugfixes**

* The code to load translation files for the main GUI was using a function in the QTranslate class
  that was added in version 5.15, which means novelWriter could not start on a lower version of the
  Qt library if translation files were present. We don't want to force users to use Qt 5.15, so the
  call has been removed. Issue #773. PR #774.

**Other Fixes**

* When generating a new project on Windows, the code that generates the new documents in the
  project would create duplicate handles, causing a warning to be printed. The warning is harmless
  as the collisions are handled. They are caused by the resolution of the clock available to Python
  on Windows being in the tens of millisecond range, much slower than the code generates the new
  project files. The solution was to append a counter to the timestamp from the clock, ensuring
  that the seed is always unique. Issue #769. PR #776.

----

## Version 1.3 [2021-05-02]

### Release Notes

The main feature of the 1.3 release is internationalisation. The release introduces support for
Portuguese, French, and Norwegian for the main GUI, in addition to the default English. The
settings for choosing the GUI language can be found in the main Preferences.

The implementation is such that the projects themselves can use a different language than the one
selected for the GUI. To allow for better support for multiple language projects, the Build Novel
Project tool has the added option to select the language of the injected text into exported
documents. In particularly for the number words that can be added for chapter headers. Available
languages here are the same as mentioned above for the main GUI, plus German.

Settings have also been added in Preferences to allow for automatic injection of spaces or non-
breaking spaces in front of, or behind, certain characters. These are features generally available
in text editors for French, but the implementation in novelWriter simply makes them a free text box
where you can list all characters or symbols where you want a space added automatically.

The translation files for this release have been provided by Bruno Meneguello for the Portuguese
translation, by Jan Lüdke (jyhelle) for the French translation, by Veronica Berglyd Olsen for the
Norwegian translation as well as the minor modifications for US English, and Marian Lückhof
provided the translation file for chapter numbers in German.

The work to rewrite novelWriter to allow for internationalisation was done by Bruno Meneguello and
Veronica Berglyd Olsen.

_These Release Notes also include the changes from 1.3 Beta 1 and RC 1._

### Detailed Changelog

**Bugfixes**

* Fixed an issue when saving a document from the Build Novel Project tool when the previous path
  used for a file dialog no longer existed. The dialog defaults to show the same folder as last
  time it was opened, but should default to the user's home folder if that path no longer exists.
  There was a bug in this default behaviour that resulted in a critical error. Issue #761. PR #762.
* Remove a duplicate error message triggered by a broken cached index file. The two error messages
  reported on the same error. The first of them was also not included in the translation framework.
  PR #759.

**Installation**

* The setup script, and file locations for the translation files, have been updated such that the
  translation files are available in both the PyPi package and in the Minimal Install packages.
  PRs #753, #764 and #765.

**Code Maintenance**

* The source code files for dialogs and tools have been moved out of the main `gui` source folder.
  The `gui` folder now only contains sub-elements of the main GUI class. PR #754.

----

## Version 1.3 RC 1 [2021-04-18]

### Release Notes

This is a release candidate of 1.3. The primary feature of release 1.3 is the addition of
internationalisation (i18n) of novelWriter. The release introduces support for Portuguese, French,
and Norwegian in addition to the default English.

There have been no major changes since the release of 1.3 Beta 1, but the bugfixes and improvements
from version 1.2.3 have been included.

### Detailed Changelog

**Internationalisation**

* The Portuguese translation has been updated and should now be complete. Thanks again to Bruno
  Meneguello (@bkmeneguello). PR #742.

*The changes since 1.3 Beta 1 also include the changes of release 1.2.3.*

----

## Version 1.3 Beta 1 [2021-03-28]

### Release Notes

This is a pre-release of 1.3. The primary feature of release 1.3 is the addition of
internationalisation (i18n) of novelWriter. The release introduces support for Portuguese, French,
and Norwegian in addition to the default English.

This is a beta release. Use with caution on live project.

### Detailed Changelog

**Internationalisation**

* Added support to the source code for internationalisation of the GUI. Thanks to Bruno Meneguello
  (@bkmeneguello) for doing most of the work. Issue #93. PRs #673, #680 and #684.
* Build Novel Project localisation has been added as well. This is separate from the GUI
  localisation as the project may not be written in the same language as the GUI is set to. PRs
  #676 and #682.
* The text editor's auto-replace features now support inserting spaces automatically when replacing
  quotes, as well as in front of major punctuation. These features are common for writing tools
  supporting French and Spanish for instance. Issue #703. PR #704.

**User Interface**

* The Preferences dialog has been updated to be more responsive to varying text label lengths due
  to different needs for different languages. PRs #687 and #711.
* The Project Settings dialog has been improved to be more consistent and user friendly across the
  Status, Importance and Auto-Replace tabs. Issue #691. PR #695.
* The About dialog has been updated to contain more information on contributions. PR #698.

**Translations**

* Portuguese translation added by Bruno Meneguello (@bkmeneguello). PRs #673, #681, #686 and #697.
* Norwegian translation added by Veronica Olsen (@vkbo). PR #679.
* German translation added (Build tool only) by Marian Lückhof (@Number042). PR #683.
* French translation added by Jan Lüdke (@jyhelle). PRs #692, #711 and #713.
* American English added by Veronica Olsen (@vkbo). PR #693.

**Installation**

* Added i18n support to the setup script. PRs #673 and #729.

**Code Maintenance**

* The ISO lookup dictionary for language codes has been removed and replaced with the lookup
  features available in Qt5 through QLocal. The remaining two source files in the constants folder
  have been moved up a level as well. PRs #673 and #730.

----

## Version 1.2.3 [2021-04-18]

### Release Notes

This patch fixes a bug where the user's word list (personal dictionary) was not saved properly for
new projects. The added words were thus "forgotten" the next time the project was opened.

In addition, uninstall commands have been added to the main setup script to make it easier to clean
up icons (Linux and Windows) and registry keys (Windows) if the user wishes to uninstall
novelWriter.

### Detailed Changelog

**Bugfixes**

* Fixed an issue where the initial file for the user dictionary for a new project would not be
  created the first time a word was added to it. This caused the words the user added to the
  dictionary to not be loaded the next time the project was opened. Issue #733. PR #734.
* Some of the `setup.py` commands could not run if the PyQt5 packages were missing due to an import
  command extracting the version number from the main `nw` package. This was not technically a bug
  as the choice to do it this way was made deliberately, but a function has been added to the
  `setup.py` script to allow reading the version number without having to import the `nw` package.
  PR #749.

**Installation**

* An `xdg-uninstall` option has been added to `setup.py` to uninstall the icons installed into the
  system by the `xdg-install` command. PR #736.
* Likewise, a `win-uninstall` option has been added to `setup.py` to uninstall the icons installed
  into the system by the `win-install` command. Issue #743 and discussion #739. PR #749.
* Improvements have also been made to the `setup_windows.bat` script, and a complementary
  `uninstall_windows.bat` has been added as well. PR #749.

----

## Version 1.2.2 [2021-03-28]

### Release Notes

This patch release is a bug fix release addressing some inconsistencies and issues with the
document header buttons when Focus Mode is active. The keyboard shortcuts for search and replace
should now also work in Focus Mode. In addition, the setup script for novelWriter has been improved
when installing on Windows.

### Detailed Changelog

**Bugfixes**

* The way Focus Mode worked when activated through the menu and through the document header button
  were inconsistent. The header button would deactivate the edit, search and close buttons, while
  the menu entry would not. These two methods now call the same set of functions to ensure the
  behaviour is consistent. PR #717.
* Closing the document while in Focus Mode now ends Focus Mode. Previously, the editor would be
  left stuck in Focus Mode with no way to exit. PR #717.

**User Interface**

* The keyboard shortcuts for the search and replace tool now also work in Focus Mode. Previously,
  the menu entries and their shortcuts were deactivated in this mode. Issue #716. PR #717.

**Installation**

* The setup script command do build minimal install archive files now also generate SHA 256 sum
  files. PR #724.
* The setup script will now copy the `novelWriter.py` file to `novelWriter.pyw` if it doesn't exist
  when the `win-install` command is run. Issue #727. PR #728.

----

## Version 1.2.1 [2021-03-21]

### Release Notes

This patch release is a bug fix release addressing issues with the document editor's search and
replace tool. Due to some recently added restrictions on when various tools are active, depending
on which part of the main window has the user's focus, the search tool keyboard shortcuts and
buttons were blocked when they shouldn't. This release resolves these issues.

### Detailed Changelog

**Bugfixes**

* Fixed an issue with the search bar where the button and shortcut actions would be blocked unless
  the document itself had focus. This focus check was added for all the text altering functions,
  but should not affect search and replace. The search and replace actions now bypass the regular
  action pipeline with the focus check. Issue #708. PR #709.

**Documentation**

* Improve the instructions for setup on Linux when manually installing using the `setup.py` script.
  Previously, the documentation wasn't very clear on the difference between a user space install
  and a system wide install. Neither did it explain how to install `setuptools` if the package is
  missing. Issue #714. PR #715.

----

## Version 1.2 [2021-03-14]

### Release Notes

This release is mainly focused on the Build Novel Project tool. Completely new export classes have
been written to support Open Document and Markdown exports. In addition, the way document layouts
are handled have been automated a little to assist the user in keeping header levels and document
layout flags in sync. The third new additoion is the ability to record and log idle time during a
writing session to improve the writing statistics information as requested by several users.
Finally, it is now possible to directly edit the project dictionary via a new, simple GUI dialog.

#### The Build Novel Project Tool

The main changes for this release are to the Build Novel Project tool. The Open Document export, as
well as the Markdown export, is now handled entirely by code written for novelWriter. Previously,
these export features depended on the underlying Qt library's save routines connected to the
preview document shown in the build dialog. Using this method of export both meant that the content
of the document was dependent on the preview being generated first, and it also meant that the
exported document had limited support for novelWriter-specific features and custom formatting. The
new export class should generate a much better result, especially for the Open Document formats.
The Open Document standard is supported by Open Office, Libre Office, Google Docs, Microsoft Word,
and probably a number of other applications too. The Markdown export hasn't changed a lot, but
should be a slight improvement on the previous export feature.

These changes to the build tool also imply that the saving process is now independent of the
content of the preview window, meaning you don't have to rebuild the preview before saving, which
was previously the case. To make this more consistent, the PDF export option has been moved to the
print button as it is actually a print-to-file feature under the hood, not technically a proper PDF
export format. It is exactly the same as printing to file from the print preview dialog.

In addition to the changes to the export features, the Build Novel Project tool now also has
controls for line height, which applies to all rich text export formats, and the option to replace
unicode characters with appropriate html entities for html export.

#### Document Layout Automation

Among other changes in this release are a few improvements to the process of creating and changing
documents. When a new document is first created, the header is generated from the assigned label
and layout.

In addition, for some document layouts, when the user changes the header level of the first header
of the document, the document layout setting is updated accordingly. This should reduce the need
for the user to maintain two ways of assigning the role of a given document. This automation only
applies to combinations of header level and current document layouts where there is no ambiguity.
For instance, changing the header level in a "Scene" document from level 3 to 2 changes the
document layout automatically to "Chapter". But changing the first header of a "Book" layout
document from 1 to 2 does not change the document's layout as the "Book" layout is a generic
document layout and it's perfectly reasonable for its first header to be a chapter header.

Keep in mind that novelWriter treats documents with layout "Book", "Chapter" and "Scene" exactly
the same during exports. The distinction is only meant as a way to indicate the purpose of a
document in the project tree. This new automation is meant to assist in keeping this information up
to date. The other layouts do have an effect on formatting during export, and are generally left
alone.

#### The Session Timer and Idle Time

Another change that has been requested by a couple of users is to have the session timer in the
status bar stop counting when the user is inactive (idle). This feature is optional, and can be
controlled from Preferences. The definition of "idle" in this context is either that the user is
active in a different application than novelWriter (loss of focus) or that the user has not made
any changes to the current document for a given amount of time. The time threshold is by default
five minutes, but can be altered in Preferences.

In addition, the idle time is also recorded in the session log, and can be viewed in the Writing
Statistics dialog and exported with the rest of the information. The idle time is recorder in the
logs regardless of whether the status bar clock takes idle time into consideration or not. So even
if you turn off the idle time switch in Preferences, the other idle time setting still affects the
writing stats log entries.

#### Other Changes

The user dictionary of the project, where words added to the dictionary from the document editor
go, can now be viewed and edited with a new "Project Word List" tool in the "Tools" menu.

A small additional feature added is also the ability to undo the last move of an item in the
project tree. The keyboard shortcut for this is `Ctrl+Shift+Z`, or it can be accessed from the
menu. The feature can only undo the last move, but it includes both documents moved to trash, moves
by up/down keypress or menu entries, and drag and drop moves.

A new keyword has been added to mark characters in the story. The new keyword is intended to tag a
character as the focus character for a chapter or scene. This is useful for stories where the
point-of-view character and the focus character are different.

Lastly, two bugfixes have been made as well. The Empty Trash feature was no longer working due to
an earlier fix solving another issue. The feature has now been restored. In addition, the indexer
now checks that a keyword (tag or reference) is valid before saving it to the index. Previously, an
invalid keyword could be saved to the index and potentially crash the application.

_These Release Notes also include the changes from 1.2 Beta 1 and RC 1._

### Detailed Changelog

**Bugfixes**

* Fixed an issue where a typo in a tag or reference using the `@` character would add an invalid
  entry into the project index. The invalid keyword would be saved to the index cache, invalidating
  the index on next load. For earlier versions of novelWriter before 1.1.1, it would also cause a
  crash. Invalid keywords are now rejected during indexing. Issue #688. PR #689.
* The "Empty Trash" option was no longer working due to an earlier fix that added a requirement
  that the project tree has focus to allow the emptying to procede. Since the Empty Trash feature
  opens a dialog, the tree loses focus, and the deletions are therefore ignored. The focus check is
  no longer considered when emptying the trash. Issue #701. PR #702.

**Documentation**

* The documentation has been updated to reflect the changes in 1.2, and a few corrections pointed
  out by @jyhelle applied. PR #700.

----

## Version 1.2 RC 1 [2021-03-02]

### Release Notes

_The Release Notes have been moved and merged into the 1.2 notes._

### Detailed Changelog

**Bugfixes**

* If a tag or reference keyword was mistyped, it would still be indexed and put into the index.
  This caused the index to be deemed invalid on the next loading of the project, triggering a
  rebuild. A check has been added to the code parsing the lines starting with `@` to ensure only
  valid keywords are written into the index. Issue #688. PR #690.

**New Features**

* Added a tool to edit the project's user dictionary. This is the dictionary where the "Add Word to
  Dictionary" actions from the document editor go. The dialog tool allows for listing, removing and
  adding words to this dictionary. Issue #665. PR #669.

**User Interface**

* Pressing the `F2` key when in the document editor will open the Item Editor for the open document
  instead of the one selected in the project tree. PR #664.
* The shortcut for deleting an item in the project tree has been changed from `Ctrl+Del` to
  `Ctrl+Shift+Del`. This change was also backported to version 1.1.1. Resolves #629. PR #664.

----

## Version 1.2 Beta 1 [2021-02-11]

### Release Notes

_The Release Notes have been moved and merged into the 1.2 RC 1 notes._

### Detailed Changelog

**New Features**

* A full Open Document exporter has been written and added for the Build Novel Project tool. This
  replaces the previously used Qt Save to ODT which just saved the content of the preview window to
  an ODT file. The Qt pathway was very limited and didn't generate proper formatting classes. The
  new export class can generate both full `.odt` and flat XML `.fodt` files. The formatting support
  of this exporter is equivalent or better than the HTML5 exporter, which was previously the best
  supported option. Solves issue #611. PRs #607, #652, #660, and #654.
* A full Markdown exporter has been written and added for the Build Novel Project tool. This too
  replaces a Qt feature that was used to save the content of the preview window into a markdown
  file. The exporter allows for both standard markdown and GitHub flavour markdown. The only
  relevant difference being that the latter allows strikethrough text. Issue #617. PR #650.
* The Build Novel Project tool now has a "Line height" property that is applied to the preview, and
  to the HTML5 and Open Document export formats. Discussion #653. Issue #654. PR #660.
* The Build Novel Project tool now has an option to convert Unicode characters to HTML entities on
  export to HTML5. Previously, some symbols were converted while others were not. This option
  provides a more consistent "all or nothing" option. PR #660.
* The last file or folder move in the project tree can now be undone from the Project menu or by
  pressing `Ctrl+Shift+Z`. PR #632.
* When a document header level is altered in a novel file of layout type Scene, Chapter,
  Unnumbered, or Partition, and that document is saved, the document's layout setting as seen in
  the project tree is updated to reflect the new level of that heading. This helps reduce the
  duplication of effort by the user to keep this information in sync. See discussion #613. This is
  an acceptable solution to #614. Issue #618. PR #620.
* The session timer now records the amount of time the user is idle. Idle is defined to be when the
  application window does not have focus, and when the user hasn't made any changes to the document
  open in the editor for a specified amount of time. The default is 5 minutes. The idle time is
  recorded to the session log and can be shown in Writing Statistics. Optionally, the status bar
  session timer can also be set to pause when the user is considered idle. Issues #606 and #651.
  PRs #656 and #661.
* It is now possible to tag a character as the focus character for a give section of text. This is
  useful for cases where the point-of-view character differs from the main character of the story,
  or the part of the story. Issue #605. PR #662.

**User Interface**

* A document's class and layout is now displayed next to its status or importance in the document
  editor footer bar. PR #628.
* When a new document is created, the header of the file is automatically generated based on the
  document's tree label, and the level determined by the selected layout. Issue #530. PR #628.
* On the Build Novel Project GUI, the PDF option has been moved from the "Save As" button to the
  "Print" button. This more accurately reflects what it actually does: print the content of the
  preview to a PDF using the printer pathway. This also means that all remaining items on the "Save
  As" dropdown list now can be executed regardless of the content of the preview window. They all
  run their own separate build process. This resolves #611. PR #650.
* Export to plain text has been dropped. PR #617.

**Code Improvements**

* The index class now scans every element of the loaded index cache before accepting it. This means
  that any unrecognised content will trigger a full re-indexing. This is particularly useful when
  opening an index that was saved by a later release. Every entry that requires a lookup is checked
  to avoid potential key errors for instance. All values are also checked for correct data type.
  The new check is extensive, but still fast enough that it only adds a few milliseconds to the
  startup time. PR #619.

**Code Maintenance**

* Cleaned up some redundant code after PR #637. PR #638.

----

## Version 1.1.1 [2021-02-21]

### Release Notes

This patch makes a couple of minor improvements to the GUI. The keyboard shortcut for deleting
entries in the project tree has been changed from `Ctrl+Del` to `Ctrl+Shift+Del` to free up that
shortcut for the document editor. It is now possible to use the shortcut for deleting the word in
front of the cursor, a common and useful feature of many text editors.

The way the negative word count filter option works on the Writing Statistics tool has been changed
to be more intuitive. Enabling this filter now appears to remove all negative entries without
altering the other entries. Previously, the removed negative counts would be included in the
following entries to make it consistent with the total word count. In addition, writing sessions
shorter than five minutes, and with no change in the word count, are no longer recorded in the
session log file.

Other changes include improving the speed of the internal spell checker, used when the Enchant
spell check library isn't available. The internal spell checker is no longer significantly slower,
but is still lacking in functionality compared to Enchant.

### Detailed Changelog

**User Interface**

* The default GUI font on Windows is now Arial. It works better with the Qt framework than the
  default system font. If Arial is missing, it falls back to the bundled font Cantarell. PR #655.
* The way word changes are calculated on the Writing Statistics tool has changed when the option to
  exclude negative word counts is active. Previously, the entries with negative counts were
  filtered out, but the change in count was still applied to the next line, altering the value.
  Now, the GUI will instead just drop the lines that are negative and keep the other lines
  unchanged. This is more intutitive, but it also means that the total count now longer matches the
  sum of the lines. PR #659.
* The keyboard shortcut for deleting entries in the project tree has been changed from `Ctrl+Del`
  to `Ctrl+Shift+Del`. The `Ctrl+Del` shortcut is thus free to be used exclusively by the editor to
  delete the word in front of the cursor. Having the same shortcut do different things depending on
  which area of the GUI has focus is a bit confusing. Related to #529. PR #666.

**Other Improvements**

* The internal spell checker, which is used when the Enchant library isn't available, has been
  given a significant speed improvement by caching the imported dictionary as a Python `set`
  instead of a `list`. The `set` has a hashed key lookup algorithm that is significantly faster.
  PR #668.
* Sessions shortar than 5 minutes, and with no word count changes, are no longer recorded in the
  session stats log file. PR #685.

**Installation**

* The PyPi packages now include the `setup.py` file, which makes it possible to install icon
  launchers for novelWriter on both Linux and Windows after installing with `pip`. PR #655.

----

## Version 1.1 [2021-02-07]

### Release Notes

The main change in this release is the addition of a new tab to the project tree on the left side
of the main window. The regular project tree is now on a tab named "Project", while a new tab named
"Novel" displays a simpler version of the information on the main "Outline" page. It lists all the
headers of the novel part of the project, as well as the word count and point-of-view character of
each section. This is an alternative way to navigate the novel part of the project. The various
tree views are now also kept better in sync when the user selects various documents and headers.

In addition, a new information dialog named "Project Details" has been added. It replaces the
"Details" tab in "Project Settings", and adds more information about the novel part of the project.
In particular, a "Table of Contents" in the "Contents" tab displays a summary of the main parts
and chapters of the project, their total word counts, and an estimated page count. This was made in
response to users asking for ways to estimate the total page count of the project. The page count
is estimated based on a words per page setting, which can be changed on the dialog window.

Since the tabs below the project tree now add some extra room on the GUI, some convenient buttons
have been added in the same area, with direct access to "Project Details", "Writing Statistics" and
"Project Setting".

A few other minor changes have been made as well. The Preferences dialog has been improved with
clearer categories and hopefully better help text. Some new options have been added too. They allow
syntax highlighting of multi-paragraph quotes. The highlighter can now optionally accept quotes to
be left "hanging", that is, no closing quote in the same paragraph.

_These Release Notes also include the changes from 1.1 RC 1._

### Detailed Changelog

**Bugfixes**

* A `None` check in the details panel below the project tree was missing, resulting in an
  occasional error message being printed to the logging output. The error was otherwise handled, so
  this is mainly a fix to prevent the error message. PR #639.

**User Interface**

* The word counts in the Novel tree are now updated each time a file is saved. Issue #636, PR #637.
* A "Remove" button has been added to the "Open Project" dialog. Previously, recent project entries
  could be removed by pressing the `Del` key, but no obvious other methods were present on the GUI.
  PR #639.
* When the search function is activated, the text in the search box is automatically selected.
  Issue #645, PR #639.

**Installation**

* The minimal zip release package tool in `setup.py` has been improved to generate tailored
  packages for each operating system. The old `pyinstaller` build command has been removed, but the
  manual build path for a Windows setup.exe file has been kept. PRs #643 and #644.

----

## Version 1.0.4 [2021-02-03]

### Release Notes

This patch release fixes a couple of minor issues with the Preferences dialog and the behaviour of
one of the keyboard shortcuts.

Aside from these fixes, the main point of this patch is to add new setup features for novelWriter
on Windows. A Windows installer will no longer be provided for the foreseeable future, and instead
functionality has been added to the main setup script to create desktop and start menu icons.

### Detailed Changelog

**Bug Fixes**

* Fixed an issue with the Preferences dialog where the setting for justified text was mixed with
  the setting for fixed text width. This meant that the justified text setting could potentially
  get overwritten when the Preferences were changed and saved. Issue #623, PR #625.
* Fixed an issue with the Open Project dialog where the list of recent projects would contain
  duplicate entries if the dialog was opened multiple times. PR #627.

**User Interface**

* The `Ctrl+Del` keyboard shortcut is now only active when the project tree has focus. Since this
  is also a common shortcut in many applications for deleting the next word ahead of the cursor,
  the activation of the delete file function when the editor has focus is unexpected to some users.
  Issue #629, PR #631.

**Installation**

* A new command has been added to the `setup.py` script. The new command, `win-install`, will
  create a desktop and start menu icon for novelWriter when run in the source folder. A windows
  batch file, `setup_windows.bat`, has also been added. Running this file from the source folder,
  either by command line or by double-click, will install dependencies from PyPi and set up the
  icons and file association with novelWriter project files. This should make it easier to run
  novelWriter from the source folder on Windows. PRs #634, #641 and #642.

**Documentation**

* The documentation on how to setup and install novelWriter has been extended and reorganised into
  one file per operating system. Some of the other documentation files have also been moved to a
  different section. PR #634.

----

## Version 1.1 RC 1 [2021-01-31]

### Release Notes

This is a preview and test release for version 1.1.

A few new features have been added. The primary change is that the project tree on the left side of
the main window now has two tabs. The regular project tree is now on a tab named "Project", while a
new tab "Novel" displays a simpler version of the information on the main "Outline" page. It lists
all the headers of the novel part of the project, as well as the word count and point-of-view
character of each section. This is an alternative way to navigate the novel part of the project.
The various tree views are now also kept better in sync when the user selects various documents and
headers.

In addition, a new information dialog named "Project Details" has been added. It replaces the
"Details" tab in "Project Settings", and adds more information about the novel part of the project.
In particular, a "Table of Contents" in the "Contents" tab displays a summary of the main parts
and chapters of the project, their total word counts, and an estimated page count. This was made in
response to users asking for ways to estimate the total page count of the project. The page count
is estimated based on the word count, and can be changed on the dialog window.

Since the tabs below the project tree now adds some extra room on the GUI, some convenient buttons
have been added, with direct access to "Project Details", "Writing Statistics" and "Project
Setting".

A few other minor changes have been made as well. The Preferences dialog has been improved with
clearer categories and hopefully better help text. Some new options have been added too. They allow
syntax highlighting of multi-paragraph quotes. The highlighter can now optionally accept quotes to
be left "hanging", that is, no closing quote in the same paragraph.

### Detailed Changelog

**User Interface**

* Added a Novel tab under the project tree where the user can navigate the novel's layout of
  chapters and scenes, similar to the Outline view, but next to the document editor. The Outline
  view and Novel/Project trees now also behave more in cooperation. When files on one are selected
  or moved, the other will follow and update. Issues #541 and #185, PR #538.
* Added a Project Details dialog that lists project details (moved from Project Settings' Details
  Tab) and a Table of Contents tab where details on chapter level is displayed. This table also
  shows an estimated page count and estimated page location of each chapter. Issue #528, PRs #555,
  #598 and #603.
* Added three buttons below the project tree that connects to Project Details, Writing Statistics,
  and Project Settings. PR #555.
* The settings and tabs in the Preferences dialog have been re-arranged into more tabs with less
  options on each tab. PRs #577 and #624.
* Minor changes to margins and alignments of widgets on the main GUI. PR #565.
* Added a keyboard shortcut to change focus to the Outline tab. The focus change now also ensures
  that the main GUI also switches to the tab where the focus is shifted. Issues #609 and #612, PR
  #615.
* The cursor should now also be visible when opening a blank document and the editor has focus.
  Issue #608, PR #621.

**Text Editor**

* Added support for multi-paragraph quote (dialogue) highlighting. This feature is optional, and
  can be enabled/disabled in Preferences. Issue #546, PR #577.
* Add several new symbols to the Insert menu/ Issue #602, PRs #603 and #604.

**Other Changes**

* Trigger a save document call before the Build Novel Project tool starts the build. This ensures
  that unsaved changes in the editor are included in the build. Issue #610, PR #616.

**Code Maintenance**

* Reformatting of source file headers and adding license headers to all test source files. Test
  source files are now also organised into subfolders. PR #563.

----

## Version 1.0.3 [2021-01-24]

### Release Notes

This patch release fixes a minor bug sometimes encountered when running novelWriter from command
line on Windows. In addition, the Solarized Dark and Solarized Light themes have been added to the
selection of GUI and syntax themes by a user contribution.

The main change in this release is to the install scripts and the documentation related to
installing and running novelWriter. The primary change is a different method of packaging the app
for Windows. Instead of building an `.exe` file, the new setup instead builds a runnable zip file
`.pyz`. The executable would often be mistakenly flagged by virus control software due to the
packaging tools. This is a known problem with pyinstaller and similar tools, but such warnings are
always concerning even if they are false positives.

### Detailed Changelog

**Bug Fixes**

* Fix crash when starting novelWriter from command line on Windows from a different mounted drive
  than where it is installed. This was caused by a relative path lookup that defaulted to the wrong
  current directory. This works on Linux/macOS which have a common root path, but not on Windows.
  Issue #581, PR #587.

**User Interface**

* Added Solarized Dark and Solarized Light GUI and syntax themes. PR #578 by @nullbasis.
* The Typewriter Scroll Mode now works better in combination with the Scroll Past End feature. The
  scroll mode still only works when there is actually any document to scroll into, but previously
  it would also not work until the total length of the document reached 40% of the height of the
  editor window. This was quite confusing. This limit is now reduced to 10%, which means that as
  long as the Scroll Past End option is enabled, the Typewriter Scroll will always work according
  to its settings. Issue #589, PR #593.

**Installation**

* Merged the `make.py` script into `setup.py`. PR #584.
* Added a second way to build distributable packages of novelWriter for Windows. The new method
  does not use any of the current package tools that produce a Windows executable of the app. These
  packages tend to cause false virus warnings. This new method uses the Python tool `zipapp` to
  bundle novelWriter as an executable `.pyz` file, and adds Python embeddable and library
  dependencies into the same folder. The folder itself can be distributed as-is, or a Windows
  installer executable can be generated with `setup.py setup-pyz`. Issue #580, PR #584.

**Documentation**

* Updated documentation, main README and Contribution Guide to make them more consistent and to
  improve installation instructions. Based on issue #586 and input from @mgrhm. PR #592.

**Other Changes**

* The HTML generator now adds line breaks after `div` blocks used to wrap tag/reference lines. This
  makes the output easier to process by scripts, but has no impact on browser rendering and import
  into other applications. PR #597.

----

## Version 1.0.2 [2021-01-19]

### Release Notes

This patch release fixes a few minor cosmetic issues, a minor issue with the indexer, and a bug
when adding words to the user's own spell check dictionary. Additionally, the documentation has
been updated based on user feedback, and some install issues resolved.

### Detailed Changelog

**Installation**

* The dependency list was missing in the setup configuration for PyPi due to a bug in the
  `setup.cfg` file. The dependencies have been moved to a different section where the setup tool
  now picks them up properly. Issue #570, PR #573 by @stranger-danger-zamu.

**Bug Fixes**

* Fixed an issue with note files being moved between a non-novel root folder and a novel root
  folder without clearing its index entry in the former note or novel index. This would cause
  duplicate entries for such a file. PR #558.
* Fixed a cosmetic issue where the meta data panel below the project tree was not cleared when the
  project was closed. PR #559.
* Fixed an issue where the main window title would not be cleared when a project was closed, and
  the new title not set when a new project was first created. Issue #560, PR #561.
* The editor context menu option to "Add Word to Dictionary" should also be visible when there are
  no spell checker suggestions. The entry was erroneously added under an if-condition that excluded
  it in those cases. Issue #574, PR #575.

**Documentation**

* Fixed some typos and spelling mistakes in the documentation, and reworded parts of the text that
  were unclear. The technical page has also been extended with more information on project folder
  structure. PR #557.
* Clarify install instructions, and remove the duplicate instructions in the README file and
  replace them with a brief section. The full instructions are in the documentation. Issues #566
  and #570, PR #576.

----

## Version 1.0.1 [2021-01-10]

### Release Notes

This release is mainly to bring the documentation up to date, as I forgot to update the install
instructions in the original 1.0 release. I also forgot to change the various settings and help
texts that describe novelWriter as under initial development (beta state).

Some minor improvements have been made to the "Edit Project Item" dialog and some restrictions on
the settings available for documents created in the "Outtakes" folder relaxed. A few minor issues
with the document and project changed icons on the status bar have also been resolved. The
indicators were previously set to changed status even if no actual change had been made to the
project.

### Detailed Changelog

**User Interface**

* Added the Outtakes folder to a list of root folders that will allow the setting of file layouts
  otherwise only permitted under the Novel root folder. It makes sense to permit the files in this
  folder to have the same extended settings that Novel files have. PR #552.
* The text input and dropdown boxes of the Edit Project Item dialog box now extend when the dialog
  window is resized. Previously, the space between the label and the box would stretch instead,
  which isn't very useful. PR #552.
* The document and project changed status icons on the status bar are now set to unchanged status
  when the project is opened. In addition, an issue with the status being set to changed on various
  events that were not actual changes to the document or project has been resolved. For instance,
  changing the size of the document editor would flag the document itself as changed. PR #554.

**Documentation**

* Updated the install instructions of the documentation and the main readme file, as well as the
  current development status as listed on PyPi. PRs #550 and #551.

----

## Version 1.0 [2021-01-03]

### Release Notes

Based on my own testing and usage, and no serious bugs discovered in quite some time (aside from a
few corner case issues), it appears that novelWriter is stable enough for a 1.0 release. Thanks to
all the new users who keep providing feedback on bugs, cosmetic issues, or suggesting improvements
and new features. I'm glad to hear that others find my application useful, and I will keep making
improvements as I get new suggestions and have new ideas myself. At the same time, I will continue
to keep novelWriter simple and clean and avoid feature-bloat.

This release mainly fixes cosmetic and other minor issues to the user interface and makes a few
minor improvements to some less used features. Aside from this, nothing major has changed since the
last release candidate.

This release concludes over two years of tinkering with this project. The project grew out of
numerous lunch and coffee discussions with my colleague Marian Lückhof at my former job. We were
both looking for a tool for writing novels on Linux that suited our needs. We started assembling a
wish list of features that has become novelWriter. In addition, users on GitHub have continued to
test new features, provide very helpful feedback, and make new suggestions for improvements.
Especially the feedback from @johnblommers has been helpful during much of the initial development
time. Over the last months more users have started posting ideas and feedback. Thanks to all of you
for your contributions.

The 1.0 release is intended as a first release of the core features of novelWriter. That does not
mean that all planned features have been fully implemented. There is a long list of ideas and
suggestions to consider and implement. New ideas and suggestions are welcome. Either as feature
requests in the issue tracker, or if not fully formed, can be discussed on the
[discussions page](https://github.com/vkbo/novelWriter/discussions).

### Detailed Changelog

**Bugfixes**

* Fixed a minor cosmetic issue with the checkbox next to the "Distraction Free Mode" entry in the
  menu where its checkmark wouldn't always correspond to the current state of the mode. PR #532.
* When opening the "Writing Stats" dialog in a new project where there is no session log file yet,
  an error dialog would pop up to complain the file is missing. A missing file is not an error, and
  should just be quietly ignored. PR #535.
* Don't enforce string data type in meta data lines written to the head of documents. Some of the
  entries can potentially be of NoneType, and the enforced type will then cause a crash. PR #539.
* Fixed a couple of faulty checks in the index and outline details panel. The checks were not
  reachable by user actions, but put in place to capture coding errors. PR #549.

**User Interface**

* The placeholder text in the "Build Novel Project" tool was referring to the name of the build
  button by a previous label. It now refers to the label that is on the current button. PR #535.
* Add "Move Item Up" and "Move Item Down" to the project tree context menu. These connect to the
  same function as the same entries in the Tools menu. PR #535.
* Block the Item Editor for the root Trash folder. PR #539.

**Other Changes**

* The special "Orphaned Files" folder has been dropped. Since the document class saves most of the
  document meta data to the header of document files, it is no longer strictly necessary and it
  does complicate the code behind the project tree as the orphaned folder isn't a tracked folder
  and therefore needs a fair bit of customised code to fit into the rest of the tree data model.
  Files found in the project's storage folder that do not exist in the project file will now be
  imported into the main project tree based on a set of fallbacks. All recovered files are prefixed
  with the word "Recovered". Issue #540, PR #543.
* Changed the way novel headers are added to the Outline view in cases where the strict logic of
  header levelled isn't obeyed. Previously. a scene header not under a chapter would be added to a
  previous chapter. That may be a bit confusing. Now, instead, a scene outside a chapter will just
  be bumped up one level. PR #549.

**Documentation**

* Fixed some minor typo or wrong word errors in the contributing guidelines. PR #537 by Curtis
  Gedak @gedakc.
* Fixed minor grammar and typo issues in documentation. PR #544 by Curtis Gedak @gedakc.
* Updated documentation with latest changes and rewritten some sections to make the terminology
  more consistent. PR #548.

**Code Improvements**

* Also enforce the maximum line length in text documents. PR #534.
* Updated various parts of the code where a question message box is opened and redirected the call
  to the main GUI class. This was done mostly for consistency, but the feature was added earlier to
  ensure that core classes do not depend on Qt libraries. PR #535.

----

## Version 1.0 Release Candidate 2 [2020-12-13]

### Release Notes

This second release candidate for 1.0 comes with only minor changes and improvements, and a handful
of minor bugfixes.

Among the improvements is the addition of all the possible @-keywords for tags and references to
the "Insert" menu under the sub-menu "Tags and References". The "Help" menu has also received a few
improvements and additional links to useful webpages. This release also adds a "Release" notes tab
to the "About novelWriter" dialog. The release notes are displayed automatically the first time you
launch novelWriter after updating to a new version.

Among the fixes is better support for high resolution screens. A few elements on the GUI did not
scale properly, among them the document editor and viewer header and footer. These were clipped on
high res screens due to an underlying issue with the Qt widget underestimating how much space it
required to accommodate the text. Unfortunately, dragging the novelWriter app between screens of
different scaling factors is not currently supported. However, the GUI should scale properly to the
scaling factor on the screen it is opened on.

The work leading up to this release has mostly been focused on improving the test coverage of the
source code of novelWriter. This helps to ensure that the code does what it is intended to do, and
is able to handle corner cases and unexpected external errors and user actions that may occur.
While writing these tests, a number of minor potential issues have been uncovered and handled. Most
of these are corner cases that may not even be reachable by unexpected user actions.

Hopefully, these changes have resulted in an even more stable version of novelWriter. If no more
issues are discovered, the next release will be the final version 1.0 release.

### Detailed Changelog

**Bugfixes**

* The headers and footers of the document editor and viewer would be clipped on high DPI monitors.
  This was due to the QWidget holding these did not automatically scale in the layout. The proper
  height of these are now calculated and enforced instead of relying on automated scaling. Issue
  #499, PR #502.
* Fixed a few inconsistencies in scaling of toggle switches, the form layouts, and the margins of
  the Item Editor when viewing on a high DPI screen. PR #502.
* Switching syntax theme live would not update all colours in the editor and viewer. This has now
  been fixed. PR #516.
* Using the Tools menu to move items up or down in the project tree, without selecting an item to
  move, would cause a crash. The move actions are now quietly rejected if no item is selected.
  Issue #521, PR #522.

**User Interface**

* Added all the possible keywords for tags and references to the Insert menu. Since the list was
  growing long, the Insert menu entries have been split up into four sub menus according to the
  previous grouping. Issue #501, PR #503.
* A "Release Notes" tab has been added to the "About novelWriter" dialog where the latest release
  notes can be displayed. PR #508.
* Menu entries that will open the "Releases" and "Discussions" pages on the novelWriter GitHub repo
  has been added to the Help menu. PRs #509, #511 and #520.
* The help text of many of the Preferences options have been clarified and rewritten. PR #516.
* Added two greyscale syntax themes. These will match with the greyscale icon themes to produce a
  GUI without colours. PR #516.

**Other Changes**

* The Windows installer now properly sets up the mime type for novelWriter, meaning novelWriter
  project files can be opened from the Explorer directly into novelWriter. PR #511.
* It is now possible to create new files in the Outtakes root folder from the context menu. Issue
  #517, PR #519.

**Test Suite**

* The tests for the core classes of novelWriter have been completely rewritten. Every class or
  source file of the core functionality (everything handling the actual project data and documents,
  as well as the meta data) is now covered by its own testmodule with a 100% coverage for each
  module. PR #512.
* Likewise, the base tests have been rewritten to cover the `Config` class, the `main` function
  that launches the app, and the error handling class. The structure matches the core tests from
  #512. PR #514.
* The GUI tests have been reorganised to match the new test structure, and somewhat improved, but
  some parts still need additional coverage. PR #527.

----

## Version 1.0 Release Candidate 1 [2020-11-16]

### Release Notes

This is the first release candidate for the upcoming release of novelWriter 1.0.

Since the fifth beta release about four weeks ago, not much has been changed in novelWriter. A few
minor tweaks have been made to the GUI.

A number of features and tools are now automatically switched off when there is no project or
document open for those features to act upon. Previously, this was a bit inconsistent, although no
serious bugs have been reported or encountered.

Most of the minor changes in this release should not be noticeable to most users. However, there
are a couple of noticeable changes.

**Typewriter Mode**

The "Typewriter Mode" of the editor has been improved. Essentially, this feature is a sort of smart
scroll. It tries to keep the cursor stationary in the vertical direction, and will try to scroll
the document up when the cursor skips to a new line while typing (or down in case of backspaces).
This is similar to the way a typewriter scrolls the paper when hitting the return key. It improves
the writing experience as the current active line will stay at the same eye heightlevel on the
screen.

Previously, the feature would lock the cursor to a given vertical position defined by the user.
Now, instead, the cursor will remain stationary in the vertical direction at any position the user
sets it to by mouse click or keyboard navigation. The user can define a minimum distance from the
top where this feature is activated. These changes makes it more flexible in terms of where the
focus is in the editor. The feature can be controlled from the main Preferences.

**Switching Syntax Theme**

It is now possible to switch syntax highlighting theme without restarting novelWriter. Previously,
changing the theme would only half-way update the document, header and footer background and text
colours. The new settings would not be fully applied until the application was shut down and
started again, thus making it a bit tedious to look through syntax themes to find the one you want.

Switching main GUI theme still requires a restart.

### Detailed Changelog

**Installation**

* A new setup option `setup.py xdg-install` will install the desktop integration (icons, mime and
  launcher) using the OS' `xdg-utils`. This is a more standardised way of installing these
  elements, and replaces the previous `launcher` option. PR #484.

**Bugfixes**

* The Details Panel below the Outline Tree View was not cleared when a project was closed, and
  whatever was listed there was still present if a new project was opened. The panel is now reset
  when a project is closed. Issue #490, PR #491.

**User Interface**

* The Typewriter Mode feature has been improved to keep the cursor stationary at any point in the
  editor viewport as long as the cursor is at a user-defined minimum distance from the top of the
  viewport. The mouse, arrow and page keys do not trigger a reposition. The new behaviour is
  similar to that of the Gutenberg editor in WordPress. PR #482.
* The document editor and viewer are now properly updated when the user switches syntax theme.
  There is no longer a need to restart novelWriter first to apply the changes. PR #487.
* Some minor GUI changes include: don't run the background word counter when there is no document
  open, make the split panels of the Build Novel Project tool non-collapsible, and set the initial
  column widths of tree views to more sensible values. PR #489.
* Block various menu actions, like split and merge documents, project backup, inserts, etc, when
  there is no project open. None of these being active caused any errors as these actions were all
  handled by the various tools, but they shouldn't even trigger when there is no project or
  document to perform the action on. PR #492.
* Clarify the message of the Close Project and Exit novelWriter dialogs. Previously, it may have
  seemed to some users that clicking "No" would allow the closing to procede without saving
  changes. This is not true as changes are saved automatically when editing a project. The dialog
  text should now make this clearer. Issue #494, PR #495.

**Other Changes**

* The index cache file `meta/tagsIndex.json` now has line breaks and indents. This makes it easier
  to version control if the user really wants to track this file. PR #483.
* The format of the meta data at the top of document files has been changed to be easier to parse,
  and easier to extend with new settings. It is also more human-readable in cases where the user
  opens a document file with other software. PR #486.
* Remove the `ToC.json` file and improve the `ToC.txt` file. There latter now has additional
  information and the format has been improved slightly to be easier to parse if read by an
  external program or script. PR #493.

**Code Improvements**

* There has been some clean-up of comments and docstrings, as well as optimisation and merging of a
  few functions that were implemented in multiple places. PR #485.
* Move some of the constants defined in various other classes into the appropriate constants
  classes, and make all constants upper case variables. PR #489.

----

## Version 1.0 Beta 5 [2020-10-18]

**Important Notes**

* The minimal supported Python version is now 3.6. While novelWriter has worked fine in the post
  with versions as low as 3.4, neither 3.4 nor 3.5 is tested. They have also both reached end of
  life. There are a couple of good reasons to drop support for older versions. PR #470.
  * Python 3.6 introduces ordered dictionaries as the standard.
  * The format string decorator (`f""`) was added in 3.6, and is much less clunky in many parts of
    the code than the full `"".format()` syntax.
  * Especially 3.4 has limited support for `*var` expansion of iterables. These are used several
    places in the code.

**Bugfixes**

* Fixed a bug in the Build Novel Project tool where novelWriter would crash when trying to build
  the preview when running a version of the Qt library lower than 5.14. Issue #471, PR #472.

**User Interface**

* An option has been added in Preferences to hide horizontal or vertical scroll bars on the main
  GUI. These optons will hide scroll bars on the Project Tree, Document Editor, Document Viewer,
  Outline Tab and on the controls of the Build Novel Project tool. Scroll bars take up space, and
  as long as the project doesn't contain very long documents, scrolling with the mouse wheel is
  enough. The feature is of course entirely optional. PRs #468 and #469.
* It is no possible to enable scrolling past the end of the document with a new option in
  Preferences. Previously, the editor would just allow scrolling to the bottom of the document. The
  new option adds a margin to the bottom of the document itself that allows for scrolling past this
  point. This avoids having to type text at the bottom of the editor window. PRs #468 and #469.
* A new feature called "Typewriter Scrolling" has been added. It basically means that the editor
  window will try to keep the cursor at a given vertical position and instead scroll the document
  when the cursor moves to a new line, either by arrow keys or while typing. The position can also
  be defined in Preferences. The scroll bar uses an animation effect to perform the scrolling to
  avoid abrupt jumps in the editor window. PRs #468 and #474.
* The line counter in the Document Editor footer now shows the location in the document in terms of
  percentage. This is convenient for very large documents. PR #474.
* A "Follow Tag" option has been added to the Document Editor context menu. This option appears
  when right-clicking a tag value on a meta data line. PR #474.
* When applying a format from the format menu to a selection of multiple paragraphs (or lines),
  only the first paragraph (or line) receives the formatting. The editor doesn't allow markdown
  formatting to span multiple lines. Issue #451, PR #475.
* The syntax highlighter no longer uses the same colour to highlight strikethrough text as for
  emphasised text. The colour is intended to stand out, which makes little sense for such text.
  Instead, the highlighter uses the same colour as for comments. PR #476.

**Other Changes**

* Since support for Python < 3.6 has been dropped, it is now possible to use `f""` formatted
  strings in many more places in the source code where this is convenient. This has been
  implemented many places, but the code is still a mix of all three styles of formatting text. PR
  #478.
* Extensive changes have been made to the build and distribute tools. The `install.py` file has
  been dropped, and the features in it merged into a new file named `make.py`. The make file can
  now also build a setup installer for Windows. The `setup.py` file has been rewritten to a more
  standardised source layout, and all the setup configuration moved to the `setup.cfg` file. PRs
  #479 and #480.

----

## Version 1.0 Beta 4 [2020-10-11]

**Bugfixes**

* When the Trash folder didn't exist because nothing had been deleted yet, the lookup function for
  the Trash folder's handle returned `None`. That meant that any item with a parent handle `None`
  would be treated as a Trash folder in many parts of the code before the Trash folder was first
  used. This caused a few decision branches to make non-critical mistakes. In particular the
  project tree context menu. This issue has now been fixed with a new check function that takes
  this into account. PRs #452 and #453.
* If an older project was opened, one with a different project file layout than the more recent
  versions, a dialog asked whether the user wants the project updated or not. However, the function
  that moves files to their new location would actually start working before the dialog asked for
  permission. The permission would only be applied to the project XML file. Now, the check is still
  run before the dialog, but the action of moving files around are postponed to after the
  permission has been given and the project XML file parsed. PR #453.
* If there were multiple headings in a file, and the last paragraph did not end in a line break,
  the word counter for the individual sections would miss the last paragraph of the last section
  due to an indexing error. This has now been fixed. PR #453.
* The last cursor position of a document in the editor would only be saved if the document had been
  altered. It is now also saved in the cases where the user makes no changes. PR #460.
* When using an aspell dictionary for spell checking, words containing a hyphen would be
  highlighted as misspelled. This is not the case for hunspell dictionaries. The hyphen is now
  taken into account when splitting sentences into words for spell check highlighting. PR #462.
* Some of the file dialogs would fail with a non-critical error when the cancel button was clicked.
  The cancel is now captured consistently in all instances where such a dialog is used, and the
  calling function exited properly. PR #463.

**User Interface**

* Some minor changes to the text formatting on the Recent Projects dialog. PR #452.
* The Build Novel Project tool has been improved. The settings side panel is now scrollable, and
  the document and settings panel now have a movable splitter between them. This gives more
  flexibility to the sizes of the various parts. PR #459.
* A new option to replace tabs with spaces has been added to the Build Novel Project tool.
  Previously, they were always replaces for HTML output. However, converting them to the HTML code
  for a tab is actually convenient for later import into for instance Libre Office, which then
  converts them back to regular tabs. Issue #458, PR #459.
* Non-breaking spaces have been removed from the HTML conversion of keywords and tags. Issue #458,
  PR #459.
* An upper limit of how large a document the Build Novel Project tool can view has been set. It is
  10 megabytes of generated HTML. The tool will still build larger documents, but they aren't
  displayed. This also limits which options are available in the "Save As" list for such large
  documents. Only native novelWriter exports are supported in such cases. The limit is an order of
  magnitude larger than a typical long novel. PR #460.
* The language indicator in the status bar now has a tooltip stating what tool and spell check
  dictionary provider is being used. PR #462.
* All representations of integers, mostly word counts, are now presented in the same way. They
  should all use a thousand separator representation defined by the local language settings. PR
  #464.
* Many parts of the GUI have had a spin/wait cursor added for processes that may take a while and
  will block the GUI in the meantime. PRs #460, #463 and #464.
* A line counter has been added to the footer of the document editor next to the word counter. It
  makes it easier to compare the position in the document when also accessing it in an external
  editor. PR #466.

**Improvements for macOS**

* The native macOS menu bar now pulls the correct menu entries into the first menu column. PR #463.
* The application name in the main menu would state Python instead of novelWriter. As long as the
  `pyobjc` package is installed, the label will now correctly state novelWriter. PR #463.
* Install and run instructions for macOS have been added to the main README. PR #463.

**Editor Performance**

* The syntax highlighter now remembers what type of line every line in the document is. This means
  that certain types of lines can be re-highlighted without having to process the entire document
  again. This is particularly useful for refreshing the highlighting of keywords and tags after the
  index has been rebuilt. PR #460.
* On a few occasions, the entire document in the editor would be reloaded in order to update the
  layout and formatting. This is not only slow for big documents, it also resets the undo stack.
  Instead, the entire document is "marked as dirty" to force the Qt library to update the layout,
  which is much faster. PR #460.
* For very large documents (in the megabyte range), the repositioning of the cursor when the
  document was opened would sometimes interfere with the rendering of the document itself. This
  could potentially cause the editor to hang for up to a couple of minutes. Instead, the
  repositioning of the cursor is now postponed until the document layout size has reached past the
  character where the cursor is to be moved. This mode is only used for documents larger than 50
  kilobytes. PR #460.
* The document editor will no longer accept single documents larger than 5 megabytes. This
  restriction has also been applied to the Build Novel Project tool. For reference, a typical long
  novel is less than 1 megabyte in size. PR #460.

**Other Changes**

* The command line switches `--quiet` and `--logfile=` have been removed. They were intended for
  testing, but have never been used. The default mode of only printing warnings and errors is quiet
  enough, and logging to file shouldn't be necessary for a GUI application. PR #453.
* A number of if-statements and conditions in the code that were intended to alter behaviour when
  running tests, mostly to stop modal dialogs from blocking the main thread, have been removed.
  These types of changes to the program flow when running tests have now been reduced to a minimum,
  and modifications instead handled with pytest monkeypatches. PR #453.
* The `QtSvg` package is no longer in use by novelWriter. The internal dependency check has been
  removed. PR #457.
* It is no longer possible to set the user's home folder as the root directory of a project. The
  home folder is the default lookup folder in many cases, so it's easy to do by mistake. PR #457.
* The background word counter has been rewritten to run on an application wide thread pool. This is
  a more appropriate way of running background tasks. PR #462.

**Test Suite**

* Major additions to the test suite, taking the test coverage to 91%. PR #453.
* Test coverage for Linux (Ubuntu) for Python versions 3.6, 3.7, and 3.8 are now separate jobs. In
  addition, Windows with Python 3.8 and macOS with Python 3.8 is also tested. All OSes are piped
  into test coverage, and they all have status badges. PRs #453 and #454.

----

## Version 1.0 Beta 3 [2020-09-20]

**Bugfixes**

* After recent changes, the `Edit Project Item` entry (or shortcut `F2`) in the menu would cause an
  error. Other means of triggering the edit dialog for a selected item were working fine. The error
  was caused by a dummy variable being sent by the menu QAction element that was caught by a new
  optional variable in the dialog function. All other menu actions have been wrapped in lambda
  functions to prevent this from happening again. PR #448.
* The Merge Tool was permitting a merge on an empty list of files to be merged. This would result
  in a new, empty file. The Merge Tool will now stop if the list of files is empty. PR #448.
* The orphaned file handling function would cause an error if the orphaned file was empty. This
  would trigger a secondary issue with uninitialised variables, which has also been fixed. PR #448.
* The context menu on the Project Tree would not show the `New File` and `New Folder` options on
  root folders if there were no Trash folder present. This weird bug was caused by the filter
  getting a `None` Trash handle and therefore assuming all root folders were Trash folders as they
  too have parent handle `None`. PR #452.

**User Interface**

* The Last Opened column in the Open Project dialog now has a fixed width font, and the Words
  column has a thin space between number and multiplier unit to make it easier to read. PR #452.

**Code Improvements**

* Minor improvemenmts have been made to the core project classes to improve encapsulation and
  better ensure consistency between the different data structures that store the novel project in
  memory. PR #447.
* Some unused or redundant code has been removed, and in some places, functions have been merged to
  reduce code repetition. PR #449.

**Test Suite**

* A lot more tests have been added and test coverage improved. PR #449.

----

## Version 1.0 Beta 2 [2020-09-13]

**Bugfixes**

* If the horizontal scroll bar appeared at the bottom of the document editor or viewer, for
  instance if a long, un-wrapable line was entered, the scroll bar would sit on top of the document
  footer. The footer bar now properly moves out of the way when the horizontal scroll bar appears.
  Issue #433, PR #434.

**New Features**

* It is now possible to set a different spell check language for a project than the one set in the
  main Preferences. It is only possible to select a different language, not a different spell check
  tool. The setting is managed in the first tab of the Project Settings dialog. Issue #368, PR
  #437.
* The document editor now has the Cut/Copy/Paste options in the main context menu. In addition,
  Select All, Select Word, and Select Paragraph have been added to the menu. The latter two will
  select the word or paragraph under the mouse pointer, not the cursor as the main menu entries do.
  Issue #438, PR #439.
* The document viewer has a new custom context menu with Copy, Select All, Select Word and Select
  Paragraph with identical functionality and look to the context menu entries in the document
  editor. PR #439.
* The document view panel now has a back navigation and forward navigation history of 20 documents.
  The navigation is activated by two buttons in the header, menu entries and keyboard shortcuts in
  the `View` menu, and by navigation buttons on the mouse. Issue #441, PR #442.
* Clicking on a document in the project tree with the middle mouse button will now open the
  document in the document viewer. PR #443.
* Added an edit and a search button to the top left corner of the document editor, in the header.
  The edit button opens the edit item dialog for the open document, and the search button toggles
  the search box for the document. PR #445.
* Added show/hide comment and synopsis buttons to the bottom right corner of the document viewer,
  in the footer. These toggle on and off the rendering of these elements in the viewed document.
  The corresponding settings in Preferences have been removed. PR #445.

**Feature Improvements**

* The document split tool now asks for permission before generating the documents. This adds a
  final confirmation before generating a lot of new documents that it can be tedious to clean up if
  the action was activated by mistake. PR #436.
* Both split and merge tools now preserve the document status or importance value from the source
  item. Previously, it would be reset to the default value. PR #436.

**Test Suite**

* Improved test coverage. PR #446.

----

## Version 1.0 Beta 1 [2020-08-30]

**Bugfixes**

* Not technically a bug, but the clearing of the document editor footer bar, both during start-up
  and when a document was closed, would print two ERROR messages to the terminal window. These were
  benign, but are now prevented from occurring by a slight change in the logic. Issue #418, PR
  #420.
* Fixed spell check highlighting for words separated by a forward slash, which was treated as a
  single word. Issue #427, PR #428.

**New Features**

* A new root folder has been added. It is named "Outtakes" by default, and functions as an archive
  folder for any file that the user wants to take out of the main project tree. The file retains
  its meta data, is editable, and is always excluded from builds. It is not possible to create
  files in this folder, but you can create subfolders for organising them. PRs #415, #416 and #419.
* Support an alternative apostrophe. There is a unicode character defined for this, but the regular
  right hand single quote symbol is the recommended character. However, sometimes this confuses the
  syntax highlighter. The alternative character bypasses this, and may also be useful for languages
  that don't use the same type of symbol for these. PRs #429 and #430.

**Feature Improvements**

* The way the enter and tab keys work in the document editor have been improved. If the search or
  replace text box has focus, the tab key switches between them, and the enter key always triggers
  the button that is to the right of the box with focus. If the editor has focus, the tab and enter
  keys work as expected for a text editor. PRs #412 and #413.
* The keyboard sequence `Ctrl+Shift+Z` is now again an alternative to `Ctrl+Y` for the redo
  functionality. PR #413.
* It is now possible to drag and drop files into the Trash folder. PR #415.
* Files moved to Outtakes or Trash are now cleared from the index, except their word counts. All
  tags and references are thus out of the project. They are automatically put back in when the file
  is dragged into the main project tree again. PR #416.
* Tabs and tab stops are now rendered properly in the document viewer. Since the `setHtml` function
  of the Qt widget used here strips tabs, they were previously just converted to eight spaces. This
  prevented the tabs from aligning vertically like they do in the editor. The stripping of tabs is
  now bypassed by replacing them with a placeholder text, and reverting the replacement after the
  document content has been set. This change also applies to the preview in the Build Novel Project
  tool, and therefore also the print and print to PDF functions. PR #419.
* The syntax highlighter is now better at detecting what is a single quoted string and what is an
  apostrophe in a word. PR #430.

**Other Changes**

* A hard maximum project tree folder depth of 30 has been added. Level 28 is the last level where a
  folder can be created, to allow for one more level of files. There is no particular reason for
  the number 30, it was mostly a matter of picking a number. 30 is assumed to be excessive. It is
  hard to navigate a project tree with that many folders. The value was set because many places in
  the code there was a soft limit of 200. If you created more, various parts of the code would stop
  working. PRs #416 and #421.
* The dialog for reporting unhandled errors has been changed and a new custom Qt subclass written.
  It does essentially the same thing as the standard QErrorMessage box did, but adds the feature of
  a clickable link to the issues tracker on GitHub, and a monospace formatted traceback for the
  issues ticket. In addition, a crash that pops this dialog will now trigger an attempted
  controlled shutdown of novelWriter. Before, it would try to keep running, but often leave
  novelWriter in a half defunct state. PR #417.

**Test Suite**

* Added better test coverage of the Project Load dialog and the Project Outline tool. PR #423.
* Switched from Travis-CI to GitHub actions for running Python tests. PRs #424, #425 and #426.
* All tests can now be run independently of other tests on a function level. Before, this was only
  possible on a test file level. Issue #431, PR #432.

----

## Version 0.12.1 [2020-08-16]

**Bugfixes**

* Some of the insert menu functions were broken due to a left-over comma in the insert source code
  converting the insert text from a string to a tuple. This is a quirk of the Python language and
  unfortunately not caught as a syntax error. Issue #409, PR #410.

**Feature Improvements**

* The Select Paragraph feature in the Edit menu now selects only the paragraph itself, without the
  leading line break. This was previously handled entirely by the Qt library, which does this for
  some reason. Issue #395, PR #405.
* A chapter heading in a file with a different layout than `Unnumbered` can now also be flagged as
  an unnumbered chapter heading by adding an asterisk to the begfinning of the title text. This
  only affects the number assignment and counter when running the Build Novel Project tool. The
  rest of the app ignores the asterisk. Issue #402, PR #406.

----

## Version 0.12 [2020-08-15]

**User Interface**

* Added a New Project Wizard that can, in addition to create the previous minimal new project, also
  create a project with pre-defined root folders and chapter and scenes. It is also possible to
  create a copy of the example project from the source code. Either from the `sample` folder in the
  source, or from a `sample.zip` file generated by the `setup.py` script and saved to the
  `nw/assets` folder. PR #366.
* When the user clicked cancel on the colour dialog in Project Settins, the icon would be reset to
  black. Instead, the colour should remain unchanged. A check that the user actually selected a
  colour has now been added. Issue #395, PR #403.

**Other Changes**

* Cleaned up code using `flake8` tool and added it as a permanent check on pull requests. The tool
  filtered out a number of unused variables and imports, which wastes CPU time and memory. Every
  bit helps. PRs #394, #397 and #401.
* Added contributing guide, code of conduct and issue templates. Direct push to main, and PR #398.

----

## Version 0.11.1 [2020-08-09]

**Bugfixes**

* The modality of the dialogs have been made more consistent and a few issues with conflicting
  settings resolved. Mostly the latter relates to some dialogs both having the `exec_()` call and
  the `show()` call. The former implies modal, the latter does not, and the latter usually took
  precedence. All dialogs are now modal with the exception of the Writing Statistics and Build
  Novel Project tools. PR #389.

**User Interface**

* The Help menu entries for the documentation have been improved a bit. If the local copy of the
  documentations is present (both files are checked now), and the Qt Assistant is installed, the
  "Documentation (Local)" entry is visible with `F1` as keyboard shortcut. The "Documentation
  (Online)" is always visible with `Shift+F1` keyboard shortcut. The `F1` key redirects to this too
  if the local copy isn't available. PR #386.
* The Writing Statistics tool now has the ability to set a cap between 100 and 100 000 words on the
  word count histogram bars. This is useful if the user has added a large chunk of text, in which
  case the histogram bar is dominated by this one entry. Now, anything on and above the cap value
  will have a full bar, and all other entries scale from 0 to the cap value. PR #387.

**Documentation**

* The main index page of the documentation now has a build date on it. PR #390.

**Other Changes**

* The Travis CI build system has been altered to first check that the tests pass for Python 3.8,
  for then to move to the other supported Python versions. These are currently 3.6 and 3.7. Python
  3.9 will be added when it is released in October. PR #388.
* Some clean-up of the source code, mostly in terms of unused imports and missing docstrings. PR
  #391.

----

## Version 0.11 [2020-08-08]

Note: The source code has now switched to a default branch named `main` ahead of the changes
planned by GitHub. See their [notes](https://github.com/github/renaming) for more information.

**Bugfixes**

* The `pytest` config file now sets the local source path as the first search path for the main
  novelWriter package. This ensures that the tests can always find the correct version of the code
  when running tests. PR #381.
* The `install.py` script was expecting an older file layout for assets files. This has now been
  updated to the curren file layout. PR #380.

**User Interface**

* A set of new exception handling functions have been added. Recoverable errors will now pop an
  error dialog with the error message and a traceback for the user. The application will not
  generally exit on such errors, unless it causes Python itself to abort. It is possible to copy
  and paste the error message so it can be used for a ticket in the issue tracker. PRs #376 and
  #378.

**Documentation**

* The full documentation for novelWriter, available at
  [novelwriter.readthedocs.io](https://novelwriter.readthedocs.io/) has been rewritten. It was
  drifting out of sync with the development of the code. In addition, many improvements have been
  made to the reStructuredText formatting of the documentation source by providing better
  cross-reference linking and highlightings. The main repository README file has been updated to
  match. PRs #375, #382, and #384.
* The main `setup.py` script has been updated to also build documentation for the Qt Assistant when
  given a `qthelp` flag. The compiled help files are copied into the `nw/assets/help` folder, and
  bundled with the source when pushed to PyPi. The GUI has been altered to open the local help
  files instead of redirecting to the online documentation if the local files are both present and
  the Qt Assistant is installed. PR #375 and #379.

**Other Changes**

* Some minor changes to the source code has been made to more correctly use the Python
  `__package__` variable. PR #376.

----

## Version 0.10.2 [2020-07-29]

**Bugfixes**

* Fixed a crash when using the replace part of search/replace when using regular expressions for
  the search. The replace code assumed the search field was a string, which isn't the case when
  using RegEx, rather itb is a QRegularExpression or QRegExp object. This has now been resolved. In
  addition, the replace feature has been improved to make sure that it only replaces text selected
  by an actual search, not any user selected text. Issue #371, PRs #372 and #373.
* The Tokenizer class used for converting novelWriter markdown to other formats produced some
  invalid escape sequence warnings. The warnings did not seem to affect the results, but have
  nevertheless been fixed. PR #370.

**Features**

* Insert menu entries to insert single and double open and close quote symbols have been added.
  These are the symbols selected as the quote symbols in Preferences. They also have keyboard
  shortcuts associated with them. PR #367.

----

## Version 0.10.1 [2020-07-11]

**Bugfixes**

* Any error encountered when converting a project from the old project folder structure to the new
  were not properly propagated to the origin of the call. Any errors of warnings occurring in the
  process would previously not have been reported properly. These are no reported in a pop-up
  dialog. PR #359.

**User Interface**

* The tooltip of the search/replace Regular Expression option has been updated to state the feature
  only works for Qt 5.3 or higher. PR #359.
* The menus have been restructured a bit. The search options have been moved to a new Search menu.
  The menu order has been changed to a more standard order. The Build Novel Project tool moved to
  the Tools menu. The full screen distraction free mode is now named Focus Mode everywhere in the
  GUI, source code and settings files. Previously, different names were used in different places.
  PR #361.
* Tooltips have been added to main GUI buttons without a button text. PRs #361 and #363.

**Features**

* The search/replace Regular Expression option now uses the newest QRegularExpression tool instead
  of the older QRegExp tool if the Qt version is 5.13 or above. Otherwise, it still uses the old.
  The main benefit of the newer tool in this context is better Unicode support. PR #360.
* The Build Novel Project tool can now generate Roman numbers for chapter markers. Both upper and
  lower case is supported. PRs #362 and #363.

**Other Changes**

* The install scripts now try to create folders before copying icons. PR #364.
* The manifest file now lists the root assets folder, so that it is included in the PyPi build. PR
  #364.
* The .desktop template file has the correct categories set according to the FreeDesktop standard.
  PR #364.

----

## Version 0.10 [2020-06-30]

**Note:** If the project file is opened by this version of novelWriter, the project file can no
longer be read by an earlier version due to the change of how autoReplace settings are stored.

**User Interface**

* The Session Log dialog, now named Writing Statistics, has been redesigned and now has a few more
  filter options. This update also fixes the filtered time count properly. The dialog now shows a
  histogram of words added in a given session, or optionally, on a given date. The filtered log
  data can also be saved as a JSON or CSV file, the latter suitable for importing to a spread
  sheet. The new dialog tool required a new session log file format, so the new session log has
  been given a new file name. The old log file will be left untouched in the project's `meta`
  folder. For projects created prior to this change, the log will record a word count offset that
  will be subtracted from the first entry such that the first word diff will always be 1 instead of
  the total word count of the entire project. Such a large word diff would otherwise saturate the
  histogram. PRs #339 and #349.
* The document editor panel has received a footer bar like the one recently added to the document
  view panel. The footer bar currently shows the status level of the document, and the document
  word count. In addition, the word counter shows the change in count for the current session in
  the same way project word count and change is shown in the status bar. The document word count
  has been removed from the main window status bar. PR #348.
* The document editor footer can optionally be hidden in Distraction Free mode. PR #351.
* The Italic and Bold menu entries have been renamed to Emphasis and Strong Emphasis, which is more
  in line with what they represent in Markdown and HTML. They are still renderred as Italic and
  Bold in the document viewer, but the HTML export is using the `<em>` and `<strong>` tags. PR
  #350.
* Due to several issues with the formatting of emphasised text using `*`, `**`, and `***` wrappers,
  especially when using nested emphasis, the syntax for emphasis (italic) and strong (bold) has
  been reverted to use `_` and `**` wrapping, respectively. This removes the ambiguity, and
  resolves the corner cases. It was possible to resolve the issues by using a custom written parser
  that takes care of all valid combinations, but such a parser would be a bit too slow for use in
  syntax highlighting. I decided therefore to stick with RegEx parsing, and keeping those RegExes
  as short and fast as possible while enforcing the basic formatting rules. Separating the notation
  for emphasis and strong is commonly recommended when writing Markdown anyway, so it is a sensible
  compromise between speed and flexibility. This PR partially reverses PR #310. Issue #353, PR
  #355.
* The syntax highlighter now properly highlights overlapping formattings, including emphasised text
  inside of highlighted quotes. PR #355.
* The colour highlighting of emphasis, strong and strikethrough, can now be switch off in
  Preferences. The syntax highlighter will still apply the italic, bold and strike effects. PR
  #357.
* The project path in the Details tab of Project Settings can now be selected and copied to
  clipboard. Issue #354, PR #356.

**Other Changes**

* The way the auto-replace settings are stored in the project XML file has been changed in order to
  be more consistent with other features, and to avoid a potential pitfall in defining the tag name
  from a user-entered string. The project class retains its ability to read the old format of the
  file, and will save in the new format. The file format of the project XML file has been bumped to
  1.2. PRs #344, #346 and #347.

----

## Version 0.9.2 [2020-06-26]

**Bugfixes**

* The project tree word counts were getting mixed up when a file was moved to the trash folder, or
  permanently deleted. This has now been fixed, and moving a file should give a zero net change of
  project word count. Permanently deleting it will result in a negative net change. Issue #333, PR
  #335.

**User Interface**

* There is a feature in the project tree class that ensures that the tree item being acted on is
  visible in the tree. It is called when you for instance click the header of an open document. It
  was also activated when opening a document from the tree view with either double-click by mouse,
  or by using the Enter key. This meant that the tree view would often move, which made it hard to
  mouse click on items after eachother since you ended up chasing a moving target. This feature is
  now disabled for document open. In addition, the scroll into view feature has been added to the
  search/replace call to move into the next document when reaching the end of the current document.
  This was requested in Issue #332. PR #334.
* The Build Novel Project tool will now display the build time of the document in the preview
  window in order for the user to know if it is potentially out of date. The timestamp is given, as
  well as a fuzzy time string, indicating the age of the content. Issue #331, PRs #336 and #337.

**Documentation**

* The documentation has been updated to clarify the correct formatting for italic, bold and
  strikethrough formatting tags. Issue #220, PR #338.

----

## Version 0.9.1 [2020-06-21]

**Bugfixes**

* Fixed a serious bug in the replace part of the search/replace function that caused novelWriter to
  crash when the replace text function was called. Issue #327, PR #328.

----

## Version 0.9 [2020-06-21]

**Core Functionality**

* Underline text formatting has been removed. It is not standard HTML5, nor Markdown, and was
  previously implemented using the double underscore notation that in standard Markdown is
  renderred as bold text. Instead, novelWriter now renders a single `*` or `_` wrapping a piece of
  text _within_ a paragraphs as italicised text, and a double `**` or `__` as bold text. The
  keyboard shortcuts and automatic features _only_ support the `*` notation. A triple set of `***`
  are treated as both bold and italicised. PR #310.
* Strikethrough formatting has been added back into novelWriter using the standard Markdown `~~`
  wrapping. PR #310.
* Added support for thin spaces and non-breaking thin spaces. PR #319.
* The `Ctrl+Z` key sequence (undo) would not go through the wrapper function for document action
  for the document editor, but act directly on the document. This caused some of the logic
  preventing conflict between auto-replace and undo to be bypassed. This has now been resolved by
  blocking the keypress itself and let the menu action handle the key sequence. Issue #320, PR
  #321.
* The dialog window size and column width setting for the auto-replace feature in Project Settings
  are now preserved between closing and opening the dialog. Issue #322, PR #324.

**User Interface**

* The Open Project dialog will now ask before removing an entry from the recent projects list. PR
  #309.
* The text emphasis functions, either selected from the menu or via keyboard shortcuts, will now
  try to respond to the command in a more meaningful way. That is, the text editor will try to
  toggle the bold or italics features independently of eachother on the selected text. A menu entry
  to apply both at the same time has also been added. PR #310.
* The document editor search tool has been completely rewritten. It now appears as a search box at
  the top of the document, and has a number of toggle switches added to it. You can modify the
  search tool to be case sensitive, select only whole words, use regular expression search strings,
  loop when reaching the end, and continue the search in the next file in the project tree. For the
  replace feature, you can also select to have the feature try to preserve the case of the replaced
  word. Issues #84 and #305, PR #314.
* A dialog has been added for selecting quotation mark style. These are now used in the Preferences
  dialog instead of a plain text edit box. PR #317.
* Added an insert menu for inserting special symbols like dashes, ellipsis, thin and non-breaking
  spaces, and hard line breaks. PR #319.
* A menu option to replace straight single and double quotes in a selected piece of text has been
  added. This uses the same logic as the auto-replace feature. Issue #312, PR #321.
* When pressing `Ctrl+R` while the document editor has focus, the edited document will be viewed or
  refreshed in the document viewer. Previously, the selected document in the project tree had
  priority. The document is also now saved before loaded in the viewer, ensuring that it shows the
  very latest changes. Issue #143, PR #323.
* The selection in the project tree should not scroll into view when just opening the document.
  This can be quite annoying if loading several documents in sequence by double-clicking as the
  target may move just when you're about to click. PR #325.

**Other Changes**

* Added the file's class and layout to the meta data string of saved document files. This meta data
  is only used to restore the file meta information into the project if it was lost from the
  project file. It is also useful information when reading the file in external tools. PR #308.

----

## Version 0.8 [2020-06-14]

**Bugfixes**

* The HTML converter, used for the document view window as well as the Build Novel Project tool,
  would crash novelWriter if a file included an `@tag:` entry with no actual tag name following it.
  In addition to fixing this issue, the call to the converter is now also wrapped in a `try/except`
  construct to prevent crashes caused by potential edge cases in document content. If the rendering
  fails, the view window will show an error message instead of the intended document. Issue #298,
  PR #299.
* Clipping of the descended part of fonts in the document title bar has been fixed. Issue #295, PR
  #300.
* When clicking a tag in the editor while the viewer was closed, nothing would happen. Now, the
  viewer is first opened before navigating to the source of the reference tag. Issue #294, PR #306.
* The missing optional rendering of synopsis comments in the document view panel has been added.
  Mentioned in Issue #301, PR #311.

**User Interface**

* A details panel below the Outline tree view has been added. The panel shows all the information
  of a selected row in the tree view above, including hidden columns, and some additional
  information. The tags and references also become clickable links that when clicked will open in
  the document viewer. PR #281.
* Icons have been added to the Title and Document columns in the Outline. The titles get a new icon
  indicating the header level, while the documents get the already existing document icon. PR #302.
* Added a context menu to the project tree for easier access to some of the most use actions on the
  tree. PR #282.
* Improved the support for High DPI screens. Margins and box sizes that were hardcoded should now
  scale. User settings should also scale back and forth when switching between scale factors. Issue
  #280, PR #285.
* The total edit time of a project is now displayed on the Details tab of the Project Settings
  dialog. PR #290.
* The title bar in the document editor now has a full screen button and a close button, and in the
  document viewer a reload button and a close button. The full screen button toggles the
  distraction free mode, and the reload button regenerates the document being viewed to update any
  changes that may have been made to it. PRs #293, #300, #303 and #306.
* The References panel below the document viewer has been redesigned. It now sits in a resizeable
  panel below the document, and its controls sit in a footer bar in the document itself. The
  functionality of the feature is otherwise unchanged, but the buttons have received new icons. PRs
  #304 and #306.
* The option to render comments and synopsis in the document view panel has been added to
  Preferences. The toggle option for comments that was previously in the menu has been removed. PR
  #311.

**Project Structure**

* The way GUI states of switches, column widths, etc., is saved has been improved a bit during the
  High DPI updates. PRs #285 and #286.
* Some settings have been moved around to more appropriate sections in the project XML file. The
  project load function still reads the values from the previous location if opening an older
  project file. PR #288.
* A file opened in the Trash folder is no longer "Read Only". The feature was rather arbitrary, and
  also required a GUI element to notify the user of the fact. Any file can now be edited. PR #292.

**Code Structure**

* The core classes making up the project itself were previously merged into a single source code
  file. This file was getting a bit big, so they have been split up again. PR #289.
* A lot of Inkscape meta data has been removed from the SVG icons, reducing the file sizes quite a
  bit. PR #291.
* Opening and closing of files are now properly handled also when using the ConfigParser tool.
  Previously, files were not properly closed after the content had been read, leaving the handles
  open until the Python garbage collector handled them. PR #300.

----

## Version 0.7.1 [2020-06-06]

**Bugfixes**

* For some fonts (especially Ubuntu) the minimum column width in the tree widgets would be
  estimated to be too large. It especially meant that the "include when exporting" flag had a
  column much wider than it needed to be. This setting is now overridden with the known size of the
  icon, plus a 6 pixel margin. PR #278.
* Correctly fixes issue #273, which was actually due to an old css setting from early development.
  PR #287.

**User Interface**

* The Build Novel Project tool now has an option to not style the text before printing or exporting
  to file. PR #276.
* When opening an item in the project tree, the focus remains on the tree and no longer switches to
  the editor. It makes it easier to flip through files and look at them by pressing enter
  repeatedly. PRs #278 and #287.
* Added a title icon and document icon to the outline view. PR #278.
* The timeline class root folder now has a calendar icon instead of a clock. PR #287.
* Regrouped the options on the Build Novel Project tool a bit. They are now sorted into Titles,
  Format, Text and File categories, with more consistent labelling. PR #278.
* A link colour has been added to the Build Novel Project tool. It's the same colour as the header.
  PR #287.

**Other Changes**

* Reduced the number of files and folders in the source code a bit. PR #277.

----

## Version 0.7 [2020-06-01]

**Bugfixes**

* Fixed a bug where novelWriter might crash if a file is deleted immediately after being created,
  and also additional points-of-failure if the project was new. PR #267.

**User Interface**

* The back-references list in the project view panel now shows references to any tag in the open
  document, not just the first tag. Issue #227, PR #234.
* Clicking a tag now tries to scroll to the header where the tag is set. The index needed a couple
  of minor changes for this feature, so this will invalidate the old index for a project saved with
  an older version, and require a new to be built. This is done automatically. PR #234.
* Moved the Close button on the "Build Novel Project" dialog to the area with the other buttons
  since we anyway increased the size of that area. PR #256.
* Updated the unit for Preferences > Editor > Big document limit from `kb` to `kB`. Issue #258, PR
  #260.
* Added Typicons-based coloured icon set also for light GUI background. PR #265.
* The export check mark that was added to the Flags column in the project tree in Version 0.6 has
  been moved to its own column, and been replaced with a proper icon. The details panel below it
  has been updated as well. PR #268.
* Icon sizes are now calculated based on the size of the text, and all text and icons should scale
  relative to the default GUI font size. PR #268.
* The font family and size of the main GUI font can now be changed in Preferences. For Windows,
  this defaults to Cantarell 11pt, which is now shipped with novelWriter. On other systems it
  defaults to the system font. Special accommodations had be made for Ubuntu where the font size of
  the tree widget was not updated automatically (Issue #273). PRs #269, #270, #274 and #275.
* There are no Monospace fonts on the main GUI any more. Where fixed width is needed, the size is
  calculated beforehand with Qt's font metrics class. PR #271.
* Fonts are now selected via the system's font dialog rather than the font combo box. PR #270.
* Word, character and paragraph counts are now updated on the project tree details panel if the
  file currently being edited is also selected in the tree. PR #272.
* The Build Novel Project dialog now shows the previous generated content when it's opened. PR
  #272.
* The Build Novel Project tool can now export the HTML and NWD output into a JSON data file. This
  file is convenient if the user wants to post-process the output with for instance Python, or one
  of the other numerous languages that can read JSON files. PR #272.

**Project Structure**

* The project folder structure has been simplified and cleaned up. We also now freeze the main
  entry values in the main XML file. The XML file is now given version 1.1, and no further core
  changes to its structure will be made without bumping this version. We're also locking it to only
  be opened by version 0.7 or later. An old project file is converted on first open. PRs #253 and
  #261.
* When a project is closed, two table of contents files are written to the project folder. They are
  named `ToC.txt` and `ToC.json` and are there for the user's convenience if they want to find a
  specific file from the project in the data folders. As discussed in Issue #259, PRs #261 and
  #262.
* The expanded node flag from the project tree was also saved for file entries, which cannot
  actually be expanded. These flags are no longer saved in the XML file. PR #261.

**Other Changes**

* Dropped the usage of `.bak` copies of document files. This was the old method to ensure the
  document data was written successfully, but it uses twice the storage space. Instead, writing via
  a temp file is the current safe way to save files. PR #248.
* The project class now records the accumulated time in seconds a project has been opened. This
  data is not yet displayed anywhere, but it is being tracked in the project XML file. PR #261.

**Test Suite**

* Added tests for Build Novel Project, Merge Folder and Split Document tools. PRs #263 and #264.

----

## Version 0.6.3 [2020-05-28]

**Bugfixes**

* It was possible to have the backup folder set to the same folder as the project, resulting in an
  infinite loop when `make_archive` was building the zip file. This crash of paths is now checked
  for before moving to the archive step. Issue #240, PR #241.
* Fixed an issue with the Build Novel Project tool on Ubuntu 16.04 LTS where the dialog wouldn't
  open. Issue #243, PR #246.

**User Interface**

* Renamed the "Generate Preview" button on the "Build Novel Project" tool to "Build Novel Project".
  You must actually click this to be able to export or print. Issue #237, PR #238.
* Added font family and font size selectors to the "Build Novel Project" tool. You may want a
  different print font than used in the editor itself. Issue #230, PR #238.
* Removed the "Help" feature in "Build Novel Project" and instead added detailed tooltips. Issue
  #250, PR #249.
* Changed the title formatting codes for "Build Novel Project" to something less verbose. The old
  codes are translated automatically. Issue #247, PR #249.
* A margin of the viewport (outside the document) has been added to the document editor and viewer
  to make room for the document title bar. Previously, the title bar would sit on top of the
  document's top margin, which would sometimes hide text that would otherwise be visible (when
  scrolling). PR #236.
* Fixed an alignment issue for the status icon on the project tree details panel. Mentioned in
  #235, PR #239.
* Removed the `Xo` icon for NO_LAYOUT in the project tree details panel. Mentioned in #235, PR
  #239.
* Added a "Details" tab to the "Project Settings" dialog, which also lists the project path. Issue
  #242, PR #239.

----

## Version 0.6.2 [2020-05-28]

* Botched release. Replaced with 0.6.3. Crashes when Build Novel Project is opened.

----

## Version 0.6.1 [2020-05-25]

**Bugfixes**

* The Outline view now takes into consideration the exported flag, and does not show excluded files
  in the outline. PR #224.
* Page layout format was ignored when exporting project. The formatting of this layout has now been
  added. PR #224.
* If multiple headings were present in a file, the sorting of headings in the Outline view would
  follow a text sort not a numerical sort of the line numbers. That is, it would be sorted as "1",
  "10", "2", "20", etc. This has been fixed. PR #226.
* The text justification in the preview in the  Build Novel Project was following the main
  Preferences settings, not the Build settings. This did not affect the formatting of the exported
  file itself, but the preview is now made consistent with the build settings. Issue #228, PR #231.

**User Interface**

* Recent projects in the open project dialog can be removed from the list by hitting the delete
  key. PR #225.
* Moved the browse button to after the path box in the open project dialog. PR #225.

**Other Changes**

* The three remaining dependencies now have a minimum version set. PR #224.
* Moved the sample project up one folder level. PR #224.

**Documentation**

* The export page in the documentation erroneously stated that line breaks could be added to titles
  by adding `%\\%`. The correct syntax is `\\`. Issue #229, PR #231.

----

## Version 0.6 [2020-05-24]

**Bugfixes**

* Fixed a bug in validation of `@tag:` meta tags where one or more spaces before the `:` would
  still pass as a valid tag, but the keyword index array would be missing those spaces in its
  counter. This mainly affected the highlighting of keywords, which would be misaligned. PR #206.

**User Interface**

* The Export Tool has been removed and replaced by a new tool called "Build Novel Project". The new
  tool has the same filtering options as the Export Tool, but with more formatting options for
  titles. It also has a preview window to display the generated document. A Save As button provides
  exports to HTML, novelWriter Markdown, plain text, PDF and Open Document format. LaTeX export has
  not been ported over, and interfacing with Pandoc is no longer supported either. Although, as
  before, the HTML export can be converted with Pandoc to other formats outside of novelWriter. The
  new tool also supports printing. PRs #204, #220 and #221.
* The Project Settings, Preferences, Item Editor, Merge Documents, and Split Documents dialogs have
  been redesigned. The ones with tabs now have vertical tabs on the left with horizontal labels.
  The dialog design should be more compact, and have room for more tabs for future settings. PR
  #212.
* A new icon, as well as a mimetype icon for the project files, have been designed and added to the
  app. PRs #213 and #214.
* The About dialog has been completely redesigned to allow more information. PR #217.
* The Open Project dialog has been cleaned up and made more readable. The project paths have been
  moved out of the list, and are now displayed when an item is selected instead. Icons have been
  added, and the New project dialog can also be triggered from this dialog. PR #218.
* The document stats have been added to the details panel below the project tree. PR #219.

----

## Version 0.5.2 [2020-05-21]

**Bugfixes**

* When running on Windows 10, some of the buttons were missing icons. More fallback icons have been
  added to ensure that all current buttons have a fallback path that always ends in an icon. PR
  #211.

**User Interface**

* The statusbar has been redesigned a bit. The block icons showing document and project saved
  status have been replaced by LED icons. The statistics has been moved to a separate label, and
  most of the detailed stats moved to its tooltip. PR #210.
* Default icon theme is now `Typicons Grey Light`. PR #211.
* Clicking on the document header selects the document in the project tree, but this functionality
  has been enhanced to also ensure the document is expanded and visible in the tree. If it's
  scrolled out of view, the tree will scroll it into view. PR #215.
* Syntax highlighting of text in quotes can now be turned off in Preferences. PR #215.

**Core Functionality**

* Checking for version dependencies and a few packages (aside from PyQt5) is now done later in the
  start-up so that it is possible to alert the user with a dialog box instead of terminal error
  messages. PR #210.
* Made a few minor changes to the code so novelWriter can run with Python 3.4.3 and Qt 5.2.1, that
  is, it runs on last version of Ubuntu 14.04. This level of compatibility is not guaranteed to
  remain in the future, but for now, the changes have no impact on functionality. PR #210.

----

## Version 0.5.1 [2020-05-14]

**Bugfixes**

* Fixed a bug where only some of the text would be rendered in the editor window when a large text
  document was loaded. The text is there in the buffer, but the rendering process was interrupted
  by the function that recalculates margins. This recalculation was added with the document tiles
  in 0.5. The re-rendering of the text could be triggered by opening the search bar, indicating
  that it was caused by the shifting of the vertical document frame. PR #208.

**User Interface**

* The icon theme functionality of novelWriter has been reworked. For the default system theme, very
  little has changed. It should still load whatever the system provides, but this doesn't work for
  all icons on Windows 10 for instance. It is now possible to select between three icon themes in
  the Preferences dialog, independent of the GUI theme. Using a theme breaks the dependency on the
  operating system to provide standard icons. Qt provides some, but not all needed by novelWriter.
  PR #207.
* Added a check that warns if the project file was saved with a newer version of novelWriter as
  that may cause meta information to be lost. This warning will remain there until the file format
  is finalised. This is an issue with preserving certain settings, not the project structure
  itself. PR #205

**Debugging**

* Reduced the number of command line switches needed for debug runs. PR #205.

----

## Version 0.5 [2020-05-09]

This release of novelWriter has a number of feature updates, bringing it one step closer to initial
feature completeness for a version 1.0 release.

In the pipeline for 1.0 is a completely new export tool with improved and added options, including
printing. Further improvements are also planned for the new Outline View added in this version.
When these additions are completed, novelWriter will start moving towards a 1.0 release via release
candidates. I'm hoping to wrap up this year and a half long stage of initial development soon so
that I can spend more time using it than creating it.

**Additional thanks** to @countjocular for PRs #173 and #174, and to @johnblommers for all the
helpful feedback and issue reports for the new features added in this, and previous releases.

### Noteable Changes

* The Timeline View dialog is now gone. Instead, the main window area has been split into two tabs.
  The first, the "Editor", contains the Document Editor and Viewer panels. The second, the
  "Outline", contains a new Outline View of the novel part of the project, broken down into a tree
  view of all the project headings. All meta data associated with each part of the novel can be
  viewed in further columns, selectable from a drop down menu by right-clicking the header. These
  columns can also be rearranged.
* Both the Editor and Viewer panels now have a header showing the document label as seen in the
  Project Tree. Optionally, the full path of the document can be viewed. Clicking this header will
  select the document in the Project Tree, making it easier to find where the document belongs in
  the structure.
* A project load dialog has been added when novelWriter is launched. It will show you your recently
  opened projects, let you browse for those that aren't listed, or create a new project. More
  features will be added to this dialog later on.
* The Preferences dialog has been completely redesigned to make it easier to find the various
  settings and understand what they do.

### Detailed Changelog

**Features**

* An Outline View panel has been added to the main GUI window. The Outline View can show all meta
  data associated with a novel heading in a column-wise manner. The Timeline View feature has been
  dropped in favour of the new Outline View. PRs #140, #181 and #191.
* A synopsis feature has been added. It allows a comment to be flagged as a synopsis comment to be
  picked up by the indexer and displayed in the GUI. Currently available in the Outline View. PRs
  #140 and #191.
* A document title bar has been added to the top of the editor and viewer. These show the document
  label as seen in the project tree. Optionally, the full document path can be shown. Clicking the
  title will highlight the document in the project tree. PRs #192 and #194.

**User Interface**

* A Project Load dialog has been added, which pops up when novelWriter is launched. It allows for
  opening other recent projects, browse for projects, or start a new project. This replaces the
  former Open and New Project features, as well as the Recent Projects menu entry. PRs #177 and
  #183.
* The command line switches for debugging have been changed a bit. Higher level of debugging now
  includes the lower levels, preventing the need for specifying for instance both debug and verbose
  debug. PR #182.
* The Preference dialog has been completely redesigned. The options are now displayed vertically,
  in four tabs instead of two, and with more informative text explaining what they do. Some
  previously unconnected options have also been added. PR #193.

**Bug Fixes**

* The `install.py` script has been fixed to reflect changes in storage location of the themes. PR
  #174.
* Fixed a bug with launching Preferences without Enchant spell checking installed. PR #190.
* A minor issue with running backups with no backup path set has been fixed. The backups would be
  written into the source folder, or wherever novelWriter was launched from, which is a very messy
  fallback. PR #195.

**Documentation**

* Some outdated links and a number of typos and spelling errors have been corrected. PR #173.
* Documentation has been brought up to date with the current set of features of novelWriter. PR
  #202.

**Project Structure**

* Opening a project now writes a lock file to alert the user if the same project is opened more
  than once. The warning can be ignored if the user wants to proceed. PR #179.
* Two new meta tags have been added to the project file to store a counter for the number of times
  the project has been saved or autosaved. The meta information is not currently displayed in the
  GUI, but could be added to an About Project dialog in the future. The PR also adds checks to
  ensure XML attributes exist before attempting to load them. PR #180.
* A single line of document meta data is now written to the top of document files. They mainly
  serve to identify the file content if one opens the file directly in an external editor, but also
  assist the Orphaned Files tool to identify the files when they are found, but missing from the
  project tree. PRs #200 and #201.

**Code Improvements**

* For the Outline View, the `NWIndex` class has been restructure and extensively rewritten. It is
  more fault tolerant, and will automatically rebuild a corrupt index loaded from cache. PR #140.
* The way that dialog options (which options were selected last time a dialog was open) has been
  rewritten. All data is now stored in a single JSON file in the project meta folder. PR #175.
* Since the config class is instanciated before the GUI, error reporting to the user was tricky. An
  error cache has now been added to allow non-critical errors to be displayed after the GUI is
  built. PR #176.
* All source files now have the minimal GPLv3 license note at the top. PR #188.
* Also added license info to the command line output. PR #189.
* Large chunks of the code has been restructured. Mainly the non-GUI parts, which have mostly been
  merged into a new `core` folder. Several classes which are only used by a single object have been
  merged into the same file, reducing the total number of source files a bit. PR #199.

----

## Version 0.4.5 [2020-02-17]

**Features**

* A project can now be opened from the command line by providing the project path to the launching
  script. PRs #164 and #166.

**User Interface**

* Added functionality to split a document into a folder of multiple documents, and also to merge a
  folder of documents into a single document. PRs #159 and #163.
* It is now possible to permanently delete files from the Trash folder. This can be done
  file-by-file or by using the Empty Trash option in the menu. PRs #159 and #163.
* When running the spell checker, a wait cursor is displayed. This will alert the user that
  novelWriter is working on something when, for instance, a very large document is opened and
  initial spell checking is running. PR #158.

**Bug Fixes**

* Fixed a few keyboard shortcuts that were not working in distraction free mode. PR #157.
* Added a check to ensure the user does not drag and drop an item into the Orphaned Items folder.
  Since this folder is not an actual project item, novelWriter would crash when trying to change
  the dropped item's parent item to the Orphaned Items folder. Now, instead, the drop event is
  cancelled if the target folder is Orphaned Items. PR #163.

**Code Improvements**

* The way project files are saved has been altered slightly. When a project file or document file
  is saved, the data is first streamed to a temp file. Then the old storage file is renamed to
  .bak, and and the temp file is renamed to the correct storage file name. This ensures that the
  storage file is only replaced after a complete and successful write. PR #165.
* The cache folder has been removed. It was used to store the 10 most recent versions of the
  project file. Instead, the previous project file is renamed to .bak, and can be restored if
  opening from the latest project file fails. Any additional restore capabilities should be ensured
  by backup solutions, either the internal simple zip backup, or other third party tools. PR #165.
* The dependency on the Python package `appdirs` has been dropped. It was used only for extracting
  the path to the user's config folder, a feature which is also provided by Qt. PR #169.

----

## Version 0.4.4 [2020-02-17]

* Botched release. Replaced with 0.4.5.

----

## Version 0.4.3 [2019-11-24]

**User Interface**

* Added keyboard shortcuts and menu entries for formatting headers, comments, and removing block
  formats. PR #155.
* Disable re-highlighting of open file when resizing window. This is potentially a slow process if
  the spell checker is on and the file is large. There is no need to do this just for reflowing
  text, so it is now disabled on resize events. Issue #150, PR #153.
* Improved the speed of the syntax highlighter by about 40% by not using regular expressions for
  highlighting block formats and by skipping empty lines entirely. PR #154.

**Bug Fixes**

* Fixed an issue when closing the import file dialog without selecting a file, the import would
  procede, but fail on file not found. The import is now cancelled when there is no file selected.
  PR #149.
* Fixed an issue with markdown export where it did not take into account hard line breaks. Issue
  #151, PR #152.
* Fixed a crash when running file status check when the project contains orphaned files. PR #152.

----

## Version 0.4.2 [2019-11-17]

**User Interface**

* Distraction free mode now also hides the menu bar, but all keyboard shortcuts used for editing
  remain active. The rest are disabled. PR #142.

**Bug Fixes**

* Fixed various issues with spell checking highlighting. The highlighting and the editor didn't
  always agree on what words were spelled wrong. PR #141.
* The status bar now shows what spell checking language is actually loaded. Previously, it just
  showed the language selected in the settings. That was a bit misleading as the available
  dictionaries can change due to the change in installed dictionary on the system. PR #145.

----

## Version 0.4.1 [2019-11-10]

**Features**

* If no external spell check package is available, novelWriter can now fall back to use a simple
  spell checker based on word similarity comparison provided by the Python standard package
  `difflib`. That means spell checking is always available, although the difflib-based spell
  checker is both slow and lacks many features of other packages. This feature comes with a general
  English dictionary, and a GB and US dictionary. These are just lists of correct words provided by
  aspell. PR #130.
* Language information (spell checker) is now shown on the status bar. In addition, the timer has
  been converted to monospace font and received an icon. PR #136.
* The new icons exist in both dark and neutral mode, and the mode can be set in the preferences.
  This makes it easier to see the icons on a dark system theme. PR #135.
* Distraction free mode, key shortcut `F8`, and full screen mode, shortcut `F11`, are now
  available. This PR also fixes some issues with rescaling of text margins when windows or panels
  are resized. PR #137.

**User Interface**

* Most text boxes now have a character limit. Before, the only limit was the limit set by Qt itself
  of ~32k characters. PR #126.
* Key combination `Ctrl+G` is now an alternative to `F3`, forward search, and vice versa for
  backwards search. This makes more sense on macOS. Issue #124, PR #126.
* The shortcut for the replace feature is now `Cmd+=` on macOS, and remains `Ctrl+H` on Linux and
  Windows. Issue #124, PR #126.
* The sample project in the source code has been improved to better show the features of
  novelWriter as they currently are. The old text was a bit out of date. The new text also explains
  the features it demonstrates. PR #132.

**Bug Fixes**

* Fixed a bug where a long file label would expand the tree pane due to the details panel
  expanding. The label itself will no longer show more than 100 characters, and is word wrapped.
  Issue #120, PR #122.

**Code Improvements**

* The code has been reorganised, import headers been cleaned up, and the code made more or less
  PEP8 compliant. PRs #118, #119, and #138.
* The dependency on the `pycountry` package has been dropped. The feature based on it now uses an
  internal list of country codes for describing spell checker languages. PR #129.
* The themes manager has been improved, and the loading of icons now supports a number of fallback
  steps to ensure something is shown in most cases. The final fallback is the system's own icon
  theme. PR #135.

----

## Version 0.4 [2019-11-03]

**Features**

* The export dialog now allows limited support for exports using Pandoc. The Pandoc conversion is
  run as a stage two of the export process. Pandoc integration is fickly on Windows, but works well
  on Linux. PRs #82 and #104.
* The editor now supports Markdown standard hard line breaks, and exports these correctly to the
  various file formats and to the document view pane. Hard line breaks can be inserted by either
  appending two or more spaces to the end of a line, or by pressing `Shift+Enter`. PR #83.
* The editor now supports and preserves non-breaking spaces. Unfortunately, the preservation of
  these spaces on save and reload is dependent on Qt 5.9 or later. Non-breaking spaces are
  preserved on export to html and LaTeX. PR #87.
* An option to show tabs/spaces and line endings in the document editor has been added to the
  Preferences dialog. PR #90.
* The document view pane now has a "Referenced By" panel at the bottom, showing links to all
  documents referring back to the document being viewed. The panel is collapsible, and has a sticky
  option that will prevent it from updating if links are followed. PRs #109 and #110.
* The tag and reference system no longer has any restrictions on file class. That is, any file can
  have tags and references, and they are indexed by the indexer and displayed as links in the
  document view pane. The timeline view behaves as before, only listing active Novel files. PR
  #114.
* A new root folder type and keyword for "Entities" has been added. These can be useful for
  describing plot elements fitting under such a category. PR #115.

**User Interface**

* Tags and references in the editor are now "clickable" in the sense that pressing `Ctrl+Enter`
  with the cursor on them will open the reference in the view pane. PR #98.
* Warnings triggered when the user tries to use features with missing package dependencies will now
  provide a link to the package website. PR #86.
* Adding the `~` character in file path boxes is now expanded to the user's home directory. PR #94.
* The recent projects submenu no longer has a number prefix, and a "Clear Recent Projects" option
  has been added. PRs #86 and #94.
* Syntax themes based on Night Owl and Light Owl themes have been added. PR #97.
* Read-only files now have a notification popping up at the top of the edit pane, and the files are
  actually not editable. PR #106.
* Tabs are now properly exported in formats where this makes sense. For plain text files, a tab is
  converted to four spaces. For html exports they are converted to a long space, equivalent to four
  spaces. PR #113.
* A toggle button in the Document menu now allows displaying file comments in the document view
  panel. PR #115.

**Bug Fixes**

* Some issues with unicode conversion and LaTeX export have been addressed, but the escaping of
  unicode characters is prone to errors. The user should be careful with using special symbols if
  export to LaTeX is intended. The package `latexcodec` should be able to handle Latin based,
  language specific characters. PRs #73 and #79.
* Fixed some long-standing issues with running novelWriter on Windows. The config folder requires a
  set of two folders to be created on first use, which the config class did not expect. This is now
  resolved. In addition, Python does not default to utf-8 when writing files on Windows, so all
  open statements now have encoding defined. Failing to open files also had the risk of truncating
  them. This has been avoided by distinguishing new files from broken files. PR #81.
* Dark theme was not rendering properly on multiple platforms. This was resolved by forcing the Qt5
  style to "Fusion", which allows further formatting by the novelWriter themes code. The user can
  override the Qt styling option through the `--style=` flag on the command line. PR #96.
* The behaviour of files in the Trash folder has been fixed. These are now read only. PR #106.
* Fixed a bug where the last line of a title or partition page would be ignored on export. PR #113.
* Drag and drop onto the root level of the tree has been disabled. This was anyway only allowed for
  root folder items, but it was tricky to enforce this properly for other files. In order to move
  root folders around now, the move up and down features need to be used instead. #115.

**Installation**

* A script for `pyinstaller` has been added, making it possible to generate standalone executables
  of novelWriter on at least Windows and Linux. PR #91.
* novelWriter has been made `pip install` ready. PRs #107 and #108.

----

## Version 0.3.2 [2019-10-27]

**Documentation**

* The documentation has been rewritten and added to the Read the Docs website. Pressing `F1` or
  `Help > Documentation` in the menu opens the novelWriter documentation page. PRs #68 and #69.

**User Interface**

* Filters have been added to the Timeline View window so unused tags can be hidden, and it's
  possible to select only certain classes of tags to display. PRs #61 and #62.
* The dialog boxes for Timeline View and Session Log now remember the filter choices from previous
  instance for the same project. PR #62.
* When having a document open in the editor, text can be imported into it from a plain text file.
  No formatting conversion of the imported text is performed. That is up to the user. However, this
  allows for importing novelWriter documents from other projects or from a previous export,
  partially addressing request in issue #63. PR #65.
* The Export feature now includes exporting to LaTeX, which allows building PDFs with pdflatex or
  other tools. PR #73.
* Export of a novelWriter flavour markdown file is also supported. This file can be imported back
  in as-is, and almost completes an export-edit-import cycle. A split document into multiple files
  feature will be added soon. PR #73.

----

## Version 0.3.1 [2019-10-20]

**Bug Fixes**

* The backup request dialog should pop up on any change to the project during the last session, not
  just on unsaved changes. PR #58.
* The regex that searches for words for the spell check highlighter was not including unicode
  characters, so it would underline parts of words using unicode characters even if the word was
  spelled correctly. PR #58.
* When having unsaved changes in an open document, while changing editor configuration options, the
  document would be reloaded from disk when the changes were applied. This meant the unsaved
  changes were lost. The document is now saved before the editor is re-initialised. PR #58.

**User Interface**

* Added a GUI to display the session log. The log has been around for a while, and records when a
  project is opened, when it's closed, and how many words were added or removed during the session.
  This information is now available in a small dialog under `Project > Session Log` in the main
  menu. PR #59.
* The export project feature now also exports the project to Markdown and HTML5 format. PR #57.

----

## Version 0.3 [2019-10-19]

**User Interface**

* Added project export feature with a new GUI dialog and a number of export setting. The export
  feature currently only exports to a plain text file. PR #55.

----

## Version 0.2.3 [2019-10-06]

**User Interface**

* The search feature now also allows for replacing text, so the basic search/replace tools in now
  complete. PRs #51 and #52.
* All icons have been removed from the menu, and the dark theme has received a new set of basic
  icons. They are not very fancy, so will perhaps be replaced by a proper icon set later. PR #53.

----

## Version 0.2.2 [2019-09-29]

**Bug Fixes**

* Fixed a bug where loading a config file with the dictionary language set to `None`, or presumably
  a missing dictionary, would trigger a fatal error. PR #47.

**User Interface**

* Added a basic search function for the currently open document. This is a simple interface to the
  find command that exists in the Qt document editor. It will be extended further in the future. PR
  #49.

----

## Version 0.2.1 [2019-09-14]

**Bug Fixes**

* The _Tomorrow_ theme had the wrong set of colours. PR #39.

**Documentation**

* Added the backup feature to the documentation. PR #40.

**User Interface**

* The auto-replace list in project settings is now sorted alphabetically. PR #43.
* Added version checking of the Qt5 and PyQt5 dependencies. Non-essential functionality that
  depends on very recent versions of Qt5 are now switched off if version is too low. Currently only
  affects the custom tab stop length, which requires version 5.10. Issue #44, PR #45.

**Code Improvements**

* Minor changes to the About novelWriter dialog and to how backup filenames are generated. PR #41.

----

## Version 0.2 [2019-06-27]

**Documentation**

* Added documentation in English. The help file opens in the document view pane when the user
  presses `F1` or selects it from the Help menu. PR #27.

**Themes**

* Complete rewrite of how syntax highlighting and GUI themes are handled. These are now set
  separately, and the dark theme uses QPalette to handle the dark colours, which makes the dark
  theme a lot more portable between operating systems. #34 and #35.
* Added the five "Tomorrow" colour themes to list of syntax highlighter themes. PRs #34 and #35.

**User Interface**

* Added a preferences dialog for the program settings. No longer necessary to edit the config file.
  PR #30.
* The document viewer remembers scroll bar position when pressing `Ctrl+R` on a document already
  being viewed. PR #28.
* Removed version number from windows title. PR #28.
* The auto-replace items in Project Settings are now editable. PR #29.
* Changed how document margins are handled. This implementation works better and drops the
  difference between horizontal and vertical margins in favour of using the QTextDocument margin
  setting. PR #33.

**Code Improvements**

* Spell checking is now handled by a standard class that can be subclassed to support different
  spell check tools. This was done because pyenchant is no longer maintained and having a standard
  wrapper makes it easier to support other tools. PR #31.

----

## Version 0.1.5 [2019-06-08]

**Bug Fixes**

* Closing the application with the window X button, and selecting No on the dialog, still closed
  the application. Properly handling the close event now so that the closing is cancelled. PR #21.
* Many of the menu option would cause novelWriter to exit or otherwise make mistakes when clicked
  if no project was open. They all check for this now. PR #23.

**Timeline**

* Added an index to the project that holds the position of all headers in the novel part of the
  project and all tags set in the notes part. It also holds all the links from novel files to
  notes. The relationship can be viewed in a new TimeLineView GUI. It's in the tools menu, and can
  also be opened with `Ctrl+T`. PR #22.
* The spell checker now used this index to highlight keywords/value sets. If the keyword or value
  is not valid, it will not be highlighted and will instead have a wiggly line under it. This also
  checks that references point to valid tags. For this to work, the index has to be up to date. The
  index of a file is saved when the file is saved, but the entire index can be rebuilt by pressing
  `F9`. PR #22.

**Status Bar**

* Redesign of the status bar adding project and session stats as well as a session timer. PR #21.
* Project word count is written to the project file, which is needed for the session word count. PR
  #21.
* Closing a project now clears the status bar. PR #21.

**Editor**

* Spell checker now ignores lines staring with `@`, and words in all uppercase. PR #21.
* A document can be closed, which also clears it from last edited document setting in the project
  file. I.e. it is not re-opened on next start. PR #21.
* Tab width is now by default 40 pixels, and can be set in the config. PR #21.

----

## Version 0.1.4 [2019-05-25]

**Bug Fixes**

* Fixed a bug where an item had to be selected in the tree view for a root item to be created. PR
  #16.

**User Interface**

* The main area can now be split into two, with the document editor on the left and a document
  viewer on the right. PR #13.
* The list of novel document status and plot element importance levels can now be edited through
  the Project Settings dialog. The values are per project, and saved in the main project XML file.
  PR #17.
* Cleaned up opening and closing projects, as well as how new projects are created. A new project
  can also not be saved in a folder already containing a novelWriter project. That was previously
  possible, resulting in the old XML file being overwritten. PR #18.
* Some minor GUI improvements were added, PR #19:
  * Pressing `F2` also opens the edit item dialog, like `Ctrl+E` does.
  * When the document editor and viewer split slider is moved, the editor resizes properly.
  * The document viewer can be closed, expanding the editor to the full window size again.
  * A project can be closed with `Ctrl+Shift+W`, and the menu entry has an icon.
  * Exit button/menu now asks if you want to close.

**Themes**

* The colours for syntax highlighting can now be edited in a config file in the themes folder. The
  main GUI css file also lives in the same folder. The default theme lives in the default
  subfolder, and more folders can be added. Switching themes involve changing the theme setting in
  the main config file to the name of the themes subfolder. PR #15.

**Code Improvements**

* Loading the project with the items in the wrong order is possible. That is, the child item is
  stored before its parent. A saved file should not ever be like that, but an edited file might.
  Even if the file shouldn't be edited manually. PR #16.

----

## Version 0.1.3 [2019-05-18]

**User Interface**

* The cursor position is now saved when a document is saved, and restored when the document is
  opened. PR #12.

**Test Suite**

* Major upgrades to the test suite, now also testing GUI elements. Coverage at 73%. PRs #9 and #11.

----

## Version 0.1.2 [2019-05-12]

**Bugfixes**

* Fixed a critical GUI bug when trying to create new folders and files in the tree.
* Caught a bug when creating a new file, but novelWriter couldn't figure out what class the parent
  item had and returned a `None`. Could not recreate the bug, but added a check for it anyway.

**Code Improvements**

* Changed the way user alerts are generated, and added the alert levels to an enum class named
  `nwAlert`. Also added a new level named `BUG`.

----

## Version 0.1.1 [2019-05-12]

**User Interface**

* Rewritten the spell check context menu. The previous implementation was adapted from a Qt4
  example, but could be improved a great deal. It now also doesn't have the default context menu,
  and allows for adding words to personal word list. Spell checking can also be enabled and
  disabled from the menu, and re-run on a the current document. PRs #1 and #3

**Test Suite**

* Added a unit test framework based on `pytest`. This currently checks basic opening and saving of
  the main config file and the main project file. PR #2

----

## Version 0.1 [2019-05-10]

This is the initial release of a working version of novelWriter, but with very limited
capabilities. So far, the following has been implemented:

* A document tree with a set of pre-defined root folders of a given set of classes for different
  purposes for novel writing. That is, a root item for the novel itself, one for charcaters, plot
  elements, timeline, locations, objects, and a custom one.
* A plain text editor with a simplified markdown format that allows for four levels of titles, and
  bold, italics and underline text.
  * In addition, the format supports comments with lines starting with a `%`.
  * It also allows for keyword/value sets staring with the character `@`. These will later be used
    to link documents together as tags point to other documents. For instance, a scene file can
    point the keyword `@POV:name` to a character file with the keyword `@THIS:name`.
* The text editor has a set of autoreplace features:
  * Dashes are made by combining two or three hyphens.
  * Three dots are replaced with the ellipsis.
  * Straight quotes with your quote format of choice.
* The text editor also allows for wrapping either selected text, or the word under the cursor, in:
  * Bold, italics, or underline tags.
  * Single, or double quotes.
