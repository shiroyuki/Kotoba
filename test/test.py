import os
import sys
import unittest
import bootstrap

file_path = os.path.abspath(__file__)
code_path = os.path.dirname(os.path.abspath(file_path + '/../'))
test_path = os.path.dirname(file_path)

if code_path not in sys.path:
    sys.path.remove(code_path)

sys.path.insert(0, code_path)

if test_path not in sys.path:
    sys.path.remove(test_path)

sys.path.insert(0, test_path)

suite = unittest.TestLoader().discover(
    bootstrap.testing_base_path,
    pattern='test_*.py'
)
unittest.TextTestRunner(verbosity=1).run(suite)
