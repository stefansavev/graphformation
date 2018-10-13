from graphformation.spec import *
from graphformation import runner


def test_no_change():
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

    state0, exec0=capture(lambda: p1(), {})
    state1, exec1=capture(lambda: p2(), state0)
    assert(exec1.stri() == "")


def test_prop_change():
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

    state0, exec0=capture(lambda: p1(), {})
    state1, exec1=capture(lambda: p2(), state0)
    expected_exec1 = """
"""
    assert(exec1 == expected_exec1)

def ignore():
    print("State 0")
    print("--------------------------")
    print(json.dumps(state0, indent=2))
    print("--------------------------")
    print(exec0)
    print("--------------------------")

    print("\n\n")
    print("State 1")
    print("--------------------------")
    print(json.dumps(state1, indent=2))
    print("--------------------------")
    print(exec1)
    print("--------------------------")

    # if __name__ == "__main__":
    #    runner.run()
