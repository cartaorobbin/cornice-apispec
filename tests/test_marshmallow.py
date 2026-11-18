from typing import ClassVar

import marshmallow as ma
from apispec import APISpec
from marshmallow_oneofschema import OneOfSchema

from cornice_apispec.marshmallow import MarshmallowPlugin, OneofOpenAPIConverter

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class CatSchema(ma.Schema):
    name = ma.fields.String()
    meow_volume = ma.fields.Integer()


class DogSchema(ma.Schema):
    name = ma.fields.String()
    bark_pitch = ma.fields.Integer()


class PetSchema(OneOfSchema):
    type_field = "pet_type"
    type_schemas: ClassVar[dict[str, type[ma.Schema]]] = {"cat": CatSchema, "dog": DogSchema}


# Schemas that collide on resolved name ("Part")
class PartSchema(ma.Schema):
    """V1 PartSchema — resolves to 'Part'."""

    part_id = ma.fields.Integer()


# Second PartSchema in a fake v3 module — also resolves to "Part"
_V3PartSchema = type("PartSchema", (ma.Schema,), {"weight": ma.fields.Float()})
_V3PartSchema.__module__ = "myapp.views.api.v3.schemas"
_V3PartSchema.__qualname__ = "PartSchema"


class CollisionOneOf(OneOfSchema):
    type_field = "kind"
    type_schemas: ClassVar[dict[str, type[ma.Schema]]] = {"v3_part": _V3PartSchema}


def _make_spec(**kw):
    return APISpec(
        title="Test",
        version="0.1.0",
        openapi_version="3.0.2",
        plugins=[MarshmallowPlugin()],
        **kw,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestQualifyName:
    def test_extracts_version_from_module(self):
        cls = type("Foo", (), {"__module__": "myapp.views.api.v3.schemas"})
        result = OneofOpenAPIConverter._qualify_name(cls, "Foo")
        assert result == "V3Foo"

    def test_extracts_version_v12(self):
        cls = type("Bar", (), {"__module__": "app.v12.models"})
        result = OneofOpenAPIConverter._qualify_name(cls, "Bar")
        assert result == "V12Bar"

    def test_fallback_to_parent_module(self):
        # rsplit('.', 2) on "myapp.alternate.schemas" → ['myapp', 'alternate', 'schemas']
        # parts[-2] = 'alternate'
        cls = type("Baz", (), {"__module__": "myapp.alternate.schemas"})
        result = OneofOpenAPIConverter._qualify_name(cls, "Baz")
        assert result == "AlternateBaz"

    def test_fallback_single_segment(self):
        cls = type("Qux", (), {"__module__": "schemas"})
        result = OneofOpenAPIConverter._qualify_name(cls, "Qux")
        assert result == "AltQux"

    def test_empty_module(self):
        cls = type("Empty", (), {"__module__": ""})
        result = OneofOpenAPIConverter._qualify_name(cls, "Empty")
        assert result == "AltEmpty"


class TestOneOfNoCollision:
    def test_oneof_generates_discriminator(self):
        spec = _make_spec()
        spec.components.schema("Pet", schema=PetSchema)
        spec_dict = spec.to_dict()

        pet = spec_dict["components"]["schemas"]["Pet"]
        assert "oneOf" in pet
        assert "discriminator" in pet
        assert pet["discriminator"]["propertyName"] == "pet_type"
        assert len(pet["oneOf"]) == 2

        # Both sub-schemas registered (apispec strips "Schema" suffix)
        assert "Cat" in spec_dict["components"]["schemas"]
        assert "Dog" in spec_dict["components"]["schemas"]

    def test_refs_point_to_components(self):
        spec = _make_spec()
        spec.components.schema("Pet", schema=PetSchema)
        spec_dict = spec.to_dict()

        pet = spec_dict["components"]["schemas"]["Pet"]
        refs = {item["$ref"] for item in pet["oneOf"]}
        assert "#/components/schemas/Cat" in refs
        assert "#/components/schemas/Dog" in refs


class TestOneOfWithCollision:
    def test_collision_qualifies_name(self):
        spec = _make_spec()

        # Register V1 Part first — the resolved name is "Part"
        spec.components.schema("Part", schema=PartSchema)

        # Now register the OneOfSchema whose type_schema also resolves to "Part"
        spec.components.schema("CollisionOneOf", schema=CollisionOneOf)

        spec_dict = spec.to_dict()
        schemas = spec_dict["components"]["schemas"]

        # Original stays
        assert "Part" in schemas
        # Collision was qualified with V3 prefix
        assert "V3Part" in schemas
        # The OneOf ref points to the qualified name
        collision = schemas["CollisionOneOf"]
        refs = {item["$ref"] for item in collision["oneOf"]}
        assert "#/components/schemas/V3Part" in refs

    def test_no_duplicate_error_raised(self):
        """The whole point: this must not raise DuplicateComponentNameError."""
        spec = _make_spec()
        spec.components.schema("Part", schema=PartSchema)
        # Should not raise
        spec.components.schema("CollisionOneOf", schema=CollisionOneOf)
