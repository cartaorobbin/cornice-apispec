# Knowledge Directory

The `knowledge/` directory contains AI-facing living documentation — one markdown file per feature area describing its current state, design decisions, API surface, and gotchas.

## Two Audiences

- **`docs/` and `README.md`** are for humans — developers, users, contributors. Focus on clarity, examples, and getting-started guidance.
- **`knowledge/`** is for the AI — the agent reads these files to understand the codebase. Focus on precision, design decisions, API surface, gotchas, and non-obvious learnings. Conciseness matters more than prose quality.
- Both must stay in sync. When a feature changes, update both.

## Structure

One markdown file per feature area (e.g., `knowledge/auth.md`, `knowledge/billing.md`, `knowledge/architecture.md`). Each file follows a consistent structure:

1. **Overview** — What this area does, in one or two sentences.
2. **Design Decisions** — The current choice, in a short statement, plus a link to the Accepted ADR. Full context, alternatives, and consequences live only in the ADR.
3. **API Surface** — Key classes, functions, types, and their relationships.
4. **Key Learnings / Gotchas** — Non-obvious behaviors, edge cases, things that broke before.

**Exception:** `knowledge/ganesha.md` is a Ganesha classification file, not a feature doc. It must stay Type-only (`# Ganesha` + `## Type` is `project`, `library`, or `infra`). Do not expand it to this structure. Do not treat it as stale for missing Overview / Design Decisions / API Surface.

## Architectural Decision Records

A decision that chooses a direction is one file: `knowledge/adr/NNNN-short-title.md`. The number is 4 digits. The next number is one higher than the current max. The filename never changes.

Required sections, in order: **Status**, **Date**, **Context**, **Decision**, **Consequences**, **Alternatives considered**.

Status is one of:

- `Accepted` — this is the current decision.
- `Superseded by ADR-MMMM` — a newer ADR replaces this one. The new file is the current decision.
- `Deprecated` — the decision is no longer in force and nothing replaces it (feature removed, approach abandoned), plus one sentence on why it stopped.

Never delete an ADR. Agents read `knowledge/`, not removed files. The only edit allowed on an old ADR is the Status section. Context, Decision, Consequences, and Alternatives stay as written.

`knowledge/architecture.md` is the index. It lists every file in `knowledge/adr/`, grouped by status, one line each (number, title, link, and for a retired row the superseding ADR or the deprecation reason). A new, superseded, or deprecated ADR updates that index in the same change. Accepted entries are the current set. A feature file links only Accepted ADRs.

## When to Update

- After completing a new feature — create or extend the relevant file.
- After fixing a significant bug that revealed something non-obvious — add to Key Learnings.
- After making an architectural change — update the affected files.
- After an architectural decision — add `knowledge/adr/NNNN-short-title.md`, link it from the feature file's Design Decisions, and update the index in `knowledge/architecture.md`.

## What Does NOT Belong

- Task lists, progress tracking, or backlog items. If the project has a `planning/` directory, leave it alone — do not copy current tasks into `knowledge/`.
- Changelogs or timestamps — feature files describe the present, not the history. Dates and superseded history belong in `knowledge/adr/` only.
- Documentation for end users — that lives in `docs/`.

## Reading Before Writing

Before making changes to a feature area, read the relevant `knowledge/*.md` file first. It contains context that may affect your approach.
