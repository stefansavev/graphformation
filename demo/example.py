from graphformation import *

mydir=directory(
  id="dir",
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

#dump_graph()
execute("/tmp/state.txt")
