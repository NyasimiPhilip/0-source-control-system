import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test.test_base import TestBase
from test.test_data import TestData
from test.test_diff import TestDiff
from test.test_remote import TestRemote

if __name__ == '__main__':
    unittest.main()