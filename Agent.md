About

--- contains project info

(Add general project information, architecture overview, and goals here)

Important

Frontend / Backend Sync

Whenever a new field is added to a backend model or database entity that is surfaced in the frontend (e.g. settings panels), it must also be handled in the corresponding frontend component so the two stay in sync. This is a convention/reminder only — there is no automatic syncing mechanism; the frontend enumerates fields explicitly.

planning/Spec-ing

Use Tracer bullets comes from the Pragmatic Programmer. When building systems, you want to write code that gets you feedback as quickly as possible. Tracer bullets are small slices of functionality that go through all layers of the system, allowing you to test and validate your approach early. This helps in identifying potential issues and ensures that the overall architecture is sound before investing significant time in development.

Implementation Guidelines

Commit the spec before the development commits

Use comments only when necessary to explain "why?" not "how?", how must be clear from the code itself

Development Details

Guidelines for writing good code for a developer

Choose clean code over clever code.

Write object oriented code as much as possible.

Keep function sizes small, ideally 10 lines.

Try and keep files between 100 and 300 lines.

Don't keep too many files in a folder or module. Try and keep it under 15.

Avoid abbreviations.

Use standard API as much as possible.

Reuse. Write as little code as possible.

Use the project's standard design system and established components for UI styling.

Always write tests, and make sure they work.

Build the minimum working app, then iterate towards your goals.

Keep the verbosity less in new changes (inline comments, docstrings erc). Explain only what's absolutely needed in inline comments. Actual changes explanation can be part of commit message.

Regression tests

When we fix a bug, add at the very least a Unit test, and verify before/after by temp revert of fix to make sure the test tests what is intended

For bigger features/workflows, e2e playwright tests are a must.

Another Details

(Add any additional environment setups, deployment scripts, or miscellaneous rules here)

Commit or PR Style

Pull Requests

The canonical repo is <organization>/<repository> (git remote upstream). fork (origin) entirely.

Branch off upstream/develop (run git fetch upstream develop first), not local/fork develop - the fork's develop is often stale and inflates the diff.

Push the feature branch to upstream (<organization>/<repository>) and raise the PR there: gh pr create --repo <organization>/<repository> --base develop .... Set gh repo set-default <organization>/<repository> so this is the default.

Before raising, sanity-check the diff is only your files: git diff --stat upstream/develop..<branch>. A huge diff means you based on or targeted the wrong (fork) develop - fix the base before opening the PR.

Raise PR always against the develop branch

Keep pull request descriptions stupid simple

Some formats:

h2 Problem (1-2 sentences), h2 Solution: good for bugs, etc.

h2 Why? h2 What? h2 How?: good for new features and enhancements