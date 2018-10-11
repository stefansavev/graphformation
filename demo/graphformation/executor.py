import json, os
from graphformation import schema


class OpCtx(object):
    def __init__(self, op_type, resource, comment=None):
        self.comment = "# {op_type} {resource_type} {resource_id}".format(
            op_type = op_type,
            resource_type=resource["type"],
            resource_id=resource["id"]
        )
        self.commands = []

    def command(self, cmd):
        self.commands.append(cmd)

    def dump(self, indent):
        commands_repr = "\n".join(map(lambda x: x + " ", self.commands))
        repr = self.comment + "\n"
        repr += commands_repr
        repr += "\n# end\n\n"
        return repr

class ScriptCtx(object):
    def __init__(self, repr):
        self.repr = repr
        self.operations = []

    def operation(self, type, resource, comment=None):
        operation = OpCtx(type, resource, comment=None)
        self.operations.append(operation)
        return operation

    def get_ref(self, ref):
        id = ref.get("ref")
        if id is None:
            raise Exception("Internal error. Expected reference, found {}".format(json.format(ref)))
        return self.repr[id]

    def dump(self):
        r = "\n".join(map(lambda x: x.dump(2), self.operations))
        print(r)

class ExecutableResource(object):
    pass

class Directory(ExecutableResource):
    def __init__(self, resource):
        self.resource=resource
        self.schema = schema.from_type("directory")
        super().__init__()

    def changed_properties(self):
        pass

    def create(self, ctx):
        op = ctx.operation("create", self.resource)
        props = self.resource["properties"]
        op.command("mkdir -f {dirname}".format(dirname=props["location"]))

    def update(self, ctx, changed_properties):
        op = ctx.operation("update", self.resource, "change permissions")
        props = self.resource["properties"]
        for prop in changed_properties:
            if prop == "location":
                op.command("chmod {permissions} {dirname}".format(props["location"], props["permissions"]))

    def delete(self, ctx):
        op = ctx.operation("delete", self.resource, "change permissions")
        props = self.resource["properties"]
        op.command("rm -fr {dirname}".format(props["location"]))


class File(ExecutableResource):
    def __init__(self, resource):
        self.resource=resource
        self.schema=schema.from_type("file")
        super().__init__()

    def create(self, ctx):
        op = ctx.operation("create", self.resource)
        props = self.resource["properties"]
        parent = ctx.get_ref(props["parent"])
        fullpath = os.path.join(parent["properties"]["location"], props["filename"])
        cmd = None
        if "text" in props:
            cmd = """echo << ENDOFFILE
{text}
ENDOFFILE > {fullpath}
""".format(text=props["text"], fullpath=fullpath)
        if "source" in props:
            cmd = "wget {source} {fullpath}".format(source=props["source"], fullpath=fullpath)
        if cmd is None:
            raise Exception("Internal error in File")
        op.command(cmd)

schemas = {
    "directory": lambda r: Directory(r),
    "file": lambda r: File(r)
}


def from_type(type):
    if type not in schemas:
        raise Exception("Internal error. Cannot find schema for type {type}".format(type))
    return schemas[type]

def execute(graph_repr):
    # sort the graph topologicall

    ctx = ScriptCtx(graph_repr)
    for repr in graph_repr.values():
        exec = from_type(repr["type"])(repr)
        exec.create(ctx)

    ctx.dump()