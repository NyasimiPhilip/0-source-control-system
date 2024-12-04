import os
import shutil
import unittest
from unittest.mock import patch

from ugit import base, data

class TestBase(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = os.path.join(os.path.dirname(__file__), 'test_repo')
        os.makedirs(self.test_dir, exist_ok=True)
        os.chdir(self.test_dir)
        
        # Initialize test repo
        data.GIT_DIR = os.path.join(self.test_dir, '.ugit')
        base.init()

    def tearDown(self):
        # Clean up the test directory
        os.chdir(os.path.dirname(__file__))
        shutil.rmtree(self.test_dir)

    def test_init(self):
        """Test repository initialization"""
        self.assertTrue(os.path.exists(data.GIT_DIR))
        self.assertTrue(os.path.exists(os.path.join(data.GIT_DIR, 'objects')))
        
        # Check HEAD reference
        head = data.get_ref('HEAD')
        self.assertTrue(head.symbolic)
        self.assertEqual(head.value, 'refs/heads/master')

    def test_write_and_read_tree(self):
        """Test writing and reading tree structures"""
        # Create test files
        os.makedirs('dir1')
        with open('dir1/file1.txt', 'w') as f:
            f.write('content1')
        with open('file2.txt', 'w') as f:
            f.write('content2')

        # Add files to index
        base.add(['dir1/file1.txt', 'file2.txt'])
        
        # Write tree and verify
        tree_oid = base.write_tree()
        self.assertIsNotNone(tree_oid)
        
        # Read tree and verify
        base.read_tree(tree_oid, update_working=True)
        
        # Verify files exist and content matches
        self.assertTrue(os.path.exists('dir1/file1.txt'))
        self.assertTrue(os.path.exists('file2.txt'))
        with open('dir1/file1.txt') as f:
            self.assertEqual(f.read(), 'content1')
        with open('file2.txt') as f:
            self.assertEqual(f.read(), 'content2')

    def test_commit_and_get_commit(self):
        """Test creating and retrieving commits"""
        # Create a test file and commit it
        with open('test.txt', 'w') as f:
            f.write('test content')
        
        base.add(['test.txt'])
        commit_message = "Initial commit"
        commit_oid = base.commit(commit_message)
        
        # Retrieve and verify commit
        commit = base.get_commit(commit_oid)
        self.assertIsNotNone(commit.tree)
        self.assertEqual(commit.message, commit_message)
        self.assertEqual(commit.parents, [])

    def test_checkout(self):
        """Test checkout functionality"""
        # Create initial commit
        with open('test.txt', 'w') as f:
            f.write('version 1')
        base.add(['test.txt'])
        commit1 = base.commit("First commit")

        # Create second commit
        with open('test.txt', 'w') as f:
            f.write('version 2')
        base.add(['test.txt'])
        commit2 = base.commit("Second commit")

        # Checkout first commit
        base.checkout(commit1)
        with open('test.txt') as f:
            self.assertEqual(f.read(), 'version 1')

        # Checkout second commit
        base.checkout(commit2)
        with open('test.txt') as f:
            self.assertEqual(f.read(), 'version 2')

    def test_create_and_get_branch(self):
        """Test branch creation and retrieval"""
        # Create initial commit
        with open('test.txt', 'w') as f:
            f.write('test content')
        base.add(['test.txt'])
        commit_oid = base.commit("Initial commit")

        # Create branch
        branch_name = 'test-branch'
        base.create_branch(branch_name, commit_oid)

        # Verify branch exists
        branches = list(base.iter_branch_names())
        self.assertIn(branch_name, branches)

        # Verify branch points to correct commit
        self.assertTrue(base.is_branch(branch_name)) 