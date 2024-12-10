import os
import sys
import textwrap
import subprocess
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

def _print_commit(oid, commit, refs=None):
    refs_str = f' ({", ".join(refs)})' if refs else ''
    print(f'commit {oid}{refs_str}\n')
    print(textwrap.indent(commit.message, '    '))
    print('')

def log(args):
    refs = {}
    for refname, ref in data.iter_refs():
        refs.setdefault(ref.value, []).append(refname)

    for oid in base.iter_commits_and_parents({args.oid}):
        commit = base.get_commit(oid)
        _print_commit(oid, commit, refs.get(oid))

def show(args):
    if not args.oid:
        return
    commit = base.get_commit(args.oid)
    parent_tree = None
    if commit.parents:
        parent_tree = base.get_commit(commit.parents[0]).tree

    _print_commit(args.oid, commit)
    result = diff.diff_trees(
        base.get_tree(parent_tree), base.get_tree(commit.tree))
    sys.stdout.flush()
    sys.stdout.buffer.write(result)

def diff(args):
    oid = args.commit and base.get_oid(args.commit)

    if args.commit:
        tree_from = base.get_tree(oid and base.get_commit(oid).tree)

    if args.cached:
        tree_to = base.get_index_tree()
        if not args.commit:
            oid = base.get_oid('@')
            tree_from = base.get_tree(oid and base.get_commit(oid).tree)
    else:
        tree_to = base.get_working_tree()
        if not args.commit:
            tree_from = base.get_index_tree()

    result = diff.diff_trees(tree_from, tree_to)
    sys.stdout.flush()
    sys.stdout.buffer.write(result)

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

def k(args):
    dot = 'digraph commits {\n'
    oids = set()
    
    for refname, ref in data.iter_refs(deref=False):
        dot += f'"{refname}" [shape=note]\n'
        dot += f'"{refname}" -> "{ref.value}"\n'
        if not ref.symbolic:
            oids.add(ref.value)

    for oid in base.iter_commits_and_parents(oids):
        commit = base.get_commit(oid)
        dot += f'"{oid}" [shape=box style=filled label="{oid[:10]}"]\n'
        for parent in commit.parents:
            dot += f'"{oid}" -> "{parent}"\n'
    dot += '}'
    print(dot)

    with subprocess.Popen(
            ['dot', '-Tgtk', '/dev/stdin'],
            stdin=subprocess.PIPE) as proc:
        proc.communicate(dot.encode())

def status(args):
    HEAD = base.get_oid('@')
    branch = base.get_branch_name()
    if branch:
        print(f'On branch {branch}')
    else:
        print(f'HEAD detached at {HEAD[:10]}')

    MERGE_HEAD = data.get_ref('MERGE_HEAD').value
    if MERGE_HEAD:
        print(f'Merging with {MERGE_HEAD[:10]}')

    print('\nChanges to be committed:\n')
    HEAD_tree = HEAD and base.get_commit(HEAD).tree
    for path, action in diff.iter_changed_files(base.get_tree(HEAD_tree),
                                              base.get_index_tree()):
        print(f'{action:>12}: {path}')

    print('\nChanges not staged for commit:\n')
    for path, action in diff.iter_changed_files(base.get_index_tree(),
                                              base.get_working_tree()):
        print(f'{action:>12}: {path}')

def reset(args):
    base.reset(args.commit)

def merge(args):
    base.merge(args.commit)

def merge_base(args):
    print(base.get_merge_base(args.commit1, args.commit2))

def fetch(args):
    remote.fetch(args.remote)

def push(args):
    remote.push(args.remote, f'refs/heads/{args.branch}')

def add(args):
    base.add(args.files)

def clone(args):
    remote.clone(args.remote, args.target)