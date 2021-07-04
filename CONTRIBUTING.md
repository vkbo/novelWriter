# Contributing Guide

When contributing to this repository, please first discuss the change you wish to make via the
issue tracker or the discussions page with the owner of this repository before making a change. If
you just want to make a minor correction, like fix a typo or similar, feel free to just make a pull
request directly.

## Branching Structure

There are three protected branches on this repository. They are used in the following way:

* `main` – This is the Stable branch. It is used for releases and subsequent patches. No
  development code should be merged into this branch starting from version 1.0.
* `dev` – This is the Unstable (development) branch. It is where new features are merged, and where
  pre-releases are taken from.
* `testing` – This is the Testing branch. It is populated from the `dev` branch for pre-releases
  that need a longer testing phase.

Stable releases and patches will be tagged in the `main` branch, pre-releases may be tagged from
either `testing` or `dev` branch.

### What Branch to Use for Contributions

* If your contribution is a fix for the latest stable release, branch from the `main` branch.
* If your contribution is a new feature, branch from the `dev` branch.
* The `testing` branch is used infrequently. It is only used for pre-releases when new code is
  being developed that is not a part of the current testing release.

The current status of each branch is described in a pinned issue titled
"[Development Flow & Status](https://github.com/vkbo/novelWriter/issues/707)".

Please do not make your changes on a branch with the same name as any of the above mentioned
branches. You should make a unique and descriptive branch name in your fork for your changes.

## Pull Request Process

1. Make sure your code passes all tests and conforms to the style guide. You can check that the
   code conforms by running `flake8` from the root of the project folder.
2. Please provide a complete description of the changes in the pull request, and a summary that can
   be copied into the [CHANGELOG](CHANGELOG.md). Remember to reference any issue related by
   providing the issue number.
3. Do not change the version number. Version numbers are bumped in separate release pull requests
   by the maintainer.

## Code of Conduct

There is a code of conduct. Please follow it in all your interactions with the project.

### Our Pledge

In the interest of fostering an open and welcoming environment, we as contributors and maintainers
pledge to making participation in our project and our community a harassment-free experience for
everyone, regardless of age, body size, disability, ethnicity, gender identity and expression,
level of experience, nationality, personal appearance, race, religion, or sexual identity and
orientation.

Please see the [CODE_OF_CONDUCT](CODE_OF_CONDUCT.md) file for the full text.

## Code Style Guide

The source code of novelWriter broadly follows the [PEP8](https://www.python.org/dev/peps/pep-0008)
style guide, but with a few modifications and exceptions listed below.

### Line Length

For this project, source lines should stay within the 79 and 99 character limits described by PEP8.
79 characters is often too restrictive, so 99 character lines are acceptable when that is more
practical. Readability has priority. Generally, if a code statement requires multiple lines, the
lines should wrap at 79 characters, not 99. If wrapping can be avoided by going to 99, then that is
generally preferrable.

For text files, the text should also be wrapped at 99 character. The exception is markdown image
tags and urls.

Please do not submit pull requests that re-wrap existing source or text unless this has been
discussed beforehand.

### Linting with `flake8`

An excellent tool for checking Python code for errors and coding style is `flake8`. The
documentation is available [here](https://flake8.pycqa.org/en/latest/).

The `setup.cfg` file in the root of this project has the following settings for `flake8` that
matches the coding standard:
```conf
[flake8]
ignore = E203,E221,E226,E228,E241,E251
max-line-length = 99
exclude = docs/*
```

The command line equivalent, with reporting, is:
```bash
flake8 . --count --ignore E203,E221,E226,E228,E241,E251 --max-line-length=99 --show-source --statistics
```

Passing this check is required before contributions are merged into the `main`, `testing` or `dev`
branches. This is checked automatically when you make a pull request. You can run the `flake8`
command locally to check beforehand. The full command will give you a detailed description of the
code lines that do not conform to the standard.

## Ignored Errors

Some `flake8` error codes are ignored for this project for various reasons. The source also uses
camelCase function and variable names. This is the standard for the Qt libraries novelWriter
integrates with. It also happens to be the author's personal preferences. (Yay!)

The reason behind the other ignored error codes are listed below. Two of them are due to PEP8 not
permitting column alignment as opposed to many other coding styles, like for instance for Go. I
find them useful in regions of bulk value assignments. There's a reason why tables are more
readable than lists. They should be used sparingly though.

The ignored errors are all `pycodestyle` errors, and they are documented
[here](https://pycodestyle.pycqa.org/en/latest/intro.html#error-codes).

**E221:** multiple spaces before operator  
**Reason:** Column alignment.

**E226:** missing whitespace around arithmetic operator  
**Reason:** This doesn't actually follow the
[PEP8 recommendation](https://www.python.org/dev/peps/pep-0008/#other-recommendations)
of grouping longer equations by operator precedence like `2*a + 3*b` instead of `a * a + 3 * b`.
Generally, don't use spaces around `*`, `/` and `**`, but _do_ use spaces around `+` and `-`.
For appending strings, the spaces can be dropped. Don't use the `+` operator for appending multiple
strings. Use formatting instead.

**E228** missing whitespace around modulo operator  
**Reason:** See reason for E226. Formatting `%` like `/` and `*` should be possible.

**E241:** multiple spaces after ‘,’  
**Reason:** Column alignment.
