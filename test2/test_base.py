import os
import shutil
import unittest
from ugit import base, data

class TestBase(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.join(os.path.dirname(__file__), 'test_repo')
        os.makedirs(self.test_dir, exist_ok=True)
        os.chdir(self.test_dir)
        data.GIT_DIR = os.path.join(self.test_dir, '.ugit')
        base.init()

    def tearDown(self):
        os.chdir(os.path.dirname(__file__))
        shutil.rmtree(self.test_dir)

    def test_init(self):
        self.assertTrue(os.path.exists(data.GIT_DIR))
        self.assertTrue(os.path.exists(os.path.join(data.GIT_DIR, 'objects')))

    def test_write_tree(self):
        os.makedirs('dir1')
        with open('dir1/file1.txt', 'w') as f:
            f.write('content1')
        with open('file2.txt', 'w') as f:
            f.write('content2')

        base.add(['dir1/file1.txt', 'file2.txt'])
        tree_oid = base.write_tree()
        self.assertIsNotNone(tree_oid)

    def test_commit(self):
        with open('test.txt', 'w') as f:
            f.write('test content')
        base.add(['test.txt'])
        commit_oid = base.commit("Initial commit")
        self.assertIsNotNone(commit_oid)

    def test_checkout(self):
        with open('test.txt', 'w') as f:
            f.write('version 1')
        base.add(['test.txt'])
        commit1 = base.commit("First commit")

        with open('test.txt', 'w') as f:
            f.write('version 2')
        base.add(['test.txt'])
        commit2 = base.commit("Second commit")

        base.checkout(commit1)
        with open('test.txt') as f:
            self.assertEqual(f.read(), 'version 1')

        base.checkout(commit2)
        with open('test.txt') as f:
            self.assertEqual(f.read(), 'version 2')

    def test_merge(self):
        with open('test.txt', 'w') as f:
            f.write('version 1')
        base.add(['test.txt'])
        commit1 = base.commit("First commit")

        with open('test.txt', 'w') as f:
            f.write('version 2')
        base.add(['test.txt'])
        commit2 = base.commit("Second commit")

        base.merge(commit1)
        with open('test.txt') as f:
            self.assertEqual(f.read(), 'version 1')