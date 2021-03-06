import os
from unittest import TestCase

from kotoba        import load_from_file
from kotoba.kotoba import Kotoba, Kami

class TestInitializationWithFile(TestCase):
    def setUp(self):
        file_path = os.path.join(os.path.dirname(__file__), '../data/sandbox.xml')
        self.x    = load_from_file(file_path)

    def tearDown(self):
        pass

    def test_initial_loading(self):
        self.assertIsInstance(self.x, Kotoba)
        self.assertIsInstance(self.x.adjacents(), Kami)
        self.assertFalse(self.x._is_children_initialized)

        self.assertIsInstance(self.x.children(), Kami)
        self.assertTrue(self.x._is_children_initialized)

    def test_trigger_lazy_loading_with_children(self):
        self.assertIsInstance(self.x, Kotoba)
        self.assertIsInstance(self.x.adjacents(), Kami)
        self.assertFalse(self.x._is_children_initialized)

        self.assertIsInstance(self.x.children(), Kami)
        self.assertTrue(self.x._is_children_initialized)

    def test_trigger_lazy_loading_with_data(self):
        self.assertIsInstance(self.x, Kotoba)
        self.assertIsInstance(self.x.adjacents(), Kami)
        self.assertFalse(self.x._is_children_initialized)

        self.x.data()
        self.assertTrue(self.x._is_children_initialized)

