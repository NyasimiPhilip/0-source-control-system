import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test2.test_base import TestBase
from test2.test_data import TestData
from test2.test_diff import TestDiff
from test2.test_remote import TestRemote

if __name__ == '__main__':
    unittest.main()