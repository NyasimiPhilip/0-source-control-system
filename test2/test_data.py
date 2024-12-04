import os
import shutil
import unittest
from ugit import data

class TestData(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.join(os.path.dirname(__file__), 'test_repo')
        os.makedirs(self.test_dir, exist_ok=True)
        os.chdir(self.test_dir)
        data.GIT_DIR = os.path.join(self.test_dir, '.ugit')
        data.init()

    def tearDown(self):
        os.chdir(os.path.dirname(__file__))
        shutil.rmtree(self.test_dir)

    def test_hash_object(self):
        test_data = b'test content'
        oid = data.hash_object(test_data)
        self.assertIsNotNone(oid)
        retrieved_data = data.get_object(oid)
        self.assertEqual(retrieved_data, test_data)

    def test_update_ref(self):
        ref_name = 'refs/test'
        ref_value = data.RefValue(symbolic=False, value='test_value')
        data.update_ref(ref_name, ref_value)
        retrieved_ref = data.get_ref(ref_name)
        self.assertEqual(retrieved_ref.value, ref_value.value)
        self.assertEqual(retrieved_ref.symbolic, ref_value.symbolic)

    def test_symbolic_ref(self):
        ref_name = 'refs/symbolic'
        ref_value = data.RefValue(symbolic=True, value='refs/heads/master')
        data.update_ref(ref_name, ref_value)
        ref = data.get_ref(ref_name, deref=False)
        self.assertTrue(ref.symbolic)
        self.assertEqual(ref.value, 'refs/heads/master')