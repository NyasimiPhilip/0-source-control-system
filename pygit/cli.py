import argparse
import os
import sys
import textwrap
import subprocess

from . import diff
from . import base
from . import data
from . import remote


def main():
    print("ugit CLI started")
    with data.change_git_dir('.'):
        args = parse_args()
        args.func(args)


def parse_args():
    parser = argparse.ArgumentParser(
        description='ugit: A lightweight implementation of Git in Python'
    )

    commands = parser.add_subparsers(dest='command', help='Available commands')
    commands.required = True

    oid = base.get_oid

    init_parser = commands.add_parser('init', help='Initialize a new repository')
    init_parser.set_defaults(func=init)

    hash_object_parser = commands.add_parser('hash-object', help='Compute object hash')
    hash_object_parser.set_defaults(func=hash_object)
    hash_object_parser.add_argument('file', help='File to hash')

    cat_file_parser = commands.add_parser('cat-file', help='Display object contents')
    cat_file_parser.set_defaults(func=cat_file)
    cat_file_parser.add_argument('object', type=oid, help='Object to display')

    write_tree_parser = commands.add_parser('write-tree', help='Create a tree object')
    write_tree_parser.set_defaults(func=write_tree)

    read_tree_parser = commands.add_parser('read-tree', help='Read a tree object')
    read_tree_parser.set_defaults(func=read_tree)
    read_tree_parser.add_argument('tree', type=oid, help='Tree to read')

    commit_parser = commands.add_parser('commit', help='Create a new commit')
    commit_parser.set_defaults(func=commit)
    commit_parser.add_argument('-m', '--message', required=True, help='Commit message')

    log_parser = commands.add_parser('log', help='Show commit history')
    log_parser.set_defaults(func=log)
    log_parser.add_argument('oid', default='@', type=oid, nargs='?', help='Commit to start from')

    show_parser = commands.add_parser('show', help='Show commit details')
    show_parser.set_defaults(func=show)
    show_parser.add_argument('oid', default='@', type=oid, nargs='?', help='Commit to show')

    diff_parser = commands.add_parser('diff', help='Show changes between commits')
    diff_parser.set_defaults(func=_diff)
    diff_parser.add_argument('--cached', action='store_true', help='Show changes staged for commit')
    diff_parser.add_argument('commit', nargs='?', help='Commit to diff against')

    checkout_parser = commands.add_parser('checkout', help='Switch branches or restore files')
    checkout_parser.set_defaults(func=checkout)
    checkout_parser.add_argument('commit', help='Commit or branch to checkout')

    tag_parser = commands.add_parser('tag', help='Create a new tag')
    tag_parser.set_defaults(func=tag)
    tag_parser.add_argument('name', help='Tag name')
    tag_parser.add_argument('oid', default='@', type=oid, nargs='?', help='Object to tag')

    branch_parser = commands.add_parser('branch', help='List or create branches')
    branch_parser.set_defaults(func=branch)
    branch_parser.add_argument('name', nargs='?', help='Branch name')
    branch_parser.add_argument('start_point', default='@', type=oid, nargs='?', help='Start point for the branch')

    k_parser = commands.add_parser('k', help='Visualize commit history')
    k_parser.set_defaults(func=k)

    status_parser = commands.add_parser('status', help='Show working tree status')
    status_parser.set_defaults(func=status)

    reset_parser = commands.add_parser('reset', help='Reset current HEAD to the specified state')
    reset_parser.set_defaults(func=reset)
    reset_parser.add_argument('commit', type=oid, help='Commit to reset to')

    merge_parser = commands.add_parser('merge', help='Join two or more development histories')
    merge_parser.set_defaults(func=merge)
    merge_parser.add_argument('commit', type=oid, help='Commit to merge into the current branch')

    merge_base_parser = commands.add_parser('merge-base', help='Find best common ancestor of two commits')
    merge_base_parser.set_defaults(func=merge_base)
    merge_base_parser.add_argument('commit1', type=oid, help='First commit')
    merge_base_parser.add_argument('commit2', type=oid, help='Second commit')

    fetch_parser = commands.add_parser('fetch', help='Download objects and refs from another repository')
    fetch_parser.set_defaults(func=fetch)
    fetch_parser.add_argument('remote', help='Remote repository to fetch from')

    push_parser = commands.add_parser('push', help='Update remote refs along with associated objects')
    push_parser.set_defaults(func=push)
    push_parser.add_argument('remote', help='Remote repository to push to')
    push_parser.add_argument('branch', help='Branch to push')

    add_parser = commands.add_parser('add', help='Add file contents to the index')
    add_parser.set_defaults(func=add)
    add_parser.add_argument('files', nargs='+', help='Files to add')

    clone_parser = commands.add_parser('clone', help='Clone a repository into a new directory')
    clone_parser.set_defaults(func=clone)
    clone_parser.add_argument('remote', help='Remote repository to clone')
    clone_parser.add_argument('target', help='Target directory for the clone')

    return parser.parse_args()


