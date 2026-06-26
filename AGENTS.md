# novelWriter Agent Instructions

## AI Policy

- This repository does not allow large AI-generated contributions. Such PRs will be rejected.
- Code can be written with AI assistance, but must be concise, performant, and of a comparable
  quality to existing code.

## Scope

- This repository is `novelWriter`, a Python application using PyQt6.
- Prefer small, targeted changes that match existing patterns in `novelwriter/`.
- The root import path for all application code is `novelwriter`.

## Working Rules

- Follow the existing code style in nearby files; avoid broad refactors.
- Preserve current behavior unless the task explicitly asks for a change.
- When editing code, keep diffs minimal and update only the relevant files.
- Prefer project-local helpers and conventions over introducing new abstractions.
- The code base should use camelCase style to match the Qt library style.
- For Qt enums and related Qt type constants, prefer aliases imported from `novelwriter/types.py`
  instead of direct enum members from PyQt6 modules where aliases are already available.
- When connecting Qt signals and passing parameters, prefer `qtLambda` from `novelwriter/common.py`
  over inline lambdas where it fits existing project patterns.
- The `i18n/*.ts` files are auto-generated and must never be edited manually.
- Do not edit files under `sample/` unless explicitly requested.
- Do not edit files under `tests/lipsum/` unless explicitly requested.
- Any folder containing `nwProject.nwx` is a novelWriter project storage folder and must not be
  edited unless explicitly requested.

## Codebase Navigation

- The application code lives under `novelwriter/`. Everything else is supporting code and build
  scripts that are not published.
- `novelwriter/core/` contains code that manages the application user's writing project.
- `novelwriter/dialogs/` contains GUI dialog classes with a smaller scope than full GUI tools.
- `novelwriter/extensions/` contains GUI classes that modify or extend standard Qt6 classes.
- `novelwriter/formats/` contains classes used for generating exports for the user's projects.
- `novelwriter/gui/` contains GUI classes for the main GUI components.
- `novelwriter/text/` contains various text processing utilities.
- `novelwriter/tools/` contains larger GUI components that process data.
- `novelwriter/` root contains shared codes, constants, variables and utility functions.
- Build getter key strings used with `BuildSettings` are defined in `novelwriter/core/buildsettings.py`.
- For formats changes, check adjacent format implementations before modifying shared logic.
- All formats classes are write only, and do not need to read the same file formats.

## Validation

- When making code changes, run `uv run ruff format`.
- When making code changes, run `uv run ruff check` and address relevant issues in touched files.
- When making code changes, run `uv run pyright` and address relevant issues in touched files.
- Run the most relevant tests for the changed area when available.
- If tests are missing for the touched path, add focused tests alongside the change when practical.
- Do not fix unrelated failures unless they block the requested task.
- When running tests, set `QT_QPA_PLATFORM=offscreen` to disable the Qt GUI. Use `./run_tests.py -o`
  or `QT_QPA_PLATFORM=offscreen python -m pytest`.

## Documentation

- Link to existing docs instead of duplicating them.
- Keep agent guidance concise and specific to repository conventions.
- All titles should be in title case.
- All text should be written with British English spelling.
