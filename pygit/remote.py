"""Remote repository operations for PyGit."""

import os
import shutil
from . import data
from . import base


REMOTE_REFS_BASE = 'refs/heads/'
LOCAL_REFS_BASE = 'refs/remote/'

def fetch (remote_path):
    """
    Fetch objects and refs from remote repository.
    
    Args:
        remote_path: Path to remote repository
    """
    # Get refs from remote
    refs = _get_remote_refs (remote_path)
    
    # Ensure objects directory exists
    os.makedirs(f'{data.GIT_DIR}/objects', exist_ok=True)
    
    # Fetch all objects
    for oid in base.iter_objects_in_commits (refs.values ()):
        data.fetch_object_if_missing (oid, remote_path)
    
    # Update local refs to match remote
    for refname, value in refs.items ():
        if refname.startswith('refs/heads/'):
            # Store remote refs under refs/remotes/
            remote_ref = f'refs/remotes/origin/{refname[11:]}'
            data.update_ref (remote_ref, data.RefValue (symbolic=False, value=value))
            
            # If this is our current branch, update it
            current_branch = base.get_branch_name()
            if current_branch and refname == f'refs/heads/{current_branch}':
                # Fast-forward if possible
                current_ref = data.get_ref (f'refs/heads/{current_branch}').value
                if base.is_ancestor_of (value, current_ref):
                    data.update_ref (refname, data.RefValue (symbolic=False, value=value))
                    # Update working directory
                    commit = base.get_commit (value)
                    base.read_tree (commit.tree, update_working=True)


def push (remote_path, refname):
    """
    Push current branch to remote repository.
    
    Args:
        remote_path: Path to remote repository
        refname: Reference to push (e.g., refs/heads/master)
    """
    # Get refs and objects that need to be pushed
    remote_refs = _get_remote_refs(remote_path)
    remote_ref = remote_refs.get(refname)
    local_ref = data.get_ref(refname).value
    
    if not local_ref:
        print(f"error: No local ref found for {refname}")
        return
    
    # Don't allow force push
    if remote_ref and not base.is_ancestor_of(local_ref, remote_ref):
        raise Exception("Push would not be fast-forward")

    # Get all objects that need to be pushed
    local_objects = set()
    for oid in base.iter_objects_in_commits({local_ref}):
        local_objects.add(oid)

    # Get remote objects
    remote_objects = set()
    if remote_ref:
        with data.change_git_dir(remote_path):
            for oid in base.iter_objects_in_commits({remote_ref}):
                remote_objects.add(oid)

    # Push missing objects
    objects_to_push = local_objects - remote_objects
    for oid in objects_to_push:
        data.push_object(oid, remote_path)

    # Update remote repository
    with data.change_git_dir(remote_path):
        # Update ref
        data.update_ref(refname, data.RefValue(symbolic=False, value=local_ref))
        
        # Get the commit we're pushing
        commit = base.get_commit(local_ref)
        
        # Update working directory
        base.read_tree(commit.tree, update_working=True)
        
        # Update index
        with data.get_index() as index:
            tree = base.get_tree(commit.tree)
            for path, oid in tree.items():
                index[path] = oid
                
                # Ensure parent directories exist
                dir_path = os.path.dirname(path)
                if dir_path:  # Only create directory if path is not empty
                    os.makedirs(os.path.join(remote_path, dir_path), exist_ok=True)
                
                # Write file content
                file_content = data.get_object(oid)
                with open(os.path.join(remote_path, path), 'wb') as f:
                    f.write(file_content)

    print(f"Pushed to {remote_path}:{refname}")
    print(f"Updated {len(objects_to_push)} objects")

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
        # Create repository structure
        os.makedirs(f'{data.GIT_DIR}/objects', exist_ok=True)
        os.makedirs(f'{data.GIT_DIR}/refs/heads', exist_ok=True)
        os.makedirs(f'{data.GIT_DIR}/refs/tags', exist_ok=True)
        
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
            # First set HEAD value
            with open(f'{data.GIT_DIR}/HEAD', 'w') as f:
                f.write('ref: refs/heads/master\n')
            
            # Then set up master branch
            data.update_ref('refs/heads/master', 
                          data.RefValue(symbolic=False, value=master_ref))
            
            # Add all files to index
            with data.get_index() as index:
                for root, _, files in os.walk('.'):
                    for file in files:
                        path = os.path.relpath(os.path.join(root, file))
                        if not base.is_ignored(path):
                            with open(path, 'rb') as f:
                                oid = data.hash_object(f.read())
                            index[path] = oid
