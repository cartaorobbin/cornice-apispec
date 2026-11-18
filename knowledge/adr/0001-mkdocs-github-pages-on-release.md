# ADR-0001: MkDocs documentation deployed to GitHub Pages on release tags

## Status

Accepted

## Date

2026-11-18

## Context

The project had only a README. Users need a guide to the `pcm_*` predicates, the
per-version `apispecview` module convention, and the OneOfSchema collision fix, plus an
API reference. The repository is public on GitHub and already releases by pushing `v*`
tags, which trigger the PyPI publish workflow.

## Decision

- Build the site with MkDocs and the Material theme. Generate the API reference from
  docstrings with `mkdocstrings[python]`, using Google-style docstrings.
- Keep the docs tooling in the Poetry `dev` group.
- Deploy with the official GitHub Pages actions (`upload-pages-artifact` and
  `deploy-pages`) from `.github/workflows/docs.yml`. Pages source is "GitHub Actions".
  No `gh-pages` branch.
- Deploy on `v*` tag pushes, so the site matches the latest release on PyPI. Allow a
  manual `workflow_dispatch` run as well.
- Build with `mkdocs build --strict` in the test workflow so broken docs fail CI before
  a release.

## Consequences

- Docs changes merged to `main` are not live until the next release tag or a manual run.
- The `github-pages` environment must allow `v*` tags. By default it accepts only the
  default branch, and tag deploys are rejected.
- Public functions shown in the reference need Google-style docstrings.

## Alternatives considered

- **Sphinx with autodoc**: more powerful cross-referencing, but reStructuredText and
  more configuration for a small library.
- **MkDocs without mkdocstrings**: simpler, but the API reference would drift from the code.
- **Deploy on every push to `main`**: docs would describe unreleased behavior.
- **`mkdocs gh-deploy` to a `gh-pages` branch**: needs write access to the repository
  contents and keeps generated HTML in git history.
