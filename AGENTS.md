# novelWriter Agent Instructions

## AI Policy

- This repository does not allow large AI-generated contributions. Such PRs will be rejected.
- Code can be written with AI assistance, but it must stay concise, performant, and match the existing code quality

## Scope

- This repository is `novelWriter`, a Python application using PyQt6
- The root import path for application code is `novelwriter`

## Working Rules

- Use camelCase naming to match Qt-style conventions
- Single-sentence inline comments should not end with punctuation
- For Qt enums and related Qt constants, prefer aliases from `novelwriter/types.py` when available
- When connecting Qt signals and passing parameters, prefer `qtLambda` from `novelwriter/common.py` over inline lambdas where it fits the existing pattern
- The `i18n/*.ts` files are auto-generated and must never be edited manually
- Do not edit files under `sample/` and `tests/_lipsum/` unless explicitly requested
- Treat unstaged changes under `sample/` and `tests/_lipsum/` as expected test/runtime churn (timestamps, counters, hashes) and ignore them completely during reviews, status checks, and commit preparation unless explicitly requested
- Any folder containing `nwProject.nwx` is a novelWriter project storage folder and must not be edited unless explicitly requested

## Codebase Navigation

- Application code lives under `novelwriter/`; everything else is supporting code and build scripts
- Build getter key strings used with `BuildSettings` are defined in `novelwriter/manuscript/buildsettings.py`
- For format changes, check adjacent implementations before modifying shared logic; format classes are write-only and do not need to read the same file formats

## Validation

- Run `uv run ruff format`, `uv run ruff check`, and `uv run pyright` on touched files when making code changes
- Run the most relevant tests for the changed area when available
- If tests are missing for the touched path, add focused tests alongside the change when practical
- Always run tests with `QT_QPA_PLATFORM=offscreen` in this repository
- If a test tool does not allow setting environment variables, run tests in terminal as `QT_QPA_PLATFORM=offscreen uv run pytest ...`
- Never run GUI tests in this repository without the offscreen environment variable
- Avoid adding test-specific code to the main code base
- `CONFIG` is fully reset before every test by the autouse `functionFixture` fixture in `tests/conftest.py`; never save/restore `CONFIG.*` values in a test, just set them directly
- Both line and branch test coverage should be complete and at 100%

## Documentation

- Link to existing docs instead of duplicating them
- Keep agent guidance concise and specific to repository conventions
- Use title case for headings and British English spelling throughout
