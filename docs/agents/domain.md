# Domain Docs

How the engineering skills should consume this repo's domain documentation when exploring the codebase.

## Layout

This is a single-context repo.

The expected domain documentation locations are:

- `CONTEXT.md` at the repo root
- `docs/adr/` for architectural decision records

## Before Exploring

Before doing domain-sensitive work, read:

- `CONTEXT.md`, if it exists
- Relevant ADRs under `docs/adr/`, if they exist

If these files do not exist yet, proceed silently. Do not block work just because the domain docs have not been created yet.

## Vocabulary

When output names a domain concept, use the term as defined in `CONTEXT.md`.

If the needed concept is not in the glossary yet, note the gap when relevant instead of inventing competing terms.

## ADR Conflicts

If a proposal or implementation contradicts an existing ADR, surface the conflict explicitly instead of silently overriding it.
