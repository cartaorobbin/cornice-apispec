import pytest

from cornice_apispec.generator import AutoDoc


@pytest.mark.parametrize(
    ("introspectable", "expected"),
    [
        ({"pcm_deprecated": True}, True),
        ({"pcm_deprecated": False}, None),
        ({}, None),
    ],
    ids=["deprecated", "explicitly-not-deprecated", "missing"],
)
def test_operation_deprecated_flag(users_service, introspectable, expected):
    """`pcm_deprecated` marks the operation and is omitted when falsy."""
    operation = AutoDoc("GET", introspectable, users_service).to_dict()["get"]

    assert operation.get("deprecated") == expected


def test_querystring_parameter_deprecated_from_field_metadata(users_service, query_schema):
    """A querystring field with `deprecated` metadata becomes a deprecated parameter."""
    introspectable = {"pcm_request": {"querystring": query_schema}}

    operation = AutoDoc("GET", introspectable, users_service).to_dict()["get"]
    parameters = {p["name"]: p for p in operation["parameters"]}

    assert parameters["offset"]["deprecated"] is True
    assert "deprecated" not in parameters["page"]


def test_header_parameter_deprecated_from_field_metadata(users_service, headers_schema):
    """A header field with `deprecated` metadata becomes a deprecated parameter."""
    introspectable = {"pcm_request": {"headers": headers_schema}}

    operation = AutoDoc("GET", introspectable, users_service).to_dict()["get"]
    parameters = {p["name"]: p for p in operation["parameters"]}

    assert parameters["X-Legacy-Token"] == {
        "name": "X-Legacy-Token",
        "in": "header",
        "required": False,
        "schema": {"type": "string"},
        "description": "Client headers.",
        "deprecated": True,
    }
    assert "deprecated" not in parameters["X-Client-Version"]


def test_pcm_deprecated_predicate_is_registered(config, empty_view):
    """`add_view` accepts `pcm_deprecated` and stores it on the view introspectable."""
    config.add_route("users", "/users")
    config.add_view(empty_view, route_name="users", request_method="GET", pcm_deprecated=True)
    config.commit()

    introspector = config.registry.introspector
    route = introspector.get("routes", "users")
    related_views = introspector.related(route)

    assert [view.get("pcm_deprecated") for view in related_views] == [True]
