import os
import itertools
import operator
from collections import deque, namedtuple
import string

from . import diff
from . import data

def init ():
    """Initialize a new PyGit repository with required directories and HEAD reference."""
    print("Creating .pygit directory...")  # Debug print
    if not os.path.exists(data.GIT_DIR):
        os.makedirs(data.GIT_DIR)
        os.makedirs(f'{data.GIT_DIR}/objects', exist_ok=True)
    print("Setting up HEAD reference...")  # Debug print
    data.update_ref ('HEAD', data.RefValue (symbolic=True, value='refs/heads/master'))


def write_tree ():
    """Create a tree object from current index and return its OID."""
    # Index is flat, we need it as a tree of dicts
    index_as_tree = {}
    with data.get_index () as index:
        for path, oid in index.items ():
            path = path.split ('/')
            dirpath, filename = path[:-1], path[-1]

            current = index_as_tree
            # Find the dict for the directory of this file
            for dirname in dirpath:
                current = current.setdefault (dirname, {})
            current[filename] = oid

    def write_tree_recursive (tree_dict):
        entries = []
        for name, value in tree_dict.items ():
            if type (value) is dict:
                type_ = 'tree'
                oid = write_tree_recursive (value)
            else:
                type_ = 'blob'
                oid = value
            entries.append ((name, oid, type_))

        tree = ''.join (f'{type_} {oid} {name}\n'
                        for name, oid, type_
                        in sorted (entries))
        return data.hash_object (tree.encode (), 'tree')

    return write_tree_recursive (index_as_tree)

def _iter_tree_entries (oid):
    """
    Iterate through entries in a tree object.
    
    Args:
        oid: Object ID of tree
        
    Yields:
        tuple: (type, oid, name) for each entry
    """
    if not oid:
        return
    tree = data.get_object (oid, 'tree')
    for entry in tree.decode ().splitlines ():
        type_, oid, name = entry.split (' ', 2)
        yield type_, oid, name


def get_tree (oid, base_path=''):
    """
    Get dictionary of paths and OIDs for a given tree object.
    
    Args:
        oid: Object ID of the tree
        base_path: Base path prefix for tree entries
    
    Returns:
        dict: Mapping of paths to OIDs
    """
    result = {}
    for type_, oid, name in _iter_tree_entries (oid):
        assert '/' not in name
        assert name not in ('..', '.')
        path = base_path + name
        if type_ == 'blob':
            result[path] = oid
        elif type_ == 'tree':
            result.update (get_tree (oid, f'{path}/'))
        else:
            assert False, f'Unknown tree entry {type_}'
    return result

def get_working_tree ():
    """Get dictionary of paths and OIDs for current working directory."""
    result = {}
    for root, _, filenames in os.walk ('.'):
        for filename in filenames:
            path = os.path.relpath (f'{root}/{filename}')
            if is_ignored (path) or not os.path.isfile (path):
                continue
            with open (path, 'rb') as f:
                result[path] = data.hash_object (f.read ())
    return result

def get_index_tree ():
    """Get dictionary of paths and OIDs from current index."""
    with data.get_index () as index:
        return index


def _empty_current_directory ():
    """Remove all tracked files from working directory."""
    for root, dirnames, filenames in os.walk ('.', topdown=False):
        for filename in filenames:
            path = os.path.relpath (f'{root}/{filename}')
            if is_ignored (path) or not os.path.isfile (path):
                continue
            os.remove (path)
        for dirname in dirnames:
            path = os.path.relpath (f'{root}/{dirname}')
            if is_ignored (path):
                continue
            try:
                os.rmdir (path)
            except (FileNotFoundError, OSError):
                pass

def read_tree (tree_oid, update_working=False):
    """Read a tree into the index and optionally update working directory"""
    with data.get_index () as index:
        index.clear ()
        for path, oid in get_tree (tree_oid, base_path='').items ():
            index[path] = oid
            if update_working:
                # Skip if path is empty
                if not path:
                    continue
                    
                # Create directory if needed
                dir_path = os.path.dirname(path)
                if dir_path:  # Only create directory if path is not empty
                    os.makedirs(dir_path, exist_ok=True)
                    
                # Write file contents
                with open(path, 'wb') as f:
                    f.write(data.get_object(oid))


def read_tree_merged (t_base, t_HEAD, t_other, update_working=False):
    """
    Read merged tree into index and optionally update working directory.
    
    Args:
        t_base: Base tree OID
        t_HEAD: HEAD tree OID
        t_other: Other tree OID
        update_working: Whether to update working directory
    """
    with data.get_index () as index:
        index.clear ()
        index.update (diff.merge_trees (
            get_tree (t_base),
            get_tree (t_HEAD),
            get_tree (t_other)
        ))

        if update_working:
            _checkout_index (index)

