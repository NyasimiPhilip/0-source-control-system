import os
import shutil
import unittest
from ugit import base, data, remote

class TestRemote(unittest.TestCase):
    def setUp(self):
        # Create test directories for local and remote repos
        self.test_dir = os.path.join(os.path.dirname(__file__), 'test_repos')
        self.local_dir = os.path.join(self.test_dir, 'local')
        self.remote_dir = os.path.join(self.test_dir, 'remote')
        
        os.makedirs(self.local_dir)
        os.makedirs(self.remote_dir)

        # Initialize both repos
        os.chdir(self.remote_dir)
        data.GIT_DIR = os.path.join(self.remote_dir, '.ugit')
        base.init()

        os.chdir(self.local_dir)
        data.GIT_DIR = os.path.join(self.local_dir, '.ugit')
        base.init()

    def tearDown(self):
        os.chdir(os.path.dirname(__file__))
        shutil.rmtree(self.test_dir)

    def test_fetch_and_push(self):
        """Test fetching and pushing between repositories"""
        # Create a commit in remote
        os.chdir(self.remote_dir)
        with data.change_git_dir(self.remote_dir):
            with open('test.txt', 'w') as f:
                f.write('remote content')
            base.add(['test.txt'])
            remote_commit = base.commit("Remote commit")

        # Fetch from remote to local
        os.chdir(self.local_dir)
        with data.change_git_dir(self.local_dir):
            remote.fetch(self.remote_dir)
            
            # Verify object was fetched
            self.assertTrue(data.object_exists(remote_commit))

        # Create a new commit in local
        os.chdir(self.local_dir)
        with data.change_git_dir(self.local_dir):
            with open('local.txt', 'w') as f:
                f.write('local content')
            base.add(['local.txt'])
            local_commit = base.commit("Local commit")

            # Push to remote
            remote.push(self.remote_dir, 'refs/heads/master')

        # Verify push was successful
        os.chdir(self.remote_dir)
        with data.change_git_dir(self.remote_dir):
            self.assertTrue(data.object_exists(local_commit)) 

    def test_clone(self):
        # Set up a remote repository
        os.chdir(self.remote_dir)
        with data.change_git_dir(self.remote_dir):
            with open('test.txt', 'w') as f:
                f.write('remote content')
            base.add(['test.txt'])
            remote_commit = base.commit("Remote commit")

        # Clone the remote repository
        target_dir = os.path.join(self.test_dir, 'clone')
        remote.clone(self.remote_dir, target_dir)

        # Verify the cloned repository
        os.chdir(target_dir)
        with data.change_git_dir(target_dir):
            self.assertTrue(data.object_exists(remote_commit))
            self.assertEqual(data.get_ref('HEAD').value, remote_commit) 