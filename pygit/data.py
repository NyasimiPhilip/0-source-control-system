"""Core data storage operations for PyGit.

This module handles all low-level data storage operations including:
- Object storage (blobs, trees, commits)
- Reference management (branches, tags)
- Index (staging area) operations
"""

import os
import shutil
import hashlib
import json

from collections import namedtuple
from contextlib import contextmanager

# Named tuple for reference values
RefValue = namedtuple('RefValue', ['symbolic', 'value'])

# Will be initialized in cli.main()
GIT_DIR = None

@contextmanager
def change_git_dir(new_dir):
    """
    Temporarily change GIT_DIR for context operations.
    
    Args:
        new_dir: New directory path for GIT_DIR
    """
    global GIT_DIR
    old_dir = GIT_DIR
    GIT_DIR = f'{new_dir}/.pygit'
    yield
    GIT_DIR = old_dir

def hash_object(data, type_='blob'):
    """
    Compute hash of object and store it.
    
    Args:
        data: Content to hash and store
        type_: Object type ('blob', 'tree', 'commit')
        
    Returns:
        str: Object ID (SHA-1 hash)
    """
    obj = type_.encode() + b'\x00' + data
    oid = hashlib.sha1(obj).hexdigest()
    with open(f'{GIT_DIR}/objects/{oid}', 'wb') as out:
        out.write(obj)
    return oid

def update_ref (ref, value, deref=True):
    """Update a reference to point to a specific value."""
    ref = _get_ref_internal (ref, deref)[0]

    assert value.value
    if value.symbolic:
        value = f'ref: {value.value}'
    else:
        value = value.value

    ref_path = f'{GIT_DIR}/{ref}'
    os.makedirs (os.path.dirname (ref_path), exist_ok=True)
    with open (ref_path, 'w') as f:
        f.write (value)


def get_ref (ref, deref=True):
    """Get the value of a reference."""
    ref_path = f'{GIT_DIR}/{ref}'
    value = None
    if os.path.isfile (ref_path):
        with open (ref_path) as f:
            value = f.read ().strip ()

    symbolic = bool (value) and value.startswith ('ref:')
    if symbolic:
        value = value.split (':', 1)[1].strip ()
        if deref:
            return get_ref (value, deref=True)

    return RefValue (symbolic=symbolic, value=value)

def delete_ref (ref, deref=True):
    ref = _get_ref_internal (ref, deref)[0]
    os.remove (f'{GIT_DIR}/{ref}')

def _get_ref_internal (ref, deref):
    ref_path = f'{GIT_DIR}/{ref}'
    value = None
    if os.path.isfile (ref_path):
        with open (ref_path) as f:
            value = f.read ().strip ()

    symbolic = bool (value) and value.startswith ('ref:')
    if symbolic:
        value = value.split (':', 1)[1].strip ()
        if deref:
            return _get_ref_internal (value, deref=True)

    return ref, RefValue (symbolic=symbolic, value=value)


def iter_refs (prefix='', deref=True):
    """Iterate through all refs in the repository"""
    # First, check if refs directory exists
    refs_dir = f'{GIT_DIR}/refs'
    if not os.path.exists(refs_dir):
        return

    # Start with HEAD and MERGE_HEAD
    refs = ['HEAD', 'MERGE_HEAD']
    
    # Walk through all files in refs directory
    for root, _, filenames in os.walk(refs_dir):
        # Convert Windows paths to Unix-style for consistency
        root = root.replace('\\', '/')
        # Get relative path from GIT_DIR
        root = os.path.relpath(root, GIT_DIR)
        # Add each ref file found
        for name in filenames:
            refs.append(f'{root}/{name}')

    # Yield each ref that matches the prefix
    for refname in refs:
        # Normalize path separators
        refname = refname.replace('\\', '/')
        if not refname.startswith(prefix):
            continue
        ref = get_ref(refname, deref=deref)
        if ref.value:
            yield refname, ref

@contextmanager
def get_index ():
    index = {}
    if os.path.isfile (f'{GIT_DIR}/index'):
        with open (f'{GIT_DIR}/index') as f:
            index = json.load (f)

    yield index

    with open (f'{GIT_DIR}/index', 'w') as f:
        json.dump (index, f)


def hash_object (data, type_='blob'):
    obj = type_.encode () + b'\x00' + data
    oid = hashlib.sha1 (obj).hexdigest ()
    with open (f'{GIT_DIR}/objects/{oid}', 'wb') as out:
        out.write (obj)
    return oid

def get_object (oid, expected='blob'):
    with open (f'{GIT_DIR}/objects/{oid}', 'rb') as f:
        obj = f.read ()

    type_, _, content = obj.partition (b'\x00')
    type_ = type_.decode ()

    if expected is not None:
        assert type_ == expected, f'Expected {expected}, got {type_}'
    return content


def object_exists (oid):
    return os.path.isfile (f'{GIT_DIR}/objects/{oid}')


def fetch_object_if_missing (oid, remote_path):
    """Fetch an object from a remote repository if it doesn't exist locally"""
    if object_exists (oid):
        return
        
    # Ensure objects directory exists
    os.makedirs(f'{GIT_DIR}/objects', exist_ok=True)
    
    remote_git_dir = f'{remote_path}/.pygit'
    src = f'{remote_git_dir}/objects/{oid}'
    dst = f'{GIT_DIR}/objects/{oid}'
    
    shutil.copy(src, dst)

def push_object (oid, remote_path):
    """Push an object to a remote repository"""
    remote_git_dir = f'{remote_path}/.pygit'
    
    # Ensure remote objects directory exists
    os.makedirs(f'{remote_git_dir}/objects', exist_ok=True)
    
    src = f'{GIT_DIR}/objects/{oid}'
    dst = f'{remote_git_dir}/objects/{oid}'
    
    shutil.copy(src, dst)

