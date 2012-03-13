from re      import split
from time    import time
from .common    import node_debug_message, is_string
from .exception import *
from .graph     import Vertex
from .selector  import make_selector, PathType

class Kotoba(Vertex):
    '''
    XML Parser with Level-3 CSS Selectors
    
    *source* can be a string representing the file path or the XML data, or Kotoba node.
    
    Currently supported selectors:
    
    * selectors with at least one of element name, attributes and pseudo classes (only ``:root`` and ``:empty``)
    * all four combinations of selectors are supported (e.g., ``selector_1 operator_1 selector_2 ...``)
    * support wildcard search (only for element name)
    * support multi combinations in a single statement (e.g., ``combo_1, combo_2``)
    '''
    
    static_guid = 1
    debug_mode  = False
    
    def __init__(self, node=None, level=0):
        """
        Construct an XML parser using CSS3 selectors
        """
        super(self.__class__, self).__init__()
        
        self._guid   = Kotoba.static_guid
        self._level  = level
        self._node   = node
        self._parent = None
        self._data   = None
        self._adjacents  = Kami()
        self._children   = Kami()
        self._attributes = None
        
        # lazy-loading flag
        self._is_children_initialized = False
        
        self.init(node)
        
        # Take care of static data
        Kotoba.static_guid += 1
    
    def guid(self):
        return self._guid
    
    def level(self):
        return self._level
    
    def parent(self, parent=None):
        if parent:
            self._parent = parent
        
        return self._parent
    
    def attribute(self, key):
        if not self.node().attributes.has_key(key):
            return None
        
        return self.node().attributes[key].value
    
    def children(self, selector=None, include_data_blocks=False):
        if not self._is_children_initialized:
            for original_child_node in self._node.childNodes:
                child_node = Kotoba(original_child_node, self.level() + 1)
                
                if (child_node.is_data() and not child_node.node().nodeValue) or child_node.is_comment():
                    continue
                
                child_node.parent(self)
                self.adjacents().append(child_node)
                
                if child_node.is_element():
                    self._children.append(child_node)
            
            self._is_children_initialized = True
        
        if is_string(selector):
            selector = make_selector(selector)
        
        returnees = self._children
        
        if selector:
            returnees = self._find_descendants(selector, True)
        if include_data_blocks:
            returnees = self.adjacents()
        
        return returnees
    
    def find(self, selector):
        if is_string(selector):
            selector = make_selector(selector)
        
        if not selector:
            raise InvalidSelectorError
        
        returnees = Kotoba._direct_search(self, selector)
        
        return returnees
    
    @staticmethod
    def _direct_search(node, selector):
        node_debug_message(node, node)
        
        search_type = selector.kind()
        
        if search_type == PathType.any_siblings or search_type == PathType.immediate_siblings:
            raise Exception, 'Future Features'
        
        node_debug_message(node, '[SEARCH] DESCENDANTS/CHILDREN')
        
        # Continue the search from the descendants.
        return node._find_descendants(selector, search_type == PathType.children)
    
    def debug_message(self, message, ignore_indentation=False):
        node_debug_message(self, message, ignore_indentation)
    
    def _find_descendants(self, selector, stop_here=False):
        returnees = Kami()
        
        for child in self.children():
            if not child.is_element():
                raise Exception, 'This child is not an element.'
            
            if selector.match(child): # if matched
                if not selector.next(): # if this is the last selector
                    returnees.append(child)
                    if not child.children():
                        continue
                    
                    if not stop_here:
                        returnees.extend(child.find(selector))
                    
                    continue
                
                if not stop_here:
                    returnees.extend(child.find(selector.next()))
                
                continue
            
            if not stop_here:
                returnees.extend(child.find(selector))
        
        return returnees
    
    def init(self, node=None):
        if not node: return
        
        self._is_initialized = True
        self._node = node
        self.name(self._node.nodeName)
        
        return self
    
    def node(self, node=None):
        self.init(node)
        return self._node
    
    def kind(self):
        return self._node.nodeType
    
    def is_element(self):
        return self._node.nodeType == self._node.ELEMENT_NODE
    
    def is_comment(self):
        return self._node.nodeType == self._node.COMMENT_NODE
    
    def is_data(self):
        return self._node.nodeType in [self._node.CDATA_SECTION_NODE, self._node.TEXT_NODE]
    
    def data(self):
        if not self._data:
            self._data = []
            
            for child in self.children(None, True):
                if child.is_data():
                    data = child.node().nodeValue and unicode(child.node().nodeValue).strip() or ''
                    self._data.append(data)
                    continue
                
                self._data.append(child.data())
            
            self._data = ''.join(self._data)
        
        return self._data
    
    def dump(self, label, force_print=False, ignore_indentation=False):
        if not force_print:
            return
        
        if label:
            self.debug_message('[%s]' % label, ignore_indentation)
        
        self.debug_message('CURRENT: %s' % self, ignore_indentation)
        self.debug_message('PARENT:  %s' % self.parent(), ignore_indentation)
        self.debug_message('KIND: %s' % self.kind(), ignore_indentation)
    
    def __str__(self):
        representative = 'NODE %s AT LEVEL %s (%s)' % (self.name(), self.level(), self._guid)
        
        if self.is_data():
            representative = 'NODE [DATA] AT LEVEL %s (%s)' % (self.level(), self._guid)
        elif not self.name():
            representative = 'NODE [TYPE-%d] AT LEVEL %s (%s)' % (self.kind(), self.level(), self._guid)
        
        return representative

class Kami(list):
    '''
    The list of :class:`kotoba.kotoba.Kotoba`.
    '''
    def __init__(self):
        self.__registered_nodes = []
    
    def data(self):
        output = []
        
        for kotoba in self:
            output.append(kotoba.data())
        
        return ''.join(output)
    
    def append(self, kotoba):
        if kotoba.guid() in self.__registered_nodes:
            return
        
        self.__registered_nodes.append(kotoba.guid())
        
        super(Kami, self).append(kotoba)
    
    def extend(self, other_kami):
        for kotoba in other_kami:
            self.append(kotoba)