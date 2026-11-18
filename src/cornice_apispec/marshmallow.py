import re

from apispec.ext import marshmallow
from apispec.ext.marshmallow import common
from marshmallow_oneofschema import OneOfSchema


class OneofOpenAPIConverter(marshmallow.OpenAPIConverter):

    @staticmethod
    def _qualify_name(schema_cls, base_name):
        """Prefix with version segment from module path to avoid collision."""
        module = schema_cls.__module__ or ""
        match = re.search(r"\bv(\d+)\b", module)
        if match:
            return f"V{match.group(1)}{base_name}"
        parts = module.rsplit(".", 2)
        qualifier = parts[-2] if len(parts) >= 2 else "Alt"
        return f"{qualifier.capitalize()}{base_name}"

    def schema2jsonschema(self, schema):
        if self.openapi_version.major < 3 or not is_oneof(schema):
            return super().schema2jsonschema(schema)

        mapping = {}
        oneof = []
        for name, type_schema in schema.type_schemas.items():
            schema_instance = common.resolve_schema_instance(type_schema)
            schema_key = common.make_schema_key(schema_instance)

            if schema_key not in self.refs:
                component_name = self.schema_name_resolver(type_schema) or name

                # FIX: qualify name if it already exists (v3 vs v1 collision)
                if component_name in self.spec.components.schemas:
                    component_name = self._qualify_name(
                        type(schema_instance), component_name
                    )

                self.spec.components.schema(component_name, schema=type_schema)

            ref_dict = self.get_ref_dict(schema_instance)
            mapping[name] = ref_dict["$ref"]
            oneof.append(ref_dict)

        return {
            "oneOf": oneof,
            "discriminator": {
                "propertyName": schema.type_field,
                "mapping": mapping,
            },
        }


def is_oneof(schema):
    return (isinstance(schema, type) and issubclass(schema, OneOfSchema)) or isinstance(
        schema, OneOfSchema
    )


class MarshmallowPlugin(marshmallow.MarshmallowPlugin):
    Converter = OneofOpenAPIConverter

    def init_spec(self, spec):
        super().init_spec(spec)
        self.spec = spec
        self.openapi_version = spec.openapi_version
        self.openapi = OneofOpenAPIConverter(
            openapi_version=spec.openapi_version,
            schema_name_resolver=self.schema_name_resolver,
            spec=spec,
        )
