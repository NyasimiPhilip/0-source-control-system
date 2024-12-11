import os
import shutil
import unittest
from pygit import base, data

class TestIgnore(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.join(os.path.dirname(__file__), 'test_repo')
        os.makedirs(self.test_dir, exist_ok=True)
        os.chdir(self.test_dir)
        data.GIT_DIR = os.path.join(self.test_dir, '.pygit')
        base.init()

    def tearDown(self):
        os.chdir(os.path.dirname(__file__))
        shutil.rmtree(self.test_dir)

    def test_pygit_dir_always_ignored(self):
        """Test that .pygit directory is always ignored"""
        self.assertTrue(base.is_ignored('.pygit/objects/abc'))
        self.assertTrue(base.is_ignored('.pygit/refs/heads/master'))

    def test_ignore_patterns(self):
        """Test various ignore patterns"""
        # Create .pygitignore
        with open('.pygitignore', 'w') as f:
            f.write('*.log\n')
            f.write('temp/\n')
            f.write('exact.txt\n')

        # Test patterns
        self.assertTrue(base.is_ignored('test.log'))
        self.assertTrue(base.is_ignored('temp/file.txt'))
        self.assertTrue(base.is_ignored('exact.txt'))
        self.assertFalse(base.is_ignored('test.txt'))

    def test_ignore_with_status(self):
        """Test that ignored files don't show in status"""
        # Create .pygitignore
        with open('.pygitignore', 'w') as f:
            f.write('*.log\n')

        # Create ignored and non-ignored files
        with open('test.log', 'w') as f:
            f.write('ignored')
        with open('test.txt', 'w') as f:
            f.write('not ignored')

        # Add all files
        base.add(['.'])

        # Check working tree
        working_tree = base.get_working_tree()
        self.assertNotIn('test.log', working_tree)
        self.assertIn('test.txt', working_tree) 