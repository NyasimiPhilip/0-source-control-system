"""Remote repository operations for PyGit."""

import os
import shutil
from . import data
from . import base


REMOTE_REFS_BASE = 'refs/heads/'
LOCAL_REFS_BASE = 'refs/remote/'

def fetch (remote_path):
    """Fetch objects and refs from remote repository."""
    refs = _get_remote_refs (remote_path)
    
    # Ensure objects directory exists
    os.makedirs(f'{data.GIT_DIR}/objects', exist_ok=True)
    
    # Fetch all objects
    for oid in base.iter_objects_in_commits (refs.values ()):
        data.fetch_object_if_missing (oid, remote_path)
    
    # Update local refs to match remote
    for refname, value in refs.items ():
        data.update_ref (refname, data.RefValue (symbolic=False, value=value))


def push (remote_path, refname):
    """Push current branch to remote repository."""
    # Get refs and objects that need to be pushed
    remote_refs = _get_remote_refs (remote_path)
    remote_ref = remote_refs.get (refname)
    local_ref = data.get_ref (refname).value
    known_remote_refs = filter (None, remote_refs.values ())

    # Don't allow force push
    if remote_ref not in base.iter_commits_and_parents ({local_ref}):
        raise Exception("Push would not be fast-forward")

    # Compute which objects the server doesn't have
    remote_objects = set (base.iter_objects_in_commits (known_remote_refs))
    local_objects = set (base.iter_objects_in_commits ({local_ref}))
    objects_to_push = local_objects - remote_objects

    # Push missing objects
    for oid in objects_to_push:
        data.push_object (oid, remote_path)

    # Update server ref to our value
    with data.change_git_dir (remote_path):
        data.update_ref (refname, data.RefValue (symbolic=False, value=local_ref))

def _get_remote_refs (remote_path):
    """Get all refs from remote repository"""
    with data.change_git_dir(remote_path):
        refs = {}
        # Get HEAD ref
        head = data.get_ref('HEAD', deref=False)
        if head.value:
            refs['HEAD'] = head.value
        
        # Get all other refs
        for refname, ref in data.iter_refs():
            refs[refname] = ref.value
        
        return refs

def clone(remote_path, target_path):
    """Clone a repository from remote_path to target_path"""
    # Remove target directory if it exists
    if os.path.exists(target_path):
        shutil.rmtree(target_path)
    
    # First, copy the entire source directory
    shutil.copytree(remote_path, target_path, ignore=shutil.ignore_patterns('.pygit*'))
    
    # Initialize new repository in target
    with data.change_git_dir(target_path):
        data.init()
        
        # Ensure required directories exist
        os.makedirs(f'{data.GIT_DIR}/objects', exist_ok=True)
        os.makedirs(f'{data.GIT_DIR}/refs/heads', exist_ok=True)
        
        # Get refs from remote
        refs = _get_remote_refs(remote_path)
        
        # Fetch all objects
        for oid in base.iter_objects_in_commits(refs.values()):
            data.fetch_object_if_missing(oid, remote_path)
        
        # Update refs to match remote
        for refname, value in refs.items():
            if refname.startswith('refs/heads/'):
                data.update_ref(refname, data.RefValue(symbolic=False, value=value))
        
        # Set up HEAD to point to master
        master_ref = refs.get('refs/heads/master')
        if master_ref:
            data.update_ref('HEAD', data.RefValue(symbolic=True, value='refs/heads/master'))
            
            # Add all files to index
            with data.get_index() as index:
                for root, _, files in os.walk('.'):
                    for file in files:
                        path = os.path.relpath(os.path.join(root, file))
                        if not base.is_ignored(path):
                            with open(path, 'rb') as f:
                                oid = data.hash_object(f.read())
                            index[path] = oid
