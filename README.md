# novelWriter

[![Linux](https://github.com/vkbo/novelWriter/actions/workflows/test_linux.yml/badge.svg?branch=main)](https://github.com/vkbo/novelWriter/actions/workflows/test_linux.yml)
[![Windows](https://github.com/vkbo/novelWriter/actions/workflows/test_win.yml/badge.svg?branch=main)](https://github.com/vkbo/novelWriter/actions/workflows/test_win.yml)
[![MacOS](https://github.com/vkbo/novelWriter/actions/workflows/test_mac.yml/badge.svg?branch=main)](https://github.com/vkbo/novelWriter/actions/workflows/test_mac.yml)
[![Flake8](https://github.com/vkbo/novelWriter/workflows/flake8/badge.svg)](https://github.com/vkbo/novelWriter/actions)
[![CodeCov](https://codecov.io/gh/vkbo/novelWriter/branch/main/graph/badge.svg)](https://codecov.io/gh/vkbo/novelWriter)

<img align="left" style="margin: 0 0 4px 0;" src="https://raw.githubusercontent.com/vkbo/novelWriter/main/setup/novelwriter_readme.png">

novelWriter is a plain text editor designed for writing novels assembled from many smaller text
documents. It uses a minimal formatting syntax inspired by Markdown, and adds a meta data syntax
for comments, synopsis, and cross-referencing. It's designed to be a simple text editor that allows
for easy organisation of text and notes, using human readable text files as storage for robustness.

The project storage is suitable for version control software, and also well suited for file
synchronisation tools. All text is saved as plain text files with a meta data header. The core
project structure is stored in a single project XML file. Other meta data is primarily saved as
JSON files.

For more details, and how to install and use novelWriter, please see the main website and
documentation.

**Project Links**

* Website: [novelwriter.io](https://novelwriter.io)
* Documentation: [docs.novelwriter.io](https://docs.novelwriter.io)
* Internationalisation: [crowdin.com/project/novelwriter](https://crowdin.com/project/novelwriter)
* PyPi Project: [pypi.org/project/novelWriter](https://pypi.org/project/novelWriter)
* Social Media: [fosstodon.org/@novelwriter](https://fosstodon.org/@novelwriter)

## Sponsors

<table style="border: none;">
<tr>
  <td><img align="left" style="height: 25px;" src="https://raw.githubusercontent.com/vkbo/novelWriter/main/setup/signpath_logo.png"></td>
  <td>Free code signing on Windows provided by <a href="https://about.signpath.io/">SignPath.io</a>, certificate by <a href="https://signpath.org/">SignPath Foundation</a>.</td>
</tr>
</table>

## Implementation

novelWriter is written with Python 3 (3.9+) using Qt5 and PyQt5 (5.15 only), and is released on
Linux, Windows and macOS. It can in principle run on any Operating System that also supports Qt,
PyQt and Python.

## Project Contributions

Please don't make feature pull requests without first having discussed them with the maintainer.
You can make a feature request in the issue tracker, or if the idea isn't fully formed, start a
discussion on the discussion page. Please also don't make pull requests to reformat or rewrite
existing code unless there is a very good reason for doing so.

Fixes and patches are welcome. Contributions related to packaging and installing novelWriter will
also be appreciated, but please make an issue or a discussion topic first. Before contributing any
code, please also read the full
[Contributing Guide](https://github.com/vkbo/novelWriter/blob/main/CONTRIBUTING.md).

Project credits are available in [CREDITS.md](https://github.com/vkbo/novelWriter/blob/main/CREDITS.md).

**Note:** As of April 2024 only pre-releases are made from the `main` branch. Full releases are
made from the `release` branch. So if you're submitting a fix to a current release, **including
changes to documentation**, they must be made to the `release` branch.

### Translations

New translations are always welcome. This project uses Crowdin to maintain translations, and you
can contribute translations at the [Crowdin project page](https://crowdin.com/project/novelwriter).
If you have any questions, feel free to post them to the
[Translations of novelWriter](https://github.com/vkbo/novelWriter/issues/93) issue thread.

For more details, and how to use Qt Linguist for translations, see the
[i18n instructions](https://github.com/vkbo/novelWriter/blob/main/i18n/README.md).

## Licence

This is Open Source software, and novelWriter is licenced under GPLv3. See the
[GNU General Public License website](https://www.gnu.org/licenses/gpl-3.0.en.html) for more
details, or consult the [License](https://github.com/vkbo/novelWriter/blob/main/LICENSE.md)
document. Bundled assets and their licences are listed in the
[Credits](https://github.com/vkbo/novelWriter/blob/main/CREDITS.md) document.
