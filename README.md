# novelWriter

[![Linux](https://github.com/vkbo/novelWriter/actions/workflows/test_linux.yml/badge.svg?branch=main)](https://github.com/vkbo/novelWriter/actions/workflows/test_linux.yml)
[![Windows](https://github.com/vkbo/novelWriter/actions/workflows/test_win.yml/badge.svg?branch=main)](https://github.com/vkbo/novelWriter/actions/workflows/test_win.yml)
[![macOS](https://github.com/vkbo/novelWriter/actions/workflows/test_mac.yml/badge.svg?branch=main)](https://github.com/vkbo/novelWriter/actions/workflows/test_mac.yml)
[![flake8](https://github.com/vkbo/novelWriter/workflows/flake8/badge.svg)](https://github.com/vkbo/novelWriter/actions)
[![codecov](https://codecov.io/gh/vkbo/novelWriter/branch/main/graph/badge.svg)](https://codecov.io/gh/vkbo/novelWriter)
[![docs](https://readthedocs.org/projects/novelwriter/badge/?version=latest)](https://novelwriter.readthedocs.io/en/latest/?badge=latest)  
[![release](https://img.shields.io/github/v/release/vkbo/novelwriter)](https://github.com/vkbo/novelWriter/releases)
[![pypi](https://img.shields.io/pypi/v/novelwriter)](https://pypi.org/project/novelWriter)
[![python](https://img.shields.io/pypi/pyversions/novelwriter)](https://pypi.org/project/novelWriter)

<img align="left" style="margin: 0 16px 4px 0;" src="https://raw.githubusercontent.com/vkbo/novelWriter/main/setup/icons/scaled/icon-novelwriter-96.png">

novelWriter is a plain text editor designed for writing novels assembled from many smaller text
documents. It uses a minimal formatting syntax inspired by Markdown, and adds a meta data syntax
for comments, synopsis, and cross-referencing. It's designed to be a simple text editor that allows
for easy organisation of text and notes, using human readable text files as storage for robustness.

The project storage is suitable for version control software, and also well suited for file
synchronisation tools. All text is saved as plain text files with a meta data header. The core
project structure is stored in a single project XML file. Other meta data is primarily saved as
JSON files.

The full documentation is available on [readthedocs.io](https://novelwriter.readthedocs.io).

The full credits are listed in [CREDITS.md](https://github.com/vkbo/novelWriter/blob/main/CREDITS.md).

## Implementation

The application is written in Python 3 (3.6+) using Qt5 and PyQt5 (5.3+). It is developed on Linux,
but should in principle work fine on other operating systems as well as long as dependencies are
met. It is regularly tested on Debian and Ubuntu Linux, Windows, and macOS.

## Project Contributions

Please don't make feature pull requests without first having discussed them with the maintainer.
You can make a feature request in the issue tracker, or if the idea isn't fully formed, start a
discussion on the discussion page. Please also don't make pull requests to reformat or rewrite
existing code unless there is a very good reason for doing so.

Fixes and patches are welcome. Contributions related to packaging and installing novelWriter will
also be appreciated, but please make an issue or a discussion topic first. Before contributing any
code, please read the full [Contributing Guide](https://github.com/vkbo/novelWriter/blob/main/CONTRIBUTING.md).

New translations are always welcome. Please read the additional
[instructions](https://github.com/vkbo/novelWriter/blob/main/i18n/README.md) for further details.

## Key Features

Some key features of novelWriter are listed below. Consult the
[documentation](https://novelwriter.readthedocs.io) for more information.

### Formatting Codes

Although novelWriter is a plain text editor, it uses a Markdown-like syntax to allow for a minimal
set of formatting that is useful for the specific task of writing novels.

| Code       | Usage    | Description |
|------------|----------|-------------|
| `#`        | Prefix   | Headings level 1 to 4. |
| `_`        | Wrapped  | Emphasised (italicised) text. |
| `**`       | Wrapped  | Strongly emphasised (bold) text. |
| `~~`       | Wrapped  | Strikethrough text. |
| `%`        | Prefix   | A comment; does not count towards the word count.<sup>1</sup> |
| `@`        | Prefix   | The following text is parsed as a keyword/value command for meta data. |
| `>`        | Prefix   | The paragraph is indented one tab width from the left.<sup>2</sup> |
| `<`        | Suffix   | The paragraph is indented one tab width from the right.<sup>2</sup> |
| `>>`       | Prefix   | The paragraph is right-aligned.<sup>2</sup> |
| `<<`       | Suffix   | The paragraph is left-aligned.<sup>2</sup> |
| `>>`, `<<` | Wrapped  | The paragraph is centred.<sup>2</sup> |

<sup>1</sup> If the first word of the comment is `synopsis:`, the comment is indexed and treated as the
synopsis for the section of text where it occurs. These synopsis comments can be used to build an
outline and exported to external documents.

<sup>2</sup> The indent and alignment codes are available from version 1.4.

In additions:

* A variety of thin and non-breaking spaces are supported. Some of them depend on the system
  running at least Qt 5.9. Earlier versions of Qt will unfortunately strip them out when saving.
* Tabs can be used in the text, and should be properly aligned in both editor and viewer. This can
  be used to make simple tables and lists. Note that for HTML exports, most browsers will treat a
  tab as a space, so it may not show up like expected. Open Document exports should produce the
  expected result.

### Export Formats

The core export formats of novelWriter are Open Document and HTML5. Open Document is an open
standard for office type documents that is supported by most office applications. See
[Open Document > Application Support](https://en.wikipedia.org/wiki/OpenDocument#Application_support)
for more details.

You can also export the entire project as a single novelWriter-flavour document. These can later be
imported again into novelWriter. In addition, printing and export to PDF is offered through the Qt
library, although with limitations to formatting.

### Colour Themes

The editor has syntax highlighting for the features it supports, and includes a set of different
syntax highlighting themes. Optional GUI themes are also available, including dark themes.

### Easy Organising of Project Files

The structure of the project is shown on the left hand side of the main window. Project files are
organised into root folders, indicating what class of file they are. The most important root folder
is the `Novel` folder, which contains all of the files that make up the novel itself. Each root
folder can have subfolders. Subfolders have no impact on the final project structure, they are
there for you to organise your files in whatever way you want.

The editor supports four levels of headings, which determine what level the following text belongs
to. Headings of level one signify a book or partition title. Headings of level two signify the
start of a new chapter. Headings of level three signify the start of a new scene. Headings of level
four can be used internally in each scene to create separate sections.

Each novel file can be assigned a layout format, which shows up as a flag next to the item in the
project tree. These are mostly to help the user track what they contain, but they also have some
impact on the layout of the exported document. See the
[documentation](https://novelwriter.readthedocs.io) for further details.

### Project Notes

Supporting notes can be added for the story plot, characters, locations, story timeline, etc. These
have their separate root folders and are optional to use.

### Visualisation of Story Elements

The different notes can be assigned tags, which other files can refer back to using `@`-prefixed
meta keywords. This information can be used to display an outline of the story, showing where each
scene connects to the plot, and which characters, etc. occur in them. In addition, the tags
themselves are clickable in the document view pane, and control-clickable in the editor. They make
it possible to quickly navigate between the documents while writing.

## Standard Installation

For a regular installation, it is recommended that you download one of the minimal zip files from
the [Releases](https://github.com/vkbo/novelWriter/releases) page or the
[novelwriter.io](https://novelwriter.io/) website.
The [documentation](https://novelwriter.readthedocs.io/) has detailed install instructions for
[Linux](https://novelwriter.readthedocs.io/en/latest/setup_linux.html),
[Windows](https://novelwriter.readthedocs.io/en/latest/setup_windows.html), and
[macOS](https://novelwriter.readthedocs.io/en/latest/setup_mac.html).
They are pretty straightforward.

## Running from Source

If you want to run novelWriter directly from the source code, you must run the `novelWriter.py`
file from command line.

**Note:** You may need to replace `python` with `python3` and `pip` with `pip3` in the instructions
below on some systems. You may also want to add the `--user` flag for `pip` to install in your user
space only.

### Dependencies

Dependencies can generally be installed from PyPi with:
```bash
pip install -r requirements.txt
```

### Additional Steps for Linux

On Linux, you can most likely find the dependencies in your distribution's repository. On Ubuntu
and Debian, run:
```bash
sudo apt install python3-pyqt5 python3-lxml python3-enchant
```

If you want to set up a launcher and icons on Linux, you can run:
```bash
python setup.py xdg-install
```

### Additional Steps for macOS

First, make sure you have properly set up Python3 with Homebrew. If not, check their
[documentation](https://docs.brew.sh/Homebrew-and-Python).
In addition, the following steps are necessary to install all dependencies:
```bash
brew install enchant
pip3 install --user -r requirements.txt
pip3 install --user pyobjc
```

### Additional Steps for Windows

Windows does not by default come with Python installed. If you haven't installed it already, get it
from [python.org/downloads](https://www.python.org/downloads/). Remember to select "Add Python to
PATH" during the installation.

The script `windows_install.bat` in the `setup` folder can be used to create desktop and start menu
icons for novelWriter. The script will also install dependencies for you from PyPi.

### Internationalisation

If you install from source, you must build the translation files yourself if you want to switch to
a different GUI language than British English. This requires that you have the Qt translation
framework installed. Check the specific instruction in the README in the `i18n` source folder for
how to build the translation files.

## Debugging

If you need to debug novelWriter, you must run it from the command line. It takes a few parameters,
which can be listed with the switch `--help`. The `--info`, `--debug` or `--verbose` flags are
particularly useful for increasing logging output for debugging.

## Licenses

This is Open Source software, and novelWriter is licensed under GPLv3. See the
[GNU General Public License website](https://www.gnu.org/licenses/gpl-3.0.en.html) for more
details, or consult the [LICENSE](https://github.com/vkbo/novelWriter/blob/main/LICENSE.md) file.

Bundled assets and their licenses are listed in
[CREDITS](https://github.com/vkbo/novelWriter/blob/main/CREDITS.md).

## Screenshots

**novelWriter with default system theme:**
![Screenshot 1](https://raw.githubusercontent.com/vkbo/novelWriter/main/docs/source/images/screenshot_default.png)

**novelWriter with dark theme:**
![Screenshot 2](https://raw.githubusercontent.com/vkbo/novelWriter/main/docs/source/images/screenshot_dark.png)
