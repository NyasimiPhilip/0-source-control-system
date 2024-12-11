import os
import shutil
import unittest
from pygit import base, data

class TestBranch(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.join(os.path.dirname(__file__), 'test_repo')
        os.makedirs(self.test_dir, exist_ok=True)
        os.chdir(self.test_dir)
        data.GIT_DIR = os.path.join(self.test_dir, '.pygit')
        base.init()

    def tearDown(self):
        os.chdir(os.path.dirname(__file__))
        shutil.rmtree(self.test_dir)

    def test_create_branch(self):
        """Test branch creation"""
        # Create initial commit
        with open('test.txt', 'w') as f:
            f.write('test content')
        base.add(['test.txt'])
        commit_oid = base.commit("Initial commit")

        # Create branch
        base.create_branch('feature', commit_oid)
        
        # Verify branch exists
        branches = list(base.iter_branch_names())
        self.assertIn('feature', branches)
        self.assertIn('master', branches)

    def test_checkout_branch(self):
        """Test branch checkout"""
        # Create initial commit
        with open('test.txt', 'w') as f:
            f.write('master content')
        base.add(['test.txt'])
        base.commit("Master commit")

        # Create and checkout feature branch
        base.create_branch('feature', base.get_oid('@'))
        base.checkout('feature')
        
        # Verify current branch
        self.assertEqual(base.get_branch_name(), 'feature')

    def test_branch_switching(self):
        """Test switching between branches with different content"""
        # Create master content
        with open('test.txt', 'w') as f:
            f.write('master content')
        base.add(['test.txt'])
        base.commit("Master commit")

        # Create feature branch with different content
        base.create_branch('feature', base.get_oid('@'))
        base.checkout('feature')
        with open('test.txt', 'w') as f:
            f.write('feature content')
        base.add(['test.txt'])
        base.commit("Feature commit")

        # Switch between branches and verify content
        base.checkout('master')
        with open('test.txt') as f:
            self.assertEqual(f.read(), 'master content')

        base.checkout('feature')
        with open('test.txt') as f:
            self.assertEqual(f.read(), 'feature content') 