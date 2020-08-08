# novelWriter

[![Build Status](https://travis-ci.com/vkbo/novelWriter.svg?branch=main)](https://travis-ci.com/vkbo/novelWriter)
[![codecov](https://codecov.io/gh/vkbo/novelWriter/branch/main/graph/badge.svg)](https://codecov.io/gh/vkbo/novelWriter)
[![Documentation Status](https://readthedocs.org/projects/novelwriter/badge/?version=latest)](https://novelwriter.readthedocs.io/en/latest/?badge=latest)
[![PyPI](https://img.shields.io/pypi/v/novelwriter)](https://pypi.org/project/novelWriter/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/novelwriter)](https://pypi.org/project/novelWriter/)

<img align="left" style="margin: 0 16px 4px 0;" src="https://raw.githubusercontent.com/vkbo/novelWriter/main/assets/icons/96x96/novelwriter.png">

novelWriter is a markdown-like text editor designed for writing novels and larger projects of many
smaller plain text documents. It uses its own flavour of markdown that supports a meta data syntax
for comments, synopsis and cross-referencing between files. It's designed to be a simple text editor
which allows for easy organisation of text files and notes, built on plain text files for
robustness.

The plain text storage is suitable for version control software, and also well suited for file
synchronisation tools. The core project structure is stored in a project XML file. Other meta data
is primarily saved in JSON files.

The full documentation is available at [novelwriter.readthedocs.io](https://novelwriter.readthedocs.io/).


### Note on the Default Branch

The default branch on this repository switched to `main` on 6. August 2020. If you are running
novelWriter from a git clone, you need to clone the repository again.

Alternatively, you can run the following to get back on the main branch:

```bash
git remote update
git checkout -t origin/main
```


### Development Status

The application is still under initial development, but all core features have now been added. The
core functionality has been in place for a while, and novelWriter is being used for writing projects
by the author and collaborators.

No new major features will be added at this time, until the application is stable. Until then,
novelWriter is in a _beta_ state. Please report any issues you may encounter in the repository issue
tracker.

You should be able to use novelWriter for real projects, but as with all software, please make
regular backups. There is a built in backup feature that can pack the entire project into a zip file
on close. Please check the documentation for further details.


## License

This is Open Source software, and novelWriter is licensed under GPLv3. See the
[GNU General Public License website](https://www.gnu.org/licenses/gpl-3.0.en.html) for more details,
or consult the [LICENSE](LICENSE.md) file.

Bundled assets have the following licenses:

* The Typicon-based icon themes by Stephen Hutchings are licensed under
  [CC BY-SA 4.0](http://creativecommons.org/licenses/by-sa/4.0/). The icons have been altered in
  size and colour for use with novelWriter, and some additional icons added. The original icon set
  is available at [stephenhutchings/typicons.font](https://github.com/stephenhutchings/typicons.font).
* The Cantarell font by Dave Crossland is licensed under [OPEN FONT LICENSE Version 1.1](http://scripts.sil.org/OFL).
  It is available at [Google Fonts](https://fonts.google.com/specimen/Cantarell).
* The Tomorrow syntax themes use colour schemes taken from Chris Kempson's collection of code editor
  themes, licensed with the [MIT License](https://github.com/chriskempson/tomorrow-theme/blob/master/LICENSE.md),
  and the main repo is available at [chriskempson/tomorrow-theme](https://github.com/chriskempson/tomorrow-theme).
* Likewise, the Owl syntax themes use colours from Sarah Drasner's code editor themes, licensed with
  the [MIT License](https://github.com/sdras/night-owl-vscode-theme/blob/master/LICENSE), and the
  main repo is available at [sdras/night-owl-vscode-theme](https://github.com/sdras/night-owl-vscode-theme).


## Markdown Flavour

novelWriter is _not_ a full-feature Markdown editor. It allows for a minimal set of formatting
needed for writing text documents for novels. These are currently limited to:

* Headings level 1 to 4 using the `#` syntax only.
* Emphasised, strong text. These are rendered as italicised and bold.
* Strikethrough text.
* Hard line breaks using two or more spaces at the end of a line.

That is it. Features not supported in the editor are also not exported when using the export tool.

In addition, novelWriter adds the following, which is otherwise not supported by Markdown:

* A line starting with `%` is treated as a comment and not rendered on exports unless requested.
  Comments do not count towards the word count. If the first word of the comment is `synopsis:`, the
  comment is indexed and treated as the synopsis for the following section of text. These synopsis
  comments can be used to build an outline and exported to external documents.
* A set of meta data keyword/value sets starting with the character `@`. This is used for tagging
  and inter-linking documents.
* Non-breaking spaces are supported as long as your system is using at least Qt 5.9. For earlier
  version, non-breaking spaces are converted to normal spaces when saving the document. This is done
  by the Qt library.
* Thin spaces are also supported, as well as non-breaking thin spaces.
* Tabs may be rendered, depending on export format. With Qt 5.10 or higher, the width of a tab in
  pixels can be changed in Preferences.

The core export format of novelWriter is HTML5. You can also export the entire project as a single
novelWriter flavour document. In addition, other exports to Open Document, PDF, and plain text is
offered through the Qt library, although with limitations to formatting.


## Implementation

The application is written in Python3 using Qt5 via PyQt5. It is developed on Linux, but it should
in principle work fine on other operating systems as well as long as dependencies are met. It is
regularly tested on Windows 10.

The application can be started from the source folder with one of the commands:
```
./novelWriter.py
python novelWriter.py
python3 novelWriter.py
```

It also takes a few parameters for debugging and such, which can be listed with the switch `--help`.

In the root assets folder there are icons and scripts and a template for setting up a launcher on
Gnome desktops. You may need to modify those scripts slightly, but as they are, they work on Debian
and Ubuntu. For other operating systems, please consult your operating system documentation for how
to make those. Feel free to submit more if you are able to make them.


## Package Dependencies

It is recommended that novelWriter runs with Qt 5.10 or later, and Python 3.6 or later. Running with
Qt as low as 5.2.1 and Python 3.4.3 has been tested, and worked in the past, but there are no
guarantees that this will keep working as these are not a part of the test builds.

For the apt package manager on Debian systems, the following Python3 packages are needed:

* `python3-pyqt5` for the GUI
* `python3-pyqt5.qtsvg` may need to be installed separately
* `python3-lxml` for writing project files

These are optional, but recommended:

* `python3-enchant` for better spell checking

Alternatively, the packages can be installed with `pip` by running
```bash
pip install -r requirements.txt
```

in the application folder.

You can also do them one at a time, skipping the ones you don't need:
```bash
pip install pyqt5
pip install lxml
pip install pyenchant
```

PyQt/Qt should be at least 5.3, but ideally 5.10 or higher for nearly all features to work.
Exporting to markdown requires PyQt/Qt 5.14. There are no known minimum for `lxml`, but the code
was originally written with 4.2. The optional spell check library must be at least 3.0.0 to work
with Windows 64 bit systems. On Linux, 2.0.0 also works fine.

If no external spell checking tool is installed, novelWriter will use a basic spell checker based on
standard Python package `difflib`. Currently, only English dictionaries are available for this spell
checker, but more can be added to the `nw/assets/dict` folder. See the [README](nw/assets/dict/README.md)
file in that folder for how to generate more dictionaries. Note that the difflib-based option is
both slow and limited.

Note: On Windows, make sure Python3 is in your PATH if you want to launch novelWriter from command
line. You can also right click the `novelWriter.py` file, create a shortcut, then right click again,
select "Properties" and change the target to your python executable and `novelWriter.py`.

It should look something like this:
```
C:\...\AppData\Local\Programs\Python\Python38\python.exe novelWriter.py
```

## Key Features

Some features of novelWriter are listed below. Consult the documentation for more information.


### Colour Themes

The editor has syntax highlighting for the features it supports, and includes a set of different
syntax highlighting themes. The GUI also has an optional dark theme in addition to the default
system theme.

New themes can easily be added to the `nw/assets/themes` folder. Have a look in the existing folders
for examples of how to define the colours.


### Auto-Saving and Document Stats

Open documents and the project file itself is saved regularly on a timer. The status of this is
indicated by two indicators on the right hand side of the status bar. Latest project word count is
shown next to these indicators in the status bar. The counts are updated regularly, but not
as-you-type.

The word count for documents is presented in a footer in the document editor itself. Both project
and document word counters will also show how many words you've added in the current writing
session.


### Easy Organising of Project Files

The structure of the project is shown on the left hand side of the main GUI. Project files are
organised into root folders, indicating what class of file they are. The most important root folder
is the Novel folder, which contains all of the files that makes up the finished novel. Each root
folder can have subfolders. Folders have no impact on the project structure, they are purely tools
for organising the files in whatever way the user needs.

The editor supports four levels of headings, which determines what level the following text belongs
to. Headings of level one signify a book or partition title. Headings of level two signify the start
of a new chapter. Headings of level three signify the start of a new scene. Headings of level four
can be used internally in each scene to separate sections.

Each novel file can be assigned a layout format, which shows up as a flag next to the item in the
project tree. These are mostly to help the user see what they contain, but they also have some
impact on the format of the exported document. See the documentation for further details.


#### Project Notes

Supporting note files can be added for the story plot, characters, locations, story timeline, etc.
These have their separate root folders. These are optional files.


### Visualisation of Story Elements

The different notes can be assigned tags, which other files can refer back to using special meta
keywords. This information can be used to display an outline of the story, showing where each scene
connects to the plot, and which characters, etc. occur in them. In addition, the tags themselves are
clickable in the document view pane, and control-clickable in the editor. They make it possible to
quickly navigate between the documents while editing.


## Contribution

If you want to contribute to novelWriter, please follow the coding convention laid out in the
[Style Guide](markdown/style.md). They broadly follow Python PEP8, but there are a few
modifications.


## Screenshot

**novelWriter with default system theme:**
![Screenshot 1](https://raw.githubusercontent.com/vkbo/novelWriter/main/docs/source/images/screenshot_default.png)

**novelWriter with dark theme:**
![Screenshot 2](https://raw.githubusercontent.com/vkbo/novelWriter/main/docs/source/images/screenshot_dark.png)
