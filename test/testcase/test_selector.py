from unittest import TestCase

from kotoba.kotoba   import Kotoba
from kotoba.parser   import selector

class TestSelector(TestCase):    
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    def test_constructor_basic(self):
        s = selector('element')
        
        self.assertEquals(s.name(), 'element')
    
    def test_constructor_element_with_attribute(self):
        s = selector('element[aname="avalue"]')
        
        self.assertEquals(s.name(), 'element')
        
        self.assertEquals(len(s.attributes()), 1)
        
        s = selector('element[aname1="avalue1"][aname2="avalue2"]')
        
        self.assertEquals(s.name(), 'element')
        
        self.assertEquals(len(s.attributes()), 2)