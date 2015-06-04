import os

from unittest import TestCase

from kotoba        import load_from_file
from kotoba.kotoba import Kotoba, Kami

class FunctionalTest(TestCase):
    def setUp(self):
        collection_path = os.path.join(os.path.dirname(__file__), '../data/sandbox_collection.json')
        document_path   = os.path.join(os.path.dirname(__file__), '../data/sandbox_document.json')

        self.x = load_from_file(collection_path)
        self.y = load_from_file(document_path)

    def tearDown(self):
        pass

    def do_assertion(self, root, selector, expected_count, expected_value):
        nodes = root.find(selector)

        actual_count = len(nodes)
        actual_value = nodes.data()

        self.assertEquals(
            actual_count,
            expected_count,
            'Expected {} node(s) from {}, got {}.'.format(
                expected_count,
                selector,
                actual_count
            )
        )

        self.assertEquals(
            actual_value,
            expected_value,
            'Expected {} ({}) from {}, got {} ({})'.format(
                expected_value,
                type(expected_value).__name__,
                selector,
                actual_value,
                type(actual_value).__name__,
            )
        )

    def test_collection_simple(self):
        self.do_assertion(self.x, '0 name', 1, 'Python')

    def test_collection_with_attributes(self):
        self.do_assertion(self.x, '[id=2] name', 1, 'Elephant')

    def test_collection_with_wildcard(self):
        self.do_assertion(self.x, '* name', 3, 'PythonElephantRuby')

    def test_document_simple(self):
        self.do_assertion(self.y, '> name', 1, 'Juti') # trick to refer to the level-1 nodes
        self.do_assertion(self.y, 'name', 4, 'ThaiEnglishJapaneseJuti')

    def test_document_with_attributes(self):
        self.do_assertion(self.y, 'languages [name=Japanese] since', 1, 2004)

    def _test_document_with_wildcard(self):
        """ Still not supported """
        self.do_assertion(self.x, 'languages * name', 3, 'ThaiEnglishJapanese')
