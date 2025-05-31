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
* Improvements to the documentation. Particularly if the documentation is unclear. Please don't
  make any larger changes to the documentation without discussing them with the maintainer first.
* Adaptations, installation or packaging features targeting specific operating systems.

**Please do not:**

* Make a pull request that restructures or reformats existing code. If you think some part of the
  code could be improved, please make an issue thread or start a discussion. The same applies to
  any text document in the repository.

## Picking the Correct Branch for a Pull Request

Pre-releases are made from the `main` branch, and full releases are made from the `release` branch.
If you are submitting a fix to a current release you must do so from the `release` branch. If you
make such a fix on the `main` branch, **it cannot be included in a patch release**. This also
applies to the documentation for the latest release published on the main website.

New features are only accepted on full releases, so a feature pull request must be made to the
`main` branch. However, if the `main` branch is very close to a new full release, pull requests may
not be merged until the release is completed.

## Pull Request Check List

Make sure the pull request follows these rules:

* The `main` branch is the default branch. For general changes, please make a new branch in your
  own fork from the current `main` branch. Do not make pull requests from your copy of the `main`
  branch.
* Please provide a description of the changes in the pull request under the summary section of the
  pull request template, and reference any related issues by providing the issue number.
* Do not change the version number.
* Do not submit files that were not actively changed but have otherwise been modified. This is
  mostly an issue with translation files. The language tool may update all files in the `i18n`
  folder.

## General Rules

These are the guidelines for the project. The source code of novelWriter broadly follows the
[PEP8](https://www.python.org/dev/peps/pep-0008) style guide, but with a few exceptions.

### Tests

* New code must not break any existing tests.
* New code must come with tests that cover the code in full. If the code has branches that only
  runs on some OSes, they must be covered when test are run on that OS. The test suite runs on
  Linux, Windows and MacOS.

### Code Formatting

* Do not run automatic formatting tools like `black` or `ruff` on the code. Auto-formatting using
  `ruff` is planned, but there are a couple of features missing in it, so it is currently only used
  for linting. Auto-formatting with `isort` is configured in `pyproject.toml` and can be used.
* The pull request code *must* pass the `ruff` linting rules specified in `pyproject.toml`.
* In general, do not make large scale formatting changes to the code.

### Type Annotations

* All functions and parameters must be type annotated, and so must variables and attributes if the
  type cannot be inferred from the initial value. Typing rules are set in `pyproject.toml` and a
  pull request must pass `pyright` with these settings.
* Do not use the `Any` type when an actual type exists. `Any` is allowed for functions that
  actually handles any kind of input and returns a standard type.
* Do not use deprecated capitalised annotations like `Dict`, `List`, `Tuple`, etc.
* Type annotated code must be runnable on all supported Python versions.

### Internationalisation

* All comments and docstrings in the code must be in English.
* All text presented to the user must be wrapped in calls to Qt's translation framework, and the
  spelling of this text *must* be UK English. US English spelling is not allowed for these strings.
* Commit descriptions and pull requests must also be in English.

### Line Length

* Source code lines can extend to the upper limit of 99 characters. Generally, if a code statement
  requires multiple lines, the lines should wrap at 79 characters if possible. If wrapping can be
  avoided by going to 99, then that is generally preferable. Readability has priority.
* For text files, the text should be wrapped at 99 character. The exception is Markdown image tags
  and URLs which can run past that limit.

### Spaces, Indentation and Alignment

* Only indentation by multiples of 4 spaces is allowed.
* No trailing spaces should occur on any line in the source code, including empty lines.
* Common line wrapping methods are allowed in the code except `\`, but avoid deep indentations.
* Aligning operators and attributes in columns with multiple spaces is not allowed by PEP8. The
  rule is relaxed a bit here. Alignment is allowed when populating large dictionaries or setting
  many class attributes. It does improve readability in such cases, but should not be overused.

### General Code Rules

* Use f-string style for string formatting as the first choice, and `.format` functions if there is
  a good reason for it. Do not use `%` style formatting except for logging output. For logging, `%`
  must be used (it's a limitation in the logging library unfortunately).
* Functions should be on camelCase form for consistency with the Qt library code.
