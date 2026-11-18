# View predicates

`config.include("cornice_apispec")` registers these view predicates. They always match,
so they never change routing. They only attach OpenAPI metadata to the view, which
`get_spec` reads back from the Pyramid introspector.

| Predicate | Value | OpenAPI output |
|---|---|---|
| `pcm_show` | API version string, such as `"v1"` | Includes the view in that version's spec |
| `pcm_request` | `dict` of location to schema | `requestBody` and `parameters` |
| `pcm_responses` | `dict` of status code to schema or text | `responses` |
| `pcm_tags` | `list` of strings | `tags` |
| `pcm_summary` | string | `summary` |
| `pcm_description` | string | `description` |
| `pcm_security` | security scheme name | `security: [{name: []}]` |
| `pcm_deprecated` | `bool` | `deprecated: true` |

## `pcm_show`

A view appears in a spec only when `pcm_show` equals the `{version}` segment of the
spec URL. A view with `pcm_show="v1"` is in `/v1/openapi.json` and nowhere else. Views
without `pcm_show` are never documented.

## `pcm_request`

Map a request location to a Marshmallow schema:

- `"body"`: becomes the `requestBody`, as a `$ref` to the schema component.
- `"querystring"`: each declared field becomes an `in: query` parameter.
- `"headers"`: each declared field becomes an `in: header` parameter.

Parameter names use the field's `data_key` when set. `required` comes from the field,
and the type comes from the field class (`Integer`, `UUID`, `DateTime`, and so on).
Unknown field types are documented as strings.

```python
@users.post(
    pcm_show="v1",
    pcm_request={"body": CreateUserSchema, "querystring": DryRunSchema},
    pcm_responses={"201": UserSchema, "400": "Invalid payload"},
)
def create_user(request): ...
```

## `pcm_responses`

Map a status code to either:

- A schema class or instance. The response description is the schema docstring.
  An instance with `many=True` becomes an array of that schema.
- A string. The response has that description and no content.

The content type is the first one declared on the Cornice service for that method,
or `application/json` when none is declared.

## `pcm_security`

Name a scheme that you pass to `get_spec(security_scheme=...)`:

```python
@users.delete(pcm_show="v1", pcm_security="bearerAuth")
def delete_user(request): ...
```

## Deprecation

Cornice has no deprecation concept, so you mark deprecated parts of the API yourself.

To deprecate an operation, set `pcm_deprecated=True`. The operation gets
`deprecated: true`. The key is left out when the value is falsy.

```python
@users.get(pcm_show="v1", pcm_deprecated=True)
def list_users_legacy(request): ...
```

To deprecate a single field, set `deprecated` in the field metadata:

```python
class ListUsersQuery(Schema):
    page = fields.Integer()
    offset = fields.Integer(metadata={"deprecated": True})
```

A field in a `"querystring"` or `"headers"` schema becomes a parameter with
`deprecated: true`. A field in a `"body"` or response schema becomes a component
property with `deprecated: true`.

## Component names

Schema classes use their class name as the component name. A schema instance created
with `exclude=` gets a short hash suffix, so two instances of the same class with
different exclusions do not share a component. A schema with
`__apispec__ = {"model": "Name"}` uses that name instead.
