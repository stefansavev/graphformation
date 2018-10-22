Graphformation
--------

This is a simple example how to use the library::

    >>> from graphformation.spec import *
    >>> from graphformation import runner
    >>> mydir=directory(
    >>>  id="dir",
    >>>  permissions="777",
    >>>  location="/tmp/mydirectory"
    >>> )
    >>> runner.run()
