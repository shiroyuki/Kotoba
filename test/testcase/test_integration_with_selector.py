from unittest import TestCase

from kotoba        import load_from_file
from kotoba.kotoba import Kotoba, Kami

class TestIntegrationWithSelector(TestCase):    
    def setUp(self):
        self.x = load_from_file('data/sandbox.xml')
        self.y = load_from_file('data/locator.xml')
    
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
    
        
    
    
    
    