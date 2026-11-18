# Development

The project uses [Poetry](https://python-poetry.org/). A dev container with Python 3.12
and Poetry is included. Reopen the repository in the container and the dependencies
are installed with `poetry install`.

## Common commands

```bash
poetry install                 # install runtime and dev dependencies
poetry run pytest              # run the tests
poetry run ruff check .        # lint
poetry run ruff format .       # format
```

## Documentation

The docs use MkDocs with the Material theme. The API reference is generated from
docstrings by mkdocstrings.

```bash
poetry run mkdocs serve           # live preview at http://127.0.0.1:8000
poetry run mkdocs build --strict  # the same build CI runs
```

CI builds the docs with `--strict` on every push and pull request, so warnings such as
broken links fail the build.

## Releases

Pushing a `v*` tag publishes the package to PyPI and deploys this site to
GitHub Pages. You can also deploy the site manually by running the **Docs** workflow
from the Actions tab.
