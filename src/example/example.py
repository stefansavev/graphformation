# -*- coding: utf-8 -*-
"""Example

This module demonstrates how to write your own program in graphformation
"""

from graphformation.spec import directory, file, ref
from graphformation import runner

MY_DIR = directory(
    resource_id="dir",
    permissions="777",
    location="/tmp/mydirectory"
)

file(
    resource_id="contentfile",
    filename="file1",
    parent=ref(MY_DIR),
    text="Lorem ipsum dolor"
)

file(
    resource_id="downloadedfile",
    filename="file2",
    parent=ref(MY_DIR),
    source="https://webserver.com/file2.txt"
)

if __name__ == "__main__":
    runner.run()
