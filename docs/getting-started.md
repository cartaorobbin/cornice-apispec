# Getting started

## 1. Include the package

Include `cornice_apispec` in your Pyramid configuration, next to Cornice:

```python
from pyramid.config import Configurator


def main(global_config, **settings):
    with Configurator(settings=settings) as config:
        config.include("cornice")
        config.include("cornice_apispec")
        config.scan()
    return config.make_wsgi_app()
```

`includeme` does three things:

- Includes `pyramid_apispec.views`, which provides the API explorer.
- Registers the `pcm_*` [view predicates](predicates.md).
- Adds the `openapi_spec` route at `/{version}/openapi.json` and the explorer at
  `/{version}/api-explorer`.

## 2. Add one spec module per API version

The `/{version}/openapi.json` view imports this module:

```text
{root_package}.views.api.{version}.apispecview
```

Then it calls the module's `api_spec(request)` function. `root_package` is the package
that created the `Configurator`. For a request to `/v1/openapi.json` in a package named
`myapp`, the module is `myapp.views.api.v1.apispecview`:

```python
# myapp/views/api/v1/apispecview.py
from cornice_apispec import get_spec


def api_spec(request):
    return get_spec(
        request,
        title="My API",
        version="1.0.0",
        description="Public API, version 1.",
        security_scheme={
            "bearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"},
        },
    )
```

!!! note
    If the module does not exist, the view responds with `404` and an empty JSON body.

## 3. Describe your views

Mark each Cornice view with `pcm_show` set to the version it belongs to, and add
schemas and metadata:

```python
import marshmallow as ma
from cornice import Service


class UserSchema(ma.Schema):
    """A user."""

    id = ma.fields.UUID()
    email = ma.fields.Email(required=True)


users = Service(name="users", path="/v1/users", description="Users")


@users.get(
    pcm_show="v1",
    pcm_tags=["users"],
    pcm_summary="List users",
    pcm_responses={"200": UserSchema(many=True)},
)
def list_users(request):
    ...
```

Open `/v1/openapi.json` for the generated document, or `/v1/api-explorer` to browse it.

## What gets generated

`get_spec` builds an OpenAPI `3.0.2` document:

- Only views whose `pcm_show` equals the `{version}` path segment are included.
- `HEAD` views are skipped.
- `{placeholder}` segments in the route pattern become required string path parameters.
- Schemas in `pcm_request` and `pcm_responses` are registered as components.
- `servers` is set to the scheme and host of the current request.
- `security_scheme` entries are added to `components.securitySchemes`.
