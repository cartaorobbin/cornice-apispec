# Documentation

User-facing docs site at `https://cartaorobbin.github.io/cornice-apispec/`, built with MkDocs Material and deployed to GitHub Pages when a `v*` tag is pushed.

## Design Decisions

MkDocs Material with an mkdocstrings API reference, deployed by the official Pages actions on `v*` tags or a manual run. See [ADR-0001](adr/0001-mkdocs-github-pages-on-release.md).

## API Surface

- `mkdocs.yml`: site config, Material theme, the `mkdocstrings` python handler (`paths: [src]`, `docstring_style: google`), and the nav.
- `docs/`:
  - `index.md`: overview and why this fork exists.
  - `getting-started.md`: `config.include`, the `apispecview` module, and the generated output.
  - `predicates.md`: the `pcm_*` predicates.
  - `oneof-collisions.md`: how names are qualified.
  - `reference.md`: `:::` blocks with explicit `members` lists for `cornice_apispec`, `.generator`, and `.marshmallow`.
  - `development.md`: Poetry commands and building the docs.
- `.github/workflows/docs.yml`: triggered by `push.tags: v*` and `workflow_dispatch`. The `build` job runs `mkdocs build --strict` and uploads `site/`. The `deploy` job deploys to the `github-pages` environment.
- `.github/workflows/tests.yml`: runs `mkdocs build --strict` on every push and PR.
- Local preview: `poetry run mkdocs serve`. `site/` is gitignored.

## Key Learnings / Gotchas

- Tag deploys need a `v*` tag rule on the `github-pages` environment (`deployment-branch-policies` with `type=tag`). Without it the deploy job fails with an environment protection error.
- Pages must be enabled with `build_type=workflow`. The legacy branch source ignores the Actions artifact.
- `--strict` turns warnings into errors: broken internal links, nav entries pointing to missing files, and unresolvable `:::` identifiers.
- `reference.md` lists members explicitly. A new public function does not appear until it is added there.
- Ruff 0.17 formats Python code blocks inside Markdown, so `ruff format` rewrites `docs/*.md` (for example, it collapses `...` bodies onto the `def` line).
- Ruff excludes `.cursor/` and `.claude/`. Those skill files are managed externally and must not be reformatted.
