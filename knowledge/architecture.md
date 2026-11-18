# Architecture

OpenAPI spec generation for Cornice and Pyramid. A host app calls `config.include("cornice_apispec")`, annotates views with `pcm_*` predicates, and serves `/{version}/openapi.json`. `OneofOpenAPIConverter` qualifies colliding `OneOfSchema` component names with a version prefix taken from the schema module path.

## Package Structure

```
src/cornice_apispec/
├── __init__.py        # includeme, get_spec, route /{version}/openapi.json
├── predicates.py      # pcm_* view predicates
├── generator.py       # AutoDoc builds one OpenAPI operation from a view and a Cornice service
└── marshmallow.py     # MarshmallowPlugin and OneofOpenAPIConverter
tests/
├── conftest.py          # Cornice service, query/header schemas, Configurator with predicates
├── test_generator.py    # AutoDoc deprecation output, pcm_deprecated registration
└── test_marshmallow.py  # OneOfSchema component names, including v1/v3 collisions
docs/                    # MkDocs pages (see knowledge/documentation.md)
mkdocs.yml               # MkDocs Material + mkdocstrings config
.github/workflows/
├── tests.yml            # pytest, ruff, mkdocs build --strict
├── publish.yml          # PyPI publish on v* tags
└── docs.yml             # GitHub Pages deploy on v* tags or manual run
.devcontainer/
└── devcontainer.json    # Python 3.12 Poetry container
```

## Architectural Decision Records

Index of `knowledge/adr/`.

### Accepted

- ADR-0001: [MkDocs documentation deployed to GitHub Pages on release tags](adr/0001-mkdocs-github-pages-on-release.md)

### Superseded

None yet.

### Deprecated

None yet.

## Core Design Decisions

The library is a Pyramid add-on. `includeme` includes `pyramid_apispec.views`, registers the `pcm_*` predicates, and mounts one JSON view at `/{version}/openapi.json`. That view imports `{root_package}.views.api.{version}.apispecview` and calls `api_spec(request)`. A missing version module returns 404.

`get_spec` builds an OpenAPI 3.0.2 document with `MarshmallowPlugin`. It walks introspected views, keeps those whose `pcm_show` matches the URL version, and skips HEAD and OPTIONS. Path parameters come from `{placeholder}` segments in the Cornice route. The server URL is the current request's scheme and host.

Deprecation comes from two sources, because Cornice has none. `pcm_deprecated=True` on a view sets `deprecated: true` on the operation (`AutoDoc._add_deprecated`). Marshmallow field `metadata={"deprecated": True}` sets `deprecated: true` on query and header parameters (`AutoDoc._build_parameter`). apispec's Marshmallow plugin already copies the same metadata onto body and response component properties. A falsy value omits the key.

`OneofOpenAPIConverter` is the reason this fork exists. When two `OneOfSchema` members resolve to the same component name, it prefixes the name with `V{n}` from a `vN` segment in the schema's module path. `myapp.views.api.v3.schemas.PartSchema` becomes `V3PartSchema`. If the module has no `vN` segment, it uses the parent package name capitalized.

Dependencies are managed with Poetry. Runtime Python is `^3.11`. Local development and the dev container use 3.12. Dev dependencies are pytest, ruff, mkdocs-material, and mkdocstrings. Ruff excludes the managed `.cursor/` and `.claude/` folders.

## Component Relationships

```
includeme
  -> predicates.register          pcm_* view predicates
  -> route /{version}/openapi.json
       -> views.api.{version}.apispecview.api_spec
            -> get_spec
                 -> APISpec + MarshmallowPlugin
                 -> introspected views filtered by pcm_show
                 -> AutoDoc (Cornice service + pcm_* metadata)
                 -> OneofOpenAPIConverter for OneOfSchema members
```

## Key Learnings / Gotchas

- `pcm_show` must equal the `{version}` path segment. Views that do not match are omitted from the spec.
- HEAD and OPTIONS are skipped by comparing `request_methods.lower()` to `"head"` and `"option"`. The string `"options"` does not match `"option"`.
- A missing `views.api.{version}.apispecview` module is a 404 with an empty body.
- Component qualification runs only when the resolved name is already in `spec.components.schemas`. The first schema keeps the bare name. Later collisions get the version prefix.
- `get_spec` swallows `DuplicateComponentNameError` when registering `pcm_request` and `pcm_responses` schemas. Qualification of `OneOfSchema` members happens inside `OneofOpenAPIConverter.schema2jsonschema`.
- `get_schema_name` appends a 5-character MD5 prefix when a schema instance sets `exclude`, so two instances of the same class with different exclusions do not share a component name.
- Cornice 6.x `Service` and its view decorators have no `deprecated` or `sunset` option. Pyramid has none either. Use `pcm_deprecated` and field metadata.
- Query and header parameters are built by hand in `AutoDoc._build_parameter`, not by apispec. Any field metadata that should reach a parameter (such as `deprecated`) must be copied there explicitly.
- Pyramid registers its own default views, so `introspector.get_category("views")` returns more than the app's views. Tests use `introspector.related(route)` to get one route's views.
- The wrapper around an introspected view is spelled `InstropectedView`.
- Collision tests assign `__module__` on a dynamically created `PartSchema` to simulate a v3 module. Qualification depends on that module path, not on the class name.
