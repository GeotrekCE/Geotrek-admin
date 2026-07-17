# AGENTS.md

Guidance for coding agents working in this repository.

## Project summary

- Geotrek-admin is a Django/PostGIS application for managing trekking and tourism data.
- Main backend code is in `/geotrek`, with API, domain apps, and settings under `/geotrek/settings`.
- Tooling and common commands are defined in `/Makefile`.

## Working rules

- Make focused, minimal changes for the requested task.
- Do not modify unrelated files.
- Keep existing project conventions and architecture.
- Update documentation when behavior or usage changes.

## Setup notes

- Standard development uses Docker Compose with the `web` service.
- If `.env` is missing, create it from `.env.dist` before running `make` targets:
  - `cp .env.dist .env`

## Validation commands

Run relevant checks before finalizing:

- `make quality` (runs lint + format via ruff in Docker)
- `make test` (Django tests in Docker)

For documentation-only changes, skip tests unless docs behavior or tooling is affected.

## Contribution conventions

- Follow contribution docs in:
  - `/docs/contribute/contributing.rst`
  - `/docs/contribute/guidelines.rst`
- Keep pull requests small and explicit.
- Use clear commit messages and reference related issues when applicable.

## Safety and quality

- Never commit secrets, credentials, or private keys.
- Prefer existing dependencies and patterns over introducing new ones.
- Preserve backward compatibility unless the task explicitly requires a breaking change.
