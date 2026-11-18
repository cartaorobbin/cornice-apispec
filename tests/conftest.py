from collections.abc import Callable

import marshmallow as ma
import pytest
from cornice import Service
from pyramid.config import Configurator
from pyramid.request import Request
from pyramid.response import Response

from cornice_apispec.predicates import register


class ListUsersQuerySchema(ma.Schema):
    """List users query."""

    page = ma.fields.Integer()
    offset = ma.fields.Integer(metadata={"deprecated": True})


class ClientHeadersSchema(ma.Schema):
    """Client headers."""

    client_version = ma.fields.String(data_key="X-Client-Version")
    legacy_token = ma.fields.String(data_key="X-Legacy-Token", metadata={"deprecated": True})


@pytest.fixture
def users_service() -> Service:
    return Service(name="users", path="/users")


@pytest.fixture
def query_schema() -> type[ma.Schema]:
    return ListUsersQuerySchema


@pytest.fixture
def headers_schema() -> type[ma.Schema]:
    return ClientHeadersSchema


@pytest.fixture
def empty_view() -> Callable[[Request], Response]:
    return lambda request: Response()


@pytest.fixture
def config() -> Configurator:
    configurator = Configurator()
    register(configurator)
    return configurator
