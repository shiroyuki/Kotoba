from .common    import is_string
from .exception import *

class Vertex(object):
    '''
    Data structure representing a vertex in a graph.
        
    *name* (required, string) is the name of the vertex.
        
    *adjacents* (optional, list, default: None) is a list of neighbours (*graph.Vertex*).
    '''
    
    def __init__(self):
        self._name      = None
        self._adjacents = []
    
    def name(self, new_name=None):
        if new_name and not is_string(new_name):
            raise InvalidInputError
        
        if is_string(new_name):
            self._name = new_name
        
        return self._name
    
    def adjacents(self):
        return self._adjacents