import unittest
import sys
import os

# Add the parent directory to Python path so we can import ugit
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import all test modules
from tests.test_base import TestBase
from tests.test_data import TestData
from tests.test_remote import TestRemote

if __name__ == '__main__':
    unittest.main() 