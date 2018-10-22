import json
from graphformation import schema
from graphformation import executor

"""
 for simplicity our graph is global
 see execute_change_program how to execute two programs without poluting the state
"""
graph = {}


_reserved_words = ["ref"]


def _verify_id(id):
    if id in _reserved_words:
        raise Exception("id cannot be the reserved work {id}".format(id))


class Resource(object):
    def __init__(self, id, type, properties, schema):
        _verify_id(id)
        self.id=id
        self.type=type
        self.properties=properties
        self.schema = schema

    def json_repr(self):
        properties_repr = {}
        for id, value in self.properties.items():
            if value is None:
                continue
            if isinstance(value, (Resource, Ref)):
                properties_repr[id]=value.json_repr()
            else:
                properties_repr[id]=value

        return {
            "id": self.id,
            "type": self.type,
            "properties": properties_repr
        }


class Ref(object):
    def __init__(self, obj):
        self.obj = obj

    def json_repr(self):
        return {
            "!ref": self.obj.id
        }


def _add_to_graph(obj):
    if obj.id in graph:
        raise Exception(("Resource with {id} has already been defined. ",
                        "You probably need to change the id for the following resource: {obj}").format(
                        id=id, obj=obj))
    graph[obj.id] = obj


def _define(id, type, properties):
    s = schema.from_type(type)
    resource = Resource(id, type, properties, s)

    _add_to_graph(resource)
    return resource


def directory(*, id, location, permissions="700"):
    return _define(id, "directory", {
        "location": location,
        "permissions": permissions
    })


def file(*, id, parent, filename=None, text=None, source=None, permissions="600"):
    return _define(id, "file", {
        "parent": parent,
        "filename": filename,
        "text": text,
        "source": source,
        "permissions": permissions
    })


def dummy_ref_resource(*, id, mutable_parent=None, immutable_parent=None):
    return _define(id, "dummy_ref_resource", {
        "mutable_parent": mutable_parent,
        "immutable_parent": immutable_parent,
    })


def ref(input):
    return Ref(input)


def graph_repr():
    repr = {}
    for id, resource in graph.items():
        repr[id] = resource.json_repr()
        resource.schema.validate_definition(repr[id])
    return repr


def dump_graph():
    print(json.dumps(graph_repr(), indent=2, sort_keys=True))


def execute(filename):
    repr = graph_repr()
    return executor.execute(filename, repr)


def execute_change_program(f, old_state):
    global graph
    save_graph = graph
    graph = {}
    try:
        f() # run the program
        result = execute(old_state)
    finally:
        graph = save_graph
    return result