from graphformation.spec import *

"""
We simutate running two version of the program

In version 1 we setup the infrastructure
In version 2 we modify the infrastructure

Because this library was designed with a global state, we 
had to introduce a new function, execute_change_program which leaves
the global state as it has found it.

Each test has two programs:
p1(): gives the initial infrastructure
p2(): gives the modified infrastructure

both programs return the new state and the "operations" than have to be executed
to bring the environment into the desired state

"""

def test_no_change():
    """
    If we run the same program again, there should be not change detected
    """
    def p1():
        directory(
          id="dir",
          permissions="777",
          location="/tmp/mydirectory"
        )

    def p2():
        directory(
            id="dir",
            permissions="777",
            location="/tmp/mydirectory"
        )

    state0, exec0=execute_change_program(lambda: p1(), {})
    state1, exec1=execute_change_program(lambda: p2(), state0)
    assert(exec1.strip() == "")


def test_prop_change():
    """
    If we change a single property (here permission), an update command should be executed
    """
    def p1():
        directory(
          id="dir",
          permissions="777",
          location="/tmp/mydirectory"
        )

    def p2():
        directory(
            id="dir",
            permissions="770",
            location="/tmp/mydirectory"
        )

    state0, exec0=execute_change_program(lambda: p1(), {})
    state1, exec1=execute_change_program(lambda: p2(), state0)

    expected_exec1 = """
# update directory dir
chmod 770 /tmp/mydirectory 
# end
    """
    assert(exec1.strip() == expected_exec1.strip())


def test_remove_resource():
    """
    we test deletion of a resource
    """
    def p1():
        directory(
          id="dir",
          permissions="777",
          location="/tmp/mydirectory"
        )

    def p2():
        pass

    state0, exec0=execute_change_program(lambda: p1(), {})
    state1, exec1=execute_change_program(lambda: p2(), state0)

    expected_exec1 = """
# delete directory dir
rm -fr /tmp/mydirectory 
# end
    """
    assert(exec1.strip() == expected_exec1.strip())


def test_add_new_resource():
    """
    we test adding a new resource
    """
    def p1():
        directory(
          id="dir",
          permissions="777",
          location="/tmp/mydirectory"
        )

    def p2():
        directory(
          id="dir",
          permissions="777",
          location="/tmp/mydirectory"
        )
        directory(
          id="another_dir",
          permissions="777",
          location="/tmp/another_directory"
        )
    state0, exec0=execute_change_program(lambda: p1(), {})
    state1, exec1=execute_change_program(lambda: p2(), state0)
    with open('/tmp/f4.txt', 'w') as f:
        f.write(exec1)
    expected_exec1 = """
# create directory another_dir
mkdir -f /tmp/another_directory 
# end
    """
    assert(exec1.strip() == expected_exec1.strip())


def test_change_ref_property():
    """
    we test changing a property
    """
    def p1():
        dir1 = directory(
          id="dir",
          permissions="777",
          location="/tmp/mydirectory"
        )

        directory(
          id="another_dir",
          permissions="777",
          location="/tmp/another_directory"
        )

        file(
            id="contentfile",
            filename="file1",
            parent=ref(dir1),
            text="Lorem ipsum dolor"
        )

    def p2():
        directory(
          id="dir",
          permissions="777",
          location="/tmp/mydirectory"
        )

        dir2 = directory(
          id="another_dir",
          permissions="777",
          location="/tmp/another_directory"
        )

        file(
            id="contentfile",
            filename="file1",
            parent=ref(dir2),
            text="Lorem ipsum dolor"
        )


    state0, exec0=execute_change_program(lambda: p1(), {})
    state1, exec1=execute_change_program(lambda: p2(), state0)

    expected_exec1="""
# delete file contentfile
rm -f /tmp/mydirectory/file1 
# end


# create file contentfile
echo << ENDOFFILE
Lorem ipsum dolor
ENDOFFILE > /tmp/another_directory/file1
 
# end
    """

    assert(exec1.strip() == expected_exec1.strip())


def test_swap_two_mutable_references():
    """
    we test swapping two mutable references. in this case no objects have to be re-created
    """
    def p1():
        r1 = dummy_ref_resource(
            id="resource1",
        )

        dummy_ref_resource(
            id="resource2",
            mutable_parent=ref(r1)
        )

    def p2():
        r2 = dummy_ref_resource(
            id="resource2",
        )

        dummy_ref_resource(
            id="resource1",
            mutable_parent=ref(r2)
        )

    state0, exec0 = execute_change_program(lambda: p1(), {})
    state1, exec1 = execute_change_program(lambda: p2(), state0)

    expected_exec1 = """
# update dummy_ref_resource resource2
echo update: [{"new_value": null, "old_value": {"!ref": "resource1"}, "property": "mutable_parent"}] 
# end


# update dummy_ref_resource resource1
echo update: [{"new_value": {"!ref": "resource2"}, "old_value": null, "property": "mutable_parent"}] 
# end
    """
    assert (exec1.strip() == expected_exec1.strip())


def test_swap_two_immutable_references():
    """
    we test swapping two immutable references. in this case objects need to be re-created
    """
    def p1():
        r1 = dummy_ref_resource(
            id="resource1",
        )

        dummy_ref_resource(
            id="resource2",
            immutable_parent=ref(r1)
        )

    def p2():
        r2 = dummy_ref_resource(
            id="resource2",
        )

        dummy_ref_resource(
            id="resource1",
            immutable_parent=ref(r2)
        )

    state0, exec0 = execute_change_program(lambda: p1(), {})
    state1, exec1 = execute_change_program(lambda: p2(), state0)

    with open('/tmp/f10.txt', 'w') as f:
        f.write(exec1)

    expected_exec1 = """
# delete dummy_ref_resource resource2
echo delete: {"computed_props": {}, "id": "resource2", "properties": {"immutable_parent": {"!ref": "resource1"}}, "status": "created", "type": "dummy_ref_resource"} 
# end


# delete dummy_ref_resource resource1
echo delete: {"computed_props": {}, "id": "resource1", "properties": {}, "status": "created", "type": "dummy_ref_resource"} 
# end


# create dummy_ref_resource resource2
echo create: {"id": "resource2", "properties": {}, "type": "dummy_ref_resource"} 
# end


# create dummy_ref_resource resource1
echo create: {"id": "resource1", "properties": {"immutable_parent": {"!ref": "resource2"}}, "type": "dummy_ref_resource"} 
# end
    """
    assert (exec1.strip() == expected_exec1.strip())