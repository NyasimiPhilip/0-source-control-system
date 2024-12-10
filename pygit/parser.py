"""Command-line argument parsing for PyGit."""

import argparse
from . import base
from . import commands

def create_parser():
    """Create and return the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description='PyGit: A lightweight implementation of Git in Python'
    )
    commands_parser = parser.add_subparsers(dest='command', help='Available commands')
    commands_parser.required = True
    _add_basic_commands(commands_parser)
    _add_branch_commands(commands_parser)
    _add_remote_commands(commands_parser)
    _add_plumbing_commands(commands_parser)
    return parser

def _add_basic_commands(commands_parser):
    """Add basic Git commands like init, add, commit, status, and log."""
    # Init
    init_parser = commands_parser.add_parser('init', help='Initialize a new repository')
    init_parser.set_defaults(func=commands.init)

    # Add
    add_parser = commands_parser.add_parser('add', help='Add file contents to the index')
    add_parser.set_defaults(func=commands.add)
    add_parser.add_argument('files', nargs='+', help='Files to add')

    # Commit
    commit_parser = commands_parser.add_parser('commit', help='Create a new commit')
    commit_parser.set_defaults(func=commands.commit)
    commit_parser.add_argument('-m', '--message', required=True, help='Commit message')

    # Add diff command
    diff_parser = commands_parser.add_parser('diff', help='Show changes between commits')
    diff_parser.set_defaults(func=commands.diff)
    diff_parser.add_argument('--cached', action='store_true', help='Show staged changes')
    diff_parser.add_argument('commit', nargs='?', help='Commit to diff against')

    # Status
    status_parser = commands_parser.add_parser('status', help='Show working tree status')
    status_parser.set_defaults(func=commands.status)

    # Log
    log_parser = commands_parser.add_parser('log', help='Show commit history')
    log_parser.set_defaults(func=commands.log)
    log_parser.add_argument('oid', default='@', type=base.get_oid, nargs='?')

def _add_branch_commands(commands_parser):
    """Add branch-related commands like branch, checkout, and merge."""
    # Branch
    branch_parser = commands_parser.add_parser('branch', help='List or create branches')
    branch_parser.set_defaults(func=commands.branch)
    branch_parser.add_argument('name', nargs='?', help='Branch name')
    branch_parser.add_argument('start_point', default='@', type=base.get_oid, nargs='?')

    # Checkout
    checkout_parser = commands_parser.add_parser('checkout', help='Switch branches or restore files')
    checkout_parser.set_defaults(func=commands.checkout)
    checkout_parser.add_argument('commit', help='Commit or branch to checkout')

    # Merge
    merge_parser = commands_parser.add_parser('merge', help='Join two development histories')
    merge_parser.set_defaults(func=commands.merge)
    merge_parser.add_argument('commit', type=base.get_oid, help='Commit to merge')

def _add_remote_commands(commands_parser):
    """Add remote operation commands like clone, fetch, and push."""
    # Clone
    clone_parser = commands_parser.add_parser('clone', help='Clone a repository')
    clone_parser.set_defaults(func=commands.clone)
    clone_parser.add_argument('remote', help='Remote repository to clone')
    clone_parser.add_argument('target', help='Target directory')

    # Fetch
    fetch_parser = commands_parser.add_parser('fetch', help='Download objects from remote')
    fetch_parser.set_defaults(func=commands.fetch)
    fetch_parser.add_argument('remote', help='Path to remote repository')

    # Push
    push_parser = commands_parser.add_parser('push', help='Update remote refs and objects')
    push_parser.set_defaults(func=commands.push)
    push_parser.add_argument('remote', help='Remote repository path')
    push_parser.add_argument('branch', help='Branch to push')

def _add_plumbing_commands(commands_parser):
    """Add low-level plumbing commands like hash-object and cat-file."""
    # Hash-object
    hash_object_parser = commands_parser.add_parser('hash-object', help='Compute object hash')
    hash_object_parser.set_defaults(func=commands.hash_object)
    hash_object_parser.add_argument('file', help='File to hash')

    # Cat-file
    cat_file_parser = commands_parser.add_parser('cat-file', help='Display object contents')
    cat_file_parser.set_defaults(func=commands.cat_file)
    cat_file_parser.add_argument('object', type=base.get_oid, help='Object to display')

def _add_visualization_commands(commands_parser):
    # Visualize commit graph
    k_parser = commands_parser.add_parser('k', help='Visualize commit graph')
    k_parser.set_defaults(func=commands.k) 