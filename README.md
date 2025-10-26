# novelWriter

[![Linux](https://github.com/vkbo/novelWriter/actions/workflows/test_linux.yml/badge.svg)](https://github.com/vkbo/novelWriter/actions/workflows/test_linux.yml)
[![Windows](https://github.com/vkbo/novelWriter/actions/workflows/test_win.yml/badge.svg)](https://github.com/vkbo/novelWriter/actions/workflows/test_win.yml)
[![MacOS](https://github.com/vkbo/novelWriter/actions/workflows/test_mac.yml/badge.svg)](https://github.com/vkbo/novelWriter/actions/workflows/test_mac.yml)
[![Linting](https://github.com/vkbo/novelWriter/actions/workflows/syntax.yml/badge.svg)](https://github.com/vkbo/novelWriter/actions/workflows/syntax.yml)
[![CodeCov](https://codecov.io/gh/vkbo/novelWriter/branch/main/graph/badge.svg)](https://codecov.io/gh/vkbo/novelWriter)

<img align="left" style="margin: 0 0 4px 0;" src="https://raw.githubusercontent.com/vkbo/novelWriter/main/setup/novelwriter_readme.png">

novelWriter is a plain text editor designed for writing novels assembled from many smaller text
documents. It uses a minimal formatting syntax inspired by Markdown, and adds a meta data syntax
for comments, synopsis, and cross-referencing. It's designed to be a simple text editor that allows
for easy organisation of text and notes, using human readable text files as storage for robustness.
The project format is well suited both for version control software and file synchronisation tools.

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

novelWriter is written in Python and uses Qt6 with PyQt6 Python binding as the UI framework. It is
released on Linux, Windows and MacOS. It can in principle run on any Operating System that also
supports Qt, PyQt and Python.

<p align="center">
  <img width="80%" src="https://raw.githubusercontent.com/vkbo/novelWriter/main/setup/screenshot.png">
</p>


## Project Contributions

Please don't make feature pull requests without first having discussed them with the maintainer.
You can make a feature request in the [issues tracker](https://github.com/vkbo/novelWriter/issues),
or if the idea isn't fully formed, start a [discussion](https://github.com/vkbo/novelWriter/discussions).
Please also don't make pull requests to reformat or rewrite existing code unless there is a very
good reason for doing so. Please do not submit AI generated content.

Fixes and patches are welcome. Contributions related to packaging and installing novelWriter will
also be appreciated, but please make an issue or a discussion topic first. Before contributing any
code, please also read the full
[Contributing Guide](https://github.com/vkbo/novelWriter/blob/main/CONTRIBUTING.md).

Project credits are available in [CREDITS.md](https://github.com/vkbo/novelWriter/blob/main/CREDITS.md).

**Note:** New features and pre-releases are made on the `main` branch. Full releases are made from
the `release` branch. So if you're submitting a fix to a current release, **including changes to
documentation**, they must be made to the `release` branch.


### Translations

New translations are always welcome. This project uses Crowdin to maintain translations, and you
can contribute translations at the [Crowdin project page](https://crowdin.com/project/novelwriter).
If you have any questions, feel free to post them to the
[Translations of novelWriter](https://github.com/vkbo/novelWriter/issues/93) issue thread.


## Licence

This is Open Source software, and novelWriter is licenced under GPLv3. See the
[GNU General Public License website](https://www.gnu.org/licenses/gpl-3.0.en.html) for more
details, or consult the [License](https://github.com/vkbo/novelWriter/blob/main/LICENSE.md)
document. Bundled assets and their licences are listed in the
[Credits](https://github.com/vkbo/novelWriter/blob/main/CREDITS.md) document.
