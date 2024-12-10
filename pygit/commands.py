import os
import sys
import textwrap
from . import base
from . import data
from . import diff
from . import remote

def init(args):
    print("Starting initialization...")
    base.init()
    print(f'Initialized empty pygit repository in {os.getcwd()}/{data.GIT_DIR}')
    print("Initialization complete")

def hash_object(args):
    with open(args.file, 'rb') as f:
        print(data.hash_object(f.read()))

def cat_file(args):
    sys.stdout.flush()
    sys.stdout.buffer.write(data.get_object(args.object, expected=None))

def write_tree(args):
    print(base.write_tree())

def read_tree(args):
    base.read_tree(args.tree)

def commit(args):
    print(base.commit(args.message))

def checkout(args):
    base.checkout(args.commit)

def tag(args):
    base.create_tag(args.name, args.oid)

def branch(args):
    if not args.name:
        current = base.get_branch_name()
        for branch in base.iter_branch_names():
            prefix = '*' if branch == current else ' '
            print(f'{prefix} {branch}')
    else:
        base.create_branch(args.name, args.start_point)
        print(f'Branch {args.name} created at {args.start_point[:10]}')

# ... other command handlers ... 