def init(args):
    print("Starting initialization...")
    base.init()
    print(f'Initialized empty ugit repository in {os.getcwd()}/{data.GIT_DIR}')
    print("Initialization complete")

def hash_object (args):
    with open (args.file, 'rb') as f:
        print (data.hash_object (f.read ()))

def cat_file (args):
    sys.stdout.flush ()
    sys.stdout.buffer.write (data.get_object (args.object, expected = None))

def write_tree (args):
    print(base.write_tree ())

def read_tree (args):
    base.read_tree (args.tree)

def commit (args):
    print(base.commit(args.message))

def _print_commit (oid, commit, refs=None):
    refs_str = f' ({", ".join (refs)})' if refs else ''
    print (f'commit {oid}{refs_str}\n')
    print (textwrap.indent (commit.message, '    '))
    print ('')


def log (args):
    refs = {}
    for refname, ref in data.iter_refs ():
        refs.setdefault (ref.value, []).append (refname)

    for oid in base.iter_commits_and_parents ({args.oid}):
        commit = base.get_commit (oid)
        _print_commit (oid, commit, refs.get (oid))

def show (args):
    if not args.oid:
        return
    commit = base.get_commit (args.oid)
    parent_tree = None
    if commit.parents:
        parent_tree = base.get_commit (commit.parents[0]).tree

    _print_commit (args.oid, commit)
    result = diff.diff_trees (
        base.get_tree (parent_tree), base.get_tree (commit.tree))
    sys.stdout.flush ()
    sys.stdout.buffer.write (result)

def _diff (args):
    oid = args.commit and base.get_oid (args.commit)

    if args.commit:
        # If a commit was provided explicitly, diff from it
        tree_from = base.get_tree (oid and base.get_commit (oid).tree)

    if args.cached:
        tree_to = base.get_index_tree ()
        if not args.commit:
            # If no commit was provided, diff from HEAD
            oid = base.get_oid ('@')
            tree_from = base.get_tree (oid and base.get_commit (oid).tree)
    else:
        tree_to = base.get_working_tree ()
        if not args.commit:
            # If no commit was provided, diff from index
            tree_from = base.get_index_tree ()

    result = diff.diff_trees (tree_from, tree_to)
    sys.stdout.flush ()
    sys.stdout.buffer.write (result)

def checkout(args):
    base.checkout (args.commit)

def tag (args):
    base.create_tag (args.name, args.oid)


def branch (args):
    if not args.name:
        current = base.get_branch_name ()
        for branch in base.iter_branch_names ():
            prefix = '*' if branch == current else ' '
            print (f'{prefix} {branch}')
    else:
        base.create_branch (args.name, args.start_point)
        print (f'Branch {args.name} created at {args.start_point[:10]}')


def k (args):
    dot = 'digraph commits {\n'

    oids = set ()
    for refname, ref in data.iter_refs (deref=False):
        dot += f'"{refname}" [shape=note]\n'
        dot += f'"{refname}" -> "{ref.value}"\n'
        if not ref.symbolic:
            oids.add (ref.value)

    for oid in base.iter_commits_and_parents (oids):
        commit = base.get_commit (oid)
        dot += f'"{oid}" [shape=box style=filled label="{oid[:10]}"]\n'
        for parent in commit.parents:
            dot += f'"{oid}" -> "{parent}"\n'
    dot += '}'
    print (dot)

    with subprocess.Popen (
            ['dot', '-Tgtk', '/dev/stdin'],
            stdin=subprocess.PIPE) as proc:
        proc.communicate (dot.encode ())

def status (args):
    HEAD = base.get_oid ('@')
    branch = base.get_branch_name ()
    if branch:
        print (f'On branch {branch}')
    else:
        print (f'HEAD detached at {HEAD[:10]}')

    MERGE_HEAD = data.get_ref ('MERGE_HEAD').value
    if MERGE_HEAD:
        print (f'Merging with {MERGE_HEAD[:10]}')

    print ('\nChanges to be committed:\n')
    HEAD_tree = HEAD and base.get_commit (HEAD).tree
    for path, action in diff.iter_changed_files (base.get_tree (HEAD_tree),
                                                 base.get_index_tree ()):
        print (f'{action:>12}: {path}')

    print ('\nChanges not staged for commit:\n')
    for path, action in diff.iter_changed_files (base.get_index_tree (),
                                                 base.get_working_tree ()):
        print (f'{action:>12}: {path}')



def reset (args):
    base.reset (args.commit)

def merge (args):
    base.merge (args.commit)

def merge_base (args):
    print (base.get_merge_base (args.commit1, args.commit2))

def fetch (args):
    remote.fetch (args.remote)

def push (args):
    remote.push (args.remote, f'refs/heads/{args.branch}')

def add (args):
    base.add (args.files)

def clone(args):
    remote.clone(args.remote, args.target)

if __name__ == '__main__':
    main()