def _checkout_index (index):
    """
    Update working directory to match index.
    
    Args:
        index: Dictionary mapping paths to OIDs
    """
    _empty_current_directory ()
    for path, oid in index.items ():
        os.makedirs (os.path.dirname (f'./{path}'), exist_ok=True)
        with open (path, 'wb') as f:
            f.write (data.get_object (oid, 'blob'))

def commit (message):
    """
    Create a new commit with the current index state.
    
    Args:
        message: Commit message
    
    Returns:
        str: OID of new commit
    """
    commit = f'tree {write_tree ()}\n'

    HEAD = data.get_ref ('HEAD').value
    if HEAD:
        commit += f'parent {HEAD}\n'
    MERGE_HEAD = data.get_ref ('MERGE_HEAD').value
    if MERGE_HEAD:
        commit += f'parent {MERGE_HEAD}\n'
        data.delete_ref ('MERGE_HEAD', deref=False)

    commit += '\n'
    commit += f'{message}\n'

    oid = data.hash_object (commit.encode (), 'commit')

    data.update_ref ('HEAD', data.RefValue (symbolic=False, value=oid))

    return oid


def checkout (name):
    """
    Switch to specified branch or commit.
    
    Args:
        name: Branch name or commit OID to checkout
    """
    oid = get_oid (name)
    commit = get_commit (oid)
    read_tree (commit.tree, update_working= True)

    if is_branch (name):
        HEAD = data.RefValue (symbolic=True, value=f'refs/heads/{name}')
    else:
        HEAD = data.RefValue (symbolic=False, value=oid)

    data.update_ref ('HEAD', HEAD, deref=False)

def reset (oid):
    """
    Reset HEAD to specified commit.
    
    Args:
        oid: Object ID to reset to
    """
    data.update_ref ('HEAD', data.RefValue (symbolic=False, value=oid))

def merge (other):
    """
    Merge specified commit into current branch.
    
    Args:
        other: OID of commit to merge
    """
    HEAD = data.get_ref ('HEAD').value
    assert HEAD
    merge_base = get_merge_base (other, HEAD)
    c_other = get_commit (other)

    # Handle fast-forward merge
    if merge_base == HEAD:
        read_tree (c_other.tree, update_working=True)
        data.update_ref ('HEAD',
                         data.RefValue (symbolic=False, value=other))
        print ('Fast-forward merge, no need to commit')
        return

    data.update_ref ('MERGE_HEAD', data.RefValue (symbolic=False, value=other))

    c_base = get_commit (merge_base)
    c_HEAD = get_commit (HEAD)
    read_tree_merged (c_base.tree, c_HEAD.tree, c_other.tree, update_working=True)
    print ('Merged in working tree\nPlease commit')



def get_merge_base (oid1, oid2):
    """
    Find most recent common ancestor of two commits.
    
    Args:
        oid1: First commit OID
        oid2: Second commit OID
        
    Returns:
        str: OID of merge base commit
    """
    parents1 = set (iter_commits_and_parents ({oid1}))

    for oid in iter_commits_and_parents ({oid2}):
        if oid in parents1:
            return oid

def is_ancestor_of (commit, maybe_ancestor):
    """
    Check if one commit is ancestor of another.
    
    Args:
        commit: Potential descendant commit OID
        maybe_ancestor: Potential ancestor commit OID
        
    Returns:
        bool: True if maybe_ancestor is ancestor of commit
    """
    return maybe_ancestor in iter_commits_and_parents ({commit})

def create_tag (name, oid):
    """
    Create a tag reference pointing to specified commit.
    
    Args:
        name: Tag name
        oid: Object ID to tag
    """
    data.update_ref (f'refs/tags/{name}', data.RefValue (symbolic=False, value=oid))


def create_branch (name, oid):
    """
    Create a new branch pointing to specified commit.
    
    Args:
        name: Branch name
        oid: Object ID for branch to point to
    """
    ref_path = f'refs/heads/{name}'
    data.update_ref(ref_path, data.RefValue(symbolic=False, value=oid))
    print(f"Created branch {name} at {ref_path}")  # Debug print

def iter_branch_names ():
    """Iterate through all branch names in the repository"""
    for refname, _ in data.iter_refs('refs/heads/'):
        # Normalize path separators to forward slashes
        refname = refname.replace('\\', '/')
        if not refname.startswith('refs/heads/'):
            continue
        # Extract branch name from refs/heads/branch-name
        branch_name = refname[len('refs/heads/'):]
        yield branch_name

