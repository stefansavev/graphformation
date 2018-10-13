import json, os
from graphformation import schema
from toposort import toposort, toposort_flatten

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
        id = ref.get("!ref")
        if id is None:
            raise Exception("Internal error. Expected reference, found {}".format(json.format(ref)))
        return self.repr[id]

    def dump(self):
        r = "\n".join(map(lambda x: x.dump(2), self.operations))
        print(r)

    def dump_str(self):
        r = "\n".join(map(lambda x: x.dump(2), self.operations))
        return r


class ExecutableResource(object):
    def __init__(self, resource):
        self.resource=resource

    def update_status(self, status, computed_props):
        self.resource["status"] = status
        self.resource["computed_props"] = computed_props

class Directory(ExecutableResource):
    def __init__(self, resource):
        self.schema = schema.from_type("directory")
        super().__init__(resource)

    def create(self, ctx):
        op = ctx.operation("create", self.resource)
        props = self.resource["properties"]
        op.command("mkdir -f {dirname}".format(dirname=props["location"]))
        self.update_status("created", {})

    def requires_recreate(self, ctx, old_resource):
        # TODO
        # yes, if the resource name has been changed
        changed_props = _resource_diff(self.resource, old_resource)
        yes = "location" in changed_props
        return yes

    def update(self, ctx, changed_properties):
        op = ctx.operation("update", self.resource, "change permissions")
        props = self.resource["properties"]
        for prop in changed_properties:
            if prop == "permissions":
                print(props)
                op.command("chmod {permissions} {dirname}".format(dirname=props["location"], permissions=props["permissions"]))
        self.update_status("updated", {})


    def delete(self, ctx):
        op = ctx.operation("delete", self.resource, "change permissions")
        props = self.resource["properties"]
        op.command("rm -fr {dirname}".format(dirname=props["location"]))
        self.update_status("deleted", {})


class File(ExecutableResource):
    def __init__(self, resource):
        self.resource=resource
        self.schema=schema.from_type("file")
        super().__init__(resource)

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
        self.update_status("created", {})

    def requires_recreate(self, ctx, new_obj, old_obj):
        return True

    def update(self, ctx):
        raise Exception("This resource always require recreate")

    def delete(self, ctx):
        op = ctx.operation("delete", self.resource)
        props = self.resource["properties"]
        parent = ctx.get_ref(props["parent"])
        fullpath = os.path.join(parent["properties"]["location"], props["filename"])
        cmd = "rm -f {fullpath}".format(fullpath=fullpath)
        op.command(cmd)
        self.update_status("deleted", {})


schemas = {
    "directory": lambda r: Directory(r),
    "file": lambda r: File(r)
}


def from_type(type):
    if type not in schemas:
        raise Exception("Internal error. Cannot find schema for type {type}".format(type))
    return schemas[type]


def _read_state(filename):
    if not os.path.isfile(filename):
        return {}
    with open(filename, 'r') as f:
        contents = f.read()
    return json.loads(contents)


def _resource_diff(new_resource, old_resource):
    old_properties, new_properties = old_resource['properties'], new_resource['properties']
    all_properties = set(old_properties).union(set(new_properties))
    diff_props = []
    for prop in all_properties:
        old_value = old_resource['properties'].get(prop, None)
        new_value = new_resource['properties'].get(prop, None)
        print(prop, old_value, new_value)
        if old_value != new_value:
            diff_props.append(prop)
    return diff_props


def _diff(ctx, new_state, old_state):
    new_keys = set(new_state.keys())
    old_keys = set(old_state.keys())
    inserted = list(new_keys.difference(old_keys))
    deleted = list(old_keys.difference(new_keys))
    modified_candidates = new_keys.intersection(old_keys)

    while True:
        modified = []
        for m in modified_candidates:
            if len(_resource_diff(new_state[m], old_state[m])) > 0:
                modified.append(m)

        # we need to figure which updates will be handled via delete/create and which in-place
        must_be_recreated = [] # then we have to trigger updates, and this may force others to get re-created

        new_modified = []
        for m in modified:
            new_obj = new_state[m]
            old_obj = old_state[m]
            if new_obj['type'] != old_obj['type']:
                must_be_recreated.append(m)
                continue
            assert new_obj['type'] == old_obj['type']
            exec = from_type(new_obj['type'])(new_obj)
            if exec.requires_recreate(ctx, old_obj):
                must_be_recreated.append(m)
                continue
            new_modified.append(m)

        if len(modified) == len(new_modified):
            break
        modified_candidates = new_modified

        for m in must_be_recreated:
            inserted.append(m)
            deleted.append(m)

    inserted = set(inserted)
    deleted = set(deleted)
    actually_modified = []

    for k in new_keys.union(old_keys):
        if k not in inserted and k not in deleted:
            actually_modified.append(k)

    return {
        "created": inserted,
        "deleted": deleted,
        "modified": modified
    }


# for the modified ones we need to find out which can be modified without destroying them
def topological_sort(graph):
    items = {}
    for key, item in graph.items():
        sources = []
        for value in graph[key]['properties'].values():
            if isinstance(value, dict) and '!ref' in value:
                ref = value['!ref']
                sources.append(ref)
        items[key] = set(sources)
    return list(toposort(items))


def execute(filename, graph_repr):
    # TODO: sort the graph topologically

    sorted_new_keys = topological_sort(graph_repr)
    # TODO:
    if isinstance(filename, str):
        old_state = _read_state(filename)
    else:
        old_state=filename
    sorted_old_keys = topological_sort(old_state)
    ctx = ScriptCtx(graph_repr)
    diff = _diff(ctx, graph_repr, old_state)
    deleted = 0
    for key_group in sorted_old_keys[::-1]:
        for key in key_group:
            if key in diff['deleted']:
                repr = old_state[key]
                exec = from_type(repr["type"])(repr)
                exec.delete(ctx)
                deleted += 1

    created = 0
    for key_group in sorted_new_keys:
        for key in key_group:
            if key in diff['created']:
                repr = graph_repr[key]
                exec = from_type(repr["type"])(repr)
                exec.create(ctx)
                created += 1

    modified = 0
    for key_group in sorted_new_keys:
        for key in key_group:
            if key in diff['modified']:
                repr = graph_repr[key]
                exec = from_type(repr["type"])(repr)
                changed_props = _resource_diff(graph_repr[key], old_state[key])
                exec.update(ctx, changed_props)
                modified += 1

    print("{deleted} deleted".format(deleted=deleted))
    print("{created} created".format(created=created))
    print("{modified} modified".format(modified=modified))

    return graph_repr, ctx.dump_str()
    # TODO
    #ctx.dump()
    #with open(filename, 'w') as f:
    #    f.write(json.dumps(graph_repr, indent=2))
