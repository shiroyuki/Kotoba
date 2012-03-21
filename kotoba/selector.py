from re import compile, sub, split

from .common    import node_debug_message, is_string
from .exception import SelectorSyntaxError
from .graph     import Vertex as BaseVertex

class PathType(object):
    registered   = [None, '>', '+', '~']
    descendants  = 0
    children     = 1
    any_siblings = 3
    immediate_siblings = 2

class Selector(BaseVertex):
    wildcards = ['','*']
    
    def __init__(self, parsed_selector_block, _kind=PathType.descendants):
        super(self.__class__, self).__init__()
        
        self._block = parsed_selector_block
        
        self._name = None
        self._attributes     = None
        self._pseudo_classes = None
        self._kind = _kind
        self._next = None
        
        if is_string(self._block):
            self._name  = self._block
            self._block = None
    
    def name(self):
        if not self._name and self._block:
            self._name = self._block.name
        
        return self._name
    
    def attributes(self):
        if not self._attributes:
            self._attributes = []
            
            if self._block:
                for raw_attribute in self._block.attributes:
                    attribute = Attribute.parse(raw_attribute)
                    
                    self._attributes.append(attribute)
        
        return self._attributes
    
    def kind(self, _kind=None):
        if _kind and not self._kind:
            self._kind = _kind
        
        return self._kind
    
    def next(self, next=None):
        if next and not self._next:
            self._next = next
        
        return self._next
    
    def match(self, vertex):
        node_debug_message(vertex, '[SELECTOR/MATCHING] %s --> %s' % (self.name(), vertex.name()))
        try:
            if not self.name() in self.wildcards:
                assert self.name() == '*' or self.name() == vertex.name()
            
            for attribute in self.attributes():
                assert attribute.match(vertex)
        except AssertionError:
            return False
        
        return True
    
    def __str__(self):
        return u'SELECTOR %s' % self.name()

class Attribute(object):
    _re_syntax   = compile('^\[(?P<name>[^=~\^\$\*\|]+)(?P<operator>[~\^\$\*\|]?=?)(?P<value>.*)\]$')
    _re_operator = compile('^[~\^\$\*\|]?=$')
    
    @staticmethod
    def parse(raw_attribute):
        matches = Attribute._re_syntax.search(raw_attribute)
        
        if not matches:
            raise SelectorSyntaxError, 'The give raw attribute is malform as well as the selector.'
        
        matches = matches.groupdict()
        
        if matches['operator']:
            if not Attribute._re_operator.search(matches['operator']):
                raise SelectorSyntaxError, 'The operator of the attribute is not recognized.'
            
            if not matches['value']:
                raise SelectorSyntaxError, 'Where is the value?'
            
            if matches['value'][0] == '"':
                matches['value'] = matches['value'][1:]
                
            if matches['value'][-1] == '"':
                matches['value'] = matches['value'][:-1]
        
        return Attribute(**matches)
    
    def __init__(self, name, operator, value):
        self._name     = name
        self._operator = operator
        self._value    = value
    
    def name(self):
        return self._name
    
    def operator(self):
        return self._operator
    
    def value(self):
        return self._value
    
    def match(self, vertex):
        try:
            attribute = vertex.attribute(self.name())
            
            assert attribute is not None
            
            if self.operator() == '=':
                assert self.value() == attribute
        
        except AssertionError:
            return False
        
        return True
    
    def __str__(self):
        return u'SELECTOR:ATTRIBUTE %s %s %s' % (self.name(), self.operator(), self.value())
    