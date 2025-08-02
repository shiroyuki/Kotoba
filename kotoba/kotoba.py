from re      import split
from time    import time

from .common    import node_debug_message, is_string
from .exception import *
from .graph     import Vertex
from .kami      import Kami
from .selector  import PathType
from .parser    import selector as parse_selector

__all__ = ['Kotoba']

class Kotoba(Vertex):
    """
    XML Parser with Level-3 CSS Selectors

    :param kotoba.driver.IDriver node:

    Currently supported selectors:

    * selectors with at least one of element name, attributes and pseudo classes (only ``:root`` and ``:empty``)
    * all four combinations of selectors are supported (e.g., ``selector_1 operator_1 selector_2 ...``)
    * support wildcard search (only for element name)
    * support multi combinations in a single statement (e.g., ``combo_1, combo_2``)
    """

    static_guid = 1
    debug_mode  = False

    def __init__(self, node=None, level=0):
        """ Construct an XML parser using CSS3 selectors """
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

        self.name(node.name())

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
        if not key in self.attributes():
            return None

        return self.attributes()[key]

    def has_attribute(self, key):
        return key in self.attributes()

    def attributes(self):
        if not self._attributes:
            self._attributes = dict(self.node().attributes())

        return self._attributes

    def children(self, selector=None, include_data_blocks=False):
        if not self._is_children_initialized:
            self._node.__class__.initialize_children(self)

            self._is_children_initialized = True

        if is_string(selector):
            selector = parse_selector(selector)

        returnees = self._children

        if selector:
            returnees = self._find_descendants(selector, True)
        if include_data_blocks:
            returnees = self.adjacents()

        return returnees

    def find(self, selector):
        if is_string(selector):
            selector = parse_selector(selector)

        if not selector:
            raise InvalidSelectorError()

        returnees = Kotoba._direct_search(self, selector)

        return returnees

    def __repr__(self):
        return '<{}:{}>'.format(self.__class__.__name__, self.name())

    @staticmethod
    def _direct_search(node, selector):
        node_debug_message(node, node)

        search_type = selector.kind()

        if search_type == PathType.any_siblings or search_type == PathType.immediate_siblings:
            raise Runtime('Future Features')

        node_debug_message(node, '[SEARCH] DESCENDANTS/CHILDREN')

        # Continue the search from the descendants.
        return node._find_descendants(selector, search_type == PathType.children)

    def debug_message(self, message, ignore_indentation=False):
        node_debug_message(self, message, ignore_indentation)

    def _find_descendants(self, selector, stop_here=False):
        returnees = Kami()

        for child in self.children():
            if not child.is_element():
                raise RuntimeException('This child is not an element.')

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

    def node(self):
        return self._node

    def original_value(self):
        """ Retrieve the value of the node (node driver).

            .. versionadded:: 3.1
        """

        return self._node.value()

    def kind(self):
        return self._node.nodeType

    def is_element(self):
        return self._node.is_element()

    def is_comment(self):
        return self._node.is_comment()

    def is_data(self):
        return self._node.is_data()

    def data(self):
        if not self._data:
            self._data = self._node.__class__.retrieve_data(self)

        return self._data

    def dump(self, label, force_print=False, ignore_indentation=False):
        if not force_print:
            return

        if label:
            self.debug_message('[{}]'.format(label), ignore_indentation)

        self.debug_message('CURRENT: {}'.format(self), ignore_indentation)
        self.debug_message('PARENT:  {}'.format(self.parent()), ignore_indentation)
        self.debug_message('KIND: {}'.format(self.kind()), ignore_indentation)

    def __str__(self):
        representative = 'NODE {} AT LEVEL {} ({})'.format(self.name(), self.level(), self._guid)

        if self.is_data():
            representative = 'NODE [DATA] AT LEVEL {} ({})'.format(self.level(), self._guid)
        elif not self.name():
            representative = 'NODE [TYPE-{}] AT LEVEL {} ({})'.format(self.kind(), self.level(), self._guid)

        return representative
