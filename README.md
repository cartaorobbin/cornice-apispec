# cornice-apispec

OpenAPI spec generation for Cornice/Pyramid with Marshmallow and OneOfSchema support.

Forked from [pycornmarsh](https://github.com/niccolofanton/pycornmarsh) with a fix for `OneOfSchema` component name collisions when multiple API versions define schemas with the same class name.

## Installation

```bash
pip install cornice-apispec
```

## The Problem

When using `marshmallow-oneofschema` with multiple API versions (e.g. `v1.PartSchema` and `v3.PartSchema`), the OpenAPI spec generator would raise `DuplicateComponentNameError` because both schemas resolve to the same component name `PartSchema`.

## The Fix

`OneofOpenAPIConverter` now detects name collisions and automatically qualifies the component name with a version prefix extracted from the schema's module path (e.g. `V3PartSchema`).

## Usage

```python
from cornice_apispec import get_spec

# In your Pyramid app
config.include("cornice_apispec")
```

## License

BSD-3-Clause
