import os
import shutil
import unittest
from pygit import base, data

class TestStatus(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.join(os.path.dirname(__file__), 'test_repo')
        os.makedirs(self.test_dir, exist_ok=True)
        os.chdir(self.test_dir)
        data.GIT_DIR = os.path.join(self.test_dir, '.pygit')
        base.init()

    def tearDown(self):
        os.chdir(os.path.dirname(__file__))
        shutil.rmtree(self.test_dir)

    def test_untracked_files(self):
        """Test detection of untracked files"""
        # Create untracked file
        with open('untracked.txt', 'w') as f:
            f.write('untracked content')

        working_tree = base.get_working_tree()
        self.assertIn('untracked.txt', working_tree)

    def test_modified_files(self):
        """Test detection of modified files"""
        # Create and commit a file
        with open('test.txt', 'w') as f:
            f.write('initial content')
        base.add(['test.txt'])
        base.commit("Initial commit")

        # Modify the file
        with open('test.txt', 'w') as f:
            f.write('modified content')

        # Check working tree
        working_tree = base.get_working_tree()
        index_tree = base.get_index_tree()
        self.assertNotEqual(working_tree['test.txt'], index_tree['test.txt'])

    def test_staged_files(self):
        """Test detection of staged files"""
        # Create and stage a file
        with open('staged.txt', 'w') as f:
            f.write('staged content')
        base.add(['staged.txt'])

        # Verify file is in index
        index_tree = base.get_index_tree()
        self.assertIn('staged.txt', index_tree)

    def test_deleted_files(self):
        """Test detection of deleted files"""
        # Create and commit a file
        with open('delete.txt', 'w') as f:
            f.write('to be deleted')
        base.add(['delete.txt'])
        base.commit("Add file")

        # Delete the file
        os.remove('delete.txt')

        # Check working tree
        working_tree = base.get_working_tree()
        self.assertNotIn('delete.txt', working_tree) 