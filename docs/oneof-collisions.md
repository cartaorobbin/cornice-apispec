# OneOfSchema collisions

## The problem

`marshmallow-oneofschema` lets one schema stand for several concrete schemas. In
OpenAPI it becomes a `oneOf` with a `discriminator`, and each concrete schema is
registered as its own component.

With versioned APIs, two concrete schemas often share a class name:

```text
myapp/views/api/v1/schemas.py   -> class PartSchema
myapp/views/api/v3/schemas.py   -> class PartSchema
```

Both resolve to the same component name. Plain apispec raises
`DuplicateComponentNameError` when the second one is registered.

## The fix

`MarshmallowPlugin` from this package uses `OneofOpenAPIConverter`. When it registers a
`OneOfSchema` member whose component name is already taken, it qualifies the name:

1. If the schema's module path has a `vN` segment, the name gets a `V{N}` prefix.
   `myapp.views.api.v3.schemas.PartSchema` becomes `V3Part...`.
2. Otherwise, the name gets the capitalized parent package as a prefix.
   `myapp.alternate.schemas` gives `Alternate...`.
3. If the module has no parent package, the prefix is `Alt`.

The `oneOf` entries and the discriminator `mapping` point to the qualified component.

```python
from apispec import APISpec
from cornice_apispec.marshmallow import MarshmallowPlugin

spec = APISpec(
    title="Example",
    version="1.0.0",
    openapi_version="3.0.2",
    plugins=[MarshmallowPlugin()],
)
spec.components.schema("Part", schema=V1PartSchema)
spec.components.schema("PartUnion", schema=PartUnion)  # a OneOfSchema with v3 PartSchema

schemas = spec.to_dict()["components"]["schemas"]
assert "Part" in schemas
assert "V3Part" in schemas
```

!!! note
    Only later collisions are qualified. The first schema keeps the bare name.
    Qualification depends on the module path, not on the class name.