def is_branch (branch):
    """
    Check if specified name is a valid branch.
    
    Args:
        branch: Branch name to check
        
    Returns:
        bool: True if branch exists
    """
    return data.get_ref (f'refs/heads/{branch}').value is not None

def get_branch_name ():
    """Get the name of the current branch"""
    HEAD = data.get_ref('HEAD', deref=False)
    if not HEAD.symbolic:
        return None
    HEAD = HEAD.value.replace('\\', '/')  # Normalize path separators
    if not HEAD.startswith('refs/heads/'):
        return None
    return HEAD[len('refs/heads/'):]  # Extract branch name



Commit = namedtuple ('Commit', ['tree', 'parents', 'message'])


def get_commit (oid):
    """Get commit object by OID and return Commit namedtuple."""
    parents = []
    commit = data.get_object (oid, 'commit').decode ()
    lines = iter (commit.splitlines ())
    for line in itertools.takewhile (operator.truth, lines):
        key, value = line.split (' ', 1)
        if key == 'tree':
            tree = value
        elif key == 'parent':
            parents.append (value)
        else:
            assert False, f'Unknown field {key}'

    message = '\n'.join (lines)
    return Commit (tree=tree, parents=parents, message=message)

def iter_commits_and_parents (oids):
    """
    Iterate through commits and their parents.
    
    Args:
        oids: Set of commit OIDs to start from
        
    Yields:
        str: OID of each commit encountered
    """
    oids = deque (oids)
    visited = set ()

    while oids:
        oid = oids.popleft ()
        if not oid or oid in visited:
            continue
        visited.add (oid)
        yield oid

        commit = get_commit (oid)
        # Return first parent next
        oids.extendleft (commit.parents[:1])
        # Return other parents later
        oids.extend (commit.parents[1:])

def iter_objects_in_commits (oids):
    """
    Iterate through all objects reachable from commits.
    
    Args:
        oids: Set of commit OIDs to start from
        
    Yields:
        str: OID of each object encountered
    """
    visited = set ()
    def iter_objects_in_tree (oid):
        visited.add (oid)
        yield oid
        for type_, oid, _ in _iter_tree_entries (oid):
            if oid not in visited:
                if type_ == 'tree':
                    yield from iter_objects_in_tree (oid)
                else:
                    visited.add (oid)
                    yield oid

    for oid in iter_commits_and_parents (oids):
        yield oid
        commit = get_commit (oid)
        if commit.tree not in visited:
            yield from iter_objects_in_tree (commit.tree)


def get_oid (name):
    if name == '@': name = 'HEAD'
    # Name is ref
    refs_to_try = [
        f'{name}',
        f'refs/{name}',
        f'refs/tags/{name}',
        f'refs/heads/{name}',
    ]
    for ref in refs_to_try:
        if data.get_ref (ref, deref=False).value:
            return data.get_ref (ref).value


    # Name is SHA1
    is_hex = all (c in string.hexdigits for c in name)
    if len (name) == 40 and is_hex:
        return name

    assert False, f'Unknown name {name}'

def add (filenames):

    def add_file (filename):
        # Normalize path
        filename = os.path.relpath (filename)
        with open (filename, 'rb') as f:
            oid = data.hash_object (f.read ())
        index[filename] = oid

    def add_directory (dirname):
        for root, _, filenames in os.walk (dirname):
            for filename in filenames:
                # Normalize path
                path = os.path.relpath (f'{root}/{filename}')
                if is_ignored (path) or not os.path.isfile (path):
                    continue
                add_file (path)

    with data.get_index () as index:
        for name in filenames:
            if os.path.isfile (name):
                add_file (name)
            elif os.path.isdir (name):
                add_directory (name)


def is_ignored (path):
    """Check if a path should be ignored"""
    # Normalize path separators to forward slashes
    path = path.replace('\\', '/')
    
    # List of patterns to ignore
    ignore_patterns = [
        '.pygit/',           # Ignore .pygit directory and its contents
        '__pycache__/',      # Ignore Python cache directories
        '*.pyc',             # Ignore Python compiled files
        '*.pyo',             # Ignore Python optimized files
        '*.pyd',             # Ignore Python DLL files
    ]
    
    # Check if path matches any ignore pattern
    for pattern in ignore_patterns:
        if pattern.endswith('/'):
            # Directory pattern
            if pattern[:-1] in path.split('/'):
                return True
        else:
            # File pattern (simple wildcard matching)
            if pattern.startswith('*'):
                if path.endswith(pattern[1:]):
                    return True
            elif pattern == path:
                return True
    
    return False
