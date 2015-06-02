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

    def test_constructor_element_with_one_attribute(self):
        s = selector('element[aname="avalue"]')

        self.assertEquals(s.name(), 'element')
        self.assertEquals(s.attribute('aname'), 'avalue')
        self.assertEquals(len(s.attributes()), 1)

    def test_constructor_element_with_two_attributes(self):
        s = selector('element[aname1="avalue1"][aname2="avalue2"]')

        self.assertEquals(s.name(), 'element')
        self.assertEquals(s.attribute('aname1'), 'avalue1')
        self.assertEquals(s.attribute('aname2'), 'avalue2')
        self.assertEquals(len(s.attributes()), 2)

    def test_constructor_element_in_simple_mode(self):
        s = selector('element[aname1=avalue1][aname2="avalue2"]')

        self.assertEquals(s.name(), 'element')
        self.assertEquals(s.attribute('aname1'), 'avalue1')
        self.assertEquals(len(s.attributes()), 2)