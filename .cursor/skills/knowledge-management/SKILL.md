---
name: knowledge-management
description: Create or update knowledge files for a feature area. Use when the user says "update knowledge", "create knowledge file for X", "document this feature", or after completing a feature that needs knowledge documentation.
---

# Knowledge Management

This skill guides you through creating or updating files in the `knowledge/` directory. Follow the conventions defined in `.cursor/rules/knowledge.mdc` and `.claude/rules/knowledge.md`.

## Step 1: Determine the Action

Use AskQuestion:

```
prompt: "What would you like to do?"
options:
  - Create a new knowledge file for a feature area
  - Update an existing knowledge file
  - Record an architectural decision
  - Review all knowledge files for staleness
```

---

## Creating a New Knowledge File

### Step 2a: Identify the Feature Area

Ask the user which feature area to document, or infer it from the conversation context. The file should be named after the feature area in lowercase with underscores (e.g., `knowledge/billing.md`, `knowledge/auth.md`).

### Step 3a: Explore the Codebase

Read the source code for the feature area thoroughly:
1. Identify the key modules, classes, and functions
2. Trace the main code paths and data flow
3. Note design decisions that are not obvious from the code alone
4. Look for edge cases, gotchas, and non-obvious behaviors

Also read `knowledge/architecture.md` to understand how this area fits into the overall system.

### Step 4a: Draft the Knowledge File

Write the file following this structure:

```markdown
# <Feature Area Name>

<One or two sentences describing what this area does.>

## Design Decisions

<Current choice only. One short paragraph per decision, plus a link to the Accepted ADR. Full context and alternatives live in `knowledge/adr/`.>

## API Surface

<Key classes, functions, types, and their relationships. Focus on what another developer (or the AI) needs to know to work in this area correctly.>

## Key Learnings / Gotchas

<Non-obvious behaviors, edge cases, things that broke before, common mistakes to avoid.>
```

### Step 5a: Write and Confirm

Write the file to `knowledge/<feature-area>.md`. Tell the user what was created and suggest they review it.

---

## Updating an Existing Knowledge File

### Step 2b: Identify What Changed

Determine which knowledge file needs updating. This can come from:
- The user specifying a file directly
- A feature that was just implemented or modified
- A bug fix that revealed a non-obvious behavior

### Step 3b: Read Current State

Read the existing knowledge file and the relevant source code. Identify which sections are stale or incomplete.

### Step 4b: Rewrite Affected Sections

Update only the sections that need changes. Feature files describe the **present state** — rewrite sections entirely rather than appending notes or changelogs. Keep the same structure (Design Decisions, API Surface, Key Learnings / Gotchas).

Design Decisions stays a short statement of the current choice plus a link to the Accepted ADR. When the choice changed, write a new ADR (see below) instead of expanding the feature file with history. Do not edit Context, Decision, Consequences, or Alternatives on an existing ADR.

### Step 5b: Write and Confirm

Write the updated file. Tell the user what was changed and why.

---

## Recording an Architectural Decision

### Step 2d: Write the ADR

1. List `knowledge/adr/` and take the next 4-digit number (max + 1). The filename never changes after that.
2. Write `knowledge/adr/NNNN-short-title.md` with these sections, in order: Status (`Accepted`), Date (`YYYY-MM-DD`), Context, Decision, Consequences, Alternatives considered.
3. In the feature file's Design Decisions, state the current choice in one short paragraph and link this ADR. Do not paste the full rationale there.
4. Update the Architectural Decision Records index in `knowledge/architecture.md` in the same change. Group by status. One line each. Accepted entries are the current set.

To retire a decision, do not delete the file.

- **Superseded** — write the new ADR, then set the old Status section to `Superseded by ADR-MMMM`. Move the old index row to Superseded and name the replacement.
- **Deprecated** — nothing replaces it. Set the Status section to `Deprecated` plus one sentence on why it stopped. Move the index row to Deprecated.

The only edit allowed on an old ADR is that Status section. A feature file links only Accepted ADRs.

### Step 3d: Confirm

Tell the user the ADR path, the feature file that links it, and that `knowledge/architecture.md` now lists it.

---

## Reviewing All Knowledge Files

### Step 2c: Scan for Staleness

For each feature file in `knowledge/` except `knowledge/ganesha.md` (Ganesha classification file — Type-only, not a feature doc) and except `knowledge/adr/` (historical records — do not rewrite them to match the feature-file structure):
1. Read the knowledge file
2. Check if the source code it describes has changed significantly since the file was last written
3. Flag files that appear outdated

### Step 3c: Report

Present a summary listing each knowledge file with its status:
- **Current** — the file accurately reflects the source code
- **Needs update** — the source code has diverged; explain what looks stale
- **Missing** — a significant feature area has source code but no knowledge file

Also check that `knowledge/architecture.md` lists every file in `knowledge/adr/` under the status written in that file. Flag a missing or mismatched index row as **Needs update**.

Use **AskQuestion** with `allow_multiple: true` to let the user pick which files to update, then follow the update flow above for each.
