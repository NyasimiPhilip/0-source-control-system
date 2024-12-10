import os
import shutil
import hashlib
import json

from collections import namedtuple
from contextlib import contextmanager


# Will be initialized in cli.main()
GIT_DIR = None


@contextmanager
def change_git_dir (new_dir):
    global GIT_DIR
    old_dir = GIT_DIR
    GIT_DIR = f'{new_dir}/.pygit'
    yield
    GIT_DIR = old_dir

def init():
    if not os.path.exists(GIT_DIR):
        os.makedirs(GIT_DIR)
        os.makedirs (f'{GIT_DIR}/objects', exist_ok=True)

RefValue = namedtuple ('RefValue', ['symbolic', 'value'])


def update_ref (ref, value, deref=True):
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
    """Get the value of a ref"""
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


def fetch_object_if_missing (oid, remote_git_dir):
    if object_exists (oid):
        return
    remote_git_dir += '/.pygit'
    shutil.copy (f'{remote_git_dir}/objects/{oid}',
                 f'{GIT_DIR}/objects/{oid}')

def push_object (oid, remote_git_dir):
    remote_git_dir += '/.pygit'
    shutil.copy (f'{GIT_DIR}/objects/{oid}',
                 f'{remote_git_dir}/objects/{oid}')

