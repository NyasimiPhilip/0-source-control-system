from collections import defaultdict
import subprocess
from tempfile import NamedTemporaryFile as Temp
from . import data

def compare_trees(*trees):
    entries = defaultdict(lambda: [None] * len(trees))
    for i, tree in enumerate(trees):
        for path, oid in tree.items():
            entries[path][i] = oid

    for path, oids in entries.items():
        yield (path, *oids)

def iter_changed_files(t_from, t_to):
    """Iterate through changed files between two trees"""
    for path, o_from, o_to in compare_trees(t_from, t_to):
        if o_from != o_to:
            action = ('new file' if not o_from else
                     'deleted' if not o_to else
                     'modified')
            yield path, action

def diff_trees(t_from, t_to):
    """Generate a diff between two trees"""
    output = b''
    for path, o_from, o_to in compare_trees(t_from, t_to):
        if o_from != o_to:
            output += create_diff(o_from, o_to, path)
    return output

def create_diff(o_from, o_to, path='blob'):
    """Create a diff between two blobs without using external diff command"""
    def get_content(oid):
        if not oid:
            return []
        try:
            # Try to decode as text
            return data.get_object(oid).decode().splitlines()
        except UnicodeDecodeError:
            # If binary file, just return a message
            return ["Binary file"]

    # Get content of both versions
    from_lines = get_content(o_from)
    to_lines = get_content(o_to)

    # Create diff header
    output = []
    output.append(f'diff --git a/{path} b/{path}'.encode())
    
    # If either file is binary, just show a message
    if from_lines == ["Binary file"] or to_lines == ["Binary file"]:
        output.append(b"Binary files differ")
        return b'\n'.join(output) + b'\n'

    if not o_from:
        output.append(f'--- /dev/null'.encode())
    else:
        output.append(f'--- a/{path}'.encode())
    
    if not o_to:
        output.append(f'+++ /dev/null'.encode())
    else:
        output.append(f'+++ b/{path}'.encode())

    # Simple diff implementation
    from_idx = 0
    to_idx = 0
    
    while from_idx < len(from_lines) or to_idx < len(to_lines):
        if from_idx >= len(from_lines):
            # Rest of the lines are additions
            output.append(f'+{to_lines[to_idx]}'.encode())
            to_idx += 1
        elif to_idx >= len(to_lines):
            # Rest of the lines are deletions
            output.append(f'-{from_lines[from_idx]}'.encode())
            from_idx += 1
        elif from_lines[from_idx] == to_lines[to_idx]:
            # Lines are the same
            output.append(f' {from_lines[from_idx]}'.encode())
            from_idx += 1
            to_idx += 1
        else:
            # Lines are different
            output.append(f'-{from_lines[from_idx]}'.encode())
            output.append(f'+{to_lines[to_idx]}'.encode())
            from_idx += 1
            to_idx += 1

    return b'\n'.join(output) + b'\n'

def merge_trees(t_base, t_HEAD, t_other):
    """Merge three trees and return the merged tree"""
    tree = {}
    for path, o_base, o_HEAD, o_other in compare_trees(t_base, t_HEAD, t_other):
        tree[path] = data.hash_object(merge_blobs(o_base, o_HEAD, o_other))
    return tree

def merge_blobs(o_base, o_HEAD, o_other):
    """Simple merge strategy: take the changed version"""
    if o_HEAD == o_other:
        return data.get_object(o_HEAD)
    elif o_base == o_HEAD:
        return data.get_object(o_other)
    elif o_base == o_other:
        return data.get_object(o_HEAD)
    else:
        # Conflict - take HEAD version but indicate conflict
        content = data.get_object(o_HEAD)
        return b'<<<<<<< HEAD\n' + content + b'\n=======\n' + data.get_object(o_other) + b'\n>>>>>>>\n'

