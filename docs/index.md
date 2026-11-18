# cornice-apispec

OpenAPI 3 spec generation for [Cornice](https://cornice.readthedocs.io/) and
[Pyramid](https://trypyramid.com/) services, with
[Marshmallow](https://marshmallow.readthedocs.io/) and
[marshmallow-oneofschema](https://github.com/marshmallow-code/marshmallow-oneofschema) support.

You describe each view with `pcm_*` view predicates. The package walks the Pyramid
introspector, builds one OpenAPI document per API version, and serves it at
`/{version}/openapi.json` with an API explorer at `/{version}/api-explorer`.

## Why this fork

cornice-apispec is a fork of [pycornmarsh](https://github.com/niccolofanton/pycornmarsh).
It fixes `OneOfSchema` component name collisions.

When several API versions define schemas with the same class name, such as
`v1.PartSchema` and `v3.PartSchema`, both resolve to the same component name.
apispec then raises `DuplicateComponentNameError`.

`OneofOpenAPIConverter` detects the collision and qualifies the later name with the
version taken from the schema's module path, for example `V3PartSchema`. See
[OneOfSchema collisions](oneof-collisions.md) for the details.

## Installation

```bash
pip install cornice-apispec
```

Requires Python 3.11 or newer.

## Next steps

- [Getting started](getting-started.md): wire the package into a Pyramid app.
- [View predicates](predicates.md): describe operations with `pcm_*` arguments.
- [API reference](reference.md): the public functions and classes.
