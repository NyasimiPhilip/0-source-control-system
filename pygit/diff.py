from collections import defaultdict
import os
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

def is_text_file(path):
    """Check if a file is a text file based on extension"""
    text_extensions = {
        '.txt', '.md', '.py', '.js', '.css', '.html', '.json', 
        '.yml', '.yaml', '.xml', '.csv', '.ini', '.conf',
        '.sh', '.bat', '.ps1', '.c', '.cpp', '.h', '.java',
        '.rb', '.php', '.pl', '.sql', '.go', '.rs', '.ts'
    }
    return os.path.splitext(path)[1].lower() in text_extensions

def diff_trees(t_from, t_to):
    """Show detailed changes between two trees"""
    output = []
    
    for path, o_from, o_to in compare_trees(t_from, t_to):
        if o_from != o_to:
            # Add file header
            output.append(f"\nFile: {path}")
            output.append("=" * (len(path) + 6))
            
            # Skip binary files
            if not is_text_file(path):
                output.append("Binary file")
                continue
                
            # Get file contents
            old_content = data.get_object(o_from).decode('utf-8', errors='replace') if o_from else ""
            new_content = data.get_object(o_to).decode('utf-8', errors='replace') if o_to else ""
            
            # Show changes
            if not o_from:
                output.append("New file added:")
                output.append("+++ New content")
                output.extend("+ " + line for line in new_content.splitlines())
            elif not o_to:
                output.append("File deleted:")
                output.append("--- Previous content")
                output.extend("- " + line for line in old_content.splitlines())
            else:
                output.append("File modified:")
                old_lines = old_content.splitlines()
                new_lines = new_content.splitlines()
                
                # Show side-by-side diff
                max_lines = max(len(old_lines), len(new_lines))
                output.append("-" * 40 + "|" + "-" * 40)
                output.append("Previous Content".ljust(40) + "|" + "New Content".ljust(40))
                output.append("-" * 40 + "|" + "-" * 40)
                
                for i in range(max_lines):
                    old_line = old_lines[i] if i < len(old_lines) else ""
                    new_line = new_lines[i] if i < len(new_lines) else ""
                    if old_line != new_line:
                        output.append(f"{old_line:<40}|{new_line:<40}  <")
                    else:
                        output.append(f"{old_line:<40}|{new_line:<40}")
                
                output.append("-" * 40 + "|" + "-" * 40)
            
            output.append("\n")
    
    return "\n".join(output).encode()

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

