# -*- coding: utf-8 -*-
"""Spec

In this module we define(specify) our resources
"""


import json
import os
from graphformation import schema as gf_schema
from graphformation import executor


# for simplicity our graph is global
# see execute_change_program how to execute two programs without poluting the state
GRAPH = {}


_RESERVED_WORDS = ["!ref"]


def _verify_id(resource_id):
    if resource_id in _RESERVED_WORDS:
        raise Exception("id cannot be the reserved word {resource_id}".
                        format(resource_id=resource_id))


class Resource: # pylint: disable=too-few-public-methods
    """
    Resource represents a virtual resource
    """
    def __init__(self, resource_id, resource_type, properties, schema):
        _verify_id(resource_id)
        self.resource_id = resource_id
        self.resource_type = resource_type
        self.properties = properties
        self.schema = schema

    def json_repr(self):
        """
        Converts the object to dictionary useful for dumping the object into json
        :return: dictionary
        """
        properties_repr = {}
        for resource_id, value in self.properties.items():
            if value is None:
                continue
            if isinstance(value, (Resource, Ref)):
                properties_repr[resource_id] = value.json_repr()
            else:
                properties_repr[resource_id] = value

        return {
            "id": self.resource_id,
            "resource_type": self.resource_type,
            "properties": properties_repr
        }


class Ref:
    """
    Ref represents a reference to a resource
    """
    def __init__(self, obj):
        self.obj = obj

    def json_repr(self):
        """
        Converts the object to dictionary useful for dumping the object into json
        :return: dictionary
        """
        return {
            "!ref": self.obj.resource_id
        }


def _add_to_graph(obj):
    if obj.resource_id in GRAPH:
        msg = ("Resource with {resource_id} has already been defined. "
               "You probably need to change the id for the following "
               "resource: {obj}").format(resource_id=obj.resource_id, obj=obj.json_repr())
        raise Exception(msg)
    GRAPH[obj.resource_id] = obj


def _define(resource_id, resource_type, properties):
    resource_schema = gf_schema.from_type(resource_type)
    resource = Resource(resource_id, resource_type, properties, resource_schema)

    _add_to_graph(resource)
    return resource


def directory(*, resource_id, location, permissions="700"):
    """
    :param resource_id: the id of the resource
    :param location: location on disk of the directory
    :param permissions: permissions of the directory
    :return: a resource representing the directory
    """
    return _define(resource_id, "directory", {
        "location": location,
        "permissions": permissions
    })


def file(*, resource_id, parent, filename=None, text=None, source=None, permissions="600"):
    """
    :param resource_id: the id of the resource
    :param parent: the parent directory of the resource
    :param filename: the filename under which the file will be created
    :param text: the text of the file if the file is a textual file
    :param source: the url or file from which the file was copied
    :param permissions: the permissions on the file
    :return: a resource representing a file
    """
    return _define(resource_id, "file", {
        "parent": parent,
        "filename": filename,
        "text": text,
        "source": source,
        "permissions": permissions
    })


def dummy_ref_resource(*, resource_id, mutable_parent=None, immutable_parent=None):
    """
    :param resource_id: the id of the resource
    :param mutable_parent: a parent which can be changed
    :param immutable_parent: a parent which cannot be changed.
    both parents can be different or the same resource
    :return: a resource representing a reference
    """
    return _define(resource_id, "dummy_ref_resource", {
        "mutable_parent": mutable_parent,
        "immutable_parent": immutable_parent,
    })


def ref(obj):
    """
    :param input: a resource
    :return: a reference to resource
    """
    return Ref(obj)


def graph_repr():
    """
    :return: a json representation of the resource graph
    """
    json_repr = {}
    for resource_id, resource in GRAPH.items():
        json_repr[resource_id] = resource.json_repr()
        resource.schema.validate_definition(json_repr[resource_id])
    return json_repr


def print_graph():
    """
    prints the json representation of the graph on stdout
    :return: None
    """
    print(json.dumps(graph_repr(), indent=2, sort_keys=True))


def _read_state(filename):
    if not os.path.isfile(filename):
        return {}
    with open(filename, 'r') as f:
        contents = f.read()
    return json.loads(contents)


def execute(filename):
    """
    Executes or applies the resource graph
    :param filename: the filename where the state will be stored
    :return: a tuple of the json representation of the state and an executable program
    """
    old_state = _read_state(filename)
    json_repr = graph_repr()
    _, prog = executor.execute(old_state, json_repr)

    with open(filename, 'w') as f:
        f.write(json.dumps(graph_repr, indent=2))
    return json_repr, prog


def execute_change_program(f, old_state):
    """
    Executes a program without affecting global state. It is not thread safe
    :param f: a function which manipulates resources
    :param old_state: the previous state of the resoures
    :return: a tuple of the json representation of the state and an executable program
    """
    global GRAPH # pylint: disable=W0603
    save_graph = GRAPH
    GRAPH = {}
    try:
        f() # run the program
        json_repr = graph_repr()
        result = executor.execute(old_state, json_repr)
    finally:
        GRAPH = save_graph
    return result
