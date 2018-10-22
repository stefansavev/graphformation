from graphformation.spec import *
from graphformation import runner

mydir=directory(
  id="dir",
  permissions="777",
  location="/tmp/mydirectory"
)

file(
   id="contentfile",
   filename="file1",
   parent=ref(mydir),
   text="Lorem ipsum dolor"
)


file(
   id="downloadedfile",
   filename="file2",
   parent=ref(mydir),
   source="https://webserver.com/file2.txt"
)


if __name__ == "__main__":
    runner.run()
