import os
import shutil
import unittest
from pygit import data

class TestData(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.join(os.path.dirname(__file__), 'test_repo')
        os.makedirs(self.test_dir, exist_ok=True)
        os.chdir(self.test_dir)
        data.GIT_DIR = os.path.join(self.test_dir, '.pygit')
        os.makedirs(data.GIT_DIR)
        os.makedirs(os.path.join(data.GIT_DIR, 'objects'))
        os.makedirs(os.path.join(data.GIT_DIR, 'refs', 'heads'))

    def tearDown(self):
        os.chdir(os.path.dirname(__file__))
        shutil.rmtree(self.test_dir)

    def test_hash_and_get_object(self):
        """Test object storage and retrieval"""
        # Store object
        test_data = b'test content'
        oid = data.hash_object(test_data)
        
        # Verify object exists
        object_path = os.path.join(data.GIT_DIR, 'objects', oid)
        self.assertTrue(os.path.exists(object_path))
        
        # Retrieve and verify content
        retrieved = data.get_object(oid)
        self.assertEqual(retrieved, test_data)

    def test_ref_operations(self):
        """Test reference operations"""
        # Create symbolic ref
        data.update_ref('HEAD', 
                       data.RefValue(symbolic=True, 
                                   value='refs/heads/master'))
        
        # Create regular ref
        test_oid = 'abcd' * 10  # 40 char dummy hash
        data.update_ref('refs/heads/master',
                       data.RefValue(symbolic=False,
                                   value=test_oid))
        
        # Test ref retrieval
        head_ref = data.get_ref('HEAD', deref=True)
        self.assertEqual(head_ref.value, test_oid)
        
        # Test symbolic ref retrieval without dereferencing
        symbolic_ref = data.get_ref('HEAD', deref=False)
        self.assertTrue(symbolic_ref.symbolic)
        self.assertEqual(symbolic_ref.value, 'refs/heads/master')

    def test_index_operations(self):
        """Test index file operations"""
        test_data = {
            'file1.txt': 'abc' * 13,  # 39 char dummy hash
            'dir/file2.txt': 'def' * 13
        }
        
        # Write to index
        with data.get_index() as index:
            index.update(test_data)
        
        # Read from index
        with data.get_index() as index:
            self.assertEqual(index, test_data)
            
        # Verify index file exists
        self.assertTrue(os.path.exists(os.path.join(data.GIT_DIR, 'index')))

    def test_ref_iteration(self):
        """Test iterating through refs"""
        # Create some refs
        refs = {
            'refs/heads/master': 'aaa' * 13,
            'refs/heads/feature': 'bbb' * 13,
            'refs/tags/v1.0': 'ccc' * 13
        }
        
        for ref_name, value in refs.items():
            data.update_ref(ref_name, 
                          data.RefValue(symbolic=False, value=value))
            
        # Get all refs
        found_refs = dict(data.iter_refs())
        
        # Verify each ref
        for ref_name, value in refs.items():
            self.assertIn(ref_name, found_refs)
            self.assertEqual(found_refs[ref_name].value, value)

    def test_change_git_dir(self):
        """Test changing GIT_DIR context manager"""
        original_dir = data.GIT_DIR
        test_dir = "test_git_dir"
        
        with data.change_git_dir(test_dir):
            self.assertEqual(data.GIT_DIR, f'{test_dir}/.pygit')
            
        self.assertEqual(data.GIT_DIR, original_dir)