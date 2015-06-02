import os

from unittest import TestCase

from kotoba        import load_from_file
from kotoba.kotoba import Kotoba, Kami

class TestIntegrationWithSelector(TestCase):
    def setUp(self):
        sandbox_path = os.path.join(os.path.dirname(__file__), '../data/sandbox.xml')
        locator_path = os.path.join(os.path.dirname(__file__), '../data/locator.xml')

        self.x = load_from_file(sandbox_path)
        self.y = load_from_file(locator_path)

    def tearDown(self):
        pass

    def test_single_simple_selector(self):
        nodes = self.x.find('created_at')
        self.assertIsInstance(nodes, Kami)
        self.assertEquals(len(nodes), 4)

        nodes = self.x.find('Created_at')
        self.assertEquals(len(nodes), 0)

    def test_many_simple_selector(self):
        nodes = self.x.find('status created_at')
        self.assertEquals(len(nodes), 4)

        nodes = self.x.find('user created_at')
        self.assertEquals(len(nodes), 2)

        nodes = self.x.find('status lang')
        self.assertEquals(len(nodes), 1)

    def test_selector_with_chilren_search(self):
        nodes = self.x.find('status > created_at')
        self.assertEquals(len(nodes), 2)

        nodes = self.x.find('status > lang')
        self.assertEquals(len(nodes), 0)

    def test_selector_with_attributes(self):
        nodes = self.y.find('entity[id="poo"]')
        self.assertEquals(len(nodes), 1)

    def test_selector_with_attributes_without_quotation_marks(self):
        nodes = self.y.find('entity[id=poo]')
        self.assertEquals(len(nodes), 1)





