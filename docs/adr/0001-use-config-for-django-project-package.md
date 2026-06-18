# ADR 0001: Use `config` For The Django Project Package

## Status

Accepted

## Context

School Utilities is intended to contain multiple school-related tools over time. The first tool is Auto Grader.

The initial Django project package was named `auto_grader`, which also describes the first domain tool. If the package keeps that name, it becomes harder to later create a dedicated `auto_grader` Django app for the actual Auto Grader domain behavior.

## Decision

Rename the Django project/configuration package from `auto_grader` to `config`.

The `config` package owns project-level Django configuration:

- settings
- root URLs
- WSGI entry point

The name `auto_grader` is reserved for a future domain app if the current `core` app is split into bounded apps.

## Consequences

- Project-level imports now use `config.settings`, `config.urls`, and `config.wsgi`.
- The database name remains `auto_grader`; this is an infrastructure name and does not need to change with the Python package.
- Future refactoring can move Auto Grader-specific models, forms, views, and templates out of `core` into a dedicated app without a naming conflict.
