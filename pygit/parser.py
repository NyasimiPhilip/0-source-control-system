import argparse
from . import base
from . import commands

def create_parser():
    parser = argparse.ArgumentParser(
        description='pygit: A lightweight implementation of Git in Python'
    )

    commands_parser = parser.add_subparsers(dest='command', help='Available commands')
    commands_parser.required = True

    # Basic commands
    _add_basic_commands(commands_parser)
    
    # Branch and merge commands
    _add_branch_commands(commands_parser)
    
    # Remote commands
    _add_remote_commands(commands_parser)

    return parser

def _add_basic_commands(commands):
    # Init
    init_parser = commands.add_parser('init', help='Initialize a new repository')
    init_parser.set_defaults(func=commands.init)

    # Add
    add_parser = commands.add_parser('add', help='Add file contents to the index')
    add_parser.set_defaults(func=commands.add)
    add_parser.add_argument('files', nargs='+', help='Files to add')

    # Commit
    commit_parser = commands.add_parser('commit', help='Create a new commit')
    commit_parser.set_defaults(func=commands.commit)
    commit_parser.add_argument('-m', '--message', required=True, help='Commit message')

    # ... other basic commands ...

def _add_branch_commands(commands):
    # Branch
    branch_parser = commands.add_parser('branch', help='List or create branches')
    branch_parser.set_defaults(func=commands.branch)
    branch_parser.add_argument('name', nargs='?', help='Branch name')
    branch_parser.add_argument('start_point', default='@', type=base.get_oid, nargs='?')

    # ... other branch commands ...

def _add_remote_commands(commands):
    # Clone
    clone_parser = commands.add_parser('clone', help='Clone a repository')
    clone_parser.set_defaults(func=commands.clone)
    clone_parser.add_argument('remote', help='Remote repository to clone')
    clone_parser.add_argument('target', help='Target directory')

    # ... other remote commands ... 