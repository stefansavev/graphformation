import json


class Property(object):
    def __init__(self, *, required, mutable):
        self.required=required
        self.mutable=mutable


def _one_of_validator(resource, expected_properties):
    has_properties = []
    defined_properties = resource["properties"]
    for prop in expected_properties:
        if defined_properties.get(prop, None):
            has_properties = prop
    if len(has_properties) == 0:
        raise Exception("Expected one of the following properties {expected_properties} to be defined for {obj}".
                        format(expected_properties=", ".join(expected_properties), obj=json.dumps(resource, indent=2)))


def _required_validator(resource, expected_property):
    defined_properties = resource["properties"]
    if defined_properties.get(expected_property, None) is None:
        raise Exception("The property {expected_property} is expected to be defined for {obj}".
                        format(expected_property=expected_property, obj=json.dumps(resource, indent=2)))


class Schema(object):
    def __init__(self, type, properties):
        self.type = type
        self.properties = properties

    def validate_definition(self, resource):
        self.validate("define", resource)

    def validate(self, operation, resource):
        if resource["type"] != self.type:
            raise Exception("Internal error. Wrong resource type passed to schema")

        for propname, prop_def in self.properties.items():
            if type(prop_def.required) == bool:
                if prop_def.required:
                    _required_validator(resource, propname)
            else:
                # must be custom validator
                prop_def.required(resource)


class Directory(Schema):
    def __init__(self):
        properties = {
                "location": Property(required=True, mutable=False),
                "permissions": Property(required=True, mutable=True)
            }
        super().__init__("directory", properties)


class File(Schema):
    def __init__(self):
        def custom_validator(resource):
            return _one_of_validator(resource, ["source", "text"])

        properties = {
            "filename": Property(required=True, mutable=True),
            "parent": Property(required=True, mutable=False),
            "source": Property(required=custom_validator, mutable=False),
            "text": Property(required=custom_validator, mutable=False)
        }

        super().__init__("file", properties)


class DummyRefResource(Schema):
    def __init__(self):
        properties = {
            "mutable_parent": Property(required=False, mutable=True),
            "immutable_parent": Property(required=False, mutable=False)
        }

        super().__init__("dummy_ref_resource", properties)


schemas = {
    "directory": Directory(),
    "file": File(),
    "dummy_ref_resource": DummyRefResource()
}


def from_type(type):
    if type not in schemas:
        raise Exception("Internal error. Cannot find schema for type {type}".format(type))
    return schemas[type]