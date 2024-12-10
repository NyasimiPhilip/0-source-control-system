import os
import shutil
import unittest
from pygit import base, data, diff

class TestDiff(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.join(os.path.dirname(__file__), 'test_repo')
        os.makedirs(self.test_dir, exist_ok=True)
        os.chdir(self.test_dir)
        data.GIT_DIR = os.path.join(self.test_dir, '.ugit')
        base.init()

    def tearDown(self):
        os.chdir(os.path.dirname(__file__))
        shutil.rmtree(self.test_dir)

    def test_diff_trees(self):
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
        self.assertIn(b'-content1', diff_output)
        self.assertIn(b'+content2', diff_output)