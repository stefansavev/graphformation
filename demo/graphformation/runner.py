import argparse
from graphformation import spec

parser = argparse.ArgumentParser()

parser.add_argument("-deploy", help="Name of the file which to deploy", action="store_true")
parser.add_argument("-state-file", help="Name of the state file", default="state.json")
parser.add_argument("-dry-run", help="Do not run. Only output the change set", default=False)


parser.add_argument("-show-json", help="Shows the json representation of the program", action="store_true")


def run():
    args = parser.parse_args()
    if args.deploy:
        print(args.deploy)
        print(args.statefile)
        print(args.dryrun)
    elif args.show_json:
        spec.dump_graph()
    else:
        print("No arguments have been specified. Run with -h and read the help.")

