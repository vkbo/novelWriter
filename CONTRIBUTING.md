# Contributing Guide

See also [CODE_OF_CONDUCT](CODE_OF_CONDUCT.md).

When contributing to this repository, please first discuss the change you wish to make with the
owner. Either via the issue tracker or on the discussions page. Especially if it is regarding new
features. If you just want to make a minor correction, like fix a typo or similar, feel free to
just make a pull request directly.

**The following contributions are welcome:**

* Bugfixes for new or existing bugs. Please also report new bugs in the issue tracker even if you
  also provide a fix. It makes it easier to keep track of what has been fixed and when.
* Translations made via the [Crowdin project page](https://crowdin.com/project/novelwriter).
* Translations of the documentation. These need to use Sphinx i18n tooling. Please start a
  discussion before beginning such work as it requires some coordination.
* Improvements to the documentation. Particularly if the documentation is unclear. Please don't
  make any larger changes to the documentation without discussing them with the maintainer first.
* Adaptations, installation or packaging features targeting specific operating systems.
* Using AI as a coding assistant is fine as long as the code is of good quality and the scope of
  change is small.

**Please do not:**

* Make a pull request that restructures or reformats existing code. If you think some part of the
  code could be improved, please make an issue thread or start a discussion. The same applies to
  any text document in the repository.
* Make pull requests with AI generated code. This is not a project suitable for vibe coding.
  Outright slop will result in the account being blocked.


## Running from Source

This project uses [uv](https://docs.astral.sh/uv/) to maintain dependencies. In order to run
novelWriter directly from checked out source, simply call from the root folder with:

```bash
uv run novelwriter
```

To set up a development environment with all needed dependencies, run:

```bash
uv sync
```

Many tasks, like building assets from source, are handled by the `pkgutils.py` helper tool.
This tool requires no dependencies, so you can either run it directly with Python, or `uv run`.

```bash
python pkgutils.py --help
```

The translation files needed at runtime can be built with:

```bash
python pkgutils.py qtlrelease
```

Material design icons are included with the source. Optional icon themes can be built with:

```bash
python pkgutils.py icons optional
```


### Running Tests

* New code must not break any existing tests.
* New code must come with tests that cover the code in full. This includes branch coverage. If the
  code has branches that only runs on some OSes, they only need to be covered when test are run on
  that OS. The test suite runs on Linux, Windows and MacOS.
* It is ok to use `pragma` comments with `no cover` and `no branch` if the code is not expected to
  touch those areas or branches.

A helper script is provided for running tests. It simplifies coverage reporting and a few other
things. Run the following to see all details:

```bash
uv run run_tests.py --help
```


## Picking the Correct Branch for a Pull Request

Pre-releases are made from the `main` branch, and full releases are made from the `release` branch.
If you are submitting a fix to a current release you must do so from the `release` branch. If you
make such a fix on the `main` branch, **it cannot be included in a patch release**. This also
applies to the documentation for the latest release published on the main website.

New features are only added in full releases, so a feature pull request must be made to the `main`
branch. However, if the `main` branch is very close to a new full release, pull requests may not be
merged until the release is completed.

This project uses GitHub milestones to plan releases, and only pull requests included in the
current release cycle will be merged to `main`. Milestone tickets are not set in stone and are
often moved to other milestones.


### Pull Request Check List

Make sure the pull request follows these rules:

* The `main` branch is the default branch. For general changes, please make a new branch in your
  own fork from the current `main` branch. Do not make pull requests from your copy of the `main`
  branch. The same applies to the `release` branch.
* Please provide a description of the changes in the pull request under the summary section of the
  pull request template, and reference any related issues by providing the issue number. Do not
  post links to issue numbers as that breaks the integration. Stating the issue number is enough.
* Do not change the version number.
* Make sure the formatting and linting tools have been run before the pull request is made.


## Code Style

This code base uses camelCase convention for function and variable names. This differs from the
common convention of snake_case in Python. The reason for this is that novelWriter is built on the
Qt framework, where everything is camelCase.

Pretty much everything else regarding formatting is handled by the linter and formatter. This
project uses [ruff](https://docs.astral.sh/ruff/) for linting and formatting and
[pyright](https://github.com/microsoft/pyright) for type checking. The settings for these tools
are defined in ``pyproject.toml`, and any submitted code must pass the following three commands:

```bash
uv run ruff check
uv run ruff format
uv run pyright
```

### Line Length

* The line length of the source code is enforced by the formatter, and is set to 120 characters.
  Docstrings should be wrapped manually at 79 characters for better readability.
* For text files, the text should be wrapped 120 character. The exception is Markdown image tags
  and URLs which can run past that limit.


### Internationalisation

* All comments and docstrings in the code must be in English.
* All text presented to the user must be wrapped in calls to Qt's translation framework, and the
  spelling of this text *must* be British English. US English spelling *is not allowed* for these
  strings.
* Commit descriptions and pull requests must also be in English.
