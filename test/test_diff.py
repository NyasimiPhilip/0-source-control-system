import os
import shutil
import unittest
from pygit import base, data, diff

class TestDiff(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.join(os.path.dirname(__file__), 'test_repo')
        os.makedirs(self.test_dir, exist_ok=True)
        os.chdir(self.test_dir)
        data.GIT_DIR = os.path.join(self.test_dir, '.pygit')
        base.init()

    def tearDown(self):
        os.chdir(os.path.dirname(__file__))
        shutil.rmtree(self.test_dir)

    def test_diff_trees(self):
        """Test file modification"""
        with open('file1.txt', 'w') as f:
            f.write('content1')
        base.add(['file1.txt'])
        commit1 = base.commit("First commit")

        with open('file1.txt', 'w') as f:
            f.write('content2')
        base.add(['file1.txt'])
        commit2 = base.commit("Second commit")

        tree1 = base.get_tree(base.get_commit(commit1).tree)
        tree2 = base.get_tree(base.get_commit(commit2).tree)
        diff_output = diff.diff_trees(tree1, tree2)
        
        # Update assertions to match actual output format
        self.assertIn(b'File modified:', diff_output)
        self.assertIn(b'content1', diff_output)
        self.assertIn(b'content2', diff_output)

    def test_new_file_diff(self):
        """Test new file addition"""
        # Create empty tree
        tree1 = {}
        
        # Create tree with new file
        with open('new.txt', 'w') as f:
            f.write('new content')
        base.add(['new.txt'])
        commit = base.commit("Add new file")
        tree2 = base.get_tree(base.get_commit(commit).tree)
        
        diff_output = diff.diff_trees(tree1, tree2)
        # Update assertions to match actual output format
        self.assertIn(b'New file added:', diff_output)
        self.assertIn(b'new content', diff_output)

    def test_delete_file_diff(self):
        """Test file deletion"""
        # Create initial tree with file
        with open('delete.txt', 'w') as f:
            f.write('to be deleted')
        base.add(['delete.txt'])
        commit1 = base.commit("Add file")
        tree1 = base.get_tree(base.get_commit(commit1).tree)

        # Create tree without file
        os.remove('delete.txt')
        # Need to update the index to reflect the deletion
        with data.get_index() as index:
            if 'delete.txt' in index:
                del index['delete.txt']
        commit2 = base.commit("Delete file")
        tree2 = base.get_tree(base.get_commit(commit2).tree)

        diff_output = diff.diff_trees(tree1, tree2)
        # Update assertions to match actual output format
        self.assertIn(b'File deleted:', diff_output)
        self.assertIn(b'to be deleted', diff_output)

    def test_binary_file_diff(self):
        # Test binary file handling
        with open('binary.bin', 'wb') as f:
            f.write(b'\x00\x01\x02')
        base.add(['binary.bin'])
        commit = base.commit("Add binary file")

        tree = base.get_tree(base.get_commit(commit).tree)
        diff_output = diff.diff_trees({}, tree)
        self.assertIn(b'Binary file', diff_output)