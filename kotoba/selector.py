from re import sub, split

from .common import node_debug_message, is_string
from .graph  import Vertex as BaseVertex

def make_selector(path):
    selector = None
    path     = split(' ', sub('\s{2,}', ' ', path.strip()))
    
    previous_selector = None
    combinator        = None
    
    for p in path:
        if p in PathType.registered:
            combinator = PathType.registered.index(p)
            continue
        
        new_selector = Selector(p, combinator)
        combinator = None
        
        if previous_selector:
            previous_selector.next(new_selector)
        
        previous_selector = new_selector
        
        if not selector:
            selector = new_selector
    
    return selector

class PathType(object):
    registered   = [None, '>', '+', '~']
    descendants  = 0
    children     = 1
    any_siblings = 3
    immediate_siblings = 2

class Selector(BaseVertex):
    def __init__(self, name, _kind=PathType.descendants):
        super(self.__class__, self).__init__()
        
        self._name = name
        self._kind = _kind
        self._next = None
    
    def name(self):
        return self._name
    
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
        return self.name() == vertex.name()
    
    def __str__(self):
        return u'SELECTOR %s' % self.name()
