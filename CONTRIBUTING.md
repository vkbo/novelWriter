# Contributing

When contributing to this repository, please first discuss the change you wish to make via the
issue tracker with the owner of this repository before making a change. If you just want to make a
minor correction, like fix a typo or similar, feel free to just make a pull request directly.

There is a code of conduct. Please follow it in all your interactions with the project.

## Pull Request Process

1. Make sure your code passes all tests and conforms to the style guide. You can check that the code
   conforms by running `flake8` from the root of the project folder.
2. Please provide a complete description of the changes in the pull request, and a summary that can
   be copied into the [CHANGELOG](CHANGELOG.md). Remember to reference any issue related by
   providing the issue number.
3. Do not change the version number unless asked to do so. Version numbers are bumped in separate
   release pull requests by the maintainer.

## Code of Conduct

### Our Pledge

In the interest of fostering an open and welcoming environment, we as contributors and maintainers
pledge to making participation in our project and our community a harassment-free experience for
everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level
of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

Please see the [CODE_OF_CONDUCT](CODE_OF_CONDUCT.md) file for the full text.

## Code Style Guide

The source code of novelWriter broadly follows the [PEP8](https://www.python.org/dev/peps/pep-0008/)
style guide , but with a few modifications and exceptions.

### Linting with flake8

An excellent tool for checking Python code for errors and coding style is `flake8`.
The documentation is available [here](https://flake8.pycqa.org/en/latest/).

The `setup.cfg` file in the root of this project has the following settings:
```conf
[flake8]
ignore = E203,E221,E226,E241,E251,E261,E266,E302,E305
max-line-length = 99
exclude = docs/*
```

The command line equivalent, with reporting, is:
```bash
flake8 . --count --ignore E203,E221,E226,E241,E251,E261,E266,E302,E305 --max-line-length=99 --show-source --statistics
```

Passing this check is required before contributions are merged into the `main` branch. This is
checked automatically when you make a pull request. You can run the `flake8` command locally to
check beforehand. The full command will give you a detailed description of the code lines that do
not conform to the standard.

## Ignored Errors

Some errors are ignored in novelWriter, for various reasons. In addition, novelWriter uses camelCase
function and variable names due to this being the standard for the Qt libraries, and also because of
the author's personal preferences.

The reason behind the other ignored error codes are listed below. Many of them are due to PEP8 not
permitting column alignment as opposed to many other coding styles. I find them useful in regions of
bulk value assignments. There's a reason why tables are more readable than lists. They should be
used sparingly though.

The ignored errors are all `pycodestyle` errors, and they are documented
[here](https://pycodestyle.pycqa.org/en/latest/intro.html#error-codes).

**E203:** whitespace before ‘:’  
**Reason:** Column alignment. It is natural to align dictionary columns along the `:` character.

**E221:** multiple spaces before operator  
**Reason:** Column alignment.

**E226:** missing whitespace around arithmetic operator  
**Reason:** This doesn't actually follow the PEP8 recommendation of grouping longer equations by
operator precedence like `2*a + 3*b` instead of `a * a + 3 * b`. Generally, don't use spaces around
`*`, `/` and `**`, but do use spaces around `+` and `-`. For appending strings, the spaces can be
dropped. Don't use the `+` operator for appending multiple strings. Use formatting instead.

**E241:** multiple spaces after ‘,’  
**Reason:** Column alignment.

**E251:** unexpected spaces around keyword / parameter equals  
**Reason:** Column alignment.

**E261:** at least two spaces before inline comment  
**Reason:** With syntax highlighting, this one doesn't make much sense.

**E266:** too many leading ‘#’ for block comment  
**Reason:** In the source multiple `#`s is sometimes used to indicate importance or heading level,
like markdown headers.

**E302:** expected 2 blank lines, found 0  
**Reason:** Applies to classes. Instead, end classes with a comment like `# END Class ClassName` to
make it easier to see which class just ended. The double line break is then redundant.

**E305:** expected 2 blank lines after end of function or class  
**Reason:** Instead, _always_ end a function with a `return`, preferably indented at function
level. The end of the function is then clear.
