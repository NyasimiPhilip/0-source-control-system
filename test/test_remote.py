import os
import shutil
import unittest
from pygit import base, data, remote

class TestRemote(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.join(os.path.dirname(__file__), 'test_repos')
        self.source_dir = os.path.join(self.test_dir, 'source')
        self.target_dir = os.path.join(self.test_dir, 'target')
        
        # Create source repository
        os.makedirs(self.source_dir)
        os.chdir(self.source_dir)
        data.GIT_DIR = os.path.join(self.source_dir, '.pygit')
        base.init()

    def tearDown(self):
        os.chdir(os.path.dirname(__file__))
        shutil.rmtree(self.test_dir)

    def test_clone(self):
        """Test repository cloning"""
        # Create content in source repo
        os.chdir(self.source_dir)
        with open('test.txt', 'w') as f:
            f.write('test content')
        base.add(['test.txt'])
        source_commit = base.commit("Initial commit")

        # Clone repository
        remote.clone(self.source_dir, self.target_dir)

        # Verify clone
        os.chdir(self.target_dir)
        data.GIT_DIR = os.path.join(self.target_dir, '.pygit')
        
        # Check file content
        self.assertTrue(os.path.exists('test.txt'))
        with open('test.txt') as f:
            self.assertEqual(f.read(), 'test content')

        # Check commit history
        self.assertEqual(base.get_oid('@'), source_commit)

    def test_push_and_fetch(self):
        """Test pushing and fetching changes"""
        # Create target repo
        os.makedirs(self.target_dir)
        os.chdir(self.target_dir)
        data.GIT_DIR = os.path.join(self.target_dir, '.pygit')
        base.init()

        # Create and push changes in source
        os.chdir(self.source_dir)
        data.GIT_DIR = os.path.join(self.source_dir, '.pygit')
        with open('source.txt', 'w') as f:
            f.write('source content')
        base.add(['source.txt'])
        source_commit = base.commit("Source commit")

        # Push changes to target
        remote.push(self.target_dir, 'refs/heads/master')

        # Verify push in target
        os.chdir(self.target_dir)
        data.GIT_DIR = os.path.join(self.target_dir, '.pygit')
        
        # Ensure target has the commit
        self.assertTrue(data.object_exists(source_commit))
        
        # Create changes in target
        with open('target.txt', 'w') as f:
            f.write('target content')
        base.add(['target.txt'])
        target_commit = base.commit("Target commit")

        # Fetch changes in source
        os.chdir(self.source_dir)
        data.GIT_DIR = os.path.join(self.source_dir, '.pygit')
        remote.fetch(self.target_dir)
        
        # Verify fetch
        self.assertTrue(data.object_exists(target_commit))